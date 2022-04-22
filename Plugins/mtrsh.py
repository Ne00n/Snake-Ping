import requests, json, re
from Plugins.base import Base

class mtrsh(Base):

    mapping = {}
    headers = {
        'Host':'mtr.sh',
        'Accept':'application/json;',
        'X-Application-For':'Multi-Ping',
        'Accept-Encoding':'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    
    def __init__(self):
        print("mtr.sh Loading")
        self.load()

    def prepare(self):
        print("mtr.sh Preparing")
        response = requests.get(url="https://mtr.sh/probes.json", headers=self.headers)
        if response.status_code != 200: return False
        probes = response.json()
        for name,details in probes.items():
            if details['status'] is False: continue
            if not details['country'] in self.mapping: self.mapping[details['country']] = []
            self.mapping[details['country']].append({"probe":name,"provider":details['provider'],"city":details['city']})
        return True

    def engage(self,origin,target):
        print("mtr.sh Running")
        country = self.getCountry(origin)
        if not country in self.mapping:
            print("No Probes found in Target Country")
            return False
        probes = self.mapping[country]
        results = {}
        for probe in probes:
            response = requests.get(url=f"https://mtr.sh/{probe['probe']}/ping/{target}", headers=self.headers)
            if response.status_code != 200: continue
            result = re.findall("avg\/.*?=.*?\/([0-9.]+)",response.text, re.MULTILINE)
            if not result: continue
            results[probe['probe']] = {"provider":probe['provider'],"city":probe['city'],"avg":result[0]}
        return results


