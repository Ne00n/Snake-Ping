from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio, re

class mudfish(Base):
    
    def __init__(self):
        self.load()

    def prepare(self):
        return True

    async def browse(self,target,country):
        browser = await launch(headless=True)
        page = await browser.newPage()

        await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36')
        await page.goto(f"https://ping.mudfish.net/", {'waitUntil' : 'domcontentloaded'})

        await asyncio.sleep(3)

        await page.focus('#ping_ip')
        await page.keyboard.type(target)
        html = await page.content()

        soup = BeautifulSoup(html,"html.parser")
        inputs = soup.findAll('input', id=re.compile('^checkbox_node_'))
        probes = []
        for input in inputs:
            if input['location'].startswith(country) and len(probes) <= 29:
                location = re.findall('\((.*?-\s.*?)(\)|\s[0-9]+)',str(input['location']) , re.MULTILINE)
                if location[0][0] in probes: continue
                element = await page.querySelector(f"#{input['id']}")
                await element.click()
                probes.append(location[0][0])
            if len(probes) == 29: 
                print("Warning mudfish, reached the limit of 29 probes")
                break

        element = await page.querySelector('#ping_start')
        await element.click()

        await asyncio.sleep(10)

        html = await page.content()

        await page.close()
        await browser.close()
        return html

    def engage(self,origin,target):
        print("Running mudfish")

        if not self.validateIP(target):
            print("mudfish does only work with IP's")
            return False

        html = asyncio.run(self.browse(target,origin))
        soup = BeautifulSoup(html,"html.parser")

        results = {}
        tbody = soup.findAll('tbody')
        for tr in tbody[0].findAll('tr'):
            for index, td in enumerate(tr.findAll('td')):
                if index == 0:
                    location = re.findall('<td>([A-Z]{2})\s(.*?)\s\((.*?)\s-\s(.*?)\)',str(td) , re.MULTILINE)
                    provider = location[0][3]
                    country = location[0][0]
                    city = location[0][2]
                elif index == 4:
                    avg = re.findall('>([0-9.]+)<',str(td) , re.MULTILINE)
                    if not avg: continue
                    results[f"{provider}{country}{city}"] = {"provider":provider,"avg":avg[0],"city":city,"source":self.__class__.__name__}
        print("Done mudfish")
        return results

