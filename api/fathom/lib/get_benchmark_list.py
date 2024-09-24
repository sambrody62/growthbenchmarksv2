from flask import jsonify, current_app
from fathom.providers import FACEBOOK_PROVIDER

def get_benchmark_list(provider_id=FACEBOOK_PROVIDER):    
    db = current_app.extensions['db']
    all_benchmarks_stream = db.collection('Benchmarks').stream()
    all_benchmarks = []
    prefix = f'{provider_id}-'
    for benchmark in all_benchmarks_stream:
        if prefix in benchmark.id:
            all_benchmarks.append(benchmark.id[len(prefix):])
    return jsonify({'benchmarks':all_benchmarks})