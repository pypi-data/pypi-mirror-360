import psycopg2 as pg
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
from multiprocessing import Process, Queue, Array, current_process
from underthesea import text_normalize
import math
import psycopg2
import requests
import sqlalchemy
import unidecode
import os
import sh
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import datetime as dt
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
import re
import urllib.request as urllib
import warnings
warnings.filterwarnings('ignore')
os.environ['http_proxy'] = "http://proxy.hcm.fpt.vn:80"
os.environ['https_proxy'] = "http://proxy.hcm.fpt.vn:80"
import spark_sdk as ss
ss.__version__
import os
ss.PySpark(yarn=False, num_executors=60, driver_memory='60g', executor_memory='24g',
            add_on_config1=('spark.port.maxRetries', '1000'),
          add_on_config2=('spark.jars', '/mnt/projects-data/infra_report/jars/postgresql-42.2.20.jar'))
spark = ss.PySpark().spark
spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.functions import monotonically_increasing_id 
from pyspark.sql.types import StringType
from pyspark.sql import Window
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import StringType
from pyspark.sql.functions import *
from pyspark.sql.functions import countDistinct
import pyspark.sql.functions as f
from pyspark.sql.types import IntegerType
from requests.packages import urllib3
urllib3.disable_warnings()
import yaml
from .config import infra_analytics_config

def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config

def try_join(l):
    try:
        return ','.join(map(str, l))
    except TypeError:
        return np.nan
        
def connection_v1(user_name,pwd,host,db_name,port):
    """
    Make connection to database postgresql
    """
    try:
        string = ("""postgresql+psycopg2://""" + user_name + """:""" + pwd
        + """@""" + host + """:""" + port + """/""" + db_name)
        engine = sqlalchemy.create_engine(string, isolation_level='READ COMMITTED')
    except:
        print ("I am unable to connect to the database")
    return engine


def func(matchobj):
    return '' + matchobj.group(2)
def normalize_province(dau, df):
    if dau == 'Có dấu':
        df.rename({'Tỉnh':'Tỉnh có dấu'},axis=1,inplace=True)
        df.replace({'Tỉnh có dấu' : { r'(Thành phố[ ])': '', r'Tỉnh[ ]': ''}}, regex=True,inplace=True)
        df.replace({'Tỉnh có dấu' : {  r'Bà Rịa [-] Vũng Tàu': 'Bà Rịa Vũng Tàu'}}, regex=True,inplace=True)
        df['Tỉnh có dấu'] = df['Tỉnh có dấu'].str.title()
        df['Tỉnh không dấu'] = df['Tỉnh có dấu'].apply(lambda x: unidecode.unidecode(str(x)))
    else:
        df.rename({'Tỉnh':'Tỉnh không dấu'},axis=1,inplace=True)
        df.replace({'Tỉnh không dấu' : { r'(Thanh pho[ ])': '', r'Tinh[ ]': ''}}, regex=True,inplace=True)
        df.replace({'Tỉnh không dấu' : {  r'Ba Ria [-] Vung Tau': 'Ba Ria Vung Tau'}}, regex=True,inplace=True)
        df['Tỉnh không dấu'] = df['Tỉnh không dấu'].str.title()
def normalize_district(dau, df):
    if dau == 'Có dấu':
        df.rename({'Quận':'Quận có dấu'},axis=1,inplace=True)
        df.replace({'Quận có dấu' : { r'(H[.])': 'Huyện ', r'Q[.]': 'Quận ','Tp[.]|TP[.]|TP[ ]|Tp[ ]|Thanh Pho[ ]|Thành Phố[ ]': \
                                                       'Thành phố ', 'TX[.]|Thi Xa[ ]|Thị Xã[ ]|T[.]Xa[ ]|T[.]Xã[ ]|TX[ ]':'Thị xã '}}, regex=True,inplace=True)
        # df.replace({'Quận' : { r'(Quan[ ])': '', r'Huyen[ ]': '', r'huyen[ ]': '','Thi xa[ ]': '','Thanh pho[ ]': '','Xa[ ]': ''}}, regex=True,inplace=True)
        df['Quận có dấu'] = df['Quận có dấu'].str.lower()
        df['Quận có dấu']= df['Quận có dấu'].apply(lambda x: str(x).strip())
        df['Quận có dấu']= df['Quận có dấu'].apply(lambda x: re.sub('(Q |quận +)(\d)', func, x) )
        df['Quận có dấu'] = df['Quận có dấu'].apply(lambda x: 'Quận '+ str(int(x)) if all(char.isdigit() for char in x)==True else x)
        df['Quận có dấu'] = df['Quận có dấu'].str.strip('-|,|[ ]|.')
        df['Quận có dấu'] = df['Quận có dấu'].str.title()
        df['Quận có dấu'] = df['Quận có dấu'].apply(lambda x: text_normalize(str(x)))
        df['Quận không dấu'] = df['Quận có dấu'].apply(lambda x: unidecode.unidecode(str(x)))
        df.replace({'Quận không dấu' : { r'Quan[ ]': '', r'Huyen[ ]': '','Thi Xa[ ]': '','Thanh Pho[ ]': '','Xa[ ]': ''}}, regex=True,inplace=True)
        df['Quận không dấu'] = df['Quận không dấu'].apply(lambda x: 'Quan '+ str(int(x)) if (all(char.isdigit() for char in x)==True)&(x!='') else x)
        df['Quận có dấu']=df['Quận có dấu'].str.title()
        df['Quận không dấu']=df['Quận không dấu'].str.title()
        
    else:
        df.rename({'Quận':'Quận không dấu'},axis=1,inplace=True)
        df['Quận không dấu'] = df['Quận không dấu'].apply(lambda x: unidecode.unidecode(str(x)))
        df.replace({'Quận không dấu' : { r'(H[.])': 'Huyen ', r'Q[.]': 'Quan ','Tp[.]|TP[.]|TP[ ]|Tp[ ]|Thanh Pho[ ]': \
                                                       'Thanh pho ', 'TX[.]|Thi Xa[ ]|T[.]Xa[ ]|TX[ ]':'Thi xa '}}, regex=True,inplace=True)
        df.replace({'Quận không dấu' : { r'Quan[ ]': '', r'Huyen[ ]': '', r'huyen[ ]': '','Thi xa[ ]': '','Thanh pho[ ]': '','Xa[ ]': ''}}, regex=True,inplace=True)
        df['Quận không dấu'] = df['Quận không dấu'].str.lower()
        df['Quận không dấu']= df['Quận không dấu'].apply(lambda x: x.strip())
        df['Quận không dấu']= df['Quận không dấu'].apply(lambda x: re.sub('(Q |quận +)(\d)', func, x) )
        df['Quận không dấu'] = df['Quận không dấu'].apply(lambda x: 'Quan '+ str(int(x)) if (all(char.isdigit() for char in x)==True)&(x!='') else x)
        df['Quận không dấu'] = df['Quận không dấu'].apply(lambda x: text_normalize(str(x)))
        df['Quận không dấu'] = df['Quận không dấu'].str.strip('-|,|[ ]|.')
        df['Quận không dấu'] = df['Quận không dấu'].str.title()   
def normalize_ward(dau, df):
    if dau == 'Có dấu':
        df.rename({'Phường':'Phường có dấu'},axis=1,inplace=True)
        
        df.replace({'Phường có dấu' : { r'T[.]T[.]|T[.]T[ ]|TT[.]|T[.]Tran[ ]|T[.]Trấn[ ]|Thị Trấn[ ]|Thi Tran[ ]|TT[ ]|Thi tran[ ]|Thị trấn[ ]': 'Thị trấn '\
                     , r'TX[.]|TX[ ]|T[.]xa[ ]|T[.]xã[ ]|T[.]Xa[ ]|T[.]Xã[ ]|Thi Xa[ ]|Thị Xã[ ]': 'Thị xã ','P[.]': 'Phường '\
                     , 'Xã[.]|Xa[.]|Xa[ ]|Xã[ ]|xa[ ]|xã[ ]|Xã[ ]|Xa\xa0':'Xã ','Khu Pho[ ]|Khu Phố[ ]':'Khu phố ','KCN[ ]':'Khu chế xuất '}}, regex=True,inplace=True)
        
        df['Phường có dấu'] = df['Phường có dấu'].str.lower()
        df['Phường có dấu']= df['Phường có dấu'].apply(lambda x: str(x).strip())
        df['Phường có dấu'] = df['Phường có dấu'].str.strip('-|,|[ ]|.')
        df['Phường có dấu'] = df['Phường có dấu'].apply(lambda x: re.sub('(P |phường +)(\d)', func, x))
        df['Phường có dấu'] = df['Phường có dấu'].apply(lambda x: 'Phường '+ str(int(x)) if all(char.isdigit() for char in str(x))==True else x)
        df['Phường có dấu'] = df['Phường có dấu'].str.strip('-|,|[ ]|.')
        df['Phường có dấu'] = df['Phường có dấu'].str.title()
        df['Phường có dấu'] = df['Phường có dấu'].apply(lambda x: text_normalize(str(x)))
        df['Phường không dấu'] = df['Phường có dấu'].apply(lambda x: unidecode.unidecode(str(x)))
        df.replace({'Phường không dấu' : { r'(Thi Tran[ ])': '', r'Phuong[ ]': '',r'Thi Xa[ ]': '','Xa[ ]': '','Ap[ ]': '', r'Huyen[ ]': ''}}, regex=True,inplace=True)
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: 'Phuong '+ str(int(x)) if (all(char.isdigit() for char in x)==True)&(x!='') else x)
        df['Phường có dấu']=df['Phường có dấu'].str.title()
        df['Phường không dấu']=df['Phường không dấu'].str.title()
    else:
        df.rename({'Phường':'Phường không dấu'},axis=1,inplace=True)
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: unidecode.unidecode(str(x)))
        df.replace({'Phường không dấu' : { r'T[.]T[.]|T[.]T[ ]|TT[.]|T[.]Tran[ ]|Thi Tran[ ]|TT[ ]|Thi tran[ ]': 'Thi tran '\
                                                         , r'TX[.]|TX[ ]|T[.]xa[ ]|T[.]Xa[ ]|Thi Xa[ ]': 'Thi xa ','P[.]': 'Phuong '\
                                                         , 'Xa[.]|Xa[ ]|xa[ ]|Xã[ ]|Xa\xa0':'Xa ','Khu Pho[ ]':'Khu pho ','KCN[ ]':'Khu che xuat '}}, regex=True,inplace=True)
        df.replace({'Phường không dấu' : { r'Thi tran[ ]|Thi Tran[ ]': '', r'Phuong[ ]': '',r'Thi Xa[ ]': '','Xa[ ]': '','Ap[ ]': '', r'Huyen[ ]': ''}}, regex=True,inplace=True)
        df['Phường không dấu'] = df['Phường không dấu'].str.lower()
        df['Phường không dấu']= df['Phường không dấu'].apply(lambda x: x.strip())
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: re.sub('(P |phuong +)(\d)', func, x))
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: 'Phuong '+ str(int(x)) if (all(char.isdigit() for char in x)==True)&(x!='') else x)
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: text_normalize(str(x)))
        df['Phường không dấu'] = df['Phường không dấu'].str.strip('-|,|[ ]|.')
        df['Phường không dấu'] = df['Phường không dấu'].str.title()
def normalize_address(dau, df):
    """
        Chuẩn hoá Tỉnh, Quận/Huyện, Phường/Xã":
            + Loại bỏ ký tự đặc biệt, khoảng trắng, dấu câu 
            + Đồng bộ các thông tin và định danh địa chỉ 
    """
    if 'Tỉnh' in df.columns:
        normalize_province(dau, df)
    if 'Quận' in df.columns:
        normalize_district(dau, df)
    if 'Phường' in df.columns:
        normalize_ward(dau, df)

