import copy
import itertools
import json
class indexstr(str):
    def __eq__(self, other):
        if isinstance(other, indexstr):
            return str(self) == str(other)
        return False

    def __hash__(self):
        return hash(str(self))


class State:
    def __init__(self):
        self.dict = {}
    def clear(self):
        self.dict = {}
    def add(self, x, y):
        self.dict[x] = y
    def walk(self, x):#sehr cringe
        if x in self.dict.keys():
            #(type(x),x,self.dict[x])
            return self.walk(self.dict[x])
        else:
            return x
    
    def __str__(self):
        return str(self.dict)
    
    __repr__ = __str__
    
    def unify(self, x, y):
        ###print("unifydebug: ",x," and ",y, 'in', self.dict)
        states = []
        x = self.walk(x)
        y = self.walk(y)
        ###print("UNIFYDEBUGTYPE",type(x),":",x,"  ",type(y),":",y)
        if type(x) != type(indexstr()):
            ###print(type(x),x,"   ",type(y),y)
            x,y = y,x
        copied = copy.deepcopy(self)
        if type(x) != type(indexstr()) and type(y) != type(indexstr()):
            if x==y:
                states.append(copied)
            else:
                ###print('Failed to unify', x, 'with', y)
                return []
        elif type(x) == type(indexstr()) or type(y) == type(indexstr()):
            copied.add(x,y)
            states.append(copied)
        ###print("unifydebugresult: ", states)
        return states

def disj(LoS1, LoS2):
    LoS1 = copy.copy(LoS1)
    for i in range(len(LoS1)):
        if LoS1[i] in LoS2:
            del LoS1[i]
    return LoS1+LoS2

def infdisj(LoSprovider1, LoSprovider2):
    for i,j in itertools.zip_longest(LoSprovider1,LoSprovider2):
        if i and j and i==j:
            yield i
        elif  i:
            yield i
        elif j:
            yield j

def eq(x,y):
    return lambda state: state.unify(x,y)

def OR(f,g):
    return lambda state: disj(f(state),g(state))

def conj(LoS, func):
    LoS2 = []
    ###print(func,LoS)
    for i in LoS:
        LoS2 = disj(func(i), LoS2)
    return LoS2

def infconj(LoSgen, func):
    for i in LoSgen:
        yield infdisj(func(i),LoS2)


def AND(f,g):
    return lambda state: conj(f(state),g)

def dict2state(d,name):
    ##print('dict2state called with', d)
    res = []
    for i in d:
        #print(d)
        #print(name)
        res.append(eq(indexstr(name+i),d[i]))
    while len(res) != 1:
        a = res.pop()
        b = res.pop()
        res.append(AND(a,b))
    #print('dict2stated',res[0](State()))
    return res[0]

def list2LoS(l,name):
    res = []
    ##print('l:',l)
    for item in l:
        
        state = dict2state(item,name)
        res.append(state)
        
    while len(res) != 1:
        a = res.pop()
        b = res.pop()
        res.append(OR(a, b))
    return res[0]


def tables2los(tables, names):
    res = []
    ##print('tables: ',tables)
    for item, name in zip(tables, names):
        ###print(item)
        res.append(list2LoS(item,name))
        ##print('list2losed: ', res[len(res)-1](State()))
    while len(res) != 1:
        a = res.pop()
        b = res.pop()
        res.append(AND(a,b))
    ##print(res[0](State()))
    return res[0]

def read_json(filename):
    with open(filename, "r") as file:
        data = json.load(file)
    return data


#TODO: finish file r/w support
print(dict2state(read_json('test.json')[0],'test/')(State()))
###print(list2LoS(read_json('test.json'),'test')(State()))

###print(AND(tables2los([read_json('test.json'),read_json('students.json')],['test','students']), eq(indexstr('students/owner_name'), indexstr('test/name')))(State()))

Max = AND(AND(eq(indexstr("name"),"Max"),eq(indexstr("age"),22)),eq(indexstr("teacher"),True))
Sam = AND(AND(eq(indexstr("name"),"Sam"),eq(indexstr("age"),10)),eq(indexstr("teacher"),False))
testbase = OR(Max,Sam)
##print(AND(testbase, eq(indexstr("teacher"),True))(State()))
