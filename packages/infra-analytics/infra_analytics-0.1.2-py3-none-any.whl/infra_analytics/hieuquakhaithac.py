
import spark_sdk as ss
ss.__version__
import os
ss.PySpark(yarn=False, num_executors=60, driver_memory='60g', executor_memory='24g',
            add_on_config1=('spark.port.maxRetries', '1000'))
spark = ss.PySpark().spark
from pyspark.sql.types import DoubleType, IntegerType
spark.sql("SET spark.sql.sources.partitionOverwriteMode = dynamic")
from pyspark.sql.window import Window
from pyspark.sql.functions import row_number,col

from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import glob, re
import pyspark.pandas as ps
import sh
import pyspark.sql.functions as f
import sqlalchemy
import psycopg2 as pg
from .config import infra_analytics_config

import yaml
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

def process_perport(kydautu, config: dict = infra_analytics_config):
    """
    Tổ chức lưu trữ dữ liệu về chi phí đầu tư của các kế hoạch theo kỳ:
       + Load data import: /data/fpt/ftel/infra/dwh/import_data_phattrienhatang/chi_phi_dau_tu
       + Chuyển đổi kiểu dữ liệu cho đồng bộ schema lưu trữ trước đó
       + Lưu data xuống hdfs:/data/fpt/ftel/infra/dwh/phat_trien_ha_tang/chi_phi_dau_tu.parquet 
       + Groupby theo mã kế hoạch tính trung bình chi phí đầu tư mỗi port 
    """
    if not config:
        config_file = "./config.yaml"
        config = get_config(config_file)
    hdfsdir = config['data_import']['source_path']
    filelist = [ line.rsplit(None,1)[-1] for line in sh.hdfs('dfs','-ls',hdfsdir).split('\n') if len(line.rsplit(None,1))][1:]
    keyword = config['data_import']['chiphidautu_path_input']
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
    df= ps.read_excel(recent_file,dtype=str)
    df = df.rename({'DL triển khai':'Dung lượng triển khai',
               'Phường':'Phường/Xã',
               'Quận':'Quận/Huyện',
               'Ngày hoàn tất thi công':'Ngày hoàn tất'}, axis=1)
    df = df[['Kỳ đầu tư','Vùng','Chi nhánh','Loại KH','POP','Dung lượng triển khai',
        'Phường/Xã','Quận/Huyện','Mã kế hoạch','Tổng chi phí','Perport','Ngày hoàn tất']]
    df.columns = ['ky_dau_tu', 'Vùng', 'Chi nhánh', 'Loại KH', 'POP',
           'Dung lượng triển khai', 'Phường/Xã', 'Quận/Huyện', 'ma_ke_hoach',
           'Tổng chi phí', 'perport', 'Ngày hoàn tất thi công']
    
    df_grp = df.groupby('ky_dau_tu',as_index=False).agg({'ma_ke_hoach':'count'})
    kydautu_max = df_grp[df_grp.ma_ke_hoach==df_grp.ma_ke_hoach.max()]['ky_dau_tu'][0]
    df_w = df[df.ky_dau_tu==kydautu_max]
    
    df_ = spark.createDataFrame(df_w.to_pandas())
    df_ = df_.withColumn("Dung lượng triển khai", df_["Dung lượng triển khai"].cast(IntegerType()).alias("Dung lượng triển khai"))
    df_ = df_.withColumn("Tổng chi phí", df_["Tổng chi phí"].cast(DoubleType()).alias("Tổng chi phí"))
    df_ = df_.withColumn("perport", df_["perport"].cast(DoubleType()).alias("perport"))
    
    df_ = df_.withColumn('kydautu', col('ky_dau_tu'))
    df_.coalesce(1)\
        .write.mode("overwrite")\
        .partitionBy('kydautu')\
        .option("path", config['data_import']['chiphidautu_path_output'])\
        .save()

    df_dt_perport = df[df.ky_dau_tu==kydautu].groupby(['ma_ke_hoach'],as_index=False).agg({'perport':'mean'})
    df_dt_perport['check_kh']=1
    return df_dt_perport
    