def process_diachidoi(config: dict = infra_analytics_config):
    """
    Chuẩn hoá thông tin địa chỉ thay đổi sáp nhập:
        + Load thông tin địa chỉ thay đổi: /mnt/projects-data/phat_trien_ha_tang/file_static/dia_chi_mapping_sai.xlsx
        + Loại bỏ ký tự đặc biệt, khoảng trắng, dấu câu
    """
    df_diachidoi= pd.read_excel(config['feature_ptht']['diachisai_path'],engine='openpyxl')
    df_diachidoi.columns=['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu',
           'Phường thay đổi', 'Quận thay đổi', 'Tỉnh thay đổi']
    df_diachidoi.replace({'Tỉnh thay đổi':{r'_x0008_|_x001D_':' '}}, regex=True,inplace=True)
    df_diachidoi.replace({'Quận thay đổi':{r'_x0008_|_x001D_':' '}}, regex=True,inplace=True)
    df_diachidoi.replace({'Phường thay đổi':{r'_x0008_|_x001D_':' '}}, regex=True,inplace=True)
    df_diachidoi.replace({'Tỉnh không dấu':{r'_x0008_|_x001D_':' '}}, regex=True,inplace=True)
    df_diachidoi.replace({'Quận không dấu':{r'_x0008_|_x001D_':' '}}, regex=True,inplace=True)
    df_diachidoi.replace({'Phường không dấu':{r'_x0008_|_x001D_':' '}}, regex=True,inplace=True)
    df_diachidoi['Phường không dấu']= df_diachidoi['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_diachidoi['Phường không dấu'] = df_diachidoi['Phường không dấu'].str.title() 
    
    df_diachidoi['Quận không dấu']= df_diachidoi['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_diachidoi['Quận không dấu'] = df_diachidoi['Quận không dấu'].str.title() 
    
    df_diachidoi['Tỉnh không dấu']= df_diachidoi['Tỉnh không dấu'].str.strip('-|,|[ ]|.')
    df_diachidoi['Tỉnh không dấu'] = df_diachidoi['Tỉnh không dấu'].str.title()
    df_diachidoi['Tỉnh không dấu']= df_diachidoi['Tỉnh không dấu'].str.strip('-|,|[ ]|.')
    df_diachidoi['Tỉnh không dấu'] = df_diachidoi['Tỉnh không dấu'].str.title()
    df_diachidoi['Phường thay đổi']= df_diachidoi['Phường thay đổi'].str.strip('-|,|[ ]|.')
    df_diachidoi['Phường thay đổi'] = df_diachidoi['Phường thay đổi'].str.title() 
    
    df_diachidoi['Quận thay đổi']= df_diachidoi['Quận thay đổi'].str.strip('-|,|[ ]|.')
    df_diachidoi['Quận thay đổi'] = df_diachidoi['Quận thay đổi'].str.title() 
    df_diachidoi.drop_duplicates(keep='first',inplace=True)
    return df_diachidoi
def add_zero_to_beginning(value):
    if value[0] != '0':
        value = '0' + value
    return value

def connection_v2(user_name,pwd,host,db_name,port):
    """
    Make connection to database postgresql
    """
    try:
        engine = pg.connect(dbname=db_name, user=user_name, host=host, port=port, password=pwd)
    except:
        print ("I am unable to connect to the database")
    return engine

def process_location(config: dict = infra_analytics_config):   
    """
        Lấy thông tin tỉnh thành:
           + Load dữ liệu tỉnh thành từ postgresql 177 - dwh_noc - public.dwh_province 
           + Chuẩn hoá địa chỉ đồng bộ phục vụ mapping tỉnh thành 
           + Lọc để loại bỏ các tỉnh thành nhiễu (không phải tỉnh ở Việt Nam) 
    """
    conn_wr = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    query = """SELECT * FROM public."""+ config['feature_ptht']['tablename_province']
    df_branch = pd.read_sql(query, conn_wr)
    df_branch['region'].replace('Vung','Vùng', regex=True, inplace=True)
    df_branch['name'].replace('Ba Ria$','Ba Ria Vung Tau', regex=True, inplace=True)
    df_branch['name'].replace('Hue','Thua Thien Hue', regex=True, inplace=True)
    df_branch['region'] = np.where(df_branch['name'].isin(['Dien Bien', 'Son La', 'Hoa Binh']),
                                       'Vùng 3',df_branch['region'])
    df_branch['region'] = np.where(df_branch['name'].isin(['Hung Yen']),
                                       'Vùng 2',df_branch['region'])
    df_branch = df_branch[~((df_branch.name=='Hoa Binh')&(df_branch.region==''))]
    df_branch_filter = df_branch[['name','region']].drop_duplicates(keep='first')
    df_branch_region = df_branch[['name','province','region']].drop_duplicates(keep='first')
    df_branch_region = df_branch_region[~df_branch_region.province.isin([
        'SGP','HKG','JPN','GER','USA','VTU','BRA','LGI','BLC','DAH','STY','PAY','SOC'])]
    df_branch_province = df_branch[['name','province']].drop_duplicates(keep='first')
    df_branch_province = df_branch_province[~df_branch_province.province.isin([
        'SGP','HKG','JPN','GER','USA','VTU','BRA','LGI','BLC','DAH','STY','PAY','SOC'])]
    return df_branch,df_branch_province, df_branch_region
# date='2019-09-01'
def process_ibb(date,kydautu,config):    
    """
        Lấy thông tin nhân viên sale:
            + Load dữ liệu nhân viên sale trên hive ở mức chi nhánh: ftel_dwh_isc.ds_sale_staff, ftel_dwh_isc.dim_branch_location
            + Chuẩn hoá địa chỉ đồng bộ phục vụ mapping địa chỉ với các đầu dữ liệu khác 
    """
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    # spark.sql("refresh table {}.{}".format(config['feature_ptht']['db_isc'],config['feature_ptht']['table_sale_staff']))
    str_sql ="""SELECT b.region,b.location,b.branch_name,count(s.sale_id) as IBB
    FROM {}.{} s LEFT JOIN {}.{} b
    ON s.location_id=b.location_id and s.branch_code=b.branch_code
    WHERE s.ibb_member_create_date<'{}' and s.quit_date>='{}'
    GROUP BY  b.region,b.location,b.branch_name
    """.format(config['feature_ptht']['db_isc'],config['feature_ptht']['table_sale_staff'],
               config['feature_ptht']['db_isc'],config['feature_ptht']['table_location'],date,date)
    df_sale_staff =  spark.sql(str_sql)
    df_sale_staff_pd = df_sale_staff.toPandas()
    df_sale_staff_pd.replace({'branch_name':{'_KDPP|_ADM|FSH_|_KDPP|_Dai ly|_TTKDOTT|_TTKDOTT|_KDDA|_TLS|_HO|FTI_|_FPL|_Telesale|_IVoice|_BDA':''
                                            }},regex=True, inplace=True)
    df_sale_staff_pd.replace({'location':{'Vung Tau':'Ba Ria Vung Tau',
                                          'HUE':'Thua Thien Hue'}},regex=True, inplace=True)
    df_sale_staff_pd.replace({'region':{'Vung':'Vùng',
                                          }},regex=True, inplace=True)
    df_sale_staff_pd = df_sale_staff_pd.groupby(['region', 'location', 'branch_name'],
                                                as_index=False).agg({'IBB':'sum'})
    df_sale_staff_pd['Kỳ đầu tư'] = kydautu
    return df_sale_staff_pd
def process_population(date, df_diachidoi,config): 
    """
    Lấy thông tin dân số và diện tích:
       + Load và groupby tính dân số mức xã/phường: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/dan_so.parquet
       + Load và groupby tính các thành phần dân số mức xã/phường: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/thanh_phan_dan_so.parquet
       + Load và groupby tính số hộ dân mức xã/phường: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/ho_dan.parquet
       + Xử lý dữ liệu missing và địa chỉ thay đổi nếu không mapping được các thông tin
       + Load dữ liệu diện tích từ postgresql 177 - dwh_noc - public.tbl_vnwards_info 
       + Chuẩn hoá địa chỉ diện tích và mapping với dữ liệu dân số 
       + Xử lý dữ liệu missing và địa chỉ thay đổi nếu không mapping được các thông tin
       + Tính mật độ dân số: tổng hộ dân / diện tích 
    """
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)

    df_danso_full = spark.read.parquet(config['data_import']['danso_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_danso_full)
    df_danso_full.replace({'Phường có dấu':{'Xã A Roằng':'Xã A Roàng'}},regex=True, inplace=True)
    df_danso_full.drop({'Mã tỉnh','Mã quận','Mã phường'},axis=1,inplace=True)
    df_danso_full = df_danso_full.groupby(['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu',
                           'Quận không dấu','Phường không dấu','Tỉnh không dấu']
                         ).agg({'Tổng số dân':'sum','Dân số Nông thôn':'sum','Dân số Thành thị':'sum'}).reset_index()
    df_danso_full.columns = ['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu', 'Quận không dấu',
           'Phường không dấu', 'Tỉnh không dấu', 'Tổng dân', 'Nông thôn',
           'Thành thị']
    #  thành phần dân cư 
    df_tp_danso = spark.read.parquet(config['data_import']['thanhphandanso_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_tp_danso)
    df_tp_danso.replace({'Phường có dấu':{'Xã A Roằng':'Xã A Roàng'}},regex=True, inplace=True)
    df_tp_danso.drop({'Mã tỉnh','Mã quận','Mã phường'},axis=1,inplace=True)
    df_tp_danso_full = df_tp_danso.groupby(['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu',
                           'Quận không dấu','Phường không dấu','Tỉnh không dấu']
                         ).agg({'Dưới tiểu học':'sum','Tiểu học':'sum','Trung học':'sum',
                                'Cao đẳng':'sum','Đại học':'sum','Thạc sỹ':'sum','Tiến sỹ':'sum'}).reset_index()
    #  hộ dân
    df_hodan_full = spark.read.parquet(config['data_import']['hodan_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_hodan_full)
    df_hodan_full.replace({'Phường có dấu':{'Xã A Roằng':'Xã A Roàng'}},regex=True, inplace=True)
    df_hodan_full.drop({'Mã tỉnh','Mã quận','Mã phường'},axis=1,inplace=True)
    
    df_hodan_full_2 = df_hodan_full.groupby(['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu',
                           'Quận không dấu','Phường không dấu','Tỉnh không dấu']
                         ).agg({'Tổng hộ':'sum'}).reset_index()
    df_hodan_full_2.rename({'Tổng hộ': 'Tổng số hộ'}, axis=1,inplace=True)
    df_tp_danso_full = df_tp_danso_full.merge(df_hodan_full_2, on=['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu',
                           'Quận không dấu','Phường không dấu','Tỉnh không dấu'], how='left')
    df_danso_final =  df_danso_full.merge(df_tp_danso_full, on=['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu',
                           'Quận không dấu','Phường không dấu','Tỉnh không dấu'], how='left')
    df_tpdanso_kd = df_tp_danso_full[[ 'Quận không dấu',
           'Phường không dấu', 'Tỉnh không dấu', 'Tổng số hộ', 'Dưới tiểu học',
           'Tiểu học', 'Trung học', 'Cao đẳng', 'Đại học', 'Thạc sỹ', 'Tiến sỹ']]
    df_tpdanso_kd = df_tpdanso_kd.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu']
                         ).agg({'Tổng số hộ':'sum','Dưới tiểu học':'sum','Tiểu học':'sum','Trung học':'sum',
                                'Cao đẳng':'sum','Đại học':'sum','Thạc sỹ':'sum','Tiến sỹ':'sum'}).reset_index()
    df_tpdanso_kd.columns= ['Phường không dấu',
           'Quận không dấu', 'Tỉnh không dấu', 'Tổng số hộ thay đổi',
           'Dưới tiểu học thay đổi', 'Tiểu học thay đổi', 'Trung học thay đổi', 'Cao đẳng thay đổi',
           'Đại học thay đổi','Thạc sỹ thay đổi', 'Tiến sỹ thay đổi']
    df_danso_final =  df_danso_final.merge(df_tpdanso_kd, on=['Quận không dấu','Phường không dấu',
                                                              'Tỉnh không dấu'], how='left')
    df_danso_final['Tổng số hộ'] = np.where(df_danso_final['Tổng số hộ'].isna(),
                                           df_danso_final['Tổng số hộ thay đổi'],df_danso_final['Tổng số hộ'])
    df_danso_final['Dưới tiểu học'] = np.where(df_danso_final['Dưới tiểu học'].isna(),
                                           df_danso_final['Dưới tiểu học thay đổi'],df_danso_final['Dưới tiểu học'])
    df_danso_final['Tiểu học'] = np.where(df_danso_final['Tiểu học'].isna(),
                                           df_danso_final['Tiểu học thay đổi'],df_danso_final['Tiểu học'])
    df_danso_final['Trung học'] = np.where(df_danso_final['Trung học'].isna(),
                                           df_danso_final['Trung học thay đổi'],df_danso_final['Trung học'])
    df_danso_final['Cao đẳng'] = np.where(df_danso_final['Cao đẳng'].isna(),
                                           df_danso_final['Cao đẳng thay đổi'],df_danso_final['Cao đẳng'])
    df_danso_final['Đại học'] = np.where(df_danso_final['Đại học'].isna(),
                                           df_danso_final['Đại học thay đổi'],df_danso_final['Đại học'])
    df_danso_final['Thạc sỹ'] = np.where(df_danso_final['Thạc sỹ'].isna(),
                                           df_danso_final['Thạc sỹ thay đổi'],df_danso_final['Thạc sỹ'])
    df_danso_final['Tiến sỹ'] = np.where(df_danso_final['Tiến sỹ'].isna(),
                                           df_danso_final['Tiến sỹ thay đổi'],df_danso_final['Tiến sỹ'])
    df_danso_final.drop(['Tổng số hộ thay đổi',
           'Dưới tiểu học thay đổi', 'Tiểu học thay đổi', 'Trung học thay đổi', 'Cao đẳng thay đổi',
           'Đại học thay đổi','Thạc sỹ thay đổi', 'Tiến sỹ thay đổi'],axis=1,inplace=True)
    df_tp_danso_full_ = df_tp_danso_full.merge(df_diachidoi, on=['Quận không dấu','Phường không dấu',
                                     'Tỉnh không dấu'], how='left')
    df_tp_danso_full_ = df_tp_danso_full_[~df_tp_danso_full_['Phường thay đổi'].isna()]
    df_tp_danso_full_.drop(['Quận không dấu','Phường không dấu',
                                     'Tỉnh không dấu'],axis=1,inplace=True)
    df_tp_danso_full_.rename({'Phường thay đổi':'Phường không dấu','Tỉnh thay đổi':'Tỉnh không dấu'
                              ,'Quận thay đổi':'Quận không dấu'},axis=1,inplace=True)
    df_tp_danso_kd = df_tp_danso_full_.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu']
                         ).agg({'Tổng số hộ':'sum','Dưới tiểu học':'sum','Tiểu học':'sum','Trung học':'sum',
                                'Cao đẳng':'sum','Đại học':'sum','Thạc sỹ':'sum','Tiến sỹ':'sum'}).reset_index()
    df_tp_danso_kd.columns = ['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'Tổng số hộ thay đổi',
           'Dưới tiểu học thay đổi', 'Tiểu học thay đổi', 'Trung học thay đổi', 'Cao đẳng thay đổi',
           'Đại học thay đổi','Thạc sỹ thay đổi', 'Tiến sỹ thay đổi']
    df_danso_final = df_danso_final.merge(df_tp_danso_kd, on=['Phường không dấu', 'Quận không dấu', 
                                      'Tỉnh không dấu'], how='left')
    df_danso_final['Tổng số hộ'] = np.where(df_danso_final['Tổng số hộ'].isna(),
                                           df_danso_final['Tổng số hộ thay đổi'],df_danso_final['Tổng số hộ'])
    df_danso_final['Dưới tiểu học'] = np.where(df_danso_final['Dưới tiểu học'].isna(),
                                           df_danso_final['Dưới tiểu học thay đổi'],df_danso_final['Dưới tiểu học'])
    df_danso_final['Tiểu học'] = np.where(df_danso_final['Tiểu học'].isna(),
                                           df_danso_final['Tiểu học thay đổi'],df_danso_final['Tiểu học'])
    df_danso_final['Trung học'] = np.where(df_danso_final['Trung học'].isna(),
                                           df_danso_final['Trung học thay đổi'],df_danso_final['Trung học'])
    df_danso_final['Cao đẳng'] = np.where(df_danso_final['Cao đẳng'].isna(),
                                           df_danso_final['Cao đẳng thay đổi'],df_danso_final['Cao đẳng'])
    df_danso_final['Đại học'] = np.where(df_danso_final['Đại học'].isna(),
                                           df_danso_final['Đại học thay đổi'],df_danso_final['Đại học'])
    df_danso_final['Thạc sỹ'] = np.where(df_danso_final['Thạc sỹ'].isna(),
                                           df_danso_final['Thạc sỹ thay đổi'],df_danso_final['Thạc sỹ'])
    df_danso_final['Tiến sỹ'] = np.where(df_danso_final['Tiến sỹ'].isna(),
                                           df_danso_final['Tiến sỹ thay đổi'],df_danso_final['Tiến sỹ'])
    df_danso_final.drop(['Tổng số hộ thay đổi',
           'Dưới tiểu học thay đổi', 'Tiểu học thay đổi', 'Trung học thay đổi', 'Cao đẳng thay đổi',
           'Đại học thay đổi','Thạc sỹ thay đổi', 'Tiến sỹ thay đổi'],axis=1,inplace=True)
    # sql_dtich = """(select * from %s) a"""%(config['feature_ptht']['table_arae'])
    # df_dtich = spark.read.format("jdbc").options(
    #      url='jdbc:postgresql://%s:%s/%s'%(config['dbs']['dwh_177_public']['host'],
    #                                        config['dbs']['dwh_177_public']['port'],
    #                                       config['dbs']['dwh_177_public']['dbname']), 
    #      dbtable=sql_dtich,
    #      user = config['dbs']['dwh_177_public']['user'],
    #      password = config['dbs']['dwh_177_public']['password'],
    #     ).option("driver", "org.postgresql.Driver").load()
    # df_dtich = df_dtich.toPandas()
    sql_dtich = """(select * from public.tbl_vnwards_info)"""
    conn_wr = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    df_dtich = pd.read_sql(sql_dtich, conn_wr)
    df_dtich.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_dtich.columns = ['code', 'Phường', 'level', 'Quận', 'Tỉnh', 'population', 'area',
           'density', 'wiki_url']
    normalize_address('Có dấu',df_dtich)
    df_dtich_select = df_dtich[['Phường có dấu',  'Quận có dấu', 'Tỉnh có dấu',
           'population', 'area', 'density','Tỉnh không dấu',
           'Quận không dấu', 'Phường không dấu']]
    df_mapping = df_danso_final.merge(df_dtich_select, on=['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu',
           'Quận không dấu','Phường không dấu', 'Tỉnh không dấu'], how='left')
    df_dientich_kd = df_dtich_select[[ 'Quận không dấu',
           'Phường không dấu', 'Tỉnh không dấu', 'population', 'area']]
    df_dientich_kd = df_dientich_kd.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu']
                         ).agg({'population':'sum','area':'sum'}).reset_index()
    df_dientich_kd.columns= ['Phường không dấu',
           'Quận không dấu', 'Tỉnh không dấu', 'population thay đổi',
           'area thay đổi']
    df_mapping =  df_mapping.merge(df_dientich_kd, on=['Quận không dấu','Phường không dấu',
                                                              'Tỉnh không dấu'], how='left')
    df_mapping['population'] = np.where(df_mapping['population'].isna(),
                                           df_mapping['population thay đổi'],df_mapping['population'])
    df_mapping['area'] = np.where(df_mapping['area'].isna(),
                                           df_mapping['area thay đổi'],df_mapping['area'])
    df_mapping.drop(['population thay đổi',
           'area thay đổi'],axis=1,inplace=True)
    df_dtich_select_  =  df_dtich_select[['Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
                                          'population', 'area']]
    df_dtich_select_gp = df_dtich_select_.groupby(['Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu']
                  ,as_index=False).agg({'population':'sum','area':'sum'})
    df_dtich_select_gp = df_dtich_select_gp.merge(df_diachidoi, on=['Quận không dấu','Phường không dấu',
                                     'Tỉnh không dấu'], how='left')
    df_dtich_select_gp = df_dtich_select_gp[~df_dtich_select_gp['Phường thay đổi'].isna()]
    df_dtich_select_gp.drop(['Quận không dấu','Phường không dấu',
                                     'Tỉnh không dấu'],axis=1,inplace=True)
    df_dtich_select_gp.rename({'Phường thay đổi':'Phường không dấu','Tỉnh thay đổi':'Tỉnh không dấu'
                              ,'Quận thay đổi':'Quận không dấu'},axis=1,inplace=True)
    df_dtich_select_gp = df_dtich_select_gp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu']
                         ).agg({'population':'sum','area':'sum'}).reset_index()
    df_dtich_select_gp.columns = ['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 
                                  'population thay đổi', 'area thay đổi']
    df_mapping_ = df_mapping.merge(df_dtich_select_gp, on=['Phường không dấu', 'Quận không dấu', 
                                      'Tỉnh không dấu'], how='left')
    df_mapping_['population'] = np.where(df_mapping_['population'].isna(),
                                           df_mapping_['population thay đổi'],df_mapping_['population'])
    df_mapping_['area'] = np.where(df_mapping_['area'].isna(),
                                           df_mapping_['area thay đổi'],df_mapping_['area'])
    
    df_mapping_.drop(['population thay đổi',
           'area thay đổi'],axis=1,inplace=True)
    df_mapping_['Tổng dân'] = np.where((df_mapping_['Tổng dân'].isna())|(df_mapping_['Tổng dân']<=0)
                                           , df_mapping_['population'], df_mapping_['Tổng dân'])
    df_mapping_ds = df_mapping_[['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu', 'Quận không dấu',
           'Phường không dấu', 'Tỉnh không dấu', 'area',
            'Tổng dân', 'Thành thị','Nông thôn','Tổng số hộ',
           'Dưới tiểu học', 'Tiểu học', 'Trung học', 'Cao đẳng', 'Đại học', 'Thạc sỹ', 'Tiến sỹ']]
    df_mapping_ds['area'] = np.where(df_mapping_ds['area']<0, df_mapping_ds['area']*(-1), df_mapping_ds['area'])
    df_mapping_ds['density'] =(df_mapping_ds['Tổng dân'].astype(float)/(df_mapping_ds['area'])).round(3)
    df_mapping_ds['mật độ hộ dân'] =(df_mapping_ds['Tổng số hộ']/(df_mapping_ds['area'])).round(3)
    return df_mapping_ds
def get_ngaybatdau(kydautu):
    if kydautu[0]=='1':
        ngaybatdau = str(kydautu[2:])+'-01-01'
    else:
        ngaybatdau = str(kydautu[2:])+'-07-01'
    return ngaybatdau
    
def get_nguongdanhgia(df_branch_province,config):
    """
    Tính ngưỡng đánh giá hiệu quả:
        + Load dữ liệu lịch sử đầu tư từ postgresql 177 - dwh_noc - public.tbl_planning_history
        +  Chuẩn hoá thông tin về địa chỉ: phục vụ mapping các đầu dữ liệu 
        + Xử lý dữ liệu missing về port ở các mốc thời gian 
        + Tính hiệu quả khai thác ở từng mốc thời gian 
        + Lấy dữ liệu về kỳ đầu tư mapping với lịch sử đầu tư 
        + Tính trung bình khai thác 6 tháng ở từng kỳ đầu tư 
    """
    
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    str_sql = "select * from  public.%s"%(config['feature_ptht']['table_planning'])
    df_add_ht = pd.read_sql(str_sql, conn)
    df_add_ht.drop(['created_at','updated_at'],axis=1,inplace=True)
    conn.close()
    df_add_ht.columns = ['Mã kế hoạch', 'Kỳ đầu tư', 'POP', 'Phường', 'Quận', 'Chi nhánh',
           'Vùng', 'DL triển khai', 'Perport', 'Tổng port sau 3T',
           'Port dùng sau 3T', '% khai thác sau 3T', 'Tổng port sau 6T',
           'Port dùng sau 6T', '% khai thác sau 6T', 'Tổng port sau 9T',
           'Port dùng sau 9T', '% khai thác sau 9T', 'Tổng port sau 12T',
           'Port dùng sau 12T', '% khai thác sau 12T','ngay_bat_dau']
    df_add_ht['Chi nhánh'] = df_add_ht['Chi nhánh'].str.strip('-|,|[ ]|.')
    df_add_ht[['Mã kế hoạch','Phường','Quận','Chi nhánh','POP']] = df_add_ht[['Mã kế hoạch','Phường',
                   'Quận','Chi nhánh','POP']].fillna(value='')
    df_add_ht['province'] = df_add_ht['Chi nhánh'].str[:3]
    df_add_ht['province'] = df_add_ht['province'].apply(lambda x:
                                    re.sub('\d', 'I', x))
    df_add_ht.replace({'province':{'HNII':'HNI','HBN':'HBH','BRA':'BRU',
                                  'SGN':'HCM'}},regex=True,inplace=True)
    df_add_ht['Mã kế hoạch'] = df_add_ht['Mã kế hoạch'].str.upper()
    df_province_ = df_branch_province.rename({'name':'Tỉnh'},axis=1)
    df_add_ht = df_add_ht.merge(df_province_, on='province', how='left')
    df_add_ht['Mã kế hoạch'] = np.where(df_add_ht['Mã kế hoạch']=='', '2H2023',
                                        df_add_ht['Mã kế hoạch'])
    df_add_ht['Tổng port sau 3T'] = pd.to_numeric(df_add_ht['Tổng port sau 3T'], errors='coerce')
    df_add_ht['Port dùng sau 3T'] = pd.to_numeric(df_add_ht['Port dùng sau 3T'], errors='coerce')
    df_add_ht['Tổng port sau 6T'] = pd.to_numeric(df_add_ht['Tổng port sau 6T'], errors='coerce')
    df_add_ht['Port dùng sau 6T'] = pd.to_numeric(df_add_ht['Port dùng sau 6T'], errors='coerce')
    df_add_ht['Tổng port sau 9T'] = pd.to_numeric(df_add_ht['Tổng port sau 9T'], errors='coerce')
    df_add_ht['Port dùng sau 9T'] = pd.to_numeric(df_add_ht['Port dùng sau 9T'], errors='coerce')
    df_add_ht['Tổng port sau 12T'] = pd.to_numeric(df_add_ht['Tổng port sau 12T'], errors='coerce')
    df_add_ht['Port dùng sau 12T'] = pd.to_numeric(df_add_ht['Port dùng sau 12T'], errors='coerce')
    df_add_ht['Tổng port sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']!=df_add_ht['Tổng port sau 6T'],
                                              df_add_ht['Tổng port sau 6T'],df_add_ht['Tổng port sau 3T'])
    df_add_ht['Tổng port sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']<df_add_ht['Port dùng sau 3T'],
                                              df_add_ht['DL triển khai'],df_add_ht['Tổng port sau 3T'])
    df_add_ht['Tổng port sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']<df_add_ht['Port dùng sau 3T'],
                                              df_add_ht['Port dùng sau 3T'],df_add_ht['Tổng port sau 3T'])
    df_add_ht['Tổng port sau 6T'] = np.where(df_add_ht['Tổng port sau 6T']<df_add_ht['Port dùng sau 6T'],
                                              df_add_ht['Tổng port sau 3T'],df_add_ht['Tổng port sau 6T'])
    df_add_ht['Tổng port sau 9T'] = np.where(df_add_ht['Tổng port sau 9T']<df_add_ht['Port dùng sau 9T'],
                                              df_add_ht['Tổng port sau 6T'],df_add_ht['Tổng port sau 9T'])
    df_add_ht['Tổng port sau 12T'] = np.where(df_add_ht['Tổng port sau 12T']<df_add_ht['Port dùng sau 12T'],
                                              df_add_ht['Tổng port sau 9T'],df_add_ht['Tổng port sau 12T'])
    
    normalize_address('Không dấu', df_add_ht)
    df_add_ht = df_add_ht.groupby(['Mã kế hoạch','Kỳ đầu tư','POP','Phường không dấu','Quận không dấu','Tỉnh không dấu',
        'Chi nhánh','Vùng'],as_index=False).agg({'DL triển khai':'sum','Perport':'mean','Tổng port sau 3T':'sum',
        'Port dùng sau 3T':'sum','Tổng port sau 6T':'sum','Port dùng sau 6T':'sum'
        ,'Tổng port sau 9T':'sum','Port dùng sau 9T':'sum'
         ,'Tổng port sau 12T':'sum','Port dùng sau 12T':'sum'})
    df_add_ht['% khai thác sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']<=0,0,
                                     df_add_ht['Port dùng sau 3T']/df_add_ht['Tổng port sau 3T'])
    df_add_ht['% khai thác sau 6T'] = np.where(df_add_ht['Tổng port sau 6T']<=0,0,
                                     df_add_ht['Port dùng sau 6T']/df_add_ht['Tổng port sau 6T'])
    df_add_ht['% khai thác sau 9T'] = np.where(df_add_ht['Tổng port sau 9T']<=0,0,
                                     df_add_ht['Port dùng sau 9T']/df_add_ht['Tổng port sau 9T'])
    df_add_ht['% khai thác sau 12T'] = np.where(df_add_ht['Tổng port sau 12T']<=0,0,
                                     df_add_ht['Port dùng sau 12T']/df_add_ht['Tổng port sau 12T'])
    df_add_ht = df_add_ht[['Mã kế hoạch', 'Kỳ đầu tư', 'POP', 'Phường không dấu', 'Quận không dấu',
           'Chi nhánh', 'Vùng', 'DL triển khai', 'Perport', 'Tổng port sau 3T',
           'Port dùng sau 3T', '% khai thác sau 3T', 'Tổng port sau 6T',
           'Port dùng sau 6T', '% khai thác sau 6T', 'Tổng port sau 9T',
           'Port dùng sau 9T', '% khai thác sau 9T', 'Tổng port sau 12T',
           'Port dùng sau 12T', '% khai thác sau 12T']]
    df_add_ht.columns =['Mã kế hoạch', 'Kỳ đầu tư', 'POP', 'Phường', 'Quận',
           'Chi nhánh', 'Vùng', 'DL triển khai', 'Perport', 'Tổng port sau 3T',
           'Port dùng sau 3T', '% khai thác sau 3T', 'Tổng port sau 6T',
           'Port dùng sau 6T', '% khai thác sau 6T', 'Tổng port sau 9T',
           'Port dùng sau 9T', '% khai thác sau 9T', 'Tổng port sau 12T',
           'Port dùng sau 12T', '% khai thác sau 12T']
    df_add_ht = df_add_ht.sort_values(['Mã kế hoạch','Kỳ đầu tư','POP','Phường','Quận','Chi nhánh','Vùng','DL triển khai',
                                      'Perport','Tổng port sau 3T','Tổng port sau 6T','Tổng port sau 9T','Tổng port sau 12T'],ascending=False)
    df_add_ht['% khai thác sau 6T'] = np.where(df_add_ht['% khai thác sau 6T']<df_add_ht['% khai thác sau 3T'],
                                              df_add_ht['% khai thác sau 3T'],df_add_ht['% khai thác sau 6T'])
    #  nomalize xã/ phường, quận
    df_add_ht['Quận'] = df_add_ht['Quận'].apply(lambda x: unidecode.unidecode(str(x)))
    df_add_ht['Phường'] = df_add_ht['Phường'].apply(lambda x: unidecode.unidecode(str(x)))
    df_add_ht.replace({'Quận' : { r'(H[.])': 'Huyen ', r'Q[.]': 'Quan ','Tp[.]|TP[.]|TP[ ]|Tp[ ]|Thanh Pho[ ]': \
                                                   'Thanh pho ', 'TX[.]|Thi Xa[ ]|T[.]Xa[ ]|TX[ ]':'Thi xa '}}, regex=True,inplace=True)
    df_add_ht.replace({'Phường' : { r'T[.]T[.]|T[.]T[ ]|TT[.]|T[.]Tran[ ]|Thi Tran[ ]|TT[ ]|Thi tran[ ]': 'Thi tran '\
                                                     , r'TX[.]|TX[ ]|T[.]xa[ ]|T[.]Xa[ ]|Thi Xa[ ]': 'Thi xa ','P[.]': 'Phuong '\
                                                     , 'Xa[.]|Xa[ ]|xa[ ]|Xã[ ]|Xa\xa0':'Xa ','Khu Pho[ ]':'Khu pho ','KCN[ ]':'Khu che xuat '}}, regex=True,inplace=True)
    
    df_add_ht.replace({'Phường' : { r'(Thi tran[ ])': '', r'Phuong[ ]': '',r'Thi Xa[ ]': '','Xa[ ]': '','Ap[ ]': '', r'Huyen[ ]': ''}}, regex=True,inplace=True)
    df_add_ht.replace({'Quận' : { r'(Quan[ ])': '', r'Huyen[ ]': '', r'huyen[ ]': '','Thi xa[ ]': '','Thanh pho[ ]': '','Xa[ ]': ''}}, 
                           regex=True,inplace=True)
    df_add_ht['Phường'] = df_add_ht['Phường'].str.lower()
    df_add_ht['Quận'] = df_add_ht['Quận'].str.lower()
    
    df_add_ht['Phường']= df_add_ht['Phường'].apply(lambda x: x.strip())
    df_add_ht['Quận']= df_add_ht['Quận'].apply(lambda x: x.strip())
    
    df_add_ht['Quận']= df_add_ht['Quận'].str.title()
    df_add_ht['Phường']= df_add_ht['Phường'].str.title()
    df_add_ht['Quận'] = df_add_ht['Quận'].apply(lambda x: 'Quan '+ str(int(x)) if (all(char.isdigit() for char in x)==True) and ( x not in ([''])) else x)
    # xử lý phường chứa số
    df_add_ht['Phường'] = df_add_ht['Phường'].apply(lambda x: 'Phuong '+ str(int(x)) if (all(char.isdigit() for char in x)==True) and ( x not in ([''])) else x)
    df_add_ht.replace({'Quận':{'Chau Thanh - Hau Giang':'Chau Thanh'}},regex=True, inplace=True)
    df_kydautu = pd.DataFrame({'Kỳ đầu tư':df_add_ht['Kỳ đầu tư'].unique()})
    df_kydautu['ngay_bat_dau'] = df_kydautu['Kỳ đầu tư'].apply(lambda x: get_ngaybatdau(x))
    df_kydautu['ngay_bat_dau'] = pd.to_datetime(df_kydautu['ngay_bat_dau'])
    df_kydautu = df_kydautu.sort_values('ngay_bat_dau')
    df_kydautu['index_kdt'] = df_kydautu['ngay_bat_dau'].rank().astype(int)
    df_add_ht = df_add_ht.merge(df_kydautu[['Kỳ đầu tư','index_kdt']], on='Kỳ đầu tư', how='left')
    df_dt_dk_nguong_grp = df_add_ht.groupby(['Kỳ đầu tư'], as_index=False).agg({'% khai thác sau 6T':'mean'})
    df_dt_dk_nguong_grp['year'] = df_dt_dk_nguong_grp['Kỳ đầu tư'].str[2:]
    df_dt_dk_nguong_grp['year'] = df_dt_dk_nguong_grp['year'].astype(int)+1
    df_dt_dk_nguong_grp['ky dau tu'] = df_dt_dk_nguong_grp.apply(lambda x:x['Kỳ đầu tư'][:2]+
                                                                 str(x['year']), axis=1)
    df_dt_dk_nguong_grp.drop(['Kỳ đầu tư','year'], axis=1,inplace=True)
    df_dt_dk_nguong_grp.rename({'ky dau tu':'Kỳ đầu tư'},axis=1, inplace=True)
    df_dt_dk_nguong_grp.columns  = [ 'ngưỡng TB','Kỳ đầu tư']
    df_dt_dk_nguong_grp.loc[len(df_dt_dk_nguong_grp.index)] = [df_dt_dk_nguong_grp[df_dt_dk_nguong_grp['Kỳ đầu tư']=='1H2021']['ngưỡng TB'].values[0],'1H2020'] 
    df_dt_dk_nguong_grp.loc[len(df_dt_dk_nguong_grp.index)] = [df_dt_dk_nguong_grp[df_dt_dk_nguong_grp['Kỳ đầu tư']=='1H2021']['ngưỡng TB'].values[0],'2H2020'] 
    df_dt_dk_nguong_grp.columns =['nguong_tb','ky_dau_tu']
    return df_dt_dk_nguong_grp
