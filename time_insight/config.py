import os
import sys

#BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if getattr(sys, 'frozen', False):   #check if application works as builded or not builded
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#create db folder if not exists
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'data', 'time_insight.db')}"

#DATABASE_URL = "sqlite:///../data/time_insight.db"

DB_PATH = os.path.join(DATA_DIR, 'time_insight.db')