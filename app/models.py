from sqlalchemy import Column, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Define the sequence for employee ID generation
empid_sequence = Sequence('empid_seq', start=1, increment=1)

class emp(Base):
    __tablename__ = "emp_info"
    
    empid = Column(String(10), primary_key=True, index=True)
    name = Column(String, nullable=False)
    phno = Column(String, nullable=False)
    email = Column(String, nullable=False)
    dob = Column(String, nullable=False)
    addr = Column(String, nullable=False)
    password = Column(String, nullable=False)