def process_lichsudautu(date,df_branch_province,df_dt_dk_nguong_grp,config):
    """
        Tính toán các thông tin về lịch sử đầu tư trước đó của xã/phường:
            + Load dữ liệu lịch sử đầu tư từ postgresql 177 - dwh_noc - public.tbl_planning_history
            +  Chuẩn hoá thông tin về địa chỉ: phục vụ mapping các đầu dữ liệu 
            + Xử lý dữ liệu missing về port ở các mốc thời gian 
            + Tính hiệu quả khai thác ở từng mốc thời gian 
            + Xử lý lấy số lần đầu tư cho đến hiện tại và hiệu quả đầu tư 6 tháng lần đầu tư gần nhất 
    """
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
        start_date = str(int(date[:4]))+'-07-01'
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
            start_date = str(int(date[:4]))+'-01-01'
        else:
            kydautu= '1H'+str(int(date[:4])+1)
            start_date = str(int(date[:4])+1)+'-01-01'
    if (kydautu[0]=='1'):
        kydautu_truoc = '2H'+str(int(kydautu[2:])-1)
    else:
        kydautu_truoc = '1H'+(kydautu[2:])
    next_date = (datetime.strptime(start_date,"%Y-%m-%d") + relativedelta(months=6)).strftime('%Y-%m-01')
    
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    if kydautu=='1H2020':
        str_sql = "select * from  public.{} where ngay_bat_dau<='{}'".format(config['feature_ptht']['table_planning'],next_date)
    else:
        str_sql = "select * from  public.{} where ngay_bat_dau<='{}'".format(config['feature_ptht']['table_planning'],start_date)
    df_add_ht = pd.read_sql(str_sql, conn)
    df_add_ht.drop(['created_at','updated_at'],axis=1,inplace=True)
    conn.close()
    df_add_ht.columns = ['Mã kế hoạch', 'Kỳ đầu tư', 'POP', 'Phường', 'Quận', 'Chi nhánh',
           'Vùng', 'DL triển khai', 'Perport', 'Tổng port sau 3T',
           'Port dùng sau 3T', '% khai thác sau 3T', 'Tổng port sau 6T',
           'Port dùng sau 6T', '% khai thác sau 6T', 'Tổng port sau 9T',
           'Port dùng sau 9T', '% khai thác sau 9T', 'Tổng port sau 12T',
           'Port dùng sau 12T', '% khai thác sau 12T','ngay_bat_dau']
    df_add_ht.replace({'Vùng':{'Vung':'Vùng'}},regex=True,inplace=True)

    df_add_ht['Chi nhánh'] = df_add_ht['Chi nhánh'].str.strip('-|,|[ ]|.')
    df_add_ht[['Mã kế hoạch','Phường','Quận','Chi nhánh','POP']] = df_add_ht[['Mã kế hoạch','Phường',
                   'Quận','Chi nhánh','POP']].fillna(value='')
    df_add_ht['province'] = df_add_ht['Chi nhánh'].str[:3]
    df_add_ht['province'] = df_add_ht['province'].apply(lambda x:
                                    re.sub('\d', 'I', x))
    df_add_ht.replace({'province':{'HNII':'HNI','HBN':'HBH','BRA':'BRU',
                                  'SGN':'HCM'}},regex=True,inplace=True)
    df_add_ht['Mã kế hoạch'] = df_add_ht['Mã kế hoạch'].str.upper()
    df_province_ = df_branch_province.rename({'name':'Tỉnh'},axis=1)
    df_add_ht = df_add_ht.merge(df_province_, on='province', how='left')
    df_add_ht['Mã kế hoạch'] = np.where(df_add_ht['Mã kế hoạch']=='', '2H2023',
                                        df_add_ht['Mã kế hoạch'])
    df_add_ht['Tổng port sau 3T'] = pd.to_numeric(df_add_ht['Tổng port sau 3T'], errors='coerce')
    df_add_ht['Port dùng sau 3T'] = pd.to_numeric(df_add_ht['Port dùng sau 3T'], errors='coerce')
    df_add_ht['Tổng port sau 6T'] = pd.to_numeric(df_add_ht['Tổng port sau 6T'], errors='coerce')
    df_add_ht['Port dùng sau 6T'] = pd.to_numeric(df_add_ht['Port dùng sau 6T'], errors='coerce')
    df_add_ht['Tổng port sau 9T'] = pd.to_numeric(df_add_ht['Tổng port sau 9T'], errors='coerce')
    df_add_ht['Port dùng sau 9T'] = pd.to_numeric(df_add_ht['Port dùng sau 9T'], errors='coerce')
    df_add_ht['Tổng port sau 12T'] = pd.to_numeric(df_add_ht['Tổng port sau 12T'], errors='coerce')
    df_add_ht['Port dùng sau 12T'] = pd.to_numeric(df_add_ht['Port dùng sau 12T'], errors='coerce')
    df_add_ht['Tổng port sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']!=df_add_ht['Tổng port sau 6T'],
                                              df_add_ht['Tổng port sau 6T'],df_add_ht['Tổng port sau 3T'])
    df_add_ht['Tổng port sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']<df_add_ht['Port dùng sau 3T'],
                                              df_add_ht['DL triển khai'],df_add_ht['Tổng port sau 3T'])
    df_add_ht['Tổng port sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']<df_add_ht['Port dùng sau 3T'],
                                              df_add_ht['Port dùng sau 3T'],df_add_ht['Tổng port sau 3T'])
    df_add_ht['Tổng port sau 6T'] = np.where(df_add_ht['Tổng port sau 6T']<df_add_ht['Port dùng sau 6T'],
                                              df_add_ht['Tổng port sau 3T'],df_add_ht['Tổng port sau 6T'])
    df_add_ht['Tổng port sau 9T'] = np.where(df_add_ht['Tổng port sau 9T']<df_add_ht['Port dùng sau 9T'],
                                              df_add_ht['Tổng port sau 6T'],df_add_ht['Tổng port sau 9T'])
    df_add_ht['Tổng port sau 12T'] = np.where(df_add_ht['Tổng port sau 12T']<df_add_ht['Port dùng sau 12T'],
                                              df_add_ht['Tổng port sau 9T'],df_add_ht['Tổng port sau 12T'])
    
    normalize_address('Không dấu', df_add_ht)
    # df_add_ht= df_add_ht.sort_values(['Mã kế hoạch','Kỳ đầu tư','POP','Phường không dấu','Quận không dấu',
    #                                   'Tỉnh không dấu','DL triển khai'], ascending=False)
    # df_add_ht = df_add_ht.drop_duplicates(subset=['Mã kế hoạch','Kỳ đầu tư','POP','Phường không dấu','Quận không dấu',
    #                                   'Tỉnh không dấu'], keep='first')
    df_add_ht = df_add_ht.groupby(['Mã kế hoạch','Kỳ đầu tư','POP','Phường không dấu','Quận không dấu','Tỉnh không dấu',
        'Chi nhánh','Vùng'],as_index=False).agg({'DL triển khai':'sum','Perport':'mean','Tổng port sau 3T':'sum',
        'Port dùng sau 3T':'sum','Tổng port sau 6T':'sum','Port dùng sau 6T':'sum'
        ,'Tổng port sau 9T':'sum','Port dùng sau 9T':'sum'
         ,'Tổng port sau 12T':'sum','Port dùng sau 12T':'sum'})
    df_add_ht['% khai thác sau 3T'] = np.where(df_add_ht['Tổng port sau 3T']<=0,0,
                                     df_add_ht['Port dùng sau 3T']/df_add_ht['Tổng port sau 3T'])
    df_add_ht['% khai thác sau 6T'] = np.where(df_add_ht['Tổng port sau 6T']<=0,0,
                                     df_add_ht['Port dùng sau 6T']/df_add_ht['Tổng port sau 6T'])
    df_add_ht['% khai thác sau 9T'] = np.where(df_add_ht['Tổng port sau 9T']<=0,0,
                                     df_add_ht['Port dùng sau 9T']/df_add_ht['Tổng port sau 9T'])
    df_add_ht['% khai thác sau 12T'] = np.where(df_add_ht['Tổng port sau 12T']<=0,0,
                                     df_add_ht['Port dùng sau 12T']/df_add_ht['Tổng port sau 12T'])
    df_add_ht = df_add_ht[['Mã kế hoạch', 'Kỳ đầu tư', 'POP', 'Phường không dấu', 'Quận không dấu',
           'Chi nhánh', 'Vùng', 'DL triển khai', 'Perport', 'Tổng port sau 3T',
           'Port dùng sau 3T', '% khai thác sau 3T', 'Tổng port sau 6T',
           'Port dùng sau 6T', '% khai thác sau 6T', 'Tổng port sau 9T',
           'Port dùng sau 9T', '% khai thác sau 9T', 'Tổng port sau 12T',
           'Port dùng sau 12T', '% khai thác sau 12T']]
    df_add_ht.columns =['Mã kế hoạch', 'Kỳ đầu tư', 'POP', 'Phường', 'Quận',
           'Chi nhánh', 'Vùng', 'DL triển khai', 'Perport', 'Tổng port sau 3T',
           'Port dùng sau 3T', '% khai thác sau 3T', 'Tổng port sau 6T',
           'Port dùng sau 6T', '% khai thác sau 6T', 'Tổng port sau 9T',
           'Port dùng sau 9T', '% khai thác sau 9T', 'Tổng port sau 12T',
           'Port dùng sau 12T', '% khai thác sau 12T']
    df_add_ht = df_add_ht.sort_values(['Mã kế hoạch','Kỳ đầu tư','POP','Phường','Quận','Chi nhánh','Vùng','DL triển khai',
                                      'Perport','Tổng port sau 3T','Tổng port sau 6T','Tổng port sau 9T','Tổng port sau 12T'],ascending=False)
    df_add_ht['% khai thác sau 6T'] = np.where(df_add_ht['% khai thác sau 6T']<df_add_ht['% khai thác sau 3T'],
                                              df_add_ht['% khai thác sau 3T'],df_add_ht['% khai thác sau 6T'])
    #  nomalize xã/ phường, quận
    df_add_ht['Quận'] = df_add_ht['Quận'].apply(lambda x: unidecode.unidecode(str(x)))
    df_add_ht['Phường'] = df_add_ht['Phường'].apply(lambda x: unidecode.unidecode(str(x)))
    df_add_ht.replace({'Quận' : { r'(H[.])': 'Huyen ', r'Q[.]': 'Quan ','Tp[.]|TP[.]|TP[ ]|Tp[ ]|Thanh Pho[ ]': \
                                                   'Thanh pho ', 'TX[.]|Thi Xa[ ]|T[.]Xa[ ]|TX[ ]':'Thi xa '}}, regex=True,inplace=True)
    df_add_ht.replace({'Phường' : { r'T[.]T[.]|T[.]T[ ]|TT[.]|T[.]Tran[ ]|Thi Tran[ ]|TT[ ]|Thi tran[ ]': 'Thi tran '\
                                                     , r'TX[.]|TX[ ]|T[.]xa[ ]|T[.]Xa[ ]|Thi Xa[ ]': 'Thi xa ','P[.]': 'Phuong '\
                                                     , 'Xa[.]|Xa[ ]|xa[ ]|Xã[ ]|Xa\xa0':'Xa ','Khu Pho[ ]':'Khu pho ','KCN[ ]':'Khu che xuat '}}, regex=True,inplace=True)
    
    df_add_ht.replace({'Phường' : { r'(Thi tran[ ])': '', r'Phuong[ ]': '',r'Thi Xa[ ]': '','Xa[ ]': '','Ap[ ]': '', r'Huyen[ ]': ''}}, regex=True,inplace=True)
    df_add_ht.replace({'Quận' : { r'(Quan[ ])': '', r'Huyen[ ]': '', r'huyen[ ]': '','Thi xa[ ]': '','Thanh pho[ ]': '','Xa[ ]': ''}}, 
                           regex=True,inplace=True)
    df_add_ht['Phường'] = df_add_ht['Phường'].str.lower()
    df_add_ht['Quận'] = df_add_ht['Quận'].str.lower()
    
    df_add_ht['Phường']= df_add_ht['Phường'].apply(lambda x: x.strip())
    df_add_ht['Quận']= df_add_ht['Quận'].apply(lambda x: x.strip())
    
    df_add_ht['Quận']= df_add_ht['Quận'].str.title()
    df_add_ht['Phường']= df_add_ht['Phường'].str.title()
    df_add_ht['Quận'] = df_add_ht['Quận'].apply(lambda x: 'Quan '+ str(int(x)) if (all(char.isdigit() for char in x)==True) and ( x not in ([''])) else x)
    # xử lý phường chứa số
    df_add_ht['Phường'] = df_add_ht['Phường'].apply(lambda x: 'Phuong '+ str(int(x)) if (all(char.isdigit() for char in x)==True) and ( x not in ([''])) else x)
    df_add_ht.replace({'Quận':{'Chau Thanh - Hau Giang':'Chau Thanh'}},regex=True, inplace=True)
    df_pop = df_add_ht.groupby(['Phường', 'Quận','Chi nhánh','Vùng'], as_index=False).agg({'Kỳ đầu tư':'count'})
    df_pop.drop('Kỳ đầu tư', axis=1, inplace=True)
    df_pop_1 = df_pop.copy()
    df_pop_1['Kỳ đầu tư']= kydautu
    df_add_ht = df_add_ht.merge(df_pop_1, on=[ 'Phường', 'Quận', 'Chi nhánh', 'Vùng', 'Kỳ đầu tư'], how='outer')
    df_kydautu = pd.DataFrame({'Kỳ đầu tư':df_add_ht['Kỳ đầu tư'].unique()})
    df_kydautu['ngay_bat_dau'] = df_kydautu['Kỳ đầu tư'].apply(lambda x: get_ngaybatdau(x))
    df_kydautu['ngay_bat_dau'] = pd.to_datetime(df_kydautu['ngay_bat_dau'])
    df_kydautu = df_kydautu.sort_values('ngay_bat_dau')
    df_kydautu['index_kdt'] = df_kydautu['ngay_bat_dau'].rank().astype(int)
    df_add_ht = df_add_ht.merge(df_kydautu[['Kỳ đầu tư','index_kdt']], on='Kỳ đầu tư', how='left')
    df_add_ht_cp = df_add_ht.sort_values(['Phường', 'Quận','Chi nhánh','Vùng','index_kdt'], ascending=False)
    df_add_ht_cp["rank"] = df_add_ht_cp.groupby(['Phường', 'Quận','Chi nhánh','Vùng'])["index_kdt"].rank("dense", ascending=True)
    
    df_label = df_add_ht_cp[['Mã kế hoạch', 'Kỳ đầu tư',  'Phường', 'Quận', 'Chi nhánh', 'Vùng',
                             'rank','index_kdt']]
    df_label.columns = ['Mã kế hoạch', 'Kỳ đầu tư', 'Phường', 'Quận', 'Chi nhánh', 'Vùng',
           'rank', 'index_kdt']
    
    df_kt = df_add_ht_cp[['rank','index_kdt', 'Phường', 'Quận','Chi nhánh','Vùng']]
    df_kt.columns = ['rank truoc','index_truoc',  'Phường', 'Quận','Chi nhánh','Vùng']
    df_kt['rank'] = df_kt['rank truoc'] + 1
    df_kt_full = df_label.merge(df_kt, on=[ 'Phường', 'Quận','Chi nhánh','Vùng','rank'], how='outer')
    df_kt_full = df_kt_full[~df_kt_full['Kỳ đầu tư'].isna()]
    df_kt_full_1 = df_kt_full.drop_duplicates(keep='first')
    
    df_kt_full_1['TG đầu tư gần nhất'] = (df_kt_full_1['index_kdt'] - df_kt_full_1['index_truoc'])*6
    df_dautu_min = df_kt_full_1.groupby(['Phường','Quận','Chi nhánh','Vùng']).agg({'rank':'min'}).reset_index()
    df_dautu_min.columns= ['Phường', 'Quận', 'Chi nhánh', 'Vùng','rank_min']
    df_kt_full_1 = df_kt_full_1.merge(df_dautu_min, on=[ 'Phường', 'Quận', 'Chi nhánh', 'Vùng'], how='left')
    df_kt_full_1['num_khdt_truoc'] = df_kt_full_1['rank']- df_kt_full_1['rank_min'] 
    df_dautu = df_kt_full_1[['Phường', 'Quận', 'Chi nhánh', 'Vùng']]
    df_dautu_full = df_kt_full_1.groupby(['Phường','Quận','Chi nhánh','Vùng','Kỳ đầu tư','index_kdt']).agg({
        'TG đầu tư gần nhất':'min','num_khdt_truoc':'mean'}).reset_index()
    df_add_ht_cp_1 = df_add_ht.copy()
    df_add_ht_cp_gp = df_add_ht_cp_1.groupby(['Kỳ đầu tư','index_kdt','Phường','Quận', 
        'Chi nhánh', 'Vùng'],as_index=False).agg({
    'DL triển khai':'sum','Perport':'mean','Tổng port sau 3T':'sum','Port dùng sau 3T':'sum',
    'Tổng port sau 6T':'sum','Port dùng sau 6T':'sum','Tổng port sau 9T':'sum','Port dùng sau 9T':'sum',
    'Tổng port sau 12T':'sum','Port dùng sau 12T':'sum'})
    df_add_ht_cp_gp = df_add_ht_cp_gp.sort_values(['Phường', 'Quận','Chi nhánh','Vùng','index_kdt']
                                                  , ascending=False)
    df_add_ht_cp_gp["rank"] = df_add_ht_cp_gp.groupby(['Phường', 'Quận','Chi nhánh','Vùng'])["index_kdt"].rank("dense", ascending=True)
    df_label_1 = df_add_ht_cp_gp[['Kỳ đầu tư','Phường','Quận', 'Chi nhánh', 'Vùng' ,'index_kdt','rank',
                                 'Tổng port sau 6T','Port dùng sau 6T']]
    df_label_1.columns=['Kỳ đầu tư', 'Phường', 'Quận', 'Chi nhánh', 'Vùng',  'index_kdt','rank',
                       'Tổng port sau 6T hien tai','Port dùng sau 6T hien tai']
    df_kt_1 = df_add_ht_cp_gp[['rank','index_kdt','Phường','Quận','Chi nhánh','Vùng','Perport',
                      'DL triển khai', 'Tổng port sau 3T','Port dùng sau 3T','Tổng port sau 6T',
       'Port dùng sau 6T','Tổng port sau 9T','Port dùng sau 9T', 'Tổng port sau 12T','Port dùng sau 12T']]
    df_kt_1.columns = ['rank truoc','index_truoc', 'Phường','Quận','Chi nhánh','Vùng', 'Perport',
            'DL triển khai', 'Tổng port sau 3T','Port dùng sau 3T','Tổng port sau 6T','Port dùng sau 6T',
                      'Tổng port sau 9T','Port dùng sau 9T', 'Tổng port sau 12T','Port dùng sau 12T']
    df_kt_1['rank'] = df_kt_1['rank truoc']+1
    df_kt_full_ = df_label_1.merge(df_kt_1, on=['Phường','Quận','Chi nhánh','Vùng','rank'], how='outer')
    df_kt_full_dl = df_kt_full_[(~df_kt_full_['Kỳ đầu tư'].isna())]
    df_kt_full_dl['% khai thác sau 3T'] = df_kt_full_dl['Port dùng sau 3T']/df_kt_full_dl['Tổng port sau 3T']
    df_kt_full_dl['% khai thác sau 6T'] = df_kt_full_dl['Port dùng sau 6T']/df_kt_full_dl['Tổng port sau 6T']
    df_kt_full_dl['% khai thác sau 9T'] = df_kt_full_dl['Port dùng sau 9T']/df_kt_full_dl['Tổng port sau 9T']
    df_kt_full_dl['% khai thác sau 12T'] = df_kt_full_dl['Port dùng sau 12T']/df_kt_full_dl['Tổng port sau 12T']
    df_kt_full = df_kt_full_dl.merge(df_dautu_full,
            on=['Kỳ đầu tư','index_kdt', 'Phường','Quận', 'Chi nhánh', 'Vùng'], how='outer')
    df_kt_full.replace({'Chi nhánh' : { r'_': '', r'-': '', r'HNI': 'HN', r'SGN': 'HCM', r'hcm': 'HCM',
                                      r'hcm': 'HCM' ,r'HN0': 'HN',r'HCM0': 'HCM'}}, regex=True,inplace=True)
    df_kt_full['% portfree sau 3T'] = 1 - df_kt_full['% khai thác sau 3T']
    df_kt_full['% portfree sau 6T'] = 1 - df_kt_full['% khai thác sau 6T']
    df_kt_full['% portfree sau 9T'] = 1 - df_kt_full['% khai thác sau 9T']
    df_kt_full['% portfree sau 12T'] = 1 - df_kt_full['% khai thác sau 12T']
    df_kt_full.drop_duplicates(keep='first', inplace=True)
    df_kt_full['HQKT 6T hiệu tại'] = np.where((df_kt_full['Tổng port sau 6T hien tai']==0),
                0,np.where((df_kt_full['Tổng port sau 6T hien tai']>0),
                df_kt_full['Port dùng sau 6T hien tai']/df_kt_full['Tổng port sau 6T hien tai'],None))
    df_dt_dk_nguong_grp.columns  = [ 'ngưỡng TB','Kỳ đầu tư']
    df_kt_full = df_kt_full.merge(df_dt_dk_nguong_grp, on=['Kỳ đầu tư'], how='left')
    
    df_kt_full['ngưỡng TB'] = np.where(df_kt_full['ngưỡng TB'].isna(),df_kt_full[df_kt_full['Kỳ đầu tư']=='1H2021']['ngưỡng TB'].mean(),
                                         df_kt_full['ngưỡng TB'])
    df_kt_full['danh_gia_hieu_qua'] = np.where(df_kt_full['HQKT 6T hiệu tại']>=df_kt_full['ngưỡng TB'],
                   'Hiệu quả',np.where((df_kt_full['HQKT 6T hiệu tại']<df_kt_full['ngưỡng TB'])&
                      (~df_kt_full['HQKT 6T hiệu tại'].isna()),
                     'Không hiệu quả','Chưa xác định'))
    df_check_dl = df_kt_full.groupby('Kỳ đầu tư',as_index=False).agg({'Tổng port sau 6T hien tai':'mean'})
    df_kt_full['danh_gia_hieu_qua'] = np.where(df_kt_full['Kỳ đầu tư'].isin(
                                df_check_dl[df_check_dl['Tổng port sau 6T hien tai']==0]['Kỳ đầu tư'].unique())
                                ,'Chưa xác định',df_kt_full['danh_gia_hieu_qua'])
    df_kt_full= df_kt_full[['Phường', 'Quận', 'Chi nhánh', 'Vùng', 'Kỳ đầu tư', 'index_kdt',
           'TG đầu tư gần nhất', 'num_khdt_truoc', 'DL triển khai',
           '% khai thác sau 3T', '% khai thác sau 6T', '% khai thác sau 9T',
           '% khai thác sau 12T', 'Perport', 'Tổng port sau 6T hien tai',
           'Port dùng sau 6T hien tai', '% portfree sau 3T', '% portfree sau 6T',
           '% portfree sau 9T', '% portfree sau 12T', 'HQKT 6T hiệu tại',
           'ngưỡng TB', 'danh_gia_hieu_qua']]
    df_kt_full.columns= ['Phường không dấu', 'Quận không dấu', 'Chi nhánh', 'Vùng', 'Kỳ đầu tư', 'index_kdt',
           'TG đầu tư gần nhất', 'num_khdt_truoc', 'DL triển khai',
           '% khai thác sau 3T', '% khai thác sau 6T', '% khai thác sau 9T',
           '% khai thác sau 12T', 'Perport', 'Tổng port sau 6T hien tai',
           'Port dùng sau 6T hien tai', '% portfree sau 3T', '% portfree sau 6T',
           '% portfree sau 9T', '% portfree sau 12T', 'HQKT 6T hiệu tại',
           'ngưỡng TB', 'danh_gia_hieu_qua']
    df_kt_full['HQKT 6T hiệu tại'] = df_kt_full['HQKT 6T hiệu tại'].astype(float)
    df_kt_full['province'] = np.where((df_kt_full['Chi nhánh']!='HNM')&(df_kt_full['Chi nhánh'].str.contains('HN')),
                                     'HNI',df_kt_full['Chi nhánh'].str[:3] )
    df_kt_full = df_kt_full.merge(df_branch_province, on='province',how='left')
    df_kt_full.drop('province',axis=1,inplace=True)
    df_kt_full.rename({'name':'Tỉnh không dấu'},axis=1,inplace=True)
    df_kt_full = df_kt_full[df_kt_full['Kỳ đầu tư']==kydautu]
    return df_kt_full
def process_vanphonggiaodich(df_diachidoi,config):
    """
        + Load dữ liệu văn phòng giao dịch ftel từ postgresql 177 -dwh_noc - public.tbl_shopfpttelecom_info
        + Chuẩn hoá dữ liệu địa chỉ, địa chỉ thay đổi do sáp nhập
    """
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    df_VPGD = pd.read_sql("select * from  public.%s"% (config['feature_ptht']['table_ftelshop']), conn)
    conn.close()
    df_VPGD['province']= df_VPGD['province'].str.title()
    df_VPGD = df_VPGD.where(pd.notnull(df_VPGD), '')
    df_VPGD_grp = df_VPGD.groupby(['ward', 'district','province'], as_index=False).agg({'address':'count'})
    df_VPGD_grp.columns = ['Phường', 'Huyện', 'Tỉnh', 'số_vp']
    # xử lý lại địa chỉ:trường,  bệnh viện, đại lý
    df_VPGD_grp.replace({'Phường':{'Phường|Xã|Thị Trấn':''}},regex=True, inplace=True)
    df_VPGD_grp.replace({'Huyện':{'Huyện|Thành Phố|Thị Xã|Quận|Thị Xã Ba Đồn':''}},regex=True, inplace=True)
    
    df_VPGD_grp['Huyện']= df_VPGD_grp['Huyện'].apply(lambda x: re.sub('(Q+)(\d)', func, x) )
    df_VPGD_grp['Phường'] = df_VPGD_grp['Phường'].apply(lambda x: re.sub('(P+)(\d)', func, x))
    df_VPGD_grp['Huyện'] = df_VPGD_grp['Huyện'].apply(lambda x: 'Quận '+ x if any(char.isdigit() for char in x)==True else x)
    df_VPGD_grp['Phường'] = df_VPGD_grp['Phường'].apply(lambda x: 'Phường '+ x if any(char.isdigit() for char in x)==True else x)
    df_VPGD_grp['Huyện'] = df_VPGD_grp['Huyện'].str.strip('-|,|[ ]|.')
    df_VPGD_grp['Phường'] = df_VPGD_grp['Phường'].str.strip('-|,|[ ]|.')
    df_VPGD_grp['Huyện'] = df_VPGD_grp['Huyện'].apply(lambda x: unidecode.unidecode(str(x)))
    df_VPGD_grp['Phường'] = df_VPGD_grp['Phường'].apply(lambda x: unidecode.unidecode(str(x)))
    
    df_VPGD_grp['Tỉnh'] = df_VPGD_grp['Tỉnh'].apply(lambda x: unidecode.unidecode(str(x)))
    df_VPGD_grp.columns = ['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'số_vp']
    df_VPGD_grp.replace({'Phường không dấu':{'Tri Tran':''}},regex=True, inplace=True)
    
    df_VPGD_grp = df_VPGD_grp.sort_values(['Tỉnh không dấu','Phường không dấu','Quận không dấu','số_vp'],ascending=False)
    df_VPGD_grp = df_VPGD_grp.drop_duplicates(['Tỉnh không dấu','Phường không dấu','Quận không dấu'], keep='first')
    df_VPGD_grp_filter = df_VPGD_grp[(df_VPGD_grp['Quận không dấu']!='')&
                                    (df_VPGD_grp['Phường không dấu']!='')]
    df_VPGD_grp_filter.replace({'Phường không dấu':{'Phuong  ':'Phuong '}},regex=True,inplace=True)
    df_VPGD_grp_filter.replace({'Phường không dấu':{'Phuong Co Nhue 2':'Co Nhue 2',
    'Phuong My Dinh 2':'My Dinh 2',
    'Thi  Trang Bang':'Trang Bang',
    'Phuong Gia Tan 2':'Gia Tan 2',
    'Phuong Sai':'Sai'}},regex=True,inplace=True)
    df_VPGD_grp_filter.replace({'Quận không dấu':{'Ba Don,  Quang Trach':'Quang Trach',
    'Quan  ':'Quan ',
    'Phan Rang - Thap Cham':'Phan Rang-Thap Cham'}},regex=True,inplace=True)
    df_VPGD_grp_filter['Quận không dấu'] = df_VPGD_grp_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_VPGD_grp_filter['Phường không dấu'] = df_VPGD_grp_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_VPGD_grp_filter['Quận không dấu'] = np.where((df_VPGD_grp_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                        (df_VPGD_grp_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                'Thu Duc' ,df_VPGD_grp_filter['Quận không dấu'])
    df_VPGD_grp_filter_gp = df_VPGD_grp_filter.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
    'số_vp':'sum'})
    df_VPGD_grp_filter_gp= df_VPGD_grp_filter_gp.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='left')
    df_VPGD_grp_filter_gp['Phường thay đổi']= np.where(df_VPGD_grp_filter_gp['Phường thay đổi'].isna(),
                                                      df_VPGD_grp_filter_gp['Phường không dấu'],
                                                      df_VPGD_grp_filter_gp['Phường thay đổi'])
    df_VPGD_grp_filter_gp['Quận thay đổi']= np.where(df_VPGD_grp_filter_gp['Quận thay đổi'].isna(),
                                                      df_VPGD_grp_filter_gp['Quận không dấu'],
                                                      df_VPGD_grp_filter_gp['Quận thay đổi'])
    df_VPGD_grp_filter_gp['Tỉnh thay đổi']= np.where(df_VPGD_grp_filter_gp['Tỉnh thay đổi'].isna(),
                                                      df_VPGD_grp_filter_gp['Tỉnh không dấu'],
                                                      df_VPGD_grp_filter_gp['Tỉnh thay đổi'])
    df_VPGD_grp_filter_gp= df_VPGD_grp_filter_gp[['Phường thay đổi','Quận thay đổi',
                        'Tỉnh thay đổi','số_vp']]
    df_VPGD_grp_filter_gp.columns= ['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu','số_vp']
    df_VPGD_grp_filter_gp = df_VPGD_grp_filter_gp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
    'số_vp':'sum'})
    return df_VPGD_grp_filter_gp
