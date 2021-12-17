import numpy as np
import pandas as pd
from app_main import db
from pytz import timezone
from datetime import datetime
from models import Subscription
from flask import current_app as app
from flask import render_template, make_response
from utility_functions import get_ipo_subscription_details, extract_sub_data

# Get datetime for today: start
format = "%Y-%m-%d %H:%M:%S"
now_utc = datetime.now(timezone('UTC'))
now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
today = now_asia.strftime(format)
# Get datetime for today: end

@app.route('/data', methods=['GET'])
def get_all_subscriptions():
    cdrs = Subscription.query.all()
    return make_response({'subscriptions': cdrs}, 200)

@app.route('/', methods=['GET'])
def get_ipos_data():
    # active_ipos_df, upcoming_ipos_df, past_ipos_df = get_ipo_subscription_details()
    active_ipos_df, upcoming_ipos_df = get_ipo_subscription_details()
    active_ipo_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 
        'Issue Size (Rs Cr)', 'Qualified Institutional Subscription',
       'Non Institutional Subscription', 'Retail Individual Subscription',
       'Employee Subscription', 'Others Subscription', 'Total Subscription', 'Recommendations Statistics', 'subscription_data_url', 'URL',]
    active_ipos_df = active_ipos_df[active_ipo_columns]
    active_ipos_df.columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 
        'Issue Size (Rs Cr)', 'Qualified Institutional Subscription',
       'Non Institutional Subscription', 'Retail Individual Subscription',
       'Employee Subscription', 'Others Subscription', 'Total Subscription', 'Recommendations Statistics', 'Subscription Page', 'Main Page']
    
    upcoming_ipo_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'URL']
    upcoming_ipos_df = upcoming_ipos_df[upcoming_ipo_columns]
    upcoming_ipos_df.columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'Main Page']

    # past_subs = [sub for sub in subs if not ((sub.close >= today) and (sub.open <= today))]
    saved_subs = Subscription.query.all()
    past_ipos_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Exchange Symbol', 'Issue Size (Rs Cr)', 'Total Subscription', 'Subscription Page', 'Main Page']
    past_ipos_df = pd.DataFrame(index=np.arange(len(saved_subs)), columns=past_ipos_columns)
    print(past_ipos_df)
    for index, sub in enumerate(saved_subs):
        past_ipos_df.iloc[index, :] = extract_sub_data(sub, past_ipos_df.iloc[index, :])
    past_ipos_df = past_ipos_df.sort_values(by='Open', ascending= False).reset_index(drop=True)

    # print('active_ipos_df:', active_ipos_df[['Issuer Company', 'Qualified Institutional Subscription',
    #    'Non Institutional Subscription', 'Retail Individual Subscription',
    #    'Employee Subscription', 'Others Subscription', 'Total Subscription']])

    return render_template("response.html", active_ipos_df=active_ipos_df, upcoming_ipos_df=upcoming_ipos_df, past_ipos_df=past_ipos_df)