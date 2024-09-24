from flask import current_app
from random import randint
from fathom.lib import similar_accounts

def update_company_data(company, provider_id, list_name, user):
    db = current_app.extensions["db"]
    account_id = company.get('account_id')
    
    if account_id == None:
        account_id = f'{randint(0,1000000000000)}'
        company['account_id'] = account_id
        # TODO check that this fake account id has not been used before!
    if company.get('isExampleCompany') == True:
        # get the fake 
        fake_account_ids = user.get(list_name)
        if fake_account_ids == None:
            fake_account_ids = []
        if account_id not in fake_account_ids:
            fake_account_ids.append(account_id)

            # Update this customer's fake account ids
            users_collection = db.collection('users')
            users_stream = users_collection.where('uid', '==', user['uid']).stream()
            for existing_user_ref in users_stream: 
                users_collection.document(existing_user_ref.id).update({ list_name: fake_account_ids})
    else:
        company['has_completed_questionnaire'] = True
        company_list = user.get(list_name, [])
        if user.get('is_god') != True and company_list != None and account_id not in company_list:
            return {"success": False}

    companies_collection = db.collection('Accounts')
    company_ref = companies_collection.document(f'{provider_id}-{account_id}')
    # Insert a new company if there isn't one already (e.g. if there is a fake company)
    if company_ref.get().exists:
        company_ref.update(company)
    else:
        companies_collection.document(f'{provider_id}-{account_id}').set(company)

    is_example_company = company.get('isExampleCompany') == True
    new_similar_accounts_response = similar_accounts(account_id, provider_id, is_example_company)
    new_similar_companies = [x.strip() for x in new_similar_accounts_response.split(',')]
    
    # Make sure we get the new company that might have been saved back from the db
    company_ref = companies_collection.document(f'{provider_id}-{account_id}')
    company_ref.update(
        {
            "similar_companies": new_similar_companies
        }
    )

    updated_company = company
    updated_company['similar_companies'] = new_similar_companies

    return {'success': True, "updatedCompany": updated_company}