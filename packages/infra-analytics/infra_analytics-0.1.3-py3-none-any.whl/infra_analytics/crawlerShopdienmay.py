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
# os.environ['NO_PROXY'] = "api.cellphones.com.vn"
# os.environ['NO_PROXY'] = "www.dienmayxanh.com"
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

def crawler_thegioididong(config: dict = infra_analytics_config):
    """
        + Load thông tin phường/xã toàn quốc từ /mnt/projects-data/phat_trien_ha_tang/file_static/vietnam_phuongxa.xls
        + Crawler thông tin shop thế giới di động theo tỉnh từ https://www.thegioididong.com/sieu-thi-the-gioi-di-dong
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
        + Chuẩn hoá thông tin các cột  tỉnh, quận/huyện, phường/xã, đường 
    """
    if not config: 
        config_file = "./config.yaml"
        config = get_config(config_file)
    xaphuong = pd.read_excel(config['crawler_data']['address_path'], sheet_name="Sheet1")
    xaphuong = xaphuong.rename(columns = {
        "Mã": "code",
        "Tên": "name",
        "Cấp": "level",
        "Quận Huyện": "district",
        "Tỉnh / Thành Phố": "province",
    })
    xaphuong.replace({'province' : { r'(Thành phố[ ])': '', r'Tỉnh[ ]': ''}}, regex=True,inplace=True)
    xaphuong['province'] = xaphuong['province'].apply(lambda x: unidecode.unidecode(str(x)))
    xaphuong['province'] = xaphuong['province'].str.lower()
    xaphuong.replace({'province' : {r'[ ]-[ ]':' ', r' ': '-'}}, regex=True,inplace=True)
    link = config['crawler_data']['link_thegioididong']
    df = []
    for row in xaphuong.province.unique():
        url = link + str(row)
        # print('--- url: {}'.format(url))
        hdr = {'User-Agent': 'Mozilla/5.0'}
        try:
            req = urllib.Request(url,headers=hdr)
            page = urllib.urlopen(req)
            soup = BeautifulSoup(page)
            new_feeds = soup.find('div', class_='storeaddress', on_click=False).findChildren("a", attrs={'class': not('href')}) 
            for feed in new_feeds:
                news = feed.getText(("!href")).replace("\n","").strip()
                # print('Text: {}'.format(news))
                df.append(news)
        except:
            break
    df_tgdd = pd.DataFrame({'list_address':df})
    df_tgdd['type'] = np.where(df_tgdd['list_address'].str.contains('Điện máy xanh'),
                          'Điện máy xanh','Thế giới di động')
    df_tgdd.replace({'list_address' : {r'Điện máy xanh[ ]':'', r'Thế giới di động[ ]': ''}}, regex=True,inplace=True)
    df_tgdd['list_address'] = df_tgdd['list_address'].apply(lambda x: re.sub("[(].*?[)]|[!][href]|[refref]|",'',x, flags=re.DOTALL))
    df_tgdd['province'] = df_tgdd['list_address'].str.split(',').str[-1]
    df_tgdd['district'] = df_tgdd['list_address'].str.split(',').str[-2]
    df_tgdd['ward'] = df_tgdd['list_address'].str.split(',').str[-3]
    df_tgdd['street'] = df_tgdd['list_address'].str.split(',').str[:-3]
    df_tgdd['street'] = [','.join(map(str, l)) for l in df_tgdd['street']]
    df_tgdd.drop('list_address',axis=1, inplace=True)
    
    df_tgdd['province']= df_tgdd['province'].apply(lambda x: str(x).strip())
    df_tgdd['district']= df_tgdd['district'].apply(lambda x: str(x).strip())
    df_tgdd['ward']= df_tgdd['ward'].apply(lambda x: str(x).strip())
    df_tgdd['street']= df_tgdd['street'].apply(lambda x: str(x).strip())
    df_tgdd['province'] = df_tgdd['province'].apply(lambda x :re.sub('\.$', '', x))
    df_tgdd.columns = ['store', 'province', 'district', 'ward', 'addr']
    return df_tgdd
