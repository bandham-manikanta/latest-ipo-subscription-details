import pandas as pd
import requests as reqs
from app_main import db
from datetime import date
from pytz import timezone
from datetime import datetime
from bs4 import BeautifulSoup
from collections import Counter
from models import Subscription

# exception_list = ['Pavna Industries Limited IPO', 'Party Cruisers Limited IPO']

format = "%Y-%m-%d %H:%M:%S"
now_utc = datetime.now(timezone('UTC'))
now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))

def get_ipos_data():
    all_ipos_page_response = reqs.get('https://www.chittorgarh.com/report/ipo-in-india-list-main-board-sme/82/')
    all_pages_soup = BeautifulSoup(all_ipos_page_response.content, 'html.parser')
    parent_div_table = all_pages_soup.find('div', {'id':'report_data'})
    table_tag = parent_div_table.find('table')
    thead_tag = table_tag.find('thead')
    th_tags = thead_tag.findAll('th')
    column_names = list()
    for th in th_tags:
        column_names.append(th.text.strip().replace('  ', ' '))

    tbody_tag = table_tag.find('tbody')
    tr_tags = tbody_tag.findAll('tr')
    ipo_page_links = list()
    issuer_company_names = list()
    exchange_names = list()
    open_dates = list()
    close_dates = list()
    lot_sizes = list()
    issue_prices = list()
    issue_sizes = list()

    for tr in tr_tags:
        link = tr.find('a').get('href')
        ipo_page_links.append(link.strip())
        tds = tr.findAll('td')
        issuer_company_names.append(tds[0].text.strip())
        exchange_names.append(tds[1].text.strip())
        open_dates.append(tds[2].text.strip())
        close_dates.append(tds[3].text.strip())
        lot_sizes.append(tds[4].text.strip())
        issue_prices.append(tds[5].text.strip())
        issue_sizes.append(tds[6].text.strip())

    dict_for_df = dict()

    for index, values in enumerate([issuer_company_names,exchange_names,open_dates,close_dates,lot_sizes,issue_prices,issue_sizes,ipo_page_links]):
        dict_for_df[index] = values

    column_names.append('URL')
    df = pd.DataFrame(dict_for_df)
    df.columns = column_names

    df = df[~((df['Close']=='') | (df['Close'].isna()))]
    df['Close'] = pd.to_datetime(df['Close'])
    df['Close'] = pd.to_datetime(df['Close'].dt.strftime("%Y-%m-%d 23:59:59"))

    df = df[~((df['Open']=='') | (df['Open'].isna()))]
    df['Open'] = pd.to_datetime(df['Open'])
    df['Open'] = pd.to_datetime(df['Open'].dt.strftime("%Y-%m-%d 00:00:01"))

    df['Qualified Institutional Subscription'] = None
    df['Non Institutional Subscription'] = None
    df['Retail Individual Subscription'] = None
    df['Employee Subscription'] = None
    df['Others Subscription'] = None
    df['Total Subscription'] = None
    df['Recommendations Statistics'] = None
    df['NSE Symbol'] = None
    df['Share Price Link'] = None
    df['subscription_data_url'] = None

    df['ipo_name'] = df['URL'].apply(lambda x: x.split('/')[4].strip())
    df['ipo_id'] = df['URL'].apply(lambda x: x.split('/')[5].strip())
    print('-'*50)
    print(df.shape)
    print('-'*50)
    if df.shape[0]>0:
        df['subscription_data_url'] = df.apply(lambda row: format_subscription_url(row), axis=1)

    # print('Fetched all the ipos data from IPO Mainboard: ', df.head())

    # return active_ipos_df, upcomingz_ipos_df #, past_ipos_df
    return df


def fetch_subscription_data(url:str) -> pd.DataFrame():
    sub_response = reqs.get(url)
    sup_soup = BeautifulSoup(sub_response.content, 'html.parser')
    print('url:', url)
    
    sub_table = sup_soup.find('table')
    sub_thead_tag = sub_table.find('thead')
    sub_th_tags = sub_thead_tag.findAll('th')
    sub_table_col_names = [x.text.strip() for x in sub_th_tags]

    institution_names = list()
    subscription_times = list()
    
    sub_tbody_tag = sub_table.find('tbody')
    sub_tr_tags = sub_tbody_tag.findAll('tr')
    for tr in sub_tr_tags:
        td_tags = tr.findAll('td')
        values = [td.text.strip() for td in td_tags]
        institution_names.append(values[0])
        subscription_times.append(values[1])
    sub_dict_for_df = {'0': institution_names, '1': subscription_times}
    sub_df = pd.DataFrame(sub_dict_for_df)
    sub_df.columns = sub_table_col_names
    return sub_df

