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

### timing reportLines
##print("\tnow, starting processing the file\n\t\t%s" % textFile)
##print("===>" + str(datetime.now() - startTime))

choiceDic = {"t": "item is saved as `true`...",
             "ta": "item is saved as `true always` (some will be shown for review)...",
             "tm": "manually selecting true ngram (some will be shown for review)...",
             "fix": "the item is toponym, but requires fixing",
             "f": "item is saved as `false`...",
             "fa": "item is saved as `false always` (some will be shown for review)...",
             "fm": "manually selecting false ngram (some will be shown for review)...",
             # other choices
             "s": "skipping the item...",
             "skip" : "skipping all other instances of current result (temporarily)...",
             "model": "running extrapolations from collected choices...",
             "stats": "calculating statistics on general progress",
             "save": "saving results and exiting...",
             "test": "printing out the entire row of values for testing purposes",
             "reset": "reseting results for the selected item"
             }

choicePrompt = """
========================================================================================
     t --- to tag a true match;
    ta --- to apply `true always` to tag all instances as `ta`;
           this can be used for items that are not ambiguous; for example
           if you tag toponyms, `Baġdād` cannot be anything else but `Baġdād`, so
           all instances of `Baġdād` can be automatically interpreted as `true always`;
           (cases like `Sind` or `Hind` have to be resolved one by one, or modelled)
           10% of `ta` will still be shown, just in case;
    tm --- to select a `tm` ngram manually;
   fix --- to tag a toponym that requires manual post-fixing (wrong URI, for example);
     f --- to tag a false match;
    fa --- to apply `false always` to tag all instances as `fa`;
           this can be used for items that are extremely ambiguous; for example
           if you tag toponyms, `Bih` is almost unlikely to be a reference to a place
           10% of `fa` will still be shown, just in case;
    fm --- to select a `fm` ngram manually;
     s --- to `skip` this item for now (do that if you are unsure);
========================================================================================
 model --- to model probabilities for unchecked  data
 stats --- to pring out progress statistics
  save --- to save the results and exit
========================================================================================
 reset --- to reset existing results for the item (confirmation will be required)
========================================================================================
"""


choicePrompt = """
========================================================================================
     t --- to tag a true match;
    ta --- to apply `true always` to tag all instances as `ta`;
    tm --- to select a `tm` ngram manually;
   fix --- to tag a toponym that requires manual post-fixing;
     f --- to tag a false match;
    fa --- to apply `false always` to tag all instances as `fa`;
    fm --- to select a `fm` ngram manually;
     s --- to `skip` this item for now (do that if you are unsure;
  skip --- to `skip` all instances of the currect result (temporarily)
========================================================================================
 model --- to model probabilities for unchecked  data;
 stats --- to pring out progress statistics;
  save --- to save the results and exit;
========================================================================================
 reset --- to reset existing results for the item (confirmation will be required)
========================================================================================
"""

choicePrompt = """
========================================================================================
     t --- to tag a true match;                  f --- to tag a false match;
    ta --- to apply `true always`;              fa --- to apply `false always`
    tm --- to select a `tm` ngram manually;     fm --- to select a `fm` ngram manually;
========================================================================================
     s --- to `skip` this item;               skip --- to `skip` all instances
 model --- to model probabilities            stats --- to pring out progress statistics;
 reset --- to reset results for the item      save --- to save the results and exit;
========================================================================================
"""

def choiceCollector():
    print(choicePrompt)
    choice = input("Type one of the offered choices: ")
    choice = choice.strip().lower()
    while choice not in choiceDic:
        choice = input("Not a valid choice! Try again: ")
        choice = choice.strip().lower()
    print("\t%s" % choiceDic[choice])
    return(choice)

def mChoiceCollector():
    mChoices = ["14","15","16","17","24","25","26","27","34","35","36","37","45","46","47","cancel"]
    print("Type the beginning and the end of the ngram you want to include or exclude.")
    print("Possible choices: %s" % ', '.join(mChoices))
    choice = input("Type one of the suggested choices: ")
    choice = choice.strip()
    while choice not in mChoices:
        choice = input("Try again (must be two numbers or `cancel`!): ")
        choice = choice.strip()
    return(choice)

import random
def ran(string):
    ranVar = "" + ''.join(random.choice(string) for i in range(1))
    return(ranVar)

# variables for ran(string) function
string10 = "1"*10+"0"*90
string20 = "1"*20+"0"*80
string25 = "1"*25+"0"*75
string40 = "1"*40+"0"*60
string50 = "1"*50+"0"*50

