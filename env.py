from types import SimpleNamespace

envData = open(".env", "r").readlines()
envData = [x.strip() for x in envData]

dictionary = {}
for i in envData:
    dictionary[i.split("=")[0]] = i.replace(i.split("=")[0] + "=", "") # support for multiple = in value

env = SimpleNamespace(**dictionary)