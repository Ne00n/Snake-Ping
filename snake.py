import importlib.util
import sys, os

print("Multi-Ping-Snake-Edition")
plugins = os.listdir("Plugins")

if len(sys.argv) < 3: exit("Missing params, e.g NL 1.1.1.1")
country = sys.argv[1]
target = sys.argv[2]

data = {}
for filename in plugins:
    if not filename.endswith(".py"): continue
    plugin = filename.replace(".py","")
    myClass = getattr(importlib.import_module(f"Plugins.{plugin}"), plugin)
    myInstance = myClass()
    response = myInstance.prepare()
    if response is not True:
        print(f"{plugin} failed to prepare")
        continue
    response = myInstance.engage(country,target)
    data[plugin] = response

result = {}
for plugin,pluginData in data.items():
    for probe,details in pluginData.items():
        result[details['provider']] = float(details['avg'])
    
print("--- Results ---")
result = sorted(result.items(), key=lambda x: x[1])
for data in result:
    print("{:.2f}ms".format(data[1]),data[0])
print("--- Done ---")