## FUNCTION to check if ran() with string variables will work for probabilities
## it works: the highler the number of repetitions, the more precise the distribution
##def randomTest(rep, ranString):
##    dic = {"1":0, "0":0}
##    count = rep
##    while count != 0:
##        count -= 1
##        dic[ran(ranString)] +=1
##    for k,v in dic.items():
##        test = int(v/rep*100)
##        print("%s: %d percent" % (k,test))
##
##randomTest(100, "1"*2+"0"*8)

# v[-2] = status > t, f, ta, te, fe, 0

# FUNCTION: update main dic with `ta` and `fa`
def updateDic(dic, val, item):
    count = 0
    for k,v in dic.items():
        if v[5] == item:
            if val == "reset":
                v[9] = "reset"
                v[9] = "0"
            else:
                if v[9] != "t" or v[9] != "f":
                    v[9] = val
            count +=1
    print("="*82)
    print("==> %d items identified..." % count)
    print("="*82)
    input()

def manualNgramUpdate(dic, status, item, beg, end, matchingNgram, reportValue):
    count = 0
    for k,v in dic.items():
        if v[5] == item:
            if v[9] != "t" or v[9] != "f":
                if matchingNgram == v[beg:end]:
                    v[9]  = status
                    v[11] = reportValue
                    count += 1
    print("="*82)
    print("==> %d items identified..." % count)
    print("="*82)
    input()

# FUNCTION: save the dictionary
def saveDic(dic, fileName):
    reportNew = []
    for k,v in dic.items():
        reportNew.append("\t".join(v))
    with open(generated+fileName, "w", encoding="utf8") as f9:
        f9.write("\n".join(reportNew))

# formatting long numbers
def raqm(num):
    return("{:,}".format(num))

# generates all meaningful ngrams from a given dic[val]
def generateAllNgrams(val):
    ngramList = []
    num = [[1,4],[1,5],[1,6],[1,7],[2,4],[2,5],[2,6],[2,7],[3,4],[3,5],[3,6],[3,7],[4,5],[4,6],[4,7]]
    newList = list(val)
    newList[4+1] = "ـإسمالمكانـ"
    for n in num:
        ng = "%d:%d@%s" % (n[0]+1, n[1]+2, ":".join(newList[n[0]+1:n[1]+2]))
        ngramList.append(ng)
    return(ngramList)

# modeling results, using ngrams
def modelingResults(dic, progressRep):
    data = {}
    pos = ["t", "ta", "tm"]
    neg = ["f", "fa", "fm"]
    for k,v in dic.items():
        if v[9] in pos+neg:
            ngramList = generateAllNgrams(v)
            for n in ngramList:
                if n in data:
                    data[n][v[9][:1]] += 1
                else:
                    data[n] = {"t":0, "f":0}
                    data[n][v[9][:1]] += 1
    # generating model
    model = {}
    freqs = []
    for k,v in data.items():
        # vNew : key, pos, neg, total, precision
        key = k
        tru = v["t"]
        fls = v["f"]
        tot = tru+fls
        prc = "{0:.3f}".format(tru/tot)
        model[key] = [key, str(tru), str(fls), str(tot), str(prc)]
        freqs.append(tot)

    import numpy as np
    cutoff = np.percentile(freqs, 50)
    print("cutoff value: %s" % "{0:.3f}".format(cutoff))
    # applying model
    for k,v in dic.items():
        #print(v[9])
        if v[9] not in (pos+neg):
            ngramList = generateAllNgrams(v)
            for n in ngramList:
                if n in model:
                    #print(model[n])
                    prc = float(model[n][4])

                    if prc >= 0.9:
                        sts = "te" # true, extrapolated
                    elif prc <= 0.1:
                        sts = "fe" # false, extrapolated
                    else:
                        sts = "model"

                    if float(v[10]) < prc:
                        v[9]  = sts
                        v[10] = str(prc)
                        v[11] = n

    # save model
    modelList = []
    for k,v in model.items():
        if int(v[3]) > 1:
            modelList.append("\t".join(v))
    print("Saving a model with %s ngrams" % "{:,}".format(len(modelList)))
    with open(generated+progressRep+"Model", "w", encoding="utf8") as f9:
        f9.write("\n".join(modelList))
    input("Press any button to continue...")

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


