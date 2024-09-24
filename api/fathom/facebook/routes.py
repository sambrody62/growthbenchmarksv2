from flask import Blueprint, request, jsonify, current_app
from random import randint

from fathom.lib import parse_params, authenticate, generate_account_benchmarks, get_benchmark_data, get_benchmarks, update_company_data, get_num_companies_with_data, generate_commentary, generate_anomalies, get_commentary, get_benchmark_list
from fathom.providers import FACEBOOK_PROVIDER, FACEBOOK_FAKE_PROVIDER
from fathom.lib.rankings import generate_account_rankings
from fathom.lib.util_days import get_today_as_str

from .connector import FacebookConnector
from .functions import get_account_list

facebook = Blueprint('facebook', __name__, template_folder='templates')

@facebook.route('/num_companies')
def num_companies():
    num_companies = get_num_companies_with_data(FACEBOOK_PROVIDER)
    return {"num_companies": num_companies}

@facebook.route('/set_conversion_event', methods=['POST'])
@authenticate
def set_conversion_event(user):
    data = request.get_json()
    is_example_company = data.get('is_example_company')
    account_id = data.get('account_id')
    conversion_event = data.get('conversion_event')
    account_ids = user.get('account_ids',[])
    fake_account_ids = user.get('fake_account_ids',[])

    if user.get('is_god') != True and account_id not in account_ids and account_id not in fake_account_ids:
        return jsonify({"success": False})
    
    db = current_app.extensions["db"]
    accounts_collection = db.collection('Accounts')
    prefix = 'fb-' 
    if is_example_company:
        prefix = 'fbfake-'
    company_ref = accounts_collection.document(f'{prefix}{account_id}')
    company_ref.update({"conversion_event": conversion_event})

    return jsonify({'success': True})

@facebook.route('/set_company_data', methods=['POST'])
@authenticate
def set_company_data(user):
    provider_id = FACEBOOK_PROVIDER
    list_name = "account_ids"

    data = request.get_json()
    company = data.get('company')
    if company.get('isExampleCompany') == True:
        provider_id = FACEBOOK_FAKE_PROVIDER
        list_name = "fake_account_ids"
    
    company_data = update_company_data(company, provider_id, list_name, user)
    return jsonify(company_data)

# Fetch Facebook metrics for a single company
@facebook.route('/fetch_metrics', methods=['GET'])
def fetch_metrics():
    # Get the parameters of the request
    arguments = ['access_token', 'account_id', 'testing']
    params = parse_params(request, arguments)

    facebook = FacebookConnector(account_id=params['account_id'], access_token=params['access_token'])

    if 'testing' in params and params['testing'] == True:
        data = facebook.fetch_metrics(save_data=False, skip_db=True)
    else:
        data = facebook.fetch_metrics()
    
    # Make the query to fetch metrics
    return jsonify(data)

# Load facebook metrics to firestore for all companies
@facebook.route('/load_metrics', methods=['GET'])
def load_metrics():
    """Cron job that triggers overnight to load Facebook benchmarks into firestore"""
    current_app.logger.info('Running load fb metrics')

    accounts = get_account_list()
    current_app.logger.info(f'For {len(accounts)} users')
    all_facebook_account_ids = set()
    db = current_app.extensions["db"]  
    today = get_today_as_str()
    
    for user in accounts:
        account_ids = user.get('account_ids')
        for account_id in account_ids:
            all_facebook_account_ids.add(account_id)
            # Get the company from the db
    accounts_needing_fetch_data_ref = db.collection(u'Accounts').where(u'last_date_saved', u'!=', u'{}'.format(today)
        ).where(u'has_completed_questionnaire', u'==', True).stream()
    accounts_already_fetched_data_ref = db.collection(u'Accounts').where(u'last_date_saved', u'==', u'{}'.format(today)
        ).where(u'has_completed_questionnaire', u'==', True).stream()

    accounts_needing_fetch_data = len([account for account in accounts_needing_fetch_data_ref])
    accounts_already_fetched_data = len([account for account in accounts_already_fetched_data_ref])

    # If completed questionnaire then add it to completed_questionnaire_facebook_accounts
    current_app.logger.info(f'For {len(all_facebook_account_ids)} Facebook Ad Accounts de-duped')
    current_app.logger.info(f'For {accounts_needing_fetch_data} Facebook Ad Accounts that need data')
    current_app.logger.info(f'For {accounts_already_fetched_data} Facebook Ad Accounts that were already fetched')

    # Trigger all account loads
    for user_account in accounts:
        access_token = user_account['access_token']

        for account_id in user_account['account_ids']:
            # Run task
            try:
                facebook = FacebookConnector(account_id=account_id, access_token=access_token)
                facebook.fetch_metrics(cron_job=True)

            except Exception as e:
                current_app.logger.exception(f"No insights to save for company {account_id}")
                current_app.logger.debug(str(e))
                pass

    return 'ok', 200

@facebook.route('/get_benchmark_data', methods=['POST'])
def get_benchmark_data_route():
    return get_benchmark_data(provider_id=FACEBOOK_PROVIDER)

@facebook.route('/generate_benchmarks', methods=['GET'])
def generate_benchmarks():
    return generate_account_benchmarks(provider_id=FACEBOOK_PROVIDER)

@facebook.route('/<benchmark_name>/get_benchmark', methods=['GET'])
def get_benchmarks_route(benchmark_name):
    return get_benchmarks(benchmark_name, provider_id=FACEBOOK_PROVIDER)

@facebook.route('/benchmarks/list', methods=['GET'])
def benchmarks_list():
    return get_benchmark_list(provider_id=FACEBOOK_PROVIDER)

@facebook.route('/get_commentary', methods=['GET'])
def get_facebook_commentary():
    return get_commentary(provider=FACEBOOK_PROVIDER)

@facebook.route('/generate_commentary')
def generate_facebook_commentary():
    return generate_commentary(provider=FACEBOOK_PROVIDER)


@facebook.route('/generate_rankings')
def generate_facebook_rankings():
    return generate_account_rankings(provider_id=FACEBOOK_PROVIDER)

@facebook.route('/generate_anomalies')
def generate_facebook_anomalies():
    return generate_anomalies(provider_id=FACEBOOK_PROVIDER)

    