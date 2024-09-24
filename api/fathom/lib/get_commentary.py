from flask import current_app

from fathom.providers import FACEBOOK_PROVIDER
from fathom.lib.util_days import  get_start_and_end_dates_for_2_months_as_str

def get_commentary(provider=FACEBOOK_PROVIDER):
    db = current_app.extensions['db']
    benchmarks = db.collection('Benchmarks').stream()
    start_date, end_date = get_start_and_end_dates_for_2_months_as_str()
    all_benchmarks = dict()
    for benchmark in benchmarks:
        if (provider+'-' in benchmark.id):
            commentaries = db.collection(u'Benchmarks').document(benchmark.id).collection(u'Commentary')
            if commentaries:
                last_month = commentaries.document(end_date[:7]).get().to_dict()
                prev_month = commentaries.document(start_date[:7]).get().to_dict()

                # use the max of the two months
                accounts = 0
                if last_month:
                    accounts = last_month.get('accounts', 0)
                if prev_month:
                    accounts = max(accounts, prev_month.get('accounts', 0))

                all_benchmarks[benchmark.id] = {
                    'last_month': last_month,
                    'prev_month': prev_month,
                    'accounts': accounts
                }

    return all_benchmarks