def crawler_dienmaycholon(config: dict = infra_analytics_config):
    """
        + Crawler thông tin shop điện máy chợ lớn từ https://dienmaycholon.vn/he-thong-sieu-thi
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
    """
    assert config != None, "config must be not None"
        
    link = config['crawler_data']['link_dienmaycholon']
    df_dmcl = pd.DataFrame(columns=['addr','lat','long'])
    try:
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.Request(link,headers=hdr)
        page = urllib.urlopen(req)
        soup = BeautifulSoup(page)
        new_feeds = soup.find('div', class_='position_market_parent').findAll("div", 
                                            attrs={'class': 'container_cart'}) 
        for feed in new_feeds:
            news = feed.getText(("")).replace('(Xem bản đồ)','')
            link_ = str("https://dienmaycholon.vn")+feed.find("a").get("href")
            req_ = urllib.Request(link_,headers=hdr)
            page_ = urllib.urlopen(req_)
            soup_ = BeautifulSoup(page_)
            lat = soup_.find('div', id='map')['lat']
            long = soup_.find('div', id='map')['lng']
        #     print(news)
            df2 = pd.DataFrame({"addr":[news],
                            "lat":[float(lat)],
                            "long":[float(long)]})
            df_dmcl= df_dmcl.append(df2, ignore_index = True)
    except:
        print('lỗi điện máy chợ lớn')
    df_dmcl['store'] = 'Điện máy chợ lớn'
    df_dmcl['addr'] = df_dmcl['addr'].apply(lambda x: re.sub("[(].*?[)]",'',x, flags=re.DOTALL))
    df_dmcl['province'] = df_dmcl['addr'].str.split(',').str[-1]
    df_dmcl['district'] = df_dmcl['addr'].str.split(',').str[-2]
    df_dmcl['ward'] = df_dmcl['addr'].str.split(',').str[-3]
    df_dmcl['street'] = df_dmcl['addr'].str.split(',').str[:-3]
    df_dmcl['street'] = [','.join(map(str, l)) for l in df_dmcl['street']]
    return df_dmcl
def crawler_dienmayhc(config: dict = infra_analytics_config):
    """
        + Crawler thông tin shop điện máy HC từ https://hc.com.vn/ords/s--he-thong-sieu-thi-dien-may-hc
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
    """
    assert config != None, "config must be not None"
        
    link_hc = config['crawler_data']['link_dienmayhc']
    df_dmhc = pd.DataFrame(columns=['addr','lat','long'])
    try:
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.Request(link_hc, headers=hdr)
        page = urllib.urlopen(req)
        soup = BeautifulSoup(page)
        new_feeds = soup.find('div', class_='col-xs-12 welcome-about-us').findAll('p')
        for feed in new_feeds:
            news = feed.getText(("")).replace("Xem bản đồ","").replace("-","")
            news= list(news.split("\n"))
        #     print(news)
            for i in range(len(feed.find_all('a', href=True))):
                a= feed.find_all('a', href=True)[i]
                req_ = urllib.Request(a['href'],headers=hdr)
                page_ = urllib.urlopen(req_)
                soup_ = BeautifulSoup(page_)
                td = soup_.find('div', class_='col-xs-12 welcome-about-us')
                # print(news[i])
                if (td is not None):
                    td = td.find('a').get('href')
                    m = re.match(r".*@(?P<lat>\d+\.?\d+),(?P<long>\d+\.?\d+)", td)
                    df2 = pd.DataFrame({"addr":[news[i]]})
                    df_dmhc= df_dmhc.append(df2, ignore_index = True)
                else:
                    df2 = pd.DataFrame({"addr":[news[i]],
                        "lat":[None],
                        "long":[None]})
                    df_dmhc= df_dmhc.append(df2, ignore_index = True)
    except:
        print('lỗi điện máy hc')
    # df_dmcl.replace({'addr' : { r'(Khai trương)': '', r'Mới khai trương': ''}}, regex=True,inplace=True)
    df_dmhc['store'] = 'Điện máy hc'
    df_dmhc['addr'] = df_dmhc['addr'].str.split('Khai trương').str[0]
    df_dmhc['addr'] = df_dmhc['addr'].str.split('Mới khai trương').str[0]
    df_dmhc['addr'] = df_dmhc['addr'].str.split(':').str[1]
    df_dmhc['province'] = df_dmhc['addr'].str.split(',').str[-1]
    df_dmhc['district'] = df_dmhc['addr'].str.split(',').str[-2]
    df_dmhc['ward'] = df_dmhc['addr'].str.split(',').str[-3]
    df_dmhc['street'] = df_dmhc['addr'].str.split(',').str[:-3]
    df_dmhc['street'] = [','.join(map(str, l)) for l in df_dmhc['street']]
    return df_dmhc