def process_dailycanhto(date,df_branch,config):
    """
        + Load dữ liệu về nhân viên và doanh thu đại lý canh tô từ postgresql 177 - dwh_noc - public.tbl_sale_info  và public.tbl_sales_revenue
        + Chuẩn hoá thông tin địa chỉ 
    """
    date ='2023-09-01'
    start_date = (datetime.strptime(date,"%Y-%m-%d") - relativedelta(months=6)).strftime('%Y-%m-01')
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    df_branch_nv = pd.read_sql("SELECT province, name FROM public.%s GROUP BY province, name"%(config['feature_ptht']['tablename_province']), conn)
    conn.close()
    df_branch_nv.replace({'name':{r'Hue':'Thua Thien Hue',r'Ba Ria':'Ba Ria Vung Tau'
                       }}, regex=True, inplace=True)
    df_branch_nv = df_branch_nv[~df_branch_nv.name.isna()]
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    df_nhanvien_full = pd.read_sql("SELECT * FROM %s"%(config['feature_ptht']['table_saleinfo']), conn)
    conn.close()
    df_nhanvien_full.drop(['updated_at'],axis=1,inplace=True)
    df_nhanvien_full.columns = ['Mã nhân viên', 'Tên nhân viên', 'Tên đầy đủ', 'Tình Trạng NV',
           'Thuộc nhóm QTV', 'Chức vụ', 'Phòng ban', 'Vùng', 'Trung Tâm',
           'Chi nhánh', 'Địa chỉ', 'Ngày tạo', 'Thời gian tính lương']
    
    df_nhanvien_full = df_nhanvien_full.sort_values('Ngày tạo', ascending=True)
    df_nhanvien_full['date'] = df_nhanvien_full['Ngày tạo'].dt.date
    df_nhanvien_full['Tên nhân viên'].replace('?','',inplace=True)
    df_nhanvien_full['province'] = df_nhanvien_full['Chi nhánh'].str[:3]
    df_dlct = df_nhanvien_full.merge(df_branch_nv, on='province', how='left')
    df_dlct[['province','name']] = df_dlct[['province','name']].fillna(value='')
    df_dlct_grp = df_dlct.groupby(['Tên nhân viên','province','name','Địa chỉ','Ngày tạo','Tình Trạng NV']).agg({'Mã nhân viên':'count'}).reset_index()
    df_ttin= df_dlct_grp[['Tên nhân viên','province','name','Địa chỉ','Ngày tạo','Tình Trạng NV']]
    df_ttin['Địa chỉ'] = np.where(df_ttin['Địa chỉ']=='24/9 Duong Dang Phuc Vinh(Ap Thoi Tu 1),Xa TTT,HM',
                                      '24/9 Duong Dang Phuc Vinh(Ap Thoi Tu 1),Xã Thới Tam Môn,huyện Hóc Môn',df_ttin['Địa chỉ'])
    df_ttin['Địa chỉ gốc'] = df_ttin['Địa chỉ']
    # viết hoa chữ cái đầu
    #  xoá dấu
    df_ttin['Địa chỉ'] = df_ttin['Địa chỉ'].str.title()
    df_ttin['Địa chỉ'] = df_ttin['Địa chỉ'].apply(lambda x: unidecode.unidecode(str(x)))
    
    df_ttin.replace({'Địa chỉ':{
    'Phuong 12 Go Vap':' phuong 12, Go Vap','Ng Van Bi':'Dang Van Bi','[,] Phung[ ]':', Phuong ','Tp.Th C':'TP Thu Duc'
    ,'H Chi Minh':'Ho Chi Minh',
    'Ha Ni$':'Ha Noi','Chau Th Kim':'Chau Thi Kim','A Nng$':'Da Nang','Qung Binh$':'Quang Binh',
    'Bn Tre$':'Ben Tre','Hi Phong$':'Hai Phong','Nam Nh':'Nam Dinh','Ngo Quyn':'Ngo Quyen',
    'Bui Xuong Trch':'Bui Xuong Trach','Khuong Inh':'Khuong Dinh','Chu Mnh Trinh':'Chu Manh Trinh',
    'Tp.Ng Hi':'Tp. Dong Hoi','Bc Ly':'Bac Ly','Tp.Bntre':'Tp. Ben Tre',
    'Trn Thanh Ng':'Tran Thanh Ngo','Kin An':'Kien An','Vn M':'Van My','Lc Vung':'Loc Vuong',
    'Hip Binh Phuc':'Hiep Binh Phuoc','Ung S 16':'Duong so 16','Nguyn Xin  Bdg':'Nguyen Xien',
    'Hoang Diu':'Hoang Dieu','Linh Chiu':'Linh Chieu',
    'C Chi$':'Cu Chi', 'Can Duoc Long An':'Can Duoc, Long An','Phung Linh Trung':'Phuong Linh Trung','TP.Th c':'TP. Thu Duc',
    'Duong Dang Phuc Vinh[(]Ap Thoi Tu 1[)], xa Ttt,Hm':'Duong Dang Thuc Vinh, ap Thoi Tu, xa Thoi Tam Thon, huyen Hoc Mon, Ho Chi Minh',
    'H Chi Minh':'Ho Chi Minh','Tnh L':'Tinh Lo','Quc L':'Quoc Lo','C Chi':'Cu Chi','Tan Thnh Ong':'Tan Thanh Dong',
    'Phuc Thnh':'Phuoc Thanh','Phm Van Ci':'Pham Van Coi','Trung Lp Thung':'Trung Lap Thuong',
    'Trung Lp':'Trung Lap',
    r'[ ]H[ ]|H[.]|Huyen':' huyen ',
    r'Ttr[.]|Tt[.]|Ttr[ ]|Thi[ ]Tran|T[.]tran|Tt[ ]':' thi tran '
    ,r'Tx[.]|Tx[ ]|Thi xa[ ]|Thi Xa[ ]|Th  xa':' thi xa ',r'T[.]|[ ]T[ ]|Tinh[ ]':' tinh '
    ,r'Tp[.]|Tp[ ]|Thanh pho[ ]|Thanh Pho[ ]':' thanh pho ',
    r'[ ]P[ ]|[ ]p[.]|P[.]|Ph[ ]|Ph[.]|Phuong[ ]':' phuong ',r'X[.]|Xa[ ]':' xa ',
    r'Q[.]|Q[ ]|Quan[ ]':' quan ',
    'Kien Gian$':'Kien Giang','Dong Tha$':'Dong Thap','Ngh An$':'Nghe An',
    'xa Qunh Lp':'Xa Quynh Lap','10, Lê Van Th':'10, Lê Van Thu','xa Nghia M':'xa Nghia My',
     'Thu Uc':'Thu Duc','Tan Binh Chanh':'Tan Tuc, Binh Chanh','Banh Chanh':'Binh Chanh'
    }}, regex=True, inplace=True) 
    df_ttin.replace({'Địa chỉ':{r'Vung Tau|Ba Ria Vung Tau|Ba Ria - Vung Tau|Br Vung Tau|Ba Ra  Vung Tau':' Ba Ria Vung Tau',
                        r'Ak Lak|Daklak| K Lk':' Dak Lak'
                        ,r'Ha Ni$|Hn$':' Ha Noi',r'Qnh':'Quang Ninh'
                       ,r'Phu Th$':' Phu Tho',
                        r'A Nang|A Nng':' Da Nang',r'Qung Tr$':' Quang Tri',
                       r'Qung':' Quang ',r'Bc Giang':' Bac Giang',r'Nd$|Nam Inh':' Nam Định'
                       ,r'Lam Ong$':' Lam Dong',
                        r'Bn Tre|Bentre':'Ben Tre',
                       r'Qung':' Quang ',r'Bd$':' Binh Duong',
                        r'Hcm|Hm|H Chi Minh|Tphcm|huyen Chi Minh$':' Ho Chi Minh',
                        r'Thua Thien - Hue|Tha Thien Hu|[,] Hue$|thanh pho Hue$':' Thua Thien Hue',
                       r'I Lc':' Dai Loc ',r'Hi Duong':' Hai Duong',
                        r'Bc Lieu':' Bac Lieu ',r'Tian Giang|Tin Giang':' Tien Giang',
                       r'Nam Nh|Nam inh':' Nam Dinh',r'Binh Inh|Binh Nh$':' Binh Dinh',
                        r'Ls':'Lang Son',r'Thanh Haa':' Thanh Hoa',
                       r'Hu Giang':' Hau Giang',r'Qun 7':' Quan 7 ',r'Cn Tho|Tpct':' Can Tho',
                       r'Soctrang':' Soc Trang',r'Ng Thap|Ong Thap':' Dong Thap',
                        r'Ong Nai|Ng Nai':' Dong Nai ',r'In Bien':' Dien Bien',
                       r'Lam Ng$':' Lam Dong',r'[ ]A Lt':' Da Lat ',
                        r'Bc Kn':' Bac Kan ',r'Ak Nong|Daknong':' Dak Nong',
                       r'Gv|Go Vp':'Go Vap',r'Hi Phong':' Hai Phong ',
                        r'Ngh An':' Nghe An',r'U Liêu, thi xa Hng Linh':' Dau Lieu, thi xa Hong Linh',
                       r'Cm Ph':' Cam Pha ',r'Ninh Thun':' Ninh Thuan',
                        r'Binh Thun':' Binh Thuan',r'Cao Bng':' Cao Bang',
                       r'Bc Ninh':' Bac Ninh','Binh Thnh':'Binh Thanh','09':'9'}}, regex=True, inplace=True)
    df_ttin.replace({'Địa chỉ':{r'thanh pho Ben Tre|Tpbt':'TPBT', r'thanh pho Cao Bang':'TPCB',
    r'thanh pho Ba Ria, Ba Ria':'TPBR',
    '435/6A Kp3   Tan Thoi Thanh':'435/6A Kp3 ,phuong Tan Thoi Thanh',
    'Ap 10 Tan Thanh Dong':'Ap 10, Tan Thanh Dong','F4/14S Vinh Lc A':'F4/14S , Vinh Loc A',
    '80 Kp 3 Hiep Thanh':'80 Kp 3 ,Hiep Thanh',
    '34/102Atran Binh Trong phuong 1':'34/102A Tran Binh Trong, phuong 1',
    'phuong 22 Binh Thanh':'phuong 22, Binh Thanh','Phung Linh Trung':'Phuong Linh Trung',
    'Phung Cu Ong Lanh':'Phuong Cau Ong Lanh ','Phung An Phu Ong':'Phuong An Phu Ong',
    'Phung Tan Hung':'Phuong Tan Hung','Phung Thnh Xuan':'Phuong Thanh Xuan',
    'Phung Phu Thun':'Phuong Phu Thuan','Phuong1':'Phuong 1',
    'Tuyhoa':'Tuy Hoa','Song Bng':'Song Bang','Ba Ria - Vung Tau':'Ba Ria Vung Tau','Huyn':'Huyen'}}, regex=True, inplace=True)
    #  get tỉnh 
    df_ttin['Tỉnh'] = df_ttin['Địa chỉ'].str.split(',|-|[.]').str[-1]
    df_ttin['Tỉnh'] = df_ttin['Tỉnh'].str.strip('-|,|[ ]|.')
    df_ttin['Tỉnh'] =df_ttin['Tỉnh'].str.replace('thanh pho|tinh','', regex=True)
    list_province = df_branch.name.unique().tolist()
    df_ttin['Tỉnh']= df_ttin['Tỉnh'].str.strip('-|,|[ ]|.')
    df_ttin['Tỉnh'] = df_ttin['Tỉnh'].replace(r'\s+', ' ', regex=True)
    df_ttin['check_province'] = df_ttin['Tỉnh'].apply(lambda x: 
                             1 if ((x is not None) and (any(x.strip('-|,|[ ]|.')== s for s in list_province)==True)) else 0)
    df_ttin['Tỉnh'] = np.where(df_ttin['check_province']==1,df_ttin['Tỉnh'],df_ttin['name'])
    df_ttin.drop(['check_province','name'], axis=1, inplace=True)
    df_ttin['Địa chỉ'] = df_ttin.apply(lambda x: re.sub(x['Tỉnh'].strip('-|,|[ ]|.')+'$', '', x['Địa chỉ'].strip('-|,|[ ]|.'))
                      if x['Địa chỉ'].strip('-|,|[ ]|.').endswith(x['Tỉnh'].strip('-|,|[ ]|.')) else x['Địa chỉ'], axis=1)
    df_ttin['Địa chỉ'] = df_ttin['Địa chỉ'].str.strip('-|,|[ ]|.')
    df_ttin['Địa chỉ'] =df_ttin['Địa chỉ'].str.replace('thanh pho$|tinh$','', regex=True)
    df_ttin['Địa chỉ'] = df_ttin['Địa chỉ'].str.strip('-|,|[ ]|.')
    
    df_ttin['Huyện'] = df_ttin['Địa chỉ'].str.split('[.]|,|-').str[-1]
    df_ttin['Xã'] = df_ttin['Địa chỉ'].str.split('[.]|,|-').str[-2]
    
    df_ttin['Đường'] = df_ttin['Địa chỉ'].str.split('[.]|,|-').str[:-2]
    df_ttin['Đường'] = [try_join(l) for l in df_ttin['Đường']]
    df_ttin['Tỉnh'] = df_ttin['Tỉnh'].str.strip('-|,|[ ]|.')
    df_ttin['Huyện'] = df_ttin['Huyện'].str.strip('-|,|[ ]|.')
    df_ttin['Xã'] = df_ttin['Xã'].str.strip('-|,|[ ]|.')
    df_ttin['Đường'] = df_ttin['Đường'].str.strip('-|,|[ ]|.')
    df_ttin.replace({'Huyện':{r'TPBT':'thanh pho Ben Tre', r'TPCB':'thanh pho Cao Bang',
                              r'TPBR':'thanh pho Ba Ria','TP[ ]':''}}, regex=True, inplace=True)
    df_ttin.replace({'Xã':{'xa|phuong|thi tran':'','02':'2'}}, regex=True,inplace=True)
    df_ttin['Huyện']= df_ttin['Huyện'].str.replace('thanh pho|thi xa|quan|huyen|Quan|Qun','', regex=True)
    df_ttin.drop_duplicates(keep='first',inplace=True)
    df_ttin['Xã'] = df_ttin['Xã'].fillna(value='')
    df_ttin['Xã'] = df_ttin['Xã'].apply(lambda x: re.sub('(Phung+)(\d)', func, x))
    df_ttin['Huyện']= df_ttin['Huyện'].apply(lambda x: re.sub('(Q+)(\d)', func, x) )
    df_ttin['Xã'] = df_ttin['Xã'].apply(lambda x: re.sub('(P+)(\d)', func, x))
    df_ttin['Huyện'] = df_ttin['Huyện'].str.strip('-|,|[ ]|.')
    df_ttin['Xã'] = df_ttin['Xã'].str.strip('-|,|[ ]|.')
    df_ttin_cp = df_ttin.copy()
    df_ttin['Huyện'] = df_ttin['Huyện'].apply(lambda x: 'Quan '+ x if all(char.isdigit() for char in x)==True else x)
    df_ttin['Xã'] = df_ttin['Xã'].apply(lambda x: 'Phuong '+ x if all(char.isdigit() for char in x)==True else x)
    df_ttin['Tỉnh']= np.where(df_ttin['Địa chỉ']=='Hoa Long 3, An Chau, Chau Thanh',
                             'An Giang', df_ttin['Tỉnh'])
    df_ttin[df_ttin['Tên nhân viên'].str.contains('07928', na=False)]
    df_ttin.rename(columns={'Địa chỉ': 'Địa chỉ xử lý'}, inplace=True)
    df_ttin.rename(columns={'Địa chỉ gốc': 'Địa chỉ'}, inplace=True)
    # df_ttin['Tỉnh'] = np.where(df_ttin['Tỉnh'].isna(),
    #                                 df_ttin['name'],df_ttin['Tỉnh'])
    df_ttin['Tỉnh'] = df_ttin['Tỉnh'].str.strip('-|,|[ ]|.')
    df_ttin['Huyện'] = df_ttin['Huyện'].str.strip('-|,|[ ]|.')
    df_ttin['Xã'] = df_ttin['Xã'].str.strip('-|,|[ ]|.')
    df_ttin['Đường'] = df_ttin['Đường'].str.strip('-|,|[ ]|.')
    # df_ttin.drop(['name'], axis=1, inplace=True)
    df_ttin['Tỉnh'] = np.where((df_ttin['Tỉnh']=='Ho Chi Minh')& (df_ttin['Huyện']=='Ben Tre'), 
                                    'Ben Tre', df_ttin['Tỉnh'])
    df_ttin['Tỉnh'] = np.where((df_ttin['Tỉnh']=='An Giang')& (df_ttin['Huyện']=='Chau Thanh'), 
                                    'Ben Tre', df_ttin['Tỉnh'])
    df_ttin['Tên nhân viên'] = df_ttin['Tên nhân viên'].str.extract('(\d+)')
    df_ttin['Tên nhân viên']= df_ttin['Tên nhân viên'].astype(str)
    df_ttin['Tên nhân viên'] = df_ttin['Tên nhân viên'].apply(add_zero_to_beginning)
    df_ttin.drop_duplicates(inplace=True)
    df_ttin_dc = df_ttin.groupby(['Tên nhân viên','Tỉnh','Huyện','Xã','Ngày tạo','Tình Trạng NV'],as_index=False).agg({
        'province':'count'})[['Tên nhân viên','Tỉnh','Huyện','Xã','Ngày tạo','Tình Trạng NV']]
    df_ttin_dc['Tên nhân viên'] = df_ttin_dc['Tên nhân viên'].str.upper()
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    df_doanhthu_full = pd.read_sql("SELECT * FROM public.%s "%(config['feature_ptht']['table_salerevenue']), conn)
    conn.close()
    df_doanhthu_full.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_doanhthu_full.columns = ['Name', 'month', 'code', 'Doanh số', 'Doanh thu', 'Tên nhân viên']
    df_mapping_dt =df_doanhthu_full.merge(df_ttin_dc, on='Tên nhân viên', how='outer') 
    df_mapping_dt['Name'] = np.where(df_mapping_dt['Name'].isna(), df_mapping_dt['Tên nhân viên'],df_mapping_dt['Name'])
    df_mapping_dt.replace({'Xã':{'10 Chi Lang':'Chi Lang','230 Tam Quan':'Tam Quan'}}, regex=True, inplace=True)
    df_mapping_dt = df_mapping_dt.sort_values('month')
    df_mapping_dt = df_mapping_dt.sort_values(['Name', 'month', 'code', 'Doanh số', 'Doanh thu', 'Tên nhân viên',
           'Tỉnh', 'Huyện', 'Xã', 'Ngày tạo', 'Tình Trạng NV'], ascending=False)
    df_mapping_dt.drop_duplicates(subset=['month', 'code', 'Tên nhân viên',
           'Tỉnh', 'Huyện', 'Xã', 'Ngày tạo'], keep='first',inplace=True)
    df_mapping_dt['Tháng bắt đầu'] = df_mapping_dt['Ngày tạo'].dt.to_period("M")
    df_mapping_dt['Tháng tính lương'] = df_mapping_dt['month'].astype(str)
    df_mapping_dt['Tháng tính lương'] = pd.to_datetime(df_mapping_dt['Tháng tính lương'])
    df_mapping_dt_tlmin = df_mapping_dt.groupby(['Name'], as_index=False).agg({
    'Tháng tính lương':'min'})
    df_mapping_dt_tlmin.columns=['Name','Tháng lương min']
    df_mapping_dt_tlmax = df_mapping_dt.groupby(['Name'], as_index=False).agg({
    'Tháng tính lương':'max'})
    df_mapping_dt_tlmax.columns=['Name','Tháng lương max']
    df_mapping_dt = df_mapping_dt.merge(df_mapping_dt_tlmin, on='Name', how='outer')
    df_mapping_dt = df_mapping_dt.merge(df_mapping_dt_tlmax, on='Name', how='outer')
    df_mapping_dt_ntm = df_mapping_dt.groupby(['Name'], as_index=False).agg({
    'Ngày tạo':'max'})
    df_mapping_dt_ntm.columns=['Name','Ngày tạo max']
    df_mapping_dt = df_mapping_dt.merge(df_mapping_dt_ntm, on='Name', how='outer')
    df_mapping_dt['Tháng bắt đầu'] = df_mapping_dt['Tháng bắt đầu'].dt.to_timestamp('s').dt.strftime('%Y-%m-%d %H:%M:%S.000')
    df_mapping_dt['Tháng bắt đầu'] = pd.to_datetime(df_mapping_dt['Tháng bắt đầu'])
    df_mapping_dt['month'] = np.where(df_mapping_dt['month'].isna(),
                                      df_mapping_dt['Tháng bắt đầu'],df_mapping_dt['month'])
    df_mapping_dt['Ngày tạo'] = np.where(df_mapping_dt['Ngày tạo'].isna(),
                                      df_mapping_dt['Tháng lương min'],df_mapping_dt['Ngày tạo'])
    df_mapping_dt_filter = df_mapping_dt[((df_mapping_dt['Ngày tạo']==df_mapping_dt['Ngày tạo max'])&
                                        (df_mapping_dt['Tháng tính lương']>=df_mapping_dt['Ngày tạo']))|
                                        ((df_mapping_dt['Ngày tạo']<df_mapping_dt['Ngày tạo max'])&
                                        (df_mapping_dt['Tháng tính lương']<df_mapping_dt['Ngày tạo max']))]
    df_mapping_dt_filter = df_mapping_dt_filter[(df_mapping_dt_filter['Tháng tính lương']>=dt.datetime.strptime(start_date, '%Y-%m-%d'))
    &(df_mapping_dt_filter['Tháng tính lương']<dt.datetime.strptime(date, '%Y-%m-%d'))]
    df_mapping_dt_filter['Kỳ đầu tư'] = kydautu
    df_feature_doanhthu_grp = df_mapping_dt_filter.groupby(['Kỳ đầu tư','Tỉnh','Huyện','Xã'],as_index=False).agg({
    'Doanh số':'count','Doanh thu':'sum'})
    df_mapping_sale = df_mapping_dt.groupby(['Tên nhân viên','Tỉnh','Huyện','Xã','Ngày tạo','Tình Trạng NV',
                                            'Ngày tạo max'],as_index=False
                         ).agg({'Tháng lương max':'max'})
    df_mapping_sale['month'] = df_mapping_sale['Ngày tạo'].to_numpy().astype('datetime64[M]')
    df_mapping_sale['Tháng lương max'] = np.where(df_mapping_sale['Tháng lương max'].isna(),df_mapping_sale['Ngày tạo max'],
                                                 df_mapping_sale['Tháng lương max'])
    df_mapping_sale['Tháng lương max delta'] = df_mapping_sale['Tháng lương max'].apply(
        lambda x: x+relativedelta(months=1) if (x is pd.NaT) else x)
    df_mapping_sale['Tháng lương max delta'] = df_mapping_sale['Tháng lương max delta'].dt.date
    df_mapping_sale['Ngày nghỉ'] = np.where((df_mapping_sale['Ngày tạo']<df_mapping_sale['Ngày tạo max']),
    df_mapping_sale['Tháng lương max delta'],
    np.where((df_mapping_sale['Tình Trạng NV']=='Nghỉ Việc')&(df_mapping_sale['Ngày tạo']<dt.datetime.strptime('2022-12-01', '%Y-%m-%d')),
    dt.datetime.strptime('2022-12-01', '%Y-%m-%d').date(),
    np.where((df_mapping_sale['Tình Trạng NV']=='Nghỉ Việc')&(df_mapping_sale['Ngày tạo']>=dt.datetime.strptime('2022-12-01', '%Y-%m-%d')),
    dt.datetime.strptime('2023-08-23', '%Y-%m-%d').date(),(datetime.now() + relativedelta(years=1)).date())))
    df_mapping_sale['Ngày nghỉ'] = pd.to_datetime(df_mapping_sale['Ngày nghỉ'])
    df_mapping_sale_filter = df_mapping_sale[(df_mapping_sale['Ngày tạo'] < dt.datetime.strptime(date, '%Y-%m-%d'))
        &(df_mapping_sale['Ngày nghỉ'] >= dt.datetime.strptime(date, '%Y-%m-%d'))]
    df_nhanvien_dt_full = df_mapping_sale_filter.groupby(['Tỉnh','Huyện','Xã'],as_index=False).agg({'Tên nhân viên':'count'})
    df_nhanvien_dt_full.rename({'Tên nhân viên':'đại lý canh tô'},axis=1,inplace=True)
    
    df_daily_canhto = df_feature_doanhthu_grp.merge(df_nhanvien_dt_full, 
                                                    on=['Tỉnh','Huyện','Xã'], how='outer')
    df_daily_canhto.fillna(0, inplace=True)
    df_daily_canhto_filter = df_daily_canhto.copy()
    df_daily_canhto_filter.rename({'Tỉnh':'Tỉnh không dấu','Huyện':'Quận','Xã':'Phường',
                                   'Doanh số':'Số HĐ với KH'},axis=1,inplace=True)
    
    df_daily_canhto_filter = df_daily_canhto_filter.sort_values(['Tỉnh không dấu','Phường','Quận',
                                                                 'Kỳ đầu tư','đại lý canh tô'],ascending=False)
    df_daily_canhto_filter= df_daily_canhto_filter.drop_duplicates(['Tỉnh không dấu','Phường','Quận',
                                                                'Kỳ đầu tư'], keep='first')
    normalize_address('Không dấu',df_daily_canhto_filter)
    df_daily_canhto_filter = df_daily_canhto_filter.sort_values([ 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
           'Kỳ đầu tư', 'đại lý canh tô', 'Số HĐ với KH', 'Doanh thu'], ascending=False)
    df_daily_canhto_filter= df_daily_canhto_filter.drop_duplicates(['Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
           'Kỳ đầu tư'],keep='first')
    df_daily_canhto_filter['Kỳ đầu tư'] = kydautu
    return df_daily_canhto_filter
