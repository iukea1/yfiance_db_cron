from sqlalchemy import create_engine, Column, Integer, Float, String, Date, Boolean, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class StockPrice(Base):
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uix_stock_prices_ticker_date'),
        Index('idx_stock_prices_ticker_date', 'ticker', 'date')
    )

class StockSplit(Base):
    __tablename__ = 'stock_splits'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    split_ratio = Column(Float)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uix_stock_splits_ticker_date'),
    )

class Dividend(Base):
    __tablename__ = 'dividends'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uix_dividends_ticker_date'),
    )

class AnalystPriceTarget(Base):
    __tablename__ = 'analyst_price_targets'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    firm = Column(String)
    target_price = Column(Float)
    rating = Column(String)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', 'firm', name='uix_apt_ticker_date_firm'),
    )

class BalanceSheet(Base):
    __tablename__ = 'balance_sheet'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    item_name = Column(String, nullable=False)
    value = Column(Float)
    is_quarterly = Column(Boolean)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', 'item_name', 'is_quarterly', 
                        name='uix_balance_sheet_ticker_date_item'),
        Index('idx_balance_sheet_ticker_date', 'ticker', 'date')
    )

class CashFlow(Base):
    __tablename__ = 'cash_flow'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    item_name = Column(String, nullable=False)
    value = Column(Float)
    is_quarterly = Column(Boolean)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', 'item_name', 'is_quarterly', 
                        name='uix_cash_flow_ticker_date_item'),
        Index('idx_cash_flow_ticker_date', 'ticker', 'date')
    )

class IncomeStatement(Base):
    __tablename__ = 'income_statement'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    item_name = Column(String, nullable=False)
    value = Column(Float)
    is_quarterly = Column(Boolean)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', 'item_name', 'is_quarterly', 
                        name='uix_income_statement_ticker_date_item'),
        Index('idx_income_statement_ticker_date', 'ticker', 'date')
    )

class Sustainability(Base):
    __tablename__ = 'sustainability'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Float)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', 'metric_name', 
                        name='uix_sustainability_ticker_date_metric'),
    )

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'event_type', 'date', 
                        name='uix_calendar_events_ticker_type_date'),
    )

class CapitalGain(Base):
    __tablename__ = 'capital_gains'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', name='uix_capital_gains_ticker_date'),
    )

class AnalystRecommendation(Base):
    __tablename__ = 'analyst_recommendations'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    firm = Column(String, nullable=False)
    from_grade = Column(String)
    to_grade = Column(String)
    action = Column(String)
    
    __table_args__ = (
        UniqueConstraint('ticker', 'date', 'firm', 
                        name='uix_analyst_recommendations_ticker_date_firm'),
    )

# Database initialization function
def init_db(database_url='sqlite:///finance_data.db'):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine

# Create a session factory
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

# Usage example:
if __name__ == '__main__':
    engine = init_db()
    session = get_session(engine)