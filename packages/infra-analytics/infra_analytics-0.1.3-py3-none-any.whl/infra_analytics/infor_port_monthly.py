
from sqlalchemy import create_engine
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
from .config import infra_analytics_config

from requests.packages import urllib3
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

import yaml
def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config
    
def connection_v2(user_name,pwd,host,db_name,port):
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


def infor_port_monthly(date, config: dict = infra_analytics_config):
    """
    Cập nhật thông tin port của bộ chia cấp 2 theo tháng:
           + Load data hạ tầng bộ chia cấp 2: /data/fpt/ftel/infra/dwh/splitter_level_2_info.parquet
           + Xử lý cột địa chỉ 
           + Xử lý lấy thông tin tập điểm cấp 2 lúc port cao nhất 
           + Groupby theo tập điểm cấp 1 và tính tổng port hiện hữu 
           + Chuyển đổi kiểu dữ liệu cho đồng bộ schema lưu trữ trước đó trên hive 
           + Lưu data xuống table hive ftel_dwh_infra.infor_port_monthly
    """
    assert config != None, "config must be not None"
        
    start_date = (datetime.strptime(date,"%Y-%m-%d")- timedelta(days=1)).strftime('%Y-%m-01')
    db_name = config['dbs']['dwh_177_report']['dbname']
    user_name = config['dbs']['dwh_177_report']['user']
    pwd = config['dbs']['dwh_177_report']['password']
    host = config['dbs']['dwh_177_report']['host']
    port =config['dbs']['dwh_177_report']['port']
    conn_wr = connection_v2(user_name, pwd, host, db_name , port)
    query = """SELECT * FROM public.dwh_province"""
    df_branch = pd.read_sql(query, conn_wr)
    df_province = df_branch[df_branch.region!='International'].groupby(['province','region'],as_index=False).agg({
    'name':'count'})[['province','region']]
    str_path = config['infor_port_monthly']['splitter_path'] +'d='+start_date[:7]+'-*'
    df_info_port_gp = spark.read.parquet(str_path).cache()
    df_info_port_gp = df_info_port_gp.withColumn('province',upper(col('bo_chia_cap_2').substr(1, 3)))
    df_province_spk =spark.createDataFrame(df_province.astype(str)) 
    df_info_port_gp = df_info_port_gp.join(df_province_spk, on='province', how='left')
    df_info_port_gp = df_info_port_gp.withColumnRenamed("province", "branch")
    df_info_port_gp = df_info_port_gp.withColumn('typedeivce', lit(''))\
                                    .withColumn('type', lit(''))\
                                    .withColumn('status', lit(''))
    df_info_port = df_info_port_gp.sort(col("region").desc(),col("branch").desc(),col("Plans").desc(),col("hop_dau_noi").desc(),col("bo_chia_cap_2").desc(),col("Address").desc(),col("District").desc()
         ,col("ngay_su_dung").desc(),col("ward").desc(),col("sum_port_cai_dat").desc(),col("sum_port_cai_dat_dang_dung").desc()).cache()
    df_info_port_drop = df_info_port.dropDuplicates(['region', 'branch',"Plans",  'hop_dau_noi','bo_chia_cap_2', 'Address', 'District', 'Ward', 'sum_port_cai_dat', 'ngay_su_dung']).cache()
    df_info_port_drop = df_info_port_drop.withColumn('ngay_su_dung',to_timestamp('ngay_su_dung'))
    df_info_port_drop = df_info_port_drop.withColumn("ngay_su_dung", 
                   when(df_info_port_drop.ngay_thi_cong>df_info_port_drop.ngay_su_dung,df_info_port_drop.ngay_thi_cong)
                   .otherwise(df_info_port_drop.ngay_su_dung))
    df_info_port_group = df_info_port_drop.groupBy(['region','typedeivce','type','status','branch','Address','District',
              'Ward','hop_dau_noi',"Plans"]).agg(min('ngay_su_dung').alias('createdate'),
              sum('sum_port_cai_dat').alias('port'),sum('sum_port_cai_dat_dang_dung').alias('portuse'),
              sum('sum_port_cai_dat_free').alias('portfree'),sum('sum_port_bad_die').alias('portmaintain'))
    df_info_port_group = df_info_port_group.withColumn('portdie',lit(0))
    df_info_port_group = df_info_port_group.withColumn('popname',upper(col('hop_dau_noi').substr(1, 7)))
    df_info_port_group = df_info_port_group.withColumn('createdate', to_date(col('createdate')))
    df_info_port_group = df_info_port_group.withColumnRenamed('hop_dau_noi', 'name')
    df_info_port_group = df_info_port_group.withColumn("port",df_info_port_group.port.cast(ShortType()))
    df_info_port_group = df_info_port_group.withColumn("portuse",df_info_port_group.portuse.cast(ShortType()))
    df_info_port_group = df_info_port_group.withColumn("portfree",df_info_port_group.portfree.cast(ShortType()))
    df_info_port_group = df_info_port_group.withColumn("portdie",df_info_port_group.portdie.cast(ShortType()))
    df_info_port_group = df_info_port_group.withColumn("portmaintain",df_info_port_group.portmaintain.cast(ShortType()))
    df_info_port_group = df_info_port_group.withColumn('date',lit(datetime.strptime(start_date,"%Y-%m-%d").date()))
    df_info_port_group = df_info_port_group.withColumn('index',lit(1))
    df_info_port_group = df_info_port_group.select('index','region','branch','popname','name','address','district','ward','port','portuse','portfree',
    'portdie','portmaintain','createdate','typedeivce','type','date','status',"Plans")
    df_info_port_group.withColumn('d',col('date'))\
    .coalesce(1).write.mode("overwrite")\
    .partitionBy('d').parquet(config['infor_port_monthly']['infor_port_monthly_path_output'])
    spark.sql('msck repair table {}.{}'.format(config['infor_port_monthly']['dbs_output'],
                                config['infor_port_monthly']['table_output']))
