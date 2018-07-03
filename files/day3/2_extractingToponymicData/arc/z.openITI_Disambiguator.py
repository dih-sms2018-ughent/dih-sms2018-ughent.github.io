import re
import sys, os.path, shutil

import ara, maintenance

from datetime import datetime
startTime = datetime.now()

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
             "model": "running extrapolations from collected choices...",
             "stats": "calculating statistics on general progress",
             "save": "saving results and exiting...",
             "test": "print out the entire row of values for testing purposes"
             }

choicePrompt = """
=======================================================================================
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
    tm --- to select a `fm` ngram manually;
     s --- to `skip` this item for now (do that if you are unsure);
=======================================================================================
 model --- to model probabilities for unchecked  data
 stats --- to pring out progress statistics
  save --- to save the results and exit
=======================================================================================
"""

# ISSUES: BARQA and bi-RAQQA get confused --- not sure how to deal with them...


choicePrompt = """
=======================================================================================
     t --- to tag a true match;
    ta --- to apply `true always` to tag all instances as `ta`;
    tm --- to select a `tm` ngram manually;
   fix --- to tag a toponym that requires manual post-fixing;
     f --- to tag a false match;
    fa --- to apply `false always` to tag all instances as `fa`;
    tm --- to select a `fm` ngram manually;
     s --- to `skip` this item for now (do that if you are unsure;
=======================================================================================
 model --- to model probabilities for unchecked  data;
 stats --- to pring out progress statistics;
  save --- to save the results and exit;
=======================================================================================
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
    for k,v in dic.items():
        if v[5] == item:
            if v[9] != "t" or v[9] != "f":
                v[9] = val

def manualNgramUpdate(dic, status, item, beg, end, matchingNgram, reportValue):
    for k,v in dic.items():
        if v[5] == item:
            if v[9] != "t" or v[9] != "f":
                if matchingNgram == v[beg:end]:
                    v[9]  = status
                    v[11] = reportValue

# FUNCTION: save the dictionary
def saveDic(dic, fileName):
    reportNew = []
    for k,v in dic.items():
        reportNew.append("\t".join(v))
    with open(dataFolder+fileName, "w", encoding="utf8") as f9:
        f9.write("\n".join(reportNew))

def raqm(num):
    return("{:,}".format(num))

# FUNCTION: stats report from the dictionary
def dicStats(dic):
    stats      = {"t":0, "ta":0, "tm":0, "te":0, "fix":0, "f":0, "fa":0, "fm":0, "fe":0}
    listStatus = ["t", "ta", "tm", "te", "fix", "f", "fa", "fm", "fe"]
    for k,v in dic.items():
        if v[9] in listStatus:
            stats[v[9]] +=1
    # reporting progress:
    # - % true (details here)
    # - % false (details here)
    # - % unprocessed (details here)
    tots = len(dic)
    tAllabs = stats["t"]+stats["ta"]+stats["tm"]+stats["te"]++stats["fix"]
    tAll = '{: 10,.2f}%'.format((tAllabs/tots)*100)
    fAllabs = stats["f"]+stats["fa"]+stats["fm"]+stats["fe"]
    fAll = '{: 10,.2f}%'.format((fAllabs/tots)*100)
    totsRem = '{: 10,.2f}%'.format(((tots-tAllabs-fAllabs)/tots)*100)

    # printing the report
    os.system("clear") # commands clears the screen
    print("="*82)
    print("PROGRESS REPORT:")
    print("="*82)
    print("TRUE:   \t%s (t: %s; ta: %s; tm: %s; te: %s; fix:%s)" %  (tAll, raqm(stats["t"]), raqm(stats["ta"]), raqm(stats["tm"]), raqm(stats["te"]), raqm(stats["fix"])))
    print("FALSE:  \t%s (f: %s; fa: %s; fm: %s; fe: %s)" % (fAll, raqm(stats["f"]), raqm(stats["fa"]), raqm(stats["fm"]), raqm(stats["fe"])))
    print("="*82)
    print("REMAINS:\t%s (%s out of %s)" % (totsRem, (tots-tAllabs-fAllabs), tots))
    print("="*82)
    input()

# FUNCTION: the main function
def disambiguator(progressReport):
    with open(dataFolder+progressReport, "r", encoding="utf8") as f1:
        report = f1.read().split("\n")
        progress    = {}
        frequencies = {}
        for r in report:
            r = r.split("\t")
            progress[r[0]] = r

            # # calculating frequencies
            # listStatus = ["t", "ta", "tm", "te", "f", "fa", "fm", "fe"]
            # if r[9] not in listStatus:
            #     if r[5] in frequencies:
            #         frequencies[r[5]] += 1
            #     else:
            #         frequencies[r[5]]  = 1

    # reviewing results
    counter = 0
    # DEV: add some routine to process most frequent items first ???
    for k,v in progress.items():
        # check v[-2] value
        testValue = 0 # 0 - skip; 1 - process
        if v[9] == "t" or v[9] == "f":
            testValue = 0
        elif v[9] == "te" or v[9] == "fe":
            testValue = ran(string25)
        elif v[9] == "ta" or v[9] == "fa":
            testValue = ran(string10)
        elif v[9] == "tm" or v[9] == "fm":
            testValue = ran(string25)
        else:
            testValue = 1

        os.system("clear") # commands clears the screen
        if testValue == 1:
            # print out statistics ?
            counter += 1
            # collect data
            #print("="*88)
            #print(v[0])
            print("="*88)
            print(v[1])
            print("="*88)
            tag = re.search(r"(@TOP@[A-Za-z0-9_:]+)", v[13]).group(1)
            print("           Tag: %s" % tag)
            print("   Tagged item: %s" % v[5])
            print("Current status: %s" % v[9])
            choice = choiceCollector()
            # choices: t, ta, f, fa, s, model, stop
            if choice == "t" or choice == "f" or choice == "fix":
                v[9] = choice
            elif choice == "ta" or choice == "fa":
                v[9] = choice[0] # this, for some reason gets overwritten...
                updateDic(progress, choice, v[5])

            # collecting manually defined ngrams
            elif choice == "tm" or choice == "fm":
                c = 0
                for i in v[2:9]: # ngrams
                    c += 1
                    print ("\t%d: %s" % (c, i))
                print("="*82)
                mChoice = mChoiceCollector()
                if mChoice == "cancel":
                    pass
                else:
                    beg = int(mChoice[0])+1   #  first 1 - to align with the list in the result
                    end = int(mChoice[1])+1+1 # second 1 - to align with the python list range counting
                    print("The following ngram has been selected:")
                    print("v[%d:%d]" % (beg,end))
                    print("\t"+re.sub("\[|\]", "", " ".join(v[beg:end])))
                    input()
                    # run extrapolation from manual ngrams
                    reportValue = "v[%d:%d]@[%s:%s]#" % (beg,end,mChoice[0],mChoice[1])+":".join(v[beg:end])
                    matchingNgram = v[beg:end]
                    #manualNgramUpdate(dic, status, item, beg, end, matchingNgram, reportValue)
                    manualNgramUpdate(progress, choice, v[5], beg, end, matchingNgram, reportValue)

            # skipping this item for now
            elif choice == "s":
                pass

            # start a modeling function (analysis of ngrams)
            elif choice == "model":
                # run modeling function
                pass

            # prints out progress statistics
            elif choice == "stats":
                dicStats(progress)

            # breaks the loop, saves results, exits
            elif choice == "save":
                break
            elif choice == "test":
                print("="*82)
                print("\n".join(v))
                print("="*82)
                input()
            else:
                pass

            if counter % 50 == 0:
                saveDic(progress, progressReport)

    saveDic(progress, progressReport)
    dicStats(progress)

dataFolder    = "./data/"
schemeFolder  = "./interpretative_schemes/"

textFile      = "0578IbnBashkuwal.Sila.Shamela0022788-ara1.mARkdown"
taggingScheme = "TopTagScheme.csv"
progressRep   = textFile+".TopTagSchemeProgress"

disambiguator(progressRep)
print("===>" + str(datetime.now() - startTime))
print("Done!")
