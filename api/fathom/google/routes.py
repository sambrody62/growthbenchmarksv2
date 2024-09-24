from .connector import GoogleAdsConnector, FireStoreWrapper
import pandas as pd
from random import randint

# Errors:
from .errors import GenericGoogleAdsError
from fathom.components import NoAccessTokenOrRefreshToken, PlatformNotDefined

# Standard imports:
from flask import Blueprint, request, jsonify, current_app
from fathom.lib import parse_params, authenticate, generate_account_benchmarks, get_benchmark_data, get_benchmarks, update_company_data, get_num_companies_with_data, generate_commentary, get_commentary, generate_anomalies, get_benchmark_list
from fathom.providers import GOOGLE_PROVIDER, GOOGLE_FAKE_PROVIDER
from fathom.lib.rankings import generate_account_rankings

google = Blueprint('google', __name__, template_folder='templates')

@google.route('/num_companies')
def num_companies():
    num_companies = get_num_companies_with_data(GOOGLE_PROVIDER)
    return {"num_companies": num_companies}

# Custom Error Handlers:
@google.errorhandler(GenericGoogleAdsError)
def generic_google_ads_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@google.errorhandler(NoAccessTokenOrRefreshToken)
def no_token_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@google.errorhandler(PlatformNotDefined)
def platform_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# TEST ROUTE:
@google.route('/test', methods=['GET'])
def test_route():
    return 'Hello World'

## USER SIGN UP FLOW ROUTES:

# 1. User sign up flow, we can get a list of accounts using this method:
@google.route('/extract_accessible_accounts', methods=['POST'])
def extract_accessible_accounts():
    data = request.json
    google_ads = GoogleAdsConnector(refresh_token=data['refresh_token'], platform='GOOGLE_ADS')
    return google_ads.get_primary_accounts_list().to_json(orient='records')

# 2. Test route to see if there is any traffic from a specific domain:
@google.route('/test_account_traffic', methods=['POST'])
def test_account_traffic() -> pd.DataFrame:
    data = request.json
    google_ads = GoogleAdsConnector(account_id=data.get('account_id'), access_token=data.get('access_token'), 
            refresh_token=data.get('refresh_token'), login_id=data.get('login_id'), platform='GOOGLE_ADS')
    result = google_ads.test_account_for_data_last_30_days()
    if result is not None:
        return jsonify({'state': True})
    else:   
        return jsonify({'state': False})

# 3. Test route for generating insights:
@google.route('/generate_all_data_example', methods=['POST'])
def generate_all_data() -> pd.DataFrame:
    data = request.json
    google_ads = GoogleAdsConnector(account_id=data.get('account_id'), access_token=data.get('access_token'), 
            refresh_token=data.get('refresh_token'), login_id=data.get('login_id'), platform='GOOGLE_ADS')
    result = google_ads.get_insights()
    return jsonify(result)

### DATA PIPELINE ROUTES:

# Fetch and save the Google metrics for a single company:
@google.route('/fetch_metrics', methods=['GET', 'POST'])
def fetch_metrics():
    # Get the parameters of the request
    arguments = ['refresh_token', 'account_id']
    params = parse_params(request, arguments)

    firestore_wrapper = FireStoreWrapper(platform_prefix='google') 
    account_doc = firestore_wrapper.read_account_document(account_id=params.get('account_id'))
    login_id = account_doc.get('login_id')

    # Only fetching the metrics for Google documents:
    if account_doc:
        # Setting up the Google Ads API client:
        if login_id:
            print(f"The login_id is: {login_id}")
            google_ads = GoogleAdsConnector(account_id=params.get('account_id'), refresh_token=params.get('refresh_token'), 
            login_id=login_id, platform='GOOGLE_ADS')
        else:
            google_ads = GoogleAdsConnector(account_id=params.get('account_id'), 
            refresh_token=params.get('refresh_token'), platform='GOOGLE_ADS')

    result = google_ads.fetch_metrics()
    # Make the query to fetch metrics
    return jsonify(result)

# Load google_ads metrics to firestore for all companies:
@google.route('/load_metrics', methods=['GET'])
def load_metrics():
    """Cron job that triggers overnight to load Google benchmarks into firestore"""
    current_app.logger.info('Running load fb metrics')

    # This has changed in relation to the Facebook route:
    firestore_wrapper = FireStoreWrapper(platform_prefix='google') 
    accounts = firestore_wrapper.get_account_list(account_ids_platform='google_account_ids')
    current_app.logger.info(f'For {len(accounts)} accounts')
    
    # Loop through all of the accounts:
    for user_account in accounts:
        # This has changed in relation to the Facebook route:
        refresh_token = user_account['refresh_token']
        
        for account_id in user_account['account_ids']:
            current_app.logger.info(f'Loading metrics for {account_id}')

            # Only return the an document if they include google within the document prefix:
            account_doc = firestore_wrapper.read_account_document(account_id=account_id)

            # Only fetch if is a google document:
            if account_doc:
                login_id = account_doc.get('login_id')

                # Run a task:
                try:
                    # Setting up the Google Ads API client:
                    if login_id:
                        google_ads = GoogleAdsConnector(account_id=account_id, refresh_token=refresh_token, login_id=login_id)
                    else:
                        google_ads = GoogleAdsConnector(account_id=account_id, refresh_token=refresh_token)
                    
                    # Fetch and store the metrics:
                    google_ads.fetch_metrics(cron_job=True)
                    current_app.logger.info(f"Insights saved for company {account_id}")
                except Exception as e:
                    current_app.logger.exception(f"No insights to save for company {account_id}")
                    current_app.logger.debug(str(e))
                    pass

                current_app.logger.info(f'Finished loading google metrics for {account_id}')

    current_app.logger.info('Finished running load google metrics')
    return 'ok', 200

@google.route('/set_company_data', methods=['POST'])
@authenticate
def set_company_data(user):
    provider_id = GOOGLE_PROVIDER
    list_name = "account_ids"

    data = request.get_json()
    company = data.get('company')
    if company.get('isExampleCompany') == True:
        provider_id = GOOGLE_FAKE_PROVIDER
        list_name = "fake_account_ids"
    
    company_data = update_company_data(company, provider_id, list_name, user)

    return jsonify(company_data)

@google.route('/generate_benchmarks', methods=['GET'])
def generate_benchmarks():
    return generate_account_benchmarks(provider_id=GOOGLE_PROVIDER)    

@google.route('/benchmarks/list', methods=['GET'])
def benchmarks_list():
    return get_benchmark_list(provider_id=GOOGLE_PROVIDER)
    
@google.route('/<benchmark_name>/get_benchmark', methods=['GET'])
def get_benchmarks_route(benchmark_name):
    return get_benchmarks(benchmark_name, provider_id=GOOGLE_PROVIDER)

@google.route('/get_benchmark_data', methods=['POST'])
def get_benchmark_data_route():
    return get_benchmark_data(provider_id=GOOGLE_PROVIDER)

@google.route('/get_commentary', methods=['GET'])
def get_google_commentary():
    return get_commentary(provider=GOOGLE_PROVIDER)

@google.route('/generate_commentary')
def generate_google_commentary():
    return generate_commentary(provider=GOOGLE_PROVIDER)


@google.route('/generate_rankings')
def generate_google_rankings():
    return generate_account_rankings(provider_id=GOOGLE_PROVIDER)

@google.route('/generate_anomalies')
def generate_google_anomalies():
    return generate_anomalies(provider_id=GOOGLE_PROVIDER)