import re, textwrap
import sys, os.path, shutil

import ara, maintenance

from datetime import datetime
startTime = datetime.now()

# REPORT STRUCTURE
#  0 : match          - complete match as a key
#  1 : display        - reformatted match for display
#  2 : ng1            - ngrams (tagged-3)
#  3 : ng2            - ngrams (tagged-2)
#  4 : ng3            - ngrams (tagged-1)
#  5 : tagged (ng4)   - ngrams (tagged-0)
#  6 : ng5            - ngrams (tagged+1)
#  7 : ng6            - ngrams (tagged+2)
#  8 : ng7            - ngrams (tagged+3)
#  9 : "status"       - status of review
# 10 : "probability"  - probabilities, based on ngram extrapolations
# 11 : "ngram"        - ngrams (numbers), for matches exclude/include
# 12 : "position"     - position in the text broken into list on space
# 13 : "middleTag"    - tagged item as it appears in the text
# 14 : "gazForm"      - gazetteer form of an item

def updateDic(dic, key, val):
    if key in dic:
        dic[key] += val
    else:
        dic[key]  = val
        

def loadGazetteer():
    dic = {}

    with open(schemeFolder+"topMicro.csv", "r", encoding="utf8") as f1:
        raw = f1.read().replace("=", " ").split("\n")

        for r in raw[1:]:
            a = r.split("\t")
            dic[a[0]] = r

    return(dic)

def convertProgressReport(progressRep):
    dic = {}

    with open(generated+progressRep, "r", encoding="utf8") as f1:
        data = f1.read().split("\n")

        for d in data:
            a = d.split("\t")

            status = a[9]
            uri    = a[13]

##            if status[0] == "t":
##                updateDic(dic, uri, 1)

            updateDic(dic, uri, 1)

        regDic = {}
        topoList = []
        for k,v in dic.items():
            if k in gaz:
                topoList.append(gaz[k]+"\t"+str(v))
                reg = gaz[k].split("\t")[1]
                updateDic(regDic, reg, v)

        regList = []
        for k,v in regDic.items():
            if k in gaz:
                regList.append(gaz[k]+"\t"+str(v))

        HEAD = "URI\tREG_MESO\tTR\tSEARCH\tEN\tTYPE\tLON\tLAT\tAR\tAR_Alt\tAR_Sort\tFREQ\n"

        topoList = HEAD+"\n".join(topoList)
        regList =  HEAD+"\n".join(regList)

        with open(gist+progressRep+".topoFreq_RAW.csv", "w", encoding="utf8") as f9:
            f9.write(topoList)

        with open(gist+progressRep+".regFreq_RAW.csv", "w", encoding="utf8") as f9:
            f9.write(regList)       
            
           
# VARIABLES ########################################

dataFolder    = "./data/"
schemeFolder  = "./interpretative_schemes/"
generated     = "./generated/"
gist = "../3_GIStingTexts/"

with open("_fileToEdit.txt", "r", encoding="utf8") as f1:
    textFile = f1.read()
taggingScheme = "ToponymML.csv"
progressRep   = textFile+".ToponymsMLprogressReport"

# RUNNING ##########################################

gaz = loadGazetteer()
convertProgressReport(progressRep)

print("===>" + str(datetime.now() - startTime))
print("Done!")