# FUNCTION: stats report from the dictionary
def dicStats(dic, progressReport):
    stats      = {"t":0, "ta":0, "tm":0, "te":0, "fix":0, "f":0, "fa":0, "fm":0, "fe":0}
    listStatus = ["t", "ta", "tm", "te", "fix", "f", "fa", "fm", "fe"]
    for k,v in dic.items():
        if v[9] in listStatus:
            stats[v[9]] +=1
    # reporting progress:
    tots = len(dic)
    tAllabs = stats["t"]+stats["ta"]+stats["tm"]+stats["te"]++stats["fix"]
    tAll = '{: 10,.2f}%'.format((tAllabs/tots)*100)
    fAllabs = stats["f"]+stats["fa"]+stats["fm"]+stats["fe"]
    fAll = '{: 10,.2f}%'.format((fAllabs/tots)*100)
    totsRem = '{: 10,.2f}%'.format(((tots-tAllabs-fAllabs)/tots)*100)
    totsPro = '{: 10,.2f}%'.format(((tAllabs+fAllabs)/tots)*100)

    # printing the report
    displayReport = ""
    displayReport += "\n" + "="*82
    displayReport += "\n" + "FILE: %s" % progressReport
    displayReport += "\n" + "PROGRESS REPORT — %s" % datetime.now().strftime("%Y-%m-%d %H:%M")
    displayReport += "\n" + "="*82
    displayReport += "\n" + "TRUE      : %s (t: %s; ta: %s; tm: %s; te: %s; fix:%s)" %  (tAll, raqm(stats["t"]), raqm(stats["ta"]), raqm(stats["tm"]), raqm(stats["te"]), raqm(stats["fix"]))
    displayReport += "\n" + "FALSE     : %s (f: %s; fa: %s; fm: %s; fe: %s)" % (fAll, raqm(stats["f"]), raqm(stats["fa"]), raqm(stats["fm"]), raqm(stats["fe"]))
    displayReport += "\n" + "="*82
    displayReport += "\n" + "PROCESSED : %s (%s out of %s)" % (totsPro, raqm(tAllabs+fAllabs), raqm(tots))
    displayReport += "\n" + "REMAINS   : %s (%s out of %s)" % (totsRem, raqm(tots-tAllabs-fAllabs), raqm(tots))
    displayReport += "\n" + "="*82

    os.system("clear") # commands clears the screen
    input(displayReport)

    # save/append displayReport
    displayReportFile = generated + progressReport + "Stats"
    reportText = ""
    if os.path.isfile(displayReportFile):
        with open(displayReportFile, "r", encoding="utf8") as f1:
            reportText = f1.read()
    with open(displayReportFile, "w", encoding="utf8") as f9:
        f9.write(displayReport + "\n\n" + reportText)