def tbl_planning_history(date, config: dict = infra_analytics_config):
    """
    Upsert hiệu quả khai thác của các kế hoạch theo thời gian:
       + Load data từ /data/fpt/ftel/infra/dwh/infor_port_monthly.parquet
       + Xử lý lấy ngày thi công từ mã kế hoạch => Nếu createdate null thì gán bằng ngày thi công
       + Xử lý lấy ngày used_date là ngày createdate sớm nhất (nếu có nhiều createdate)
       + Tính tuổi tập điểm: date (ngày ghi nhận dữ liệu) - used_date (ngày đưa vào sử dụng)
       + Tính delta_month (3T, 6T, 9T, 12T, > 1 năm): từ tuổi của tập điểm 
       + Lọc lấy thời điểm mà tập điểm có port cao nhất theo: 'Plans','region', 'branch','district','ward', 'popname', 'name',  'delta_month'
       + Groupby: 'Plans','ky_dau_tu', 'popname','region', 'branch','district','ward', 'delta_month' => Tính tổng port, portuse 
       + Pivot table để có các cột port theo delta_month
       + Mapping thêm chi phí đầu tư mỗi port từ function process_perport 
       + Tính tỉ lệ khai thác theo các khoảng thời gian: port_use/port
       + Thực hiện upsert vào bảng lưu trữ lịch sử đầu tư trước đó tbl_planning_history (server 177 - dwh_noc)
    """
    assert config != None, "config must be not None"
        
    date = datetime.strptime(date, '%Y-%m-%d')
    if (date.month>=1)&(date.month<7):
        kydautu = '1H'+str(date.year)
    else:
        kydautu= '2H'+str(date.year)
     
    base_path = config['infor_port_monthly']['infor_port_monthly_path_output']
    df= spark.read.parquet(base_path).cache()
    df = df.withColumn('str_ngay_thi_cong', f.split(df['Plans'], '[.]').getItem(4))
    df = df.withColumn('str_ngay_thi_cong', f.when(f.col('str_ngay_thi_cong').contains('PP'), f.col('str_ngay_thi_cong').substr(-6, 6))\
         .otherwise(f.col('str_ngay_thi_cong')))
    df = df.withColumn('ngay_thi_cong', f.to_date(df["str_ngay_thi_cong"], "ddMMyy"))
    df = df.withColumn('createdate', f.when(df.createdate.isNull(),df.ngay_thi_cong).otherwise(df.createdate))
    df_drp = df.groupBy(['Plans','region','branch','district','ward','popname','name','port','portuse','portfree',
                'createdate', 'date']).agg(f.count(f.col('d')).alias('num_row')).cache()
    df_old =df.groupBy(['Plans','region','branch','district','ward','popname','name']).agg(f.min(f.col('createdate')).alias('used_date')).cache()
    df_full = df_drp.join(df_old, on=['Plans','region','branch','district','ward','popname','name'], how='left').cache()
    df_full= df_full.withColumn("month_old_device", f.round(f.months_between(f.col("date"),f.col("used_date")),0)).cache()
    df_full= df_full.withColumn("delta_month",f.when(df_full.month_old_device <=3, '3T')\
            .when((df_full.month_old_device > 3)&(df_full.month_old_device <=6), '6T')\
            .when((df_full.month_old_device > 6)&(df_full.month_old_device <=9), '9T')\
            .when((df_full.month_old_device > 9)&(df_full.month_old_device <=12), '12T').otherwise('>1 năm')).cache()
    df_full_prp = df_full.sort(f.col("Plans").desc(),f.col("region").desc(),f.col("branch").desc(),f.col("district").desc(),f.col("ward").desc()
        ,f.col("popname").desc(),f.col("name").desc(),f.col("delta_month").desc(),f.col("date").desc())
    df_full_prp = df_full_prp.dropDuplicates(['Plans','region', 'branch','district','ward', 'popname', 'name', 
                                              'delta_month']).cache()
    df_full_prp = df_full_prp.filter(df_full_prp.delta_month!='>1 năm')
    df_full_prp = df_full_prp.withColumn('ky_dau_tu',f.when((f.month(df_full_prp.createdate)>=1)&\
                            (f.month(df_full_prp.createdate)<7),f.concat(f.lit('1H'),f.lit(f.year(df_full_prp.createdate))))\
                            .otherwise(f.concat(f.lit('2H'),f.lit(f.year(df_full_prp.createdate)))))
    df_full_plans = df_full_prp.groupBy(['Plans','ky_dau_tu', 'popname','region', 'branch','district','ward',
                           'delta_month']).agg(f.sum('port').alias('port'),f.sum('portuse').alias('portuse'))
    df_port_pd = df_full_plans.toPandas()
    df_port_pd= df_port_pd.sort_values(['Plans','ky_dau_tu', 'popname','region', 'branch','district','ward',
                           'delta_month'],ascending=True)
    df_port_pd_filter = df_port_pd[df_port_pd.Plans!='']
    df_port_pd_filter.rename({'Plans':'ma_ke_hoach'},axis=1,inplace=True)
    df_port_pivot = pd.pivot_table(df_port_pd_filter, values=['port','portuse'], index=['ma_ke_hoach',
                'ky_dau_tu', 'popname', 'region', 'branch', 'district', 'ward'],
                         columns=['delta_month'],  aggfunc={"mean"}, fill_value=None).reset_index()
    df_port_pivot.columns=['ma_ke_hoach','ky_dau_tu', 'pop', 'vung', 'chi_nhanh'
    , 'quan', 'phuong','tong_port_sau_12t','tong_port_sau_3t',
    'tong_port_sau_6t','tong_port_sau_9t','port_dung_sau_12t','port_dung_sau_3t','port_dung_sau_6t'
    ,'port_dung_sau_9t']
    df_dt_perport = process_perport(kydautu)
    df_dt_perport = df_dt_perport.to_pandas()
    df_port_pivot = df_port_pivot.merge(df_dt_perport,on='ma_ke_hoach',how='left')
    df_port_pivot = df_port_pivot[(~df_port_pivot.check_kh.isna())&(~df_port_pivot.vung.isna())]
    df_port_pivot.drop('check_kh',axis=1,inplace=True)
    df_port_pivot['dung_luong_trien_khai'] = df_port_pivot['tong_port_sau_3t']
    df_port_pivot['ti_le_khai_thac_3t'] = np.where(df_port_pivot['tong_port_sau_12t']<=0,0,
                      df_port_pivot['port_dung_sau_3t']/df_port_pivot['tong_port_sau_12t'])
    df_port_pivot['ti_le_khai_thac_6t'] = np.where(df_port_pivot['tong_port_sau_6t']<=0,0,
                      df_port_pivot['port_dung_sau_6t']/df_port_pivot['tong_port_sau_6t'])
    df_port_pivot['ti_le_khai_thac_9t'] = np.where(df_port_pivot['tong_port_sau_9t']<=0,0,
                      df_port_pivot['port_dung_sau_9t']/df_port_pivot['tong_port_sau_9t'])
    df_port_pivot['ti_le_khai_thac_12t'] = np.where(df_port_pivot['tong_port_sau_12t']<=0,0,
                      df_port_pivot['port_dung_sau_12t']/df_port_pivot['tong_port_sau_12t'])
    df_port_pivot_filter = df_port_pivot[['ma_ke_hoach', 'ky_dau_tu', 'pop', 'phuong', 'quan', 'chi_nhanh',
           'vung', 'dung_luong_trien_khai', 'perport', 'tong_port_sau_3t',
           'port_dung_sau_3t', 'ti_le_khai_thac_3t', 'tong_port_sau_6t',
           'port_dung_sau_6t', 'ti_le_khai_thac_6t', 'tong_port_sau_9t',
           'port_dung_sau_9t', 'ti_le_khai_thac_9t', 'tong_port_sau_12t',
           'port_dung_sau_12t', 'ti_le_khai_thac_12t']]
    df_port_pivot_filter['ky_dau_tu'] =kydautu
    lst_data = df_port_pivot_filter.values.tolist()
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur_1 = conn.cursor()
    for i in range(len(lst_data)):
        tupl = (lst_data[i])
        cur_1.execute(
        " INSERT INTO tbl_planning_history(ma_ke_hoach, ky_dau_tu, pop, phuong, quan, chi_nhanh,"
        "vung, dung_luong_trien_khai, perport, tong_port_sau_3t,"
        "port_dung_sau_3t, ti_le_khai_thac_3t, tong_port_sau_6t,"
        "port_dung_sau_6t, ti_le_khai_thac_6t, tong_port_sau_9t,"
        "port_dung_sau_9t, ti_le_khai_thac_9t, tong_port_sau_12t,"
        "port_dung_sau_12t, ti_le_khai_thac_12t) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,"
        "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        " ON CONFLICT (ma_ke_hoach, ky_dau_tu, pop, phuong, quan, chi_nhanh,vung)"
        " DO UPDATE SET dung_luong_trien_khai = EXCLUDED.dung_luong_trien_khai, "
        " perport = EXCLUDED.perport, tong_port_sau_3t = EXCLUDED.tong_port_sau_3t,"
        "port_dung_sau_3t = EXCLUDED.port_dung_sau_3t,ti_le_khai_thac_3t = EXCLUDED.ti_le_khai_thac_3t, "
        "tong_port_sau_6t = EXCLUDED.tong_port_sau_6t, port_dung_sau_6t = EXCLUDED.port_dung_sau_6t,"
        "ti_le_khai_thac_6t = EXCLUDED.ti_le_khai_thac_6t,tong_port_sau_9t = EXCLUDED.tong_port_sau_9t, "
        "port_dung_sau_9t = EXCLUDED.port_dung_sau_9t,ti_le_khai_thac_9t = EXCLUDED.ti_le_khai_thac_9t,"
        "tong_port_sau_12t = EXCLUDED.tong_port_sau_12t,port_dung_sau_12t = EXCLUDED.port_dung_sau_12t,"
        "ti_le_khai_thac_12t = EXCLUDED.ti_le_khai_thac_12t;", (tuple(tupl))
        )
    try:
        conn.commit()
        conn.close()
        print("Successfully!!!!")
    except:
        print("Don't save DB")