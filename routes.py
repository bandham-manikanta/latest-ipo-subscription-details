import numpy as np
import pandas as pd
from app_main import db
from models import Subscription
from flask import current_app as app
from flask import render_template, make_response
from utility_functions import get_ipo_subscription_details, extract_sub_data

@app.route('/data', methods=['GET'])
def get_all_subscriptions():
    cdrs = Subscription.query.all()
    return make_response({'subscriptions': cdrs}, 200)

@app.route('/', methods=['GET'])
def get_ipos_data():
    active_ipos_df, upcoming_ipos_df, past_ipos_df = get_ipo_subscription_details()
    active_ipo_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 
        'Issue Size (Rs Cr)', 'Qualified Institutional Subscription',
       'Non Institutional Subscription', 'Retail Individual Subscription',
       'Employee Subscription', 'Others Subscription', 'Total Subscription', 'subscription_data_url', 'URL']
    active_ipos_df = active_ipos_df[active_ipo_columns]
    active_ipos_df.columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 
        'Issue Size (Rs Cr)', 'Qualified Institutional Subscription',
       'Non Institutional Subscription', 'Retail Individual Subscription',
       'Employee Subscription', 'Others Subscription', 'Total Subscription', 'Subscription Page', 'Main Page']
    
    upcoming_ipo_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'Total Subscription', 'URL']
    upcoming_ipos_df = upcoming_ipos_df[upcoming_ipo_columns]
    upcoming_ipos_df.columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'Total Subscription', 'Main Page']

    subs = Subscription.query.all()
    past_ipos_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'Total Subscription', 'Subscription Page', 'Main Page']
    past_ipos_df = pd.DataFrame(index=np.arange(len(subs)), columns=past_ipos_columns)
    for index, sub in enumerate(subs):
        past_ipos_df.iloc[index, :] = extract_sub_data(sub, past_ipos_df.iloc[index, :])

    # TODO: REMOVE ACTIVE IPOS FROM PAST IPOS

    # df['Open'] = df['Open'].dt.strftime('%d-%m-%Y')
    return render_template("response.html", active_ipos_df=active_ipos_df, upcoming_ipos_df=upcoming_ipos_df, past_ipos_df=past_ipos_df)