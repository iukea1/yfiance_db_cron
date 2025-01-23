import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from typing import Optional, Union
import numpy as np
from modles import (
    Ticker, StockPrice, StockSplit, Dividend, AnalystPriceTarget,
    BalanceSheet, CashFlow, IncomeStatement, Sustainability,
    CalendarEvent, CapitalGain, AnalystRecommendation
)
import time
# Set up logging configuration for tracking script execution
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockDataCollector:
    """
    A class to collect and store stock market data from Yahoo Finance.
    Handles data collection for prices, dividends, financial statements,
    and other stock-related metrics.
    """
    
    def __init__(self, ticker_symbol: str, db_url: str):
        """
        Initialize the stock data collector.
        
        Args:
            ticker_symbol (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            db_url (str): Database connection URL for data storage
        """
        self.ticker_symbol = ticker_symbol
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.stock_data = yf.Ticker(ticker_symbol)
        self.ticker_id = None
        
    def safe_float_convert(self, value: Union[int, float, str, None]) -> Optional[float]:
        """
        Safely convert various data types to float, handling null values and errors.
        Used throughout the class to ensure consistent data type conversion.
        """
        if pd.isna(value) or value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_or_create_ticker(self, session) -> None:
        """
        Retrieve existing ticker from database or create new entry if not found.
        Also fetches basic company information from Yahoo Finance.
        """
        ticker = session.query(Ticker).filter_by(symbol=self.ticker_symbol).first()
        if not ticker:
            # Get company info from yfinance
            info = self.stock_data.info
            company_name = info.get('longName', None)
            
            ticker = Ticker(
                symbol=self.ticker_symbol,
                name=company_name,
                is_active=True
            )
            session.add(ticker)
            session.flush()  # This will populate the id without committing
            logger.info(f"Created new ticker entry for {self.ticker_symbol}")
        
        self.ticker_id = ticker.id

    def save_historical_prices(self, session) -> None:
        """
        Fetch and store historical price data including:
        - Daily open, high, low, close prices
        - Trading volume
        Data is retrieved for the entire available history of the stock.
        """
        try:
            df = self.stock_data.history(period="max")
            for index, row in df.iterrows():
                stock_price = StockPrice(
                    ticker_id=self.ticker_id,
                    date=index,
                    open=self.safe_float_convert(row['Open']),
                    high=self.safe_float_convert(row['High']),
                    low=self.safe_float_convert(row['Low']),
                    close=self.safe_float_convert(row['Close']),
                    volume=int(row['Volume']) if pd.notna(row['Volume']) else None
                )
                session.add(stock_price)
            logger.info(f"Saved historical prices for {self.ticker_symbol}")
        except Exception as e:
            logger.error(f"Error saving historical prices: {str(e)}")
            raise

    def save_splits_and_dividends(self, session) -> None:
        """
        Store historical stock splits and dividend payments.
        - Stock splits: Records when shares were split and the split ratio
        - Dividends: Records all dividend payments and their amounts
        """
        try:
            # Save splits
            splits_df = self.stock_data.splits
            for index, split_ratio in splits_df.items():
                split = StockSplit(
                    ticker_id=self.ticker_id,
                    date=index,
                    split_ratio=self.safe_float_convert(split_ratio)
                )
                session.add(split)

            # Save dividends
            dividends_df = self.stock_data.dividends
            for index, amount in dividends_df.items():
                dividend = Dividend(
                    ticker_id=self.ticker_id,
                    date=index,
                    amount=self.safe_float_convert(amount)
                )
                session.add(dividend)
            
            logger.info(f"Saved splits and dividends for {self.ticker_symbol}")
        except Exception as e:
            logger.error(f"Error saving splits and dividends: {str(e)}")
            raise

    def save_analyst_data(self, session) -> None:
        """
        Store analyst recommendations and price targets.
        Includes:
        - Target prices set by analysts
        - Firm names
        - Ratings (e.g., Buy, Sell, Hold)
        """
        try:
            price_targets = self.stock_data.analyst_price_targets
            if isinstance(price_targets, pd.DataFrame) and not price_targets.empty:
                for index, row in price_targets.iterrows():
                    target = AnalystPriceTarget(
                        ticker_id=self.ticker_id,
                        date=index,
                        firm=str(row.get('Firm', '')),
                        target_price=self.safe_float_convert(row.get('Target Price')),
                        rating=str(row.get('Rating', ''))
                    )
                    session.add(target)
            logger.info(f"Saved analyst data for {self.ticker_symbol}")
        except Exception as e:
            logger.error(f"Error saving analyst data: {str(e)}")
            raise

    def save_financial_statements(self, session) -> None:
        """
        Store quarterly financial statement data including:
        - Balance Sheet: Assets, liabilities, and equity
        - Cash Flow Statement: Operating, investing, and financing activities
        - Income Statement: Revenue, expenses, and earnings
        Data is stored with item-by-item granularity for detailed analysis.
        """
        try:
            # Balance Sheet
            balance_sheet = self.stock_data.quarterly_balance_sheet
            if isinstance(balance_sheet, pd.DataFrame):
                for date in balance_sheet.columns:
                    for item_name, value in balance_sheet[date].items():
                        if pd.notna(value):
                            balance = BalanceSheet(
                                ticker_id=self.ticker_id,
                                date=date,
                                item_name=str(item_name),
                                value=self.safe_float_convert(value),
                                is_quarterly=True
                            )
                            session.add(balance)

            # Cash Flow
            cash_flow = self.stock_data.quarterly_cashflow
            if isinstance(cash_flow, pd.DataFrame):
                for date in cash_flow.columns:
                    for item_name, value in cash_flow[date].items():
                        if pd.notna(value):
                            cashflow = CashFlow(
                                ticker_id=self.ticker_id,
                                date=date,
                                item_name=str(item_name),
                                value=self.safe_float_convert(value),
                                is_quarterly=True
                            )
                            session.add(cashflow)

            # Income Statement
            income_stmt = self.stock_data.quarterly_financials
            if isinstance(income_stmt, pd.DataFrame):
                for date in income_stmt.columns:
                    for item_name, value in income_stmt[date].items():
                        if pd.notna(value):
                            income = IncomeStatement(
                                ticker_id=self.ticker_id,
                                date=date,
                                item_name=str(item_name),
                                value=self.safe_float_convert(value),
                                is_quarterly=True
                            )
                            session.add(income)
                            
            #AnalystRecommendation
            analyst_recommendation = self.stock_data.recommendations
            if isinstance(analyst_recommendation, pd.DataFrame) and not analyst_recommendation.empty:
                for index, row in analyst_recommendation.iterrows():
                    # Convert Timestamp index to date object
                    date = index.date() if hasattr(index, 'date') else None
                    if date:  # Only add if we have a valid date
                        recommendation = AnalystRecommendation(
                            ticker_id=self.ticker_id,
                            date=date,
                            firm=str(row['Firm']) if 'Firm' in row else '',
                            to_grade=str(row['To Grade']) if 'To Grade' in row else '',
                            from_grade=str(row['From Grade']) if 'From Grade' in row else '',
                            action=str(row['Action']) if 'Action' in row else ''
                        )
                        session.add(recommendation)

            logger.info(f"Saved financial statements for {self.ticker_symbol}")
        except Exception as e:
            logger.error(f"Error saving financial statements: {str(e)}")
            raise

    def save_sustainability_data(self, session) -> None:
        """
        Store ESG (Environmental, Social, Governance) metrics and sustainability data.
        Captures current sustainability metrics with their corresponding values.
        """
        try:
            sustainability = self.stock_data.sustainability
            if isinstance(sustainability, pd.DataFrame):
                current_date = datetime.now().date()
                # Transpose if needed to get metrics as rows
                if len(sustainability.columns) > len(sustainability.index):
                    sustainability = sustainability.transpose()
                
                for index, row in sustainability.iterrows():
                    # Handle the case where values might be Series
                    value = row.iloc[0] if isinstance(row, pd.Series) else row
                    if pd.notna(value):
                        sustainability_record = Sustainability(
                            ticker_id=self.ticker_id,
                            date=current_date,
                            metric_name=str(index),
                            value=self.safe_float_convert(value)
                        )
                        session.add(sustainability_record)
            logger.info(f"Saved sustainability data for {self.ticker_symbol}")
        except Exception as e:
            logger.error(f"Error saving sustainability data: {str(e)}")
            raise

    def collect_and_save_all_data(self) -> None:
        """
        Main orchestration method that:
        1. Creates a database session
        2. Ensures ticker exists in database
        3. Collects and saves all available data types
        4. Handles transaction management and error cases
        """
        session = self.Session()
        try:
            # First, ensure ticker exists and get its ID
            self.get_or_create_ticker(session)
            # Now collect and save all related data
            self.save_historical_prices(session)
            self.save_splits_and_dividends(session)
            self.save_analyst_data(session)
            self.save_financial_statements(session)
            self.save_sustainability_data(session)
            
            session.commit()
            logger.info(f"Successfully saved all data for {self.ticker_symbol}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error in data collection process: {str(e)}")
            raise
        finally:
            session.close()

