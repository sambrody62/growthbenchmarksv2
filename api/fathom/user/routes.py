import requests
from mailchimp_marketing import Client # pylint: disable=import-error
from mailchimp_marketing.api_client import ApiClientError # pylint: disable=import-error
from flask import Blueprint, json, request, jsonify, current_app

from fathom.lib.util_days import get_today_as_str
from fathom.providers import FACEBOOK_PROVIDER, FACEBOOK_FAKE_PROVIDER, GOOGLE_PROVIDER, GOOGLE_FAKE_PROVIDER
from fathom.lib import authenticate, currency_conversions, get_benchmark_data_from_db
from fathom.facebook import FacebookConnector, get_facebook_ad_accounts, get_long_lived_access_token
from fathom.google import GoogleAdsConnector


user = Blueprint('user', __name__, template_folder='templates')
mailchimp = Client()
mailchimp.set_config({
  "api_key": "11e323cac90ae7bb2fafe5339149b861",
  "server": "us9"
})
list_id = 'ee6836aa8f'

@user.route('/google_authenticate_code', methods=['POST'])
def google_authenticate_code():
    code = request.get_json().get('code')
    google_response = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': '480005130966-6g0kp8sdf5bajit6ghqf3h8fpjunqsob.apps.googleusercontent.com',
        'client_secret': 'nKx92VJL7pJTsQIfUM7iTxRj',
        'grant_type': 'authorization_code',
        'redirect_uri': 'postmessage' # https://stackoverflow.com/questions/11485271/google-oauth-2-authorization-error-redirect-uri-mismatch
    })
    tokens = google_response.json()
    return tokens

@user.route('/delete_account', methods=['POST'])
@authenticate
def delete_account(user):
    data = request.get_json()
    account_id = data.get('account_id')
    db = current_app.extensions["db"]
    accounts_collection = db.collection('Accounts')
    # CHECK WHETHER THIS IS INDEED A FACEBOOK ACCOUNT
    account = accounts_collection.document(f'fb-{account_id}')
    if account.get().exists:
        account.delete()
        return jsonify({'success': True})
    account = accounts_collection.document(f'fbfake-{account_id}')
    if account.get().exists:
        account.delete()
        return jsonify({'success': True})
    return jsonify({'success':False})

@user.route('/get_is_subscribed', methods=['GET'])
@authenticate
def get_is_subscribed(user):
    return jsonify({"is_subscribed": user.get('is_subscribed')} )

@user.route('/update_is_subscribed', methods=['POST'])
@authenticate
def update_is_subscribed(user):
    data = request.get_json()
    is_subscribed = data.get('is_subscribed')
    db = current_app.extensions["db"]
    users_stream = db.collection('users').where('uid', '==', user.get('uid')).stream()
    for existing_user in users_stream:
        existing_user.reference.update({'is_subscribed': is_subscribed})
    return jsonify({'success': True})

