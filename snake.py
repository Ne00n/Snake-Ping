from concurrent.futures import ProcessPoolExecutor as Pool
from Plugins.base import Base
import sys, os

print("Snake-Ping")
plugins = os.listdir("Plugins")

if len(sys.argv) < 3: exit("Missing params, e.g NL 1.1.1.1")
origin = sys.argv[1]
target = sys.argv[2]
pluginToLoad = sys.argv[3] if len(sys.argv) == 4 else ""

data,toLoad = {},[]
for filename in plugins:
    if not filename.endswith(".py") or filename == "base.py": continue
    plugin = filename.replace(".py","")
    if pluginToLoad != "" and plugin != pluginToLoad: continue
    toLoad.append({"plugin":plugin,"origin":origin,"target":target})

notMyBase = Base()
dataUnsorted,results,output = {},[],[]

pool = Pool(max_workers = 6)
results = pool.map(notMyBase.run, toLoad)
pool.shutdown(wait=True)

if target == "compare":
    print("Combining Results")
    combined, pingData = {},{}
    for pluginData in results:
        if not pluginData: continue
        combined.update(pluginData)
    print("Collection data")
    originCountry, targetCountry = origin.split(',')
    for probe,probeDetails in combined.items():
        print(f"Getting Data for {probe}")
        for index, row in enumerate(toLoad): toLoad[index] = {"plugin":row['plugin'],"origin":targetCountry,"target":probeDetails['ipv4']}
        pool = Pool(max_workers = 6)
        probeResults = pool.map(notMyBase.run, toLoad)
        pool.shutdown(wait=True)
        for data in probeResults:
            if not data: continue
            for probeTarget,probeTargetDetails in data.items():
                if not probe in pingData: pingData[probe] = []
                pingData[probe].append(probeTargetDetails)
    #sort data by probe
    for probe,probeData in pingData.items():
        pingData[probe] = sorted(probeData, key=lambda d: float(d['avg'])) 
    #Generate Output
    for probe,probeData in pingData.items():
        output.append(f"Probe {probe}")
        output.append("Latency\tSource\tCity\tProvider")
        output.append("-------\t-------\t-------\t-------")
        for index, probeDetails in enumerate(probeData):
            if index < 10:
                avg = "{:.2f}ms".format(float(probeDetails['avg']))
                output.append(f"{avg}\t{probeDetails['source']}\t{probeDetails['city']}\t{probeDetails['provider']}")

else:
    for data in results:
        if not data: continue
        for probe,details in data.items():
            dataUnsorted[probe] = {"plugin":details['source'],"avg":float(details['avg']),"provider":details['provider'],"city":details['city']}
        #Generate Output
        output.append("Latency\tSource\tCity\tProvider")
        output.append("-------\t-------\t-------\t-------")
        dataSorted = sorted(dataUnsorted.items(), key=lambda x: x[1]['avg'])
        for data in dataSorted:
            avg = "{:.2f}ms".format(data[1]['avg'])
            output.append(f"{avg}\t{data[1]['plugin']}\t{data[1]['city']}\t{data[1]['provider']}")

def formatTable(list):
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

output = formatTable(output)
print(f"\nResults")
print(output)