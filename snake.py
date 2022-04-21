import importlib.util
import sys, os

print("Snake-Ping")
plugins = os.listdir("Plugins")

if len(sys.argv) < 3: exit("Missing params, e.g NL 1.1.1.1")
origin = sys.argv[1]
target = sys.argv[2]
pluginToLoad = sys.argv[3] if len(sys.argv) == 4 else ""

data = {}
for filename in plugins:
    if not filename.endswith(".py") or filename == "base.py": continue
    plugin = filename.replace(".py","")
    if pluginToLoad != "" and plugin != pluginToLoad: continue
    myClass = getattr(importlib.import_module(f"Plugins.{plugin}"), plugin)
    myInstance = myClass()
    response = myInstance.prepare()
    if response is not True:
        print(f"{plugin} failed to prepare")
        continue
    response = myInstance.engage(origin,target)
    data[plugin] = response

results = {}
for plugin,pluginData in data.items():
    if not pluginData: continue
    for probe,details in pluginData.items():
        results[probe] = {"plugin":plugin,"avg":float(details['avg']),"provider":details['provider'],"city":details['city']}

output = []
output.append("Latency\tSource\tCity\tProvider")
output.append("-------\t-------\t-------\t-------")
results = sorted(results.items(), key=lambda x: x[1]['avg'])
for data in results:
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