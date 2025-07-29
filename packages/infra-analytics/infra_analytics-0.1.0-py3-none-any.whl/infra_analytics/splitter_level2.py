#  đổi từ ngày 2023-04-26 thêm ngày thi công, kỳ đầu tư, mã kế hoạch 
# import psycopg2 as pg
from sqlalchemy import create_engine
from dateutil.relativedelta import relativedelta
# from psycopg2.extras import execute_values
# import psycopg2
import datetime as dt
import psycopg2 as pg
from sqlalchemy import create_engine
import requests
import sqlalchemy
import os
from datetime import datetime, timedelta
import pyspark
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.functions import monotonically_increasing_id 
from pyspark.sql.types import StringType
from pyspark.sql import Window
import pandas as pd
from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql.types import StringType
from pyspark.sql.functions import *
from datetime import datetime,timedelta
import pyspark.sql.functions as f
from pyspark.sql.types import IntegerType,StringType
import numpy as np
import pandas as pd
from pyspark.sql.functions import countDistinct
import re
import urllib.request as urllib
import warnings
warnings.filterwarnings('ignore')
import json
import time
from requests.packages import urllib3
from .config import infra_analytics_config

urllib3.disable_warnings()

os.environ['SPARK_HOME']="/opt/spark/spark-3.0.2-bin-hadoop2.7/"
os.environ['JAVA_HOME']="/usr/jdk64/jdk1.8.0_112/"
os.environ['PYSPARK_DRIVER_PYTHON']="python"
# Do not set in cluster modes
os.environ['HADOOP_OPTS']="-Dhdp.version=3.1.0.0-78"


conf = SparkConf()

# config location for spark finding metadata from hive metadata server
conf.set("hive.metastore.uris", "thrift://master01-dc9c14u40.bigdata.local:9083,thrift://master02-dc9c14u41.bigdata.local:9083")
conf.set("spark.sql.hive.metastore.jars", "/opt/spark/spark-3.0.2-bin-hadoop2.7/*")

# config directory to use for "scratch" space in Spark, including map output files and RDDs that get stored on disk
# conf.set('spark.local.dir', '/tmp/user')
# config in-memory columnar data format that is used in Spark to efficiently transfer data between JVM and Python processes
conf.set("spark.kryoserializer.buffer.max", "2000")
conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
conf.set("spark.sql.execution.arrow.enabled", "true")
conf.set("spark.sql.execution.arrow.pyspark.fallback.enabled", "false")
conf.set("spark.sql.execution.arrow.maxRecordsPerBatch", "50000")


# config spark driver memory
conf.set("spark.driver.memory", '10g')
conf.set('spark.driver.maxResultSize', '5G')
conf.set('spark.default.parallelism', '8')

#set metastore.client.capability.check to false
conf.set("hive.metastore.client.capability.check", "false")

conf.set("spark.ui.port", "7070")
conf.set("spark.driver.extraJavaOptions", "-Dhdp.version=3.1.0.0-78")
conf.set("spark.yarn.am.extraJavaOptions", "-Dhdp.version=3.1.0.0-78")

spark = SparkSession.builder.config(conf=conf).master("local[10]").enableHiveSupport().getOrCreate()
spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")

import yaml
def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config
    
