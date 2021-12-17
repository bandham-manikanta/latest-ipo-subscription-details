from app_main import db
from dataclasses import dataclass

@dataclass
class Subscription(db.Model):
    __tablename__ = 'IPO_SUBSCRIPTION_DATA'

    company_name: str
    open: str
    close: str
    issue_price: str
    issue_size: str
    qualified_inst_sub: str
    non_inst_sub: str
    retail_indv_sub: str
    employee_sub: str
    others_sub: str
    total_sub: str
    sub_page: str
    main_page: str
    exchange_symbol: str

    company_name = db.Column(db.String, primary_key=True)
    open = db.Column(db.String)
    close = db.Column(db.String)
    issue_price = db.Column(db.String)
    issue_size = db.Column(db.String)
    qualified_inst_sub = db.Column(db.String)
    non_inst_sub = db.Column(db.String)
    retail_indv_sub = db.Column(db.String)
    employee_sub = db.Column(db.String)
    others_sub = db.Column(db.String)
    total_sub = db.Column(db.String)
    sub_page = db.Column(db.String)
    main_page = db.Column(db.String)
    exchange_symbol = db.Column(db.String)