from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import multiprocessing
import requests, asyncio, re

class lookingHouse(Base):
    
    localMapping = {"UK":"GB"}
    secondaryMapping = {"United States":"USA"}
    mapping = {}

    def __init__(self,config):
        self.config = config
        self.load()

    def prepare(self):
        html = self.browseWrapper(f"https://looking.house/index.php",3)
        soup = BeautifulSoup(html,"html.parser")
        for a in soup.findAll('a'):
            if a['href'].startswith("/points.php?country"):
                location = re.findall('points.php\?country=([0-9]+).*?text-align:center.*?>(.*?)<',str(a) , re.MULTILINE | re.DOTALL)
                self.mapping[location[0][1]] = location[0][0]
        return True

    def isComparable(self):
        return True

    def run(self,point):
        headers = {
        'Origin':'https://looking.house',
        'Referer':f'https://looking.house/point.php?id={point[0]}&d={self.target}&f=ping',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Content-Type':'application/x-www-form-urlencoded'}
        dataRaw = f'id={point[0]}&domain={self.target}'
        try: 
            response = requests.post(url="https://looking.house/action.php?mode=looking_glass&action=ping", data=dataRaw, headers=headers,timeout=15)
        except:
            return {}

        if response.status_code != 200: return {}
        data = response.json()
        if data['Error'] != 0: return {}

        soup = BeautifulSoup(data['Template'],"html.parser")
        pre = soup.findAll('pre')
        avg = re.findall('avg\/.*?=.*?\/([0-9.]+)',str(pre[0]) , re.MULTILINE | re.DOTALL)
        if not avg: return {}
        point[1]['avg'] = avg[0]
        return point[1]

    def engage(self,origin,target):
        print("Running lookingHouse")

        self.start()
        if origin in self.localMapping: origin = self.localMapping[origin]
        country = self.getCountry(origin)
        #Why is it called fucking USA
        if country in self.secondaryMapping: country = self.secondaryMapping[country]
        if not country in self.mapping:
            print("Warning lookingHouse, No Probes found in Target Country")
            return {}
        
        countryID = self.mapping[country]
        html = self.browseWrapper(f"https://looking.house/points.php?country={countryID}",3)
        soup = BeautifulSoup(html,"html.parser")
        
        points = {}
        containers = soup.findAll("div",{"class":"container"})
        for tr in containers[3].findAll("tr"):
            if "Speed test / Network test" in str(tr): continue
            for index, td in enumerate(tr.findAll("td")):
                if index == 0:
                    pointID = re.findall('point.php\?id=([0-9]+)',str(td) , re.MULTILINE | re.DOTALL)[0]
                    ipv4 = re.findall('>([0-9.]+)<',str(td) , re.MULTILINE)[0]
                elif index == 1:
                    location = re.findall('src=".*?> (.*?)\n',str(td) , re.MULTILINE | re.DOTALL)[0]
                    provider = re.findall('company.php.*?>(.*?)<',str(td) , re.MULTILINE | re.DOTALL)[0]
                    city = location.split(", ")[1]
                    points[pointID] = {"location":location,"provider":provider,"city":city}

        self.target = target
        if len(points) > 30: print(f"Notice lookingHouse, {len(points)} probes gonna take some time")
        pool = multiprocessing.Pool(processes = 4)
        results = pool.map(self.run, points.items())
        pool.close()
        pool.join()

        output = {}
        for details in results:
            if not "avg" in details: continue
            output[f"{details['provider']}{details['location']}"] = {"provider":details['provider'],"avg":details['avg'],"city":details['city'],"ipv4":ipv4,"source":self.__class__.__name__}
            
        total = self.diff()
        print(f"Done lookingHouse done in {total}s")
        return output

