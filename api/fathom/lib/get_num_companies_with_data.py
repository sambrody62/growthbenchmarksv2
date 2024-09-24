from flask import current_app

def get_num_companies_with_data(provider_id):
    db = current_app.extensions["db"]
    accounts_with_data = db.collection(u'Accounts').where(u'has_completed_questionnaire', u'==', True).stream()
    num_companies = 0
    for account in accounts_with_data:
        if (account.id.startswith(f'{provider_id}-')):
            num_companies += 1
    return num_companies