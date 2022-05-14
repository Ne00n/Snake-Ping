from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio, re

class pingsx(Base):
    
    def __init__(self,config):
        self.config = config
        self.load()

    def prepare(self):
        return True

    def canRunAny(self):
        return True

    async def browse(self,target):
        browser = await launch(headless=True)
        page = await browser.newPage()

        await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36')
        await page.goto(f"https://ping.sx/ping?t={target}", {'waitUntil' : 'domcontentloaded'})

        await asyncio.sleep(5)
        
        element = await page.querySelector('button.btn-sm')
        await element.click()

        await asyncio.sleep(30)

        html = await page.content()

        await page.close()
        await browser.close()
        return html

    def engage(self,origin,target):
        print("Running ping.sx")

        html = asyncio.run(self.browse(target))
        soup = BeautifulSoup(html,"html.parser")

        results = {}
        for tr in soup.findAll('tr'):
            if tr.has_attr("class") == False: continue
            for index,td in enumerate(tr.findAll('td')):
                if index == 0:
                    country = re.findall('img alt="(.*?) Flag',str(td) , re.MULTILINE)[0]
                    city = re.findall('flex-0">(.*?)<',str(td) , re.MULTILINE)[0]
                elif index == 1:
                    provider = re.findall('>(.{1,25}?)<',str(td) , re.MULTILINE)[0]
                elif index == 7:
                    #why best? avg is lower than best sometimes
                    avg = re.findall('>([0-9.]+)<',str(td) , re.MULTILINE)
                    if not avg: continue
                    if origin == self.GetAlpha2(country) or origin == "any":
                        results[f"{provider}{country}{city}"] = {"provider":provider,"avg":avg[0],"city":city,"source":self.__class__.__name__}
        print("Done ping.sx")
        return results

