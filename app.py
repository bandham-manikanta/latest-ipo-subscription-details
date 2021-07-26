from flask import Flask, render_template
from utility_functions import get_ipo_subscription_details

app = Flask(__name__)

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

    past_ipo_columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'subscription_data_url', 'URL']
    past_ipos_df = past_ipos_df[past_ipo_columns]
    past_ipos_df.columns = ['Issuer Company', 'Open', 'Close', 'Issue Price (Rs)', 'Issue Size (Rs Cr)', 'Subscription Page', 'Main Page']

    # df['Open'] = df['Open'].dt.strftime('%d-%m-%Y')
    return render_template("response.html", active_ipos_df=active_ipos_df, upcoming_ipos_df=upcoming_ipos_df, past_ipos_df=past_ipos_df)

if __name__ == '__main__':
    app.run(debug=True)