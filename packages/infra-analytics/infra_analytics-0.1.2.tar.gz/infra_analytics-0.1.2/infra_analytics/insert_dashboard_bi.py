import psycopg2 as pg
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
from multiprocessing import Process, Queue, Array, current_process
from underthesea import text_normalize
import psycopg2
import requests
import sqlalchemy
import unidecode
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
from datetime import datetime,timedelta
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
import re
import datetime as dt
from dateutil.relativedelta import relativedelta
import json
import warnings
warnings.filterwarnings('ignore')

import spark_sdk as ss
ss.__version__
import os
ss.PySpark(yarn=False, num_executors=60, driver_memory='60g', executor_memory='24g',
            add_on_config1=('spark.port.maxRetries', '1000'),
          add_on_config2=('spark.jars', '/mnt/projects-data/infra_report/jars/postgresql-42.2.20.jar'))
spark = ss.PySpark().spark
spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")
from pathlib import Path

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.functions import monotonically_increasing_id 
from pyspark.sql.types import *
from pyspark.sql import Window
from pyspark.sql.functions import *
import pyspark.sql.functions as f
from pyspark.sql.functions import min as sparkMin
spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")
import sqlalchemy
pd.set_option('display.max_colwidth', None)
import subprocess
import yaml
from .config import infra_analytics_config

def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config
    
def hdfs_file_exists(path):
    result = subprocess.run(['hdfs', 'dfs', '-test', '-e', path])
    return result.returncode == 0
    
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
        df['Quận có dấu']= df['Quận có dấu'].apply(lambda x: re.sub('(q |q|quận +)(\d)', func, x) )
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
        df['Quận không dấu']= df['Quận không dấu'].apply(lambda x: re.sub('(q |q|quận +)(\d)', func, x) )
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
        df['Phường có dấu'] = df['Phường có dấu'].apply(lambda x: re.sub('(^p |^p|phường +)(\d)', func, x))
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
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: re.sub('(^p |^p|phuong +)(\d)', func, x))
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: 'Phuong '+ str(int(x)) if (all(char.isdigit() for char in x)==True)&(x!='') else x)
        df['Phường không dấu'] = df['Phường không dấu'].apply(lambda x: text_normalize(str(x)))
        df['Phường không dấu'] = df['Phường không dấu'].str.strip('-|,|[ ]|.')
        df['Phường không dấu'] = df['Phường không dấu'].str.title()
def normalize_address(dau, df):
    """
        Chuẩn hoá Tỉnh, Quận/Huyện, Phường/Xã:
            + Loại bỏ ký tự đặc biệt, khoảng trắng, dấu câu 
            + Đồng bộ các thông tin và định danh địa chỉ 
    """
    if 'Tỉnh' in df.columns:
        print('normalize province')
        normalize_province(dau, df)
    if 'Quận' in df.columns:
        print('normalize district')
        normalize_district(dau, df)
    if 'Phường' in df.columns:
        print('normalize ward')
        normalize_ward(dau, df)
def connection_v2(user_name,pwd,host,db_name,port):
    """
    Make connection to database postgresql
    """
    try:
        engine = pg.connect(dbname=db_name, user=user_name, host=host, port=port, password=pwd)
    except:
        print ("I am unable to connect to the database")
    return engine
