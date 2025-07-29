from sqlalchemy import create_engine, Column, String, Integer, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ResponseData(Base):
    __tablename__ = 'response_data'
    id = Column(Integer, primary_key=True)
    signature = Column(String, unique=True)
    method = Column(String)
    params = Column(JSON)
    response = Column(JSON)

class dbConfig:
    def __init__(self):
        # Example configuration, adjust as per your actual database setup
        engine = create_engine('postgresql://partners:solcatch123!!!456@192.168.0.100:5432/solcatcher')
        Session = sessionmaker(bind=engine)
        self.session = Session()

# This function checks if an entry exists in the database for the given method and parameters.
def fetch_response_data(method, params):
    session = dbConfig().session
    existing_entry = session.query(ResponseData).filter_by(method=method, params=json.dumps(params)).first()

    if existing_entry:
        print(f"Found existing entry for method: {method} and params: {params}.")
        return json.loads(existing_entry.response)
    
    return None