@user.route('/get_data', methods=['POST'])
@authenticate
def get_data(user):
    data = request.get_json()
    company_id = data.get('companyId')
    provider_id = data.get('providerId')
    selected_benchmarks = data.get('selectedBenchmarks')
    is_example_company = False

    is_god = user.get('is_god')

    dates = list()
    you = dict()
    similar_companies = dict()
    db = current_app.extensions["db"]
    accounts_collection = db.collection('Accounts')
    has_completed_first_data_pull = None

    target_currency_conversion = 1
    
    # if company id is None
    if company_id is not None:
        companies_ref = accounts_collection.document(f'{provider_id}-{company_id}').get()
        main_company = companies_ref.to_dict()

        # Get the right list of account ids i.e. google_account_ids if provider_id = google
        if provider_id == FACEBOOK_PROVIDER:
            account_ids_ref = 'account_ids'
            account_ids = user.get(account_ids_ref, [])
            has_completed_first_data_pull = main_company.get(f'has_completed_first_{provider_id}_data_pull')
            access_token = user.get('access_token')
            ConnectorClass = FacebookConnector
            refresh_token = None
        elif provider_id == GOOGLE_PROVIDER:
            account_ids_ref = f'{provider_id}_account_ids'
            account_ids = user.get(account_ids_ref, [])
            has_completed_first_data_pull = main_company.get(f'has_completed_first_{provider_id}_data_pull')
            access_token = user.get(f'{provider_id}_access_token')
            refresh_token = user.get(f'{provider_id}_refresh_token')
            ConnectorClass = GoogleAdsConnector
        elif provider_id == FACEBOOK_FAKE_PROVIDER:
            is_example_company = True
            account_ids = user.get('fake_account_ids', [])
        elif provider_id == GOOGLE_FAKE_PROVIDER:
            is_example_company = True
            account_ids = user.get('google_fake_account_ids', [])
        else:
            account_ids = []

        if is_god != True and company_id is not None and company_id not in account_ids:
            return jsonify({"error": 'Insufficient permissions'})

        today = get_today_as_str()
        if main_company != None and (main_company.get('last_date_saved') != today or has_completed_first_data_pull != True) and is_example_company == False:
            if company_id not in account_ids and is_god is True:
                # if the user is god, then find the user who owns this company to get their access token
                users_collection = db.collection('users')
                user_ref = users_collection.where(account_ids_ref, 'array_contains', company_id).get()
                if len(user_ref) > 0:
                    user_doc = user_ref[0].to_dict()
                    refresh_token = user_doc.get(f'{provider_id}_refresh_token')
                    if provider_id == FACEBOOK_PROVIDER:
                        access_token = user_doc['access_token']
                    else:
                        access_token = user_doc[f'{provider_id}_access_token']

            # Fetch and save data for this company
            provider_connector = ConnectorClass(account_id=company_id, access_token=access_token, refresh_token=refresh_token, login_id=main_company.get('login_id'))
            data = provider_connector.fetch_metrics()

        if main_company:
            currency = main_company.get('currency')
        if currency:
            target_currency = currency
        else:
            target_currency = 'USD'
        target_currency_conversion = currency_conversions.get(target_currency)

    # Get similar company data
    for similar_company in main_company['similar_companies']:
        similar_company = similar_company.strip()
        similar_company_ref = accounts_collection.document(f'{similar_company}').get()
        similar_company_data = similar_company_ref.to_dict()
        account_currency = similar_company_data.get('currency')
        currency_conversion = target_currency_conversion / currency_conversions.get(account_currency)
        similar_companies_metrics_ref = accounts_collection.document(f'{similar_company}').collection('Metrics').get()
        for metrics in similar_companies_metrics_ref:
            doc_datum = metrics.to_dict()
            start_date = metrics.id
            if start_date not in dates:
                dates.append(start_date)
            for key in doc_datum.keys():
                if key in ['date_start', 'date_saved', 'account_id']:
                    continue
                if start_date not in similar_companies:
                    similar_companies[start_date] = dict()
                if key not in similar_companies[start_date]:
                    similar_companies[start_date][key] = 0

                value = float(doc_datum.get(key))
                if key == 'spend' or (len(key) > 6 and key[-6:] == '.value'):
                    value = value * currency_conversion
                similar_companies[start_date][key] += value
    
    # Get you data
    if is_example_company != True:
        metrics_ref = accounts_collection.document(f'{provider_id}-{company_id}').collection('Metrics').get()
        for metrics in metrics_ref:
            start_date= metrics.id
            doc_datum = metrics.to_dict()
            if start_date not in dates:
                dates.append(start_date)
            you[start_date] = doc_datum

    benchmarks = list()
    for selected_benchmark in selected_benchmarks:
        benchmark_data = get_benchmark_data_from_db(selected_benchmark, list(), target_currency_conversion, provider_id)
        benchmarks.append(benchmark_data)
    
        new_dates = benchmark_data['dates']
        for new_date in new_dates:
            if new_date not in dates:
                dates.append(new_date)
    
    dates.sort()

    return jsonify({
        "you": you,
        "similar_companies": similar_companies,
        "benchmarks": benchmarks,
        "dates": dates,
        "account_id": company_id,
        "has_completed_first_data_pull": has_completed_first_data_pull
    })


@user.route('/get_my_companies', methods=['GET'])
@authenticate
def get_my_companies(user):
    db = current_app.extensions["db"]
    accounts_collection = db.collection('Accounts')

    companies = list()
    if user.get('is_god'):
        stream = accounts_collection.stream()
        for doc in stream:
            companies.append({**doc.to_dict(), 'provider_id':doc.id.split('-')[0]})
    else:
        account_ids = user.get('account_ids')
        companies = get_account_information(companies, account_ids, accounts_collection, FACEBOOK_PROVIDER)
        fake_account_ids = user.get('fake_account_ids')
        companies = get_account_information(companies, fake_account_ids, accounts_collection, FACEBOOK_FAKE_PROVIDER)
        google_account_ids = user.get('google_account_ids')
        companies = get_account_information(companies, google_account_ids, accounts_collection, GOOGLE_PROVIDER)
        google_fake_account_ids = user.get('google_fake_account_ids')
        companies = get_account_information(companies, google_fake_account_ids, accounts_collection, GOOGLE_FAKE_PROVIDER)
    return jsonify({'companiesList': companies})

def get_account_information(companies, account_ids, accounts_collection, prefix):
    if account_ids != None:
        for account_id in account_ids:
            company = accounts_collection.document(f'{prefix}-{account_id}').get().to_dict()
            if company:
                company['provider_id'] = prefix
                companies.append(company)
    return companies

