from flask.json import jsonify
from facebook_business.api import FacebookAdsApi # pylint: disable=import-error
from facebook_business.adobjects.adaccount import AdAccount # pylint: disable=import-error
from flask import current_app
import requests # pylint: disable=import-error
import pandas as pd # pylint: disable=import-error
import numpy as np # pylint: disable=import-error

facebook_graph_root_url = "https://graph.facebook.com/v12.0/"

def get_all_ad_accounts(response, all_ad_accounts, access_token):
    response_json = response.json()
    
    ad_accounts = response_json.get('data')
    all_ad_accounts = list()
    for ad_account in ad_accounts:
        ad_account_details = {
            "account_id": ad_account.get("account_id"),
            "currency": ad_account.get("currency"),
            "name": ad_account.get("name"),
        }
        all_ad_accounts.append(ad_account_details)

    paging = response_json.get('paging')
    paging_next = paging.get('next')
    if paging_next != None:
        new_ad_accounts = get_all_ad_accounts(requests.get(paging_next), all_ad_accounts, access_token)
        all_ad_accounts = all_ad_accounts + new_ad_accounts

    return all_ad_accounts

def get_facebook_ad_accounts(user_id, access_token):
    url = facebook_graph_root_url + user_id + "/adaccounts"
    payload = {
        "access_token": access_token,
        "fields": "name, currency, account_id"
    }
    response = requests.get(
        url,
        params=payload,
    )    
    return get_all_ad_accounts(response, [], access_token)

def get_long_lived_access_token(short_access_token):
    facebook_app_id = current_app.config['CONNECTORS']['FACEBOOK']['APP_ID']
    facebook_app_secret = current_app.config['CONNECTORS']['FACEBOOK']['APP_SECRET']
    url = facebook_graph_root_url + "oauth/access_token"
    payload = {
        "grant_type": "fb_exchange_token",
        "client_id": facebook_app_id,
        "client_secret": facebook_app_secret,
        "fb_exchange_token": short_access_token,
    }
    response = requests.get(
        url,
        params=payload,
    )
    response_json = response.json()
    return response_json.get('access_token')

def get_account_list():
    db = current_app.extensions["db"]
    users_ref = db.collection(u'users')
    users = users_ref.stream()

    accounts = list()
    for user_doc in users:
        user_doc = user_doc.to_dict()
        user_account_ids = user_doc.get('account_ids')
        user_access_token = user_doc.get('access_token')
        if user_account_ids and user_access_token:
            user_accounts = dict()
            user_accounts['access_token'] = user_access_token
            user_accounts['account_ids'] = user_account_ids
            accounts.append(user_accounts)
    return accounts