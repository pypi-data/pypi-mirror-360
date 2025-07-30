import shlex
import json
import subprocess
import json
import html
import psycopg2 as pg
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
from multiprocessing import Process, Queue, Array, current_process
from underthesea import text_normalize
from bs4 import BeautifulSoup
import requests
import unidecode
import os
import numpy as np
import pandas as pd
import re
import urllib.request as urllib
import warnings
warnings.filterwarnings('ignore')
os.environ['http_proxy'] = "http://proxy.hcm.fpt.vn:80"
os.environ['https_proxy'] = "http://proxy.hcm.fpt.vn:80"
import yaml
from .config import infra_analytics_config

def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config
    
def infra_crawlershopftel(config: dict = infra_analytics_config):
    """
    Crawler thông tin văn phòng giao dịch của Ftel:
        + crawler thông tin văn phòng giao dịch Ftel từ: https://ftel.vn/getStoreBrach
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
        + Drop dữ liệu duplicate 
        + Upsert thông tin văn phòng giao dịch Ftel vào postgresql 177 - dwh_noc - public.tbl_shopfpttelecom_info
    """
    assert config != None, "config must be not None"
        
    cURL = r"""curl 'https://ftel.vn/getStoreBrach' \
    -H 'authority: ftel.vn' \
    -H 'accept: */*' \
    -H 'accept-language: vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5' \
    -H 'cookie: _gcl_au=1.1.1026824109.1701587762; _gid=GA1.2.802365421.1701587762; _gat_gtag_UA_245503180_1=1; _gat=1; _ga=GA1.1.1105386993.1701587762; XSRF-TOKEN=eyJpdiI6IkkvRTlWeGJDdU9PR3M5QnkwUlNBN1E9PSIsInZhbHVlIjoiS3hPSDlSaGt0V2lIYTk4TXFua0NqR0FKeUQzL0lEUWw2djVsNzc4T1hSNDI5OW1yR0c3WVdJRFM0WXdVbEV3Zy94YUJ5aFVwRDNkeVJFbEF1ZWt2UmZmcm1hTDRNUVlvcFhtTU1NMzFsZGl4SVRGMlR4ZWgveWlUQXZnZ212SjIiLCJtYWMiOiI3NWUyMzI5N2E3NGY5MzQzZTQyNTk3OTNmMjFjYjljZTJkZGU4NTBkMDFlZjg1NzU0ZWUwZjdkOTNiMGJmODBjIn0%3D; fleetcart_session=eyJpdiI6Imh2Q1d6anoyZnJHUFpLYjlkTXhjZHc9PSIsInZhbHVlIjoibEo4c0dxZW1EM2lHNEowd0JiWGJoOVFnRkhOWk1GWHRNMkdtckh5Tm10Z1VKd1Mxc0pqVUd2WTlyeDJpVjV1aTdMRVFUM2VaZDU2Z0JZRURRMnROcXpqMHlKZCs4T28yd0h0cUhyNmFXYkFvTXR6NVB6WEhEeGxXREkyaUlQUkUiLCJtYWMiOiI1Yjk1ZTdjZGRlYWRjZjIyYTMzOGVmYWQ1ZjliNDJkNWYxYWQ5ZmM1MDM5NDg5ZTFhMTU2Y2Q5ZDk4MmFlYzcyIn0%3D; _ga_H27VLGD6XJ=GS1.1.1701587761.1.1.1701587809.0.0.0; _ga_34B604LFFQ=GS1.1.1701587764.1.1.1701587809.15.0.0' \
    -H 'referer: https://ftel.vn/ho-tro/lien-he-24-7/diem-giao-dich' \
    -H 'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "macOS"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' \
    -H 'x-requested-with: XMLHttpRequest' \
    --compressed"""
    lCmd = shlex.split(cURL) # Splits cURL into an array
    p = subprocess.Popen(lCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate() # Get the output and the err message
    json_data = json.loads(out.decode("utf-8"))
    lst_data_single = pd.DataFrame(json_data)
    df_vpgd = lst_data_single[['address']]
    df_vpgd['province'] = df_vpgd['address'].str.split(',').str[-1]
    df_vpgd['district'] = df_vpgd['address'].str.split(',').str[-2]
    df_vpgd['ward'] = df_vpgd['address'].str.split(',').str[-3]
    df_vpgd['street'] = df_vpgd['address'].str.split(',').str[:-3]
    df_vpgd['street'] = [','.join(map(str, l)) for l in df_vpgd['street']]
    df_vpgd = df_vpgd[['address','province','district','ward']]
    df_vpgd.drop_duplicates(keep='first',inplace=True)
    lst_data = df_vpgd.values.tolist()
    conn =  pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur_1 = conn.cursor()
    for i in range(len(lst_data)):
        tupl = (lst_data[i])
        cur_1.execute(
        " INSERT INTO tbl_shopfpttelecom_info(address,province,district, ward) VALUES( %s, %s, %s, %s)"
        " ON CONFLICT (address)"
        " DO UPDATE SET province = EXCLUDED.province, district = EXCLUDED.district, ward = EXCLUDED.ward;", (tuple(tupl))
        )
    try:
        conn.commit()
        conn.close()
        print("Successfully!!!!")
    except:
        print("Don't save DB")