def splitter_level2(date, config: dict = infra_analytics_config):
    """
    Tổ chức và lưu trữ thông tin port của bộ chia tập điểm cấp 2 theo ngày:
        + Lấy data bộ chia tập điểm từ API:http://portapi.fpt.vn/api/APIInfReport/ReportSplitter
        + Xử lý lấy ngày thi công từ mã kế hoạch 
        + Lưu trữ dưới hdfs: /data/fpt/ftel/infra/dwh/splitter_level_2_info.parquet
    """
    start_date =datetime.strptime(date,"%Y-%m-%d")
    if not config:
        config_file = "./config.yaml"
        config = get_config(config_file)
    df_info_port_gp = spark.read.parquet(config['splitter_lv2']['infor_port_monthly_path']).cache()
    df_chinhanh = df_info_port_gp.select('branch').distinct().toPandas()
    df_chinhanh['branch'] = df_chinhanh['branch'].str.upper()
    df_chinhanh.drop_duplicates(keep='first', inplace=True)
    df_full_splitter = pd.DataFrame()
    headers = {
    'content-type': 'application/json',
    }
    proxies = {
    "http_proxy": "http://proxy.hcm.fpt.vn:80",
    "https_proxy": "http://proxy.hcm.fpt.vn:80",
    "no_proxy": "portapi.fpt.vn"
    }
    for i in df_chinhanh['branch']:
        try:
            r = requests.post(config['splitter_lv2']['api_splitter_v2'],
                          headers=headers, json={  "Branch": i}, proxies=proxies)
            critical_dict = json.loads(r.text)
            lst_data_single = critical_dict['Data']
            lst_data_single = pd.DataFrame(lst_data_single)
            df_full_splitter = df_full_splitter.append(lst_data_single)
            time.sleep(3)
            # print(df_full_splitter.shape)
        except:
            continue
    df_full_splitter.drop_duplicates(keep='first', inplace=True)
    print(df_full_splitter.shape)
    print(df_full_splitter.columns)
    # tách ngày thi công  
    df_full_splitter['str_ngay_thi_cong'] = df_full_splitter['Plans'].apply(lambda x:str(x).split('.') if str(x)!='' else None)
    df_full_splitter['str_ngay_thi_cong'] = df_full_splitter['str_ngay_thi_cong'].str[-2]
    df_full_splitter['ngay_thi_cong'] = np.where(df_full_splitter['str_ngay_thi_cong'].str.contains('PP'),
              df_full_splitter['str_ngay_thi_cong'].str[-6:],df_full_splitter['str_ngay_thi_cong'])
    df_full_splitter['ngay_thi_cong'] = pd.to_datetime(df_full_splitter['ngay_thi_cong']
                                          , format='%d%m%y', errors='coerce')
    df_full_splitter['ky_dau_tu'] = df_full_splitter['ngay_thi_cong'].apply(lambda x: '1H'+ str(x.year) 
                                    if ((x.month>=1)&(x.month<7))
                                    else '2H'+ str(x.year) )
    df_full_splitter.replace({'ky_dau_tu':{'2Hnan':None}},regex=True, inplace=True)
    print(df_full_splitter.shape)
    df_full_splitter = df_full_splitter.fillna(np.nan)
    df_full_splitter_spk = spark.createDataFrame(df_full_splitter) 
    df_full_splitter_spk = df_full_splitter_spk.withColumn('date_time', lit(start_date))
    df_full_splitter_spk = df_full_splitter_spk.withColumn('ten_olt', df_full_splitter_spk['ten_olt'].cast(StringType()))
    df_full_splitter_spk.withColumn('d',to_date(col('date_time')))\
        .coalesce(1).write.mode("overwrite")\
        .partitionBy('d').parquet(config['splitter_lv2']['splitter_v2_path_output'])
    spark.sql('msck repair table {}.{}'.format(config['splitter_lv2']['dbs_output'],
                                        config['splitter_lv2']['table_output']))

def get_ngaybatdau(kydautu):
    if kydautu[0]=='1':
        ngaybatdau = str(kydautu[2:])+'-01-01'
    else:
        ngaybatdau = str(kydautu[2:])+'-07-01'
    return ngaybatdau
def get_kydautu(date):
    if (date.month>=1)&(date.month<7):
        kydautu = '1H'+str(date.year)
    else:
        kydautu= '2H'+str(date.year)
    return kydautu
