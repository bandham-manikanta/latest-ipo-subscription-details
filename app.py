from flask import Flask
from utility_functions import get_ipo_subscription_details

app = Flask(__name__)

@app.route('/', methods=['GET'])
def get_ipos_data():
    df = get_ipo_subscription_details()
    columns = ['Issuer Company', 'Open', 'Close', 'Issue Price  (Rs)', 
        'Issue Size (Rs Cr)', 'Qualified Institutional Subscription',
       'Non Institutional Subscription', 'Retail Individual Subscription',
       'Employee Subscription', 'Others Subscription', 'Total Subscription', 'subscription_data_url', 'URL']
    df = df[columns]
    return df.to_html(header="true", table_id="table")

if __name__ == '__main__':
    app.run(debug=True)