# date = '2023-09-01'
def process_tangtruongport(date,df_diachidoi,df_branch_province,config):
    """
        + Load dữ liệu tốc độ tăng trưởng port từ postgresql 177 - dwh_noc - public.tbl_tang_truong_port 
        + Chuẩn hoá dữ liệu địa chỉ, địa chỉ thay đổi sáp nhập 
        + Xử lý dữ liệu missing 
        + Tính trung bình tuổi và tốc độ khai thác port trên mỗi xã/phường 
    """
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    str_sql = "SELECT * FROM public.%s"% (config['tangtruong_port']['table_name'])
    df_tangtruong = pd.read_sql(str_sql, conn)
    conn.close()
    df_tangtruong.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_tangtruong.columns = ['Kỳ đầu tư', 'region', 'branch', 'district', 'ward', 'index_month',
           'TT_port', 'TT_portuse', 'TT_portfree', 'TT_portdie', 'TT_portmaintain','Tuổi']
    df_tangtruong.columns = ['Kỳ đầu tư', 'Vùng', 'Chi nhánh', 'Quận', 'Phường', 'index_month',
           'TT_port', 'TT_portuse', 'TT_portfree', 'TT_portdie', 'TT_portmaintain',
           'Tuổi']
    ####  nomalize xã/ phường, quận
    df_tangtruong['Quận'] = df_tangtruong['Quận'].apply(lambda x: unidecode.unidecode(str(x)))
    df_tangtruong['Phường'] = df_tangtruong['Phường'].apply(lambda x: unidecode.unidecode(str(x)))
    df_tangtruong.replace({'Quận' : { r'(H[.])': 'Huyen ', r'Q[.]': 'Quan ','Tp[.]|TP[.]|TP[ ]|Tp[ ]|Thanh Pho[ ]': \
                                                   'Thanh pho ', 'TX[.]|Thi Xa[ ]|T[.]Xa[ ]|TX[ ]':'Thi xa '}}, regex=True,inplace=True)
    df_tangtruong.replace({'Phường' : { r'T[.]T[.]|T[.]T[ ]|TT[.]|T[.]Tran[ ]|Thi Tran[ ]|TT[ ]|Thi tran[ ]': 'Thi tran '\
                                                     , r'TX[.]|TX[ ]|T[.]xa[ ]|T[.]Xa[ ]|Thi Xa[ ]': 'Thi xa ','P[.]': 'Phuong '\
                                                     , 'Xa[.]|Xa[ ]|xa[ ]|Xã[ ]|Xa\xa0':'Xa ','Khu Pho[ ]':'Khu pho ',
                                    'KCN[ ]':'Khu che xuat '}}, regex=True,inplace=True)
    df_tangtruong.replace({'Phường' : { r'(Thi tran[ ])': '', r'Phuong[ ]': '',r'Thi Xa[ ]': '','Xa[ ]': '','Ap[ ]': '', r'Huyen[ ]': ''}}, regex=True,inplace=True)
    df_tangtruong.replace({'Quận' : { r'(Quan[ ])': '', r'Huyen[ ]': '', r'huyen[ ]': '','Thi xa[ ]': '','Thanh pho[ ]': '','Xa[ ]': ''}}, regex=True,inplace=True)
    df_tangtruong['Phường'] = df_tangtruong['Phường'].str.lower()
    df_tangtruong['Quận'] = df_tangtruong['Quận'].str.lower()
    df_tangtruong.replace({'Chi nhánh' : { r'_': '', r'-': '', r'HNI': 'HN', r'SGN': 'HCM', r'hcm': 'HCM',
                                      r'hcm': 'HCM' ,r'HN0': 'HN',r'HCM0': 'HCM'}}, regex=True,inplace=True)
    df_tangtruong['Phường']= df_tangtruong['Phường'].apply(lambda x: str(x).strip())
    df_tangtruong['Quận']= df_tangtruong['Quận'].apply(lambda x: str(x).strip())
    df_tangtruong['Chi nhánh']= df_tangtruong['Chi nhánh'].apply(lambda x: str(x).strip())
    df_tangtruong_pivot = pd.pivot_table(df_tangtruong, values='TT_portuse', index=['Kỳ đầu tư','Tuổi','Vùng','Chi nhánh',
            'Quận','Phường'],columns=['index_month'], aggfunc=np.sum).reset_index()
    df_tangtruong_pivot.columns=['Kỳ đầu tư','Tuổi', 'Vùng', 'Chi nhánh', 'Quận', 'Phường', 'T1', 'T2', 'T3',
           'T4', 'T5']
    df_tt_port_fil_mode = df_tangtruong.groupby(['Phường', 'Quận', 'Chi nhánh'],\
                         as_index=False).agg({'TT_portuse':pd.Series.mode})
    df_tt_port_fil_mode = df_tangtruong.groupby(['Phường', 'Quận', 'Chi nhánh'],\
                         as_index=False).agg({'TT_portuse':pd.Series.mode})
    df_tt_port_fil_mode.columns = ['Phường', 'Quận', 'Chi nhánh', 'port_mode']
    df_tt_port_fil_mode['port_mode'] = df_tt_port_fil_mode['port_mode'].apply(lambda x: np.ceil(x.mean()))
    
    df_tt_port_map_ = df_tangtruong_pivot[df_tangtruong_pivot['Kỳ đầu tư']==kydautu].merge(df_tt_port_fil_mode, on=['Phường', 'Quận', 'Chi nhánh'], how='inner')
    df_tt_port_map_['T1'] = np.where(df_tt_port_map_['T1'].isna(),df_tt_port_map_['port_mode'],df_tt_port_map_['T1'])
    df_tt_port_map_['T2'] = np.where(df_tt_port_map_['T2'].isna(),df_tt_port_map_['port_mode'],df_tt_port_map_['T2'])
    df_tt_port_map_['T3'] = np.where(df_tt_port_map_['T3'].isna(),df_tt_port_map_['port_mode'],df_tt_port_map_['T3'])
    df_tt_port_map_['T4'] = np.where(df_tt_port_map_['T4'].isna(),df_tt_port_map_['port_mode'],df_tt_port_map_['T4'])
    df_tt_port_map_['T5'] = np.where(df_tt_port_map_['T5'].isna(),df_tt_port_map_['port_mode'],df_tt_port_map_['T5'])
    df_tt_port_map_['T1'] = np.where(df_tt_port_map_['Tuổi']<0, 0,df_tt_port_map_['T1'])
    df_tt_port_map_['T2'] = np.where(df_tt_port_map_['Tuổi']<0, 0,df_tt_port_map_['T2'])
    df_tt_port_map_['T3'] = np.where(df_tt_port_map_['Tuổi']<0, 0,df_tt_port_map_['T3'])
    df_tt_port_map_['T4'] = np.where(df_tt_port_map_['Tuổi']<0, 0,df_tt_port_map_['T4'])
    df_tt_port_map_['T5'] = np.where(df_tt_port_map_['Tuổi']<0, 0,df_tt_port_map_['T5'])
    df_tt_port_map_['Tuổi'] = np.where(df_tt_port_map_['Tuổi']<0, 0,df_tt_port_map_['Tuổi'])
    df_tt_port_map_['province'] = df_tt_port_map_['Chi nhánh'].str[:3]
    df_tt_port_map_['province']= np.where(df_tt_port_map_['province'].str.contains('HN')
                                          ,'HNI',df_tt_port_map_['province'])
    df_tt_port_map_= df_tt_port_map_.merge(df_branch_province,on='province', how='left')
    
    df_tt_port_map_=df_tt_port_map_[['Kỳ đầu tư', 'Phường', 'Quận','Vùng',  'name', 'T1', 'T2', 'T3',
           'T4', 'T5', 'Tuổi']]
    df_tt_port_map_.columns=['Kỳ đầu tư', 'Phường', 'Quận','Vùng',  'Tỉnh', 'T1', 'T2', 'T3',
           'T4', 'T5', 'Tuổi']
    normalize_address('Không dấu',df_tt_port_map_)
    
    df_tt_port_map_= df_tt_port_map_.groupby(['Kỳ đầu tư', 'Phường không dấu', 'Quận không dấu', 'Vùng',
           'Tỉnh không dấu'],as_index=False).agg({'T1':'max','T2':'max','T3':'max','T4':'max'
                                                              ,'T5':'max','Tuổi':'max'})
    df_tt_port_map_['Phường không dấu']= df_tt_port_map_['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_tt_port_map_['Phường không dấu'] = df_tt_port_map_['Phường không dấu'].str.title() 
    
    df_tt_port_map_['Quận không dấu']= df_tt_port_map_['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_tt_port_map_['Quận không dấu'] = df_tt_port_map_['Quận không dấu'].str.title() 
    
    df_tt_port_map_['Tỉnh không dấu']= df_tt_port_map_['Tỉnh không dấu'].str.strip('-|,|[ ]|.')
    df_tt_port_map_['Tỉnh không dấu'] = df_tt_port_map_['Tỉnh không dấu'].str.title()
    df_tt_port_map_ = df_tt_port_map_.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='left')
    df_tt_port_map_['Phường thay đổi']= np.where(df_tt_port_map_['Phường thay đổi'].isna(),
                                                      df_tt_port_map_['Phường không dấu'],
                                                      df_tt_port_map_['Phường thay đổi'])
    df_tt_port_map_['Quận thay đổi']= np.where(df_tt_port_map_['Quận thay đổi'].isna(),
                                                      df_tt_port_map_['Quận không dấu'],
                                                      df_tt_port_map_['Quận thay đổi'])
    df_tt_port_map_['Tỉnh thay đổi']= np.where(df_tt_port_map_['Tỉnh thay đổi'].isna(),
                                                      df_tt_port_map_['Tỉnh không dấu'],
                                                      df_tt_port_map_['Tỉnh thay đổi'])
    df_tt_port_map_= df_tt_port_map_[['Kỳ đầu tư','Phường thay đổi','Quận thay đổi','Tỉnh thay đổi',
    'Vùng','Tuổi', 'T1', 'T2', 'T3', 'T4', 'T5']]
    df_tt_port_map_.columns= ['Kỳ đầu tư','Phường không dấu','Quận không dấu','Tỉnh không dấu',
    'Vùng','Tuổi', 'T1', 'T2', 'T3', 'T4', 'T5']
    
    df_tt_port_map_ = df_tt_port_map_.groupby(['Kỳ đầu tư','Phường không dấu','Quận không dấu',
    'Tỉnh không dấu','Vùng'],as_index=False).agg({'Tuổi':'mean','T1':'mean',
    'T2':'mean','T3':'mean','T4':'mean','T5':'mean','Tuổi':'mean'})
    df_tt_port_map_.replace({'Vùng':{'Vung':'Vùng'}},regex=True,inplace=True)
    return df_tt_port_map_
def process_thiphan(date,df_branch_province,df_diachidoi,config):
    """
        + Load dữ liệu hạ tầng port trên hive: ftel_dwh_infra.infor_port_monthly
        + Chuẩn hoá dữ liệu địa chỉ, chi nhánh 
        + Summary thông tin port, portuse, portfree, portdie, portmaintain, device ở mức xã/phường 
    """
    start_date = (datetime.strptime(date,"%Y-%m-%d") - relativedelta(months=6)).strftime('%Y-%m-01')
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    
    sql_str = """select * from {}.{} where date>='{}'
                and date<'{}'""".format(config['infor_port_monthly']['dbs_output'],config['infor_port_monthly']['table_output'],start_date,date)
    df_info_port= spark.sql(sql_str)
    df_info_port_grp  = df_info_port.groupBy(['region','branch','district','ward','d']).agg(
    sum('port').alias('port'),sum('portuse').alias('portuse'),sum('portfree').alias('portfree')
    ,sum('portdie').alias('portdie')  ,sum('portmaintain').alias('portmaintain'), countDistinct('name').alias('num_device'))
    df_info_port_pd = df_info_port_grp.toPandas()
    df_info_port_pd['d'] = pd.to_datetime(df_info_port_pd['d'])
    
    df_info_port_pd['Kỳ đầu tư'] = kydautu
    df_info_port_pd = df_info_port_pd.sort_values(['region','branch','district','ward','Kỳ đầu tư','portuse'],ascending=False)
    df_info_port_pd = df_info_port_pd.drop_duplicates(['region','branch','district','ward','Kỳ đầu tư'],keep='first')
    df_info_port_pd.drop('d',axis=1, inplace=True)
    df_info_port_pd.columns= ['Vùng', 'Chi nhánh', 'Quận', 'Phường', 'port', 'portuse', 'portfree',
           'portdie', 'portmaintain', 'num_device', 'Kỳ đầu tư']
    normalize_address('Không dấu',df_info_port_pd)
    df_info_port_pd = df_info_port_pd.sort_values(['Vùng', 'Chi nhánh', 'Quận không dấu', 'Phường không dấu','Kỳ đầu tư','portuse'],ascending=False)
    df_info_port_pd = df_info_port_pd.drop_duplicates(['Vùng', 'Chi nhánh', 'Quận không dấu', 'Phường không dấu','Kỳ đầu tư']
                                                      ,keep='first')
    df_info_port_pd['province'] = df_info_port_pd['Chi nhánh'].str[:3]
    df_info_port_pd['province'] = df_info_port_pd['province'].str.upper()
    df_info_port_pd['province']= np.where(df_info_port_pd['province'].str.contains('HN'),'HNI',df_info_port_pd['province'])
    df_info_port_pd['province']= np.where(df_info_port_pd['province'].str.contains('SG'),'HCM',df_info_port_pd['province'])
    
    df_port_hh_full= df_info_port_pd.merge(df_branch_province,on='province', how='left')
    df_port_hh_full.rename({'name':'Tỉnh không dấu'},axis=1,inplace=True)
    df_port_hh_full['Chi nhánh'] = df_port_hh_full['Chi nhánh'].str.upper()
    df_port_hh_full.replace({'Chi nhánh' : {r'SGN': 'HCM','SG':'HCM', r'NTG':'KHA', r'HNI-0': 'HN',  
                                'HNI-':'HN','HCM-0':'HCM','HCM-':'HCM', r'HN0': 'HN',r'HCM0': 'HCM'}}, regex=True,inplace=True)
    df_port_hh_full.drop({'province'},axis=1,inplace=True)
    df_port_hh_full_ = df_port_hh_full.sort_values(['Vùng', 'Chi nhánh', 'Quận không dấu', 'Phường không dấu',
      'Kỳ đầu tư',  'Tỉnh không dấu', 'port', 'portuse', 'portfree', 'portdie', 'portmaintain', 'num_device',
           ],ascending=False)
    df_port_hh_full_ = df_port_hh_full_.drop_duplicates(['Vùng', 'Chi nhánh', 'Quận không dấu',
                     'Phường không dấu', 'Kỳ đầu tư',  'Tỉnh không dấu'],keep='first')
    df_port_hh_full_['Phường không dấu']= df_port_hh_full_['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_port_hh_full_['Phường không dấu'] = df_port_hh_full_['Phường không dấu'].str.title() 
    
    df_port_hh_full_['Quận không dấu']= df_port_hh_full_['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_port_hh_full_['Quận không dấu'] = df_port_hh_full_['Quận không dấu'].str.title() 
    
    df_port_hh_full_['Tỉnh không dấu']= df_port_hh_full_['Tỉnh không dấu'].str.strip('-|,|[ ]|.')
    df_port_hh_full_['Tỉnh không dấu'] = df_port_hh_full_['Tỉnh không dấu'].str.title()
    df_port_hh_full_ = df_port_hh_full_.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='left')
    df_port_hh_full_['Phường thay đổi']= np.where(df_port_hh_full_['Phường thay đổi'].isna(),
                                                      df_port_hh_full_['Phường không dấu'],
                                                      df_port_hh_full_['Phường thay đổi'])
    df_port_hh_full_['Quận thay đổi']= np.where(df_port_hh_full_['Quận thay đổi'].isna(),
                                                      df_port_hh_full_['Quận không dấu'],
                                                      df_port_hh_full_['Quận thay đổi'])
    df_port_hh_full_['Tỉnh thay đổi']= np.where(df_port_hh_full_['Tỉnh thay đổi'].isna(),
                                                      df_port_hh_full_['Tỉnh không dấu'],
                                                      df_port_hh_full_['Tỉnh thay đổi'])
    
    df_port_hh_full_= df_port_hh_full_[['Vùng', 'Phường thay đổi', 'Quận thay đổi',
    'Tỉnh thay đổi','port', 'portuse', 'portfree', 'portdie', 'portmaintain', 'num_device']]
    df_port_hh_full_.columns= ['Vùng', 'Phường không dấu','Quận không dấu',
    'Tỉnh không dấu', 'port', 'portuse', 'portfree', 'portdie', 'portmaintain', 'num_device']
    df_port_hh_full_.replace({'Vùng':{'Vung':'Vùng'}},regex=True, inplace=True)
    df_port_hh_full_ = df_port_hh_full_.groupby(['Vùng', 'Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu'],as_index=False).agg({'port':'sum','portuse':'sum','portfree':'sum','portdie':'sum','portmaintain':'sum','num_device':'sum'})
    return df_port_hh_full_
def process_doithu(df_diachidoi,config):
    """
        + Load dữ liệu về đối thủ từ postgresql 177 - dwh_noc - inf.tbl_isp_ap_info 
        + Chuẩn hoá dữ liệu địa chỉ, địa chỉ thay đổi sáp nhập 
    """
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    sql = """select * from inf.%s tiai where isp != 'FTEL';"""%(config['feature_ptht']['table_doithu'])
    df_dthu = pd.read_sql_query(sql, conn)
    df_dt_gp = df_dthu.groupby(['ward_ten','district_ten','province_ten'],as_index =False).agg({'bssid':'count'})
    df_dt_gp.columns=['Phường', 'Quận', 'Tỉnh', 'ap_doi_thu']
    df_dt_gp['Phường']= df_dt_gp['Phường'].apply(lambda x: unidecode.unidecode(str(x)))
    df_dt_gp['Quận']= df_dt_gp['Quận'].apply(lambda x: unidecode.unidecode(str(x)))
    df_dt_gp['Tỉnh']= df_dt_gp['Tỉnh'].apply(lambda x: unidecode.unidecode(str(x)))
    normalize_address('Không dấu',df_dt_gp)
    df_dt_gp = df_dt_gp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({'ap_doi_thu':'sum'})
    df_dt_gp_filter = df_dt_gp[(df_dt_gp['Quận không dấu']!='')&
                                    (df_dt_gp['Phường không dấu']!='')]
    df_dt_gp_filter.replace({'Phường không dấu':{'Phuong  ':'Phuong '}},regex=True,inplace=True)
    df_dt_gp_filter.replace({'Phường không dấu':{'Phuong Co Nhue 2':'Co Nhue 2',
    'Phuong My Dinh 2':'My Dinh 2',
    'Thi  Trang Bang':'Trang Bang',
    'Phuong Gia Tan 2':'Gia Tan 2',
    'Phuong Sai':'Sai'}},regex=True,inplace=True)
    df_dt_gp_filter.replace({'Quận không dấu':{'Ba Don,  Quang Trach':'Quang Trach',
    'Quan  ':'Quan ',
    'Phan Rang - Thap Cham':'Phan Rang-Thap Cham'}},regex=True,inplace=True)
    df_dt_gp_filter['Quận không dấu'] = df_dt_gp_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_dt_gp_filter['Phường không dấu'] = df_dt_gp_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_dt_gp_filter['Quận không dấu'] = np.where((df_dt_gp_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                        (df_dt_gp_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                'Thu Duc' ,df_dt_gp_filter['Quận không dấu'])
    df_dt_gp_filter_gp = df_dt_gp_filter.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
    'ap_doi_thu':'sum'})
    df_dt_gp_filter_gp= df_dt_gp_filter_gp.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='left')
    df_dt_gp_filter_gp['Phường thay đổi']= np.where(df_dt_gp_filter_gp['Phường thay đổi'].isna(),
                                                      df_dt_gp_filter_gp['Phường không dấu'],
                                                      df_dt_gp_filter_gp['Phường thay đổi'])
    df_dt_gp_filter_gp['Quận thay đổi']= np.where(df_dt_gp_filter_gp['Quận thay đổi'].isna(),
                                                      df_dt_gp_filter_gp['Quận không dấu'],
                                                      df_dt_gp_filter_gp['Quận thay đổi'])
    df_dt_gp_filter_gp['Tỉnh thay đổi']= np.where(df_dt_gp_filter_gp['Tỉnh thay đổi'].isna(),
                                                      df_dt_gp_filter_gp['Tỉnh không dấu'],
                                                      df_dt_gp_filter_gp['Tỉnh thay đổi'])
    df_dt_gp_filter_gp= df_dt_gp_filter_gp[['Phường thay đổi','Quận thay đổi',
                        'Tỉnh thay đổi','ap_doi_thu']]
    df_dt_gp_filter_gp.columns= ['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu','ap_doi_thu']
    df_dt_gp_filter_gp = df_dt_gp_filter_gp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
    'ap_doi_thu':'sum'})
    return df_dt_gp_filter_gp