def process_insert_customer_province(date_init, config : dict = infra_analytics_config):
    """
        + Load và chuẩn hoá dữ liệu tỉnh/vùng từ postgresql 177 - dwh_noc - public.dwh_province
        + Load dữ liệu hạ tầng port: ftel_dwh_infra.infor_port_monthly (hive) => chuẩn hoá địa chỉ và summary thông tin port ở mức tỉnh 
        + Load dữ liệu khách hàng: ftel_dm_opt_customer.stag_idatapay_daily (hive)=> tính tổng khách hàng ở mức tỉnh 
        + Load dữ liệu khách hàng rời mạng: ftel_dm_opt_customer.stag_idatapay_daily (hive) => tính tổng khách hàng rời mạng ở mức tỉnh 
        +  Load dữ liệu khách hàng nợ cước: ftel_dm_opt_customer.stag_idatapay_daily (hive) => tính tổng khách hàng nợ cước ở mức tỉnh 
        + Chuẩn hoá địa chỉ và mapping các thông tin trên 
        + Load dữ liệu hộ dân: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/ho_dan.parquet => chuẩn hoá địa chỉ và summary hộ dân ở mức tỉnh 
        + Mapping tất cả thông tin trên và lưu xuống postgresql 177 - dwh_noc - public.tbl_customer_province
    """
    date = (datetime.strptime(date_init, '%Y-%m-%d') - relativedelta(days=1)).strftime('%Y-%m-%d')
    if (int(date[5:7])>=7)&(int(date[5:7])<=12):
        start = str(int(date[:4]))+'-07-01'
        kydautu = '2H'+str(int(date[:4]))
    else:
        kydautu= '1H'+str(int(date[:4]))
        start = str(int(date[:4])) + '-01-01'
    print(kydautu)
    r = relativedelta(datetime.strptime(date_init, '%Y-%m-%d'), datetime.strptime(start, '%Y-%m-%d'))
    list_month =  []
    for i in range(r.months):
        start_month = (datetime.strptime(date_init, '%Y-%m-%d') - relativedelta(months=i)).strftime('%Y-%m-01')
        list_month.append(start_month)
    assert config != None, "config must be not None"
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                          ,config['dbs']['dwh_177_public']['password']
                                                         ,config['dbs']['dwh_177_public']['host']
                                                        ,config['dbs']['dwh_177_public']['port']
                                                        ,config['dbs']['dwh_177_public']['dbname']))
    query = """SELECT * FROM public.%s"""% (config['feature_ptht']['tablename_province'])
    df_branch = pd.read_sql(query, conn)
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
    sql_str = """select * from ftel_dwh_infra.{} where date>='{}'
            and date<'{}'""".format(config['infor_port_monthly']['table_output'],start,date_init)
    df_port= spark.sql(sql_str)
    df_port = df_port.withColumn('region', f.regexp_replace('region', 'Vung', 'Vùng')) 
    df_port= df_port.withColumn('province',f.upper(f.col('name').substr(1, 3)))
    df_port = df_port.filter((df_port.name!='')&(df_port.port>0))
    df_port_grp = df_port.sort(f.desc('region'), f.desc('province'),f.desc('name'),
                                   f.desc('port'))
    df_port_grp= df_port_grp.dropDuplicates(subset=['province', 'name'])
    df_info_port_grp  = df_port_grp.groupBy(['province']).agg(
    f.sum('port').alias('port'),f.sum('portuse').alias('portuse'),f.sum('portfree').alias('portfree')
    ,f.sum('portdie').alias('portdie')  ,f.sum('portmaintain').alias('portmaintain'), f.countDistinct('name').alias('num_device'))
    df_info_port_pd = df_info_port_grp.toPandas()
    df_info_port_pd['province'] = df_info_port_pd['province'].str.upper()
    df_port_hh_full= df_info_port_pd.merge(df_branch_region,on='province', how='left')
    df_port_hh_full.rename({'name':'Tỉnh'},axis=1,inplace=True)
    str_slq = """SELECT  *
                FROM ftel_dm_opt_customer.{}
                WHERE d ='{}'""".format(config['feature_ptht']['table_idatapay'],date_init)
    df_khg = spark.sql(str_slq)
    df_khg_grp = df_khg.groupBy(['province']).agg(f.countDistinct('contract').alias('num_khg'))
    df_khg_pd =  df_khg_grp.toPandas()
    
    str_slq = """SELECT  *
            FROM ftel_dm_opt_customer.{}
            WHERE net_status in ('Da cham dut hop dong','Chu thue bao di vang')
            and d  in ('{}')""".format(config['feature_ptht']['table_idatapay'],', '.join(z for z in list_month).replace(", ","','"))
    df_roimang = spark.sql(str_slq)
    df_roimang = df_roimang.withColumn('month',f.trunc("d", "month"))
    df_roimang_grp = df_roimang.groupBy(['province','month']).agg(f.countDistinct('contract').alias('khg_roimang'))
    df_roimang_pd = df_roimang_grp.toPandas()
    df_roimang_pd_grp = df_roimang_pd.groupby(['province'],as_index=False).agg({'khg_roimang':'mean'})
    df_roimang_pd_grp['khg_roimang'] = df_roimang_pd_grp['khg_roimang'].astype(int)
    
    str_slq = """SELECT  *
                FROM ftel_dm_opt_customer.{}
                WHERE net_status in ('Ngung vi ly do thanh toan')
                and d  in ('{}')""".format(config['feature_ptht']['table_idatapay'],', '.join(z for z in list_month).replace(", ","','"))
    df_nocuoc = spark.sql(str_slq)
    df_nocuoc = df_nocuoc.withColumn('month',f.trunc("d", "month"))
    df_nocuoc_grp = df_nocuoc.groupBy(['province','month']).agg(f.countDistinct('contract').alias('khg_nocuoc'))
    df_nocuoc_pd = df_nocuoc_grp.toPandas()
    df_nocuoc_pd_grp = df_nocuoc_pd.groupby(['province'],as_index=False).agg({'khg_nocuoc':'mean'})
    df_nocuoc_pd_grp['khg_nocuoc'] = df_nocuoc_pd_grp['khg_nocuoc'].astype(int)
    
    df_port_hh_full_ = df_port_hh_full[[ 'Tỉnh', 'region','port', 'portuse', 'portfree', 'portdie', 'portmaintain',
           'num_device']]
    df_port_hh_full_.columns=[ 'province', 'region','port', 'portuse', 'portfree', 'portdie', 'portmaintain',
           'num_device']
    df_full = df_khg_pd.merge(df_roimang_pd_grp, on=['province'], how='outer')
    df_full = df_full.merge(df_nocuoc_pd_grp, on=['province'], how='outer')
    df_full.replace({'province':{'Nha Trang':'Khanh Hoa','Hue':'Thua Thien Hue','Vung Tau':'Ba Ria Vung Tau'}},
                   regex=True,inplace=True)
    df_full = df_full.merge(df_port_hh_full_, on=['province'], how='outer')
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    df_tinh = pd.read_sql("select tinh_co_dau,tinh_khong_dau from  report.{} group by tinh_co_dau,tinh_khong_dau".format(config['insert_dashboard']['table_ptht']), conn)
    conn.close()
    df_tinh.columns = ['tinh_co_dau', 'province']
    df_full_ = df_full.merge(df_tinh, on='province', how='left')
    df_full_ = df_full_[['region', 'tinh_co_dau', 'num_khg', 'khg_roimang', 'khg_nocuoc', 'port',
           'portuse', 'portfree', 'portdie', 'portmaintain', 'num_device']]
    df_full_.rename({'region':'vung'},axis=1, inplace=True)
    df_danso = spark.read.parquet(config['data_import']['hodan_path_output']+'d={}-01-01'.format(kydautu[2:])).toPandas()
    normalize_address('Có dấu',df_danso)
    df_danso.replace({'Phường có dấu':{'Xã A Roằng':'Xã A Roàng'}},regex=True, inplace=True)
    df_danso.drop({'Mã tỉnh','Mã quận','Mã phường'},axis=1,inplace=True)
    df_ds_grp = df_danso.groupby(['Tỉnh có dấu']).agg({'Tổng hộ':'sum'}).reset_index()
    df_ds_grp.columns = ['tinh_co_dau', 'tong_ho']
    df_full_1= df_full_.merge(df_ds_grp, on='tinh_co_dau', how='outer')
    df_full_1['ky_dau_tu']= kydautu
    df_full_1 = df_full_1[['ky_dau_tu','vung', 'tinh_co_dau', 'num_khg', 'khg_roimang', 'khg_nocuoc', 'port',
       'portuse', 'portfree', 'portdie', 'portmaintain', 'num_device', 'tong_ho']]
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    cur = conn.cursor()
    tablename =config['insert_dashboard']['table_customer_province']
    sql = """DELETE FROM """ + tablename + """ WHERE ky_dau_tu = '""" + kydautu + """';"""
    cur.execute(sql)
    conn.commit()
    engine = create_engine("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    df_full_1.to_sql(tablename, engine, if_exists='append', index=False)

def insert_info_bcc2(month_init, config: dict = infra_analytics_config):
    """
        + Load và chuẩn hoá dữ liệu tỉnh/vùng từ postgresql 177 - dwh_noc - public.dwh_province
        + Load dữ liệu bộ chia tập điểm cấp 2: ftel_dwh_infra.splitter_level_2_info (hive)
        + Transform dữ liệu đặc biệt, missing, convert datatype 
        + Xử lý createdate khi missing: lấy ngày thi công hoặc lấy createdate min 
        + Tính tuổi thiết bị: ngày lấy dữ liệu - ngày tạo 
        + Xử lý dữ liệu duplicate  => chuẩn hoá dữ liệu địa chỉ 
        + Lấy dữ liệu chi phí đầu tư từ postgresql - dwh_noc - public.tbl_planning_history
        + Load dữ liệu billing khách hàng: ftel_dm_opt_customer.scd_billing_user (Hive) => CHuẩn hoá địa chỉ và tính trung bình doanh thu POP-Tỉnh 
        + Mapping tất cả thông tin -> chuẩn hoá địa chỉ-> xử lý dữ liệu missing 
        + Lưu xuống postgresql 177 - dwhn_noc - report.dmt_info_bcc2
    """
    m= (datetime.strptime(month_init, '%Y-%m-%d')).strftime('%Y-%m-01')
    print(m)
    m_prev = (datetime.strptime(m, '%Y-%m-%d') - relativedelta(months=1)).strftime('%Y-%m-01')
    m_ = (datetime.strptime(m, '%Y-%m-%d') - relativedelta(months=2)).strftime('%Y-%m-01')
    next_m = (datetime.strptime(m, '%Y-%m-%d') + relativedelta(months=1)).strftime('%Y-%m-01')
    assert config != None, "config must be not None"
    
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    query = """SELECT * FROM public.%s"""% (config['feature_ptht']['tablename_province'])
    df_branch = pd.read_sql(query, conn)
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
    df_branch_province.columns = ['Tỉnh', 'province']
    df_province_spk = spark.createDataFrame(df_branch_region)
    
    sql_str = """select * from ftel_dwh_infra.{} where d>='{}' and d<'{}'""".format(config['splitter_lv2']['table_output'],m_,next_m)
    df= spark.sql(sql_str)
    df = df.withColumn('province',upper(col('bo_chia_cap_2').substr(1, 3)))
    df = df.join(df_province_spk, on='province', how='left')
    df = df.withColumnRenamed("province", "branch").withColumnRenamed("name", "Tỉnh")
    df = df.withColumn('popname',upper(col('bo_chia_cap_2').substr(1, 7)))
    df = df.withColumnRenamed("sum_port_cai_dat", "port").withColumnRenamed("sum_port_cai_dat_dang_dung", "portuse")\
            .withColumnRenamed("sum_port_cai_dat_free", "portfree")\
            .withColumnRenamed("ngay_su_dung", "createdate")
    df_filter = df.filter(df.Plans.isNotNull())
    df_filter = df_filter.withColumn("month", f.trunc("d", "month"))
    df_filter = df_filter.withColumn('createdate', when(df_filter.createdate.isNull(),df_filter.ngay_thi_cong).otherwise(df_filter.createdate))
    df_filter = df_filter.withColumn('createdate',to_timestamp('createdate'))
    df_filter = df_filter.withColumn("createdate", 
                   when(df_filter.ngay_thi_cong>df_filter.createdate,df_filter.ngay_thi_cong)
                   .otherwise(df_filter.createdate))
    df_drp = df_filter.groupBy(['Plans','region','branch','Tỉnh','Ward','District','popname','bo_chia_cap_2',
               'hop_dau_noi','port','portuse','portfree','createdate', 'date_time','month']).agg(count(col('d')).alias('num_row')).cache()
    df_old =df_filter.groupBy(['Plans','region','branch','Tỉnh','Ward','District','popname','hop_dau_noi','bo_chia_cap_2']).agg(min(col('createdate')).alias('used_date')).cache()
    df_full = df_drp.join(df_old, on=['Plans','region','branch','Tỉnh','Ward','District','popname','hop_dau_noi','bo_chia_cap_2'], how='left').cache()
    df_full= df_full.withColumn("month_old_device", round(months_between(col("date_time"),col("used_date")),0)).cache()
    df_full_prp = df_full.sort(col("Plans").desc(),col("region").desc(),col("branch").desc()
             ,col("popname").desc(),col("hop_dau_noi").desc(),col("bo_chia_cap_2").desc(),col("Tỉnh").desc(),col("Ward").desc()
          ,col("District").desc(),col("month").desc(),col("date_time").desc())
    df_full_prp = df_full_prp.dropDuplicates(['Plans','region', 'branch', 'popname', 'hop_dau_noi',"bo_chia_cap_2",
                  'Tỉnh', 'Ward','District']).cache()
    df_full_prp =  df_full_prp.filter(df_full_prp.Plans!='')
    df_full_prp = df_full_prp.withColumn('createdate',col("createdate").cast("string"))
    df_full_prp = df_full_prp.withColumn('month',col("month").cast("string"))
    df_full_prp = df_full_prp.withColumn('ky_dau_tu',when((f.month(df_full_prp.createdate)>=1)&\
                                (f.month(df_full_prp.createdate)<7),concat(lit('1H'),lit(year(df_full_prp.createdate))))\
                                .otherwise(concat(lit('2H'),lit(year(df_full_prp.createdate)))))
    df_full_pd = df_full_prp.select('Plans','popname','region','Tỉnh','Ward','District','hop_dau_noi','bo_chia_cap_2','createdate',
                       'port','portuse','portfree','month','ky_dau_tu').toPandas()
    df_full_pd.columns = ['Mã kế hoạch', 'POP', 'Vùng', 'Tỉnh', 'Phường', 'Quận', 'hop_dau_noi',
           'bo_chia_cap_2', 'Ngày sử dụng', 'port', 'portuse', 'portfree', 'month','ky_dau_tu']
    df_full_pd['month'] = m
    df_full_pd['month'] = pd.to_datetime(df_full_pd['month'])
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    str_sql = "select * from  public.%s"%(config['feature_ptht']['table_planning'])
    df_dt_dk = pd.read_sql(str_sql, conn)
    conn.close()
    df_dt_dk_grp = df_dt_dk.groupby(['ma_ke_hoach','perport'],as_index=False).agg({
        'ky_dau_tu':'count'})[['ma_ke_hoach','perport']]
    df_dt_dk_grp.columns = ['Mã kế hoạch','Perport']
    
    df_full_final = df_full_pd.merge(df_dt_dk_grp, on='Mã kế hoạch', how='left')
    normalize_address('Không dấu', df_full_final)
    df_full_final.replace({'Nha Trang':'Khanh Hoa','^Ba Ria$':'Ba Ria Vung Tau'}, regex=True, inplace=True)
    df_dt_dk['province'] = df_dt_dk['pop'].str[:3]
    df_dt_dk_pop = df_dt_dk.groupby(['pop','ky_dau_tu'],as_index=False).agg({'perport':'mean'})[['ky_dau_tu','pop','perport']]
    df_dt_dk_pop.rename({'perport':'perport_pop','pop':'POP'},axis=1, inplace=True)
    df_full_final = df_full_final.merge(df_dt_dk_pop, on=['POP','ky_dau_tu'], how='left')
    df_full_final['Perport'] = np.where(df_full_final['Perport'].isna(),df_full_final['perport_pop']
                                        ,df_full_final['Perport'])
    spark.sql("refresh table ftel_dm_opt_customer.%s"%(config['insert_dashboard']['table_billing']))
    spark.sql("refresh table ftel_dwh_isc.%s"%(config['feature_ptht']['table_demographic']))
    spark.sql("refresh table ftel_dwh_isc.%s"%(config['feature_ptht']['table_contract']))
    sql = """SELECT b.m, c.region,c.province,c.branch, d.ward as ward_addr,
                d.district as district_addr,LEFT (c.group_point, 7) as POP, sum(b.internet_fee) as internet_fee, count(b.contract) as KHG_cuoc
                FROM (ftel_dm_opt_customer.{} b LEFT JOIN ftel_dwh_isc.{} c
                ON b.contract =c.contract)
                LEFT JOIN ftel_dwh_isc.{} d
                ON b.contract = d.contract
                WHERE m = '{}'
                GROUP BY b.m, c.region,c.province,c.branch, d.ward, d.district,LEFT (c.group_point, 7)
                """.format(config['insert_dashboard']['table_billing'],config['feature_ptht']['table_contract'],
                           config['feature_ptht']['table_demographic'],m_prev)
    df_billing = spark.sql(sql).cache()
    df_billing_pd =  df_billing.filter(df_billing.internet_fee>0).toPandas()
    df_billing_pd['Tb_doanhthu']= df_billing_pd['internet_fee']/df_billing_pd['KHG_cuoc']
    df_billing_pd.columns = ['month', 'Vùng', 'Tỉnh', 'Chi nhánh', 'Phường', 'Quận',
           'POP', 'internet_fee', 'KHG_cuoc', 'Tb_doanhthu']
    normalize_address('Không dấu', df_billing_pd)
    df_billing_pd.replace({'Nha Trang':'Khanh Hoa','^Vung Tau$':'Ba Ria Vung Tau','^Hue$':'Thua Thien Hue'}, regex=True, inplace=True)
    
    df_billing_gp = df_billing_pd.groupby(['POP','Phường không dấu','Quận không dấu','Tỉnh không dấu'],
                                          as_index=False).agg({'Tb_doanhthu':'mean'})
    df_full_final = df_full_final.merge(df_billing_gp, on=['POP','Phường không dấu','Quận không dấu','Tỉnh không dấu'], how='left')
    
    df_billing_gp_q = df_billing_pd.groupby(['POP','Quận không dấu','Tỉnh không dấu'],
                                          as_index=False).agg({'Tb_doanhthu':'mean'})
    df_billing_gp_q.rename({'Tb_doanhthu':'Tb_doanhthu_q'},axis=1, inplace=True)
    df_full_final = df_full_final.merge(df_billing_gp_q, on=['POP','Quận không dấu',
                                   'Tỉnh không dấu'], how='left')
    df_full_final['Tb_doanhthu'] = np.where(df_full_final['Tb_doanhthu'].isna(),
                                            df_full_final['Tb_doanhthu_q'],df_full_final['Tb_doanhthu'])
    
    df_billing_gp_tp = df_billing_pd.groupby(['POP','Tỉnh không dấu'],
                                          as_index=False).agg({'Tb_doanhthu':'mean'})
    df_billing_gp_tp.rename({'Tb_doanhthu':'Tb_doanhthu_tp'},axis=1, inplace=True)
    df_full_final = df_full_final.merge(df_billing_gp_tp, on=['POP',
                                   'Tỉnh không dấu'], how='left')
    df_full_final['Tb_doanhthu'] = np.where(df_full_final['Tb_doanhthu'].isna(),
                                            df_full_final['Tb_doanhthu_tp'],df_full_final['Tb_doanhthu'])
    
    df_billing_gp_t = df_billing_pd.groupby(['Tỉnh không dấu'],
                                          as_index=False).agg({'Tb_doanhthu':'mean'})
    df_billing_gp_t.rename({'Tb_doanhthu':'Tb_doanhthu_t'},axis=1, inplace=True)
    df_full_final = df_full_final.merge(df_billing_gp_t, on=[
                                   'Tỉnh không dấu'], how='left')
    df_full_final['Tb_doanhthu'] = np.where(df_full_final['Tb_doanhthu'].isna(),
                                            df_full_final['Tb_doanhthu_t'],df_full_final['Tb_doanhthu'])
    df_full_final.drop({'Tb_doanhthu_q','perport_pop',
                    'Tb_doanhthu_tp','Tb_doanhthu_t','ky_dau_tu'}, axis=1, inplace=True)
    df_full_final['Perport'] = df_full_final['Perport'].astype(int, errors='ignore')
    df_full_final['Tb_doanhthu'] = df_full_final['Tb_doanhthu'].astype(int, errors='ignore')
    df_full_final['Ngày sử dụng'] = pd.to_datetime(df_full_final['Ngày sử dụng'])
    df_full_final.columns = ['ma_ke_hoach', 'pop', 'vung', 'tinh', 'phuong',
       'quan', 'hop_dau_noi', 'bo_chia_cap_2', 'ngay_su_dung',
       'port', 'portuse', 'portfree', 'month', 'perport', 'tb_doanhthu']
    df_full_final = df_full_final[['ma_ke_hoach', 'pop', 'vung', 'tinh', 'phuong',
       'quan', 'hop_dau_noi', 'bo_chia_cap_2', 'ngay_su_dung',
       'port', 'portuse', 'portfree', 'perport', 'tb_doanhthu', 'month']]
    df_full_final = df_full_final.sort_values(['ma_ke_hoach', 'pop', 'vung', 'tinh', 'phuong', 'quan', 'hop_dau_noi',
       'bo_chia_cap_2', 'ngay_su_dung', 'port', 'portuse', 'portfree',
       'perport', 'tb_doanhthu', 'month'], ascending=False)
    df_full_final.drop_duplicates(subset=['ma_ke_hoach', 'pop', 'vung', 'tinh', 'phuong', 'quan', 'hop_dau_noi',
       'bo_chia_cap_2', 'ngay_su_dung', 'month'], keep='first', inplace=True)
    df_full_final = df_full_final.sort_values(['ma_ke_hoach', 'pop', 'vung', 'tinh', 'phuong', 'quan', 'hop_dau_noi',
       'bo_chia_cap_2', 'ngay_su_dung', 'port', 'portuse', 'portfree',
       'perport', 'tb_doanhthu', 'month'], ascending=False)
    # df_full_final.drop_duplicates(subset=['ma_ke_hoach', 'pop', 'vung', 'tinh', 'phuong', 'quan', 'hop_dau_noi',
    #    'bo_chia_cap_2', 'ngay_su_dung', 'month'], keep='first', inplace=True)
    df_full_final['vung']= df_full_final['vung'].fillna('')
    df_full_final['tinh']= df_full_final['tinh'].fillna('')
    df_full_final.drop_duplicates(subset=['ma_ke_hoach', 'pop', 'vung', 'tinh', 'phuong', 'quan', 'hop_dau_noi',
       'bo_chia_cap_2', 'month'], keep='first', inplace=True)
    
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    cur = conn.cursor()
    tablename = config['insert_dashboard']['table_bcc2']
    sql = """DELETE FROM report.""" + tablename + """ WHERE month = '""" + m + """';"""
    cur.execute(sql)
    conn.commit()
    engine = create_engine("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    df_full_final.to_sql(tablename, engine, if_exists='append', index=False, schema='report')
    
def get_ngaybatdau(kydautu):
    if kydautu[0]=='1':
        ngaybatdau = str(kydautu[2:])+'-01-01'
    else:
        ngaybatdau = str(kydautu[2:])+'-07-01'
    return ngaybatdau
def insert_dashboard_ptht(date, config: dict = infra_analytics_config):
    """
        + Load các chỉ số feature model dự án từ  ftel_dwh_infra.ds_feature_ptht (theo kỳ đầu tư) và kết quả dự đoán của dự án từ /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/result_phattrienhatang.parquet
        + Chuẩn hoá dữ liệu địa chỉ, xử lý duplicates, lưu trữ kết quả xuống postgresql 177- dwh_noc - report.dmt_dashboard_ptht
    """
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
    prev_month = (datetime.strptime(date, '%Y-%m-%d') - relativedelta(months=6))
    assert config != None, "config must be not None"
    if (int(date[5:7])==3)|(int(date[5:7])==9):
        sql_str = """select * from ftel_dwh_infra.{} where ky_dau_tu= '{}'""".format(config['feature_ptht']['table_feature'], kydautu)
        df_feature_= spark.sql(sql_str)
        df_feature_ = df_feature_.toPandas()
        df_score = spark.read.parquet(config['training_model']['result_phattrienhatang_path']+'kydautu={}'.format(kydautu)).toPandas()
        df_score = df_score[['phuong', 'quan', 'tinh','score', 'de_xuat', 'DL_range','surv_prob']]
        df_feature_ = df_feature_.merge(df_score, on=['phuong', 'quan', 'tinh'], how='left')
        df_feature_.rename({'quan':'Quận','phuong':'Phường','tinh':'Tỉnh'},axis=1,inplace=True)
        normalize_address('Có dấu', df_feature_)
        
        df_kydautu = pd.DataFrame({'ky_dau_tu':df_feature_['ky_dau_tu'].unique()})
        df_kydautu['ngay_dau_tu'] = df_kydautu['ky_dau_tu'].apply(lambda x: get_ngaybatdau(x))
        df_kydautu['ngay_dau_tu'] = pd.to_datetime(df_kydautu['ngay_dau_tu'])
        df_feature_ = df_feature_.merge(df_kydautu, on='ky_dau_tu', how='left')
        
        df_feature_.columns = ['quan_co_dau', 'phuong_co_dau', 'tinh_co_dau','vung','ky_dau_tu',
         'chi_nhanh','port_6t_hien_tai','port_dung_6t_hien_tai','hqkt_6t_hieu_tai','nguong_danh_gia',
         'danh_gia_hieu_qua','dien_tich','tong_dan','thanh_thi','nong_thon','tong_so_ho','duoi_tieu_hoc','tieu_hoc','trung_hoc','cao_dang',
         'dai_hoc', 'thac_sy', 'tien_sy', 'mat_do_dan_so', 'mat_do_ho_dan', 'thu_nhap', 'so_benh_vien', 'so_co_so_y_te',
         'so_truong_tieu_hoc', 'so_truong_trung_hoc','so_truong_pho_thong','so_truong_cao_dang','so_truong_dai_hoc',
         'so_doanh_nghiep','so_doanh_nghiep_von_nuoc_ngoai','so_doanh_nghiep_xuat_nhap_khau','so_kinh_doanh_ca_the',
         'so_doanh_nghiep_khach_san','so_ca_the_khach_san','so_doanh_nghiep_vua_nho','so_doanh_nghiep_cntt','so_doanh_nghiep_ttdt',
         'so_cho','so_sieu_thi', 'so_trung_tam_thuong_mai', 'so_san_bay', 'so_cang', 'so_duongga', 'so_caotoc', 'loi_olt',
         'so_ticket', 'thoi_gian_loi', 'name_device', 'khach_hang_anh_huong', 'so_ngan_hang', 'so_vp', 'so_shop', 'ap_doi_thu', 'khach_hang_roi_mang',
         'khach_hang_no_cuoc', 'khach_hang', 'ti_le_roi_mang', 'ti_le_no_cuoc', 'so_checlist', 'avg_operation_pop', 'avg_quality_pop', 'thoi_gian_dau_tu_gan_nhat',
         'so_khdt_truoc', 'dung_luong_trien_khai', 'khai_thác_sau_3t', 'khai_thác_sau_6t', 'khai_thác_sau_9t', 'khai_thác_sau_12t',
         'perport','tl_portfree_sau_3t','tl_portfree_sau_6t','tl_portfree_sau_9t','tl_portfree_sau_12t','ibb','dai_ly_canh_to',
         'so_hd_voi_kh','doanh_thu','t1','t2','t3','t4','t5','tuoi','port','portuse','portfree','portdie','portmaintain',
         'num_device','dl_kh','rate_port_use','rate_port_free','tp_ftel','ftel_doithu','create_date'
          ,'scoring','de_xuat','dung_luong','surv_prob','tinh_khong_dau','quan_khong_dau','phuong_khong_dau','ngay_dau_tu']
        conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
        query = """SELECT * FROM public.%s"""%(config['feature_ptht']['tablename_province'])
        df_branch = pd.read_sql(query, conn)
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
        df_branch_region = df_branch_region[df_branch_region.province!='NTG']
        df_branch_province = df_branch_region[['name','province']]
        df_branch_province.columns = ['tinh_khong_dau','ma_tinh']
        df_feature_ = df_feature_.merge(df_branch_province, on='tinh_khong_dau',how='left')
        df_feature_ = df_feature_[['quan_co_dau', 'phuong_co_dau', 'tinh_co_dau', 'quan_khong_dau',
        'phuong_khong_dau', 'tinh_khong_dau', 'ma_tinh', 'chi_nhanh', 'vung',
        'port_6t_hien_tai', 'port_dung_6t_hien_tai', 'nguong_danh_gia',
        'danh_gia_hieu_qua', 'ky_dau_tu','ngay_dau_tu', 'dien_tich', 'tong_dan', 'thanh_thi',
        'nong_thon', 'tong_so_ho', 'duoi_tieu_hoc', 'tieu_hoc', 'trung_hoc',
        'cao_dang', 'dai_hoc', 'thac_sy', 'tien_sy', 'mat_do_dan_so', 'mat_do_ho_dan',
        'thu_nhap', 'so_benh_vien', 'so_co_so_y_te', 'so_truong_tieu_hoc',
        'so_truong_trung_hoc', 'so_truong_pho_thong', 'so_truong_cao_dang',
        'so_truong_dai_hoc', 'so_doanh_nghiep',
        'so_doanh_nghiep_von_nuoc_ngoai', 'so_doanh_nghiep_xuat_nhap_khau',
        'so_kinh_doanh_ca_the', 'so_doanh_nghiep_khach_san',
        'so_ca_the_khach_san', 'so_doanh_nghiep_vua_nho',
        'so_doanh_nghiep_cntt', 'so_doanh_nghiep_ttdt', 'so_cho', 'so_sieu_thi',
        'so_trung_tam_thuong_mai', 'so_san_bay', 'so_cang', 'so_duongga',
        'so_caotoc', 'loi_olt', 'so_ticket', 'thoi_gian_loi', 'khach_hang_anh_huong',
        'so_checlist', 'so_ngan_hang', 'so_vp', 'so_shop', 'ap_doi_thu',
        'khach_hang_roi_mang', 'khach_hang_no_cuoc', 'khach_hang', 'ti_le_roi_mang', 'ti_le_no_cuoc',
        'avg_operation_pop', 'avg_quality_pop', 'thoi_gian_dau_tu_gan_nhat',
        'so_khdt_truoc', 'dung_luong_trien_khai', 'khai_thác_sau_3t',
        'khai_thác_sau_6t', 'khai_thác_sau_9t', 'khai_thác_sau_12t',
        'perport', 'ibb', 'dai_ly_canh_to', 'so_hd_voi_kh', 'doanh_thu', 't1',
        't2', 't3', 't4', 't5', 'tuoi', 'port', 'portuse', 'portfree',
        'portdie', 'portmaintain', 'num_device' ,'scoring','de_xuat','dung_luong','surv_prob']]
        df_feature_ = df_feature_.sort_values(['quan_co_dau', 'phuong_co_dau', 'tinh_co_dau', 'quan_khong_dau',
               'phuong_khong_dau', 'tinh_khong_dau', 'ma_tinh', 'chi_nhanh', 'vung',
               'port_6t_hien_tai', 'port_dung_6t_hien_tai', 'nguong_danh_gia',
               'danh_gia_hieu_qua', 'ky_dau_tu', 'ngay_dau_tu', 'dien_tich',
               'tong_dan', 'thanh_thi', 'nong_thon', 'tong_so_ho', 'duoi_tieu_hoc',
               'tieu_hoc', 'trung_hoc', 'cao_dang', 'dai_hoc', 'thac_sy', 'tien_sy',
               'mat_do_dan_so', 'mat_do_ho_dan', 'thu_nhap', 'so_benh_vien',
               'so_co_so_y_te', 'so_truong_tieu_hoc', 'so_truong_trung_hoc',
               'so_truong_pho_thong', 'so_truong_cao_dang', 'so_truong_dai_hoc',
               'so_doanh_nghiep', 'so_doanh_nghiep_von_nuoc_ngoai',
               'so_doanh_nghiep_xuat_nhap_khau', 'so_kinh_doanh_ca_the',
               'so_doanh_nghiep_khach_san', 'so_ca_the_khach_san',
               'so_doanh_nghiep_vua_nho', 'so_doanh_nghiep_cntt',
               'so_doanh_nghiep_ttdt', 'so_cho', 'so_sieu_thi',
               'so_trung_tam_thuong_mai', 'so_san_bay', 'so_cang', 'so_duongga',
               'so_caotoc', 'loi_olt', 'so_ticket', 'thoi_gian_loi',
               'khach_hang_anh_huong', 'so_checlist', 'so_ngan_hang', 'so_vp',
               'so_shop', 'ap_doi_thu', 'khach_hang_roi_mang', 'khach_hang_no_cuoc',
               'khach_hang', 'ti_le_roi_mang', 'ti_le_no_cuoc', 'avg_operation_pop',
               'avg_quality_pop', 'thoi_gian_dau_tu_gan_nhat', 'so_khdt_truoc',
               'dung_luong_trien_khai', 'khai_thác_sau_3t', 'khai_thác_sau_6t',
               'khai_thác_sau_9t', 'khai_thác_sau_12t', 'perport', 'ibb',
               'dai_ly_canh_to', 'so_hd_voi_kh', 'doanh_thu', 't1', 't2', 't3', 't4',
               't5', 'tuoi', 'port', 'portuse', 'portfree', 'portdie', 'portmaintain',
               'num_device' ,'scoring','de_xuat','dung_luong','surv_prob'],ascending=False)
        df_feature_.drop_duplicates(subset=['quan_co_dau', 'phuong_co_dau', 'tinh_co_dau', 'quan_khong_dau',
               'phuong_khong_dau', 'tinh_khong_dau', 'ma_tinh', 'chi_nhanh', 'vung',
               'port_6t_hien_tai', 'port_dung_6t_hien_tai', 'nguong_danh_gia',
               'danh_gia_hieu_qua', 'ky_dau_tu', 'ngay_dau_tu'],inplace=True)
        df_feature_['de_xuat'] = np.where((df_feature_['de_xuat']=='Đề xuất')&(df_feature_['dung_luong'].isna()),'Không đề xuất',df_feature_['de_xuat'])
        conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
        cur = conn.cursor()
        tablename =config['insert_dashboard']['table_ptht']
        sql = """DELETE FROM report.""" + tablename + """ WHERE ky_dau_tu = '""" + kydautu + """';"""
        cur.execute(sql)
        conn.commit()
        engine = create_engine("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                              ,config['dbs']['dwh_177_report']['password']
                                                             ,config['dbs']['dwh_177_report']['host']
                                                            ,config['dbs']['dwh_177_report']['port']
                                                            ,config['dbs']['dwh_177_report']['dbname']))
        df_feature_.to_sql(tablename, engine, if_exists='append', index=False, schema='report')
        
def insert_province_bi(config: dict = infra_analytics_config):
    """
        + Load thông tin xã/phường toàn quốc từ postgresql 177 - dwh_noc - report.dmt_dashboard_ptht
        + Upsert vào bảng smartops.tbl_province_bi (postgresql 177 - dwh_noc)
    """
    assert config != None, "config must be not None"
        
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    df_tinh_vung = pd.read_sql("select tinh_khong_dau from  report.%s group by tinh_khong_dau"%(config['insert_dashboard']['table_ptht']), conn)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                          ,config['dbs']['dwh_177_public']['password']
                                                         ,config['dbs']['dwh_177_public']['host']
                                                        ,config['dbs']['dwh_177_public']['port']
                                                        ,config['dbs']['dwh_177_public']['dbname']))
    df_tinh = pd.read_sql("select * from smartops.%s"%(config['insert_dashboard']['table_provincebi']), conn)
    conn.close()
    df_tinh['tinh_khong_dau_goc'] = df_tinh['tinh_khong_dau']
    df_tinh['tinh_khong_dau'] = df_tinh['tinh_khong_dau'].str.strip('-|,|[ ]|.')
    df_tinh_full = df_tinh.merge(df_tinh_vung, on='tinh_khong_dau', how='left')
    df_tinh_full.drop('tinh_khong_dau',axis=1,inplace=True)
    df_tinh_full.rename({'tinh_khong_dau_goc':'tinh_khong_dau'},axis=1,inplace=True)
    lst_data = df_tinh_full.values.tolist()
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur_1 = conn.cursor()
    for i in range(len(lst_data)):
        tupl = (lst_data[i])
        cur_1.execute(
        " INSERT INTO smartops.tbl_province_bi(tinh,vung,tinh_khong_dau) VALUES( %s, %s, %s)"
        " ON CONFLICT (tinh)"
        " DO UPDATE SET vung = EXCLUDED.vung, "
        "tinh_khong_dau = EXCLUDED.tinh_khong_dau;", (tuple(tupl))
        )
    try:
        conn.commit()
        conn.close()
        print("Successfully!!!!")
    except:
        print("Don't save DB")

