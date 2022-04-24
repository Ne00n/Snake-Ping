from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio, re

class dnstools(Base):
    
    def __init__(self):
        self.load()

    def prepare(self):
        return True

    def engage(self,origin,target):
        print("Running dnstools.ws")

        html = asyncio.run(self.browse(f"https://dnstools.ws/ping/{target}/"))
        soup = BeautifulSoup(html,"html.parser")
        results = {}
        for tr in soup.findAll('tr'):
            if tr.has_attr("class") == False or "dns-detail-expanded" in tr['class']: continue

            for index,td in enumerate(tr.findAll('td')):
                if td.has_attr("class") == False or "expand-cell" in td['class']: continue
                
                if index == 1:
                    location = re.findall('svg>(.*?)<',str(td) , re.MULTILINE)
                    if not location: continue
                    countryCase = location[0].count(",")
                    if countryCase == 0:
                        country = location[0]
                        city = "n/a"
                    elif countryCase == 1:
                        location = location[0].split(", ")
                        country = location[1]
                        city = location[0]
                elif index == 2:
                    avg = re.findall('>([0-9.]+)ms',str(td) , re.MULTILINE | re.DOTALL)
                    if not avg: break
                elif index == 3:
                    if origin == self.GetAlpha2(country):
                        results[f"{city}{country}"] = {"provider":"n/a","avg":float(avg[0]),"city":city,"source":self.__class__.__name__}
        print("Done dnstools.ws")
        return results

