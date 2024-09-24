from google.ads.googleads.errors import GoogleAdsException
from google.protobuf.json_format import MessageToDict
import pandas as pd

# How To Scan The Hierachy: 
class HierachyParser():
    def __init__(googleads_service, customer_service):
        # A collection of customer IDs to handle.
        seed_customer_ids = []

        # Creates a query that retrieves all child accounts of the
        # manager pecified in search calls below.
        query = """
            SELECT
            customer_client.client_customer,
            customer_client.level,
            customer_client.manager,
            customer_client.descriptive_name,
            customer_client.currency_code,
            customer_client.time_zone,
            customer_client.id
            FROM customer_client
            WHERE customer_client.level <= 1"""

        # Issue a  request for all customers accessible by this authenticated Google account.
        customer_resource_names = (customer_service.list_accessible_customers().resource_names)

        for customer_resource_name in customer_resource_names:
            customer = customer_service.get_customer(resource_name=customer_resource_name)
            seed_customer_ids.append(customer.id)

        # Extract the hierachy:
        master_accounts_hierachy_list = []

        for seed_customer_id in seed_customer_ids:
            # Performs a breadth-first search to build a Dictionary that maps
            # managers to their child accounts (customerIdsToChildAccounts).
            unprocessed_customer_ids = [seed_customer_id]
            customer_ids_to_child_accounts = dict()
            root_customer_client = None

            while unprocessed_customer_ids:
                customer_id = unprocessed_customer_ids.pop(0)
                
                try:
                    response = googleads_service.search(
                        customer_id=str(customer_id), query=query)

                    # Iterates over all rows in all pages to get all customer
                    # clients under the specified customer's hierarchy.
                    for googleads_row in response:
                        customer_client = googleads_row.customer_client

                        # The customer client that with level 0 is the specified
                        # customer.
                        if customer_client.level == 0:
                            if root_customer_client is None:
                                root_customer_client = customer_client
                            continue

                        # For all level-1 (direct child) accounts that are a
                        # manager account, the above query will be run against them
                        # to create a Dictionary of managers mapped to their child
                        # accounts for printing the hierarchy afterwards.
                        if customer_id not in customer_ids_to_child_accounts:
                            customer_ids_to_child_accounts[customer_id] = []

                        customer_ids_to_child_accounts[customer_id].append(
                            customer_client)

                        if customer_client.manager:
                            # A customer can be managed by multiple managers, so to
                            # prevent visiting the same customer many times, we
                            # need to check if it's already in the Dictionary.
                            if (customer_client.id
                                not in customer_ids_to_child_accounts
                                and customer_client.level == 1):
                                unprocessed_customer_ids.append(customer_client.id)
                except GoogleAdsException as ex:
                    print('Request with ID "%s" failed with status "%s" and includes the '
                        "following errors:" % (ex.request_id, ex.error.code().name))
                    for error in ex.failure.errors:
                        print('\tError with message "%s".' % error.message)
                        if error.location:
                            for field_path_element in error.location.field_path_elements:
                                print("\t\tOn field: %s" % field_path_element.field_name)

            if root_customer_client is not None:
                # Save all of the information for cleaning later on:
                master_accounts_hierachy_list.append((root_customer_client, 
                customer_ids_to_child_accounts)) 
            else:
                pass

        # Removing dead hierarchies:
        master_accounts_hierachy_list = [item for item in master_accounts_hierachy_list if item[0]]

        # Flattening out the hierachies: 
        all_results = []

        for item in master_accounts_hierachy_list:
            all_results.append(item[0])
            for key, value in item[1].items():
                all_results.extend(value)     
                
        # Constructing a list of dictionaries:
        all_results_cleaned = [MessageToDict(result._pb) for result in all_results]

        # Clean Up And Remove Any Strictly MCC Account IDs:
        df = pd.DataFrame(all_results_cleaned)
        df = df[df['manager'] != True]

        # De-duplicate based upon the unique id:
        df.drop_duplicates(subset=['id'], inplace=True)
        return df