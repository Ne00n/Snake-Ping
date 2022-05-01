import ipaddress, asyncio, time, json, re
from timeit import default_timer as timer
from pyppeteer import launch
import importlib.util

class Base():

    def __init__(self,config={}):
        self.config = config

    def load(self,config={}):
        with open('mapping.json', 'r') as f:
            self.map = json.load(f)

    def find(self,target,field):
        for row in self.map:
            if target in row[field]: return row

    def start(self):
        self.timer = timer()

    def diff(self):
        return round((timer() - self.timer),2)

    def isComparable(self):
        return False

    def canRunAny(self):
        return False

    def compare(self,countries,param):
        origin, target = countries.split(',')
        originData = self.engage(origin,"1.1.1.1")
        return originData

    def run(self,data):
        myClass = getattr(importlib.import_module(f"Plugins.{data['plugin']}"), data['plugin'])
        myInstance = myClass(self.config)
        response = myInstance.prepare()
        if response is not True:
            print(f"{data['plugin']} failed to prepare")
            return {}
        if data['target'] == "compare" and myInstance.isComparable():
            return myInstance.compare(data['origin'],data['target'])
        elif data['origin'] == "any":
            if myInstance.canRunAny() is False: return {}
            return myInstance.engage(data['origin'],data['target'])
        elif data['target'] != "compare":
            return myInstance.engage(data['origin'],data['target'])
        else:
            return {}

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

    def validateIP(self,address):
        try:
            ip = ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    async def browse(self,target,wait=10,element=""):
        browser = await launch(headless=True,executablePath=self.config['executablePath'])

        for run in range(4):
            page = await browser.newPage()   
            try:
                await page.goto(target, {'waitUntil' : 'domcontentloaded'})

                if wait == 0:
                    await page.waitForSelector(element)
                else:
                    await asyncio.sleep(wait)

                html = await page.content()
                await page.close()
                break
            except:
                print("Page crashed, retrying")
                print("Closing page")
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

    def formatTable(self,list):
        longest,response = {},""
        for row in list:
            elements = row.split("\t")
            for index, entry in enumerate(elements):
                if not index in longest: longest[index] = 0
                if len(entry) > longest[index]: longest[index] = len(entry)
        for i, row in enumerate(list):
            elements = row.split("\t")
            for index, entry in enumerate(elements):
                if len(entry) < longest[index]:
                    diff = longest[index] - len(entry)
                    while len(entry) < longest[index]:
                        entry += " "
                response += f"{entry}" if response.endswith("\n") or response == "" else f" {entry}"
            if i < len(list) -1: response += "\n"
        return response