def process_vanhanh(date,df_branch_province,df_diachidoi,config):
    """
        + Load dữ liệu về điểm vận hành POP từ postgresql 177 - dwh_noc - public.tbl_quality_pop
        + Mapping địa chỉ của POP: /mnt/projects-data/phat_trien_ha_tang/file_static/address_pop_mapping.csv
        + Chuẩn hoá dữ liệu về địa chỉ và tính trung bình điểm đánh giá POP ở mức xã/phường 
    """
    start_date = (datetime.strptime(date,"%Y-%m-%d") - relativedelta(months=6)).strftime('%Y-%m-01')
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                          ,config['dbs']['dwh_177_public']['password']
                                                         ,config['dbs']['dwh_177_public']['host']
                                                        ,config['dbs']['dwh_177_public']['port']
                                                        ,config['dbs']['dwh_177_public']['dbname']))
    sql = """select * from {} where month >='{}' and month < '{}'""".format(config['data_import']['tablename_qualitypop'],start_date, date)
    df_vh = pd.read_sql_query(sql, conn)
    df_vh.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_vh.columns = ['month', 'POP', 'province', 'avg_operation_pop', 'avg_quality_pop']
    df_vh['Kỳ đầu tư'] = kydautu
    df_vh = df_vh[df_vh['Kỳ đầu tư']!=''].sort_values(['POP','month'], ascending=False)
    
    df_address_pop = pd.read_csv(config['feature_ptht']['addresspop_path'])
    df_address_pop.columns = [ 'POP', 'ward', 'district', 'branch','province', 'region']
    df_address_pop.columns=['POP', 'Phường', 'Quận', 'branch', 'province', 'region']
    normalize_address('Không dấu',df_address_pop)
    df_vh=df_vh.merge(df_address_pop, on=['province','POP'], how='left')
    df_vh_grp = df_vh.groupby(['Kỳ đầu tư', 'Phường không dấu', 'Quận không dấu','province']
                              ,as_index=False).agg({'avg_operation_pop':'mean','avg_quality_pop':'mean'})
    df_vh_grp = df_vh_grp.merge(df_branch_province,on='province',how='left')
    df_vh_grp.drop('province',axis=1, inplace=True)
    df_vh_grp.rename({'name':'Tỉnh không dấu'},axis=1, inplace=True)
    
    
    df_vh_grp_filter = df_vh_grp[(~df_vh_grp['Quận không dấu'].isna())&
                                (~df_vh_grp['Phường không dấu'].isna())&
                                (~df_vh_grp['Tỉnh không dấu'].isna())]
    df_vh_grp_filter.replace({'Phường không dấu':{'Phuong  ':'Phuong '}},regex=True,inplace=True)
    df_vh_grp_filter.replace({'Phường không dấu':{'Phuong Co Nhue 2':'Co Nhue 2',
    'Phuong My Dinh 2':'My Dinh 2',
    'Thi  Trang Bang':'Trang Bang',
    'Phuong Gia Tan 2':'Gia Tan 2',
    'Phuong Sai':'Sai'}},regex=True,inplace=True)
    df_vh_grp_filter.replace({'Quận không dấu':{'Ba Don,  Quang Trach':'Quang Trach',
    'Quan  ':'Quan ','Lagi':'La Gi',
    'Phan Rang - Thap Cham':'Phan Rang-Thap Cham'}},regex=True,inplace=True)
    df_vh_grp_filter['Quận không dấu'] = df_vh_grp_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_vh_grp_filter['Phường không dấu'] = df_vh_grp_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_vh_grp_filter['Quận không dấu'] = np.where((df_vh_grp_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                        (df_vh_grp_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                'Thu Duc' ,df_vh_grp_filter['Quận không dấu'])
    df_vh_grp_filter_gp = df_vh_grp_filter.groupby(['Phường không dấu','Quận không dấu',
                   'Kỳ đầu tư','Tỉnh không dấu'],as_index=False).agg({
    'avg_operation_pop':'mean','avg_quality_pop':'mean'})
    df_vh_grp_filter_gp= df_vh_grp_filter_gp.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='left')
    
    df_vh_grp_filter_gp['Phường thay đổi']= np.where(df_vh_grp_filter_gp['Phường thay đổi'].isna(),
                                                      df_vh_grp_filter_gp['Phường không dấu'],
                                                      df_vh_grp_filter_gp['Phường thay đổi'])
    df_vh_grp_filter_gp['Quận thay đổi']= np.where(df_vh_grp_filter_gp['Quận thay đổi'].isna(),
                                                      df_vh_grp_filter_gp['Quận không dấu'],
                                                      df_vh_grp_filter_gp['Quận thay đổi'])
    df_vh_grp_filter_gp['Tỉnh thay đổi']= np.where(df_vh_grp_filter_gp['Tỉnh thay đổi'].isna(),
                                                      df_vh_grp_filter_gp['Tỉnh không dấu'],
                                                      df_vh_grp_filter_gp['Tỉnh thay đổi'])
    df_vh_grp_filter_gp= df_vh_grp_filter_gp[['Phường thay đổi','Quận thay đổi',
     'Tỉnh thay đổi','Kỳ đầu tư','avg_operation_pop','avg_quality_pop']]
    df_vh_grp_filter_gp.columns= ['Phường không dấu','Quận không dấu',
    'Tỉnh không dấu','Kỳ đầu tư','avg_operation_pop','avg_quality_pop']
    df_vh_grp_filter_gp = df_vh_grp_filter.groupby(['Phường không dấu','Quận không dấu',
                   'Kỳ đầu tư','Tỉnh không dấu'],as_index=False).agg({
    'avg_operation_pop':'mean','avg_quality_pop':'mean'})
    return df_vh_grp_filter_gp
def process_ticket(date,df_branch_province,config):
    """
        + Load dữ liệu ticket từ postgresql 177 - dwh_noc - report.dmt_device_ticket
        + Chuẩn hoá dữ liệu chi nhánh và mapping lấy tỉnh thành 
        + Tính số sự cố, downtime, thiết bị gặp sự cố, khách hàng bị ảnh hưởng ở mức độ tỉnh thành
    """
    start_date = (datetime.strptime(date,"%Y-%m-%d") - relativedelta(months=6)).strftime('%Y-%m-01')
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    sql_ticket = """select * from report.{}
                    where createddate>='{}' and createddate<'{}';""".format(config['feature_ptht']['table_ticket'],start_date,date)
    df_ticket = pd.read_sql_query(sql_ticket, conn)
    df_ticket['month'] = df_ticket['createddate'].dt.to_period('M')
    df_ticket['month'] = df_ticket['month'].astype(str)
    df_ticket['Chi nhánh'] = df_ticket['branch'].str.findall(r'\((.*?)\)').str[0]
    df_ticket['Kỳ đầu tư'] = kydautu
    df_ticket_grp = df_ticket.groupby(['province','Chi nhánh','Kỳ đầu tư','ticketcode'],as_index=False).agg({
    'name_device':'count','timetotal':'mean','cus_qty':'mean'})
    df_ticket_full = df_ticket_grp.groupby(['province','Chi nhánh','Kỳ đầu tư'],as_index=False).agg({
    'ticketcode':'nunique','timetotal':'sum','name_device':'sum','cus_qty':'sum'})
    df_ticket_full['province'] = np.where((df_ticket_full['province'].isna())|(df_ticket_full['province']==''),
                         df_ticket_full['Chi nhánh'], df_ticket_full['province'])
    df_ticket_full['province'] = df_ticket_full['province'].apply(lambda x:
                                    re.sub('\d', 'I', x))
    df_ticket_full.replace({'province':{'HNII':'HNI','HBN':'HBH','BRA':'BRU'}}
                           ,regex=True,inplace=True)
    df_ticket_full = df_ticket_full.merge(df_branch_province, on='province', how='inner')
    df_ticket_full.rename({'name':'Tỉnh'}, axis=1, inplace=True)
    df_ticket_full_ = df_ticket_full.groupby(['Tỉnh','Kỳ đầu tư'],as_index=False).agg({
        'ticketcode':'sum','timetotal':'sum','name_device':'sum','cus_qty':'sum'})
    return df_ticket_full_

def process_khachhang(date,df_diachidoi,config):
    """
        + Load dữ liệu địa chỉ khách hàng: ftel_dwh_isc.ds_customer_demographic (hive)
        + Load dữ liệu full toàn bộ khách hàng và tính số lượng khách hàng ở mức xã/phường: ftel_dm_opt_customer.stag_idatapay_daily (hive)
        + Load dữ liệu khách hàng rời mạng và tính số lượng khách hàng rời mạng ở mức xã/phường: ftel_dm_opt_customer.stag_idatapay_daily (hive) 
        + Load dữ liệu khách hàng nợ cước và tính số lượng khách hàng nợ cước ở mức xã/phường: ftel_dm_opt_customer.stag_idatapay_daily (hive) 
        + Load dữ liệu checklist và tính số lượng checklist ở mức xã/phường: ftel_dm_opt_customer.stag_idatapay_daily (hive) 
        + Chuẩn hoá dữ liệu địa chỉ, địa chỉ thay đổi sáp nhập và mapping tất cả thông tin về khách hàng về mức xã/phường 
    """
    start_date = (datetime.strptime(date,"%Y-%m-%d") - relativedelta(months=6)).strftime('%Y-%m-01')
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    df_infographic = spark.sql("""SELECT ct.contract, d.ward as ward_addr, d.district as district_addr,
            ct.province as province_addr
            FROM ftel_dwh_isc.{} d LEFT JOIN ftel_dwh_isc.{} ct 
            ON d.contract = ct.contract""".format(config['feature_ptht']['table_demographic'],
                                                  config['feature_ptht']['table_contract'])).cache()
    #  khách hàng 
    spark.sql('REFRESH TABLE ftel_dm_opt_customer.{}'.format(config['feature_ptht']['table_idatapay']))
    str_slq = """SELECT  contract
            FROM ftel_dm_opt_customer.{}
            WHERE d ='{}'""".format(config['feature_ptht']['table_idatapay'],date)
    df_khg = spark.sql(str_slq)
    df_khg = df_khg.join(df_infographic,on='contract', how='left')
    df_khg = df_khg.withColumn('Kỳ đầu tư',lit(kydautu))
    df_khg_gp  = df_khg.groupBy(['ward_addr','district_addr','province_addr','Kỳ đầu tư']).agg(
            countDistinct('contract').alias('number_khg'))
    df_khg_pd = df_khg_gp.toPandas()
    df_khg_pd.columns = ['Phường', 'Quận', 'Tỉnh', 'Kỳ đầu tư','number_khg']
    normalize_address('Không dấu', df_khg_pd)
    df_khg_pd = df_khg_pd.groupby(['Tỉnh không dấu', 'Quận không dấu','Phường không dấu',
      'Kỳ đầu tư'],as_index=False).agg({'number_khg':'max'})
    #  rời mạng
    list_month =  []
    for i in range(6):
        start_month = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(months=i)).strftime('%Y-%m-01')
        list_month.append(start_month)
    spark.sql('REFRESH TABLE ftel_dm_opt_customer.{}'.format(config['feature_ptht']['table_idatapay']))
    str_slq = """SELECT  *
                FROM ftel_dm_opt_customer.{}
                WHERE net_status in ('Da cham dut hop dong','Chu thue bao di vang')
                and d  in ('{}')""".format(config['feature_ptht']['table_idatapay'],
                                           ', '.join(z for z in list_month).replace(", ","','"))
    df_roimang = spark.sql(str_slq)
    df_roimang = df_roimang.join(df_infographic,on='contract', how='left')
    df_roimang = df_roimang.withColumn("month", f.trunc("d", "month"))
    df_roimang_grp = df_roimang.groupBy(['month','province_addr','district_addr','ward_addr']).agg(
                countDistinct('contract').alias('roi_mang')).cache()
    df_roimang_grp_ = df_roimang_grp.groupBy(['province_addr','district_addr','ward_addr']).agg(
        mean('roi_mang').alias('roi_mang'))
    df_roimang_full = df_roimang_grp_.withColumn('Kỳ đầu tư',lit(kydautu))
    df_roimang_full_pd = df_roimang_full.toPandas()
    df_roimang_full_pd.columns = ['Tỉnh', 'Quận', 'Phường', 'roi_mang', 'Kỳ đầu tư']
    normalize_address('Không dấu', df_roimang_full_pd)
    df_roimang_full_pd = df_roimang_full_pd.groupby(['Tỉnh không dấu', 'Quận không dấu','Phường không dấu',
          'Kỳ đầu tư'],as_index=False).agg({'roi_mang':'max'})
    
    #  nợ cước 
    spark.sql('REFRESH TABLE ftel_dm_opt_customer.{}'.format(config['feature_ptht']['table_idatapay']))
    str_slq = """SELECT  *
                FROM ftel_dm_opt_customer.{}
                WHERE net_status = 'Ngung vi ly do thanh toan'
                and d  in ('{}')""".format(config['feature_ptht']['table_idatapay'],
                                           ', '.join(z for z in list_month).replace(", ","','"))
    df_nocuoc = spark.sql(str_slq)
    df_nocuoc = df_nocuoc.join(df_infographic,on='contract', how='left')
    df_nocuoc = df_nocuoc.withColumn("month", f.trunc("d", "month"))
    df_nocuoc_grp = df_nocuoc.groupBy(['month','province_addr','district_addr','ward_addr']).agg(
                countDistinct('contract').alias('no_cuoc')).cache()
    df_nocuoc_grp_ = df_nocuoc_grp.groupBy(['province_addr','district_addr','ward_addr']).agg(
        mean('no_cuoc').alias('no_cuoc'))
    df_nocuoc_full = df_nocuoc_grp_.withColumn('Kỳ đầu tư',lit(kydautu))
    df_nocuoc_full_pd = df_nocuoc_full.toPandas()
    df_nocuoc_full_pd.columns = ['Tỉnh', 'Quận', 'Phường', 'no_cuoc', 'Kỳ đầu tư']
    normalize_address('Không dấu', df_nocuoc_full_pd)
    df_nocuoc_full_pd = df_nocuoc_full_pd.groupby(['Tỉnh không dấu', 'Quận không dấu','Phường không dấu',
          'Kỳ đầu tư'],as_index=False).agg({'no_cuoc':'max'})

    # checklist 
    srt_sql = """
            SELECT c.cl_create_date,c.contract,c.province,d.ward, d.district
            FROM ftel_dwh_isc.{}  c
            LEFT JOIN ftel_dwh_isc.{} d
            ON c.contract = d.contract
            WHERE c.cl_create_date>=  '{}' and c.cl_create_date< '{}'
            """.format(config['feature_ptht']['table_checklist'],
                       config['feature_ptht']['table_demographic'],start_date,date)
    df_checklist =  spark.sql(srt_sql).cache()
    df_checklist = df_checklist.withColumn('Kỳ đầu tư',lit(kydautu))
    df_checklist_grp = df_checklist.groupBy(['ward','district','province','Kỳ đầu tư'])\
                                .agg(count('contract').alias('num_checlist'))
    df_checklist_pd = df_checklist_grp.toPandas()
    df_checklist_pd.columns = ['Phường', 'Quận', 'Tỉnh', 'Kỳ đầu tư', 'num_checlist']
    normalize_address('Không dấu', df_checklist_pd)
    df_checklist_pd.replace({'Tỉnh không dấu':{'Vung Tau':'Ba Ria Vung Tau'
    ,'Nha Trang': 'Khanh Hoa'
    ,'Hue':'Thua Thien Hue'}}, regex=True, inplace=True)
    df_checklist_pd = df_checklist_pd.groupby(['Tỉnh không dấu', 'Quận không dấu','Phường không dấu',
          'Kỳ đầu tư'],as_index=False).agg({'num_checlist':'max'})
    
    df_info_khg = df_khg_pd.merge(df_roimang_full_pd, on=['Tỉnh không dấu', 'Quận không dấu',
                      'Phường không dấu', 'Kỳ đầu tư'], how='outer')
    df_info_khg = df_info_khg.merge(df_nocuoc_full_pd, on=['Tỉnh không dấu', 'Quận không dấu',
                      'Phường không dấu', 'Kỳ đầu tư'], how='outer')
    df_info_khg.replace({'Tỉnh không dấu':{'Vung Tau':'Ba Ria Vung Tau'
    ,'Nha Trang': 'Khanh Hoa'
    ,'Hue':'Thua Thien Hue'}}, regex=True, inplace=True)

    df_info_khg = df_info_khg.merge(df_checklist_pd, on=['Tỉnh không dấu', 'Quận không dấu','Phường không dấu',
          'Kỳ đầu tư'], how='left')
    df_info_khg['roi_mang'] = pd.to_numeric(df_info_khg['roi_mang'], errors='coerce')
    df_info_khg['no_cuoc'] = pd.to_numeric(df_info_khg['no_cuoc'], errors='coerce')
    df_info_cus_filter = df_info_khg[(~df_info_khg['Quận không dấu'].isna())&
                                (~df_info_khg['Phường không dấu'].isna())&
                                (~df_info_khg['Tỉnh không dấu'].isna())]
    df_info_cus_filter.replace({'Phường không dấu':{'Phuong  ':'Phuong '}},regex=True,inplace=True)
    df_info_cus_filter.replace({'Phường không dấu':{'Phuong Co Nhue 2':'Co Nhue 2',
    'Phuong My Dinh 2':'My Dinh 2',
    'Thi  Trang Bang':'Trang Bang',
    'Phuong Gia Tan 2':'Gia Tan 2',
    'Phuong Sai':'Sai'}},regex=True,inplace=True)
    df_info_cus_filter.replace({'Quận không dấu':{'Ba Don,  Quang Trach':'Quang Trach',
    'Quan  ':'Quan ','Lagi':'La Gi',
    'Phan Rang - Thap Cham':'Phan Rang-Thap Cham',
    'Phan Rang - Tc':'Phan Rang - Thap Cham'}},regex=True,inplace=True)
    df_info_cus_filter['Quận không dấu'] = df_info_cus_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_info_cus_filter['Phường không dấu'] = df_info_cus_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_info_cus_filter['Quận không dấu'] = np.where((df_info_cus_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                        (df_info_cus_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                'Thu Duc' ,df_info_cus_filter['Quận không dấu'])
    df_info_cus_filter = df_info_cus_filter.groupby(['Phường không dấu','Quận không dấu',
                   'Kỳ đầu tư','Tỉnh không dấu'],as_index=False).agg({
                    'number_khg':'max','roi_mang':'max','no_cuoc':'max','num_checlist':'max'})
    df_info_cus_filter_gp= df_info_cus_filter.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='left')
    df_info_cus_filter_gp['Phường thay đổi']= np.where(df_info_cus_filter_gp['Phường thay đổi'].isna(),
                                                      df_info_cus_filter_gp['Phường không dấu'],
                                                      df_info_cus_filter_gp['Phường thay đổi'])
    df_info_cus_filter_gp['Quận thay đổi']= np.where(df_info_cus_filter_gp['Quận thay đổi'].isna(),
                                                      df_info_cus_filter_gp['Quận không dấu'],
                                                      df_info_cus_filter_gp['Quận thay đổi'])
    df_info_cus_filter_gp['Tỉnh thay đổi']= np.where(df_info_cus_filter_gp['Tỉnh thay đổi'].isna(),
                                                      df_info_cus_filter_gp['Tỉnh không dấu'],
                                                      df_info_cus_filter_gp['Tỉnh thay đổi'])
    df_info_cus_filter_gp= df_info_cus_filter_gp[['Phường thay đổi','Quận thay đổi',
     'Tỉnh thay đổi','Kỳ đầu tư','number_khg','roi_mang','no_cuoc','num_checlist']]
    df_info_cus_filter_gp.columns= ['Phường không dấu','Quận không dấu',
    'Tỉnh không dấu','Kỳ đầu tư','total_customer','total_roimang','total_nocuoc','num_checlist']
    df_info_cus_filter_gp = df_info_cus_filter_gp.groupby(['Phường không dấu','Quận không dấu',
                   'Kỳ đầu tư','Tỉnh không dấu'],as_index=False).agg({
                    'total_customer':'max','total_roimang':'max','total_nocuoc':'max','num_checlist':'max'})
    df_info_cus_filter_gp.columns = ['Phường không dấu', 'Quận không dấu', 'Kỳ đầu tư', 'Tỉnh không dấu',
           'number_khg', 'KHG_RM', 'number_nocuoc', 'num_checlist']
    df_info_cus_filter_gp = df_info_cus_filter_gp[(df_info_cus_filter_gp['Phường không dấu']!='')&
    (df_info_cus_filter_gp['Phường không dấu']!="' '")]
    return df_info_cus_filter_gp
def process_nganhang(kydautu,config):
    """
    Load, chuẩn hoá dữ liệu địa chỉ ngân hàng: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/ngan_hang.parquet
    """
    df_nganhang = spark.read.parquet(config['data_import']['nganhang_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_nganhang)
    df_nganhang_grp=df_nganhang.groupby(['Quận có dấu', 'Phường có dấu', 'Tỉnh có dấu',
                           'Quận không dấu','Phường không dấu','Tỉnh không dấu'],as_index=False).agg({'so_ngan_hang':'sum'})
    df_nganhang_grp['Phường có dấu'] = np.where(df_nganhang_grp['Phường có dấu']=='Nan',
               df_nganhang_grp['Quận có dấu'],df_nganhang_grp['Phường có dấu'])
    df_nganhang_grp['Phường không dấu'] = np.where(df_nganhang_grp['Phường không dấu']=='Nan',
               df_nganhang_grp['Quận không dấu'],df_nganhang_grp['Phường không dấu'])
    return df_nganhang_grp
def process_thunhap(date,config):
    """
        Load, chuẩn hoá dữ liệu địa chỉ bình quân chi tiêu: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/chi_tieu.parquet
    """
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    df_thunhap = spark.read.parquet(config['data_import']['chitieu_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    df_thunhap= df_thunhap[(~df_thunhap.Quận.str.contains(
        'Thành phố Hà Nội|Thành phố Hải Phòng|Thành phố Đà Nẵng|Thành phố Hồ Chí Minh|Thành phố Cần Thơ|Tỉnh'))]
    df_thunhap['Quận'] = np.where((df_thunhap['Quận'].isin(['Quận 2','Quận 9']))&
                                        (df_thunhap['Tỉnh']=='Thành phố Hồ Chí Minh'),
                                                'Quận Thủ Đức' ,df_thunhap['Quận'])
    normalize_address('Có dấu',df_thunhap)
    df_thunhap['Bình quân chi tiêu'] = df_thunhap['Bình quân chi tiêu'].astype(float)
    df_thunhap = df_thunhap.groupby(['Tỉnh có dấu','Quận có dấu','Tỉnh không dấu',
                'Quận không dấu'],as_index=False).agg({'Bình quân chi tiêu':'mean'})
    df_thunhap.rename({'Bình quân chi tiêu':'Thu nhập'},axis=1,inplace=True)
    return df_thunhap
def preprocess_dienmay(df_diachidoi,config):
    """
        Load, chuẩn hoá dữ liệu địa chỉ shop điện máy và tính tổng shop: /mnt/projects-data/phat_trien_ha_tang/file_static/shop_dien_may.csv
    """
    # conn = pg.connect("postgresql://dwh_noc:fNSdAnGVEA23NjTTPvRv@172.27.11.177:6543/dwh_noc")
    # df_dm = pd.read_sql("select * from  public.tbl_shop_info", conn) => data shop điện máy crawler
    # conn.close()
    #  không dùng data crawler do không check được danh sách thay đổi trên web, địa chỉ cập nhật liên tục và không khớp với địa chỉ cũ để update
    df_dm = pd.read_csv(config['feature_ptht']['shopdienmay_path'])
    df_dm = df_dm[['address','store', 'province', 'district', 'ward']]
    df_dm.columns=[ 'address','store', 'Tỉnh', 'Quận', 'Phường']
    df_dm_grp = df_dm.groupby(['Phường','Quận','Tỉnh'],as_index=False).agg({'store':'count'})
    df_dm_grp.columns = ['Phường', 'Quận', 'Tỉnh', 'Số_shop']
    normalize_address('Không dấu',df_dm_grp)
    df_dm_grp.replace({'Quận không dấu':{'^Phan Rang Thap Cham$|^Phan Rang$|^Thap Cham$':'Phan Rang-Thap Cham'
                                        }},regex=True,inplace=True)
    df_dm_grp_filter = df_dm_grp[(df_dm_grp['Quận không dấu']!='')&
                                    (df_dm_grp['Phường không dấu']!='')]
    df_dm_grp_filter.replace({'Phường không dấu':{'Phuong  ':'Phuong '}},regex=True,inplace=True)
    df_dm_grp_filter.replace({'Phường không dấu':{'Phuong Co Nhue 2':'Co Nhue 2',
    'Phuong My Dinh 2':'My Dinh 2',
    'Thi  Trang Bang':'Trang Bang',
    'Phuong Gia Tan 2':'Gia Tan 2',
    'Phuong Sai':'Sai'}},regex=True,inplace=True)
    df_dm_grp_filter.replace({'Quận không dấu':{'Ba Don,  Quang Trach':'Quang Trach',
    'Quan  ':'Quan ',
    'Phan Rang - Thap Cham':'Phan Rang-Thap Cham'}},regex=True,inplace=True)
    df_dm_grp_filter['Quận không dấu'] = df_dm_grp_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_dm_grp_filter['Phường không dấu'] = df_dm_grp_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_dm_grp_filter['Quận không dấu'] = np.where((df_dm_grp_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                        (df_dm_grp_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                'Thu Duc' ,df_dm_grp_filter['Quận không dấu'])
    df_dm_grp_filter_gp = df_dm_grp_filter.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
    'Số_shop':'sum'})
    df_dm_grp_filter_gp = df_dm_grp_filter_gp.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='outer')
    df_dm_grp_filter_gp['Phường thay đổi']= np.where(df_dm_grp_filter_gp['Phường thay đổi'].isna(),
                                                      df_dm_grp_filter_gp['Phường không dấu'],
                                                      df_dm_grp_filter_gp['Phường thay đổi'])
    df_dm_grp_filter_gp['Quận thay đổi']= np.where(df_dm_grp_filter_gp['Quận thay đổi'].isna(),
                                                      df_dm_grp_filter_gp['Quận không dấu'],
                                                      df_dm_grp_filter_gp['Quận thay đổi'])
    df_dm_grp_filter_gp['Tỉnh thay đổi']= np.where(df_dm_grp_filter_gp['Tỉnh thay đổi'].isna(),
                                                      df_dm_grp_filter_gp['Tỉnh không dấu'],
                                                      df_dm_grp_filter_gp['Tỉnh thay đổi'])
    df_dm_grp_filter_gp= df_dm_grp_filter_gp[['Phường thay đổi','Quận thay đổi',
                        'Tỉnh thay đổi','Số_shop']]
    df_dm_grp_filter_gp.columns= ['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu','Số_shop']
    df_dm_grp_filter_gp = df_dm_grp_filter_gp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
    'Số_shop':'sum'})
    return df_dm_grp_filter_gp
def process_sanbay(config):
    """
        Load , chuẩn hoá dữ liệu địa chỉ dữ liệu sân bay: /mnt/projects-data/phat_trien_ha_tang/file_static/san_bay.csv
    """
    df_sanbay = pd.read_csv(config['feature_ptht']['sanbay_path'])
    df_sanbay_grp = df_sanbay.groupby(['Thành_phố','Tỉnh'],as_index=False).agg({'Tên_sân_bay':'count'})
    df_sanbay_grp.columns=['Quận', 'Tỉnh', 'số_sân_bay']
    normalize_address('không dấu', df_sanbay_grp)
    df_sanbay_grp.replace({'Quận không dấu':{'Hcm':'Tan Binh','Ha Noi':'Soc Son',
          'Can Tho':'Binh Thuy','Da Nang':'Hai Chau'}},regex=True, inplace=True)
    return df_sanbay_grp
def process_cangbien(config):
    """
        Load , chuẩn hoá dữ liệu địa chỉ dữ liệu cảng biển : /mnt/projects-data/phat_trien_ha_tang/file_static/cang_bien.csv
    """
    df_cangbien = pd.read_csv(config['feature_ptht']['cangbien_path'])
    df_cangbien['Tên_cảng'].replace('Côn Đảo','Bến Đầm',regex=True, inplace=True)
    df_cangbien['addr_cangbien'] = 'Cảng '+ df_cangbien['Tên_cảng'] + ', '+df_cangbien['Địa_phận_tỉnh']
    df_cangbien_grp = df_cangbien.groupby('Địa_phận_tỉnh',as_index=False).agg({'Tên_cảng':'count'})
    df_cangbien_grp.columns=['Tỉnh không dấu','Số_cảng']
    return df_cangbien_grp
def process_gaduong(config):
    """
        Load , chuẩn hoá dữ liệu địa chỉ dữ liệu sân ga :/mnt/projects-data/phat_trien_ha_tang/file_static/ga_duong_sat.csv
    """
    df_gaduong_full = pd.read_csv(config['feature_ptht']['duongsat_path'])
    df_gaduong_full['addr_ga'] = 'Ga '+df_gaduong_full['Tên_ga']+', '+df_gaduong_full['Tỉnh']
    df_gaduong_grp = df_gaduong_full.groupby('Tỉnh',as_index=False).agg({'Tên_ga':'count'})
    df_gaduong_grp.columns=['Tỉnh không dấu','Số_duongga']
    return df_gaduong_grp
    
def process_caotoc(config):
    """
        Load và tính tổng cao tốc ở các tỉnh: /mnt/projects-data/phat_trien_ha_tang/file_static/cao_toc.csv
    """
    df_caotoc_prep = pd.read_csv(config['feature_ptht']['caotoc_path'])
    df_caotoc_grp= df_caotoc_prep.groupby('province',as_index=False).agg({'Tên_tuyến':'count'})
    df_caotoc_grp.columns=['Tỉnh không dấu', 'số_caotoc']
    return df_caotoc_grp
