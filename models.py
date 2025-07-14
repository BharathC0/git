from sqlalchemy import Column, Integer, String, Float, Date, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Invoice(Base):
    __tablename__ = 'invoices'
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    extracted_text = Column(Text)
    category = Column(String)
    amount = Column(Float)
    date = Column(String)
    vendor = Column(String) 