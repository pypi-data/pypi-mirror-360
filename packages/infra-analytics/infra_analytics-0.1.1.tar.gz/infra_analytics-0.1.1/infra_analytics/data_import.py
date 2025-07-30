import os
import spark_sdk as ss
ss.__version__
import os
ss.PySpark(yarn=False, num_executors=60, driver_memory='60g', executor_memory='24g',
            add_on_config1=('spark.port.maxRetries', '1000'))
spark = ss.PySpark().spark

from pyspark.sql.window import Window
from pyspark.sql.functions import row_number
import pyspark.pandas as ps
from pyspark.sql.functions import to_date,col
spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")
from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import glob, re

import sh
import requests
import pandas as pd
import psycopg2 as pg
from sqlalchemy import create_engine

import yaml
from .config import infra_analytics_config

def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config
    
def extract_date(file_path):
    # Split tên file để lấy phần ngày tháng
    file_name = file_path.split('/')[-1]  # Lấy phần cuối cùng sau dấu '/'
    date_str = file_name.split('_')[-1]   # Lấy phần sau dấu '_' chứa ngày tháng
    date_str = date_str.replace('.xlsx','')
    # Chuyển đổi từ string sang datetime
    return datetime.strptime(date_str, '%Y%m%d')
def process_hodannam(year,config):
    """
    Tổ chức lưu trữ thông tin hộ dân hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/ho_dan 
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/ho_dan.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['hodan_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df.columns = ['Mã tỉnh', 'Tỉnh', 'Mã quận', 'Quận', 'Mã phường', 'Phường', 'Tổng hộ',
               'Thành thị', 'Nông thôn', 'Năm']
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['hodan_path_output'])\
        .save()

def process_dansonam(year,config):
    """
    Tổ chức lưu trữ thông tin dân số hàng năm:
        + input:/data/fpt/ftel/infra/dwh/import_data_phattrienhatang/dan_so
        + output:/data/fpt/ftel/infra/dwh/phat_trien_ha_tang/dan_so.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['danso_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df.columns = ['Mã tỉnh', 'Tỉnh', 'Mã quận', 'Quận', 'Mã phường', 'Phường', 'Tổng số dân',
           'Dân số Nông thôn', 'Dân số Thành thị', 'Năm']
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['danso_path_output'])\
        .save()
