from flask import current_app

def move_company_to_accounts(account_id):
    db = current_app.extensions['db']
    new_account_ref = db.collection('Accounts').document(f'fb-{account_id}')

    if new_account_ref.get().exists:
        current_app.logger.info(f'Company already exists in new structure {account_id}')
        pass
    else:
        old_company_ref = db.collection('companies').document(account_id)
        old_company_doc = old_company_ref.get().to_dict()

        new_account_ref = db.collection('Accounts').document(f'fb-{account_id}')
        new_account_ref.set({
            'account_id': old_company_doc.get('account_id'),
            'currency': old_company_doc.get('currency'),
            'has_completed_questionnaire': old_company_doc.get('hasCompletedQuestionnaire', False),
            'has_fetched_fb_data': old_company_doc.get('hasFetchedFBData', False),
            'industry': old_company_doc.get('industry'),
            'last_date_saved': old_company_doc.get('lastDateSaved'),
            'location': old_company_doc.get('location'),
            'model': old_company_doc.get('model'),
            'name': old_company_doc.get('name'),
            'property': old_company_doc.get('property'),
            'similar_companies': old_company_doc.get('similar_companies'),
            'spend': old_company_doc.get('spend'),
        })