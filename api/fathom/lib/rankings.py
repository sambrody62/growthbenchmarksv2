from flask import current_app
from fathom.lib.util_days import get_this_month_as_str, get_last_month_as_str, get_date_as_month_str
from fathom.providers import FACEBOOK_PROVIDER, GOOGLE_PROVIDER
from fathom.lib.util_send_email import send_email
from fathom.lib.email_templates.account_ranking import account_ranking_email

## Possible values for ranking are:

# Top 5% of accounts
# Top 10% of accounts
# Top 20% of accounts
# Above Average (top 35% of accounts)
# Average (middle 30% of accounts)
# Below Average (bottom 35%  of accounts)
# Bottom 20% of accounts
# Bottom 10% of accounts
# Bottom 5% of accounts

# If a metric being high is bad (CPC), top % of accounts means lower

def generate_account_rankings(provider_id=FACEBOOK_PROVIDER):
    db = current_app.extensions["db"]

    last_month = get_last_month_as_str()
    accounts_collection = db.collection(u'Accounts')
    accounts_ref = accounts_collection.where(u'has_completed_questionnaire', u'==', True).stream()

    # make a list of all accounts
    account_metrics = []

    for account in accounts_ref:
        account_document_id = account.id
        if f"{provider_id}-" in account_document_id:
            print(f'checking rankings for {account_document_id}')

            # sum up the metrics for last month
            account_name = account.to_dict().get("name", "")
            account_id = account.to_dict().get("account_id", "")
            last_month_metrics = {"account_id": account_id, "month": get_this_month_as_str(), "provider_id": provider_id, "account_name": account_name}
            metrics_ref = account.reference.collection('Metrics').stream()
            
            has_data = False
            for stats in metrics_ref:
                has_data = True
                date_str = stats.id
                month_date = get_date_as_month_str(date_str)
                if month_date == last_month:
                    data = stats.to_dict()
                    for metric, value in data.items():
                        if metric in ['id', 'date_start', 'date_saved', 'account_id', 'date']:
                            continue
                        elif metric in last_month_metrics:
                            last_month_metrics[metric] += float(value)
                        else:
                            last_month_metrics[metric] = float(value)

            filter_metrics = add_filter_metrics(last_month_metrics)
            if has_data:
                # add to the list a object like this:
                # {"account_id", "account_name", "month", "provider_id", "clicks", "spend", "impressions", "cpc", "ctr", "cpm"} 
                account_metrics.append(filter_metrics)

    print(f'Generating rankings for all companies')
    # sort the account_metrics to get rankings
    cpm_sort = sorted(account_metrics, key=lambda x: x.get('cpm', float('inf')), reverse=False)
    ctr_sort = sorted(account_metrics, key=lambda x: x.get('ctr', float('-inf')), reverse=True)
    cpc_sort = sorted(account_metrics, key=lambda x: x.get('cpc', float('inf')), reverse=False)

    total = len(account_metrics)
    ranked_metrics = {}

    # add the rankings to each account
    for i in range(0, len(cpm_sort)):
        account_document_id = cpm_sort[i]['account_id']
        if account_document_id in ranked_metrics:
            rank_data = ranked_metrics[account_document_id].copy()
            
            rank_data['cpm_rank'] = i
            rank_data['cpm_rank_text'] = get_ranking_text(i, total)
            
            ranked_metrics[account_document_id] = rank_data
        else:
            rank_data = cpm_sort[i].copy()
            
            rank_data['cpm_rank'] = i
            rank_data['cpm_rank_text'] = get_ranking_text(i, total)
            
            ranked_metrics[account_document_id] = rank_data
    
    for i in range(0, len(ctr_sort)):
        account_document_id = ctr_sort[i]['account_id']
        if account_document_id in ranked_metrics:
            rank_data = ranked_metrics[account_document_id].copy()
            
            rank_data['ctr_rank'] = i
            rank_data['ctr_rank_text'] = get_ranking_text(i, total)
            
            ranked_metrics[account_document_id] = rank_data
        else:
            rank_data = ctr_sort[i].copy()
            
            rank_data['ctr_rank'] = i
            rank_data['ctr_rank_text'] = get_ranking_text(i, total)
            
            ranked_metrics[account_document_id] = rank_data

    for i in range(0, len(cpc_sort)):
        account_document_id = cpc_sort[i]['account_id']
        if account_document_id in ranked_metrics:
            rank_data = ranked_metrics[account_document_id].copy()
            
            rank_data['cpc_rank'] = i
            rank_data['cpc_rank_text'] = get_ranking_text(i, total)
            
            ranked_metrics[account_document_id] = rank_data
        else:
            rank_data = cpc_sort[i].copy()
            
            rank_data['cpc_rank'] = i
            rank_data['cpc_rank_text'] = get_ranking_text(i, total)
            
            ranked_metrics[account_document_id] = rank_data

    # save all the accounts with rankings
    save_account_rankings(ranked_metrics)
    print(f'Saving rankings for all companies')
    return 'ok'    

def save_account_rankings(ranked_metrics):
    db = current_app.extensions["db"]
    rankings_ref = db.collection(u'Rankings')
    for account_id, ranked_data in ranked_metrics.items():
        rank_ref = rankings_ref.document(f"{ranked_data['provider_id']}-{account_id}-{ranked_data['month']}")
        # object looks like this:
        # {"cpc_rank", "cpm_rank", "ctr_rank", "cpc_rank_text", "cpm_rank_text", "ctr_rank_text", 
        #   "account_id", "account_name", "month", "provider_id", "clicks", "spend", "impressions", "cpc", "ctr", "cpm"}
        rank_ref.set(ranked_data)

