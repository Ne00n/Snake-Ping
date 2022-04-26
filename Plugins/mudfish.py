from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio, socket, re

class mudfish(Base):
    
    def __init__(self):
        self.load()

    def prepare(self):
        return True

    def isComparable(self):
        return True

    def compare(self,countries,param):
        origin, target = countries.split(',')
        #get ips from origin
        originData = self.engage(origin,"1.1.1.1")
        #get ips from target
        targetData = self.engage(target,"1.1.1.1")
        return {"origin":originData,"target":targetData}

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
        probes = {}
        for input in inputs:
            if input['location'].startswith(country):
                location = re.findall('\((.*?-\s.*?)(\)|\s[0-9]+)',str(input['location']) , re.MULTILINE)
                if location[0][0] in probes: continue
                probes[f"#{input['id']}"] = location[0][0]

        html = ""
        if len(probes) == 0:
            print("Warning mudfish, No Probes found in Target Country")
            return html
        if len(probes) > 30: print(f"Notice mudfish, {len(probes)} probes gonna take some time")

        response = []
        runs = round(len(probes) / 29)
        for run in range(runs):
            targets = list(probes.items())[run*29:(run+1)*29]
            #Batch Selection
            for target in targets:
                element = await page.querySelector(target[0])
                await element.click()
            #Batch Start
            element = await page.querySelector('#ping_start')
            await element.click()
            #Wait
            await asyncio.sleep(10)
            #Save Batch Data
            response.append(await page.content())
            #Batch Remove Selection
            for target in targets:
                element = await page.querySelector(target[0])
                await element.click()      

        await page.close()
        await browser.close()
        return response

    def engage(self,origin,target):
        print("Running mudfish")

        if not self.validateIP(target):
            try:
                ip = socket.gethostbyname(target)
                target = ip
            except:
                return False

        results = {}
        data = asyncio.run(self.browse(target,origin))
        for entry in data:
            soup = BeautifulSoup(entry,"html.parser")

            tbody = soup.findAll('tbody')
            if tbody:
                for tr in tbody[0].findAll('tr'):
                    for index, td in enumerate(tr.findAll('td')):
                        if index == 0:
                            location = re.findall('<td>([A-Z]{2})\s(.*?)\s\((.*?)\s-\s(.*?)\)',str(td) , re.MULTILINE)
                            provider = location[0][3]
                            country = location[0][0]
                            city = location[0][2]
                        elif index == 1:
                            ipv4 = re.findall('<td>([0-9.]+)<',str(td) , re.MULTILINE)[0]
                        elif index == 4:
                            avg = re.findall('>([0-9.]+)<',str(td) , re.MULTILINE)
                            if not avg: continue
                            results[f"{provider}{country}{city}"] = {"provider":provider,"avg":avg[0],"city":city,"ipv4":ipv4,"source":self.__class__.__name__}
        print("Done mudfish")
        return results

