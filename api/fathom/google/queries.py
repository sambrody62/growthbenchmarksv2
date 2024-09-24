from fathom.lib.util_days import get_since_and_until_dates_as_str

# Calculating 90 days into the past:
since, until = get_since_and_until_dates_as_str(days=90)

get_accounts_query = f"""
SELECT
customer_client.client_customer,
customer_client.level,
customer_client.manager,
customer_client.descriptive_name,
customer_client.currency_code,
customer_client.time_zone,
customer_client.id
FROM customer_client"""

test_account_traffic_query = f"""
SELECT
metrics.cost_micros,
metrics.impressions,
metrics.clicks,
segments.date
FROM customer
WHERE segments.date DURING LAST_30_DAYS
"""

clicks_query = f"""
SELECT
metrics.cost_micros,
metrics.impressions,
metrics.clicks,
segments.date
FROM customer
WHERE segments.date >= '{since}' AND segments.date <= '{until}'
"""

conversion_query = f"""
SELECT
segments.date,
segments.conversion_action_category,
metrics.all_conversions,
metrics.all_conversions_value
FROM customer
WHERE segments.date >= '{since}' AND segments.date <= '{until}'
"""