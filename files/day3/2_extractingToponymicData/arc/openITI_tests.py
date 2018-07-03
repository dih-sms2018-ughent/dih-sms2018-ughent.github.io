import re, regex
import sys, os.path, shutil

sys.path.append("/Users/romanov/GitProjects/a.UCA_Centennial/OpenArabic/pyoa/pyoa/")
import ara, maintenance

from datetime import datetime
startTime = datetime.now()

# FUNCTION: test if indexing works fine
def testIndex(textFile, progressReport):
    # open tagged file
    splitter = "#META#Header#End#"
    taggedFile = dataFolder+textFile+".tagged"
    with open(taggedFile, "r", encoding="utf8") as f1:
        t = f1.read().split(splitter)
        text1 = t[1]

        text1 = text1.replace("\n~~", " ")
        text1 = re.sub(" +", " ", text1)

        TL = text1.replace("\n", "::n::")
        TL = TL.split(" ")

    with open(dataFolder+progressReport, "r", encoding="utf8") as f1:
        report = f1.read().split("\n")
        progress = {}
        for r in report:
            r = r.split("\t")
            progress[r[0]] = r

            print(r[5])
            print(TL[int(r[-1])])
            input()


dataFolder    = "./data/"
schemeFolder  = "./interpretative_schemes/"

textFile      = "0748Dhahabi.TarikhIslam.Shamela0035100-ara1.mARkdown"
taggingScheme = "TopTagScheme.csv"
progressRep   = "0748Dhahabi.TarikhIslam.Shamela0035100-ara1.mARkdown.TopTagSchemeProgress"
limit         = 0

testIndex(textFile, progressRep)

print("===>" + str(datetime.now() - startTime))
print("Done!")
