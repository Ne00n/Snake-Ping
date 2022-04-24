from pyppeteer import launch
import asyncio, time, json, re

class Base():

    def load(self):
        with open('mapping.json', 'r') as f:
            self.map = json.load(f)

    def find(self,target,field):
        for row in self.map:
            if target in row[field]: return row

    def GetAlpha2(self,target):
        if len(target) == 2: return target
        elif len(target) == 3:
            result = self.find(target,"alpha-3")
            if not result: return False
            return result['alpha-2']
        elif len(target) > 3:
            result = self.find(target,"name")
            if not result: return False
            return result['alpha-2']

    def getCountry(self,target):
        if len(target) == 2:
            result = self.find(target,"alpha-2")
            if not result: return False
            return result['name']
        elif len(target) == 3:
            result = self.find(target,"alpha-3")
            if not result: return False
            return result['name']
        elif len(target) > 3: return target

    async def browse(self,target,wait=10,element=""):
        browser = await launch()
        page = await browser.newPage()   

        await page.goto(target, {'waitUntil' : 'domcontentloaded'})

        if wait == 0:
            await page.waitForSelector(element)
        else:
            await asyncio.sleep(wait)

        html = await page.content()
        await page.close()
        await browser.close()
        return html

    def browseWrapper(self,target,wait=10,element=""):
        for run in range(4):
            try:   
                return asyncio.run(self.browse(target,wait,element)) 
            except Exception as e:
                print(f"Retrying {target}")
                time.sleep(2)
                if run == 3: return False