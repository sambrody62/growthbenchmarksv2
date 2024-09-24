from .convert_to_datum import convert_to_datum
import numpy as np # pylint: disable=import-error

def identify_outliers(data):
    """Takes performance data and identifies any outliers.
    - data: [{
                'clicks': '2',
                'date_start': '2020-12-01',
                'impressions': '214',
                'spend': '5.36',
                'post_reaction': '1',
                'post_engagement': '1',
                'page_engagement': '1',
                'date_saved': '2021-03-01'
            }, {
                'clicks': '2',
                'date_start': '2020-12-01',
                'impressions': '214',
                'spend': '5.36',
                'post_reaction': '1',
                'post_engagement': '1',
                'page_engagement': '1',
                'date_saved': '2021-03-01'
            }, {
                'clicks': '10000',
                'date_start': '2020-12-01',
                'impressions': '214',
                'spend': '5.36',
                'post_reaction': '1',
                'post_engagement': '1',
                'page_engagement': '1',
                'date_saved': '2021-03-01'
            }]
    """
    metrics = convert_to_datum(data)

    identified_outliers = []

    for metric, datums in metrics.items():
        values = [d.value for d in datums]
        std_dev = np.std(values)
        mean = np.mean(values)
        outliers_cutoff = std_dev * 3

        lower_limit = mean - outliers_cutoff
        upper_limit = mean + outliers_cutoff

        for i in range(len(datums)):
            if (datums[i].value > upper_limit or datums[i].value < lower_limit):
                
                outlier = datums[i]
                outlier['metric'] = metric
                identified_outliers.append(outlier)