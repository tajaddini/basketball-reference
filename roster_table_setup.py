import pandas as pd
from sqlalchemy import create_engine
import os

folder_path = os.path.dirname(os.path.abspath(__file__))
csv_name = 'roster_data.csv' 
csv_path = os.path.join(folder_path, csv_name)

df = pd.read_csv(csv_path)
db_path = os.path.join(folder_path, 'roster_data.sqlite')

engine = create_engine(f'sqlite:///{db_path}')
df.to_sql('roster', con=engine, if_exists='replace', index=False)