from bs4 import BeautifulSoup
from Plugins.base import Base
from pyppeteer import launch
import asyncio, re

class pingpe(Base):
    
    def __init__(self):
        print("ping.pe Loading")
        self.load()

    def prepare(self):
        print("ping.pe Preparing")
        return True

    async def browse(self,target):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(f"https://ping.pe/{target}/", {'waitUntil' : 'domcontentloaded'})

        await asyncio.sleep(10)
        html = await page.content()

        await page.close()
        await browser.close()
        return html

    def engage(self,origin,target):
        print("ping.pe Running")
        html = asyncio.run(self.browse(target))

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
                results[probe[0]] = {"provider":provider[0],"avg":avg[0],"city":city}
        return results

