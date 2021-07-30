from app_main import db
from models import Subscription
from flask import current_app as app
from flask import render_template, make_response
from utility_functions import get_ipo_subscription_details

@app.route('/data', methods=['GET'])
def get_all_cdrs():
    cdrs = Subscription.query.all()
    return make_response({'cdrs': cdrs}, 200)

@app.route('/data1', methods=['GET'])
def get_data():
    sub = Subscription(company_name = "Bandham industries",open="open1",close="close1",issue_price="issue_price1",issue_size="issue_size",qualified_inst_sub="qualified_inst_sub",non_inst_sub="non_inst_sub",retail_indv_sub="retal_indv_sub",employee_sub="employee_sub",others_sub="others_sub",total_sub="total_sub",sub_page="sub_page",main_page="main_page")
    db.session.add(sub)
    db.session.commit()
    return make_response({'cdrId': sub.company_name}, 201)

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

    past_ipo_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'Total Subscription', 'subscription_data_url', 'URL']
    past_ipos_df = past_ipos_df[past_ipo_columns]
    past_ipos_df.columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'Total Subscription', 'Subscription Page', 'Main Page']

    # df['Open'] = df['Open'].dt.strftime('%d-%m-%Y')
    return render_template("response.html", active_ipos_df=active_ipos_df, upcoming_ipos_df=upcoming_ipos_df, past_ipos_df=past_ipos_df)