def insert_dashboard_perfomance_monthly(end_date, config: dict = infra_analytics_config):
    """
        + Load dữ liệu hạ tầng port: ftel_dwh_infra.infor_port_monthly (hive) 
        + Mapping thông tin tỉnh thành =>  Tính tuổi thiết bị => Đánh index_month 
        + Chuẩn hoá dữ liệu địa chỉ => chuyển chiều dữ liệu để có các cột tốc độ tăng trưởng theo index_month 
        + Xử lý dữ liệu missing => lưu dữ liệu vào db postgresql 177 - dwh_noc - report.dmt_dashboard_perfomance_monthly
    """
    date = (datetime.strptime(end_date, '%Y-%m-%d') - relativedelta(days=1)).strftime('%Y-%m-%d')
    if (int(date[5:7])>=7)&(int(date[5:7])<=12):
        ky_dau_tu = '2H'+str(int(date[:4]))
        start_date = str(int(date[:4]))+'-07-01'
    else:
        ky_dau_tu= '1H'+str(int(date[:4]))
        start_date = str(int(date[:4])) + '-01-01'
    print(ky_dau_tu)
    r = relativedelta(datetime.strptime(end_date, '%Y-%m-%d'), datetime.strptime(start_date, '%Y-%m-%d'))
    assert config != None, "config must be not None"
    if (r.months + (12*r.years))>=1:
        query = """SELECT * 
        FROM ftel_dwh_infra.{}
        WHERE createdate>='{}' and createdate <'{}'""".format(config['infor_port_monthly']['table_output'],start_date, end_date)
        df = spark.sql(query)
        df = df.withColumn('region', regexp_replace('region', 'Vung', 'Vùng'))
        df = df.withColumn('province',upper(col('name').substr(1, 3)))
        
        conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
        query = """SELECT * FROM public.%s"""%(config['feature_ptht']['tablename_province'])
        df_branch = pd.read_sql(query, conn)
        df_province = df_branch[df_branch.region!='International'].groupby(['province','region','name'],as_index=False).agg({
        'full_name':'count'})[['province','region','name']]
        df_province_spk =spark.createDataFrame(df_province.astype(str))
        df_province_spk_ = df_province_spk.select(col('province'),col('name').alias('Tỉnh'))
        
        df = df.join(df_province_spk_, on='province', how='left')
        df_drp = df.groupBy(['region','branch','Tỉnh','district','ward','popname','name','port','portuse','portfree',
                    'portdie','portmaintain','createdate','date']).agg(count(col('d')).alias('num_row')).cache()
        df_full= df_drp.withColumn("month_old_device", round(months_between(col("date"),
                                                                            col("createdate")),0).cast(IntegerType())).cache()
        df_full_filter = df_full.filter((df_full.month_old_device>0)&(df_full.month_old_device<7))
        df_full_filter = df_full_filter.sort(col("region").desc(),col("branch").desc(),col("Tỉnh").desc(),col("district").desc(),col("ward").desc()
                 ,col("popname").desc(),col("name").desc(),col("createdate").desc(),col("month_old_device").desc(),col("date").desc())
        df_full_filter_1 = df_full_filter.dropDuplicates(['region','branch', 'Tỉnh', 'district', 'ward', 'popname',
                                                          'name',"createdate", 'month_old_device']).cache()
        df_full_pd  =  df_full_filter_1.toPandas()
        df_full_pd['index_month'] = df_full_pd['month_old_device'].apply(lambda x: 'T'+str(x))
        df_full_pd.columns = ['Vùng','branch', 'Tỉnh', 'Quận', 'Phường', 'popname', 'name', 'port',
               'portuse', 'portfree', 'portdie', 'portmaintain', 'createdate', 'date',
               'num_row', 'month_old_device', 'index_month']
        normalize_address('Không dấu', df_full_pd)
        df_full_pd.replace({'Tỉnh không dấu':{'Hue':'Thua Thien Hue','Ba Ria':'Ba Ria Vung Tau'}}, regex=True, inplace=True)
        df_full_pd= df_full_pd.sort_values(['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate', 'date','index_month'],ascending=True)
        df_full_pd.drop_duplicates(subset= ['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate','index_month'], keep='first', inplace=True)
        df_port_fil_mode = df_full_pd.groupby(['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate'],as_index=False)['port'].apply(lambda x: x.mode().iloc[0])
        df_port_fil_mode.columns = ['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate', 'port_mode']
        table_port = pd.pivot_table(df_full_pd, values='port', index=['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate'],columns=['index_month'], aggfunc="sum").reset_index()
        table_port =  table_port.merge(df_port_fil_mode, on=['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate'], how='left')
        list_columns = ['T1','T2','T3','T4','T5','T6']
        for i in list_columns:
            if i not in table_port.columns:
                table_port[i] = np.nan       
        table_port['T1'] = np.where(table_port['T1'].isna(),table_port['port_mode'],table_port['T1'])
        table_port['T2'] = np.where(table_port['T2'].isna(),table_port['port_mode'],table_port['T2'])
        table_port['T3'] = np.where(table_port['T3'].isna(),table_port['port_mode'],table_port['T3'])
        table_port['T4'] = np.where(table_port['T4'].isna(),table_port['port_mode'],table_port['T4'])
        table_port['T5'] = np.where(table_port['T5'].isna(),table_port['port_mode'],table_port['T5'])
        table_port['T6'] = np.where(table_port['T6'].isna(),table_port['port_mode'],table_port['T6'])
        table_port.drop('port_mode', axis=1, inplace=True)
        table_port.columns = ['Vùng', 'branch', 'Tỉnh', 'Quận', 'Phường', 'popname', 'name',
               'createdate', 'T1', 'T2', 'T3', 'T4', 'T5','T6']
        table_port_stack = table_port.set_index(['Vùng', 'branch', 'Tỉnh', 'Quận', 'Phường', 'popname', 'name',
               'createdate']).stack().reset_index(name='port').rename(columns={'level_8':'index_month'})
        
        df_portuse_fil_mode = df_full_pd.groupby(['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate'],as_index=False)['portuse'].apply(lambda x: x.mode().iloc[0])
        df_portuse_fil_mode.columns = ['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate', 'port_mode']
        
        table_portuse = pd.pivot_table(df_full_pd, values='portuse', index=['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate'],columns=['index_month'], aggfunc="sum").reset_index()
        table_portuse =  table_portuse.merge(df_portuse_fil_mode, on=['Vùng','branch', 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
               'popname', 'name', 'createdate'], how='left')
        for i in list_columns:
            if i not in table_portuse.columns:
                table_portuse[i] = np.nan  
        table_portuse['T1'] = np.where(table_portuse['T1'].isna(),table_portuse['port_mode'],table_portuse['T1'])
        table_portuse['T2'] = np.where(table_portuse['T2'].isna(),table_portuse['port_mode'],table_portuse['T2'])
        table_portuse['T3'] = np.where(table_portuse['T3'].isna(),table_portuse['port_mode'],table_portuse['T3'])
        table_portuse['T4'] = np.where(table_portuse['T4'].isna(),table_portuse['port_mode'],table_portuse['T4'])
        table_portuse['T5'] = np.where(table_portuse['T5'].isna(),table_portuse['port_mode'],table_portuse['T5'])
        table_portuse['T6'] = np.where(table_portuse['T6'].isna(),table_portuse['port_mode'],table_portuse['T6'])
        table_portuse.drop('port_mode', axis=1, inplace=True)
        
        table_portuse.columns = ['Vùng', 'branch', 'Tỉnh', 'Quận', 'Phường', 'popname', 'name',
               'createdate', 'T1', 'T2', 'T3', 'T4', 'T5','T6']
        table_portuse_stack = table_portuse.set_index(['Vùng', 'branch', 'Tỉnh', 'Quận', 'Phường', 'popname', 'name',
               'createdate']).stack().reset_index(name='portuse').rename(columns={'level_8':'index_month'})
        
        df_kt_monthly =  table_port_stack.merge(table_portuse_stack, on=['Vùng','branch', 'Tỉnh', 'Quận', 'Phường',
               'popname', 'name', 'createdate','index_month'], how='outer')
        df_kt_monthly_final = df_kt_monthly.groupby(['Tỉnh', 'Quận', 'Phường','index_month'],as_index=False).agg({
            'port':'sum','portuse':'sum'
        })
        df_kt_monthly_final.columns = [ 'tỉnh', 'quận', 'phường','index_month', 'port', 'portuse']
        conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
        query = """SELECT quan_co_dau,phuong_co_dau,tinh_co_dau,quan_khong_dau as Quận,
        phuong_khong_dau  as Phường,tinh_khong_dau as Tỉnh,chi_nhanh,vung 
        FROM report.%s"""%(config['insert_dashboard']['table_ptht'])
        df_dc = pd.read_sql(query, conn)
        df_full_final = df_kt_monthly_final.merge(df_dc, on =[ 'tỉnh', 'quận', 'phường'], how='left')
        df_full_final['phuong_co_dau'] = np.where(df_full_final['phuong_co_dau'].isna(),df_full_final['phường'],
                                                  df_full_final['phuong_co_dau'])
        df_full_final['quan_co_dau'] = np.where(df_full_final['quan_co_dau'].isna(),df_full_final['quận'],
                                                  df_full_final['quan_co_dau'])
        df_full_final['tinh_co_dau'] = np.where(df_full_final['tinh_co_dau'].isna(),df_full_final['tỉnh'],
                                                  df_full_final['tinh_co_dau'])
        df_full_final_w =  df_full_final[[ 'vung','chi_nhanh', 'tinh_co_dau','quan_co_dau', 'phuong_co_dau', 
                                          'index_month', 'port', 'portuse']]
        df_full_final_w['ky_dau_tu'] =ky_dau_tu
        df_full_final_w.columns = ['vung', 'chi_nhanh', 'tinh_co_dau', 'quan_co_dau', 'phuong_co_dau',
               'index_month', 'port', 'portuse', 'ky_dau_tu']
        conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
        cur = conn.cursor()
        tablename =config['insert_dashboard']['table_dashboard_perfomance']
        sql = """DELETE FROM report.""" + tablename + """ WHERE ky_dau_tu = '""" + ky_dau_tu + """';"""
        cur.execute(sql)
        conn.commit()
        engine = create_engine("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                              ,config['dbs']['dwh_177_report']['password']
                                                             ,config['dbs']['dwh_177_report']['host']
                                                            ,config['dbs']['dwh_177_report']['port']
                                                            ,config['dbs']['dwh_177_report']['dbname']))
        df_full_final_w.to_sql(tablename, engine, if_exists='append', index=False, schema='report')

