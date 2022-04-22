from bs4 import BeautifulSoup
from Plugins.base import Base
from pyppeteer import launch
import asyncio, re

class pingpe(Base):
    
    def __init__(self):
        self.load()

    def prepare(self):
        return True

    def engage(self,origin,target):
        print("Running ping.pe")
        html = asyncio.run(self.browse(f"https://ping.pe/{target}/"))

        soup = BeautifulSoup(html,"html.parser")
        rows = soup.findAll('tr', id=re.compile('^ping-'))
        results = {}
        for row in rows:
            row = str(row)
            avg = re.findall("ping-.*?avg.*?>([0-9.]+)",row , re.MULTILINE)
            if not avg: continue
            probe = re.findall('<td id="ping.(.*?)-location"',row , re.MULTILINE)
            provider = re.findall('td-provider".*?>(.*?)<',row , re.MULTILINE)
            country = re.findall("td-location.*?>(.*?)<",row , re.MULTILINE)
            countryCase = country[0].count(",")
            if countryCase == 0:
                country = country[0]
                city = "n/a"
            elif countryCase == 1:
                location = country[0].split(", ")
                country = location[0]
                city = location[1]
            elif countryCase == 2:
                location = country[0].split(", ")
                country = location[0]
                city = location[2]
            if "UAE" == country: country = "ARE"
            if origin == self.GetAlpha2(country):
                results[probe[0]] = {"provider":provider[0],"avg":avg[0],"city":city,"source":self.__class__.__name__}
        print("Done ping.pe")
        return results

