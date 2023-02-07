from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

#postgres://postgres:[YOUR-PASSWORD]@db.dtohwsymdfnwstwyburf.supabase.co:6543/postgres  //Using This

#Use Connection Pooling Port
load_dotenv()
supabase_passwd = str(os.environ.get("SUPABASE_PASSWORD"))
pool_url = "postgresql://postgres:"+supabase_passwd+"@db.dtohwsymdfnwstwyburf.supabase.co:6543/postgres"
engine = create_engine(pool_url)

SessionLocal = sessionmaker(bind= engine, autocommit=False, autoflush=False)
Base = declarative_base()