def process_ibb(month, start_date, end_date, prev_month, config):
    """
        + Load dữ liệu nhân viên sale: ftel_dwh_isc.ds_sale_staff
        + Chuẩn hoá dữ liệu địa chỉ -> summary số nhân viên sale theo mức chi nhánh 
    """
    df_sale_staff =  spark.sql("""
        SELECT s.*,b.location,b.branch_name
        FROM ftel_dwh_isc.{} s LEFT JOIN ftel_dwh_isc.{} b
        ON s.location_id=b.location_id and s.branch_code=b.branch_code
        """.format(config['feature_ptht']['table_sale_staff'],config['feature_ptht']['table_location'])).cache()
    df_sale_staff_pd = df_sale_staff.toPandas()
    df_sale_staff_pd.replace({'branch_name':{'_KDPP|_ADM|FSH_|_KDPP|_Dai ly|_TTKDOTT|_TTKDOTT|_KDDA|_TLS|_HO|FTI_|_FPL|_Telesale|_IVoice|_BDA':''
                                            }},regex=True, inplace=True)
    df_sale_staff_pd.replace({'location':{'^Vung Tau$':'Ba Ria Vung Tau',
                                          '^HUE$':'Thua Thien Hue'}},regex=True, inplace=True)
    
    df_sale_staff_filter = df_sale_staff_pd[['location','branch_name'
                                             ,'sale_id','ibb_member_create_date','quit_date']]
    df_sale_staff_filter['ibb_member_create_date'] = pd.to_datetime(df_sale_staff_filter['ibb_member_create_date'])
    df_sale_staff_filter['quit_date'] = pd.to_datetime(df_sale_staff_filter['quit_date'])
    df_sale_staff_filter['nhan_vien_ibb'] = np.where(
        (df_sale_staff_filter['ibb_member_create_date'] <= start_date)
        &(df_sale_staff_filter['quit_date'] > start_date),True,False)
    
    df_sale_staff_monthly = df_sale_staff_filter.groupby(['location','branch_name'],as_index=False)['nhan_vien_ibb'].apply(
        lambda x: (x==True).sum())
    df_sale_staff_monthly.columns = [ 'Tỉnh', 'Chi nhánh', 'nhan_vien_ibb']
    return df_sale_staff_monthly
def process_doithu(month, start_date, end_date, prev_month, config):
    """
        + Load dữ liệu đối thủ từ postgresql 177 - dwh_noc - inf.tbl_isp_ap_info tiai
        + Chuẩn hoá dữ liệu địa chỉ -> summary ap đối thủ ở mức xã/phường 
    """
    
    sql = """select * from inf.%s tiai where isp != 'FTEL';"""%(config['feature_ptht']['table_doithu'])
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                          ,config['dbs']['dwh_177_public']['password']
                                                         ,config['dbs']['dwh_177_public']['host']
                                                        ,config['dbs']['dwh_177_public']['port']
                                                        ,config['dbs']['dwh_177_public']['dbname']))
    df_dthu = pd.read_sql_query(sql, conn)
    df_dthu['month'] = df_dthu['modifieddate'].to_numpy().astype('datetime64[M]')
    df_dthu['ap_doi_thu'] = np.where(
        (df_dthu['month'] < (start_date + relativedelta(days=31))),True,False)
    df_dthu_monthly = df_dthu.groupby(['ward_ten','district_ten','province_ten','month'],as_index=False)['ap_doi_thu'].apply(
        lambda x: (x==True).sum())
    df_dthu_monthly.columns=['Phường', 'Quận', 'Tỉnh','Thang', 'ap_doi_thu']
    df_dthu_monthly_filter = df_dthu_monthly[df_dthu_monthly.Thang==month]
    df_dthu_monthly_filter['Phường']= df_dthu_monthly_filter['Phường'].apply(lambda x: unidecode.unidecode(str(x)))
    df_dthu_monthly_filter['Quận']= df_dthu_monthly_filter['Quận'].apply(lambda x: unidecode.unidecode(str(x)))
    df_dthu_monthly_filter['Tỉnh']= df_dthu_monthly_filter['Tỉnh'].apply(lambda x: unidecode.unidecode(str(x)))

    normalize_address('Không dấu',df_dthu_monthly_filter)
    df_dthu_monthly_filter = df_dthu_monthly_filter.groupby(['Phường không dấu','Quận không dấu',
                             'Tỉnh không dấu','Thang'],as_index=False).agg({'ap_doi_thu':'sum'})
    return df_dthu_monthly_filter
