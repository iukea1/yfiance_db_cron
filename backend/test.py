from db_setup import DatabaseConnection
import yfinance as yf
import pandas as pd
from database import Stock, HistoricalPrice, BalanceSheet, IncomeStatement, CashFlow, AnalystRecommendation, InstitutionalHolder, Dividend, Earnings
from datetime import datetime
from sqlalchemy import func

def verify_data(session):
    # Get count of records
    stock_count = session.query(Stock).count()
    prices_count = session.query(HistoricalPrice).count()
    
    # Get the first and last dates
    first_date = session.query(func.min(HistoricalPrice.date)).scalar()
    last_date = session.query(func.max(HistoricalPrice.date)).scalar()
    
    print("\nData Verification:")
    print(f"Number of stocks: {stock_count}")
    print(f"Number of price records: {prices_count}")
    print(f"Date range: {first_date} to {last_date}")
    
    # Get sample of price data
    sample_prices = session.query(HistoricalPrice)\
        .order_by(HistoricalPrice.date.desc())\
        .limit(5)\
        .all()
    
    print("\nMost recent price records:")
    for price in sample_prices:
        print(f"Date: {price.date}, Close: {price.close}, Volume: {price.volume}")

def main():
    # Initialize database
    db = DatabaseConnection()
    session = db.get_session()
    
    try:
        # Create a new stock entry
        symbol = "MSFT"
        
        # Check if stock already exists
        stock = session.query(Stock).filter_by(symbol=symbol).first()
        if not stock:
            stock = Stock(symbol=symbol)
            session.add(stock)
            session.commit()
        
        # Get stock data from yfinance
        yf_stock = yf.Ticker(symbol)
        
        # Store historical prices
        history_df = yf_stock.history(period='1y')
        print(f"\nProcessing {len(history_df)} historical prices...")
        
        for date, row in history_df.iterrows():
            # Check if price already exists for this date
            existing_price = session.query(HistoricalPrice)\
                .filter_by(stock_id=stock.id, date=date.date())\
                .first()
            
            if not existing_price:
                hist_price = HistoricalPrice(
                    stock_id=stock.id,
                    date=date.date(),
                    open=row['Open'],
                    high=row['High'],
                    low=row['Low'],
                    close=row['Close'],
                    volume=int(row['Volume']),
                    dividends=row['Dividends'],
                    stock_splits=row['Stock Splits']
                )
                session.add(hist_price)
        
        # Commit the changes
        session.commit()
        print(f"Successfully stored data for {symbol}")
        
        # Verify the data
        verify_data(session)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        session.rollback()
    
    finally:
        session.close()
        db.close()

if __name__ == "__main__":
    main()