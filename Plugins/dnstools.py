from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio, re

class dnstools(Base):
    
    def __init__(self):
        print("dnstools.ws Loading")
        self.load()

    def prepare(self):
        print("dnstools.ws Preparing")
        return True

    def engage(self,origin,target):
        print("dnstools.ws Running")

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
                    avg = td.renderContents().decode().replace("ms","")
                elif index == 3:
                    if origin == self.GetAlpha2(country):
                        results[f"{city}{country}"] = {"provider":"n/a","avg":float(avg),"city":city}
        return results

