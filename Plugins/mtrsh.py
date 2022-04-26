from Plugins.base import Base
import requests, json, re
import multiprocessing

class mtrsh(Base):

    localMapping = {"UK":"GB"}
    mapping = {}
    headers = {
        'Host':'mtr.sh',
        'Accept':'application/json;',
        'X-Application-For':'Snake-Ping',
        'Accept-Encoding':'gzip, deflate',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'}
    
    def __init__(self):
        self.load()

    def prepare(self):
        response = requests.get(url="https://mtr.sh/probes.json", headers=self.headers)
        if response.status_code != 200: return False
        probes = response.json()
        for name,details in probes.items():
            if details['status'] is False: continue
            if not details['country'] in self.mapping: self.mapping[details['country']] = []
            self.mapping[details['country']].append({"probe":name,"provider":details['provider'],"city":details['city']})
        return True

    def run(self,probe):
        response = requests.get(url=f"https://mtr.sh/{probe['probe']}/ping/{self.target }", headers=self.headers)
        if response.status_code != 200: return {}
        avg = re.findall("avg\/.*?=.*?\/([0-9.]+)",response.text, re.MULTILINE)
        if not avg: return {}
        probe['avg'] = avg[0]
        return probe

    def engage(self,origin,target):
        print("Running mtr.sh")
        if origin in self.localMapping: origin = self.localMapping[origin]
        country = self.getCountry(origin)
        if not country in self.mapping:
            print("Warning mtr.sh, No Probes found in Target Country")
            return {}

        output = {}
        self.target = target
        pool = multiprocessing.Pool(processes = 4)
        results = pool.map(self.run, self.mapping[country])

        for result in results:
            if not "avg" in result: continue
            output[result['probe']] = {"provider":result['provider'],"city":result['city'],"avg":result['avg'],"source":self.__class__.__name__}
        print("Done mtr.sh")
        return output


