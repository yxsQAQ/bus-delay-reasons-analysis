import warnings
import pymysql
import pandas as pd

from sqlalchemy import create_engine
from My_API import data_analysis


warnings.filterwarnings("ignore")

host="127.0.0.1"
user="root"
password="root123"
database="bods_bus_database"

conn = pymysql.connect(host=host, user=user, password=password, db=database)

all_table_names = data_analysis.get_table_names(conn)

df = data_analysis.get_data_from_tables(conn, all_table_names)

conn.close()

df['RecordedAtTime'] = pd.to_datetime(df['RecordedAtTime'])

df['hour'] = df['RecordedAtTime'].dt.hour

# Operator analysis
BRTB = df['Degree'].loc[df['OperatorRef']=='BRTB'].astype(float)
CT4N = df['Degree'].loc[df['OperatorRef']=='CT4N'].astype(float)
KBUS = df['Degree'].loc[df['OperatorRef']=='KBUS'].astype(float)
NDTR = df['Degree'].loc[df['OperatorRef']=='NDTR'].astype(float)
TBTN = df['Degree'].loc[df['OperatorRef']=='TBTN'].astype(float)
VECT = df['Degree'].loc[df['OperatorRef']=='VECT'].astype(float)

df_res = pd.DataFrame(columns=['Name', 'Length', 'Median', 'Mean', 'Mode', 'Maximum', 'Minimum',
                               'Variance', 'Quartile_0_25', 'Quartile_0_75', 'Skewness', 'Kurtosis'])

df_res = data_analysis.get_statistical_data('BRTB', BRTB, df_res)
df_res = data_analysis.get_statistical_data('KBUS', KBUS, df_res)
df_res = data_analysis.get_statistical_data('TBTN', TBTN, df_res)
df_res = data_analysis.get_statistical_data('VECT', VECT, df_res)

# Line analysis
_904 = df['Degree'].loc[df['LineRef']=='904'].astype(float)
cal = df['Degree'].loc[df['LineRef']=='cal'].astype(float)
cot = df['Degree'].loc[df['LineRef']=='cot'].astype(float)
i4 = df['Degree'].loc[df['LineRef']=='i4'].astype(float)
igo = df['Degree'].loc[df['LineRef']=='igo'].astype(float)
key = df['Degree'].loc[df['LineRef']=='key'].astype(float)
mln = df['Degree'].loc[df['LineRef']=='mln'].astype(float)
rv = df['Degree'].loc[df['LineRef']=='rv'].astype(float)
sky = df['Degree'].loc[df['LineRef']=='sky'].astype(float)
_18 = df['Degree'].loc[df['LineRef']=='18'].astype(float)
_9 = df['Degree'].loc[df['LineRef']=='9'].astype(float)
roy = df['Degree'].loc[df['LineRef']=='roy'].astype(float)
_3A = df['Degree'].loc[df['LineRef']=='3A'].astype(float)
_3B = df['Degree'].loc[df['LineRef']=='3B'].astype(float)
_3C = df['Degree'].loc[df['LineRef']=='3C'].astype(float)
one = df['Degree'].loc[df['LineRef']=='one'].astype(float)
ra = df['Degree'].loc[df['LineRef']=='ra'].astype(float)
two = df['Degree'].loc[df['LineRef']=='two'].astype(float)
_90 = df['Degree'].loc[df['LineRef']=='90'].astype(float)
_90B = df['Degree'].loc[df['LineRef']=='90B'].astype(float)
_90C = df['Degree'].loc[df['LineRef']=='90C'].astype(float)
_92 = df['Degree'].loc[df['LineRef']=='92'].astype(float)

df_res = data_analysis.get_statistical_data('cal', cal, df_res)
df_res = data_analysis.get_statistical_data('cot', cot, df_res)
df_res = data_analysis.get_statistical_data('i4', i4, df_res)
df_res = data_analysis.get_statistical_data('igo', igo, df_res)
df_res = data_analysis.get_statistical_data('key', key, df_res)
df_res = data_analysis.get_statistical_data('mln', mln, df_res)
df_res = data_analysis.get_statistical_data('sky', sky, df_res)
df_res = data_analysis.get_statistical_data('9', _9, df_res)
df_res = data_analysis.get_statistical_data('3A', _3A, df_res)
df_res = data_analysis.get_statistical_data('3B', _3B, df_res)
df_res = data_analysis.get_statistical_data('3C', _3C, df_res)
df_res = data_analysis.get_statistical_data('one', one, df_res)
df_res = data_analysis.get_statistical_data('ra', ra, df_res)
df_res = data_analysis.get_statistical_data('two', two, df_res)
df_res = data_analysis.get_statistical_data('90', _90, df_res)
df_res = data_analysis.get_statistical_data('90B', _90B, df_res)
df_res = data_analysis.get_statistical_data('90C', _90C, df_res)
df_res = data_analysis.get_statistical_data('92', _92, df_res)

# Direction analysis
inbound = df['Degree'].loc[df['DirectionRef']=='inbound'].astype(float)
outbound = df['Degree'].loc[df['DirectionRef']=='outbound'].astype(float)

df_res = data_analysis.get_statistical_data('inbound', inbound, df_res)
df_res = data_analysis.get_statistical_data('outbound', outbound, df_res)

# Time analysis
hour_data = {}

for i in range(24):
    hour_data[i] = df[df['hour'] == i]['Degree'].astype(float)
    if not hour_data[i].empty:
        df_res = data_analysis.get_statistical_data('hour'+ str(i), hour_data[i], df_res)

df_res = df_res.dropna()

# Connection
conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='root123', db='bods_bus_visualization_users')

try:
    with conn.cursor() as cursor:
        # Clear the table
        cursor.execute("TRUNCATE TABLE bods_bus_analysis")
        conn.commit()
finally:
    conn.close()

engine = create_engine("mysql+pymysql://root:root123@localhost:3306/bods_bus_visualization_users")
df_res.to_sql('bods_bus_analysis', con=engine, if_exists='append', index=False)
