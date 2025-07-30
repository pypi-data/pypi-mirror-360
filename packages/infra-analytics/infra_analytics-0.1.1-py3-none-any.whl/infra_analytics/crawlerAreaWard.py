import queue
import traceback
import pandas as pd
import requests as rq
import psycopg2 as pg
from sqlalchemy import create_engine
from psycopg2.extras import execute_values
from multiprocessing import Process, Queue, Array, current_process,Pool
from bs4 import BeautifulSoup
from underthesea import text_normalize
import yaml
from .config import infra_analytics_config

def get_config(config_file):
    with open(config_file, "r") as cf:
        config = yaml.load(cf, Loader=yaml.SafeLoader)
    return config

def getxpinfo(conv_queue, result_queue, config: dict = infra_analytics_config):  
    """
        Crawler dữ liệu diện tích của xã/phường từ trang wikipedia:
           + Tiền xử lý địa chỉ input cần crawler trên wiki 
           + Crawler thông tin xã/phường từ:https://vi.wikipedia.org/wiki/%s
           + Trích lấy thông tin về population, area, dist
    """
    if not config: 
        config_file = "./config.yaml"
        config = get_config(config_file)
        
    while True:
        try:
            xp = conv_queue.get_nowait()
            current_size = conv_queue.qsize()
            if conv_queue.qsize() % 100 == 0:
                print(current_size)
        except queue.Empty:
            break
        else:
            try:
                name, level, district, province = xp[1], xp[2], xp[3], xp[5]
                search_pattern = None
                xp_info = xp + [None, None, None, None]
                xa, huyen = None, None
                if isinstance(name, float):
                    search_pattern = district.split("Huyện", 1)[1].strip().replace(" ", "_")
                elif "Thị Trấn" in name:
                    xa = name.split("Thị Trấn", 1)[1].strip().replace(" ", "_")
                    search_pattern = xa
                else:
                    if level == "Xã":
                        xa = name.split("Xã", 1)[1].strip().replace(" ", "_")
                    if level == "Phường":
                        if any(char.isdigit() for char in name):
                            xa = name.strip().replace(" ", "_")
                        else:
                            xa = name.split("Phường", 1)[1].strip().replace(" ", "_")
                    if level == "Thị trấn":
                        xa = name.split("Thị trấn", 1)[1].strip().replace(" ", "_")
                    if level == "Huyện":
                        xa = name.split("Huyện", 1)[1].strip().replace(" ", "_")
                    if "Huyện" in district:
                        huyen = district.split("Huyện", 1)[1].replace(" ", "_")
                    if "Quận" in district:
                        huyen = district.split("Quận", 1)[1].replace(" ", "_")
                    if "Thành phố" in district:
                        huyen = district.split("Thành phố", 1)[1].replace(" ", "_")
                    if "Thị xã" in district:
                        huyen = "_thị_xã" + district.split("Thị xã", 1)[1].replace(" ", "_")
                    search_pattern = xa + "," + huyen if xa and huyen else None
                retry = 0
                while retry >= 0:
                    url = config['crawler_data']['link_wiki']+ "%s" % search_pattern
                    resp = rq.request(method="GET", url=url)
                    # print("\n" + url + ": " + str(resp.status_code) + "\n")
                    if resp.status_code != 200:
                        # print('----------'+str(retry)+'--------')
                        if retry == 0:
                            search_pattern = "%s_(phường)" % xa
                        if retry == 1:
                            if "Huyện" in district:
                                huyen = "_huyện" + district.split("Huyện", 1)[1].replace(" ", "_")
                            if "Quận" in district:
                                huyen = "_quận" + district.split("Quận", 1)[1].replace(" ", "_")
                            if "Thành phố" in district:
                                huyen = "_thành_phố" + district.split("Thành phố")[1].replace(" ", "_")
                            search_pattern = xa + "," + huyen if xa and huyen else None
                            
                        if retry == 2:
                            if "Thị Trấn" in name:
                                search_pattern = "%s_(thị_trấn)" % xa
                            if "Xã" in name:
                                search_pattern = "%s_(xã)" % xa
                        if retry == 3:
                            if "Thị Trấn" in name:
                                search_pattern = "%s_(thị_trấn)" % xa +"%s" % huyen.replace('_huyện_','')
                            if "Xã" in name:
                                search_pattern = "%s_(xã),_" % xa +"%s" % huyen.replace('_huyện_','')
                        if retry == 4:
                           search_pattern = "%s" % xa +",_%s" % huyen.replace('_huyện_','')+ "_(%s)" % province.replace(" ", "_")
                        if retry == 5:
                           search_pattern = "%s_(thị_trấn)" % xa
                        if retry == 6:
                           search_pattern = "%s,_" % xa +"%s" % huyen.replace('_thị_xã_','')
                        if retry == 7:
                            search_pattern = xa
                        if retry == 8:
                            retry = -7
                        retry += 1
                    else:
                        try:
                            retry = -1
                            content = resp.content.decode()
                            population_pattern = re.compile(r"(?P<population>\d+[.,]?\d+|\d+) người")
                            g1 = population_pattern.search(content)
                            population = int(g1.group("population").replace(".", ""))
                            ###
                            area_pattern = re.compile(r"(?P<area>\d+[.,]?\d+|\d+) km²")
                            g2 = area_pattern.search(content)
                            area = float(g2.group("area").replace(",", "."))
                            ###
                            dist_pattern = re.compile(r"(?P<dist>\d+[.,]?\d+|\d+) người/km²")
                            g3 = dist_pattern.search(resp.content.decode())
                            dist = float(g3.group("dist").replace(",", "."))
                            xp_info = xp + [population, area, dist, url]
                        except:
                            print(traceback.format_exc())
                        finally:
                            result_queue.put(xp_info)
                    # print(url)
                            
            except:
                print(traceback.format_exc())