def crawler_dienmaynguyenkim():
    """
        + Crawler thông tin shop điện máy Nguyễn Kim từ https://www.nguyenkim.com/index.php?dispatch=nk_mp_mall.apimall
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
    """
    cURL = r"""curl 'https://www.nguyenkim.com/index.php?dispatch=nk_mp_mall.apimall' \
          -H 'Accept: application/json, text/javascript, */*; q=0.01' \
          -H 'Accept-Language: vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5' \
          -H 'Connection: keep-alive' \
          -H 'Cookie: __uzma=c8ed7501-db2b-46ff-96b2-861f558fb77a; __uzmb=1701424464; __uzme=8643; _gid=GA1.2.105846784.1701424465; __ssds=2; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22RS1ALAW0DTWVTAA7h73Q%22%7D; _atm_objs=eyJzb3VyY2UiOiJjaXR5YWRzIiwibWVkaXVtIjoiY3BhIiwiY2FtcGFpZ24iOiIyTktaIiwiY29u%0D%0AdGVudCI6IiIsInRlcm0iOiIiLCJ0eXBlIjoiYXNzb2NpYXRlX3V0bSIsImNoZWNrc3VtIjoiKiIs%0D%0AInRpbWUiOjE3MDE0MjQ0NjUwMDV9; state_name=TP.HCM; state_code=001; unauthHomeLocation_code=001; storeLocation_name=TP.HCM; storeLocation_code=001; installmentLocation_name=TP.HCM; installmentLocation_code=001; __ssuzjsr2=a9be0cd8e; __uzmaj2=0974ffd7-398a-46f8-b717-7f6fd25d2d3d; __uzmbj2=1701424465; _ac_au_gt=1701424465226; login_form_event=sign_in; mp_skin=desktop; _fbp=fb.1.1701424465546.141731762; utm_source=cityads; utm_medium=cpa; utm_campaign=2NKZ; click_id=8nNZ20RSfjZt9V4; sid_customer_5120c=57dd406f9c53054e0013f495114b9ce4-C; nk_auth=unauth; _asm_uid=1297867988; _ac_client_id=1297876943.1701424472; au_id=1297876943; __zi=2000.SSZzejyD5ja-a_QhmHqUcJQLzgUEK0FNE8sq-vnQ7SLwdwBesmLRndZJw-_V15d7Sj6Wwj0F4iDtqQFdr0OVpG.1; nkcache_id=22b447c26392cdeead3b3a1f0d8a02f5; _asm_visitor_type=r; login_form_event_time=1701483785; _utm_objs=eyJzb3VyY2UiOiJyLnNydnRyY2suY29tIiwibWVkaXVtIjoicmVmZXJyZXIiLCJjYW1wYWlnbiI6%0D%0AIiIsImNvbnRlbnQiOiIiLCJ0ZXJtIjoiIiwidHlwZSI6InJlZmVycmVyIiwidGltZSI6MTcwMTQ4%0D%0ANDE1NTY5MiwiY2hlY2tzdW0iOiJjaTV6Y25aMGNtTnJMbU52YlMxeVpXWmxjbkpsY2kwdE1UY3dN%0D%0AVFE0TkRFMU5UWTVNZz09In0%3D; _gat_UA-17048930-1=1; cto_bundle=W1o-gl8lMkZQeDFpd0RDdWtvRVA2cDY3SiUyRlBJRFRaT0tZSHVScE14RGxKJTJGVkRMRkdXWGUyWEdFUk5JdFcwS1NaYjhhdVhsNmVpTGJMWWpxSW5CZlRjSVFzR3RGY3Z5M3Y5VXRrT0JoMWRiTk9yMlpuOHJkWWdkZlY3bDRQQlhWJTJCbEg2Nk9rZHNiR2lEQk5vcHFQQm1oZEJhOUFuRUNzQzdwVWx5JTJCdlVhN3prVjBnUFYlMkJzSHE2aElDJTJGSmczWDM4TiUyRm5HU0s2NGJaNGI3QjhaclJpN2sxZVpCb3ZXazlENmdqYlNCaGJxTVllUkQyT1A1TVpOME03ME5tNmsxdXoyUnA1MzFyVVlnY1FsZHNWUkFZQlRTRU8wVlV6ZjlQY0N6N1BGWG5veXVIZDdZaG9JcW9DVXVQZG12WGpJNXY0UkJSaldYbXdpMjRwcmpaU1dDQUVnJTJCZmpneEhQanJVdGVQcm1EJTJGZ1BHOXNvUWFrMXdoRSUzRA; _pk_ref.554926188.973b=%5B%22%22%2C%22%22%2C1701505007%2C%22https%3A%2F%2Fexcel.officeapps.live.com%2F%22%5D; _pk_id.554926188.973b=1297876943.1701424465.3.1701505007.1701505007.; _pk_ses.554926188.973b=*; __uzmcj2=729563435905; __uzmdj2=1701505007; _clck=1n3tsu%7C2%7Cfh7%7C0%7C1430; _cdp_cfg=%257B%2522refferal_exclusion%2522%3A%255B%2522secureacceptance.cybersource.com%2522%2C%2522nguyenkim.com%2522%255D%257D; _ac_an_session=zkzhznzqzizlzmzlzjzgzrzkzmzkzkzizdzjzdzizkzjzizmzjzmzjzjzkzdzizdzizkzjzizmzjzmzjzjzkzdzizkzjzizmzjzmzjzjzkzdzizdzhzqzdzizd2f27zdzgzdzlzmzmznzqzd; _clsk=1v2k3ka%7C1701505008331%7C1%7C1%7Co.clarity.ms%2Fcollect; _ga_8S8EFGF74J=GS1.2.1701505007.3.0.1701505009.58.0.0; _gat=1; _ga=GA1.1.576348471.1701424465; __uzmc=3718810948761; __uzmd=1701505042; _ga_34B604LFFQ=GS1.1.1701505006.3.1.1701505042.24.0.0' \
          -H 'Referer: https://www.nguyenkim.com/cac-trung-tam-mua-sam-nguyen-kim.html' \
          -H 'Sec-Fetch-Dest: empty' \
          -H 'Sec-Fetch-Mode: cors' \
          -H 'Sec-Fetch-Site: same-origin' \
          -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' \
          -H 'X-Requested-With: XMLHttpRequest' \
          -H 'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"' \
          -H 'sec-ch-ua-mobile: ?0' \
          -H 'sec-ch-ua-platform: "macOS"' \
          --compressed"""
    df_nk = pd.DataFrame(columns=['address'])
    try:
        lCmd = shlex.split(cURL) # Splits cURL into an array
        p = subprocess.Popen(lCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate() # Get the output and the err message
        json_data = json.loads(out.decode("utf-8"))
        lst_data_single = pd.DataFrame(json_data)
        df_nk = lst_data_single[['address']]
    except:
        print('không có dữ liệu')
    df_nk['store'] ='Nguyễn Kim'
    df_nk['province'] = df_nk['address'].str.split(',').str[-1]
    df_nk['district'] = df_nk['address'].str.split(',').str[-2]
    df_nk['ward'] = df_nk['address'].str.split(',').str[-3]
    df_nk['street'] = df_nk['address'].str.split(',').str[:-3]
    df_nk['street'] = [','.join(map(str, l)) for l in df_nk['street']]
    df_nk.columns = ['addr', 'store', 'province', 'district', 'ward', 'street']
        
    return df_nk
def crawler_cellphone():
    """
        + Crawler thông tin shop điện máy cellphone từ https://api.cellphones.com.vn/graphql-dashboard/graphql/query
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
    """
    cURL = r"""curl 'https://api.cellphones.com.vn/graphql-dashboard/graphql/query' \
      -H 'authority: api.cellphones.com.vn' \
      -H 'accept: application/json' \
      -H 'accept-language: vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5' \
      -H 'content-type: application/json' \
      -H 'origin: https://cellphones.com.vn' \
      -H 'referer: https://cellphones.com.vn/' \
      -H 'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"' \
      -H 'sec-ch-ua-mobile: ?0' \
      -H 'sec-ch-ua-platform: "macOS"' \
      -H 'sec-fetch-dest: empty' \
      -H 'sec-fetch-mode: cors' \
      -H 'sec-fetch-site: same-site' \
      -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' \
      --data '{"query":"query getAllStores{\n                          GetDataMap4d(lat : 10.7914333,long : 106.687859){\n                              shop {\n                                id\n                                code\n                                external_id\n                                address\n                                phone\n                                google_link\n                                zalo_link\n                                district_id\n                                province_id\n                                latitude\n                                longitude\n                                time_opening\n                                shop_description\n                                google_map_address\n                                company_id\n                                near\n                                created_at\n                                deleted_at\n                                updated_at\n                                store_opening_images\n                                store_opening_url\n                              }\n                              location {\n                                status\n                                distance {\n                                    text\n                                    value\n                                }\n                                duration {\n                                    text\n                                    value\n                                }\n                              }\n                              cps\n                              asp\n                              dtv\n                              slug\n                          }\n                        }","variables":{}}' \
      --compressed"""
    
    lCmd = shlex.split(cURL) # Splits cURL into an array
    
    p = subprocess.Popen(lCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate() # Get the output and the err message
    json_data = json.loads(out.decode("utf-8"))
    lst_data_single = pd.DataFrame(json_data['data']['GetDataMap4d'])
    json_struct = json.loads(lst_data_single.to_json(orient="records"))    
    
    df_cp_full = pd.io.json.json_normalize(json_struct)
    df_cp = df_cp_full[['shop.address','slug']]
    df_cp.columns=['address','province']
    df_cp['store'] ='CellphoneS'
    df_cp.replace({'province':{r'-':' '}}, regex=True,inplace=True)
    df_cp['province'] = df_cp['province'].str.title()
    df_cp['district'] = df_cp['address'].str.split(',').str[-1]
    df_cp['ward'] = df_cp['address'].str.split(',').str[-2]
    df_cp['street'] = df_cp['address'].str.split(',').str[:-2]
    df_cp['street'] = [','.join(map(str, l)) for l in df_cp['street']]
    df_cp.columns = ['addr', 'province', 'store', 'district', 'ward', 'street']
    return df_cp
def crawler_dienmayxanh():
    """
        + Crawler thông tin shop điện máy cellphone từ https://www.dienmayxanh.com/Store/SearchStoreByValue
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
    """
    df_dmx = pd.DataFrame(columns=['addr']) 
    try:
        for i in range(321):
            cURL = r"""curl 'https://www.dienmayxanh.com/Store/SearchStoreByValue' \
                  -H 'Accept: */*' \
                  -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
                  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' \
                  -H 'X-Requested-With: XMLHttpRequest' \
                  --data 'pageIndex={}'""".format(i)
                
            lCmd = shlex.split(cURL) # Splits cURL into an array
            p = subprocess.Popen(lCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate() # Get the output and the err message
            # json_data = json.loads(out.decode("utf-8"), strict=False)
            try:
                json_data = json.loads(out.decode("utf-8"), strict=False)
            except json.JSONDecodeError as e:
                if "Expecting value" in str(e):
                    # Handle empty content
                    json_data = None
                else:
                    # Handle other JSONDecodeError
                    raise
            decoded_string = html.unescape(json_data['html'])
            soup = BeautifulSoup(decoded_string, 'html.parser')
            new_feeds = soup.findAll('span')
            for feed in new_feeds:
                news = feed.getText((""))
                df2 = pd.DataFrame({"addr":[news]})
                df_dmx= df_dmx.append(df2, ignore_index = True)
    except:
        print('lỗi điện máy')
    df_dmx.replace({'addr':{'\n|Điện máy Xanh|Thế giới di động|, Việt Nam|- Xem bản đồ':''}},regex=True,inplace=True)
    df_dmx['addr'] = df_dmx['addr'].apply(lambda x: re.sub("[(].*?[)]|[!][href]|[refref]|[)]|[|]",'',x,
                                                                               flags=re.DOTALL))
    df_dmx['province'] = df_dmx['addr'].str.split(',').str[-1]
    df_dmx['district'] = df_dmx['addr'].str.split(',').str[-2]
    df_dmx['ward'] = df_dmx['addr'].str.split(',').str[-3]
    df_dmx['street'] = df_dmx['addr'].str.split(',').str[:-3]
    df_dmx['street'] = [','.join(map(str, l)) for l in df_dmx['street']]
    df_dmx_fil = df_dmx[['addr','province', 'district', 'ward', 'street']]
    df_dmx_fil['province']= df_dmx_fil['province'].apply(lambda x: str(x).strip())
    df_dmx_fil['district']= df_dmx_fil['district'].apply(lambda x: str(x).strip())
    df_dmx_fil['ward']= df_dmx_fil['ward'].apply(lambda x: str(x).strip())
    df_dmx_fil['street']= df_dmx_fil['street'].apply(lambda x: str(x).strip())
    df_dmx_fil['province'] = df_dmx_fil['province'].apply(lambda x :re.sub('\.$', '', x))
    df_dmx_fil['province'] = df_dmx_fil['province'].apply(lambda x :re.sub('\s\s+', ' ', x))
    df_dmx_fil['store'] ='Điện máy xanh'
    return df_dmx_fil
def crawler_fshop():
    """
        + Crawler thông tin shop điện máy cellphone từ https://fptshop.com.vn/cua-hang/Home/GetListShop?page={}
        + Tách thông tin tỉnh, quận/huyện, phường/xã, đường từ thông tin address crawler được 
    """
    df_fshop = pd.DataFrame(columns=['addr'])
    try:
        for i in range(1,40):
            cURL = r"""curl 'https://fptshop.com.vn/cua-hang/Home/GetListShop?page={}' \
              -H 'Accept: */*' \
              -H 'Accept-Language: vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5' \
              -H 'Connection: keep-alive' \
              -H 'Cookie: log_6dd5cf4a-73f7-4a79-b6d6-b686d28583fc=defb10eb-2054-43d1-9767-c8ed78ba803b; __zi=2000.SSZzejyD7iu_cVEzsr0LpYAPvhoKKa7GR9V-_iX0Iyv-rUpesmSKY7tNeA7S0nMAVDsYwjaC7i5usABfr0WNp3O.1; cf_clearance=EjDwVUTyNaWTqtTdiz3QZb6dOYVJBrqWBOUQRNjaUeY-1701506110-0-1-9288697f.9912e224.c589369f-0.2.1701506110; _gid=GA1.3.1578401529.1701506111; _gat=1; _ga=GA1.1.1244735801.1701413780; _gcl_au=1.1.1178009718.1701515146; ajs_group_id=null; fpt_uuid=%221fa9f1ac-d03d-4fae-8610-daf69ea27add%22; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22CPuCgjmaMeNWKnRndpnx%22%7D; _fbp=fb.2.1701515146558.1614252460; __admUTMtime=1701515146; _tt_enable_cookie=1; _ttp=shMRdTnH6HtY_0plx4pRPytFZlG; dtdz=83a9a83f-2cf0-4b77-a74e-5f68bd07d459; __iid=; __iid=; __su=0; __su=0; _hjSessionUser_731679=eyJpZCI6IjhkYTAwY2E5LTNiY2MtNTI0Yy05YjNmLWM4NjNiN2UxNThkZSIsImNyZWF0ZWQiOjE3MDE1MTUxNDg1MTgsImV4aXN0aW5nIjpmYWxzZX0=; _hjFirstSeen=1; _hjIncludedInSessionSample_731679=0; _hjSession_731679=eyJpZCI6ImQwMGJjNjAzLWI1ZDgtNGRlMC04OTBlLTlhNTNjMjY2ODE4NSIsImNyZWF0ZWQiOjE3MDE1MTUxNDg1MjAsImluU2FtcGxlIjpmYWxzZSwic2Vzc2lvbml6ZXJCZXRhRW5hYmxlZCI6dHJ1ZX0=; _hjAbsoluteSessionInProgress=1; __RC=5; __R=3; __uif=__uid%3A1897444670985365354%7C__ui%3A2%252C5%7C__create%3A1697444670; ins-click_tra_gop=true; _ga_34B604LFFQ=GS1.1.1701515145.3.1.1701515150.55.0.0; _ga_ZR815NQ85K=GS1.1.1701515145.3.1.1701515151.54.0.0' \
              -H 'Referer: https://fptshop.com.vn/cua-hang' \
              -H 'Sec-Fetch-Dest: empty' \
              -H 'Sec-Fetch-Mode: cors' \
              -H 'Sec-Fetch-Site: same-origin' \
              -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36' \
              -H 'X-Requested-With: XMLHttpRequest' \
              -H 'sec-ch-ua: "Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"' \
              -H 'sec-ch-ua-mobile: ?0' \
              -H 'sec-ch-ua-platform: "macOS"' \
              --compressed""".format(i)
            lCmd = shlex.split(cURL) # Splits cURL into an array
            
            p = subprocess.Popen(lCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate() # Get the output and the err message
            json_data = json.loads(out.decode("utf-8"))
            soup = BeautifulSoup(json_data['view'], 'html.parser')
            if soup.findAll('h2', class_='label-text f-w-400')!=[]:
                new_feeds = soup.findAll('h2', class_='label-text f-w-400')
                
            elif (soup.findAll('span', class_='label-text f-w-400')!=[]):
                new_feeds = soup.findAll('span', class_='label-text f-w-400')
            else:
                new_feeds = soup.findAll('div', class_='label-text f-w-400')
            for feed in new_feeds:
                news = feed.getText((""))
                df2 = pd.DataFrame({"addr":[news]})
                df_fshop= df_fshop.append(df2, ignore_index = True)
    except:
        print('lỗi')
    df_fshop['store'] ='Fshop'
    df_fshop['province'] = df_fshop['addr'].str.split(',').str[-1]
    df_fshop['district'] = df_fshop['addr'].str.split(',').str[-2]
    df_fshop['ward'] = df_fshop['addr'].str.split(',').str[-3]
    df_fshop['street'] = df_fshop['addr'].str.split(',').str[:-3]
    return df_fshop
def infra_crawlershopdienmay(config: dict = infra_analytics_config):
    """
        + Call các function crawler shop điện máy trên và concat thành dataframe 
        + Drop các row duplicate 
        + Upsert thông tin shop điện máy vào postgresql 177 - dwh_noc - public.tbl_shop_info
    """
    assert config != None, "config must be not None"
    
    df_nk=crawler_dienmaynguyenkim()
    df_fshop = crawler_fshop()
    df_hc=crawler_dienmayhc()
    df_cl=crawler_dienmaycholon()
    df_tgdd=crawler_thegioididong()
    df_dmx=crawler_dienmayxanh()
    df_cp=crawler_cellphone()
    
    df_fshop =  df_fshop[['addr','store','province','district','ward']]
    df_dmx = df_dmx[['addr','store','province','district','ward']]
    df_cp = df_cp[['addr','store','province','district','ward']]
    df_nk = df_nk[['addr','store','province','district','ward']]
    df_hc = df_hc[['addr','store','province','district','ward']]
    df_cl = df_cl[['addr','store','province','district','ward']]
    df_tgdd = df_tgdd[['addr','store','province','district','ward']]
    df_full = pd.concat([df_fshop,df_dmx,df_cp,df_nk,df_hc,df_cl,df_tgdd])
    df_full['addr'] = np.where(df_full['store']=='Thế giới di động', df_full['addr']+','+df_full['ward']+','
                               +df_full['district']+','+df_full['province'],df_full['addr'])
    df_full.drop_duplicates(keep='first',inplace=True)
    lst_data = df_full.values.tolist()
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur_1 = conn.cursor()
    for i in range(len(lst_data)):
        tupl = (lst_data[i])
        cur_1.execute(
        " INSERT INTO tbl_shop_info(addr,store,province,district, ward) VALUES( %s, %s, %s, %s, %s)"
        " ON CONFLICT (addr)"
        " DO UPDATE SET store = EXCLUDED.store, "
        " province = EXCLUDED.province, district = EXCLUDED.district, ward = EXCLUDED.ward;", (tuple(tupl))
        )
    try:
        conn.commit()
        conn.close()
        print("Successfully!!!!")
    except:
        print("Don't save DB")