def process_bienvien(kydautu,config):
    """
        + Load và chuẩn hoá dữ liệu địa chỉ bệnh viện: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/benh_vien.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ trung tâm y tế: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/trung_tam_y_te.parquet
    """
    df_bienvien = spark.read.parquet(config['data_import']['benhvien_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_bienvien)
    df_bienvien_grp = df_bienvien.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Tên đơn vị':'count'})
    df_bienvien_grp.columns= ['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu', 'Số_bệnh_viện']
    df_csyt = spark.read.parquet(config['data_import']['yte_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_csyt)
    df_csyt_grp = df_csyt.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Tên đơn vị':'count'})
    df_csyt_grp.columns= ['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu', 'Số_cơ_sở_y_tế']
    df_bienvien_grp = df_bienvien_grp.merge(df_csyt_grp,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'], how='outer')
    return df_bienvien_grp
def process_truonghoc(kydautu,config):
    """
        + Load và chuẩn hoá dữ liệu địa chỉ trường tiểu học: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_tieu_hoc.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ trường trung học: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_trung_hoc_co_so.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ trường trung học phổ thông: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_trung_hoc_pho_thong.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ trường cao đẳng: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_cao_dang.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ trường đại học: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_dai_hoc.parquet
        + Mapping các thông tin trường học và xử lý dữ liệu missing 
    """
    df_school_th = spark.read.parquet(config['data_import']['tieuhoc_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_school_th)
    df_school_th_grp = df_school_th.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Tên trường':'count'})
    df_school_th_grp.columns= ['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu', 'Số_trường_tiểu_học']
    
    df_school_thcs = spark.read.parquet(config['data_import']['trunghoccoso_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_school_thcs)
    df_school_thcs_grp = df_school_thcs.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Tên trường':'count'})
    df_school_thcs_grp.columns= ['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu', 'Số_trường_trung_học']
    
    df_school_thpt = spark.read.parquet(config['data_import']['trunghocphothong_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_school_thpt)
    df_school_thpt_grp = df_school_thpt.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Tên trường':'count'})
    df_school_thpt_grp.columns= ['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu', 'Số_trường_phổ_thông']
    
    df_school_cao_dang = spark.read.parquet(config['data_import']['truongcaodang_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_school_cao_dang)
    df_school_cao_dang_grp = df_school_cao_dang.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Tên trường':'count'})
    df_school_cao_dang_grp.columns= ['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu', 'Số_trường_cao_đẳng']
    
    df_school_dai_hoc = spark.read.parquet(config['data_import']['truongdaihoc_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_school_dai_hoc)
    df_school_dai_hoc_grp = df_school_dai_hoc.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Tên trường':'count'})
    df_school_dai_hoc_grp.columns= ['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu', 'Số_trường_đại_học']
    
    df_school_grp = df_school_th_grp.merge(df_school_thcs_grp,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_school_grp = df_school_grp.merge(df_school_thpt_grp,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_school_grp = df_school_grp.merge(df_school_cao_dang_grp,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_school_grp = df_school_grp.merge(df_school_dai_hoc_grp,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_school_grp['Phường có dấu'] =  np.where(df_school_grp['Phường có dấu']=='Nan',
                                               df_school_grp['Quận có dấu'],df_school_grp['Phường có dấu'])
    df_school_grp['Phường không dấu'] =  np.where(df_school_grp['Phường không dấu']=='Nan',
                                               df_school_grp['Quận không dấu'],df_school_grp['Phường không dấu'])
    return df_school_grp
def process_doanhnghiep(kydautu,config):
    """
        +Load và chuẩn hoá dữ liệu địa chỉ doanh nghiệp: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep.parquet
        +Load và chuẩn hoá dữ liệu địa chỉ doanh nghiệp vốn nước ngoài: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_co_von_nuoc_ngoai.parquet
        +Load và chuẩn hoá dữ liệu địa chỉ doanh nghiệp xuất nhập khẩu: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_co_hoat_dong_xuat_nhap_khau.parquet
        +Load và chuẩn hoá dữ liệu địa chỉ doanh nghiệp tư nhân: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_tu_nhan.parquet
        +Load và chuẩn hoá dữ liệu địa chỉ khách sạn: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/khach_san.parquet
        +Load và chuẩn hoá dữ liệu địa chỉ khách sạn tư nhân: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/khach_san_tu_nhan.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ doanh nghiệp vừa & nhỏ: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_vua_va_nho.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ doanh nghiệp công nghệ thông tin: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_cong_nghe_thong_tin.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ doanh nghiệp có trang thông tin điện tử: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_co_trang_thong_tin_dien_tu.parquet
        + Mapping các thông tin doanh nghiệp và xử lý dữ liệu missing 
    """
    
    df_doanhnghiep = spark.read.parquet(config['data_import']['doanhnghiep_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanhnghiep)
    df_doanhnghiep= df_doanhnghiep.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_doanh_nghiep':'sum'})
    df_doanhnghiep= df_doanhnghiep[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_doanh_nghiep']]
    
    df_doanhnghiep_vnn = spark.read.parquet(config['data_import']['doanhnghiepnuocngoai_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanhnghiep_vnn)
    df_doanhnghiep_vnn= df_doanhnghiep_vnn.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_doanh_nghiep_von_nuoc_ngoai':'sum'})
    df_doanhnghiep_vnn= df_doanhnghiep_vnn[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_doanh_nghiep_von_nuoc_ngoai']]
    
    df_doanhnghiep_xnk = spark.read.parquet(config['data_import']['doanhnghiepxuatnhapkhau_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanhnghiep_xnk)
    df_doanhnghiep_xnk= df_doanhnghiep_xnk.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_doanh_nghiep_xuat_nhap_khau':'sum'})
    df_doanhnghiep_xnk= df_doanhnghiep_xnk[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_doanh_nghiep_xuat_nhap_khau']]
    
    df_doanhnghiep_kdct = spark.read.parquet(config['data_import']['doanhnghieptunhan_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanhnghiep_kdct)
    df_doanhnghiep_kdct= df_doanhnghiep_kdct.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_kinh_doanh_ca_the':'sum'})
    df_doanhnghiep_kdct= df_doanhnghiep_kdct[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_kinh_doanh_ca_the']]

    df_doanhnghiep_ks = spark.read.parquet(config['data_import']['khachsan_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanhnghiep_ks)
    df_doanhnghiep_ks= df_doanhnghiep_ks.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_doanh_nghiep_khach_san':'sum'})
    df_doanhnghiep_ks= df_doanhnghiep_ks[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_doanh_nghiep_khach_san']]
    
    df_cathe_ks = spark.read.parquet(config['data_import']['khachsantunhan_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_cathe_ks)
    df_cathe_ks= df_cathe_ks.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_ca_the_khach_san':'sum'})
    df_cathe_ks= df_cathe_ks[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_ca_the_khach_san']]
    
    df_doanh_nghiep_vuanho = spark.read.parquet(config['data_import']['doanhnghiepvuanho_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanh_nghiep_vuanho)
    df_doanh_nghiep_vuanho= df_doanh_nghiep_vuanho.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_doanh_nghiep_vua_nho':'sum'})
    df_doanh_nghiep_vuanho= df_doanh_nghiep_vuanho[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_doanh_nghiep_vua_nho']]
    
    df_doanh_nghiep_cntt = spark.read.parquet(config['data_import']['doanhnghiepcntt_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanh_nghiep_cntt)
    df_doanh_nghiep_cntt= df_doanh_nghiep_cntt.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_doanh_nghiep_cntt':'sum'})
    df_doanh_nghiep_cntt= df_doanh_nghiep_cntt[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_doanh_nghiep_cntt']]

    df_doanh_nghiep_ttdt = spark.read.parquet(config['data_import']['doanhnghiepttdt_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_doanh_nghiep_ttdt)
    df_doanh_nghiep_ttdt= df_doanh_nghiep_ttdt.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'so_doanh_nghiep_ttdt':'sum'})
    df_doanh_nghiep_ttdt= df_doanh_nghiep_ttdt[['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','so_doanh_nghiep_ttdt']]
    
    df_doanh_nghiep_full = df_doanhnghiep.merge(df_doanhnghiep_vnn,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full = df_doanh_nghiep_full.merge(df_doanhnghiep_xnk,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full = df_doanh_nghiep_full.merge(df_doanhnghiep_kdct,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full = df_doanh_nghiep_full.merge(df_doanhnghiep_ks,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full = df_doanh_nghiep_full.merge(df_cathe_ks,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full = df_doanh_nghiep_full.merge(df_doanh_nghiep_vuanho,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full = df_doanh_nghiep_full.merge(df_doanh_nghiep_cntt,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full = df_doanh_nghiep_full.merge(df_doanh_nghiep_ttdt,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_doanh_nghiep_full['Phường có dấu'] =  np.where(df_doanh_nghiep_full['Phường có dấu']=='Nan',
                                               df_doanh_nghiep_full['Quận có dấu'],df_doanh_nghiep_full['Phường có dấu'])
    df_doanh_nghiep_full['Phường không dấu'] =  np.where(df_doanh_nghiep_full['Phường không dấu']=='Nan',
                                               df_doanh_nghiep_full['Quận không dấu'],df_doanh_nghiep_full['Phường không dấu'])
    df_doanh_nghiep_full = df_doanh_nghiep_full.groupby(['Tỉnh có dấu', 'Quận có dấu', 'Phường có dấu', 'Tỉnh không dấu',
        'Quận không dấu', 'Phường không dấu'],as_index=False).agg({
        'so_doanh_nghiep':'max','so_doanh_nghiep_von_nuoc_ngoai':'max','so_doanh_nghiep_xuat_nhap_khau':'max'
        ,'so_kinh_doanh_ca_the':'max','so_doanh_nghiep_khach_san':'max','so_ca_the_khach_san':'max'
        ,'so_doanh_nghiep_vua_nho':'max','so_doanh_nghiep_cntt':'max','so_doanh_nghiep_ttdt':'max'})
    return df_doanh_nghiep_full
def process_cho(kydautu,config):
    """
        + Load và chuẩn hoá dữ liệu địa chỉ chợ: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/cho.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ siêu thị: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/sieu_thi.parquet
        + Load và chuẩn hoá dữ liệu địa chỉ trung tâm thương mại: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/trung_tam_thuong_mai.parquet
        + Mapping các thông tin chợ, siêu thị, trung tâm thương mai cấp xã/phường 
    """
    df_cho = spark.read.parquet(config['data_import']['cho_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    df_cho['Phường'] = df_cho['Phường'].apply(lambda x: str(x).split('(')[0].strip('-|,|[ ]|.'))
    df_cho.rename({'Tên chợ':'Số chợ'},axis=1,inplace=True)
    normalize_address('Có dấu',df_cho)
    df_cho_grp = df_cho.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Số chợ':'count'})

    df_sieuthi = spark.read.parquet(config['data_import']['sieuthi_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    df_sieuthi.rename({'Tên siêu thị':'Số siêu thị'},axis=1,inplace=True)
    normalize_address('Có dấu',df_sieuthi)
    df_sieuthi_grp = df_sieuthi.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Số siêu thị':'count'})
    
    df_tttm = spark.read.parquet(config['data_import']['trungtamthuongmai_path_output']+"d={}-01-01".format(kydautu[2:])).toPandas()
    df_tttm.rename({'Tên trung tâm thương mại':'Số trung tâm thương mại'},axis=1,inplace=True)
    normalize_address('Có dấu',df_tttm)
    df_tttm_grp = df_tttm.groupby(['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],as_index=False).agg({'Số trung tâm thương mại':'count'})
    df_cho_full_ = df_cho_grp.merge(df_sieuthi_grp,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    df_cho_full_ = df_cho_full_.merge(df_tttm_grp,on=['Tỉnh có dấu','Quận có dấu', 'Phường có dấu', 
    'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu'],how='outer')
    return df_cho_full_
def process_olt(date,df_branch_province,config):
    """
        + Load dữ liệu lỗi olt từ postgresql 177 - dwh_noc -  inf.tbl_olt_error_log
        + Chuẩn hoá địa chỉ và mapping thông tin tỉnh => tính số lỗi olt ở mức tỉnh 
    """
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
        start_date = str(int(date[:4]))+'-07-01'
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
            start_date = str(int(date[:4]))+'-01-01'
        else:
            kydautu= '1H'+str(int(date[:4])+1)
            start_date = str(int(date[:4])+1)+'-01-01'
    sql_inf = """SELECT  LEFT(host,7) as POP,LEFT(host,3) as province, count(error) as total_error_olt
    FROM inf.{}
    WHERE timestamp>='{}' and timestamp <'{}' 
    GROUP BY  LEFT(host,7),LEFT(host,3);""".format(config['feature_ptht']['table_olt'],start_date,date)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    df_olt = pd.read_sql_query(sql_inf, conn)
    
    df_olt['Kỳ đầu tư'] = kydautu
    df_olt.rename({'pop':'POP'},axis=1,inplace=True)
    df_olt_grp = df_olt.groupby(['POP','province','Kỳ đầu tư'],as_index=False).agg({'total_error_olt':'sum'})
    df_olt_full = df_olt_grp.merge(df_branch_province, on='province', how='inner')
    df_olt_full.rename({'name':'Tỉnh'}, axis=1, inplace=True)
    df_olt_full_ = df_olt_full.groupby(['Tỉnh','Kỳ đầu tư'],as_index=False).agg({'total_error_olt':'sum'})
    return df_olt_full_

def inf_dwh_feature(date, config: dict = infra_analytics_config):
    """
        + Call tất cả function trên để tổng hợp các chỉ số 
        + Chuẩn hoá dữ liệu missing, thay đổi do sáp nhập và drop duplicates dữ liệu 
        + Tính thêm các chỉ số về tỉ lệ như rời mạng, nợ cước, portuse,...
        + Lưu dữ liệu xuống hdfs: /data/fpt/ftel/infra/dwh/ds_feature_ptht.parquet và table trên hive ftel_dwh_infra.ds_feature_ptht
    """
    assert config != None, "config must be not None"
        
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
        date=str(int(date[:4]))+'-03-01'
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
            date=str(int(date[:4])-1)+'-09-01'
        else:
            kydautu= '1H'+str(int(date[:4])+1)
            date=str(int(date[:4]))+'-09-01'
    print(kydautu)
    # config_file = "./config.yaml"
    # config = get_config(config_file)
    hdfsdir = config['feature_ptht']['feature_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    file_name = config['feature_ptht']['feature_path']+'/create_date='+date
    if file_name not in filelist:
        print(file_name)
        df_branch, df_branch_province, df_branch_region = process_location(config)
        df_diachidoi = process_diachidoi(config)
        df_info_cus_filter_gp = process_khachhang(date,df_diachidoi,config)
        df_sale_staff_pd = process_ibb(date,kydautu,config)
        df_mapping_ds = process_population(date, df_diachidoi,config)
        df_dt_dk_nguong_grp = get_nguongdanhgia(df_branch_province,config)
        df_VPGD_grp_filter_gp=process_vanphonggiaodich(df_diachidoi,config)
        df_nganhang_grp=process_nganhang(kydautu,config)
        df_thunhap=process_thunhap(date,config)
        df_dm_grp_filter_gp = preprocess_dienmay(df_diachidoi,config)
        df_sanbay_grp=process_sanbay(config)
        df_cangbien_grp=process_cangbien(config)
        df_gaduong_grp = process_gaduong(config)
        df_caotoc_grp = process_caotoc(config)
        df_bienvien_grp=process_bienvien(kydautu,config)
        df_school_grp=process_truonghoc(kydautu,config)
        df_doanh_nghiep_full=process_doanhnghiep(kydautu,config)
        df_cho_full_=process_cho(kydautu,config)
        df_tt_port_map_ = process_tangtruongport(date,df_diachidoi,df_branch_province,config)
        df_port_hh_full_ = process_thiphan(date,df_branch_province,df_diachidoi,config)
        df_dt_gp_filter_gp = process_doithu(df_diachidoi,config)
        df_vh_grp_filter_gp = process_vanhanh(date,df_branch_province,df_diachidoi,config)
        df_ticket_full_ = process_ticket(date,df_branch_province,config)
        df_olt_full_ = process_olt(date,df_branch_province,config)
        df_daily_canhto_filter = process_dailycanhto(date,df_branch,config)
        df_daily_canhto_filter['Kỳ đầu tư'] = kydautu
        df_sale_staff_pd.drop('region',axis=1,inplace=True)
        df_sale_staff_pd.drop_duplicates(keep='first',inplace=True)
        df_kt_full = process_lichsudautu(date,df_branch_province,df_dt_dk_nguong_grp,config)
        
        conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
        str_sql = "select ky_dau_tu from  public.%s group by ky_dau_tu"% (config['feature_ptht']['table_planning'])
        df_ht = pd.read_sql(str_sql, conn)
        df_kydautu = pd.DataFrame({'Kỳ đầu tư':df_ht['ky_dau_tu'].unique()})
        df_kydautu['ngay_bat_dau'] = df_kydautu['Kỳ đầu tư'].apply(lambda x: get_ngaybatdau(x))
        df_kydautu['ngay_bat_dau'] = pd.to_datetime(df_kydautu['ngay_bat_dau'])
        df_kydautu = df_kydautu.sort_values('ngay_bat_dau')
        df_kydautu['index_kdt'] = df_kydautu['ngay_bat_dau'].rank().astype(int)
        df_branch_province.columns = ['Tỉnh', 'province']
        df_branch_region.columns =['Tỉnh không dấu','Mã tỉnh','Vùng']
        #  SỰ CỐ VÀ LỖI OLT 
        df_error = df_olt_full_.merge(df_ticket_full_, on=['Tỉnh','Kỳ đầu tư'], how='outer')
        df_error.rename({'Tỉnh':'Tỉnh không dấu'},axis=1, inplace=True)
        
        df_mapping_ds = df_mapping_ds.merge(df_branch_region, on='Tỉnh không dấu', how='left')
        df_mapping_ds.replace({'Mã tỉnh':{'NTG':'KHA'}},regex=True,inplace=True)
        df_mapping_ds.drop_duplicates(keep='first', inplace=True)
        #  maping full dân số và bình quân chi tiêu
        df_dso_non_map  = df_mapping_ds.merge(df_thunhap,on=['Quận có dấu','Tỉnh có dấu',
                                    'Quận không dấu','Tỉnh không dấu'], how='outer')
        
        #  get các case cps dân số nhưng k có thu nhập từ tập trên
        df_non_map_ds = df_dso_non_map[(~df_dso_non_map['Tổng dân'].isna())&
                  (df_dso_non_map['Thu nhập'].isna())]
        df_non_map_ds_grp = df_non_map_ds.groupby(['Quận có dấu','Tỉnh có dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
        'Phường có dấu':'count'})[['Quận có dấu','Tỉnh có dấu','Quận không dấu','Tỉnh không dấu']]
        df_non_map_ds_grp.columns=['Quận có dấu update','Tỉnh có dấu update','Quận không dấu','Tỉnh không dấu']
        # Lấy danh sách các case có tyhu nhập nhưng k có dân số từ tập mapping full 
        df_non_map_tn = df_dso_non_map[(df_dso_non_map['Tổng dân'].isna())&
                  (~df_dso_non_map['Thu nhập'].isna())]
        df_non_map_tn_grp = df_non_map_tn.groupby(['Quận có dấu','Tỉnh có dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
        'Phường có dấu':'count'})[['Quận có dấu','Tỉnh có dấu','Quận không dấu','Tỉnh không dấu']]
        #  merge 2 tập k mapping đươc 
        df_non_map_tn_grp = df_non_map_tn_grp.merge(df_non_map_ds_grp, on=['Quận không dấu','Tỉnh không dấu'],
                                                   how='outer')
        df_non_map_tn_grp_filter = df_non_map_tn_grp[~df_non_map_tn_grp['Quận có dấu update'].isna()]
        
        df_thunhap_full_= df_thunhap.merge(df_non_map_tn_grp_filter, 
                  on=['Quận có dấu','Tỉnh có dấu','Quận không dấu','Tỉnh không dấu'], how='left')
        df_thunhap_full_['Quận có dấu update'] = np.where(df_thunhap_full_['Quận có dấu update'].isna(),
                                    df_thunhap_full_['Quận có dấu'],df_thunhap_full_['Quận có dấu update'])
        df_thunhap_full_['Tỉnh có dấu update'] = np.where(df_thunhap_full_['Tỉnh có dấu update'].isna(),
                               df_thunhap_full_['Tỉnh có dấu'],df_thunhap_full_['Tỉnh có dấu update'])
        df_thunhap_full_ = df_thunhap_full_[['Quận có dấu update', 'Tỉnh có dấu update',
            'Tỉnh không dấu', 'Quận không dấu', 'Thu nhập']]
        df_thunhap_full_.columns=['Quận có dấu', 'Tỉnh có dấu',
            'Tỉnh không dấu', 'Quận không dấu', 'Thu nhập']
        
        df_sale_staff_full_stack_filter = df_sale_staff_pd.copy()
        df_sale_staff_full_stack_filter.columns= [ 'Tỉnh không dấu', 'Chi nhánh' ,'IBB', 'Kỳ đầu tư']
        df_sale_staff_full_stack_filter.replace({'Tỉnh không dấu':{'Nha Trang':'Khanh Hoa'}},
                                                regex=True,inplace=True)
        df_sale_staff_full_stack_filter.replace({'Chi nhánh':{'HNI_0|HNI_':'HN','_':'','HNIs':'HNI',
                            'KHA_01|KHA_02|KHA_03':'KHA','VTU':'BRU',
                            'BGG_01|BGG_02':'BGG',
                            'BNH_01|BNH_02':'BNH',
                            'QNH_01|QNH_02|QNH_03':'QNH',
                            'HDG_01|HDG_02|HDG_03|HDG_04|HDG_05':'HDG',
                            'HPG_01|HPG_02|HPG_03|HPG_04|HPG_05|HPG_06':'HPG',
                            'DNG_01|DNG_02|DNG_03':'DNG','BDG_01|BDG_02|BDG_03':'BDG', 
                            'DNI_01|DNI_02|DNI_03|DNI_04|DNI_05|DNI_06|DNI_07':'DNI' }}, regex=True, inplace=True)
        
        df_kt_sale = df_kt_full.merge(df_sale_staff_full_stack_filter,on=['Tỉnh không dấu',
                                      'Chi nhánh','Kỳ đầu tư'], how='outer')
        
        df_kt_sale = df_kt_sale.merge(df_daily_canhto_filter,on=['Tỉnh không dấu','Quận không dấu',
                         'Phường không dấu','Kỳ đầu tư'], how='left')
        df_kt_sale.columns = ['Phường không dấu', 'Quận không dấu', 'Chi nhánh', 'Vùng đầu tư', 'Kỳ đầu tư',
               'index_kdt', 'TG đầu tư gần nhất', 'num_khdt_truoc', 'DL triển khai',
               '% khai thác sau 3T', '% khai thác sau 6T', '% khai thác sau 9T',
               '% khai thác sau 12T', 'Perport', 'Tổng port sau 6T hien tai',
               'Port dùng sau 6T hien tai', '% portfree sau 3T', '% portfree sau 6T',
               '% portfree sau 9T', '% portfree sau 12T', 'HQKT 6T hiệu tại',
               'ngưỡng TB', 'danh_gia_hieu_qua', 'Tỉnh không dấu', 'IBB',
               'đại lý canh tô', 'Số HĐ với KH', 'Doanh thu']
        df_kt_sale.replace({'Quận không dấu':{'T.Tran':''}},regex=False, inplace=True)
        df_kt_sale = df_kt_sale[df_kt_sale['Phường không dấu']!='']
        df_kt_sale_filter = df_kt_sale[(~df_kt_sale['Quận không dấu'].isna())&
                                    (~df_kt_sale['Phường không dấu'].isna())&
                                    (~df_kt_sale['Tỉnh không dấu'].isna())]
        df_kt_sale_filter.replace({'Phường không dấu':{'Phuong  ':'Phuong '}},regex=True,inplace=True)
        df_kt_sale_filter.replace({'Phường không dấu':{'Phuong Co Nhue 2':'Co Nhue 2',
        'Phuong My Dinh 2':'My Dinh 2',
        'Thi  Trang Bang':'Trang Bang',
        'Phuong Gia Tan 2':'Gia Tan 2',
        'Phuong Sai':'Sai'}},regex=True,inplace=True)
        df_kt_sale_filter.replace({'Quận không dấu':{'Ba Don,  Quang Trach':'Quang Trach',
        'Quan  ':'Quan ','Lagi':'La Gi',
        'Phan Rang - Thap Cham':'Phan Rang-Thap Cham',
        'Phan Rang - Tc':'Phan Rang-Thap Cham'}},regex=True,inplace=True)
        df_kt_sale_filter['Quận không dấu'] = df_kt_sale_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
        df_kt_sale_filter['Phường không dấu'] = df_kt_sale_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
        
        df_kt_sale_filter['Quận không dấu'] = np.where((df_kt_sale_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                            (df_kt_sale_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                    'Thu Duc' ,df_kt_sale_filter['Quận không dấu'])
        df_kt_sale_filter_mapping = df_kt_sale_filter.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu','Chi nhánh',
             'Kỳ đầu tư'],as_index=False).agg({'TG đầu tư gần nhất':'min','num_khdt_truoc':'max',
            'DL triển khai':'max','% khai thác sau 3T':'max','% khai thác sau 6T':'max',
          '% khai thác sau 9T':'max','% khai thác sau 12T':'max','Perport':'max',
          '% portfree sau 3T':'max','% portfree sau 6T':'max','% portfree sau 9T':'max',
            '% portfree sau 12T':'max','IBB':'max','đại lý canh tô':'max','Số HĐ với KH':'max','Doanh thu':'max'})
        df_kt_sale_filter_mapping.columns= ['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'Chi nhánh',
               'Kỳ đầu tư', 'TG đầu tư gần nhất update', 'num_khdt_truoc update', 'DL triển khai update',
               '% khai thác sau 3T update', '% khai thác sau 6T update', '% khai thác sau 9T update',
               '% khai thác sau 12T update', 'Perport update', '% portfree sau 3T update',
               '% portfree sau 6T update', '% portfree sau 9T update', '% portfree sau 12T update', 'IBB update',
               'đại lý canh tô update', 'Số HĐ với KH update', 'Doanh thu update']
        
        df_kt_sale_filter = df_kt_sale_filter.merge(df_kt_sale_filter_mapping,
           on=['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'Chi nhánh','Kỳ đầu tư'],how='left')
        df_kt_sale_filter['TG đầu tư gần nhất'] = np.where(df_kt_sale_filter['TG đầu tư gần nhất'].isna(),
                                                          df_kt_sale_filter['TG đầu tư gần nhất update'],
                                                           df_kt_sale_filter['TG đầu tư gần nhất'])
        df_kt_sale_filter['num_khdt_truoc'] = np.where(df_kt_sale_filter['num_khdt_truoc'].isna(),
                                                          df_kt_sale_filter['num_khdt_truoc update'],
                                                           df_kt_sale_filter['num_khdt_truoc'])
        df_kt_sale_filter['DL triển khai'] = np.where(df_kt_sale_filter['DL triển khai'].isna(),
                                                          df_kt_sale_filter['DL triển khai update'],
                                                           df_kt_sale_filter['DL triển khai'])
        df_kt_sale_filter['% khai thác sau 3T'] = np.where(df_kt_sale_filter['% khai thác sau 3T'].isna(),
                                                          df_kt_sale_filter['% khai thác sau 3T update'],
                                                           df_kt_sale_filter['% khai thác sau 3T'])
        df_kt_sale_filter['% khai thác sau 6T'] = np.where(df_kt_sale_filter['% khai thác sau 6T'].isna(),
                                                          df_kt_sale_filter['% khai thác sau 6T update'],
                                                           df_kt_sale_filter['% khai thác sau 6T'])
        df_kt_sale_filter['% khai thác sau 9T'] = np.where(df_kt_sale_filter['% khai thác sau 9T'].isna(),
                                                          df_kt_sale_filter['% khai thác sau 9T update'],
                                                           df_kt_sale_filter['% khai thác sau 9T'])
        df_kt_sale_filter['% khai thác sau 12T'] = np.where(df_kt_sale_filter['% khai thác sau 12T'].isna(),
                                                          df_kt_sale_filter['% khai thác sau 12T update'],
                                                           df_kt_sale_filter['% khai thác sau 12T'])
        df_kt_sale_filter['Perport'] = np.where(df_kt_sale_filter['Perport'].isna(),
                                                          df_kt_sale_filter['Perport update'],
                                                           df_kt_sale_filter['Perport'])
        df_kt_sale_filter['% portfree sau 3T'] = np.where(df_kt_sale_filter['% portfree sau 3T'].isna(),
                                                          df_kt_sale_filter['% portfree sau 3T update'],
                                                           df_kt_sale_filter['% portfree sau 3T'])
        df_kt_sale_filter['% portfree sau 6T'] = np.where(df_kt_sale_filter['% portfree sau 6T'].isna(),
                                                          df_kt_sale_filter['% portfree sau 6T update'],
                                                           df_kt_sale_filter['% portfree sau 6T'])
        df_kt_sale_filter['% portfree sau 9T'] = np.where(df_kt_sale_filter['% portfree sau 9T'].isna(),
                                                          df_kt_sale_filter['% portfree sau 9T update'],
                                                           df_kt_sale_filter['% portfree sau 9T'])
        df_kt_sale_filter['% portfree sau 12T'] = np.where(df_kt_sale_filter['% portfree sau 12T'].isna(),
                                                          df_kt_sale_filter['% portfree sau 12T update'],
                                                           df_kt_sale_filter['% portfree sau 12T'])
        df_kt_sale_filter['IBB'] = np.where(df_kt_sale_filter['IBB'].isna(),
                                                          df_kt_sale_filter['IBB update'],
                                                           df_kt_sale_filter['IBB'])
        df_kt_sale_filter['đại lý canh tô'] = np.where(df_kt_sale_filter['đại lý canh tô'].isna(),
                                                          df_kt_sale_filter['đại lý canh tô update'],
                                                           df_kt_sale_filter['đại lý canh tô'])
        df_kt_sale_filter['Số HĐ với KH'] = np.where(df_kt_sale_filter['Số HĐ với KH'].isna(),
                                                          df_kt_sale_filter['Số HĐ với KH update'],
                                                           df_kt_sale_filter['Số HĐ với KH'])
        df_kt_sale_filter['Doanh thu'] = np.where(df_kt_sale_filter['Doanh thu'].isna(),
                                                          df_kt_sale_filter['Doanh thu update'],
                                                           df_kt_sale_filter['Doanh thu'])
        df_kt_sale_filter.drop({'TG đầu tư gần nhất update', 'num_khdt_truoc update', 'DL triển khai update',
               '% khai thác sau 3T update', '% khai thác sau 6T update', '% khai thác sau 9T update',
               '% khai thác sau 12T update', 'Perport update', '% portfree sau 3T update',
               '% portfree sau 6T update', '% portfree sau 9T update', '% portfree sau 12T update', 'IBB update',
               'đại lý canh tô update', 'Số HĐ với KH update', 'Doanh thu update'},axis=1,inplace=True)
        df_kt_sale_filter_grp = df_kt_sale_filter.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu','Chi nhánh',
        'Vùng đầu tư','Kỳ đầu tư','index_kdt','Tổng port sau 6T hien tai','Port dùng sau 6T hien tai',
        'HQKT 6T hiệu tại','ngưỡng TB','danh_gia_hieu_qua'],as_index=False).agg({'TG đầu tư gần nhất':'min','num_khdt_truoc':'max',
        'DL triển khai':'sum','% khai thác sau 3T':'mean','% khai thác sau 6T':'mean',
        '% khai thác sau 9T':'mean','% khai thác sau 12T':'mean','Perport':'mean',
        '% portfree sau 3T':'mean','% portfree sau 6T':'mean','% portfree sau 9T':'mean',
        '% portfree sau 12T':'mean','IBB':'mean','đại lý canh tô':'mean','Số HĐ với KH':'mean','Doanh thu':'mean'})
        df_kt_sale_filter_grp['Phường không dấu']= df_kt_sale_filter_grp['Phường không dấu'].str.strip('-|,|[ ]|.')
        df_kt_sale_filter_grp['Phường không dấu'] = df_kt_sale_filter_grp['Phường không dấu'].str.title() 
        
        df_kt_sale_filter_grp['Quận không dấu']= df_kt_sale_filter_grp['Quận không dấu'].str.strip('-|,|[ ]|.')
        df_kt_sale_filter_grp['Quận không dấu'] = df_kt_sale_filter_grp['Quận không dấu'].str.title() 
        
        df_kt_sale_filter_grp['Tỉnh không dấu']= df_kt_sale_filter_grp['Tỉnh không dấu'].str.strip('-|,|[ ]|.')
        df_kt_sale_filter_grp['Tỉnh không dấu'] = df_kt_sale_filter_grp['Tỉnh không dấu'].str.title()
        df_kt_sale_filter_grp = df_kt_sale_filter_grp.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                            'Tỉnh không dấu'],how='left')
        df_kt_sale_filter_grp['Phường thay đổi']= np.where(df_kt_sale_filter_grp['Phường thay đổi'].isna(),
                                                          df_kt_sale_filter_grp['Phường không dấu'],
                                                          df_kt_sale_filter_grp['Phường thay đổi'])
        df_kt_sale_filter_grp['Quận thay đổi']= np.where(df_kt_sale_filter_grp['Quận thay đổi'].isna(),
                                                          df_kt_sale_filter_grp['Quận không dấu'],
                                                          df_kt_sale_filter_grp['Quận thay đổi'])
        df_kt_sale_filter_grp['Tỉnh thay đổi']= np.where(df_kt_sale_filter_grp['Tỉnh thay đổi'].isna(),
                                                          df_kt_sale_filter_grp['Tỉnh không dấu'],
                                                          df_kt_sale_filter_grp['Tỉnh thay đổi'])
        df_kt_sale_filter_grp= df_kt_sale_filter_grp[['Phường thay đổi','Quận thay đổi','Tỉnh thay đổi','Chi nhánh',
        'Vùng đầu tư','Kỳ đầu tư','index_kdt','Tổng port sau 6T hien tai','Port dùng sau 6T hien tai',
        'HQKT 6T hiệu tại','ngưỡng TB','danh_gia_hieu_qua','TG đầu tư gần nhất', 'num_khdt_truoc',
               'DL triển khai', '% khai thác sau 3T', '% khai thác sau 6T',
               '% khai thác sau 9T', '% khai thác sau 12T', 'Perport',
               '% portfree sau 3T', '% portfree sau 6T', '% portfree sau 9T',
               '% portfree sau 12T', 'IBB', 'đại lý canh tô', 'Số HĐ với KH',
               'Doanh thu']]
        df_kt_sale_filter_grp.columns= ['Phường không dấu','Quận không dấu','Tỉnh không dấu','Chi nhánh',
        'Vùng đầu tư','Kỳ đầu tư','index_kdt','Tổng port sau 6T hien tai','Port dùng sau 6T hien tai',
        'HQKT 6T hiệu tại','ngưỡng TB','danh_gia_hieu_qua','TG đầu tư gần nhất', 'num_khdt_truoc',
               'DL triển khai', '% khai thác sau 3T', '% khai thác sau 6T',
               '% khai thác sau 9T', '% khai thác sau 12T', 'Perport',
               '% portfree sau 3T', '% portfree sau 6T', '% portfree sau 9T',
               '% portfree sau 12T', 'IBB', 'đại lý canh tô', 'Số HĐ với KH',
               'Doanh thu']
        
        df_kt_sale_filter_grp = df_kt_sale_filter_grp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu','Chi nhánh',
        'Vùng đầu tư','Kỳ đầu tư','index_kdt','Tổng port sau 6T hien tai','Port dùng sau 6T hien tai',
        'HQKT 6T hiệu tại','ngưỡng TB','danh_gia_hieu_qua'],as_index=False).agg({'TG đầu tư gần nhất':'min','num_khdt_truoc':'max',
        'DL triển khai':'sum','% khai thác sau 3T':'mean','% khai thác sau 6T':'mean',
        '% khai thác sau 9T':'mean','% khai thác sau 12T':'mean','Perport':'mean',
        '% portfree sau 3T':'mean','% portfree sau 6T':'mean','% portfree sau 9T':'mean',
        '% portfree sau 12T':'mean','IBB':'mean','đại lý canh tô':'mean','Số HĐ với KH':'mean','Doanh thu':'mean'})
        
        df_kt_sale_filter_grp.drop('index_kdt',axis=1,inplace=True)
        df_kt_sale_filter_grp.drop('Kỳ đầu tư',axis=1,inplace=True)
        df_info_cus_filter_gp.drop('Kỳ đầu tư',axis=1,inplace=True)
        df_vh_grp_filter_gp.drop('Kỳ đầu tư',axis=1,inplace=True)
        df_tt_port_map_.drop('Kỳ đầu tư',axis=1,inplace=True)
        df_error.drop('Kỳ đầu tư',axis=1,inplace=True)
        
        df_feature = df_mapping_ds.merge(df_thunhap_full_,on=['Quận có dấu','Tỉnh có dấu',
                                    'Quận không dấu','Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_bienvien_grp,on=['Phường có dấu','Quận có dấu','Tỉnh có dấu',
                     'Phường không dấu','Quận không dấu','Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_school_grp,on=['Phường có dấu','Quận có dấu','Tỉnh có dấu',
                     'Phường không dấu','Quận không dấu','Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_doanh_nghiep_full,on=['Phường có dấu','Quận có dấu','Tỉnh có dấu',
                     'Phường không dấu','Quận không dấu','Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_cho_full_,on=['Phường có dấu','Quận có dấu','Tỉnh có dấu',
                     'Phường không dấu','Quận không dấu','Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_sanbay_grp,on=['Quận không dấu','Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_cangbien_grp,on=['Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_gaduong_grp,on=['Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_caotoc_grp,on=['Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_error,on=['Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_nganhang_grp,on=['Phường có dấu','Quận có dấu','Tỉnh có dấu',
                                                          'Phường không dấu','Quận không dấu',
                                                          'Tỉnh không dấu'], how='left')
        df_feature  = df_feature.merge(df_VPGD_grp_filter_gp,on=['Tỉnh không dấu',
                                      'Quận không dấu','Phường không dấu'], how='left')
        df_feature = df_feature.merge(df_dm_grp_filter_gp,on=['Phường không dấu','Quận không dấu',
                                                          'Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_dt_gp_filter_gp,on=['Phường không dấu','Quận không dấu',
                                                   'Tỉnh không dấu'], how='left')
        df_feature = df_feature.merge(df_info_cus_filter_gp,on=['Phường không dấu','Quận không dấu','Tỉnh không dấu'
                                                    ], how='left')
        df_feature = df_feature.merge(df_vh_grp_filter_gp,on=['Phường không dấu','Quận không dấu',
                                                              'Tỉnh không dấu'], how='left')
        df_feature  = df_feature.merge(df_kt_sale_filter_grp,on=['Phường không dấu','Quận không dấu','Tỉnh không dấu'
                                   ], how='left')
        df_feature  = df_feature.merge(df_tt_port_map_,on=['Phường không dấu', 'Quận không dấu', 'Vùng','Tỉnh không dấu'], how='left')
        
        df_feature  = df_feature.merge(df_port_hh_full_,on=['Phường không dấu', 'Quận không dấu', 'Vùng','Tỉnh không dấu'], how='left')
        df_feature['danh_gia_hieu_qua'] = np.where(df_feature['danh_gia_hieu_qua'].isna(),
                                                   'Chưa xác định',df_feature['danh_gia_hieu_qua'])
        df_feature['Vùng đầu tư'] = np.where(df_feature['Vùng đầu tư'].isna(), df_feature['Vùng'],
                                            df_feature['Vùng đầu tư'])
        df_feature.drop({'Vùng đầu tư'},axis=1,inplace=True)
        df_feature['Chi nhánh'] = np.where(df_feature['Chi nhánh'].isna(),df_feature['Mã tỉnh'],
                                          df_feature['Chi nhánh'])
        df_feature.replace({'Chi nhánh' : {r'SGN': 'HCM','SG':'HCM', r'NTG':'KHA', r'HNI-0': 'HN',  
                                    'HNI-':'HN','HCM-0':'HCM','HCM-':'HCM', r'HN0': 'HN',
                                           r'HCM0': 'HCM'}}, regex=True,inplace=True)
        
        df_feature['number_khg'] = np.where(df_feature['number_khg']<df_feature['KHG_RM'],
                                            df_feature['KHG_RM'],df_feature['number_khg'])
        df_feature['number_khg'] = np.where(df_feature['number_khg']<df_feature['number_nocuoc'],
                                            df_feature['number_nocuoc'],df_feature['number_khg']) 
        df_feature.drop(['Quận không dấu','Phường không dấu','Tỉnh không dấu'],axis=1,inplace=True)
        df_feature['ky_dau_tu'] = kydautu
        df_feature['create_date']= date
        df_feature.columns = ['quan', 'phuong', 'tinh',
        'area','tong_dan', 'thanh_thi', 'nong_thon', 'tong_so_ho', 'duoi_tieu_hoc',
        'tieu_hoc', 'trung_hoc', 'cao_dang', 'dai_hoc', 'thac_sy', 'tien_sy',
        'density', 'mat_do_ho_dan', 'Mã tỉnh', 'vung',
        'thu_nhap', 'so_benh_vien', 'so_co_so_y_te',
        'so_truong_tieu_hoc', 'so_truong_trung_hoc', 'so_truong_pho_thong',
        'so_truong_cao_dang', 'so_truong_dai_hoc', 'so_doanh_nghiep',
        'so_doanh_nghiep_von_nuoc_ngoai', 'so_doanh_nghiep_xuat_nhap_khau',
        'so_kinh_doanh_ca_the', 'so_doanh_nghiep_khach_san',
        'so_ca_the_khach_san', 'so_doanh_nghiep_vua_nho',
        'so_doanh_nghiep_cntt', 'so_doanh_nghiep_ttdt', 'so_cho', 'so_sieu_thi',
        'so_trung_tam_thuong_mai','so_san_bay', 'so_cang', 'so_duongga',
        'so_caotoc', 'total_error_olt', 'ticketcode', 'timetotal',
        'name_device', 'cus_qty', 'so_ngan_hang', 'so_vp', 'so_shop',
         'ap_doi_thu','number_khg','khg_rm','number_nocuoc','num_checlist',
        'avg_operation_pop','avg_quality_pop', 'chi_nhanh','tong_port_sau_6t_hien_tai', 'port_dung_sau_6t_hien_tai',
        'hqkt_6t_hieu_tai','nguong_tb','danh_gia_hieu_qua',
         'tg_dau_tu_gan_nhat', 'num_khdt_truoc', 'dl_trien_khai',
        'tl_khai_thac_sau_3t', 'tl_khai_thac_sau_6t', 'tl_khai_thac_sau_9t',
        'tl_khai_thac_sau_12t', 'perport', 'tl_portfree_sau_3t',
        'tl_portfree_sau_6t', 'tl_portfree_sau_9t', 'tl_portfree_sau_12t', 'ibb',
        'dai_ly_canh_to', 'so_hd_với_khg', 'doanh_thu',
         'tuoi','t1', 't2', 't3', 't4','t5',
         'port', 'portuse', 'portfree', 'portdie', 'portmaintain','num_device',
         'ky_dau_tu', 'create_date']
        df_feature= df_feature.dropna(axis=0,thresh=10)
        data_fillna = pd.DataFrame({'column_name':df_feature.mean().index, 'value_fill':df_feature.mean().values})
        lists_ = ['tl_khai_thac_sau_3t', 'tl_khai_thac_sau_6t', 'tl_khai_thac_sau_9t',
        'tl_khai_thac_sau_12t','avg_quality_pop','avg_operation_pop', 'perport', 'area','thu_nhap','tong_so_ho']
        for i in lists_:
            df_feature[i].fillna(data_fillna.loc[data_fillna['column_name']==i,'value_fill'].values[0],inplace=True)
        df_feature[['thanh_thi', 'nong_thon', 'duoi_tieu_hoc',
        'tieu_hoc', 'trung_hoc', 'cao_dang', 'dai_hoc', 'thac_sy', 'tien_sy',
         'so_benh_vien', 'so_co_so_y_te',
        'so_truong_tieu_hoc', 'so_truong_trung_hoc', 'so_truong_pho_thong',
        'so_truong_cao_dang', 'so_truong_dai_hoc', 'so_doanh_nghiep',
        'so_doanh_nghiep_von_nuoc_ngoai', 'so_doanh_nghiep_xuat_nhap_khau',
        'so_kinh_doanh_ca_the', 'so_doanh_nghiep_khach_san',
        'so_ca_the_khach_san', 'so_doanh_nghiep_vua_nho',
        'so_doanh_nghiep_cntt', 'so_doanh_nghiep_ttdt', 'so_cho', 'so_sieu_thi',
        'so_trung_tam_thuong_mai','so_san_bay', 'so_cang', 'so_duongga',
        'so_caotoc', 'total_error_olt', 'ticketcode', 'timetotal',
        'name_device', 'cus_qty', 'so_ngan_hang', 'so_vp', 'so_shop',
        'number_khg','khg_rm','number_nocuoc','num_checlist','ap_doi_thu',
        'ibb','dl_trien_khai','num_khdt_truoc','dai_ly_canh_to','so_hd_với_khg','doanh_thu',
        'tuoi','t1', 't2', 't3', 't4','t5','port', 'portuse', 'portfree', 'portdie',
        'portmaintain','num_device']]\
            =df_feature[['thanh_thi', 'nong_thon', 'duoi_tieu_hoc',
        'tieu_hoc', 'trung_hoc', 'cao_dang', 'dai_hoc', 'thac_sy', 'tien_sy',
         'so_benh_vien', 'so_co_so_y_te',
        'so_truong_tieu_hoc', 'so_truong_trung_hoc', 'so_truong_pho_thong',
        'so_truong_cao_dang', 'so_truong_dai_hoc', 'so_doanh_nghiep',
        'so_doanh_nghiep_von_nuoc_ngoai', 'so_doanh_nghiep_xuat_nhap_khau',
        'so_kinh_doanh_ca_the', 'so_doanh_nghiep_khach_san',
        'so_ca_the_khach_san', 'so_doanh_nghiep_vua_nho',
        'so_doanh_nghiep_cntt', 'so_doanh_nghiep_ttdt', 'so_cho', 'so_sieu_thi',
        'so_trung_tam_thuong_mai','so_san_bay', 'so_cang', 'so_duongga',
        'so_caotoc', 'total_error_olt', 'ticketcode', 'timetotal',
        'name_device', 'cus_qty', 'so_ngan_hang', 'so_vp', 'so_shop',
        'number_khg','khg_rm','number_nocuoc','num_checlist','ap_doi_thu',
        'ibb','dl_trien_khai','num_khdt_truoc','dai_ly_canh_to','so_hd_với_khg','doanh_thu',
        'tuoi','t1', 't2', 't3', 't4','t5','port', 'portuse', 'portfree', 'portdie',
        'portmaintain','num_device']].fillna(0)
        df_feature['tg_dau_tu_gan_nhat'].fillna(df_feature['tg_dau_tu_gan_nhat'].max(),inplace=True)
        df_feature['tl_portfree_sau_3t'] = 1- df_feature['tl_khai_thac_sau_3t']
        df_feature['tl_portfree_sau_6t'] = 1- df_feature['tl_khai_thac_sau_6t']
        df_feature['tl_portfree_sau_9t'] = 1- df_feature['tl_khai_thac_sau_9t']
        df_feature['tl_portfree_sau_12t'] = 1- df_feature['tl_khai_thac_sau_12t']
        df_feature['area'] = np.where(df_feature['area']<=0,df_feature['area']*(-1),df_feature['area'])
        df_feature['rate_rm'] = df_feature['khg_rm']/df_feature['number_khg']
        df_feature['rate_nc'] = df_feature['number_nocuoc']/df_feature['number_khg']
        df_feature['rate_port_use'] = df_feature['portuse']/df_feature['port']
        df_feature['portfree']= df_feature['port']- df_feature['portuse']
        df_feature['rate_port_free'] = df_feature['portfree']/df_feature['port']
        df_feature['tp_ftel'] = df_feature['portuse'].div(df_feature['tong_so_ho'].where(df_feature['tong_so_ho'] != 0, np.nan))
        df_feature['ftel_doithu'] = df_feature['portuse']/(df_feature['portuse']+ df_feature['ap_doi_thu'])
        df_feature['density'] =df_feature['tong_dan']/(df_feature['area'].astype(float))
        df_feature['mat_do_ho_dan'] =(df_feature['tong_so_ho']/(df_feature['area'].astype(float)))
        df_feature['dl_kh'] = df_feature['dl_trien_khai']/df_feature['num_khdt_truoc']
        df_feature[['rate_rm','rate_nc','rate_port_use','rate_port_free','tp_ftel','ftel_doithu','dl_kh']]=\
        df_feature[['rate_rm','rate_nc','rate_port_use','rate_port_free','tp_ftel','ftel_doithu','dl_kh']].fillna(0)
        df_feature.replace([np.inf, -np.inf], 0, inplace=True)
        df_feature['chi_nhanh'] = np.where((df_feature['tinh']=="Ha Noi")&((df_feature['chi_nhanh']=="HPG"
                                     )|((df_feature['chi_nhanh']=="DNI"))), 'HNI',df_feature['chi_nhanh'])
        df_feature.drop('nguong_tb',axis=1,inplace=True)
        df_dt_dk_nguong_grp.columns =['nguong_tb','ky_dau_tu']
        df_feature_ = df_feature.merge(df_dt_dk_nguong_grp, on='ky_dau_tu', how='left')
        df_feature_ = df_feature_[['quan', 'phuong', 'tinh', 'vung', 'ky_dau_tu', 'chi_nhanh',
               'tong_port_sau_6t_hien_tai', 'port_dung_sau_6t_hien_tai',
               'hqkt_6t_hieu_tai', 'nguong_tb', 'danh_gia_hieu_qua', 'area',
               'tong_dan', 'thanh_thi', 'nong_thon', 'tong_so_ho', 'duoi_tieu_hoc',
               'tieu_hoc', 'trung_hoc', 'cao_dang', 'dai_hoc', 'thac_sy', 'tien_sy',
               'density', 'mat_do_ho_dan', 'thu_nhap', 'so_benh_vien', 'so_co_so_y_te',
               'so_truong_tieu_hoc', 'so_truong_trung_hoc', 'so_truong_pho_thong',
               'so_truong_cao_dang', 'so_truong_dai_hoc', 'so_doanh_nghiep',
               'so_doanh_nghiep_von_nuoc_ngoai', 'so_doanh_nghiep_xuat_nhap_khau',
               'so_kinh_doanh_ca_the', 'so_doanh_nghiep_khach_san',
               'so_ca_the_khach_san', 'so_doanh_nghiep_vua_nho',
               'so_doanh_nghiep_cntt', 'so_doanh_nghiep_ttdt', 'so_cho', 'so_sieu_thi',
               'so_trung_tam_thuong_mai', 'so_san_bay', 'so_cang', 'so_duongga',
               'so_caotoc', 'total_error_olt', 'ticketcode', 'timetotal',
               'name_device', 'cus_qty', 'so_ngan_hang', 'so_vp', 'so_shop',
               'ap_doi_thu', 'khg_rm', 'number_nocuoc', 'number_khg', 'rate_rm',
               'rate_nc', 'num_checlist', 'avg_operation_pop', 'avg_quality_pop',
               'tg_dau_tu_gan_nhat', 'num_khdt_truoc', 'dl_trien_khai',
               'tl_khai_thac_sau_3t', 'tl_khai_thac_sau_6t', 'tl_khai_thac_sau_9t',
               'tl_khai_thac_sau_12t', 'perport', 'tl_portfree_sau_3t',
               'tl_portfree_sau_6t', 'tl_portfree_sau_9t', 'tl_portfree_sau_12t', 'ibb',
               'dai_ly_canh_to', 'so_hd_với_khg', 'doanh_thu', 't1', 't2', 't3', 't4',
               't5', 'tuoi', 'port', 'portuse', 'portfree', 'portdie', 'portmaintain',
               'num_device', 'dl_kh', 'rate_port_use', 'rate_port_free', 'tp_ftel',
               'ftel_doithu', 'create_date']]
        
        df_feature_1 = df_feature_.sort_values(['quan', 'phuong', 'tinh', 'vung', 'ky_dau_tu', 'chi_nhanh',
               'tong_port_sau_6t_hien_tai', 'port_dung_sau_6t_hien_tai',
               'hqkt_6t_hieu_tai', 'nguong_tb', 'danh_gia_hieu_qua', 'area',
               'tong_dan', 'thanh_thi', 'nong_thon', 'tong_so_ho', 'duoi_tieu_hoc',
               'tieu_hoc', 'trung_hoc', 'cao_dang', 'dai_hoc', 'thac_sy', 'tien_sy',
               'density', 'mat_do_ho_dan', 'thu_nhap', 'so_benh_vien', 'so_co_so_y_te',
               'so_truong_tieu_hoc', 'so_truong_trung_hoc', 'so_truong_pho_thong',
               'so_truong_cao_dang', 'so_truong_dai_hoc', 'so_doanh_nghiep',
               'so_doanh_nghiep_von_nuoc_ngoai', 'so_doanh_nghiep_xuat_nhap_khau',
               'so_kinh_doanh_ca_the', 'so_doanh_nghiep_khach_san',
               'so_ca_the_khach_san', 'so_doanh_nghiep_vua_nho',
               'so_doanh_nghiep_cntt', 'so_doanh_nghiep_ttdt', 'so_cho', 'so_sieu_thi',
               'so_trung_tam_thuong_mai', 'so_san_bay', 'so_cang', 'so_duongga',
               'so_caotoc', 'total_error_olt', 'ticketcode', 'timetotal',
               'name_device', 'cus_qty', 'so_ngan_hang', 'so_vp', 'so_shop',
               'ap_doi_thu', 'khg_rm', 'number_nocuoc', 'number_khg', 'rate_rm',
               'rate_nc', 'num_checlist', 'avg_operation_pop', 'avg_quality_pop',
               'tg_dau_tu_gan_nhat', 'num_khdt_truoc', 'dl_trien_khai',
               'tl_khai_thac_sau_3t', 'tl_khai_thac_sau_6t', 'tl_khai_thac_sau_9t',
               'tl_khai_thac_sau_12t', 'perport', 'tl_portfree_sau_3t',
               'tl_portfree_sau_6t', 'tl_portfree_sau_9t', 'tl_portfree_sau_12t',
               'ibb', 'dai_ly_canh_to', 'so_hd_với_khg', 'doanh_thu', 't1', 't2', 't3',
               't4', 't5', 'tuoi', 'port', 'portuse', 'portfree', 'portdie',
               'portmaintain', 'num_device', 'dl_kh', 'rate_port_use',
               'rate_port_free', 'tp_ftel', 'ftel_doithu', 'create_date'],ascending=False)
        df_feature_1.drop_duplicates(subset=['quan', 'phuong', 'tinh', 'vung', 'ky_dau_tu', 'chi_nhanh',
               'tong_port_sau_6t_hien_tai', 'port_dung_sau_6t_hien_tai',
               'hqkt_6t_hieu_tai', 'nguong_tb', 'danh_gia_hieu_qua'],keep='first',inplace=True)
        df_feature_sp = spark.createDataFrame(df_feature_1) 
        df_feature_sp = df_feature_sp.withColumn('so_ngan_hang',col('so_ngan_hang').cast('double'))
        df_feature_sp = df_feature_sp.withColumn('total_error_olt',col('total_error_olt').cast('double'))
        df_feature_sp.coalesce(1).write.mode("overwrite").partitionBy('create_date').option("path", config['feature_ptht']['feature_path']+"/")\
        .saveAsTable("ftel_dwh_infra.{}".format(config['feature_ptht']['table_feature']))