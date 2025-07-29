# import psycopg2 as pg
from sqlalchemy import create_engine
# from psycopg2.extras import execute_values
# Link tham khảo: https://viblo.asia/p/web-crawling-voi-thu-vien-beautifulsoup-1VgZvNGOZAw

# import psycopg2
import requests
import sqlalchemy
# accented_string is of type 'unicode'
import os
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
import pyspark.sql.functions as f
from pyspark.sql.types import IntegerType,ShortType
import numpy as np
import pandas as pd
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
from pyspark.sql.functions import countDistinct
import seaborn as sns
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
import re
import urllib.request as urllib
import warnings
warnings.filterwarnings('ignore')
os.environ['http_proxy'] = "http://proxy.hcm.fpt.vn:80"
os.environ['https_proxy'] = "http://proxy.hcm.fpt.vn:80"
from sklearn.preprocessing import StandardScaler
# use feature importance for feature selection
from numpy import loadtxt
from numpy import sort
# import datetime as dt
import pytz

from pyspark.sql.functions import countDistinct
# import datetime
from dateutil.relativedelta import relativedelta
import sqlalchemy
import psycopg2 as pg

from requests.packages import urllib3
urllib3.disable_warnings()
from .config import infra_analytics_config

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
conf.set("spark.driver.memory", '60g')
conf.set('spark.driver.maxResultSize', '5G')
conf.set('spark.default.parallelism', '8')

#set metastore.client.capability.check to false
conf.set("hive.metastore.client.capability.check", "false")

conf.set("spark.ui.port", "7070")
conf.set("spark.driver.extraJavaOptions", "-Dhdp.version=3.1.0.0-78")
conf.set("spark.yarn.am.extraJavaOptions", "-Dhdp.version=3.1.0.0-78")

spark = SparkSession.builder.config(conf=conf).master("local[40]")\
.config("spark.jars", "/mnt/projects-data/infra_report/jars/postgresql-42.2.20.jar")\
.enableHiveSupport().getOrCreate()
spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yaml

def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config
    
