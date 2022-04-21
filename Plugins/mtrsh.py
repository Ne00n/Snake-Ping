import requests, json, re

class mtrsh():

    mapping = {}
    headers = {
        'Host':'mtr.sh',
        'Accept':'application/json;',
        'X-Application-For':'Multi-Ping',
        'Accept-Encoding':'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    
    def __init__(self):
        print("mtr.sh Loading")

    def prepare(self):
        print("mtr.sh Preparing")
        response = requests.get(url="https://mtr.sh/probes.json", headers=self.headers)
        if response.status_code != 200: return False
        probes = response.json()
        for name,details in probes.items():
            if details['status'] is False: continue
            if not details['country'] in self.mapping: self.mapping[details['country']] = []
            self.mapping[details['country']].append({"probe":name,"provider":details['provider']})
        return True

    def engage(self,country,target):
        print("mtr.sh Running")
        with open('mapping.json', 'r') as f:
            mapping = json.load(f)
        country = mapping[country]
        if not country in self.mapping:
            print("No Probes found in Target Country")
            return False
        probes = self.mapping[country]
        results = {}
        for probe in probes:
            print(f"mtr.sh {probe['provider']}")
            response = requests.get(url=f"https://mtr.sh/{probe['probe']}/ping/{target}", headers=self.headers)
            if response.status_code != 200: continue
            result = re.findall("avg\/.*?=.*?\/([0-9.]+)",response.text, re.MULTILINE)
            if not result: continue
            results[probe['probe']] = {"provider":probe['provider'],"avg":result[0]}
        return results


