from flask import current_app
from fathom.lib.util_days import get_today_as_str
from fathom.providers import FACEBOOK_PROVIDER

def generate_account_benchmarks(provider_id=FACEBOOK_PROVIDER):
    """Cron job that triggers overnight to generate benchmarks firestore"""
    current_app.logger.info(f'Running generate {provider_id} benchmarks')
    db = current_app.extensions["db"]

    today = get_today_as_str()
    posts_ref = db.collection(u'Accounts').where(u'has_completed_questionnaire', u'==', True)

    results = posts_ref.stream()

    accounts = dict()
    for doc in results:
        company_data = doc.to_dict()
        account_id = doc.id
        
        if f'{provider_id}-' in account_id:
            accounts[account_id] = company_data

    current_app.logger.info(f"for {len(accounts)} accounts")

    # All companies
    len_companies = len(accounts.keys())
    agg_date_all = dict()

    # Benchmark data, split by the properties of the company, and then into their answers
    # e.g. benchmark_data[industry][b2b], or benchmark_data[location][north_america]
    benchmark_data = dict()

    for account_id in accounts.keys():
        current_app.logger.info(f'Getting {provider_id} metrics for {account_id}')
        metrics = get_account_metrics(account_id)
        
        for row in metrics:
            date = row['id']
            for key, value in row.items():
                try:
                    #all
                    if key in ['id', 'date_start', 'date_saved', 'account_id']:
                        continue    
                    if date not in agg_date_all:
                        agg_date_all[date] = dict()
                    if key in agg_date_all[date]:
                        agg_date_all[date][key] += float(value) / len_companies
                    else:
                        agg_date_all[date][key] = float(value) / len_companies
                
                    # Get properties from company
                    for company_property in ['industry', 'property', 'model', 'spend', 'location']:
                        company_property_value = accounts[account_id].get(company_property)
                        if company_property not in benchmark_data:
                            benchmark_data[company_property] = dict()

                        if company_property_value not in benchmark_data[company_property]:
                            benchmark_data[company_property][company_property_value] = dict()
                        
                        if date not in benchmark_data[company_property][company_property_value]:
                            benchmark_data[company_property][company_property_value][date] = dict()


                        if key in benchmark_data[company_property][company_property_value][date]:
                            benchmark_data[company_property][company_property_value][date][key]['value'] += float(value)
                            benchmark_data[company_property][company_property_value][date][key]['count'] += 1
                        else:
                            benchmark_data[company_property][company_property_value][date][key] = dict()
                            benchmark_data[company_property][company_property_value][date][key]['value'] = float(value)
                            benchmark_data[company_property][company_property_value][date][key]['count'] = 1
                except:
                    print(f'Error {key}')

    benchmark_name = f'{provider_id}-all_companies'
    bench_ref = db.collection(u'Benchmarks').document(benchmark_name)
    benchmark_dict = bench_ref.get().to_dict()

    if benchmark_dict != None and benchmark_dict.get('date_saved') == today:
        print("Skipping full benchmark", benchmark_name)
    else:
        for date, metrics in agg_date_all.items():
            save_account_benchmark(benchmark_name, date, metrics, len_companies)
        bench_ref.set({"date_saved": today})

    # save all industry benchmarks as a benchmark with that name after industry.
    for company_property in ['industry', 'property', 'model', 'spend', 'location']:
        for company_property_value in benchmark_data[company_property].keys():
            # Get the existing benchmark and see if it has been saved today
            # if it has, then skip it
            benchmark_name = f'{provider_id}-{company_property}.{company_property_value}'
            bench_ref = db.collection(u'Benchmarks').document(benchmark_name)
            benchmark_dict = bench_ref.get().to_dict()
            if benchmark_dict != None and benchmark_dict.get('date_saved') == today:
                print("Skipping full benchmark", benchmark_name)
            else:
                
                for date, metrics in benchmark_data[company_property][company_property_value].items():
                    max_accounts = 0
                    for key in metrics:
                        if key in ['date_start', 'date_saved', 'account_id']:
                            continue
                        else:
                            # We need to get the mean value here
                            accounts_count = benchmark_data[company_property][company_property_value][date][key]['count']
                            benchmark_data[company_property][company_property_value][date][key]['value'] /= accounts_count
                            if accounts_count > max_accounts:
                                max_accounts = accounts_count
                            

                    for key in metrics:
                        if key in ['date_start', 'date_saved', 'account_id']:
                            continue
                        else:
                            benchmark_data[company_property][company_property_value][date][key] = benchmark_data[company_property][company_property_value][date][key]['value']
                    
                    save_account_benchmark(benchmark_name, date, metrics, max_accounts)
                bench_ref.set({"date_saved": today})

    current_app.logger.info(f'Finished fetch {provider_id} benchmarks async task')
    return 'ok', 200

def get_account_metrics(account_id):
    current_app.logger.debug(f'getting metrics for {account_id}')

    db = current_app.extensions["db"]

    metrics_ref = db.collection(u'Accounts').document(account_id).collection('Metrics')

    results = metrics_ref.stream()

    insights = list()
    for doc in results:
        insights.append({**doc.to_dict(), 'id': doc.id})

    return insights

def save_account_benchmark(benchmark, date, metrics, accounts=0):
    print('Saving account benchmark', benchmark, date)
    today = get_today_as_str()
    db = current_app.extensions["db"]

    bench_ref = db.collection(u'Benchmarks').document(benchmark)
    date_ref = bench_ref.collection('Metrics').document(date)

    data = metrics.copy()
    data["date_saved"] = today
    data['date'] = date
    data["benchmark"] = benchmark
    data["accounts"] = accounts

    date_ref.set(data)
    
    print("Saved benchmark for {}, {}".format(date, benchmark))
