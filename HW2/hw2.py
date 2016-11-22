# few parts of the algorithm is taken from AIMA textbook
import sys
import copy

impStr = " => "
andStr = " && "
leftBrac = "("
rightBrac = ")"
coma = ", "
outputfile = open("output.txt", 'w')

class TrivialExp(object):

    def __init__(self, pArgs, pName, pLhs=None, debug = None):
        self.argVals = pArgs
        self.lhs = pLhs
        self.nameVal = pName
    
    def present(self, pTheta, debug = None):
        s1 = self.nameVal
        s2 = ", ".join(map(lambda arg: "_" if arg[0].islower() and arg not in pTheta else arg, self.argVals))
        s3 = s1 + "(" + s2 + ")"
        return s3

class Tool(object):

    def __init__(self, debug = None):
        self.counter = 1
        self.oldVar = set([])
        self.rules = []

    def ask(self, qryString, debug=False):
        global outputfile
        qString = ""
        if type(qryString) == list:
            qString = qryString 
        else: 
            qString = [qryString]
        res = False
        for q in qString:
            for res in self.orBC(q, {}):
                if res: break
            if not res:
                break
        lastline = "True"
        if res:
            lastline = "True"
        else:
            lastline = "False"
        outputfile.write(lastline)
        return res

    def andBC(self, pAim, pTheta, debug = None):
        if pTheta == None: return
        elif len(pAim) == 0: yield pTheta
        else:
            first,rest = pAim[0],pAim[1:]
            for x in self.orBC(self.Replace(pTheta,first), copy.deepcopy(pTheta)):
                for y in self.andBC(copy.deepcopy(rest), copy.deepcopy(x)):
                    yield y

    def Replace(self, pTheta, instr, debug = None):
        instr = copy.deepcopy(instr)
        for i,j in enumerate(instr.argVals):
            while j in pTheta:
                instr.argVals[i] = pTheta[j]
                j = pTheta[j]
        return instr

    def orBC(self, pAim, pTheta, debug = None):
        outputfile.write("Ask: " + pAim.present(pTheta))
        outputfile.write("\r\n")
        self.oldVar.update(pAim.argVals)
        resVar = False
        valTrue = 0
        for instr in self.fetch(pAim):
            instr = self.standardize(instr)
            unified = self.unify(pAim, instr, copy.deepcopy(pTheta))
            if unified:
                valTrue += 1
                if valTrue > 1:
                    outputfile.write("Ask: "+ pAim.present(pTheta))
                    outputfile.write("\r\n")
                varThetas = [unified]
                if instr.lhs:
                    varThetas = self.andBC(instr.lhs, unified)
                for varTheta in varThetas:
                    outputfile.write("True: " + self.Replace(varTheta, pAim).present(pTheta))
                    outputfile.write("\r\n")
                    resVar = True
                    yield varTheta
        if not resVar:
            outputfile.write("False: " + pAim.present(pTheta))
            outputfile.write("\r\n")
            yield None

    def unify_var(self, var, x, pTheta, debug = None):
        if  var in pTheta: return self.unify(pTheta[var],x,pTheta)
        elif x in pTheta: return self.unify(var,pTheta[x],pTheta)
        else : pTheta[var]=x;return pTheta

    def unify(self, x, y, pTheta, debug = None):
        if pTheta is None: return None
        elif x == y: return pTheta
        elif type(x) is str and x[0].islower(): return self.unify_var(x, y, pTheta)
        elif type(y) is str and y[0].islower(): return self.unify_var(y, x, pTheta)
        elif isinstance(x, TrivialExp) and isinstance(y, TrivialExp): return self.unify(x.argVals, y.argVals, self.unify(x.nameVal, y.nameVal,pTheta))
        elif type(x) is list  and type(y) is list: return self.unify(x[1:], y[1:], self.unify(x[0], y[0], pTheta))
        else: return None

    def standardize(self, instr, debug = None):
        tempvar=set([])
        chn={}
        for i, arg in enumerate(instr.argVals):
            if arg in self.oldVar:
                if arg[0].islower():
                    self.counter += 1
                    self.oldVar.add("x" + str(self.counter))
                    chn[arg] = "x" + str(self.counter)
                    instr.argVals[i]=chn[arg]
            else:
                tempvar.add(arg)
        if instr.lhs:
            for tmp in instr.lhs:
                for idx, arg in enumerate(tmp.argVals):
                    if arg in chn:
                        tmp.argVals[idx] = chn[arg]
                    elif arg not in tempvar:
                        if arg in self.oldVar: 
                            if arg[0].islower():
                                self.counter += 1
                                self.oldVar.add("x" + str(self.counter))
                                newvar = "x" + str(self.counter)
                                chn[arg]= newvar
                                tmp.argVals[idx] = newvar
        self.oldVar.update(tempvar)
        return (instr)

    def fetch(self, qryString, debug = None):
        for instr in self.rules:
            if instr.nameVal == qryString.nameVal: yield copy.deepcopy(instr)

def parse(pLine, debug=False):
    pLine = pLine.strip()
    if impStr in pLine:
        divs = pLine.split(impStr)
        strVal = TrivialExp(None, None)
        parseAtomic(divs[1], strVal)
        strVal.lhs = map(lambda x: parseAtomic(x), divs[0].split(andStr))
        return strVal
    elif andStr in pLine:
        return map(lambda x:parseAtomic(x), pLine.split(andStr))
    return parseAtomic(pLine)

def parseAtomic(pLine, pStmt=None, debug=False):
    if not pStmt:
        pStmt = TrivialExp(None, None)
    pStmt.argVals = map(lambda x: x.strip(),
                            pLine[pLine.index(leftBrac)+1 : pLine.index(rightBrac)].split(coma))
    pStmt.nameVal = pLine[:pLine.index(leftBrac)]
    return pStmt

kRep = Tool()
testQry = None
with open(sys.argv[2]) as inFile:
    lines = inFile.readlines()
    testQry = parse(lines[0])
    for l in lines[2:]:
        kRep.rules.append(parse(l))

kRep.ask(testQry, debug=True)