import pickle

myDict = dict()
myDict['hello'] = 1
myDict['world'] = 10
myDict['bye'] = 100
with open('myDict.pkl', 'wb') as fout:
     pickle.dump(myDict, fout)

with open('myDict.pkl', 'rb') as fin:
     yourDict = pickle.load(fin)

print(yourDict)