def process_thanhphandansonam(year,config):
    """
    Tổ chức lưu trữ thông tin dân số hàng năm:
        + input:/data/fpt/ftel/infra/dwh/import_data_phattrienhatang/thanh_phan_dan_so
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/thanh_phan_dan_so.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['thanhphandanso_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df.columns = ['Mã tỉnh', 'Tỉnh', 'Mã quận', 'Quận', 'Mã phường', 'Phường',
           'Dưới tiểu học', 'Tiểu học', 'Trung học', 'Cao đẳng', 'Đại học',
           'Thạc sỹ', 'Tiến sỹ', 'Năm']
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['thanhphandanso_path_output'])\
        .save()

def process_nganhangnam(year,config):
    """
    Tổ chức lưu trữ thông tin ngân hàng hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/ngan_hang
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/ngan_hang.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['nganhang_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['nganhang_path_output'])\
        .save()
        
def process_chitieunam(year,config):
    """
    Tổ chức lưu trữ thông tin bình quân chi tiêu hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/chi_tieu
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/chi_tieu.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['chitieu_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['chitieu_path_output'])\
        .save()

def process_benhviennam(year,config):
    """
    Tổ chức lưu trữ thông tin bệnh viện hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/benh_vien
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/benh_vien.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['benhvien_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['benhvien_path_output'])\
        .save()

def process_trung_tam_y_tenam(year,config):
    """
    Tổ chức lưu trữ thông tin trung tâm y tế hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/trung_tam_y_te
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/trung_tam_y_te.parquet 
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['yte_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['yte_path_output'])\
        .save()
def process_truong_tieu_hocnam(year,config):
    """
    Tổ chức lưu trữ thông tin trường tiểu học hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/truong_tieu_hoc
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_tieu_hoc.parquet
    """

    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['tieuhoc_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['tieuhoc_path_output'])\
        .save()
def process_truong_trung_hoc_co_sonam(year,config):
    """
    Tổ chức lưu trữ thông tin trường trung học cơ sở hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/truong_trung_hoc_co_so
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_trung_hoc_co_so.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['trunghoccoso_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['trunghoccoso_path_output'])\
        .save()
def process_truong_trung_hoc_pho_thongnam(year,config):
    """
    Tổ chức lưu trữ thông tin trường trung học phổ thông hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/truong_trung_hoc_pho_thong
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_trung_hoc_pho_thong.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['trunghocphothong_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['trunghocphothong_path_output'])\
        .save()

def process_truong_dai_hocnam(year,config):
    """
    Tổ chức lưu trữ thông tin trường đại học hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/truong_dai_hoc
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_dai_hoc.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['truongdaihoc_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['truongdaihoc_path_output'])\
        .save()
def process_truong_cao_dangnam(year,config):
    """
    Tổ chức lưu trữ thông tin trường cao đẳng hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/truong_cao_dang
        + output:/data/fpt/ftel/infra/dwh/phat_trien_ha_tang/truong_cao_dang.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['truongcaodang_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['truongcaodang_path_output'])\
        .save()
def process_chonam(year,config):
    """
    Tổ chức lưu trữ thông tin chợ hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/cho
        + output:/data/fpt/ftel/infra/dwh/phat_trien_ha_tang/cho.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['cho_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['cho_path_output'])\
        .save()
def process_sieu_thinam(year,config):
    """
    Tổ chức lưu trữ thông tin siêu thị hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/sieu_thi
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/sieu_thi.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['sieuthi_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['sieuthi_path_output'])\
        .save()

def process_trung_tam_thuong_mainam(year,config):
    """
    Tổ chức lưu trữ thông tin trung tâm thương mại hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/trung_tam_thuong_mai
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/trung_tam_thuong_mai.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['trungtamthuongmai_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['trungtamthuongmai_path_output'])\
        .save()
def process_doanh_nghiepnam(year,config):
    """
    Tổ chức lưu trữ thông tin doanh nghiệp hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/doanh_nghiep
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['doanhnghiep_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['doanhnghiep_path_output'])\
        .save()
def process_doanh_nghiep_vua_va_nhonam(year,config):
    """
    Tổ chức lưu trữ thông tin doanh nghiệp vừa và nhỏ hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/doanh_nghiep_vua_va_nho
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_vua_va_nho.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['doanhnghiepvuanho_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['doanhnghiepvuanho_path_output'])\
        .save()

def process_doanh_nghiep_tu_nhannam(year,config):
    """
    Tổ chức lưu trữ thông tin doanh nghiệp tư nhân hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/doanh_nghiep_tu_nhan
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_tu_nhan.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['doanhnghieptunhan_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['doanhnghieptunhan_path_output'])\
        .save()
def process_khach_sannam(year,config):
    """
    Tổ chức lưu trữ thông tin khách sạn hàng năm:
        + input:/data/fpt/ftel/infra/dwh/import_data_phattrienhatang/khach_san
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/khach_san.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['khachsan_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['khachsan_path_output'])\
        .save()
def process_khach_san_tu_nhannam(year,config):
    """
    Tổ chức lưu trữ thông tin khách sạn tư nhân hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/khach_san_tu_nhan
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/khach_san_tu_nhan.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['khachsantunhan_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['khachsantunhan_path_output'])\
        .save()
def process_doanh_nghiep_co_von_nuoc_ngoainam(year,config):
    """
    Tổ chức lưu trữ thông tin doanh nghiệp có vốn nước ngoài hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/doanh_nghiep_co_von_nuoc_ngoai
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_co_von_nuoc_ngoai.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['doanhnghiepnuocngoai_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['doanhnghiepnuocngoai_path_output'])\
        .save()
def process_doanh_nghiep_co_hoat_dong_xuat_nhap_khaunam(year,config):
    """
    Tổ chức lưu trữ thông tin doanh nghiệp có hoạt động xuất nhập khẩu hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/doanh_nghiep_co_hoat_dong_xuat_nhap_khau
        + output:/data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_co_hoat_dong_xuat_nhap_khau.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['doanhnghiepxuatnhapkhau_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['doanhnghiepxuatnhapkhau_path_output'])\
        .save()
def process_doanh_nghiep_cong_nghe_thong_tinnam(year,config):
    """
    Tổ chức lưu trữ thông tin doanh nghiệp công nghệ thông tin hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/doanh_nghiep_cong_nghe_thong_tin
        + output:/data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_cong_nghe_thong_tin.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['doanhnghiepcntt_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['doanhnghiepcntt_path_output'])\
        .save()
def process_doanh_nghiep_co_trang_thong_tin_dien_tunam(year,config):
    """
    Tổ chức lưu trữ thông tin doanh nghiệp có trang thông tin điện tử hàng năm:
        + input: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/doanh_nghiep_co_trang_thong_tin_dien_tu
        + output: /data/fpt/ftel/infra/dwh/phat_trien_ha_tang/doanh_nghiep_co_trang_thong_tin_dien_tu.parquet
    """
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['doanhnghiepttdt_path_input']
    # Initialize an empty list to store matching file paths
    matching_files = []
    
    # Iterate through the file list
    for file_path in filelist:
        # Check if the keyword is present in the file path
        if keyword in file_path:
            # If yes, append the file path to the matching_files list
            matching_files.append(file_path)
    # Lấy ra file có ngày tạo gần đây nhất
    recent_file = max(matching_files, key=extract_date)
    print(recent_file)
    df= ps.read_excel(recent_file)
    df['Năm'] = year
    df_ = spark.createDataFrame(df.to_pandas())
    df_ = df_.withColumn('d', to_date(col('Năm')))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('d')\
        .option("path", config['data_import']['doanhnghiepttdt_path_output'])\
        .save()
# Hàm để lấy dữ liệu từ một trang cụ thể
def fetch_data(page, limit, config:dict = infra_analytics_config):
    if not config:
        config_file = "./config.yaml"
        config_api = get_config(config_file)
    url = config_api['data_import']['api_getstarpop']+ f'?page={page}&limit={limit}'
    headers = {
    'content-type': 'application/json',
    }
    proxies = {
    "http_proxy": "http://proxy.hcm.fpt.vn:80",
    "https_proxy": "http://proxy.hcm.fpt.vn:80",
    "no_proxy": "icdp.fpt.net"
    }
    response = requests.get(url,
                  headers=headers, 
                  proxies=proxies)
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Hàm để lấy toàn bộ dữ liệu từ API
def fetch_all_data(base_url, limit=10000):
    all_data = []
    page = 1
    while True:
        print(page)
        data = fetch_data(page, limit)
        if (len(data['data']['data'])==0):  # Nếu không còn dữ liệu mới, dừng lại
            break
        all_data.extend(data['data']['data'])
        page += 1
    return all_data
def process_get_star_pop(month,config):
    """
    Tổ chức lưu trữ thông tin đánh giá chất lượng POP theo thời gian:
    + Get data từ api https://icdp.fpt.net/flask/cads/get_star_pop
    + Lưu dữ liệu xuống postgresql 177 - dwh_noc - public.tbl_quality_pop
    """
    # Sử dụng hàm để lấy toàn bộ dữ liệu
    base_url = config['data_import']['api_getstarpop']
    all_data = fetch_all_data(base_url)
    lst_data_single = pd.DataFrame(all_data)
    lst_data_single.columns=['month','avg_operation_pop','avg_quality_pop','pop','province']
    lst_data_single['month'] = pd.to_datetime(lst_data_single['month'])
    tablename_pop = config['data_import']['tablename_qualitypop']
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur = conn.cursor()
    sql = """DELETE FROM public.""" + tablename_pop +""" WHERE month = '""" + month + """';"""
    cur.execute(sql)
    conn.commit()
    engine = create_engine("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    lst_data_single[lst_data_single.month==month].to_sql(tablename_pop, engine, if_exists='append', index=False, schema='public')

def process_dataimport(date, config: dict = infra_analytics_config):
    if (int(date[5:7])>=3)&(int(date[5:7])<9):
        kydautu = '2H'+str(int(date[:4]))
    else:
        if (int(date[5:7])>=1)&(int(date[5:7])<3):
            kydautu= '1H'+str(int(date[:4]))
        else:
            kydautu= '1H'+str(int(date[:4])+1)
    year=kydautu[2:]+'-01-01'
    if not config:
        config_file = "./config.yaml"
        config = get_config(config_file)
    
    process_get_star_pop(date,config)
    process_dansonam(year,config)
    process_hodannam(year,config)
    process_thanhphandansonam(year,config)
    process_nganhangnam(year,config)
    process_chitieunam(year,config)
    process_benhviennam(year,config)
    process_trung_tam_y_tenam(year,config)
    process_truong_tieu_hocnam(year,config)
    process_truong_trung_hoc_co_sonam(year,config)
    process_truong_trung_hoc_pho_thongnam(year,config)
    process_truong_dai_hocnam(year,config)
    process_truong_cao_dangnam(year,config)
    process_chonam(year,config)
    process_sieu_thinam(year,config)
    process_trung_tam_thuong_mainam(year,config)
    process_doanh_nghiepnam(year,config)
    process_doanh_nghiep_vua_va_nhonam(year,config)
    process_doanh_nghiep_tu_nhannam(year,config)
    process_khach_sannam(year,config)
    process_khach_san_tu_nhannam(year,config)
    process_doanh_nghiep_co_von_nuoc_ngoainam(year,config)
    process_doanh_nghiep_co_hoat_dong_xuat_nhap_khaunam(year,config)
    process_doanh_nghiep_cong_nghe_thong_tinnam(year,config)
    process_doanh_nghiep_co_trang_thong_tin_dien_tunam(year,config)