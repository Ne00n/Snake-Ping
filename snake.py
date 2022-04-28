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
    for i, (probe,probeDetails) in enumerate(combined.items()):
        print(f"{i+1} of {len(combined)}")
        print(f"Getting Data for {probeDetails['city']}, {probeDetails['provider']}")
        for index, row in enumerate(toLoad): toLoad[index] = {"plugin":row['plugin'],"origin":targetCountry,"target":probeDetails['ipv4']}
        pool = Pool(max_workers = 6)
        probeResults = pool.map(notMyBase.run, toLoad)
        pool.shutdown(wait=True)
        for data in probeResults:
            if not data: continue
            for probeTarget,probeTargetDetails in data.items():
                probeTargetDetails['probe'] = f"{probeDetails['city']}, {probeDetails['provider']}"
                pingData[f"{probe}{probeDetails['source']}{probeTarget}"] = probeTargetDetails
    #sort data by probe
    pingData = sorted(pingData.items(), key=lambda d: float(d[1]['avg'])) 
    #Generate Output
    output.append("Latency\tSource\tProbe\tCity\tProvider")
    output.append("-------\t-------\t-------\t-------\t-------")
    for probeData in pingData:
        avg = "{:.2f}ms".format(float(probeData[1]['avg']))
        output.append(f"{avg}\t{probeData[1]['source']}\t{probeData[1]['probe']}\t{probeData[1]['city']}\t{probeData[1]['provider']}")

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

output = notMyBase.formatTable(output)
print(f"\nResults")
print(output)