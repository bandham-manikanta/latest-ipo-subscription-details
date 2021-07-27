import requests as reqs
import pandas as pd
from datetime import date
from bs4 import BeautifulSoup

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
    df['Close'] = pd.to_datetime(df['Close'].dt.strftime("%Y-%m-%d 16:30:00"))

    df = df[~((df['Open']=='') | (df['Open'].isna()))]
    df['Open'] = pd.to_datetime(df['Open'])
    df['Open'] = pd.to_datetime(df['Open'].dt.strftime("%Y-%m-%d 10:00:00"))

    df['Qualified Institutional Subscription'] = None
    df['Non Institutional Subscription'] = None
    df['Retail Individual Subscription'] = None
    df['Employee Subscription'] = None
    df['Others Subscription'] = None
    df['Total Subscription'] = None

    df['ipo_name'] = df['URL'].apply(lambda x: x.split('/')[4].strip())
    df['ipo_id'] = df['URL'].apply(lambda x: x.split('/')[5].strip())
    df['subscription_data_url'] = df.apply(lambda row: format_subscription_url(row), axis=1)

    active_ipos_df = df[df['Close'] >= pd.to_datetime('today')]
    active_ipos_df = active_ipos_df[active_ipos_df['Open'] <= pd.to_datetime('today')]

    upcomingz_ipos_df = df[df['Open'] > pd.to_datetime('today')]
    past_ipos_df = df[df['Close'] < pd.to_datetime('today')]

    return active_ipos_df, upcomingz_ipos_df, past_ipos_df

def get_subscription_data(url:str) -> pd.DataFrame():
    sub_response = reqs.get(url)
    sup_soup = BeautifulSoup(sub_response.content, 'html.parser')
    
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

def get_sub_data(row):
    print(row['subscription_data_url'])
    sub_data = get_subscription_data(row['subscription_data_url'])
    row['Qualified Institutional Subscription'] = sub_data.iloc[0, :]['Subscription Status']
    row['Non Institutional Subscription'] = sub_data.iloc[1, :]['Subscription Status']
    row['Retail Individual Subscription'] = sub_data.iloc[2, :]['Subscription Status']
    row['Employee Subscription'] = sub_data.iloc[3, :]['Subscription Status']
    row['Others Subscription'] = sub_data.iloc[4, :]['Subscription Status']
    row['Total Subscription'] = sub_data.iloc[5, :]['Subscription Status']
    return row

def get_ipo_subscription_details():
    active_ipos_df, upcomings_ipos_df, past_ipos_df = get_ipos_data()

    if active_ipos_df.shape[0] != 0:
        active_ipos_df = active_ipos_df.apply(lambda row: get_sub_data(row), axis=1)

    active_ipos_df = active_ipos_df.sort_values(by='Open')
    upcomings_ipos_df = upcomings_ipos_df.sort_values(by='Open').reset_index()
    past_ipos_df = past_ipos_df.sort_values(by='Open', ascending= False).reset_index()

    return active_ipos_df, upcomings_ipos_df, past_ipos_df

def format_subscription_url(row):
    ipo_name = row['ipo_name'].replace('-','%20')
    ipo_id = row['ipo_id']
    url = 'https://www.chittorgarh.com/ajax/ajax.asp?AjaxCall=GetSubscriptionPageIPOBiddingStatus&AjaxVal={ipo_id}&CompanyShortName={ipo_name}'.format(ipo_name=ipo_name,ipo_id=ipo_id)
    return url
