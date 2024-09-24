import numpy as np # pylint: disable=import-error

def convert_to_cache(data):
    # convert to metric format
    metrics = {}
    for day in data:
        for metric, value in day.items():
            if metric in metrics:
                metrics[metric] += [value]
            else:
                metrics[metric] = [value]

    # create deltas
    deltas = {
        'link_click': {},
        'spend': {},
        'impressions': {}
    }

    for metric, values in metrics.items():
        if metric in ['link_click', 'spend', 'impressions']:
            if (values[-1] == 0 or len(values) == 0):
                deltas[metric]["delta30"] = float('inf')
                deltas[metric]["delta90"] = float('inf')
                deltas[metric]["mean"] = np.mean(values)
            else:
                deltas[metric]["delta30"] = values[-30] / values[-1]
                deltas[metric]["delta90"] = values[0] / values[-1]
                deltas[metric]["mean"] = np.mean(values)

    calculated = {}


    try:
        calculated['ctr'] = {
            'delta30': deltas['link_click']['delta30'] / deltas['impressions']['delta30'],
            'delta90': deltas['link_click']['delta90'] / deltas['impressions']['delta90'],
            'mean': deltas['link_click']['mean'] / deltas['impressions']['mean'],
        }
        calculated['cpm'] = {
            'delta30': deltas['spend']['delta30'] / deltas['impressions']['delta30'] * 1000,
            'delta90': deltas['spend']['delta90'] / deltas['impressions']['delta90'] * 1000,
            'mean': deltas['spend']['mean'] / deltas['impressions']['mean'] * 1000,
        }
        calculated['cpc'] = {
            'delta30': deltas['spend']['delta30'] / deltas['link_click']['delta30'],
            'delta90': deltas['spend']['delta90'] / deltas['link_click']['delta90'],
            'mean': deltas['spend']['mean'] / deltas['link_click']['mean'],
        }
    except KeyError:
        print(f'No data for benchmark!')

    return clean_data(calculated)

def clean_data(calculated):
    if (calculated):
        for value in ['ctr', 'cpm', 'cpc']:
            for delta in ['delta90', 'delta30', 'mean']:
                if(calculated[value] and (np.isnan(calculated[value][delta]) or calculated[value][delta] == float('inf'))):
                    del calculated[value][delta]

    return calculated