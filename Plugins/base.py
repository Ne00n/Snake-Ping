from pyppeteer import launch
import asyncio, json, re

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

    async def browse(self,target):
        browser = await launch()
        page = await browser.newPage()
        await page.goto(target, {'waitUntil' : 'domcontentloaded'})

        await asyncio.sleep(10)
        html = await page.content()

        await page.close()
        await browser.close()
        return html