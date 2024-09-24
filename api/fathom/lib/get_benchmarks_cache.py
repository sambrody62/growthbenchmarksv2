from flask import current_app, jsonify
from fathom.lib.util_days import get_today_as_str, get_since_and_until_dates_as_str

from .convert_to_cache import convert_to_cache

def get_benchmarks_cache():
    today = get_today_as_str()
    ninety_days_ago = get_since_and_until_dates_as_str(days=90)

    db = current_app.extensions["db"]
    benchmark_collection_ref = db.collection(u'Benchmarks')

    benchmark_list = [doc.id for doc in benchmark_collection_ref.stream()]

    cachedBenchmarks = {
            'ctr': {},
            'cpm': {},
            'cpc': {}
        }

    for benchmark in benchmark_list:
        benchmark_ref = benchmark_collection_ref.document(benchmark)
        metrics_ref = benchmark_ref.collection('Metrics')

        results = metrics_ref.where(u'date', u'>=', u'{}'.format(ninety_days_ago)).stream()

        data = list()
        for doc in results:
            data.append(doc.to_dict())

        calculated = convert_to_cache(data)
        
        cachedBenchmarks['updated'] = today
        for metric, values in calculated.items():
            cachedBenchmarks[metric][benchmark] = values

    return cachedBenchmarks

 # cachedBenchmarks = {
        #     "cpc": {
        #         "all_companies": {
        #         "mean": "1.00",
        #         "delta30": "10",
        #         "delta90": "20",
        #         },
        #     },
        #     "cpm": {
        #         "all_companies": {
        #         "mean": "10.00",
        #         "delta30": "10",
        #         "delta90": "20",
        #         },
        #     },
        #     "ctr": {
        #         "all_companies": {
        #         "mean": "1.00",
        #         "delta30": "10",
        #         "delta90": "20",
        #         },
        #     },
        #     "cpa": {
        #         "all_companies": {
        #         "mean": "10.00",
        #         "delta30": "10",
        #         "delta90": "20",
        #         },
        #     },
        #     "cvr": {
        #         "all_companies": {
        #         "mean": "10.00",
        #         "delta30": "10",
        #         "delta90": "20",
        #         },
        #     },
        #     "acv": {
        #         "all_companies": {
        #         "mean": "20.00",
        #         "delta30": "10",
        #         "delta90": "20",
        #         },
        #     },
        #     "roi": {
        #         "all_companies": {
        #         "mean": "100.00",
        #         "delta30": "10",
        #         "delta90": "20",
        #         },
        #     },
        # }
