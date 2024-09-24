from unittest.mock import Mock, patch
from datetime import datetime as dt
from flask import current_app

from fathom.facebook.connector import FacebookConnector

@patch('fathom.facebook.connector.dt')
@patch('fathom.facebook.connector.AdAccount')
@patch('fathom.facebook.connector.FacebookAdsApi')
def test_fetch_metrics(MockFacebookAdsApi, MockAdAccount, mock_dt, fb_response, fb_processed, tester):
    # Mock datetime
    mock_dt.today = Mock(return_value=dt(2021, 3, 1))

    # Add company to db
    db = current_app.extensions['db']
    account_ref = db.collection(u'Accounts').document(f'fb-1234')
    account_ref.set({
        "name": "ACME Inc",
        "last_date_saved": "2021-02-17", # old date --> force fb pull
        "has_completed_questionnaire": True
    })

    CONNECTORS = {
        "FACEBOOK": {
            "APP_ID": "appid",
            "APP_SECRET": "secret"
        },
    }

    # change env variables
    tester.application.config["CONNECTORS"] = CONNECTORS

    # Mocking get_insights response
    MockAdAccount.return_value.get_insights = Mock(return_value=fb_response)

    # Run the function we're testing
    facebook = FacebookConnector(account_id="1234", access_token="a0b1c2d3e4f5g6h7i8j9")
    insights = facebook.fetch_metrics()

    assert MockFacebookAdsApi.init.called
    assert MockAdAccount().get_insights.called
    assert insights[0] == fb_processed[0]
    assert insights[-1] == fb_processed[-1]
    assert insights == fb_processed 


    