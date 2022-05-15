from Plugins.base import Base
from bs4 import BeautifulSoup
import multiprocessing
import requests, re

class vultr(Base):

    headers = {
        'Origin':'https://vultr.com',
        'Referer':f'https://vultr.com',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded'}
    localMapping = {"UK":"GB"}
    locations = {} 

    def __init__(self,config):
        self.config = config
        self.load()

    def prepare(self):
        for run in range(4):
            try: 
                response = requests.post(url="https://nj-us-ping.vultr.com/", headers=self.headers,timeout=15)
                if response.status_code != 200: continue
                break
            except:
                if run == 3: return False
                continue
        soup = BeautifulSoup(response.text,"html.parser")
        for option in soup.findAll('option'):
            if not option.has_attr("data-url"): continue
            if not option['data-country'].upper() in self.locations: self.locations[option['data-country'].upper()] = []
            city = re.findall('">(.*?)<',str(option) , re.MULTILINE | re.DOTALL)
            self.locations[option['data-country'].upper()].append({"url":option['data-url'],"city":city[0]})
        return True

    def run(self,point):
        try: 
            response = requests.post(url=f"{point['url']}ajax.php?cmd=ping&host={self.target}", headers=self.headers,timeout=15)
        except Exception as e:
            return {}

        if response.status_code != 200: return {}
        avg = re.findall('avg\/.*?=.*?\/([0-9.]+)',response.text , re.MULTILINE | re.DOTALL)
        if not avg: return {}
        point['avg'] = avg[0]
        return point

    def engage(self,origin,target):
        print("Running Vultr")

        self.start()
        if origin in self.localMapping: origin = self.localMapping[origin]
        if not origin in self.locations:
            print("Warning Vultr, No Probes found in Target Country")
            return {}
        
        self.target = target
        probes = self.locations[origin]
        pool = multiprocessing.Pool(processes = 2)
        results = pool.map(self.run, probes)
        pool.close()
        pool.join()

        output = {}
        for details in results:
            if not "avg" in details: continue
            output[f"Vultr{details['city']}"] = {"provider":'Vultr',"avg":details['avg'],"city":details['city'],"source":self.__class__.__name__}
            
        total = self.diff()
        print(f"Done Vultr done in {total}s")
        return output