def get_ranking_text(rank, total):
    # Top 5% of accounts
    # Top 10% of accounts
    # Top 20% of accounts
    # Above Average (top 35% of accounts)
    # Average (middle 30% of accounts)
    # Below Average (bottom 35%  of accounts)
    # Bottom 20% of accounts
    # Bottom 10% of accounts
    # Bottom 5% of accounts
    percentile = rank / float(total)
    if percentile <= 0.05:
        return "Top 5% of accounts"
    elif percentile <= 0.10:
        return "Top 10% of accounts"
    elif percentile <= 0.20:
        return "Top 20% of accounts"
    elif percentile <= 0.35:
        return "Above Average (top 35% of accounts)"
    elif percentile <= 0.65:
        return "Average (middle 30% of accounts)"
    elif percentile <= 0.80:
        return "Below Average (bottom 35%  of accounts)"
    elif percentile <= 0.90:
        return "Bottom 20% of accounts"
    elif percentile <= 0.95:
        return "Bottom 10% of accounts"
    else:
        return "Bottom 5% of accounts"

def add_filter_metrics(company_data):
    # takes company data
    # returns filter metrics
    result = company_data.copy()
    if float(company_data.get('clicks', 0)) > 0:
        cpc = float(company_data['spend'])/float(company_data['clicks'])
        result['cpc'] = cpc

        ctr = 100 * float(company_data['clicks'])/float(company_data['impressions'])
        result['ctr'] = ctr

    if float(company_data.get('impressions', 0)) > 0:
        cpm = 1000 * float(company_data['spend']) / float(company_data['impressions'])
        result['cpm'] = cpm
    
    return result 


def find_rankings_for_an_account(account_id, provider_id):
    db = current_app.extensions["db"]
    rankings_ref = db.collection('Rankings')
    this_month = get_this_month_as_str()
    rankings_stream = rankings_ref.where('month', "==", this_month).where('account_id', "==", account_id).where('provider_id', "==", provider_id).stream()

    rankings_data = []
    for ranking in rankings_stream:
        rank_data = ranking.to_dict()
        rankings_data.append(rank_data)

    return rankings_data

def send_ranking_email_to_user(email, account_rankings, actually_send=True):
    SUBJECT = 'Growthbenchmarks.com - Where are your accounts ranked?'
    HTML_TEMPLATE = account_ranking_email(account_rankings)
    if (actually_send == False):
        return HTML_TEMPLATE

    send_email(email, SUBJECT, HTML_TEMPLATE)
    print(f"{len(account_rankings)} ranks sent to {email}")
    return HTML_TEMPLATE

def format_ranking_as_str(ranking):
    """
    {
      {"cpc_rank", "cpm_rank", "ctr_rank", "cpc_rank_text", "cpm_rank_text", "ctr_rank_text", 
       "account_id", "account_name", "month", "provider_id", "clicks", "spend", "impressions", "cpc", "ctr", "cpm"}
    }
    """
    result = f"<h2>{ranking['account_name']} ({ranking['account_id']})</h2><br/>"
    for metric in ['cpc','ctr','cpm']:
        long_provider = 'facebook'
        if (ranking['provider_id'] == 'google'):
            long_provider = 'google'
        account_link=f"https://growthbenchmarks.com/{long_provider}/{ranking['account_id']}/{metric}"
        result += f"– <a href='{account_link}'>{metric.upper()}</a> {round(float(ranking.get(metric,0)),2)} was ranked as \"{ranking.get(metric + '_rank_text')}\"<br/>"
    return result

def send_ranking_emails(testing=True, actually_send=True):
    db = current_app.extensions["db"]
    this_month = get_this_month_as_str()
    rankings_count = 0
    user_count = 0
    
    if testing:
        users_ref = db.collection('users').where("is_god", "==", True).stream()
    else:
        users_ref = db.collection('users').where("is_subscribed", "==", True).stream()

    all_emails = ""

    for user in users_ref:
        user_data = user.to_dict()

        if actually_send and user_data.get('rankings_processed') == this_month:
            continue

        all_rankings = []
        email = user_data.get('email', '')
        print("User: ", email)

        # loop through facebook accounts
        user_facebook_account_ids = user_data.get('account_ids', []) or [] # some account_ids are null not an array
        for account_id in user_facebook_account_ids:
            print(f"Getting rankings for {account_id}")
            all_rankings.extend(find_rankings_for_an_account(account_id, provider_id=FACEBOOK_PROVIDER))

        # loop through google accounts
        user_google_account_ids = user_data.get('google_account_ids', []) or []
        for account_id in user_google_account_ids:
            all_rankings.extend(find_rankings_for_an_account(account_id, provider_id=GOOGLE_PROVIDER))

        if len(all_rankings) > 0:
            user_count += 1
            rankings_count += len(all_rankings)

            print("Rankings: ", len(all_rankings))
            print("Example: ", all_rankings[0])

            if (actually_send):
                send_ranking_email_to_user(email, all_rankings, actually_send)
            else:
                all_emails += send_ranking_email_to_user(email, all_rankings, actually_send)
        else:
            print("No Rankings")

        user.reference.update({"rankings_processed": this_month})

    print(f"Sent {rankings_count} rankings to {user_count} users")
    return all_emails
