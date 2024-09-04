from types import SimpleNamespace

env = open(".env", "r").readlines()
env = [x.strip() for x in env]

dictionary = {}
for i in env:
    dictionary[i.split("=")[0]] = i.split("=")[1]

env = SimpleNamespace(**dictionary)