def get_sub_data(row, saved_subs):
    sub = Subscription.query.get(row['Issuer Company'])
    # print(list(filter(lambda x: x.company_name == row['Issuer Company'], saved_subs)))
    # is_sub_present_in_db = True if next(i for i in saved_subs if i.company_name == row['Issuer Company']) else False
    # print(is_sub_present_in_db)

    format = "%Y-%m-%d %H:%M:%S"
    now_utc = datetime.now(timezone('UTC'))
    now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
    today = now_asia.strftime(format)
    today = datetime.strptime(today, format)

    if sub==None:
        try:
            if (sub != None) and (datetime.strptime(str(row['Close']), format) >= today):
                db.session.delete(sub)
                db.session.commit()
            sub_data = fetch_subscription_data(row['subscription_data_url'])
            row['Qualified Institutional Subscription'] = sub_data.iloc[0, 1]
            row['Non Institutional Subscription'] = sub_data.iloc[1, 1]
            row['Retail Individual Subscription'] = sub_data.iloc[2, 1]
            row['Employee Subscription'] = sub_data.iloc[3, 1]
            row['Others Subscription'] = sub_data.iloc[4, 1]
            row['Total Subscription'] = sub_data.iloc[5, 1]
        except:
            row['Qualified Institutional Subscription'] = 'NA'
            row['Non Institutional Subscription'] = 'NA'
            row['Retail Individual Subscription'] = 'NA'
            row['Employee Subscription'] = 'NA'
            row['Others Subscription'] = 'NA'
            row['Total Subscription'] = 'NA'

        sub = Subscription(company_name=row['Issuer Company'],open=str(row['Open']),close=str(row['Close']),issue_price=row['Issue Price (Rs)'],issue_size=row['Issue Size (Rs Cr)'],
                          qualified_inst_sub=row['Qualified Institutional Subscription'],non_inst_sub=row['Non Institutional Subscription'],retail_indv_sub=row['Retail Individual Subscription'],
                          employee_sub=row['Employee Subscription'],others_sub=row['Others Subscription'],total_sub=row['Total Subscription'],sub_page=row['subscription_data_url'],main_page=row['URL'])
        db.session.add(sub)
        db.session.commit()
    else:
        row['Qualified Institutional Subscription'] = sub.qualified_inst_sub
        row['Non Institutional Subscription'] = sub.non_inst_sub
        row['Retail Individual Subscription'] = sub.retail_indv_sub
        row['Employee Subscription'] = sub.employee_sub
        row['Others Subscription'] = sub.others_sub
        row['Total Subscription'] = sub.total_sub
    # print(row)
    return row

def fetch_and_map_subscription_data_to_row(row):
    sub_data = pd.DataFrame()
    try:
        sub_data = fetch_subscription_data(row['subscription_data_url'])
    except:
        sub_data = pd.DataFrame({0:['NA','NA','NA','NA','NA','NA'],1:['NA','NA','NA','NA','NA','NA']})
    row['Qualified Institutional Subscription'] = sub_data.iloc[0, 1]
    row['Non Institutional Subscription'] = sub_data.iloc[1, 1]
    row['Retail Individual Subscription'] = sub_data.iloc[2, 1]
    row['Employee Subscription'] = sub_data.iloc[3, 1]
    row['Others Subscription'] = sub_data.iloc[4, 1]
    row['Total Subscription'] = sub_data.iloc[5, 1]
    return row

def get_exchange_symbol(url: str) -> str:
    resp = reqs.get(url)
    
    soup = BeautifulSoup(resp.content, 'html.parser')
    card_tags = soup.findAll('div',{'class':'card'})
    listing_date_card = next((x for x in card_tags if 'Listing Date' in x.text), None)
    table_tag = listing_date_card.find('table') if listing_date_card else None
    tr_tags = table_tag.findAll('tr') if table_tag else []
    all_symbol_tags = [x for x in tr_tags if ('NSE Symbol' in x.text or 'BSE Script Code' in x.text)]
    all_symbol_tags = list(reversed([x.findAll('td') for x in all_symbol_tags]))
    symbol_td_tags = next((x for x in all_symbol_tags if len(x[-1].text.strip())>0 ), None)
    symbol = symbol_td_tags[0].text[:3] + ':' + symbol_td_tags[1].text if symbol_td_tags else None
    symbol if symbol else 'NA'
    return symbol

def persist_subscription(row):
    row = fetch_and_map_subscription_data_to_row(row)
    exchange_symbol = get_exchange_symbol(row['URL'])
    row['Exchange Symbol'] = exchange_symbol if exchange_symbol else 'NA'
    sub = Subscription(company_name=row['Issuer Company'],open=str(row['Open']),close=str(row['Close']),issue_price=row['Issue Price (Rs)'],issue_size=row['Issue Size (Rs Cr)'],
                          qualified_inst_sub=row['Qualified Institutional Subscription'],non_inst_sub=row['Non Institutional Subscription'],retail_indv_sub=row['Retail Individual Subscription'],
                          employee_sub=row['Employee Subscription'],others_sub=row['Others Subscription'],total_sub=row['Total Subscription'],sub_page=row['subscription_data_url'],main_page=row['URL'],
                          exchange_symbol=row['Exchange Symbol'])
    db.session.add(sub)
    db.session.commit()
    return True    

