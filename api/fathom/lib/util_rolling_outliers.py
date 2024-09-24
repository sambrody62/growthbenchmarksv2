import numpy as np

def rolling_outliers(benchmark_data):
    lookback_window = 21
    standard_deviations_multiple_difference = 2
    if (len(benchmark_data) == 0):
        return {
            "lower_data":[],
            "upper_data":[],
            "outliers_data":[],
        }
    
    lower_data = []
    upper_data = []
    outliers_data = []

    raw_data = [x[1] for x in benchmark_data]

    index = 0
    for (date, value) in benchmark_data:
        # Get last x day
        if index - lookback_window < 0:
            start_index = 0
        else:
            start_index = index - lookback_window
        
        raw_data_window = raw_data[start_index:index + 1]

        # To keep this consistent with the client side
        # we need to use an unbiased standard deviation
        # https://www.codegrepper.com/code-examples/python/python+unbiased+standard+deviation
        ddof = 1
        if len(raw_data_window) == 1:
            ddof = 0
        standard_deviation = np.std(raw_data_window, ddof=ddof)
        mean = np.mean(raw_data_window)
        
        outliers_cutoff = standard_deviation * standard_deviations_multiple_difference

        lower_limit = mean - outliers_cutoff
        upper_limit = mean + outliers_cutoff

        lower_data.append((date, lower_limit))
        upper_data.append((date, upper_limit))

        if value > upper_limit or value < lower_limit:
            outliers_data.append((date,value))
        
        index += 1

    return {
            "lower_data": lower_data,
            "upper_data": upper_data,
            "outliers_data": outliers_data,
        }