def read_ticker_symbols(file_path: str) -> list[str]:
    """
    Read stock ticker symbols from a text file.
    Each symbol should be on a new line in the file.
    Handles file reading errors and filters empty lines.
    """
    try:
        with open(file_path, 'r') as f:
            # Read lines, strip whitespace, and filter out empty lines
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"Ticker symbols file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading ticker symbols file: {str(e)}")
        raise

def main():
    """
    Main execution function that:
    1. Reads ticker symbols from a specified file
    2. Processes each ticker sequentially
    3. Continues processing remaining tickers if one fails
    4. Logs progress and errors throughout execution
    """
    file_path = '/Users/jordanchaput/Desktop/coding_projects/python_projects/fiance_project/yfiance_db_cron/backend/stocks.txt'
    try:
        ticker_symbols = read_ticker_symbols(file_path)
        logger.info(f"Processing {len(ticker_symbols)} ticker symbols")
        
        for symbol in ticker_symbols:
            try:
                logger.info(f"Processing ticker: {symbol}")
                collector = StockDataCollector(
                    ticker_symbol=symbol,
                    db_url='sqlite:///finance_data.db'
                )
                collector.collect_and_save_all_data()
                logger.info(f"Successfully processed ticker: {symbol}")
            except Exception as e:
                logger.error(f"Error processing ticker {symbol}: {str(e)}")
                # Continue with next ticker instead of stopping the entire process
                continue
                
            # Add 5 second delay before next ticker
            time.sleep(5)
            #print sleeping 
            logger.info(f"Sleeping for 5 seconds before processing next ticker")
            
                
    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()