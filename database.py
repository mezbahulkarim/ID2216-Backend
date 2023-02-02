from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy import URL

#user=postgres password=[YOUR-PASSWORD] host=db.dtohwsymdfnwstwyburf.supabase.co port=5432 database=postgres

# url_object = URL.create(
#     "postgresql",
#     username="postgres",
#     password=passwd,
#     host="db.dtohwsymdfnwstwyburf.supabase.co",
#     database="postgres"
# )

#postgres://postgres:[YOUR-PASSWORD]@db.dtohwsymdfnwstwyburf.supabase.co:6543/postgres  //Using This

#Use Connection Pooling Port
load_dotenv()
supabase_passwd = str(os.environ.get("SUPABASE_PASSWORD"))
pool_url = "postgresql://postgres:"+supabase_passwd+"@db.dtohwsymdfnwstwyburf.supabase.co:6543/postgres"
engine = create_engine(pool_url)

SessionLocal = sessionmaker(bind= engine, autocommit=False, autoflush=False)
Base = declarative_base()
