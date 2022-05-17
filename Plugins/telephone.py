from Plugins.base import Base
from bs4 import BeautifulSoup
import multiprocessing
import requests, re

class telephone(Base):

    locations = {} 

    def __init__(self,config):
        self.config = config
        self.load()

    def prepare(self):
        for run in range(4):
            try: 
                response = requests.get(url="https://raw.githubusercontent.com/Ne00n/Looking-Glass-2/master/lg.json",timeout=5)
                if response.status_code != 200: continue
                self.locations = response.json()
                break
            except:
                if run == 3: return False
                continue
        return True

    def run(self,data):
        headers = {
        'Origin':data[1][0],
        'Referer':data[1][0],
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded'}

        for run in range(4):
            try: 
                response = requests.post(url=f"{data[1][0]}/ajax.php?cmd=ping&host={self.target}", headers=headers,timeout=15)
                if response.status_code != 200: continue
                break
            except Exception as e:
                if run == 3: return {}
        if response.status_code != 200: return {}
        avg = re.findall('avg\/.*?=.*?\/([0-9.]+)',response.text , re.MULTILINE | re.DOTALL)
        if not avg: return {}
        return {'avg':avg[0],'provider':data[0]}

    def engage(self,origin,target):
        print("Running telephone")

        self.start()
        origin = self.getCountry(origin)
        if not origin in self.locations['telephone']:
            print("Warning telephone, No Probes found in Target Country")
            return {}
        
        self.target = target
        probes = self.locations['telephone'][origin]
        pool = multiprocessing.Pool(processes = 3)
        results = pool.map(self.run, probes.items())
        pool.close()
        pool.join()

        output = {}
        for details in results:
            if not details: continue
            output[f"telephone{origin}{details['provider']}"] = {"provider":details['provider'],"avg":details['avg'],"city":origin,"source":self.__class__.__name__}
            
        total = self.diff()
        print(f"Done telephone done in {total}s")
        return output

