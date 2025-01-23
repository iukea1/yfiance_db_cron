# Import required SQLAlchemy components and other dependencies
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, Boolean, UniqueConstraint, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create base class for declarative models
Base = declarative_base()

# Model for storing tickers
class Ticker(Base):
    __tablename__ = 'tickers'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)  # Stock symbol
    name = Column(String)                                # Company name
    is_active = Column(Boolean, default=True)            # Whether the ticker is still active

# Model for storing historical stock price data
class StockPrice(Base):
    __tablename__ = 'stock_prices'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)      # Date of price data
    open = Column(Float)                     # Opening price
    high = Column(Float)                     # High price
    low = Column(Float)                      # Low price 
    close = Column(Float)                    # Closing price
    volume = Column(Integer)                 # Trading volume
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique ticker/date combinations and add index for performance
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', name='uix_stock_prices_ticker_date'),
        Index('idx_stock_prices_ticker_date', 'ticker_id', 'date')
    )

# Model for storing stock split events
class StockSplit(Base):
    __tablename__ = 'stock_splits'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)       # Split date
    split_ratio = Column(Float)               # Split ratio (e.g., 2.0 for 2:1 split)
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique ticker/date combinations
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', name='uix_stock_splits_ticker_date'),
    )

# Model for storing dividend payments
class Dividend(Base):
    __tablename__ = 'dividends'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)       # Dividend payment date
    amount = Column(Float)                    # Dividend amount
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique ticker/date combinations
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', name='uix_dividends_ticker_date'),
    )

# Model for storing analyst price targets
class AnalystPriceTarget(Base):
    __tablename__ = 'analyst_price_targets'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)       # Date of price target
    firm = Column(String)                     # Analyst firm name
    target_price = Column(Float)              # Price target
    rating = Column(String)                   # Stock rating (e.g., Buy, Sell)
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique ticker/date/firm combinations
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', 'firm', name='uix_apt_ticker_date_firm'),
    )

# Model for storing balance sheet data
class BalanceSheet(Base):
    __tablename__ = 'balance_sheet'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)        # Report date
    item_name = Column(String, nullable=False) # Balance sheet item name
    value = Column(Float)                      # Item value
    is_quarterly = Column(Boolean)             # Quarterly or annual report flag
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique combinations and add index for performance
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', 'item_name', 'is_quarterly', 
                        name='uix_balance_sheet_ticker_date_item'),
        Index('idx_balance_sheet_ticker_date', 'ticker_id', 'date')
    )

# Model for storing cash flow statement data
class CashFlow(Base):
    __tablename__ = 'cash_flow'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)        # Report date
    item_name = Column(String, nullable=False) # Cash flow item name
    value = Column(Float)                      # Item value
    is_quarterly = Column(Boolean)             # Quarterly or annual report flag
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique combinations and add index for performance
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', 'item_name', 'is_quarterly', 
                        name='uix_cash_flow_ticker_date_item'),
        Index('idx_cash_flow_ticker_date', 'ticker_id', 'date')
    )

# Model for storing income statement data
class IncomeStatement(Base):
    __tablename__ = 'income_statement'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)        # Report date
    item_name = Column(String, nullable=False) # Income statement item name
    value = Column(Float)                      # Item value
    is_quarterly = Column(Boolean)             # Quarterly or annual report flag
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique combinations and add index for performance
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', 'item_name', 'is_quarterly', 
                        name='uix_income_statement_ticker_date_item'),
        Index('idx_income_statement_ticker_date', 'ticker_id', 'date')
    )

# Model for storing sustainability metrics
class Sustainability(Base):
    __tablename__ = 'sustainability'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)        # Report date
    metric_name = Column(String, nullable=False) # Sustainability metric name
    value = Column(Float)                      # Metric value
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique combinations
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', 'metric_name', 
                        name='uix_sustainability_ticker_date_metric'),
    )

# Model for storing calendar events (earnings, conferences etc.)
class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    event_type = Column(String, nullable=False) # Type of event
    date = Column(Date, nullable=False)        # Event date
    description = Column(String)               # Event description
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique combinations
    __table_args__ = (
        UniqueConstraint('ticker_id', 'event_type', 'date', 
                        name='uix_calendar_events_ticker_type_date'),
    )

# Model for storing capital gains distributions
class CapitalGain(Base):
    __tablename__ = 'capital_gains'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)       # Distribution date
    amount = Column(Float)                    # Distribution amount
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique ticker/date combinations
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', name='uix_capital_gains_ticker_date'),
    )

# Model for storing analyst recommendations
class AnalystRecommendation(Base):
    __tablename__ = 'analyst_recommendations'
    
    id = Column(Integer, primary_key=True)
    ticker_id = Column(Integer, ForeignKey('tickers.id'), nullable=False)
    date = Column(Date, nullable=False)        # Recommendation date
    firm = Column(String, nullable=False)      # Analyst firm name
    from_grade = Column(String)                # Previous rating
    to_grade = Column(String)                  # New rating
    action = Column(String)                    # Action taken (upgrade/downgrade)
    
    # Relationship
    ticker = relationship("Ticker")
    
    # Ensure unique combinations
    __table_args__ = (
        UniqueConstraint('ticker_id', 'date', 'firm', 
                        name='uix_analyst_recommendations_ticker_date_firm'),
    )

# Function to initialize the database and create all tables
def init_db(database_url='sqlite:///finance_data.db'):
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return engine

# Function to create a new database session
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

# Main execution block for database initialization
if __name__ == '__main__':
    engine = init_db()
    session = get_session(engine)