def get_ipo_subscription_details():
    # active_ipos_df, upcomings_ipos_df, past_ipos_df = get_ipos_data()
    # active_ipos_df, upcomings_ipos_df = get_ipos_data()
    saved_subscriptions = Subscription.query.all()
    today = now_asia.strftime(format)
    print('Today\'s timestamp:', type(today), today)

    all_ipos = get_ipos_data()
    print(all_ipos.shape, len(saved_subscriptions))
    print(sorted(all_ipos['Issuer Company'].unique()))
    all_ipos[all_ipos['Close']<today].apply(lambda rec: persist_subscription(rec) if not check_if_sub_is_persisted(rec, saved_subscriptions) else None, axis=1)
    # print(check_if_sub_is_persisted(all_ipos.iloc[0], saved_subscriptions), all_ipos.iloc[0])
    # print(all_ipos.apply(lambda rec: True if (check_if_sub_is_persisted(rec, saved_subscriptions)) else False, axis=1))

    active_ipos_df = all_ipos[(all_ipos['Close'] >= today) & (all_ipos['Open'] <= today)]
    # active_ipos_df = active_ipos_df[active_ipos_df['Open'] <= today]
    upcomings_ipos_df = all_ipos[(all_ipos['Open'] > today) | (all_ipos['Open'].isna())]
    # past_ipos_df = df[df['Close'] < today]

    # active_ipos_df = active_ipos_df.apply(lambda row: get_sub_data(row, saved_subscriptions), axis=1)
    # past_ipos_df = past_ipos_df.apply(lambda row: get_sub_data(row), axis=1)

    # get ipo recommendation statistics for upcoming ipos
    print('Active ipos', active_ipos_df.shape)
    print('upcomings_ipos_df', upcomings_ipos_df.shape)
    active_ipos_df = active_ipos_df.apply(lambda row: get_recommendations_statistics(row), axis=1)
    active_ipos_df = active_ipos_df.apply(lambda row: fetch_and_map_subscription_data_to_row(row), axis=1)
    # print(active_ipos_df['subscription_data_url'].values)

    active_ipos_df = active_ipos_df.sort_values(by='Close').reset_index()
    upcomings_ipos_df = upcomings_ipos_df.sort_values(by='Open').reset_index()
    # past_ipos_df = past_ipos_df.sort_values(by='Open', ascending= False).reset_index()

    # return active_ipos_df, upcomings_ipos_df, past_ipos_df
    return active_ipos_df, upcomings_ipos_df

def check_if_sub_is_persisted(row, all_saved_subs):
    is_present = True if next((x for x in all_saved_subs if x.company_name==row['Issuer Company']), None) else False
    print(row['Issuer Company'], 'is present? =', is_present)
    return is_present

def format_subscription_url(row):
    print('*'*50)
    print(row)
    ipo_name = row['ipo_name'].replace('-','%20')
    print(ipo_name)
    ipo_id = row['ipo_id']
    print(ipo_name)
    url = 'https://www.chittorgarh.com/ajax/ajax.asp?AjaxCall=GetSubscriptionPageIPOBiddingStatus&AjaxVal={ipo_id}&CompanyShortName={ipo_name}'.format(ipo_name=ipo_name,ipo_id=ipo_id)
    print(url)
    print('*'*50)
    return url

def extract_sub_data(sub, row):
    row['Issuer Company'] = sub.company_name
    row['Open'] = sub.open
    row['Close'] = sub.close
    row['Issue Price (Rs)'] = sub.issue_price
    row['Issue Size (Rs Cr)'] = sub.issue_size
    row['Total Subscription'] = sub.total_sub
    row['Subscription Page'] = sub.sub_page
    row['Main Page'] = sub.main_page
    row['Exchange Symbol'] = sub.exchange_symbol
    return row

def get_recommendations_statistics(row):
    print('row in get_recommendations_statistics(row): ==>', row['URL'])
    ipo_home_page_response = reqs.get(row['URL'])
    home_page_soup = BeautifulSoup(ipo_home_page_response.content, 'html.parser')
    recomms_list = list()
    for i in home_page_soup.find_all('div'):
        if 'IPO Reviews / Ratings' in i.text:
            if len(i.find_all('div')) == 2:
                for j in i.find_all('li'):
                    rat_rev = j.text.split('-')
                    recomms_list.append(rat_rev[1].strip())
    counter = Counter(recomms_list)
    counter = sorted(counter.items(), key=lambda i: i[1], reverse=True)
    total_revs = 0
    for i in counter:
        total_revs = total_revs + i[1]
        
    final_string = ''
    for i in counter:
        perc = round((i[1]/total_revs) * 100, 2)
        final_string = final_string + i[0] + ' - ' + str(perc) + '%(' + str(i[1]) + '/' + str(total_revs) + ');\n'
    row['Recommendations Statistics'] = final_string
    # print(row)
    return row

def fetch_all_past_ipos():
    all_ipos = Subscription.query.all()
    return all_ipos