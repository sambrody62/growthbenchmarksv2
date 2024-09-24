from facebook_business.api import FacebookAdsApi # pylint: disable=import-error
from facebook_business.adobjects.adaccount import AdAccount # pylint: disable=import-error
from fathom.lib import logging
from fathom.components import BaseConnector
import requests # pylint: disable=import-error
from flask import current_app
import json
import threading
from fathom.lib.util_days import get_today_as_str, get_yesterday_as_str, get_since_and_until_dates_as_str, get_day_x_days_ago_as_str

class FacebookConnector(BaseConnector):
    def __init__(self, account_id, access_token, refresh_token=None, login_id=None): # Not using refresh_token or login_id but they are needed here
        # Passing all of the upstream variables into the base connector:
        super(FacebookConnector, self).__init__(account_id=account_id, access_token=access_token, platform='FACEBOOK')
        
        # Database
        self.get_account()

        if self.account:
            self.has_completed_first_fb_data_pull = self.account.get('has_completed_first_fb_data_pull')
        else:
            self.has_completed_first_fb_data_pull = False

        # Query
        # https://developers.facebook.com/docs/marketing-api/insights/parameters/v12.0
        self.fields = ['campaign_name', 'spend', 'impressions', 'clicks', 'actions', 'action_values']
        self.params = { 
            'date_preset': 'last_90d',
            'time_increment':'1',
            'level': 'campaign',
            }

    def get_account(self):
        self.account = self.account_ref.get().to_dict()
        return self.account

    def __repr__(self):
        return f"<FacebookConnector() app_id: {self.app_id} account_id: {self.account_id}"

    # Fetch Facebook Metrics Incrementally
    # @logging
    def fetch_metrics(self, cron_job=False, save_data=True, skip_db=False):
        # Check if account has saved metrics today
        today = get_today_as_str()

        # If filled questionnaire, AND last date is NOT today
        if (self.last_date_saved != today and self.has_completed_questionnaire == True) or skip_db == True:
            # WE NEED TO GET SOME DATA FROM FACEBOOK
            # Run Report
            self.run_async_report(save_data, cron_job)

            # If first time (i.e. (last_updated > 3s ago OR thread_running == False) AND False == 'has_completed_first_fb_data_pull')
            if self.account.get('has_completed_first_fb_data_pull') != True and cron_job != True:
                # Question ? Can we track the thread_id - see if that is still running? ?
                list_of_dates_to_pull_fb_data = self.get_account().get('list_of_dates_to_pull_fb_data')
                if list_of_dates_to_pull_fb_data is None:
                    split_dates = self.splitting([list(range(2,89))])
                    new_list_of_dates_to_pull_fb_data = [90, 1, *split_dates]
                    self.account_ref.update({"list_of_dates_to_pull_fb_data": new_list_of_dates_to_pull_fb_data}) 
                    
                thread_running = self.get_account().get('thread_running') # TODO also check that the last update time is not over 5 seconds ago...
                if thread_running is not True:
                    self.account_ref.update({"thread_running": True})

                    # START NEW THREAD
                    new_thread = threading.Thread(target=self.get_data_incrementally, args=[save_data, cron_job])
                    new_thread.start()

            # Return all existing data from the database
            data = list()
            response = self.metrics_ref.stream()
            for stats in response:
                data.append(stats.to_dict())
            return data
        # pull data from firestore or pass (If not filled in questionnaire or last date saved is today)
        elif self.has_completed_questionnaire == True and cron_job == False:
            current_app.logger.info(f'Pulling data from firestore for {self.account_id}')
            data = list()
            response = self.metrics_ref.stream()
            for stats in response:
                data.append(stats.to_dict())
            return data

        elif self.has_completed_questionnaire == True and cron_job == True:
            # current_app.logger.info(f'Data load skipped for {self.account_id} as already loaded')
            return {}
        else:
            # current_app.logger.info(f'Data load skipped for {self.account_id} as no questionnaire')
            return {}

    def process_insight_data(self, response, save_data, cron_job):
        # current_app.logger.info(f'Got response back from facebook for {self.account_id}')

        # Process response
        merged_data = {}
        has_data = False
        for day in response:
            has_data = True

            stats = dict(day)
            actions = day.get('actions')

            if actions:
                for event in actions:
                    stats[event['action_type']] = event['value']
                stats.pop('actions')

            action_values = day.get('action_values')
            if action_values:
                for event in action_values:
                    stats[event['action_type']+'.value'] = event['value']
                stats.pop('action_values')
            
            # new solution
            date = stats.get('date_start')
            # loop through stats
            for metric, value in stats.items():
                # skip string variables
                if metric in ['campaign_name', 'date_stop', 'date_start']:
                    pass
                # if date exists
                elif date in merged_data.keys():
                    # if metric exists at date, add to it
                    if metric in merged_data[date]:
                        merged_data[date][metric] += float(value)
                    # if metric hasn't been seen for this date, set it
                    else:
                        merged_data[date][metric] = float(value)
                # if date hasn't been seen, set it
                else:
                    merged_data[date] = {metric: float(value)}

        if save_data:
            if has_data:
                for day, stats in merged_data.items():
                    date_ref = self.metrics_ref.document(day)
                    date_ref.set(stats)
                    
            today = get_today_as_str()
            self.account_ref.update({
                'last_date_saved': today
            })

        if cron_job == False:
            return merged_data
        # End process insight data

    def run_async_report(self, save_data, cron_job):
        # Check if a job is running 
        # Does account have report_run_id
        account = self.get_account()
        yesterday = get_yesterday_as_str()
        if cron_job == True or account.get('report_run_id') is None or account.get('report_start', '') <= yesterday:
            # TODO handle failure (retry)            
            since, until = get_since_and_until_dates_as_str(days=90)

            create_report_url = f"https://graph.facebook.com/v12.0/act_{self.account_id}/insights"
            body = {
                "access_token": self.access_token,
                "fields": ','.join(self.fields),
                "time_range": json.dumps({
                    "since": since,
                    "until": until
                }),
                "use_unified_attribution_setting": "true",
                "level": "campaign",
                "time_increment": "1"
            }

            try:
                create_report_response = requests.post(create_report_url, json=body)
                report_json = create_report_response.json()
                response_error = report_json.get('error')
                if response_error:
                    error_message = response_error.get('message')
                    raise Exception(error_message)
                
                report_run_id = report_json['report_run_id']
                # Update Report Run Id
                self.account_ref.update({
                    'report_run_id': report_run_id,
                    'report_start' : get_today_as_str()
                })

                def get_report_status(self, report_run_id, counter=0):
                    report_status_response = requests.get(f"https://graph.facebook.com/v12.0/{report_run_id}", {"access_token": self.access_token})
                    report_status = report_status_response.json()
                    report_async_status = report_status['async_status']

                    if report_async_status != 'Job Completed' and counter < 300:
                        counter += 1
                        if report_async_status != 'Job Completed':
                            # sleep for 5 seconds
                            timer = threading.Timer(5, get_report_status, [self, report_run_id, counter])
                            timer.start()
                            return False
                    
                    if counter >= 300:
                        raise Exception('The job to get insights for this company was never completed')
                    
                    account_name = self.account.get('name')
                    print(f'Completed job - getting data for {self.account_id} ({account_name})')
                    report_status_response = requests.get(f"https://graph.facebook.com/v12.0/{report_run_id}/insights", {"access_token":self.access_token})
                    json_data = report_status_response.json()
                    response = json_data['data']

                    paging = 'next' in json_data['paging']
                    while paging:
                        next_url = json_data['paging']['next']
                        res = requests.get(next_url)
                        json_data = res.json()
                        next_response = json_data['data']
                        response += next_response
                        paging = 'next' in json_data['paging']
                        # END get_report_status and then processing the data
                    self.process_insight_data(response, save_data, cron_job)
                    # After job finished -> set has_completed_first_fb_data_pull
                    # Remove Job Id
                    # Remove list_of_dates_to_pull_fb_data
                    self.account_ref.update({
                        'has_completed_first_fb_data_pull': True,
                        'report_run_id': None,
                        'list_of_dates_to_pull_fb_data': []
                    })

                timer = threading.Timer(1, get_report_status, [self, report_run_id, 0])
                timer.start()
            except Exception as error_creating_facebook_report:
                account_name = self.account.get('name')
                print(f"Error creating a report for {self.account_id} ({account_name}): {error_creating_facebook_report}")


    def get_data_incrementally(self, save_data, cron_job):
        try:
            list_of_dates_to_pull_fb_data = self.get_account().get('list_of_dates_to_pull_fb_data')
            # Create a new thread to call these TODO create this thread here so it can continue to return the data that is already in the db
            while len(list_of_dates_to_pull_fb_data) > 0 and self.get_account().get('has_completed_first_fb_data_pull') is not True:
                # Go through these incrementally in a new thread
                # one at a time, get data, once you get it back, save it in the db and move on to the next (try and see how it goes)
                # Initialize Facebook Ads
                FacebookAdsApi.init(self.app_id, self.app_secret, self.access_token)

                # Set up query
                my_account = AdAccount('act_' + self.account_id)

                # Get response
                days = list_of_dates_to_pull_fb_data.pop(0)
                day_x_days_ago = get_day_x_days_ago_as_str(days=days)

                params = self.params
                if params.get('date_preset') is not None:
                    del params['date_preset']
                params['time_range'] = {
                    "since": day_x_days_ago,
                    "until": day_x_days_ago
                }
                response = my_account.get_insights(fields = self.fields, params = params)
                self.process_insight_data(response, save_data, cron_job)

                # Date that was process has already been popped, so update the original list
                self.account_ref.update({"list_of_dates_to_pull_fb_data": list_of_dates_to_pull_fb_data})

                # Once it has finished -> remove job_id
                if len(list_of_dates_to_pull_fb_data) == 0:
                    self.account_ref.update({
                        "has_completed_first_fb_data_pull": True,
                        "report_run_id": None, 
                        "thread_running": False
                    })
                    
            self.account_ref.update({
                "thread_running": False
            })
                
        except Exception as e:
            print(f"There was an error fetching data {e}")
            # If it fails -> set thread_running to False
            self.account_ref.update({
                "thread_running": False
            })


    def splitting(self, input_lists, output=None):
        if output is None:
            output = [1, len(input_lists[0])]
        
        if len(input_lists) == 0:
            return output
        
        output_lists = []
        
        for input_list in input_lists:
            if len(input_list) == 1:
                output.append(input_list[0])
            else:
                # Take the midpoint
                midpoint_idx = len(input_list) // 2

                # Get the first half
                front_list = input_list[:midpoint_idx]
                output_lists.append(front_list)
            
                # Get the second half
                if len(input_list) > midpoint_idx+1:
                    back_list = input_list[midpoint_idx+1:]
                    output_lists.append(back_list)
                
                # Put the midpoint in the output
                output.append(input_list[midpoint_idx])
        return self.splitting(output_lists, output)