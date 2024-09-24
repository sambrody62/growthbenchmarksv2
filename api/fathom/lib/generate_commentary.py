from flask import current_app
from fathom.lib.util_days import get_start_and_end_dates_for_2_months_as_str
from fathom.providers import FACEBOOK_PROVIDER

def generate_commentary(provider=FACEBOOK_PROVIDER):
    db = current_app.extensions["db"]

    # loop through each benchmark
    benchmarks = db.collection(u'Benchmarks').stream()
    for benchmark in benchmarks:
        if (provider+'-' in benchmark.id):
            # get the metrics for the last two months
            start_date, end_date = get_start_and_end_dates_for_2_months_as_str()
            metrics_collection = db.collection(u'Benchmarks').document(benchmark.id).collection(u'Metrics')
            if (metrics_collection is not None):
                insights_stream = metrics_collection.where(u'date', '>=', start_date).where(u'date', '<=', end_date).stream()
                max_accounts = 0
                # sum up days to get the monthly data
                commentary = {}
                for day in insights_stream:
                    dayData = day.to_dict()

                    # update max accounts
                    accounts = dayData.get('accounts', 0)
                    if accounts > max_accounts:
                        max_accounts = accounts

                    year_month = day.id[:7]

                    if year_month not in commentary:
                        commentary[year_month] = dict()

                    for key, value in dayData.items():
                        if key in ['id', 'date_start', 'date_saved', 'account_id', 'date', 'benchmark']:
                            continue    
                        if key not in commentary[year_month]:
                            commentary[year_month][key] = float(value)
                        else:
                            commentary[year_month][key] += float(value)
                    
                    # get the max accounts for the time period
                    commentary[year_month]['accounts'] = max_accounts

                # save to 'Commentary' under YYYY-MM
                for year_month in commentary.keys():
                    benchmark_ref = db.collection(u'Benchmarks').document(benchmark.id).collection(u'Commentary').document(year_month)
                    benchmark_ref.set(commentary[year_month])
    return 'ok'