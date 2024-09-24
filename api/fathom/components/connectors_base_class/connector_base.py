from .errors import NoAccessTokenOrRefreshToken, PlatformNotDefined
from flask import current_app

class BaseConnector():
    def __init__(self, account_id:str=None, access_token:str=None, 
    refresh_token:str=None, platform:str=None):

        # Raise an error if the platform is False and not in the keys within the config.py:
        if platform == None or platform not in current_app.config['CONNECTORS'].keys():
            raise PlatformNotDefined(message=f'''Use a previously configured OAuth connector, check here: 
            {current_app.config['CONNECTORS'].keys()}''')

        # Assigning the platform context:
        self.platform = platform

        # If the platform is google setup a dev token:
        if platform == "GOOGLE_ADS":
            self.developer_token =current_app.config['CONNECTORS'][platform]['APP_DEVELOPER_TOKEN'] 

        # Application information:
        self.app_id = current_app.config['CONNECTORS'][platform]['APP_ID']
        self.app_secret = current_app.config['CONNECTORS'][platform]['APP_SECRET']

        # Account information:
        self.account_id = account_id

        # Setting the access_token and refresh token:
        self.access_token = access_token
        self.refresh_token = refresh_token
        
        # Check to see whether we don't have an access_token or refresh_token:
        if self.access_token is None and self.refresh_token is None:
            raise NoAccessTokenOrRefreshToken(message='''There hasn't been either a refresh or
             access_token set. Please set one when creating a connector.''')    

        # Setting up the database:
        self.prefix = current_app.config['CONNECTORS'][platform]['PREFIX']
        self.db = current_app.extensions["db"]

        # FireStore Google metric/account references:
        self.account_ref = self.db.collection(u'Accounts').document(f'{self.prefix}-{account_id}')
        self.metrics_ref = self.account_ref.collection('Metrics')
        self.account = self.account_ref.get().to_dict()

        if self.account:
            self.last_date_saved = self.account.get('last_date_saved')
            self.has_completed_questionnaire = self.account.get('has_completed_questionnaire')
        else:
            self.last_date_saved = None
            self.has_completed_questionnaire = False