def infra_tangtruongport(end, config: dict = infra_analytics_config):
    """
    Tính toán và lưu trữ thông tin tăng trưởng port từ 1-6 tháng để phục vụ cho feature training model:
        - Load data hạ tầng port hiện hữu từ ftel_dwh_infra.infor_port_monthly theo kỳ đầu tư 
        - Tính index_month dựa trên tháng cập nhật dữ liệu 
        - Groupby theo 'Kỳ đầu tư','region','branch','district','ward','date','index_month' và tính tổng port, portuse, portfree, portdie, portmaintain
        - Xử lý lấy thông tin port hiện hữu theo index_month và lấy vào thời điểm ghi nhận port max 
        - Tính tốc độ tăng trưởng port, portuse, portfree, portdie, portmaintain trên  'Kỳ đầu tư','region','branch', 'district','ward'
        - Tính tuổi của các tập điểm theo mốc ghi nhận hạ tầng hiện hữu 
        - Groupby 'Kỳ đầu tư','region','branch','district','ward' và tính trung bình tuổi 
        - Mapping tất cả thông tin lại và lưu trữ vào postgresql 177 - dwh_noc - public.tbl_tang_truong_port
    """
    start = (datetime.strptime(end, '%Y-%m-%d') - relativedelta(months=6)).strftime('%Y-%m-01')
    if int(end[5:7])==9:
        kydautu = '1H'+str(1+int(end[:4]))
    else:
        kydautu= '2H'+str(int(end[:4]))
    if not config:
        config_file = "./config.yaml"
        config = get_config(config_file)
    sql_str = """select * from {}.{} where date>='{}'
                and date<'{}'""".format(config['infor_port_monthly']['dbs_output'],
                                        config['infor_port_monthly']['table_output'],start,end)
    df_port= spark.sql(sql_str)
    df_port =df_port.withColumn('Kỳ đầu tư',lit(kydautu))
    
    df_port_ =df_port.withColumn('index_month',when((month(df_port.date)).isin(2,8), "T0")
                                            .when((month(df_port.date)).isin(1,7), "T1")
                                            .when((month(df_port.date)).isin(12,6), "T2")
                                            .when((month(df_port.date)).isin(11,5), "T3")
                                            .when((month(df_port.date)).isin(10,4), "T4")
                                            .when((month(df_port.date)).isin(9,3), "T5")).cache()
    df_port_grp = df_port_.groupBy(['Kỳ đầu tư','region','branch','district','ward','date','index_month']).agg(
    sum('port').alias('port'), sum('portuse').alias('portuse'),sum('portfree').alias('portfree')
    ,sum('portdie').alias('portdie'),sum('portmaintain').alias('portmaintain')).cache()
    df_port_grp = df_port_grp.sort(desc('Kỳ đầu tư'),desc('region'),desc('branch'),desc('district'),desc('ward'),desc('index_month'),desc('port'),desc('portuse'))
    df_port_grp= df_port_grp.dropDuplicates(subset=['Kỳ đầu tư', 'region','branch','district','ward','index_month'])
    df_port_pd = df_port_grp.toPandas()
    df_port_pd= df_port_pd.sort_values(['Kỳ đầu tư','region','branch','district','ward','date','index_month'],ascending=True)
    df_port_pd['TT_port'] = df_port_pd.groupby(['Kỳ đầu tư','region','branch',
                                                   'district','ward'])['port'].diff(1)
    df_port_pd['TT_portuse'] = df_port_pd.groupby(['Kỳ đầu tư','region','branch',
                                                   'district','ward'])['portuse'].diff(1)
    df_port_pd['TT_portfree'] = df_port_pd.groupby(['Kỳ đầu tư','region','branch',
                                                   'district','ward'])['portfree'].diff(1)
    df_port_pd['TT_portdie'] = df_port_pd.groupby(['Kỳ đầu tư','region','branch',
                                                   'district','ward'])['portdie'].diff(1)
    df_port_pd['TT_portmaintain'] = df_port_pd.groupby(['Kỳ đầu tư','region','branch',
                                                   'district','ward'])['portmaintain'].diff(1)
    df_port_pd_filter = df_port_pd[df_port_pd.index_month.isin(['T1','T2','T3','T4','T5'])][['Kỳ đầu tư','region','branch',
                                                   'district','ward','index_month','TT_port','TT_portuse',
                                                    'TT_portfree' ,'TT_portdie','TT_portmaintain']]
    df_port =df_port.withColumn('Tuổi',datediff(to_date(lit(end),"yyyy-MM-dd"),df_port['createdate'])).cache()
    df_port_filter = df_port.filter(df_port.Tuổi>0)
    df_port_filter = df_port_filter.sort(desc('Kỳ đầu tư'),desc('region'),desc('branch'),desc('district'),desc('ward'),desc('popname'),desc('name'),desc('Tuổi'))
    df_port_filter = df_port_filter.dropDuplicates(['Kỳ đầu tư','region','branch','district','ward','popname'
                                                     ,'name','Tuổi'])
    df_port_tuoi_gp =df_port_filter.groupBy(['Kỳ đầu tư','region','branch','district','ward']).agg(
                            mean('Tuổi').alias('Tuổi')).cache()
    df_port_tuoi_pd = df_port_tuoi_gp.toPandas()
    df_port_full = df_port_pd_filter.merge(df_port_tuoi_pd, on=['Kỳ đầu tư','region','branch','district','ward']
                                           , how='outer')
    df_port_full.columns= ['ky_dau_tu', 'region', 'branch', 'district', 'ward', 'index_month',
           'tang_truong_port', 'tang_truong_portuse', 'tang_truong_portfree', 'tang_truong_portdie', 
           'tang_truong_portmaintain','tuoi']
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur = conn.cursor()
    tablename = config['tangtruong_port']['table_name']
    sql = """DELETE FROM """ + tablename + """ WHERE ky_dau_tu = '""" + kydautu + """';"""
    cur.execute(sql)
    conn.commit()
    engine = create_engine("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    df_port_full.to_sql(tablename, engine, if_exists='append', index=False)