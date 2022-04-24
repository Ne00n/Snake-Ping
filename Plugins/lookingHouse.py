from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import multiprocessing
import asyncio, re

class lookingHouse(Base):
    
    localMapping = {"UK":"GB"}
    secondaryMapping = {"United States":"USA"}
    mapping = {}

    def __init__(self):
        self.load()

    def prepare(self):
        html = self.browseWrapper(f"https://looking.house/index.php",3)
        soup = BeautifulSoup(html,"html.parser")
        for a in soup.findAll('a'):
            if a['href'].startswith("/points.php?country"):
                location = re.findall('points.php\?country=([0-9]+).*?text-align:center.*?>(.*?)<',str(a) , re.MULTILINE | re.DOTALL)
                self.mapping[location[0][1]] = location[0][0]
        return True

    def run(self,point):
        html = self.browseWrapper(f"https://looking.house/point.php?id={point[0]}&d={self.target}&f=ping",0,"pre")
        if html == False: return {}
        soup = BeautifulSoup(html,"html.parser")
        pre = soup.findAll('pre')
        avg = re.findall('avg\/.*?=.*?\/([0-9.]+)',str(pre[0]) , re.MULTILINE | re.DOTALL)
        if not avg: return {}
        point[1]['avg'] = avg[0]
        return point[1]

    def engage(self,origin,target):
        print("Running lookingHouse")

        if origin in self.localMapping: origin = self.localMapping[origin]
        country = self.getCountry(origin)
        #Why is it called fucking USA
        if country in self.secondaryMapping: country = self.secondaryMapping[country]
        if not country in self.mapping:
            print("Warning lookingHouse, No Probes found in Target Country")
            return False
        
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
                elif index == 1:
                    location = re.findall('src=".*?> (.*?)\n',str(td) , re.MULTILINE | re.DOTALL)[0]
                    provider = re.findall('company.php.*?>(.*?)<',str(td) , re.MULTILINE | re.DOTALL)[0]
                    city = location.split(", ")[1]
                    points[pointID] = {"location":location,"provider":provider,"city":city}

        self.target = target
        if len(points) > 30: print("Notice lookingHouse, lots of probes gonna take some time")
        pool = multiprocessing.Pool(processes = 4)
        results = pool.map(self.run, points.items())

        output = {}
        for details in results:
            if not "avg" in details: continue
            output[f"{details['provider']}{details['location']}"] = {"provider":details['provider'],"avg":details['avg'],"city":details['city'],"source":self.__class__.__name__}

        print("Done lookingHouse")
        return output

