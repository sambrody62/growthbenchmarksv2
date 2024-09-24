from .errors import GenericGoogleAdsError
from fathom.lib import logging
from flask import current_app
import google.protobuf
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
import numpy as np
import pandas as pd
from typing import Optional, List
from fathom.lib.util_days import get_today_as_str

# Base Classes + Components:
from fathom.components import BaseConnector, FireStoreWrapper

# Relative Components:
from .accounts import HierachyParser
from .conversion_keys import conversion_keys
from .errors import GenericGoogleAdsError
from .queries import clicks_query, conversion_query, get_accounts_query, test_account_traffic_query

class GoogleAdsConnector(BaseConnector):
    def __init__(self, account_id:str=None, access_token:str=None, refresh_token:str=None, login_id:str=None):
        # Passing all of the upstream variables into the base connector:
        super(GoogleAdsConnector, self).__init__(account_id=account_id, access_token=access_token, refresh_token=refresh_token, platform='GOOGLE_ADS')

        # The self.account_id, self.access_token, self.refresh_token and self.platform tokens
        # will be inherited from the base parent constructor.

        # Defining the config dict:
        self.config_dict = {
            'developer_token': self.developer_token,
            'refresh_token': self.refresh_token,
            'client_id': self.app_id,
            'client_secret': self.app_secret,
        }

        # Extracting any json payload If there is a login_id, we will mutate the client:
        if login_id:
            self.config_dict['login_customer_id'] = login_id

        # Creating a Google Ads client:
        self.client = GoogleAdsClient.load_from_dict(config_dict=self.config_dict)
        # Gets instances of the GoogleAdsService and CustomerService clients:
        self.googleads_service = self.client.get_service("GoogleAdsService")
        self.customer_service = self.client.get_service("CustomerService")

    def __repr__(self):
        return f"<GoogleAdsConnector() app_id: {self.app_id}"

    ### Helper Functions:
    def _get_account_hierachy(self) -> pd.DataFrame:
        """Generates a dataframe which contains all of the Google Ads accounts that can 
        be seen within the hierachy. Some of these accounts may not be accessible and therefore 
        we will need to test against the account before accepting it. 

        Returns:
            pd.DataFrame: Returns a dataframe with the 
        """
        self.df = HierachyParser(googleads_service=self.googleads_service,
        customer_service=self.customer_service)
        return self.df

    def _get_accessible_google_ads_accounts(self) -> pd.DataFrame:
        """ Generates a list of accessible accounts within Google Ads.
        Returns:
            pd.DataFrame: A pandas dataframe containing a list of accessible accounts.
        """
        try:
            accessible_accounts = []
            accessible_customers = self.customer_service.list_accessible_customers()
            resource_names = accessible_customers.resource_names
            for resource_name in resource_names:
                account = resource_name.replace("customers/","")
                accessible_accounts.append(account)
        except GoogleAdsException as ex:
            print('Request with ID "%s" failed with status "%s" and includes the ' "following errors:" % (ex.request_id, ex.error.code().name))
            for error in ex.failure.errors:
                print('\tError with message "%s".' % error.message)
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print("\t\tOn field: %s" % field_path_element.field_name)

        all_accounts = {}  # {'login id':[customerid, customer name, customer level], 'login id':[customer id, customer name, customer level]}
        sub_accounts = []  # Will collect accounts & sub-mccs that are underneath an MCC the user has access to, so we can dedupe later

        for account in accessible_accounts:
            try:
                response = self.googleads_service.search(customer_id=account, query=get_accounts_query)
                all_accounts[account] = []
                for google_ads_row in response:
                    customer_client = google_ads_row.customer_client
                    customerid = str(customer_client.id)
                    all_accounts[account].append((customerid, customer_client.descriptive_name, customer_client.level, 
                    customer_client.manager, customer_client.currency_code))
                    if customerid != account:
                        sub_accounts.append(customerid)
            except:
                print(f'FAILED TO GET ACCOUNT {account}')

        # Remove duplicates when someone has access to an MCC & subMCC or account in the same hierarchy
        for account in accessible_accounts:
            if account in sub_accounts:
                all_accounts.pop(account)
        print(f"There are {len(sub_accounts)} sub accounts and {len(all_accounts)} login accounts")
        final_accessible_accounts_list = []

        for toplevel in all_accounts:
            if len(all_accounts[toplevel]) > 1: # This toplevel contains multiple accounts ie. its an MCC
                for account in all_accounts[toplevel]: # So we make a row for each account inside it:
                    if account[3] == True: # This is an MCC:
                        pass 
                    else: # This is an account:
                        row = {'login_id': toplevel, 'account_id': account[0], 
                        'name' : account[1], 'currency': account[4]}
                        final_accessible_accounts_list.append(row)
            else: # This is a solo account, not MCC
                row = {'login_id': '', 'account_id' : toplevel, 
                'name' : all_accounts[toplevel][0][1], 'currency': all_accounts[toplevel][0][-1]}
                final_accessible_accounts_list.append(row)
        return pd.DataFrame(final_accessible_accounts_list)
    
    # Query Engine For Google Ads API:
    def _get_search_stream(self, query:str) -> list:
        # Errors that we need to handle for:
        # - We might not be able to access a specific Google Ads account.
        # - Null rows back (i.e. no data).
        # - Each batch stream object might have a different number of columns.
        # - Invalid customer id.

        """A generic search stream query that allows us to make requests against the Google Ads API:
        Args:
            query (str): A Google ads query.
        """

        # Validate that we have a a customer id:
        if not hasattr(self, 'account_id'):
            raise GenericGoogleAdsError(message=f'''You must provide an account_id (that will be used as the customer id)
            with each Google Ads search_stream request, function: self._get_search_stream()''')
        try:
            response = self.googleads_service.search_stream(customer_id=self.account_id, 
            query=query)

            all_batch_results = []

            for batch in response:

                MaskArray = batch.field_mask.ToJsonString().split(",")
                # We reformat the fieldmask to match the base_df so we can filter it to only contain those columns:
                FieldMask = []

                # Extract the returned dimensions for the batch:
                for x in MaskArray:
                    FieldMask.append(x.replace("."," "))             

                # Extract the relevant information from the batch:
                try:
                    base_df = pd.json_normalize(google.protobuf.json_format.MessageToDict(batch._pb),
                                                record_path="results", 
                                                sep=" ")
                except Exception as e:
                    print(e)
                    base_df = pd.DataFrame()

                # Test to see whether we have an empty data frame, append an empty list if there isn't any data:
                if base_df.empty == True:
                    all_batch_results.append(pd.DataFrame())
                else:
                    '''If a metric has no results, it won't be a column in base_df but it will be in the FieldMask list.
                    Therefore we can select the columns that are available per batch:'''
                    FieldMask = [value for value in FieldMask if value in base_df.columns]
                    data = base_df[FieldMask]

                    # Append if there is data:
                    single_result = pd.DataFrame(data=data,
                                        columns=FieldMask)
                    all_batch_results.append(single_result)
                    
        except GoogleAdsException as ex:
            errors = []
            top_message = f'Request with ID {ex.request_id} failed with {ex.error.code().name}'
            print(top_message)
            errors.append(top_message)
            for error in ex.failure.errors:
                print(error.message)
                errors.append(error.message)
                if error.location:
                    for field_path_element in error.location.field_path_elements:
                        print(field_path_element.field_name)
                        errors.append(f'''\n On field: {field_path_element.field_name}''')
            # Raise a custom error for when a search_stream request fails:
            raise GenericGoogleAdsError(message=errors)
        return all_batch_results

    def _check_for_data_availability(self, batch_results:list) -> bool:
        # 1. Check to see whether there is any data at all: (use this for the test response route):
        self.any_data_available = any([False if result.empty else True for result in batch_results])
        if self.any_data_available:
            return True
        else:
            return None

    def _exclude_any_empty_dataframes(self, batch_results:list) -> list:
        # 2. Exclude any of the empty pandas dataframes:
        available_data = [result for result in batch_results if result.empty == False]
        return available_data
   
    def _column_length_normaliser_df_concatenation_and_dataframe_cleaning(self, 
    available_data:list) -> Optional[pd.DataFrame]:
        """Returns a dataframe with multiple dataframes that have been concatenated.
        Args:
            available_data (list): A list of dataframes with potentially varying ranges of column sizes.

        Returns:
            Optional[pd.DataFrame]: Returns a dataframe or None.
        """     
        # 2.1 Check to see whether they are all the same shape
        different_column_numbers = set([item.shape[1] for item in available_data])

        if len(different_column_numbers) > 1:
            print(f"There are a different length of columns between dataframes:")
            # 2.2 If the number of the columns are different, add new columns with nans to the smaller ones:
            largest_column_size = 0
            columns_to_use = None
            
            # Find out which dataframe has the largest column size:
            for dataframe in available_data:
                if dataframe.shape[1] >= largest_column_size:
                    largest_column_size = dataframe.shape[1]
                    columns_to_use = dataframe.columns
                    
            # Find all of the dataframes that have less than the number of columns:
            for dataframe in available_data:
                if dataframe.shape[1] < largest_column_size:
                    for col in columns_to_use not in dataframe.columns:
                        dataframe[col] = np.nan
                        
            # Organise all of the dataframes to have the same column order before concatenating:
            columns_to_use = sorted(columns_to_use)
            available_data = [dataframe[columns_to_use] for dataframe in available_data]

        # Concatenating the data:
        final_df = pd.concat([dataframe for dataframe in available_data])

        # Drop a column if it is completed filled with nans:
        final_df.dropna(axis=1, how='all', inplace=True)

        # Drop nans per row:
        # final_df.dropna(axis=0, how='any', inplace=True)

        if final_df.empty:
            print(f"Returning None as there is no data in the df.")
            return None
        else:
            return final_df

    def _convert_dtypes_and_normalise_cost(self, final_result:pd.DataFrame) -> pd.DataFrame:
        conversionDict = dict()
        for key, value in conversion_keys.items():
            if key in final_result.columns:
                conversionDict[key] = value
        final_df = final_result.astype(conversionDict)

        # Convert the cost Micros column:
        if any("metrics costMicros" in s for s in final_df.columns):
            final_df['metrics costMicros'] = final_df['metrics costMicros'].apply(lambda x: x / 1000000)
        
        return final_df

    # End of Google Ads API Query Engine:

    # Column Re-naming/Reshaping/Joining:
    # 1. Conversion_df:
    def _flatten_the_conversion_df(self, raw_conversion_df:pd.DataFrame) -> pd.DataFrame:
            """Flattens the conversion dataframe into a day by day dataframe 
            with Xn conversion + conversion_value columns. This includes a total for:
            total_conversions and total_conversions_value:

            Args:
                raw_conversion_df (pd.DataFrame): A raw conversion dataframe.

            Returns:
                pd.DataFrame: A flattened by day dataframe.
            """        
            # Pivot the data:
            cleaned_conversion_df = raw_conversion_df.pivot_table(index=['segments date'], columns=['segments conversionActionCategory'],
                            values=['metrics allConversions', 'metrics allConversionsValue'],
                            aggfunc='sum')

            # Flatten the index:
            cleaned_conversion_df.columns = cleaned_conversion_df.columns.to_flat_index()

            # Flatten out the column names:
            cleaned_conversion_df.columns = [" ".join(col).lower() for col in cleaned_conversion_df.columns]

            # Reset the date index from the pivot:
            cleaned_conversion_df.reset_index(inplace=True)

            # Clean the column names:
            new_columns = []

            for col in cleaned_conversion_df.columns:
                if 'metrics allconversionsvalue' in col:
                    col = col.replace('metrics allconversionsvalue', 'Conversion Value')
                elif 'metrics allconversions' in col:
                    col = col.replace('metrics allconversions', 'Conversion Total')
                else:
                    col = col.replace('segments date', 'date_start')
                
                # Replacing all of the column names:
                col = col.replace(' ', '_')    
                new_columns.append(col.title())
                
            cleaned_conversion_df.columns = new_columns

            # Adding total converisons + total conversion value for each day:
            conversion_columns = [col for col in cleaned_conversion_df.columns if 'Conversion_Total' in col]
            conversion_value_columns = [col for col in cleaned_conversion_df.columns if 'Value' in col]

            cleaned_conversion_df['Conversion_Total'] = cleaned_conversion_df[conversion_columns].apply(lambda x: 
                                                                                                        sum(x), axis=1)

            cleaned_conversion_df['Conversion_Value_Total'] = cleaned_conversion_df[conversion_value_columns].apply(lambda x: 
                                                                                                        sum(x), axis=1)

            return cleaned_conversion_df

    # 2. Clicks_df:
    def _rename_cost_impressions_clicks_df(self, raw_clicks_df:pd.DataFrame) -> pd.DataFrame:
        """Performs column re-naming for the cost dataframe.
        Args:
            raw_clicks_df (pd.DataFrame): A raw cost dataframe.

        Returns:
            pd.DataFrame: A cleaned cost dataframe.
        """
        return raw_clicks_df.rename(columns={'metrics costMicros': 'spend', 'metrics impressions': 'impressions', 
                        'metrics clicks': 'clicks', 'segments date': 'date_start'})

    # 3. Data Flow For A Query:
    def _data_flow(self, query:str) -> pd.DataFrame:
        # 1. Run a query:
        result = self._get_search_stream(query=query)

        # 2. Check to see if there is data availability:
        data_availability = self._check_for_data_availability(batch_results=result)
        if not data_availability:
            return None
        # 3. Clean the data:
        cleaned_data = self._exclude_any_empty_dataframes(batch_results=result)
        if cleaned_data is None:
            return None
        cleaned_data = self._column_length_normaliser_df_concatenation_and_dataframe_cleaning(available_data=cleaned_data)
        if cleaned_data is None:
            return None
        # The data made it past all of the data integrity checks:
        cleaned_data = self._convert_dtypes_and_normalise_cost(final_result=cleaned_data)
        
        # 4. Re-shaping or changing the column anmes depending upon the query:
        if query == clicks_query:
            # print("This is a clicks query")
            final_df = self._rename_cost_impressions_clicks_df(raw_clicks_df=cleaned_data)
            return final_df
        elif query == conversion_query:
            # print("This is a conversion query")
            final_df = self._flatten_the_conversion_df(raw_conversion_df=cleaned_data)
            return final_df

        return cleaned_data
    
    ### Saving Functionality:
    def _save(self, stats:int): 
        date_ref = self.metrics_ref.document(stats['date_start'])
        return date_ref.set(stats)
    
    ### End of Helper Functions:

    ### Execution Functions:
    def get_primary_accounts_list(self):
        self.accounts = self._get_accessible_google_ads_accounts()
        return self.accounts 

    def test_account_for_data_last_30_days(self, query=test_account_traffic_query):
        final_result = self._data_flow(query=query)
        return final_result

    def get_cost_click_impressions_data(self, query=clicks_query):
        final_result = self._data_flow(query=query)
        return final_result

    def get_conversion_data(self, query=conversion_query):
        final_result = self._data_flow(query=query)
        # lowering column names to avoid issue where we have Date_Start instead of date_start
        if final_result is not None:
            final_result.columns = [c.lower() for c in final_result.columns]
        return final_result

    @logging
    def get_insights(self) -> List[dict]:
        """Extracts and converts the cost and conversion dataframes into a list of dictionaries.
        Returns:
            List[dict]: A list of dictionaries with unique records for each Date.
        """
        cost_df = self.get_cost_click_impressions_data()
        conversion_df = self.get_conversion_data()

        # Checking to see if both variables are None:
        if cost_df is None and conversion_df is None:
            print(f"Both dataframes are empty:")
            return None

        # Checking to see if there are two dataframes and both dataframes have data:
        if isinstance(cost_df, pd.DataFrame) and isinstance(conversion_df, pd.DataFrame):
            if not cost_df.empty and not conversion_df.empty:
                # There is an assumption here that we will always have cost when we have conversions and vice versa:
                print(cost_df)
                print(conversion_df)
                df = pd.merge(left=cost_df, right=conversion_df, left_on='date_start', right_on='date_start', how='left')
                # Filling in any missing values for any dates:
                df.fillna(value=0, inplace=True)
                return df.to_dict(orient='records')

        # Returning the appropriate unique dataframe: 
        if cost_df is not None:
            return cost_df.to_dict(orient='records')
        if conversion_df is not None:
            return conversion_df.to_dict(orient='records')

    # Generic Methods:
    @logging
    def fetch_metrics(self, cron_job=False, save_data=True):

        # Check if account has saved metrics today:
        today = get_today_as_str()

        # Pull data from facebook:
        if ((self.last_date_saved != today or self.account_ref.get().to_dict().get('has_completed_first_google_data_pull') != True) and self.has_completed_questionnaire == True):
            current_app.logger.info(f'Pulling data from {self.platform} for {self.account_id}')

            # Get response:
            response = self.get_insights()
            current_app.logger.info(f'Got response back from Google for {self.account_id}')

            # Check the response and return nothing if no metrics were pulled:
            data = list()
            if response:
                # Process a successful response for Xn days:
                for stats in response:
                    print("stats", stats)
                    stats["date_saved"] = today
                    data.append(stats)
                    current_app.logger.debug(f"Saving data for {stats['date_start']}")

                    # Save data:
                    if save_data:
                        self._save(stats)

            if save_data:
                # If there is an error with the Google API then this may still update incorrectly
                self.account_ref.update({'last_date_saved': today, 'has_completed_first_google_data_pull': True})

            if cron_job == False:
                return data

        # Pull data from Firestore or pass:
        elif self.has_completed_questionnaire == True and cron_job == False:
            current_app.logger.info(f'Pulling data from firestore for {self.account_id}')
            data = list()
            response = self.metrics_ref.stream()
            for stats in response:
                data.append(stats.to_dict())
            return data

        elif self.has_completed_questionnaire == True and cron_job == True:
            current_app.logger.info(f'Data load skipped for {self.account_id} as already loaded')
        
        else:
            current_app.logger.info(f'Data load skipped for {self.account_id} as no questionnaire')
            return {}