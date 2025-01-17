from backend.db_setup import DatabaseConnection
import yfinance as yf
import pandas as pd

from database import Stock, HistoricalPrice, BalanceSheet, IncomeStatement, CashFlow, AnalystRecommendation, InstitutionalHolder, Dividend, Earnings
from datetime import datetime
from sqlalchemy import func

def main():
    # Initialize database
    db = DatabaseConnection()
    session = db.get_session()
    
    # Get stock data
    dat = yf.Ticker("MSFT")







    # Calendar data
    calendar_df = dat.calendar
    if isinstance(calendar_df, pd.DataFrame):
        print("\nCalendar DataFrame:")
        print(calendar_df.head())
        print("Columns:", calendar_df.columns.tolist())

    # Analyst price targets
targets_df = dat.analyst_price_targets
if isinstance(targets_df, pd.DataFrame):
    print("\nAnalyst Price Targets:")
    print(targets_df.head())
    print("Columns:", targets_df.columns.tolist())

    print(income_df.head())
    print("Columns:", income_df.columns.tolist())

# Historical prices
history_df = dat.history(period='1y')
print("\nHistorical Prices:")
print(history_df.head())
print("Columns:", history_df.columns.tolist())

    # Balance sheet
    balance_df = dat.balance_sheet
    if isinstance(balance_df, pd.DataFrame):
        print("\nBalance Sheet:")
    print(balance_df.head())
    print("Columns:", balance_df.columns.tolist())

# Cash flow
cash_df = dat.cash_flow
if isinstance(cash_df, pd.DataFrame):
    print("\nCash Flow:")
    print(cash_df.head())
    print("Columns:", cash_df.columns.tolist())

# Earnings
earnings_df = dat.earnings
if isinstance(earnings_df, pd.DataFrame):
    print("\nEarnings:")
    print(earnings_df.head())
    print("Columns:", earnings_df.csolumns.tolist())
