#Falso dict
class MyFakeDict:
    def __getitem__(self, key):
        return 'culo'

#Real dict
class MyDict(dict):
    def test(self):
        return '1234';


print("------------- dict REAL --------------")
midict={"hola":"que tal"}
print(midict)
print("tipo: ",type(midict))
print("es dict?: ",isinstance(midict, dict))

print("------------- dict heredado ----------")
miotrodict=MyDict()
miotrodict['hola']='que tal'
print(miotrodict)
print("tipo: ",type(miotrodict))
print("es dict?: ",isinstance(miotrodict, dict))
print(miotrodict.test())

print("------------- dict FALSO ----------")
mifalsodict=MyFakeDict()
print(mifalsodict)
print("tipo: ",type(mifalsodict))
print("es dict?: ",isinstance(mifalsodict, dict))
mifalsodict['hola']='que tal'
