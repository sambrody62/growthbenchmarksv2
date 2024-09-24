# get a list of users
from flask import current_app
from fathom.lib.util_days import get_today_as_str, get_yesterday_as_str
from fathom.providers import FACEBOOK_PROVIDER, GOOGLE_PROVIDER
from fathom.lib.util_send_email import send_email
from fathom.lib.email_templates.anomaly_detection import anomaly_detection_email

def send_anomaly_emails(testing=True, actually_send=True, date_to_process=None):
    db = current_app.extensions["db"]
    
    if testing:
        users_ref = db.collection('users').where("is_god", "==", True).stream()
    else:
        users_ref = db.collection('users').where("is_subscribed", "==", True).stream()
    
    today = get_today_as_str()
    anomalies_count = 0
    user_count = 0
    all_emails = ""

    for user in users_ref:
        user_data = user.to_dict()
        
        # user is subscribed and hasn't received anomalies today
        if testing or (user_data and user_data.get('is_subscribed', True) and user_data.get('anomalies_processed') != today):
            if testing != True and user_data.get('anomalies_processed') == today:
                continue

            all_anomalies = []
            email = user_data.get('email', '')
            print("user: ", email)
            
            # loop through facebook accounts
            user_facebook_account_ids = user_data.get('account_ids', []) or [] # some account_ids are null not an array
            for account_id in user_facebook_account_ids:
                print(f"getting anomalies for {account_id}")
                all_anomalies.extend(find_anomalies_for_an_account(account_id, provider=FACEBOOK_PROVIDER, date_to_process=date_to_process))

            # loop through google accounts
            user_google_account_ids = user_data.get('google_account_ids', []) or []
            for account_id in user_google_account_ids:
                all_anomalies.extend(find_anomalies_for_an_account(account_id, provider=GOOGLE_PROVIDER, date_to_process=date_to_process))

            if len(all_anomalies) > 0:
                user_count += 1
                anomalies_count += len(all_anomalies)

                print("Anomalies: ", len(all_anomalies))
                print("Example: ", all_anomalies[0])

                if (actually_send):
                    send_anomaly_email_to_user(email, all_anomalies, actually_send, date_to_process)
                else:
                    all_emails += send_anomaly_email_to_user(email, all_anomalies, actually_send, date_to_process)
            else:
                print("No Anomalies")
    
        user.reference.update({"anomalies_processed": today})

    print(f"sent {anomalies_count} anomalies to {user_count} users")
    return all_emails

def find_anomalies_for_an_account(account_id, provider=FACEBOOK_PROVIDER, date_to_process=None):
    if (date_to_process == None):
        date_to_process = get_yesterday_as_str()
    db = current_app.extensions["db"]
    accounts_collection = db.collection(u'Accounts')
    account_ref = accounts_collection.document(f"{provider}-{account_id}")
    account_data = account_ref.get().to_dict()
    if account_data:
        account_name = account_data.get('name','')
    else:
        account_name = ''
    anomalies_ref = account_ref.collection('Anomalies')
    anomalies_stream = anomalies_ref.where('date', "==", date_to_process).stream()
    # anomalies_stream = anomalies_ref.stream()
    anomalies_data = []
    for anomaly in anomalies_stream:
        anomaly_data = anomaly.to_dict()
        anomalies_data.append({**anomaly_data, "account_name":account_name, "account_id":account_id})

    return anomalies_data

def send_anomaly_email_to_user(email, anomalies, actually_send=True, date_to_process=None):
    SUBJECT = 'Growthbenchmarks.com - Something might be wrong with your accounts!'
    
    HTML_TEMPLATE = anomaly_detection_email(anomalies, date_to_process)
    if (actually_send == False):
        return HTML_TEMPLATE

    send_email(email, SUBJECT, HTML_TEMPLATE)

    print(f"{len(anomalies)} anomalies sent to {email}")
    return HTML_TEMPLATE

def format_anomaly_as_str(anomaly):
    """
    {
        'date': '2021-01-01',
        'date_saved': '2021-09-20',
        'metric': 'cpc',
        'provider_id': 'fb',
        'value': '5.2912021021012012',
        'account_name': 'Leadsie',
        'account_id': '703677253715432'
    }
    """
    long_provider = 'facebook'
    if (anomaly['provider_id'] == 'google'):
        long_provider = 'google'
    account_link=f"https://growthbenchmarks.com/{long_provider}/{anomaly['account_id']}/{anomaly['metric']}"
    return f"<li><a href='{account_link}'>{anomaly['metric'].upper()}</a> for {anomaly['account_name']} ({anomaly['account_id']}) was {round(float(anomaly['value']), 2)}</li>"