# FUNCTION: the main function
def disambiguator(progressReport, order):
    with open(generated+progressReport, "r", encoding="utf8") as f1:
        report = f1.read().split("\n")
        progress    = {}
        servingDic  = {}
        for r in report:
            r = r.split("\t")
            progress[int(r[12])] = r

            # to show results grouped by items
            if r[5] in servingDic:
                servingDic[r[5]].append(r[12])
            else:
                servingDic[r[5]] = [r[12]]

    # reviewing results
    counter = 0
    orderedList = []
    for k,v in servingDic.items():
        val = "%010d#%s" % (len(v), ":".join(v))
        orderedList.append(val)
    # order list by decreasing frequencies
    if order == "ordered":
        orderedList = sorted(orderedList, reverse=True)

    orderedListNew = []
    for ll in orderedList:
        #print(ll)
        ll = ll.split("#")[1].split(":")
        for l in ll:
            orderedListNew.append(int(l))

    # assign a variable to skip, temporarily (progress[o][5])
    # this is mostly for sorted list, to switch to the next item
    skipValue = ""

    for o in orderedListNew:
        testValue = 0 # 0 - skip; 1 - process
        if progress[o][9] == "t" or progress[o][9] == "f":
            testValue = ran(string10)
        elif progress[o][9] == "te" or progress[o][9] == "fe":
            testValue = ran(string25)
        elif progress[o][9] == "ta" or progress[o][9] == "fa":
            testValue = ran(string10)
        elif progress[o][9] == "tm" or progress[o][9] == "fm":
            testValue = ran(string25)
        elif skipValue == progress[o][5]:
            testValue = 0
        else:
            testValue = 1

        # start processing...
        if testValue == 1:
            os.system("clear") # commands clears the screen
            # print out statistics ?
            counter += 1
            # collect data
            #print("="*88)
            #print(v[0])
            print("="*88)
            #print("ا\t" + "\nا\t".join(textwrap.wrap(v[1], 50))) # "\n".join(textwrap.wrap(v[1], 82))
            #print("="*88)
            #print("\n".join(textwrap.wrap(v[1], 50))) # "\n".join(textwrap.wrap(v[1], 82))
            #print("="*88)
            print(progress[o][1])
            # print("="*88)
            # displayTemp = progress[o][1]
            # displayTemp = "\n".join(textwrap.wrap(displayTemp, 88))
            # displayTemp = re.sub("::@::#", "\n", displayTemp)
            # displayTemp = re.sub("\.", "،،", displayTemp)
            # displayTemp = re.sub("[\$]", "", displayTemp)
            # print(displayTemp) # "\n".join(textwrap.wrap(displayTemp, 70))
            print("="*88)
            tag = progress[o][13]
            print("           Tag: %s" % tag)
            print("   Tagged item: %s" % progress[o][5])
            print("Gazetteer form: %s" % progress[o][14])
            print("Current status: %s" % progress[o][9])
            print("   Probability: %s" % progress[o][10])
            print("         Ngram: %s" % progress[o][11])
            print("      Position: %s" % o)
            choice = choiceCollector()
            # choices: t, ta, f, fa, s, model, stop
            if choice == "t" or choice == "f" or choice == "fix":
                progress[o][9] = choice
            elif choice == "ta" or choice == "fa":
                progress[o][9] = choice[0] # this, for some reason gets overwritten...
                updateDic(progress, choice, progress[o][5])

            # collecting manually defined ngrams
            elif choice == "tm" or choice == "fm":
                c = 0
                for i in progress[o][2:9]: # ngrams
                    c += 1
                    if c == 4:
                        print ("\t> %d: %s" % (c, i))
                    else:
                        print ("\t  %d: %s" % (c, i))
                print("="*82)
                mChoice = mChoiceCollector()
                if mChoice == "cancel":
                    pass
                else:
                    beg = int(mChoice[0])+1   #  first 1 - to align with the list in the result
                    end = int(mChoice[1])+1+1 # second 1 - to align with the python list range counting
                    print("The following ngram has been selected:")
                    print("progress[o][%d:%d]" % (beg,end))
                    print("\t"+re.sub("\[|\]", "", " ".join(progress[o][beg:end])))
                    #input()
                    # run extrapolation from manual ngrams
                    reportValue = "v[%d:%d]@[%s:%s]#" % (beg,end,mChoice[0],mChoice[1])+":".join(progress[o][beg:end])
                    matchingNgram = progress[o][beg:end]
                    #manualNgramUpdate(dic, status, item, beg, end, matchingNgram, reportValue)
                    manualNgramUpdate(progress, choice, progress[o][5], beg, end, matchingNgram, reportValue)

            # skipping this item for now
            elif choice == "s":
                pass

            # start a modeling function (analysis of ngrams)
            elif choice == "model":
                modelingResults(progress, progressRep)
                dicStats(progress, progressReport)

            # prints out progress statistics
            elif choice == "stats":
                dicStats(progress, progressReport)

            # breaks the loop, saves results, exits
            elif choice == "save":
                break
            elif choice == "reset":
                print("WARNING! Classification results for the selected item (%s) are about to be reset!" % progress[o][5])
                choiceConfirmation = input("Please, confirm by typing `reset` again:")
                if choiceConfirmation == "reset":
                    updateDic(progress, choice, progress[o][5])
                pass
            elif choice == "test":
                print("="*82)
                print("\n".join(v))
                print("="*82)
                input()
            elif choice == "skip":
                skipValue = progress[o][5]
            else:
                pass

            if counter % 10 == 0:
                print("===> Saving...")
                saveDic(progress, progressReport)
                input("===> Any button to continue...")

    saveDic(progress, progressReport)
    dicStats(progress, progressReport)

dataFolder    = "./data/"
schemeFolder  = "./interpretative_schemes/"
generated     = "./generated/"

textFile      = "0578IbnBashkuwal.Sila.Shamela0022788-ara1.mARkdown"
taggingScheme = "ToponymML.csv"
progressRep   = textFile+".ToponymsMLprogressReport"

disambiguator(progressRep, "ordered")
print("===>" + str(datetime.now() - startTime))
print("Done!")
