from flask import current_app
from fathom.lib.util_days import get_today_as_str
from fathom.lib.util_rolling_outliers import rolling_outliers
from fathom.providers import FACEBOOK_PROVIDER

filter_metrics_list = ['cpc', 'cpm', 'ctr']

# loop through the data for all accounts for one provider
# generate anomalies and save them to firebase on account_id
def generate_anomalies(provider_id=FACEBOOK_PROVIDER):
    db = current_app.extensions["db"]

    today = get_today_as_str()
    accounts_collection = db.collection(u'Accounts')
    accounts_ref = accounts_collection.where(u'has_completed_questionnaire', u'==', True).stream()

    for account in accounts_ref:
        account_document_id = account.id
        if f"{provider_id}-" in account_document_id:
            print(f'checking anomalies for {account_document_id}')
            delete_existing_anomalies_from_db(account_document_id, provider_id)
            
            metrics_ref = accounts_collection.document(account_document_id).collection('Metrics').stream()
            filter_metrics = [] # [ {date: date, cpc:cpc, cpm:cpm}]
            for stats in metrics_ref:
                date_str = stats.id

                # TODO: check if it's within the last X days

                company_data = stats.to_dict()
                filter_metrics.append(generate_filter_metrics(company_data, date_str))

            for filter_metric in filter_metrics_list:
                metric_anomalies = checks_filter_metrics_for_anomalies(filter_metrics, filter_metric)
                
                if len(metric_anomalies) > 0:
                    save_anomalies_to_db(metric_anomalies, account_document_id, today, provider_id, filter_metric)          

    return 'ok'

def generate_filter_metrics(company_data, metric_date):
    # Takes company data
    # Returns filter metrics for cpc, ctr and cpm only!
    result = { 'date': metric_date}
    if float(company_data.get('clicks', 0)) > 0:
        cpc = float(company_data['spend'])/float(company_data['clicks'])
        result['cpc'] = cpc

        ctr = 100 * float(company_data['clicks'])/float(company_data['impressions'])
        result['ctr'] = ctr

    if float(company_data.get('impressions', 0)) > 0:
        cpm = 1000 * float(company_data['spend']) / float(company_data['impressions'])
        result['cpm'] = cpm
    
    return result # TODO add conversion events

def checks_filter_metrics_for_anomalies(filter_metrics, metric):
    ## takes filter_metrics
    ## returns list of anomalies
    # [ {date: date, cpc:cpc, cpm:cpm}]
    metric_list = [(x['date'], x[metric]) for x in filter_metrics if metric in x]
    results = rolling_outliers(metric_list)
    # yesterday = get_yesterday_as_str()
    # outliers_data = [x for x in results['outliers_data'] if x[0] == yesterday]
    # return outliers_data
    return results['outliers_data']

def delete_existing_anomalies_from_db(account_id, provider_id):
    ## takes anomalies and account_id
    ## saves anomalies to firebase
    db = current_app.extensions["db"]
    account_ref = db.collection(u'Accounts').document(account_id)
    anomalies_ref = account_ref.collection(u'Anomalies')
    anomalies_for_provider = anomalies_ref.where('provider_id', "==", provider_id).stream()
    count = 0

    # delete the anomalies where provider_id matches
    for existing_anomaly in anomalies_for_provider:
        existing_anomaly.reference.delete()
        count += 1
    
    print(f"deleted {count} anomalies for {account_id}")

def save_anomalies_to_db(anomalies, account_id, date_saved, provider_id, metric_name):
    ## takes anomalies and account_id
    ## saves anomalies to firebase
    db = current_app.extensions["db"]
    account_ref = db.collection(u'Accounts').document(account_id)
    anomalies_ref = account_ref.collection(u'Anomalies')
    
    for anomaly in anomalies:
        doc_ref = anomalies_ref.document()
        
        anomaly_data = {
            "date": anomaly[0],
            "value": anomaly[1],
            "date_saved": date_saved,
            "provider_id": provider_id,
            "metric": metric_name
        }

        # save to firebase
        doc_ref.set(anomaly_data)
        print(f'Saved anomalies for {account_id}')

def delete_all_anomalies_from_db():
    ## takes anomalies and account_id
    ## saves anomalies to firebase
    db = current_app.extensions["db"]
    accounts_ref = db.collection(u'Accounts')
    accounts_stream = accounts_ref.where(u'has_completed_questionnaire', u'==', True).stream()
    print("Deleteing all anomalies from firestore")
    all_count = 0

    # delete the anomalies where provider_id matches
    for account in accounts_stream:
        print('Deleting anomalies for account ', account.id)
        account_count = 0
        anomaly_ref = accounts_ref.document(account.id).collection(u'Anomalies')
        for anomaly in anomaly_ref.stream():
            anomaly.reference.delete()
            all_count += 1
            account_count += 1
        print(f'Deleted {account_count} anomalies for {account.id}')
    print(f'Deleted {all_count} anomalies total')
    return 'ok'