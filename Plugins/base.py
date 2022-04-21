import json, re

class Base():

    def load(self):
        with open('mapping.json', 'r') as f:
            self.map = json.load(f)

    def find(self,target,field):
        for row in self.map:
            if row[field] == target: return row

    def GetAlpha2(self,target):
        if len(target) == 2: return target
        elif len(target) == 3:
            result = self.find(target,"alpha-3")
            return result['alpha-2']
        elif len(target) > 3:
            result = self.find(target,"name")
            return result['alpha-2']

    def getCountry(self,target):
        if len(target) == 2:
            result = self.find(target,"alpha-2")
            return result['name']
        elif len(target) == 3:
            result = self.find(target,"alpha-3")
            return result['name']
        elif len(target) > 3: return target


