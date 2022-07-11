from Plugins.base import Base
from bs4 import BeautifulSoup
from pyppeteer import launch
import asyncio, socket, re
import multiprocessing

class mtrtools(Base):

    localMapping = {"UK":"GB"}
    
    def __init__(self,config):
        self.config = config
        self.load()

    def prepare(self):
        return True

    async def browse(self,target,country):
        browser = await launch(headless=True,executablePath=self.config['executablePath'])
        page = await browser.newPage()

        await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36')
        await page.goto(f"https://mtr.tools/", {'waitUntil' : 'domcontentloaded'})

        await asyncio.sleep(1)

        await page.focus('#target')
        await page.keyboard.type(target)
        html = await page.content()

        soup = BeautifulSoup(html,"html.parser")
        divs = soup.select("div[class^='toggle btn']")
        marked = 0
        element = await page.querySelectorAll("div.toggle")
        for index, div in enumerate(divs):
            input = div.select("input")[0]
            if input.has_attr("data-asnumber") == False or input.has_attr("disabled"): continue
            alpha2 = self.GetAlpha2(input['data-country'])
            if alpha2 != country: continue
            await element[index].click()
            marked += 1

        await asyncio.sleep(1)

        if marked > 1:
            await element[3].click()
            element = await page.querySelector('#runtest')
            await element.click()

            await page.waitForSelector('div.progress-bar', {"hidden": True})
            html = await page.content()
        else:
            print("Warning mtrsh, No Probes found in Target Country")

        await page.close()
        await browser.close()
        return html

    def engage(self,origin,target):
        print("Running mtr.tools")
        if origin in self.localMapping: origin = self.localMapping[origin]
        self.start()

        html = asyncio.run(self.browse(target,origin))
        soup = BeautifulSoup(html,"html.parser")
        panels = soup.select("div.panel")
        output = {}
        for panel in panels:
            data = re.findall('\| Ping from\s(.*?)\sAS.*?in\s(.*?),\s(.*?)\s<',str(panel) , re.MULTILINE)
            avg = re.findall('mdev =.*?\/([0-9.]+)',str(panel) , re.MULTILINE)
            if not avg: continue
            output[f"{data[0][0]}{data[0][2]}"] = {"provider":data[0][0],"city":data[0][2],"avg":avg[0],"source":self.__class__.__name__}
        total = self.diff()
        print(f"Done mtr.tools done in {total}s")
        return output


