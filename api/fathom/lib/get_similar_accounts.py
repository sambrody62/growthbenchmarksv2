from flask import current_app
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_accounts_df(account_id, provider_id, is_fake_company):
    keep_keys = ['industry', 'location', 'model', 'property', 'spend']

    # we need to make sure we get the companies with real data, if this is a fake company
    base_provider_id = provider_id.replace('fake', '')

    db = current_app.extensions["db"]
    accounts_collection = db.collection(u'Accounts')
    posts_ref = accounts_collection.where(u'has_completed_questionnaire', u'==', True) # Maybe also check they are still live and so check last_saved_date
    results = posts_ref.stream()
    accounts = list()
    for doc in results:
        if f'{base_provider_id}-' in doc.id:
            account_data = doc.to_dict()
            all_keys = list(account_data.keys())
            for k in all_keys:
                if k not in keep_keys:
                    account_data.pop(k, None)

            account_data['account_id'] = doc.id
            accounts.append(account_data)
        else:
            pass

    # If it is a fake company then we also want to append this to the list
    if is_fake_company:
        main_doc_id = f'{provider_id}-{account_id}'
        account_data = accounts_collection.document(main_doc_id).get().to_dict()
        all_keys = list(account_data.keys())
        for k in all_keys:
            if k not in keep_keys:
                account_data.pop(k, None)

        account_data['account_id'] = main_doc_id
        accounts.append(account_data)
    
    return pd.DataFrame(accounts)

def similar_accounts(account_id, provider_id, is_fake_company):
    accounts = get_accounts_df(account_id, provider_id, is_fake_company)

    # Create the soup feature
    accounts['soup'] = accounts.apply(lambda x: ' '.join([x[col] for col in accounts.columns if col != 'account_id']), axis=1)

    # create the count matrix
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(accounts['soup'])

    # Compute the Cosine Similarity matrix based on the count_matrix
    cosine_sim = cosine_similarity(count_matrix, count_matrix)

    # Reset index of your main DataFrame and construct reverse mapping
    similar_acccounts = accounts.reset_index()
    indices = pd.Series(accounts.index, index=similar_acccounts['account_id'])

    lookup_key = f"{provider_id}-{account_id}"
    # Get the index of the company that matches the provider id and account id (db index)
    if (lookup_key in indices):
        idx = indices[lookup_key]

        # Get the pairwsie similarity scores of all companies with that company
        sim_scores = list(enumerate(cosine_sim[idx]))

        # Sort the companies based on the similarity scores
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        # Get the company indices
        account_indices = [i[0] for i in sim_scores]

        results = list()

        # Remove itself (it might not be at the first spot)
        for account_index in account_indices:
            if (len(results) < 5):
                account = accounts['account_id'].iloc[account_index]
                if account != lookup_key:
                    results.append(account)
            else:
                pass


        # Return the top 5 most similar companies
        return ','.join(results)

    else:
        raise NameError('No account with that ID exists on the live database')