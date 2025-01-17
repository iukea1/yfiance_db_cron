from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    historical_prices = relationship("HistoricalPrice", back_populates="stock")
    balance_sheets = relationship("BalanceSheet", back_populates="stock")
    income_statements = relationship("IncomeStatement", back_populates="stock")
    cash_flows = relationship("CashFlow", back_populates="stock")
    analyst_recommendations = relationship("AnalystRecommendation", back_populates="stock")
    institutional_holders = relationship("InstitutionalHolder", back_populates="stock")
    dividends = relationship("Dividend", back_populates="stock")
    earnings = relationship("Earnings", back_populates="stock")

class HistoricalPrice(Base):
    __tablename__ = 'historical_prices'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)
    dividends = Column(Float)
    stock_splits = Column(Float)
    
    stock = relationship("Stock", back_populates="historical_prices")
    __table_args__ = (UniqueConstraint('stock_id', 'date', name='uix_stock_date'),)

class BalanceSheet(Base):
    __tablename__ = 'balance_sheets'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column(Date, nullable=False)
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)
    cash = Column(Float)
    total_current_assets = Column(Float)
    total_current_liabilities = Column(Float)
    
    stock = relationship("Stock", back_populates="balance_sheets")
    __table_args__ = (UniqueConstraint('stock_id', 'date', name='uix_stock_date_bs'),)

class IncomeStatement(Base):
    __tablename__ = 'income_statements'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column(Date, nullable=False)
    total_revenue = Column(Float)
    gross_profit = Column(Float)
    operating_income = Column(Float)
    net_income = Column(Float)
    
    stock = relationship("Stock", back_populates="income_statements")
    __table_args__ = (UniqueConstraint('stock_id', 'date', name='uix_stock_date_is'),)

class CashFlow(Base):
    __tablename__ = 'cash_flows'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column(Date, nullable=False)
    operating_cash_flow = Column(Float)
    investing_cash_flow = Column(Float)
    financing_cash_flow = Column(Float)
    net_cash_flow = Column(Float)
    
    stock = relationship("Stock", back_populates="cash_flows")
    __table_args__ = (UniqueConstraint('stock_id', 'date', name='uix_stock_date_cf'),)

class AnalystRecommendation(Base):
    __tablename__ = 'analyst_recommendations'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column(Date, nullable=False)
    firm = Column(String)
    to_grade = Column(String)
    from_grade = Column(String)
    action = Column(String)
    
    stock = relationship("Stock", back_populates="analyst_recommendations")

class InstitutionalHolder(Base):
    __tablename__ = 'institutional_holders'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    holder = Column(String)
    shares = Column(Integer)
    date_reported = Column(Date)
    value = Column(Float)
    
    stock = relationship("Stock", back_populates="institutional_holders")

class Dividend(Base):
    __tablename__ = 'dividends'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column(Date, nullable=False)
    amount = Column(Float)
    
    stock = relationship("Stock", back_populates="dividends")
    __table_args__ = (UniqueConstraint('stock_id', 'date', name='uix_stock_date_div'),)

class Earnings(Base):
    __tablename__ = 'earnings'
    
    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    date = Column(Date, nullable=False)
    actual_eps = Column(Float)
    estimated_eps = Column(Float)
    surprise = Column(Float)
    surprise_percentage = Column(Float)
    
    stock = relationship("Stock", back_populates="earnings")
    __table_args__ = (UniqueConstraint('stock_id', 'date', name='uix_stock_date_earn'),)