def add_to_mailchimp(user):
    # Add user to mailchimp
    member_info = {
        "email_address": user.get('email'),
        "status": "subscribed",
        "merge_fields": {
            "FNAME": user.get('first_name'),
            "LNAME": user.get('last_name'),
        }
    }

    try:
        mailchimp.lists.add_list_member(list_id, member_info)
    except ApiClientError as error:
        if json.loads(error.text)['title'] != 'Member Exists':
            # This may happen if they are already added
            print("An exception occurred adding to mailchimp: {}".format(error.text))

def get_account_ids_from_ad_accounts(ad_accounts):
    account_ids = list()
    for ad_account in ad_accounts:
        account_ids.append(ad_account['account_id'])
    return account_ids

def update_user_with_accounts(user):
    user_id = user.get('id')
    provider_id = user.get('provider_id')

    ## Get ad accounts the user has access to
    if provider_id == FACEBOOK_PROVIDER:
        ## Get long lived access token
        short_access_token = user.get('access_token')
        long_access_token = get_long_lived_access_token(short_access_token)
        user['access_token'] = long_access_token
        ad_accounts = get_facebook_ad_accounts(user_id, long_access_token)
        user['account_ids'] = get_account_ids_from_ad_accounts(ad_accounts)
    elif provider_id == GOOGLE_PROVIDER:
        refresh_token = user.get('google_access_token')
        google_ads_connector = GoogleAdsConnector(refresh_token=refresh_token)
        ad_accounts = json.loads(google_ads_connector.get_primary_accounts_list().to_json(orient='records'))
        user['google_account_ids'] = get_account_ids_from_ad_accounts(ad_accounts)
    
    ## Iterate through all ad accounts and add them to the list of Accounts with currency + name
    db = current_app.extensions["db"]
    accounts_collection = db.collection('Accounts')
    for ad_account in ad_accounts:
        ad_account_id = ad_account['account_id']
        companies_ref = accounts_collection.document(f'{provider_id}-{ad_account_id}').get()
        existing_company = companies_ref.to_dict()
        if existing_company == None:
            accounts_collection.document(f'{provider_id}-{ad_account_id}').set({'name': ad_account.get('name'), "currency": ad_account.get('currency'), "account_id": ad_account_id, "provider_id": provider_id, 'login_id': ad_account.get('login_id')})
        elif (existing_company.get('name') != ad_account.get('name') or existing_company.get('currency') != ad_account.get('currency') or existing_company.get('login_id') != ad_account.get('login_id')):
            accounts_collection.document(f'{provider_id}-{ad_account_id}').update({'name': ad_account.get('name'), "currency": ad_account.get('currency'), 'login_id': ad_account.get('login_id')})

    return user

@user.route('/upsert', methods=['POST'])
def upsert_user():
    data = request.get_json()
    user = data.get('user')
    db = current_app.extensions["db"]

    add_to_mailchimp(user)

    # If logged in with email then save basic information with 'logged in with email flag'
    if user.get('isLoggedInWithEmail') == True:
        new_user_data = {
            "uid": user['uid'],
            "provider_id": "email",
            "email": user['email'],
            "email_verified": True
        }

        users_collection = db.collection('users')
        users_stream = users_collection.where('uid', '==', user['uid']).stream()

        # If there is an existing user(s) then update them
        for existing_user_ref in users_stream:
            # Update the existing user
            users_collection.document(existing_user_ref.id).update(new_user_data)
            return jsonify({'success': True})
        # Create a new user
        users_collection.document().set(new_user_data)
        return jsonify({'success': True, "isNewUser":True})
    else:
        user = update_user_with_accounts(user)

        users_collection = db.collection('users')
        users_stream = users_collection.where('uid', '==', user['uid']).stream()

        has_updated = False
        for existing_user_ref in users_stream:
            # Update the existing user
            update_for_user =  {
                "id": user.get('id'),
                "uid": user['uid'],
                "provider_id": user['provider_id'],
                "first_name": user['first_name'],
                "last_name": user['last_name'],
                "name": user['name'],
                "displayName": user['displayName'],
                "email": user['email'],
                "access_token": user.get('access_token'),
                "facebook_access_token": user.get('facebook_access_token'),
                "google_access_token": user.get('google_access_token'),
                "refresh_token": user.get('refresh_token'),
                "facebook_refresh_token": user.get('facebook_refresh_token'),
                "google_refresh_token": user.get('google_refresh_token'),
                "account_ids": user.get('account_ids'),
                "google_account_ids": user.get('google_account_ids'),
            }
            users_collection.document(existing_user_ref.id).update(update_for_user)
            has_updated = True

        if has_updated:
            return jsonify({'success': True})

    # Create a new user
    users_collection.document().set(user)
    return jsonify({'success': True, "isNewUser":True})
