import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging
from typing import Optional, Union
import numpy as np
from modles import (
    StockPrice, StockSplit, Dividend, AnalystPriceTarget,
    BalanceSheet, CashFlow, IncomeStatement, Sustainability,
    CalendarEvent, CapitalGain, AnalystRecommendation
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StockDataCollector:
    def __init__(self, ticker: str, db_url: str):
        """
        Initialize the stock data collector.
        
        Args:
            ticker (str): Stock ticker symbol
            db_url (str): Database connection URL
        """
        self.ticker = ticker
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.stock_data = yf.Ticker(ticker)
        
    def safe_float_convert(self, value: Union[int, float, str, None]) -> Optional[float]:
        """Safely convert a value to float."""
        if pd.isna(value) or value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def save_historical_prices(self, session) -> None:
        """Save historical price data to database."""
        try:
            df = self.stock_data.history(period="max")
            for index, row in df.iterrows():
                stock_price = StockPrice(
                    ticker=self.ticker,
                    date=index,
                    open=self.safe_float_convert(row['Open']),
                    high=self.safe_float_convert(row['High']),
                    low=self.safe_float_convert(row['Low']),
                    close=self.safe_float_convert(row['Close']),
                    volume=int(row['Volume']) if pd.notna(row['Volume']) else None
                )
                session.add(stock_price)
            logger.info(f"Saved historical prices for {self.ticker}")
        except Exception as e:
            logger.error(f"Error saving historical prices: {str(e)}")
            raise

    def save_splits_and_dividends(self, session) -> None:
        """Save splits and dividends data to database."""
        try:
            # Save splits
            splits_df = self.stock_data.splits
            for index, split_ratio in splits_df.items():
                split = StockSplit(
                    ticker=self.ticker,
                    date=index,
                    split_ratio=self.safe_float_convert(split_ratio)
                )
                session.add(split)

            # Save dividends
            dividends_df = self.stock_data.dividends
            for index, amount in dividends_df.items():
                dividend = Dividend(
                    ticker=self.ticker,
                    date=index,
                    amount=self.safe_float_convert(amount)
                )
                session.add(dividend)
            
            logger.info(f"Saved splits and dividends for {self.ticker}")
        except Exception as e:
            logger.error(f"Error saving splits and dividends: {str(e)}")
            raise

    def save_analyst_data(self, session) -> None:
        """Save analyst price targets and recommendations."""
        try:
            price_targets = self.stock_data.analyst_price_targets
            if isinstance(price_targets, pd.DataFrame) and not price_targets.empty:
                for index, row in price_targets.iterrows():
                    target = AnalystPriceTarget(
                        ticker=self.ticker,
                        date=index,
                        firm=str(row.get('Firm', '')),
                        target_price=self.safe_float_convert(row.get('Target Price')),
                        rating=str(row.get('Rating', ''))
                    )
                    session.add(target)
            logger.info(f"Saved analyst data for {self.ticker}")
        except Exception as e:
            logger.error(f"Error saving analyst data: {str(e)}")
            raise

    def save_financial_statements(self, session) -> None:
        """Save quarterly financial statements data."""
        try:
            # Balance Sheet
            balance_sheet = self.stock_data.quarterly_balance_sheet
            if isinstance(balance_sheet, pd.DataFrame):
                for date in balance_sheet.columns:  # dates are in columns
                    for item_name, value in balance_sheet[date].items():  # items are in index
                        if pd.notna(value):
                            balance = BalanceSheet(
                                ticker=self.ticker,
                                date=date,  # date is already a datetime object from yfinance
                                item_name=str(item_name),  # item names are in the index
                                value=self.safe_float_convert(value),
                                is_quarterly=True
                            )
                            session.add(balance)

            # Cash Flow - apply the same fix
            cash_flow = self.stock_data.quarterly_cashflow
            if isinstance(cash_flow, pd.DataFrame):
                for date in cash_flow.columns:
                    for item_name, value in cash_flow[date].items():
                        if pd.notna(value):
                            cashflow = CashFlow(
                                ticker=self.ticker,
                                date=date,
                                item_name=str(item_name),
                                value=self.safe_float_convert(value),
                                is_quarterly=True
                            )
                            session.add(cashflow)

            # Income Statement - apply the same fix
            income_stmt = self.stock_data.quarterly_financials
            if isinstance(income_stmt, pd.DataFrame):
                for date in income_stmt.columns:
                    for item_name, value in income_stmt[date].items():
                        if pd.notna(value):
                            income = IncomeStatement(
                                ticker=self.ticker,
                                date=date,
                                item_name=str(item_name),
                                value=self.safe_float_convert(value),
                                is_quarterly=True
                            )
                            session.add(income)

            logger.info(f"Saved financial statements for {self.ticker}")
        except Exception as e:
            logger.error(f"Error saving financial statements: {str(e)}")
            raise

    def save_sustainability_data(self, session) -> None:
        """Save sustainability metrics."""
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
                            ticker=self.ticker,
                            date=current_date,
                            metric_name=str(index),
                            value=self.safe_float_convert(value)
                        )
                        session.add(sustainability_record)
            logger.info(f"Saved sustainability data for {self.ticker}")
        except Exception as e:
            logger.error(f"Error saving sustainability data: {str(e)}")
            raise

    def collect_and_save_all_data(self) -> None:
        """Main method to collect and save all stock data."""
        session = self.Session()
        try:
            self.save_historical_prices(session)
            self.save_splits_and_dividends(session)
            self.save_analyst_data(session)
            self.save_financial_statements(session)
            self.save_sustainability_data(session)
            
            session.commit()
            logger.info(f"Successfully saved all data for {self.ticker}")
        except Exception as e:
            session.rollback()
            logger.error(f"Error in data collection process: {str(e)}")
            raise
        finally:
            session.close()

def main():
    """Main execution function."""
    try:
        collector = StockDataCollector(
            ticker="MSFT",
            db_url='sqlite:///finance_data.db'
        )
        collector.collect_and_save_all_data()
    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()