def process_location(config):   
    """
        + Load dữ liệu tỉnh thành từ postgresql 177 - dwh_noc - public.dwh_province 
        + Chuẩn hoá địa chỉ đồng bộ phục vụ mapping tỉnh thành 
        + Lọc để loại bỏ các tỉnh thành nhiễu (không phải tỉnh ở Việt Nam) 
    """
    conn_wr = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    query = """SELECT * FROM public.%s"""%(config['feature_ptht']['tablename_province'])
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
def process_diachidoi(config):
    """
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
def process_vanhanh(month,df_branch_province,df_diachidoi, config):
    """
        + Load dữ liệu về điểm vận hành POP từ postgresql 177 - dwh_noc - public.tbl_quality_pop
        + Mapping địa chỉ của POP: /mnt/projects-data/phat_trien_ha_tang/file_static/address_pop_mapping.csv
        + Chuẩn hoá dữ liệu về địa chỉ và tính trung bình điểm đánh giá POP ở mức xã/phường 
    """
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    sql = """select * from {} where month ='{}'""".format(config['data_import']['tablename_qualitypop'], month)
    # sql = """select * from tbl_quality_pop"""
    df_vh = pd.read_sql_query(sql, conn)
    df_vh.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_vh.columns = ['month', 'POP', 'province', 'avg_operation_pop', 'avg_quality_pop']
    df_address_pop = pd.read_csv(config['feature_ptht']['addresspop_path'])
    df_address_pop.columns = [ 'POP', 'ward', 'district', 'branch','province', 'region']
    df_address_pop.columns=['POP', 'Phường', 'Quận', 'branch', 'province', 'region']
    normalize_address('Không dấu',df_address_pop)
    df_vh=df_vh.merge(df_address_pop, on=['province','POP'], how='left')
    df_vh_grp = df_vh.groupby(['Phường không dấu', 'Quận không dấu','province']
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
                   'Tỉnh không dấu'],as_index=False).agg({
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
     'Tỉnh thay đổi','avg_operation_pop','avg_quality_pop']]
    df_vh_grp_filter_gp.columns= ['Phường không dấu','Quận không dấu',
    'Tỉnh không dấu','avg_operation_pop','avg_quality_pop']
    df_vh_grp_filter_gp = df_vh_grp_filter.groupby(['Phường không dấu','Quận không dấu',
                  'Tỉnh không dấu'],as_index=False).agg({
    'avg_operation_pop':'mean','avg_quality_pop':'mean'})
    return df_vh_grp_filter_gp
def process_khachhang(next_month, config):
    df_infographic = spark.sql("""SELECT ct.contract, d.ward as ward_addr, d.district as district_addr,
            ct.province as province_addr, ct.region
            FROM ftel_dwh_isc.{} d LEFT JOIN ftel_dwh_isc.{} ct 
            ON d.contract = ct.contract""".format(config['feature_ptht']['table_demographic'],config['feature_ptht']['table_contract'])).cache()
    spark.sql('REFRESH TABLE ftel_dm_opt_customer.{}'.format(config['feature_ptht']['table_idatapay']))
    str_slq = """SELECT  contract
            FROM ftel_dm_opt_customer.{}
            WHERE d ='{}'""".format(config['feature_ptht']['table_idatapay'],next_month)
    df_khg = spark.sql(str_slq)
    df_khg = df_khg.join(df_infographic,on='contract', how='left')
    df_khg_gp  = df_khg.groupBy(['ward_addr','district_addr','province_addr']).agg(
            countDistinct('contract').alias('number_khg'))
    return df_khg_gp

def process_nocuoc_roimang(month, date_init, start_date, end_date, prev_month, next_month, config):
    df_infographic = spark.sql("""SELECT ct.contract, d.ward as ward_addr, d.district as district_addr,
        ct.province as province_addr,ct.region
    FROM ftel_dwh_isc.{} d LEFT JOIN ftel_dwh_isc.{} ct 
    ON d.contract = ct.contract""".format(config['feature_ptht']['table_demographic'],config['feature_ptht']['table_contract'])).cache()
    df_contract_gp = process_khachhang(date_init, config)
    df_contract_pd = df_contract_gp.toPandas()
    df_contract_pd.columns = ['Phường', 'Quận', 'Tỉnh','number_khg']
    normalize_address('Không dấu', df_contract_pd)
    df_contract_pd = df_contract_pd.groupby(['Tỉnh không dấu', 'Quận không dấu','Phường không dấu'
                                            ],as_index=False).agg({'number_khg':'max'})
    str_slq = """SELECT  *
            FROM ftel_dm_opt_customer.{}
            WHERE net_status in ('Da cham dut hop dong','Chu thue bao di vang')
            and d  ='{}'""".format(config['feature_ptht']['table_idatapay'], date_init)
    df_roimang = spark.sql(str_slq)
    df_roimang =  df_roimang.drop("region")
    df_roimang = df_roimang.join(df_infographic,on='contract', how='left')
    df_roimang = df_roimang.withColumn("month", f.trunc("d", "month"))
    df_roimang_grp = df_roimang.groupBy(['province_addr','district_addr','ward_addr']).agg(
                countDistinct('contract').alias('KHG_RM')).cache()
    df_roimang_full_pd = df_roimang_grp.toPandas()
    df_roimang_full_pd.columns = ['Tỉnh', 'Quận', 'Phường', 'roi_mang']
    normalize_address('Không dấu', df_roimang_full_pd)
    df_roimang_full_pd = df_roimang_full_pd.groupby(['Tỉnh không dấu', 'Quận không dấu','Phường không dấu'
                                                    ],as_index=False).agg({'roi_mang':'max'})
    
    #  nợ cước 
    spark.sql('REFRESH TABLE ftel_dm_opt_customer.{}'.format(config['feature_ptht']['table_idatapay']))
    str_slq = """SELECT  *
                FROM ftel_dm_opt_customer.{}
                WHERE net_status = 'Ngung vi ly do thanh toan'
                and d  ='{}'""".format(config['feature_ptht']['table_idatapay'], date_init)
    df_nocuoc = spark.sql(str_slq)
    df_nocuoc =  df_nocuoc.drop("region")
    df_nocuoc = df_nocuoc.join(df_infographic,on='contract', how='left')
    df_nocuoc_grp = df_nocuoc.groupBy(['province_addr','district_addr','ward_addr']).agg(
                countDistinct('contract').alias('number_nocuoc')).cache()
    df_nocuoc_full_pd = df_nocuoc_grp.toPandas()
    df_nocuoc_full_pd.columns = ['Tỉnh', 'Quận', 'Phường', 'number_nocuoc']
    normalize_address('Không dấu', df_nocuoc_full_pd)
    df_nocuoc_full_pd = df_nocuoc_full_pd.groupby(['Tỉnh không dấu', 'Quận không dấu','Phường không dấu'
                                                  ],as_index=False).agg({'number_nocuoc':'max'})
    
    df_full = df_contract_pd.merge(df_roimang_full_pd, on=['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu'], 
                               how='outer')
    df_full = df_full.merge(df_nocuoc_full_pd, on=['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu'], 
                            how='outer')
    df_full.columns = [ 'Tỉnh', 'Quận không dấu','Phường không dấu',  'number_khg',
       'khg_rm', 'number_nocuoc']
    df_full.replace({'Tỉnh':{'^Vung Tau$':'Ba Ria Vung Tau'
                    ,'Nha Trang': 'Khanh Hoa'
                    ,'^Hue$':'Thua Thien Hue'}}, regex=True, inplace=True)
    df_full['month']= month
    return df_full
def process_tangtruongport(month, start_date, end_date, prev_month, config):
    """
        + Load dữ liệu port: /data/fpt/ftel/infra/dwh/infor_port_monthly.parquet
        + Tính tuổi thiết bị và tốc độ tăng trưởng portuse 
        + Chuẩn hoá dữ liệu địa chỉ 
    """
    base_path = config['infor_port_monthly']['infor_port_monthly_path_output']
    if (month=='2020-02-01'):
        df_port_prev= spark.read.parquet(base_path+ "d=2019-12-01*").cache()
        df_port= spark.read.parquet(base_path+ "d=2020-01-01*").cache()
    elif ('2020-03-01'):
        df_port_prev= spark.read.parquet(base_path+ "d=2020-01-01*").cache()
        df_port= spark.read.parquet(base_path+ "d={}*".format(month)).cache()
    else:
        df_port_prev= spark.read.parquet(base_path+ "d={}*".format(prev_month)).cache()
        df_port= spark.read.parquet(base_path+ "d={}*".format(month)).cache()
    
    df_port_prev_pd = df_port_prev.select('ward','district','branch','region','popname','name','port','portuse','portfree','portdie',
                       'portmaintain','createdate','date').toPandas()
    df_port_pd = df_port.select('ward','district','branch','region','popname','name','port','portuse','portfree','portdie',
                       'portmaintain','createdate','date').toPandas()
    df_port_full = df_port_pd.merge(df_port_prev_pd, on=['ward','district','branch','region','popname',
                    'name','port','portuse','portfree','portdie',
                    'portmaintain','createdate','date'], how='outer')
    df_port_full['date'] = pd.to_datetime(df_port_full['date'])
    df_port_full['createdate'] = pd.to_datetime(df_port_full['createdate'])
    df_port_full['month'] = df_port_full['date'].dt.to_period('M')
    df_port_full['Tuoi'] = (df_port_full['date'] - df_port_full['createdate']).dt.days
    df_port_full_grp = df_port_full.groupby(['ward','district','branch','region','month'],as_index=False).agg({
    'port':'sum','portuse':'sum','portfree':'sum','portdie':'sum','portmaintain':'sum','name':'nunique','Tuoi':'mean'})
    df_port_full_tt = df_port_full_grp.sort_values(['ward','district','branch','region','month'],ascending=True)
    df_port_full_tt['TT_portuse'] = df_port_full_tt.groupby(['ward','district','branch','region'])['portuse'].diff(1)
    
    df_port_full_tt[['TT_portuse']] = df_port_full_tt[['TT_portuse']].fillna(0)
    df_tangtruong = df_port_full_tt[df_port_full_tt.month==month[:7]]
    df_tangtruong['Thang'] = start_date
    df_tangtruong.drop({'month'},axis=1, inplace=True)
    df_tangtruong.columns = ['Phường', 'Quận', 'Chi nhánh', 'Vùng', 'port', 'portuse',
           'portfree', 'portdie', 'portmaintain', 'name', 'Tuoi', 'TT_portuse', 'Thang']
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
    return df_tangtruong
def add_zero_to_beginning(value):
    if value[0] != '0':
        value = '0' + value
    return value

def process_sale(month, start_date, end_date, prev_month, next_month, df_branch, config):
    """
        + Load dữ liệu về nhân viên và doanh thu đại lý canh tô từ postgresql 177 - dwh_noc - public.tbl_sale_info  và public.tbl_sales_revenue
        + Chuẩn hoá thông tin địa chỉ 
    """
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
    df_dlct_grp = df_dlct.groupby(['Tên nhân viên','province','name','Địa chỉ','Ngày tạo','Tình Trạng NV','Chi nhánh']).agg({'Mã nhân viên':'count'}).reset_index()
    df_ttin= df_dlct_grp[['Tên nhân viên','province','name','Địa chỉ','Ngày tạo','Tình Trạng NV','Chi nhánh']]
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
    
    def try_join(l):
        try:
            return ','.join(map(str, l))
        except TypeError:
            return np.nan
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
    df_ttin_dc = df_ttin.groupby(['Tên nhân viên','Tỉnh','Huyện','Xã','Ngày tạo','Tình Trạng NV','Chi nhánh'],as_index=False).agg({
        'province':'count'})[['Tên nhân viên','Tỉnh','Huyện','Xã','Ngày tạo','Tình Trạng NV','Chi nhánh']]
    df_ttin_dc['Tên nhân viên'] = df_ttin_dc['Tên nhân viên'].str.upper()
    
    #  doanh thu 
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                          ,config['dbs']['dwh_177_public']['password']
                                                         ,config['dbs']['dwh_177_public']['host']
                                                        ,config['dbs']['dwh_177_public']['port']
                                                        ,config['dbs']['dwh_177_public']['dbname']))
    query =  "SELECT * FROM public.{} where month='{}'".format(config['feature_ptht']['table_salerevenue'],month)
    df_doanhthu_full = pd.read_sql(query, conn)
    conn.close()
    df_doanhthu_full.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_doanhthu_full.columns = ['Name', 'month', 'code', 'Doanh số', 'Doanh thu', 'Tên nhân viên']
    df_doanhthu_full['Name'] = np.where(df_doanhthu_full['Name'].isna(), df_doanhthu_full['Tên nhân viên'],df_doanhthu_full['Name'])
    df_doanhthu_grp = df_doanhthu_full.groupby(['Tên nhân viên','month'],as_index=False).agg({
    'Doanh số':'count','Doanh thu':'sum'})
    df_doanhthu_grp.columns = ['Tên nhân viên', 'Thang', 'Số HĐ với KH', 'Doanh thu']
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
    df_mapping_dt_filter = df_mapping_dt_filter[(df_mapping_dt_filter['Tháng tính lương']>=start_date)
    &(df_mapping_dt_filter['Tháng tính lương']<dt.datetime.strptime(next_month, '%Y-%m-%d'))]
    df_feature_doanhthu_grp = df_mapping_dt_filter.groupby(['Tỉnh','Huyện','Xã','Chi nhánh'],as_index=False).agg({
    'Doanh số':'count','Doanh thu':'sum'})
    df_mapping_sale = df_mapping_dt.groupby(['Tên nhân viên','Tỉnh','Huyện','Xã','Chi nhánh','Ngày tạo','Tình Trạng NV',
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
    df_mapping_sale_filter = df_mapping_sale[(df_mapping_sale['Ngày tạo'] < dt.datetime.strptime(month, '%Y-%m-%d'))
        &(df_mapping_sale['Ngày nghỉ'] >= dt.datetime.strptime(month, '%Y-%m-%d'))]
    df_nhanvien_dt_full = df_mapping_sale_filter.groupby(['Tỉnh','Huyện','Xã','Chi nhánh'],as_index=False).agg({'Tên nhân viên':'count'})
    df_nhanvien_dt_full.rename({'Tên nhân viên':'đại lý canh tô'},axis=1,inplace=True)
    df_daily_canhto = df_feature_doanhthu_grp.merge(df_nhanvien_dt_full, 
                                                    on=['Tỉnh','Huyện','Xã','Chi nhánh'], how='outer')
    df_daily_canhto.fillna(0, inplace=True)
    df_daily_canhto_filter = df_daily_canhto.copy()
    df_daily_canhto_filter.rename({'Tỉnh':'Tỉnh không dấu','Huyện':'Quận','Xã':'Phường',
                                   'Doanh số':'Số HĐ với KH'},axis=1,inplace=True)
    
    df_daily_canhto_filter = df_daily_canhto_filter.sort_values(['Tỉnh không dấu','Phường','Quận','Chi nhánh',
                                                                'đại lý canh tô'],ascending=False)
    df_daily_canhto_filter= df_daily_canhto_filter.drop_duplicates(['Tỉnh không dấu','Phường','Quận','Chi nhánh'], keep='first')
    normalize_address('Không dấu',df_daily_canhto_filter)
    df_daily_canhto_filter = df_daily_canhto_filter.sort_values([ 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','Chi nhánh',
          'đại lý canh tô', 'Số HĐ với KH', 'Doanh thu'], ascending=False)
    df_daily_canhto_filter= df_daily_canhto_filter.drop_duplicates(['Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu','Chi nhánh'
           ],keep='first')
    df_daily_canhto_filter.fillna(0, inplace=True)
    return df_daily_canhto_filter

def insert_infrastructure_location_monthly(date_init, config: dict = infra_analytics_config):
    """
    Tổng hợp các hàm lấy chỉ số khách hàng, nhân viên sale, đại lý, tốc độ tăng trưởng, điểm vận hành => chuẩn hoá dữ liệu địa chỉ, xử lý missing => lưu xuống postgresql 177 - dwh_noc - smartops.tbl_infrastructure_location_monthly
    """
    date = (dt.datetime.strptime(date_init, '%Y-%m-%d')- relativedelta(days=1)).date()
    month = (date + relativedelta(months=0)).strftime('%Y-%m-01')
    print(month)
    start_date = dt.datetime.strptime(month, '%Y-%m-%d')
    end_date =start_date + relativedelta(day=31)
    prev_month = (start_date - relativedelta(months=1)).strftime('%Y-%m-%d')
    next_month = (start_date + relativedelta(months=1)).strftime('%Y-%m-%d')
    if (int(month[5:7])>=7)&(int(month[5:7])<=12):
        ky_dau_tu = '2H'+str(int(month[:4]))
    else:
        ky_dau_tu= '1H'+str(int(month[:4]))
    assert config != None, "config must be not None"
    df_branch,df_branch_province, df_branch_region = process_location(config)
    df_diachidoi = process_diachidoi(config)
    #  nhân viên ibb 
    df_sale_staff_monthly= process_ibb(month, start_date, end_date, prev_month, config)
    df_sale_staff_monthly.columns= [ 'Tỉnh không dấu', 'Chi nhánh','IBB']
    df_sale_staff_monthly.replace({'Chi nhánh':{'HNIs|HNI_FTTH':'HNI','HNI_0|HNI_':'HN','HCM_FTTH|FPLSE_HCM|FPLSUB_HCM|FPL_HCM|HCMs':'HCM','HCM_0|HCM_':'HCM',
                        'KHA_01|KHA_02|KHA_03':'KHA','VTU_01|VTU_02|VTU_03|VTU':'BRU',
                            'BGG_01|BGG_02':'BGG',
                            'BNH_01|BNH_02':'BNH',
                            'QNH_01|QNH_02|QNH_03':'QNH',
                            'HDG_01|HDG_02|HDG_03|HDG_04|HDG_05':'HDG',
                            'HPG_01|HPG_02|HPG_03|HPG_04|HPG_05|HPG_06':'HPG',
                            'DNG_01|DNG_02|DNG_03':'DNG','BDG_01|BDG_02|BDG_03':'BDG', 
                            'DNI_01|DNI_02|DNI_03|DNI_04|DNI_05|DNI_06|DNI_07':'DNI'
                            }}, regex=True, inplace=True)
    df_sale_staff_monthly.replace({'Tỉnh không dấu':{'Nha Trang':'Khanh Hoa'}},regex=True,inplace=True)
    df_sale_staff_monthly = df_sale_staff_monthly.groupby(['Tỉnh không dấu','Chi nhánh'],as_index=False).agg({'IBB':'sum'})
    #  đối thủ
    df_dthu_monthly_filter = process_doithu(month, start_date, end_date, prev_month, config)
    df_dt_gp_filter = df_dthu_monthly_filter[(df_dthu_monthly_filter['Quận không dấu']!='')&
                                    (df_dthu_monthly_filter['Phường không dấu']!='')]
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
    df_dt_gp_filter_gp = df_dt_gp_filter_gp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu'],
                                                    as_index=False).agg({'ap_doi_thu':'sum'})
    #  vận hành
    df_vh_grp_full = process_vanhanh(start_date,df_branch_province,df_diachidoi, config)
    #  đại lý canh tô 
    df_daily_canhto = process_sale(month, start_date, end_date, prev_month,next_month,df_branch, config)
    df_daily_canhto.rename({'Tỉnh không dấu':'Tỉnh','Quận không dấu':'Quận','Phường không dấu':'Phường'},axis=1,
                          inplace=True)
    df_daily_canhto_filter = df_daily_canhto.sort_values(['Tỉnh','Phường','Quận',
                    'đại lý canh tô'],ascending=False)
    df_daily_canhto_filter= df_daily_canhto_filter.drop_duplicates(['Tỉnh','Phường','Quận'], keep='first')
    normalize_address('Không dấu',df_daily_canhto_filter)
    df_daily_canhto_filter = df_daily_canhto_filter.sort_values([ 'Tỉnh không dấu', 'Quận không dấu', 'Phường không dấu',
          'đại lý canh tô', 'Số HĐ với KH', 'Doanh thu'], ascending=False)
    df_daily_canhto_filter= df_daily_canhto_filter.drop_duplicates(['Tỉnh không dấu', 'Quận không dấu', 
                                                                    'Phường không dấu'],keep='first')
    df_daily_canhto_filter.replace({'Chi nhánh':{'HCM_KDDA':'HCM','HNI_KDDA':'HNI','HNIs|HNI_FTTH':'HNI','HNI_0|HNI_':'HN','HCM_FTTH|FPLSE_HCM|FPLSUB_HCM|FPL_HCM|HCMs':'HCM','HCM_0|HCM_':'HCM',
                        'KHA_01|KHA_02|KHA_03':'KHA','VTU_01|VTU_02|VTU_03|VTU':'BRU',
                            'BGG_01|BGG_02':'BGG',
                            'BNH_01|BNH_02':'BNH',
                            'QNH_01|QNH_02|QNH_03':'QNH',
                            'HDG_01|HDG_02|HDG_03|HDG_04|HDG_05':'HDG',
                            'HPG_01|HPG_02|HPG_03|HPG_04|HPG_05|HPG_06':'HPG',
                            'DNG_01|DNG_02|DNG_03':'DNG','BDG_01|BDG_02|BDG_03':'BDG', 
                            'DNI_01|DNI_02|DNI_03|DNI_04|DNI_05|DNI_06|DNI_07':'DNI',
                             'DNG_Dai ly':'DNG','HDG_Dai ly':'HDG','BTE_Dai ly':'BTE'
                            }}, regex=True, inplace=True)
    df_sale_staff_monthly_t = df_sale_staff_monthly.sort_values(['Tỉnh không dấu','Chi nhánh','IBB'],ascending=False)
    df_sale_staff_monthly_t.drop_duplicates(['Tỉnh không dấu'], keep='first',inplace=True)
    df_sale_staff_monthly_t.columns = ['Tỉnh không dấu', 'Chi nhánh', 'IBB_t']
    df_kt_sale = df_sale_staff_monthly.merge(df_daily_canhto_filter,
            on=['Chi nhánh','Tỉnh không dấu'], how='outer')
    df_kt_sale = df_kt_sale.merge(df_sale_staff_monthly_t[['Tỉnh không dấu','IBB_t']],
            on=['Tỉnh không dấu'], how='outer')
    df_kt_sale['IBB'] = np.where(df_kt_sale['IBB'].isna(),df_kt_sale['IBB_t'],df_kt_sale['IBB'])
    df_kt_sale.drop('IBB_t', axis=1, inplace= True)
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
    df_kt_sale_filter.drop_duplicates(keep='first',inplace=True)
    
    df_kt_sale_filter['Quận không dấu'] = df_kt_sale_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_kt_sale_filter['Phường không dấu'] = df_kt_sale_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
    
    df_kt_sale_filter['Quận không dấu'] = np.where((df_kt_sale_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                        (df_kt_sale_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                'Thu Duc' ,df_kt_sale_filter['Quận không dấu'])
    df_kt_sale_filter_mapping = df_kt_sale_filter.groupby(['Phường không dấu','Quận không dấu',
          'Tỉnh không dấu','Chi nhánh'],as_index=False).agg({
        'IBB':'max','đại lý canh tô':'max','Số HĐ với KH':'max','Doanh thu':'max'})
    df_kt_sale_filter_mapping.columns= ['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'Chi nhánh',
            'IBB update','đại lý canh tô update', 'Số HĐ với KH update', 'Doanh thu update']
    df_kt_sale_filter = df_kt_sale_filter.merge(df_kt_sale_filter_mapping,
       on=['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'Chi nhánh'],how='left')
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
    df_kt_sale_filter.drop({ 'IBB update','đại lý canh tô update', 'Số HĐ với KH update', 
                            'Doanh thu update'},axis=1,inplace=True)
    df_kt_sale_filter = df_kt_sale_filter.sort_values(['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'Chi nhánh',
                                   'IBB','Số HĐ với KH','Doanh thu','đại lý canh tô'], ascending=False)
    df_kt_sale_filter.drop_duplicates(subset = ['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu', 'Chi nhánh'], 
                                      keep ='first', inplace=True)
    df_kt_sale_filter_grp = df_kt_sale_filter.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu','Chi nhánh'
                                                      ],as_index=False).agg({'IBB':'mean','đại lý canh tô':'mean','Số HĐ với KH':'mean','Doanh thu':'mean'})
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
    'IBB', 'đại lý canh tô', 'Số HĐ với KH','Doanh thu']]
    df_kt_sale_filter_grp.columns= ['Phường không dấu','Quận không dấu','Tỉnh không dấu','Chi nhánh',
     'IBB', 'đại lý canh tô', 'Số HĐ với KH','Doanh thu']
    df_kt_sale_filter_grp = df_kt_sale_filter_grp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu','Chi nhánh',
    ],as_index=False).agg({'IBB':'mean','đại lý canh tô':'mean','Số HĐ với KH':'mean','Doanh thu':'mean'})
    #  port tăng trưởng 
    df_tangtruong = process_tangtruongport(month, start_date, end_date, prev_month, config)
    df_tt_port_map_ = df_tangtruong.copy()
    df_tt_port_map_['province'] = df_tt_port_map_['Chi nhánh'].str[:3]
    df_tt_port_map_['province']= np.where(df_tt_port_map_['province'].str.contains('HN')
                                          ,'HNI',df_tt_port_map_['province'])
    df_tt_port_map_['province']= np.where(df_tt_port_map_['province'].str.contains('SG')
                                          ,'HCM',df_tt_port_map_['province'])
    df_branch_province_ = df_branch_province.copy()
    df_branch_province_.columns = ['Tỉnh', 'province']
    df_tt_port_map_= df_tt_port_map_.merge(df_branch_province_,on='province', how='left')
    normalize_address('Không dấu',df_tt_port_map_)
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
    
    df_tt_port_map_= df_tt_port_map_[['Phường thay đổi','Quận thay đổi','Tỉnh thay đổi',
     'port','portuse', 'portfree', 'portdie', 'portmaintain', 'name', 'Tuoi','TT_portuse']]
    df_tt_port_map_.columns= ['Phường không dấu','Quận không dấu','Tỉnh không dấu',
     'port','portuse', 'portfree', 'portdie', 'portmaintain', 'num_device', 'Tuoi','TT_portuse']
    
    df_tt_port_map_ = df_tt_port_map_.groupby(['Phường không dấu','Quận không dấu',
    'Tỉnh không dấu'],as_index=False).agg({'Tuoi':'mean','port':'mean',
    'portuse':'mean','portfree':'mean','portdie':'mean','portmaintain':'mean',
    'num_device':'mean','TT_portuse':'mean'})
    #  địa chỉ 
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                  ,config['dbs']['dwh_177_report']['password']
                                                 ,config['dbs']['dwh_177_report']['host']
                                                ,config['dbs']['dwh_177_report']['port']
                                                ,config['dbs']['dwh_177_report']['dbname']))
    df_danso_new_filter_ = pd.read_sql("""select tinh_co_dau,quan_co_dau,phuong_co_dau, tinh_khong_dau,quan_khong_dau,phuong_khong_dau
                from  report.%s 
                group by tinh_co_dau,quan_co_dau,phuong_co_dau, tinh_khong_dau,quan_khong_dau,phuong_khong_dau"""%(config['insert_dashboard']['table_ptht']), conn)
    df_danso_new_filter_.columns = ['Tỉnh có dấu','Quận có dấu','Phường có dấu',
                                                'Tỉnh không dấu','Quận không dấu','Phường không dấu']
    df_branch_region_ds = df_branch_region[df_branch_region['province']!='NTG']
    df_cn_rm_grp = process_nocuoc_roimang(month, date_init, start_date, end_date, prev_month,next_month, config)
    #  rời mạng nợ cước 
    df_cn_rm_grp.rename({'Tỉnh':'Tỉnh không dấu'},axis=1, inplace=True)
    df_cn_rm_grp_filter = df_cn_rm_grp[(~df_cn_rm_grp['Quận không dấu'].isna())&
                                (~df_cn_rm_grp['Phường không dấu'].isna())&
                                (~df_cn_rm_grp['Tỉnh không dấu'].isna())]
    df_cn_rm_grp_filter.replace({'Phường không dấu':{'Phuong  ':'Phuong '}},regex=True,inplace=True)
    df_cn_rm_grp_filter.replace({'Phường không dấu':{'Phuong Co Nhue 2':'Co Nhue 2',
    'Phuong My Dinh 2':'My Dinh 2',
    'Thi  Trang Bang':'Trang Bang',
    'Phuong Gia Tan 2':'Gia Tan 2',
    'Phuong Sai':'Sai'}},regex=True,inplace=True)
    df_cn_rm_grp_filter.replace({'Quận không dấu':{'Ba Don,  Quang Trach':'Quang Trach',
    'Quan  ':'Quan ','Lagi':'La Gi',
    'Phan Rang - Thap Cham':'Phan Rang-Thap Cham',
    'Phan Rang - Tc':'Phan Rang - Thap Cham'}},regex=True,inplace=True)
    df_cn_rm_grp_filter['Quận không dấu'] = df_cn_rm_grp_filter['Quận không dấu'].str.strip('-|,|[ ]|.')
    df_cn_rm_grp_filter['Phường không dấu'] = df_cn_rm_grp_filter['Phường không dấu'].str.strip('-|,|[ ]|.')
    df_cn_rm_grp_filter['Quận không dấu'] = np.where((df_cn_rm_grp_filter['Quận không dấu'].isin(['Quan 2','Quan 9']))&
                                        (df_cn_rm_grp_filter['Tỉnh không dấu']=='Ho Chi Minh'),
                                                'Thu Duc' ,df_cn_rm_grp_filter['Quận không dấu'])
    
    df_cn_rm_grp_filter_gp = df_cn_rm_grp_filter.groupby(['Phường không dấu','Quận không dấu',
                   'Tỉnh không dấu'],as_index=False).agg({
                    'khg_rm':'sum','number_nocuoc':'sum','number_khg':'sum'})
    df_cn_rm_grp_filter_gp= df_cn_rm_grp_filter_gp.merge(df_diachidoi,on=['Phường không dấu','Quận không dấu',
                        'Tỉnh không dấu'],how='left')
    df_cn_rm_grp_filter_gp['Phường thay đổi']= np.where(df_cn_rm_grp_filter_gp['Phường thay đổi'].isna(),
                                                      df_cn_rm_grp_filter_gp['Phường không dấu'],
                                                      df_cn_rm_grp_filter_gp['Phường thay đổi'])
    df_cn_rm_grp_filter_gp['Quận thay đổi']= np.where(df_cn_rm_grp_filter_gp['Quận thay đổi'].isna(),
                                                      df_cn_rm_grp_filter_gp['Quận không dấu'],
                                                      df_cn_rm_grp_filter_gp['Quận thay đổi'])
    df_cn_rm_grp_filter_gp['Tỉnh thay đổi']= np.where(df_cn_rm_grp_filter_gp['Tỉnh thay đổi'].isna(),
                                                      df_cn_rm_grp_filter_gp['Tỉnh không dấu'],
                                                      df_cn_rm_grp_filter_gp['Tỉnh thay đổi'])
    df_cn_rm_grp_filter_gp= df_cn_rm_grp_filter_gp[['Phường thay đổi','Quận thay đổi',
     'Tỉnh thay đổi','khg_rm','number_nocuoc','number_khg']]
    df_cn_rm_grp_filter_gp.columns= ['Phường không dấu','Quận không dấu',
    'Tỉnh không dấu','khg_rm','number_nocuoc','number_khg']
    df_cn_rm_grp_filter_gp = df_cn_rm_grp_filter_gp.groupby(['Phường không dấu','Quận không dấu',
                   'Tỉnh không dấu'],as_index=False).agg({
                    'khg_rm':'sum','number_nocuoc':'sum','number_khg':'sum'})
    df_cn_rm_grp_filter_gp_ = df_cn_rm_grp_filter_gp[(df_cn_rm_grp_filter_gp['Phường không dấu']!='')&
    (df_cn_rm_grp_filter_gp['Phường không dấu']!="' '")]
    df_kt_sale_filter_grp_ = df_kt_sale_filter_grp.groupby(['Phường không dấu','Quận không dấu','Tỉnh không dấu']
                              ,as_index=False).agg({'IBB':'mean','đại lý canh tô':'sum','Số HĐ với KH':'sum','Doanh thu':'sum'})
    df_feature = df_danso_new_filter_.merge(df_dt_gp_filter_gp,on=['Phường không dấu',
          'Quận không dấu', 'Tỉnh không dấu'], how='left')
    df_feature = df_feature.merge(df_cn_rm_grp_filter_gp_,on=['Phường không dấu',
          'Quận không dấu', 'Tỉnh không dấu'], how='outer')
    df_feature = df_feature.merge(df_vh_grp_full,on=['Phường không dấu',
          'Quận không dấu', 'Tỉnh không dấu'], how='left')
    df_feature = df_feature.merge(df_kt_sale_filter_grp_,on=['Phường không dấu','Quận không dấu',
                                                      'Tỉnh không dấu'], how='left')
    df_feature  = df_feature.merge(df_tt_port_map_
    ,on=['Phường không dấu', 'Quận không dấu', 'Tỉnh không dấu'], how='left')
    df_feature['Thang'] = start_date
    df_feature['Kỳ đầu tư'] = ky_dau_tu
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    query = """SELECT phuong_co_dau,quan_co_dau,tinh_co_dau,chi_nhanh 
                FROM report.{}
                WHERE ky_dau_tu='{}'
                GROUP BY phuong_co_dau,quan_co_dau,tinh_co_dau,chi_nhanh """.format(config['insert_dashboard']['table_ptht'], df_feature['Kỳ đầu tư'].unique()[0])
    df_chinhanh = pd.read_sql(query, conn)
    df_chinhanh = df_chinhanh.sort_values(['phuong_co_dau','quan_co_dau','tinh_co_dau','chi_nhanh'])
    df_chinhanh.drop_duplicates(subset=['phuong_co_dau','quan_co_dau','tinh_co_dau'], keep='first', inplace=True)
    df_chinhanh.columns = ['Phường có dấu','Quận có dấu','Tỉnh có dấu', 'Chi nhánh']
    df_feature = df_feature.merge(df_chinhanh, on=['Phường có dấu','Quận có dấu','Tỉnh có dấu'], how='left')
    
    df_feature.replace({'Chi nhánh' : {r'SGN': 'HCM','SG':'HCM', r'NTG':'KHA', r'HNI-0': 'HN',  
     'HNI-':'HN','HCM-0':'HCM','HCM-':'HCM', r'HN0': 'HN',r'HCM0': 'HCM'}}, regex=True,inplace=True)
    
    df_feature['Tỉnh có dấu'] = np.where(df_feature['Tỉnh có dấu'].isna(),df_feature['Tỉnh không dấu'],
                                        df_feature['Tỉnh có dấu'])
    df_feature['Quận có dấu'] = np.where(df_feature['Quận có dấu'].isna(),df_feature['Quận không dấu'],
                                        df_feature['Quận có dấu'])
    df_feature['Phường có dấu'] = np.where(df_feature['Phường có dấu'].isna(),df_feature['Phường không dấu'],
                                        df_feature['Phường có dấu'])
    df_feature.replace({'Tỉnh có dấu':{' Kien Giang':'Kiên Giang',' Tien Giang':'Tiền Giang'}}
                       ,regex=True,inplace=True)
    df_feature.replace({'Tỉnh không dấu':{' Kien Giang':'Kien Giang',' Tien Giang':'Tien Giang'}}
                       ,regex=True,inplace=True)
    df_branch_region_ = df_branch_region[['name','region']]
    df_branch_region_.columns =['Tỉnh không dấu','Vùng']
    df_branch_region_.drop_duplicates(subset=['Tỉnh không dấu'], keep='first', inplace=True)
    df_feature  = df_feature.merge(df_branch_region_,on=['Tỉnh không dấu'], how='left')
    df_feature.replace({'Vùng':{'Vung':'Vùng'}},regex=True, inplace=True)
    
    df_feature[['Phường có dấu', 'Quận có dấu','Tỉnh có dấu', 'Chi nhánh','Vùng']] = df_feature[['Phường có dấu', 'Quận có dấu',
                                                           'Tỉnh có dấu', 'Chi nhánh','Vùng']].fillna('')
    df_feature_full = df_feature[['Phường có dấu', 'Quận có dấu','Tỉnh có dấu', 'Chi nhánh','Vùng', 'Thang', 'Kỳ đầu tư', 'ap_doi_thu',
    'avg_operation_pop','avg_quality_pop', 'khg_rm', 'number_nocuoc', 'number_khg',
    'IBB', 'đại lý canh tô', 'Số HĐ với KH', 'Doanh thu', 'Tuoi', 'port',
    'portuse', 'portfree', 'portdie', 'portmaintain', 'num_device','TT_portuse']]
    df_feature_full.columns = ['phuong', 'quan', 'tinh', 'chi_nhanh', 'vung',
           'thang', 'ky_dau_tu', 'ap_doi_thu', 'avg_operation_pop',
           'avg_quality_pop', 'khg_roi_mang', 'khg_nocuoc', 'khach_hang', 'ibb',
           'dai_ly_canh_to', 'so_hd_voi_kh', 'doanh_thu', 'tuoi', 'port',
           'portuse', 'portfree', 'portdie', 'portmaintain', 'num_device',
           'tt_portuse']
    df_feature_full = df_feature_full[df_feature_full.phuong!='']
    df_feature_full= df_feature_full.drop_duplicates(keep='first')
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur = conn.cursor()
    table_infrastructure_location = config['insert_dashboard']['table_infrastructure_location']
    sql = """DELETE FROM smartops."""+table_infrastructure_location+ """ WHERE thang = '""" + month + """';"""
    cur.execute(sql)
    conn.commit()
    engine = create_engine("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                          ,config['dbs']['dwh_177_public']['password']
                                                         ,config['dbs']['dwh_177_public']['host']
                                                        ,config['dbs']['dwh_177_public']['port']
                                                        ,config['dbs']['dwh_177_public']['dbname']))
    df_feature_full.to_sql(table_infrastructure_location, engine, if_exists='append', index=False, schema='smartops')

def get_address(config):
    """
        + Load dữ liệu tỉnh thành từ postgresql 177 - dwh_noc - public.dwh_province 
        + Chuẩn hoá địa chỉ đồng bộ phục vụ mapping tỉnh thành 
        + Lọc để loại bỏ các tỉnh thành nhiễu (không phải tỉnh ở Việt Nam) 
    """
    #  get địa chỉ
    conn_wr = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                          ,config['dbs']['dwh_177_public']['password']
                                                         ,config['dbs']['dwh_177_public']['host']
                                                        ,config['dbs']['dwh_177_public']['port']
                                                        ,config['dbs']['dwh_177_public']['dbname']))
    query = """SELECT * FROM public.%s"""% (config['feature_ptht']['tablename_province'])
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
    df_province_ = df_branch_province.rename({'name':'Tỉnh'},axis=1)
    return df_province_
def update_port_next(kydautu, config):
    """
    Cập nhật thông tin port nếu missing data bằng cách lấy thông tin kỳ trước: 
        + Check nếu port 6 tháng kỳ hiện tại bằng 0 thì fill bằng kỳ trước đó và update vào report.dmt_dashboard_ptht
    """
    if (int(kydautu[:1])==2):
        kydautu_next = '1H'+str(int(kydautu[2:])+1)
    else:
        kydautu_next = '2H'+kydautu[2:]
        
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    str_sql = "select * from  report.{} where ky_dau_tu in ('{}','{}')".format(config['insert_dashboard']['table_ptht'], kydautu,kydautu_next)
    df_ds_full = pd.read_sql(str_sql, conn)
    conn.close()
    df_ds_full.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_ds_ht = df_ds_full[df_ds_full.ky_dau_tu==kydautu]
    df_ds_next = df_ds_full[df_ds_full.ky_dau_tu==kydautu_next]
    df_ds_ht_grp = df_ds_ht.groupby(['quan_co_dau', 'phuong_co_dau', 'tinh_co_dau',  'chi_nhanh'],dropna=False,as_index=False).agg(
         {'port_6t_hien_tai':'max','port_dung_6t_hien_tai':'max'})
    df_ds_ht_grp.columns= ['quan_co_dau', 'phuong_co_dau', 'tinh_co_dau', 'chi_nhanh',
           'port_6t_kytruoc', 'port_dung_6t_kytruoc']
    df_ds_next = df_ds_next.merge(df_ds_ht_grp,on=['quan_co_dau', 'phuong_co_dau', 'tinh_co_dau', 'chi_nhanh'],how='left')
    df_ds_next['port'] = np.where((df_ds_next.port==0)&(df_ds_next.port_6t_kytruoc>0),
                                    df_ds_next.port_6t_kytruoc,
                                    df_ds_next.port)
    df_ds_next['portuse'] = np.where((df_ds_next.portuse==0)&(df_ds_next.port_dung_6t_kytruoc>0),
                                    df_ds_next.port_dung_6t_kytruoc,
                                    df_ds_next.portuse)
    df_ds_next.drop(['port_6t_kytruoc', 'port_dung_6t_kytruoc'],axis=1,inplace=True)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    cur = conn.cursor()
    tablename =config['insert_dashboard']['table_ptht']
    sql = """DELETE FROM report.""" + tablename + """ WHERE ky_dau_tu in ('""" + kydautu_next + """');"""
    cur.execute(sql)
    conn.commit()
    engine = create_engine("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    df_ds_next.to_sql(tablename, engine,schema='report', if_exists='append', index=False)
def update_label_phattrienhatang(kydautu, config):
    """
        + Load dữ liệu kết quả dự án trên dashboard từ postgresql 177 - dwh_noc - report.dmt_dashboard_ptht
        + Update port, portuse 6 tháng nếu có đổi và lưu xuống ftel_dwh_infra.ds_label_phattrienhatang
    """
    try:
        if (int(kydautu[0])==1):
            date = str(int(kydautu[2:])-1) + '-09-01'
        else:
            date = str(kydautu[2:]) + '-03-01'
        #  feature đang ghi nhận theo mã kế hoạch => label lấy sum port và portuse  
        conn =pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                  ,config['dbs']['dwh_177_report']['password']
                                                 ,config['dbs']['dwh_177_report']['host']
                                                ,config['dbs']['dwh_177_report']['port']
                                                ,config['dbs']['dwh_177_report']['dbname']))
        str_sql = "select * from  report.%s"%(config['insert_dashboard']['table_ptht'])
        df_ds = pd.read_sql(str_sql, conn)
        conn.close()
        df_ds.drop(['created_at','updated_at'],axis=1,inplace=True)
        df_db_grp = df_ds[df_ds.ky_dau_tu==kydautu].groupby(['quan_co_dau','phuong_co_dau','tinh_co_dau','vung','ky_dau_tu','chi_nhanh'],as_index=False).agg(
        {'port_6t_hien_tai':'sum','port_dung_6t_hien_tai':'sum'})
        df_db_grp.columns=['quan','phuong','tinh','vung','ky_dau_tu','chi_nhanh','tong_port_sau_6t_hien_tai','port_dung_sau_6t_hien_tai']
        df_db_grp['create_date'] = date
        df_db_grp_filter = df_db_grp[df_db_grp.tong_port_sau_6t_hien_tai>0]
        df_db_spark = spark.createDataFrame(df_db_grp_filter[['quan', 'phuong', 'tinh', 'vung', 'ky_dau_tu', 'chi_nhanh',
               'create_date', 'tong_port_sau_6t_hien_tai',
               'port_dung_sau_6t_hien_tai']])
        df_db_spark.coalesce(1).write.mode("overwrite").partitionBy('create_date').option("path", config['training_model']['label_phattrienhatang_path'])\
        .saveAsTable("ftel_dwh_infra.%s"%(config['training_model']['table_labelgoiy']))
    except:
        print('Không có dữ liệu')
def update_performance_dashboard_report(date, config: dict = infra_analytics_config):
    """
        + Load dữ liệu port: /data/fpt/ftel/infra/dwh/infor_port_monthly.parquet
        + Tính tuổi thiết bị và tốc độ tăng trưởng portuse theo các mốc 3t,6t,9t,12t
        + Load thông tin chi phí đầu tư: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/chi_phi_dau_tu.parquet
        + Chuẩn hoá dữ liệu địa chỉ  và mapping cả 2 thông tin trên =>Xử lý lại dữ liệu missing sau khi mapping=>  lấy hiệu quả khai thác 6t gần nhất và upsert vào bảng report.dmt_dashboard_ptht (cập nhật hiệu quả khai thác mới nhất ở kỳ đầu tư)
    """
    if (int(date[5:7])>=1)&(int(date[5:7])<7):
        kydautu='1H'+str(date[:4])
        kydautu_prev= '2H'+str(int(date[:4])-1)
    else:
        kydautu='2H'+str(date[:4])
        kydautu_prev= '1H'+str(date[:4])
    assert config != None, "config must be not None"
    
    base_path = config['infor_port_monthly']['infor_port_monthly_path_output']
    df= spark.read.parquet(base_path).cache()
    df = df.withColumn('str_ngay_thi_cong', split(df['Plans'], '[.]').getItem(4))
    df = df.withColumn('str_ngay_thi_cong', when(col('str_ngay_thi_cong').contains('PP'), col('str_ngay_thi_cong').substr(-6, 6))\
         .otherwise(col('str_ngay_thi_cong')))
    df = df.withColumn('ngay_thi_cong', to_date(df["str_ngay_thi_cong"], "ddMMyy"))
    df = df.withColumn('createdate', when(df.createdate.isNull(),df.ngay_thi_cong).otherwise(df.createdate))
    df_drp = df.groupBy(['Plans','region','branch','district','ward','popname','name','port','portuse','portfree',
                'createdate', 'date']).agg(count(col('d')).alias('num_row')).cache()
    
    df_old =df.groupBy(['Plans','region','branch','district','ward','popname','name']).agg(sparkMin(col('createdate')).alias('used_date')).cache()
    df_full = df_drp.join(df_old, on=['Plans','region','branch','district','ward','popname','name'], how='left').cache()
    
    df_full= df_full.withColumn("month_old_device", round(months_between(col("date"),col("used_date")),0)).cache()
    df_full= df_full.withColumn("delta_month",when(df_full.month_old_device <=3, '3T')\
            .when((df_full.month_old_device > 3)&(df_full.month_old_device <=6), '6T')\
            .when((df_full.month_old_device > 6)&(df_full.month_old_device <=9), '9T')\
            .when((df_full.month_old_device > 9)&(df_full.month_old_device <=12), '12T').otherwise('>1 năm')).cache()
    df_full_prp = df_full.sort(col("Plans").desc(),col("region").desc(),col("branch").desc(),col("district").desc(),col("ward").desc()
        ,col("popname").desc(),col("name").desc(),col("delta_month").desc(),col("date").desc())
    df_full_prp = df_full_prp.dropDuplicates(['Plans','region', 'branch','district','ward', 'popname', 'name', 
                                              'delta_month']).cache()
    df_full_prp = df_full_prp.filter(df_full_prp.delta_month!='>1 năm')
    df_full_prp = df_full_prp.withColumn('ky_dau_tu',when((month(df_full_prp.createdate)>=1)&\
                            (month(df_full_prp.createdate)<7),concat(lit('1H'),lit(year(df_full_prp.createdate))))\
                            .otherwise(concat(lit('2H'),lit(year(df_full_prp.createdate)))))
    df_full_plans = df_full_prp.groupBy(['Plans','ky_dau_tu', 'popname','region', 'branch','district','ward',
                           'delta_month']).agg(sum('port').alias('port'),sum('portuse').alias('portuse'))
    df_port_pd = df_full_plans.toPandas()
    df_port_pd= df_port_pd.sort_values(['Plans','ky_dau_tu', 'popname','region', 'branch','district','ward',
                           'delta_month'],ascending=True)
    # df_port_pd_filter = df_port_pd[df_port_pd.Plans!='']
    df_port_pd_filter = df_port_pd.copy()
    df_port_pd_filter.rename({'Plans':'ma_ke_hoach'},axis=1,inplace=True)
    df_port_pivot = pd.pivot_table(df_port_pd_filter, values=['port','portuse'], index=['ma_ke_hoach',
                'ky_dau_tu', 'popname', 'region', 'branch', 'district', 'ward'],
                         columns=['delta_month'],  aggfunc={"mean"}, fill_value=None).reset_index()
    df_port_pivot.columns=['ma_ke_hoach','ky_dau_tu', 'pop', 'vung', 'chi_nhanh'
    , 'quan', 'phuong','tong_port_sau_12t','tong_port_sau_3t',
    'tong_port_sau_6t','tong_port_sau_9t','port_dung_sau_12t','port_dung_sau_3t','port_dung_sau_6t'
    ,'port_dung_sau_9t']
    df_port_pivot['dung_luong_trien_khai'] = df_port_pivot['tong_port_sau_3t']
    df_port_pivot['ti_le_khai_thac_3t'] = np.where(df_port_pivot['tong_port_sau_12t']<=0,0,
                      df_port_pivot['port_dung_sau_3t']/df_port_pivot['tong_port_sau_12t'])
    df_port_pivot['ti_le_khai_thac_6t'] = np.where(df_port_pivot['tong_port_sau_6t']<=0,0,
                      df_port_pivot['port_dung_sau_6t']/df_port_pivot['tong_port_sau_6t'])
    df_port_pivot['ti_le_khai_thac_9t'] = np.where(df_port_pivot['tong_port_sau_9t']<=0,0,
                      df_port_pivot['port_dung_sau_9t']/df_port_pivot['tong_port_sau_9t'])
    df_port_pivot['ti_le_khai_thac_12t'] = np.where(df_port_pivot['tong_port_sau_12t']<=0,0,
                      df_port_pivot['port_dung_sau_12t']/df_port_pivot['tong_port_sau_12t'])
    df_port_pivot = df_port_pivot[['ma_ke_hoach', 'ky_dau_tu', 'pop', 'phuong', 'quan', 'chi_nhanh',
           'vung', 'dung_luong_trien_khai', 'tong_port_sau_3t',
           'port_dung_sau_3t', 'ti_le_khai_thac_3t', 'tong_port_sau_6t',
           'port_dung_sau_6t', 'ti_le_khai_thac_6t', 'tong_port_sau_9t',
           'port_dung_sau_9t', 'ti_le_khai_thac_9t', 'tong_port_sau_12t',
           'port_dung_sau_12t', 'ti_le_khai_thac_12t']]
    df_port_pivot_filter = df_port_pivot.copy()
    df_port_pivot_filter.rename({'chi_nhanh':'province','phuong':'Phường',
                                 'quan':'Quận','vung':'Vùng'},axis=1,inplace=True)
    df_province_=get_address(config)
    df_port_pivot_filter = df_port_pivot_filter.merge(df_province_, on='province',how='left')
    normalize_address('Không dấu', df_port_pivot_filter)
    df_port_pivot_grp = df_port_pivot_filter[(df_port_pivot_filter.tong_port_sau_3t>0)].groupby(['ky_dau_tu','ma_ke_hoach',
          'Phường không dấu','Quận không dấu','Tỉnh không dấu','Vùng'],as_index=False).agg({'tong_port_sau_3t':'sum',
                 'port_dung_sau_3t':'sum','tong_port_sau_6t':'sum','port_dung_sau_6t':'sum'})
    df_port_pivot_grp['port_dung_sau_6t'] = np.where((df_port_pivot_grp['tong_port_sau_6t']==0)|
                                                     (df_port_pivot_grp['tong_port_sau_6t'].isna())|
                                                     (df_port_pivot_grp['port_dung_sau_6t']<df_port_pivot_grp['port_dung_sau_3t']),
                                                    df_port_pivot_grp['port_dung_sau_3t'],
                                                     df_port_pivot_grp['port_dung_sau_6t'])
    df_port_pivot_grp['tong_port_sau_6t'] = np.where((df_port_pivot_grp['tong_port_sau_6t']==0)|
                                                     (df_port_pivot_grp['tong_port_sau_6t']<df_port_pivot_grp['tong_port_sau_3t']),
                                                    df_port_pivot_grp['tong_port_sau_3t'],
                                                     df_port_pivot_grp['tong_port_sau_6t'])
    df_port_pivot_grp['ti_le_khai_thac_3t'] = np.where(df_port_pivot_grp['tong_port_sau_3t']>0,
           df_port_pivot_grp['port_dung_sau_3t']/df_port_pivot_grp['tong_port_sau_3t'],0)
    df_port_pivot_grp['ti_le_khai_thac_6t'] = np.where(df_port_pivot_grp['tong_port_sau_6t']>0,
           df_port_pivot_grp['port_dung_sau_6t']/df_port_pivot_grp['tong_port_sau_6t'],0)
    df_port_pivot_grp.replace({'Vùng':{'Vung':'Vùng'}},regex=True, inplace=True)
    #  check danh sách và filter read file danh sách đầu tư để filter 

    df_dsdt = pd.DataFrame()
    for i in (kydautu,kydautu_prev):
        file_name_r = config['data_import']['chiphidautu_path_output']+'kydautu={}'.format(i)
        print(file_name_r)
        if hdfs_file_exists(file_name_r):
            df_dt_r = spark.read.parquet(file_name_r).toPandas()
            df_dsdt = df_dsdt.append(df_dt_r)
    
    df_dsdt.columns = ['ky_dau_tu', 'Vùng', 'Chi nhánh', 'Loại KH', 'POP',
           'Dung lượng triển khai', 'Phường', 'Quận', 'ma_ke_hoach',
           'Tổng chi phí', 'perport', 'Ngày hoàn tất thi công']
    df_dsdt['province'] = df_dsdt['POP'].str[:3]
    df_dsdt_ = df_dsdt.merge(df_province_,on='province',how='left')
    normalize_address('Không dấu', df_dsdt_)
    df_dsdt_filter= df_dsdt_.groupby(['ky_dau_tu',  'Phường không dấu', 'Quận không dấu',
           'ma_ke_hoach', 'Tỉnh không dấu'],as_index=False).agg({'Dung lượng triển khai':'max'})
    df_dsdt_filter.drop_duplicates(inplace=True)
    df_dsdt_filter['check_dtdk']=1
    
    df_port_filter_kdt = df_port_pivot_grp[df_port_pivot_grp.ky_dau_tu.isin([kydautu,kydautu_prev])]
    df_port_dt= df_port_filter_kdt.groupby([
        'ky_dau_tu','ma_ke_hoach','Phường không dấu','Quận không dấu','Tỉnh không dấu'
    ],as_index=False).agg({'tong_port_sau_6t':'sum','port_dung_sau_6t':'sum'})
    df_dsdt_full = df_port_dt.merge(df_dsdt_filter,on=['ky_dau_tu','ma_ke_hoach',
                         'Phường không dấu','Quận không dấu','Tỉnh không dấu'],how='outer')
    df_dsdt_full['tong_port_sau_6t'] = np.where(df_dsdt_full['tong_port_sau_6t'].isna(),
                                      df_dsdt_full['Dung lượng triển khai'],df_dsdt_full['tong_port_sau_6t'])
    df_dsdt_full_ = df_dsdt_full[(df_dsdt_full.check_dtdk==1)|(~df_dsdt_full.ky_dau_tu.isin(df_dsdt_filter.ky_dau_tu.unique()))]
    df_dsdt_full_grp =  df_dsdt_full_.groupby(['ky_dau_tu',
                         'Phường không dấu','Quận không dấu','Tỉnh không dấu'],as_index=False).agg({
                        'tong_port_sau_6t':'sum','port_dung_sau_6t':'sum'})
    df_dsdt_full_grp.columns= ['ky_dau_tu', 'phuong_khong_dau', 'quan_khong_dau', 'tinh_khong_dau',
           'tong_port_sau_6t_new', 'port_dung_sau_6t_new']
    #  load danh sách 
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    str_sql = "select * from  report.{} where ky_dau_tu in ('{}','{}')".format(config['insert_dashboard']['table_ptht'], kydautu, kydautu_prev)
    df_ds = pd.read_sql(str_sql, conn)
    conn.close()
    df_ds.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_ds['port_6t_hien_tai'] = np.NaN
    df_ds['port_dung_6t_hien_tai'] = np.NaN
    
    df_ds_mapping = df_ds.merge(df_dsdt_full_grp,on=['ky_dau_tu', 'phuong_khong_dau',
                                                     'quan_khong_dau', 'tinh_khong_dau'],how='left')
    df_ds_mapping['port_6t_hien_tai'] = np.where(df_ds_mapping['tong_port_sau_6t_new'].isna(),
                          df_ds_mapping['port_6t_hien_tai'],df_ds_mapping['tong_port_sau_6t_new'])
    df_ds_mapping['port_dung_6t_hien_tai'] = np.where(df_ds_mapping['port_dung_sau_6t_new'].isna(),
                          df_ds_mapping['port_dung_6t_hien_tai'],df_ds_mapping['port_dung_sau_6t_new'])
    df_ds_mapping.drop(['tong_port_sau_6t_new','port_dung_sau_6t_new'],axis=1,inplace=True)
    df_ds_mapping['danh_gia_hieu_qua']=np.where((df_ds_mapping['port_6t_hien_tai']>0)&(df_ds_mapping['port_dung_6t_hien_tai']/df_ds_mapping['port_6t_hien_tai']>=df_ds_mapping['nguong_danh_gia']),
                                               'Hiệu quả',np.where((df_ds_mapping['port_6t_hien_tai']>0)&(df_ds_mapping['port_dung_6t_hien_tai']/df_ds_mapping['port_6t_hien_tai']<df_ds_mapping['nguong_danh_gia']),
                                                 'Không hiệu quả','Chưa xác định'))
    df_ds_mapping['port'] = np.where((df_ds_mapping.port==0)&(df_ds_mapping.port_6t_hien_tai>0),
                                df_ds_mapping.port_6t_hien_tai,
                                df_ds_mapping.port)
    df_ds_mapping['portuse'] = np.where((df_ds_mapping.portuse==0)&(df_ds_mapping.port_dung_6t_hien_tai>0),
                                df_ds_mapping.port_dung_6t_hien_tai,
                                df_ds_mapping.portuse)
    df_ds_mapping.drop_duplicates(inplace=True)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                      ,config['dbs']['dwh_177_report']['password']
                                                     ,config['dbs']['dwh_177_report']['host']
                                                    ,config['dbs']['dwh_177_report']['port']
                                                    ,config['dbs']['dwh_177_report']['dbname']))
    cur = conn.cursor()
    tablename = config['insert_dashboard']['table_ptht']
    sql = """DELETE FROM report.""" + tablename + """ WHERE ky_dau_tu in ('""" + kydautu + """','"""+kydautu_prev+"""');"""
    cur.execute(sql)
    conn.commit()
    engine = create_engine("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    df_ds_mapping.to_sql(tablename, engine,schema='report', if_exists='append', index=False)
    update_label_phattrienhatang(kydautu, config)
    update_label_phattrienhatang(kydautu_prev, config)
    update_port_next(kydautu, config)
