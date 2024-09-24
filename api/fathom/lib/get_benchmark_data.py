from flask import request, jsonify, current_app
from fathom.providers import FACEBOOK_PROVIDER
from fathom.lib import currency_conversions

def get_benchmarks(benchmark_name, provider_id=FACEBOOK_PROVIDER):
    # Get benchmark data
    dates = []
    benchmark = {}
    db = current_app.extensions['db']
    benchmarks_collection = db.collection('Benchmarks')
    benchmark_metrics = benchmarks_collection.document(f'{provider_id}-{benchmark_name}').collection('Metrics').get()
    for benchmark_metric_item in benchmark_metrics:
        doc_datum = benchmark_metric_item.to_dict()
        metric_date = doc_datum.get('date')
        if metric_date not in dates:
            dates.append(metric_date)
        benchmark[metric_date] = doc_datum

    dates.sort()
    return {'dates': dates, 'benchmark': benchmark}

def get_benchmark_data(provider_id=FACEBOOK_PROVIDER):
    data = request.get_json()
    currency = data.get('currency')
    selected_benchmarks = data.get('selectedBenchmarks')

    if currency != None:
        target_currency = currency
    else:
        target_currency = 'USD'
    target_currency_conversion = currency_conversions.get(target_currency)

    benchmarks = list()
    for selected_benchmark in selected_benchmarks:
        benchmark_data = get_benchmark_data_from_db(selected_benchmark, list(), target_currency_conversion, provider_id)
        benchmarks.append(benchmark_data)

    return jsonify({
        "benchmarks": benchmarks
        })

def get_benchmark_data_from_db(selected_benchmark, dates, target_currency_conversion, provider_id=FACEBOOK_PROVIDER):
    benchmark = dict()
    
    # Get benchmark data
    db = current_app.extensions["db"]
    benchmarks_collection = db.collection('Benchmarks')
    benchmark_metrics = benchmarks_collection.document(f'{provider_id}-{selected_benchmark}').collection('Metrics').get()
    for benchmark_metric_item in benchmark_metrics:
        doc_datum = benchmark_metric_item.to_dict()
        metric_date = doc_datum.get('date')
        if metric_date not in dates:
            dates.append(metric_date)
        
        for key in doc_datum.keys():
            if key in ['date_start', 'date_saved', 'account_id', 'last_date_saved', 'benchmark', 'date']:
                continue
            if metric_date not in benchmark:
                benchmark[metric_date] = dict()
            value = float(doc_datum.get(key))
            if key == 'spend' or (len(key) > 6 and key[-6:] == '.value'):
                value = value * target_currency_conversion
            
            benchmark[metric_date][key] = value

    dates.sort()

    return {"dates": dates, "benchmark": benchmark, "name": selected_benchmark}