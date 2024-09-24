def convert_to_datum(data):
    """Takes performance data and converts it to datum format.
    - data: 
        [{
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
            'date_start': '2020-12-02',
            'impressions': '214',
            'spend': '5.36',
            'post_reaction': '1',
            'post_engagement': '1',
            'page_engagement': '1',
            'date_saved': '2021-03-01'
        }, {
            'clicks': '10000',
            'date_start': '2020-12-03',
            'impressions': '214',
            'spend': '5.36',
            'post_reaction': '1',
            'post_engagement': '1',
            'page_engagement': '1',
            'date_saved': '2021-03-01'
        }]
    - returns: 
        {
            'clicks': [
                {'date': '2020-12-01', 'value': '2'},
                {'date': '2020-12-02', 'value': '2'},
                {'date': '2020-12-03', 'value': '1000'},
                ],
            'impressions': [
                {'date': '2020-12-01', 'value': '214'},
                {'date': '2020-12-02', 'value': '214'},
                {'date': '2020-12-03', 'value': '214'},
                ],
            'spend': [
                {'date': '2020-12-01', 'value': '5.36'},
                {'date': '2020-12-02', 'value': '5.36'},
                {'date': '2020-12-03', 'value': '5.36'},
                ],
            'post_reaction': [
                {'date': '2020-12-01', 'value': '1'},
                {'date': '2020-12-02', 'value': '1'},
                {'date': '2020-12-03', 'value': '1'},
                ],
            'post_engagement': [
                {'date': '2020-12-01', 'value': '1'},
                {'date': '2020-12-02', 'value': '1'},
                {'date': '2020-12-03', 'value': '1'},
                ],
            'page_engagement': [
                {'date': '2020-12-01', 'value': '1'},
                {'date': '2020-12-02', 'value': '1'},
                {'date': '2020-12-03', 'value': '1'},
                ],
        }
    """
    metrics = {}
    for day in data:
        base_datum = {'date': day['date_start']}
        for metric, value in day.items():
            if metric in ['date_start', 'date_saved']:
                pass
            else:
                datum = base_datum.copy()
                datum['value'] = value
                
                if metric in metrics.keys():
                    metrics[metric].append(datum)
                else:
                    metrics[metric] = [datum]

    return metrics