def get_ngaydautu(date_init, config: dict = infra_analytics_config):
    """
    Cập nhật thông tin về ngày đầu tư phục vụ cho dashboard phát triển hạ tầng:
        + Load data ngày đầu tư: report.tbl_ngay_dau_tu (postgresql server 177 - dwh_noc)
        + init ngày đầu tư mới bằng ngày hiện tại cộng lên 4 tháng => vì thời gian chạy đề xuất cho mỗi kỳ trước 4 tháng
        + Upsert data trong bảng report.tbl_ngay_dau_tu (nếu chưa tồn tại ngày mới init)
    """
    # conn = pg.connect("postgresql://dwh_noc_report_web_infra_admin:Wre0Astustifrephlwex@172.27.11.178:6543/dwh_noc")
    if not config:
        config_file = "./config.yaml"
        config = get_config(config_file)
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    str_sql = "select * from  report.tbl_ngay_dau_tu"
    df_date_raw = pd.read_sql(str_sql, conn)
    df_date_raw.drop(['created_at','updated_at'],axis=1,inplace=True)
    df_date_raw.drop(['index_kdt','next_index'],axis=1,inplace=True)
    date = dt.datetime.strptime(date_init, '%Y-%m-%d').date()
    month_prev4m = (date + relativedelta(months=4)).strftime('%Y-%m-%d')
    df_date = pd.DataFrame([month_prev4m], columns=['date'])
    df_date['date'] = pd.to_datetime(df_date['date'])
    df_date['nam_'] = df_date['date'].apply(lambda x: x - relativedelta(years=0, month=1, day=1))
    df_date['ky_dau_tu'] = df_date['date'].apply(lambda x: get_kydautu(x))
    df_date['ngay_bat_dau'] = df_date['ky_dau_tu'].apply(lambda x: get_ngaybatdau(x))
    df_date['ngay_bat_dau'] = pd.to_datetime(df_date['ngay_bat_dau'].astype(str))
    df_date = pd.concat([df_date_raw,df_date])
    df_date['ngay_bat_dau'] = pd.to_datetime(df_date['ngay_bat_dau'].astype(str))
    df_date['date'] = pd.to_datetime(df_date['date'].astype(str))
    df_date['nam_'] = pd.to_datetime(df_date['nam_'].astype(str))
    df_date_gp = df_date.groupby(['ngay_bat_dau'],as_index=False).agg({
        'date':'count'})[['ngay_bat_dau']].sort_values('ngay_bat_dau')
    df_date_gp['index_kdt'] = df_date_gp['ngay_bat_dau'].rank().astype(int)
    df_date_gp['next_index'] = df_date_gp['index_kdt']+1
    df_date = df_date.merge(df_date_gp, on=['ngay_bat_dau'], how='left')
    df_date.drop_duplicates(keep='first',inplace=True)
    lst_data = df_date.values.tolist()
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s" % (config['dbs']['dwh_177_report']['user']
                                                          ,config['dbs']['dwh_177_report']['password']
                                                         ,config['dbs']['dwh_177_report']['host']
                                                        ,config['dbs']['dwh_177_report']['port']
                                                        ,config['dbs']['dwh_177_report']['dbname']))
    cur_1 = conn.cursor()
    for i in range(len(lst_data)):
        tupl = (lst_data[i])
        cur_1.execute(
        " INSERT INTO report.tbl_ngay_dau_tu(date,nam_,ky_dau_tu, ngay_bat_dau,index_kdt,next_index) VALUES( %s, %s, %s, %s, %s, %s)"
        " ON CONFLICT (date)"
        " DO UPDATE SET nam_ = EXCLUDED.nam_, ky_dau_tu = EXCLUDED.ky_dau_tu, ngay_bat_dau = EXCLUDED.ngay_bat_dau"
        ", index_kdt = EXCLUDED.index_kdt, next_index = EXCLUDED.next_index;", (tuple(tupl)))
    try:
        conn.commit()
        conn.close()
        print("Successfully!!!!")
    except:
        print("Don't save DB")