# def write_to_pg(conn, table, columns, data):
#     cur = conn.cursor()
#     insert_sql = """
#         INSERT INTO sch_fb.{0} ({1})
#         VALUES %s""".format(table, ', '.join(str(c) for c in columns))
#     execute_values(cur, insert_sql, data)
# def insert_db(df):
#     engine = create_engine('postgresql://dwh_noc:fNSdAnGVEA23NjTTPvRv@172.27.11.177:6543/dwh_noc')
#     df.to_sql('tbl_vnwards_info', engine, if_exists='append', index=False)
#     engine.dispose()
#     print("insert new data to public.tbl_vnwards_info success")
def infra_crawlerareaward(config: dict = infra_analytics_config):
    """
    Xử lý và tổ chức lưu trữ dữ liệu diện tích xã/phường:
        + Load full thông tin địa chỉ xã/phường toàn quốc: /mnt/projects-data/phat_trien_ha_tang/file_static/vietnam_phuongxa.xls
        + Transform thông tin địa chỉ: địa chỉ bất thường, missing, convert datatype 
        + Call function getxpinfo => crawler thông tin của xã/phường đó 
        + Upsert thông tin địa phương vào postgresql 177 - dwh_noc - public.tbl_vnwards_info
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
    xaphuong = xaphuong[["code", "name", "level", "district", "province"]]
    xaphuong['code'] = xaphuong['code'].astype(pd.Int64Dtype())
    xaphuong['province_short'] = xaphuong['province'].replace({r"Thành phố[ ]":"",r"Tỉnh[ ]":""}, regex=True)
    xaphuong['province_short'].unique()
    miss = xaphuong[~xaphuong.name.isna()]
    miss['name_1'] = miss['name'].astype(str) +' '
    miss['name']=miss.apply(lambda x: str(x['name']).replace('oà', 'òa') if ('oà ' in str(x['name_1'])) else x['name'], axis=1)
    miss.replace({'name':{'uỵ':'ụy'}},regex=True, inplace=True)
    miss['name'] = miss['name'].str.title()
    miss.replace({'name':{'Xã Sủng Tráng':'Xã Sủng Cháng',
                         'Nông Trường':'Nông trường',
                         'Xã Phong Nậm':'Xã Phong Nặm',
                         'Xã Tả Ngải Chồ':'Xã Tả Ngài Chồ',
                         'Xã Nàn Xín':'Xã Nàn Sín',
                         'N.T':'Nông trường',
                          'Nt':'Nông trường',
                         'Phường V':'Phường 5',
                         'Phường Vii':'Phường 7'}},regex=True,inplace=True)
    miss['name'] = miss['name'].apply(lambda x: text_normalize(str(x)))
    miss['district'] = miss['district'].apply(lambda x: text_normalize(str(x)))
    miss['province_short'] = miss['province_short'].apply(lambda x: text_normalize(str(x)))
    nb_processes = 8
    processes = []
    conv_queue = Queue()
    result_queue = Queue()
    data_v2 = []
    
    j=0
    for i in range(1,55):
        k=j
        j = 200*i
        for xp in miss[k:j].values.tolist():
            conv_queue.put(xp)
        # Creating processes
        for w in range(nb_processes):
            p = Process(target = getxpinfo , args=(conv_queue, result_queue))
            processes.append(p)
            p.start()
        # completing process
        df_area = []
        for p in processes:
            p.join()
        
        while True:
            try:
                data_v2.append(result_queue.get_nowait())
            except queue.Empty:
                break
    df_phuong = pd.DataFrame.from_records(data_v2, columns= ['code', 'name', 'level', 'district', 'full_province',
                                                             'province', 'name_1', 'population', 'area', 'density', 'wiki_url'])
    df_phuong.drop(['name_1','full_province'], axis=1, inplace=True)
    lst_data = df_phuong[~df_phuong.area.isna()].values.tolist()
    conn = pg.connect("postgresql://%s:%s@%s:%s/%s"% (config['dbs']['dwh_177_public']['user']
                                                      ,config['dbs']['dwh_177_public']['password']
                                                     ,config['dbs']['dwh_177_public']['host']
                                                    ,config['dbs']['dwh_177_public']['port']
                                                    ,config['dbs']['dwh_177_public']['dbname']))
    cur_1 = conn.cursor()
    for i in range(len(lst_data)):
        tupl = (lst_data[i])
        cur_1.execute(
        " INSERT INTO tbl_vnwards_info(code,name,level,district, province, population, area, density, wiki_url) VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        " ON CONFLICT (code)"
        " DO UPDATE SET name = EXCLUDED.name, "
        " level = EXCLUDED.level, district = EXCLUDED.district, province = EXCLUDED.province, "
        "population = EXCLUDED.population, area = EXCLUDED.area, density = EXCLUDED.density, "
        "wiki_url = EXCLUDED.wiki_url;", (tuple(tupl))
        )
    try:
        conn.commit()
        conn.close()
        print("Successfully!!!!")
    except:
        print("Don't save DB")