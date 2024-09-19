from types import SimpleNamespace

env = open(".env", "r").readlines()
env = [x.strip() for x in env]

dictionary = {}
for i in env:
    dictionary[i.split("=")[0]] = i.replace(i.split("=")[0] + "=", "") # support for multiple = in value

env = SimpleNamespace(**dictionary)