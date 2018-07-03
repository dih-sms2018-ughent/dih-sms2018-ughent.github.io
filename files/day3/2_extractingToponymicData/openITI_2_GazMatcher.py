import re, textwrap
import sys, os.path, shutil

import ara, maintenance

# the script is designed to run matching against a gazetteer of terms.
# instead of RE, gazetteer shoud have all possible versions

from datetime import datetime

startTime = datetime.now()

# global variables
splitter = "#META#Header#End#"
arRa = re.compile("^[ذ١٢٣٤٥٦٧٨٩٠ّـضصثقفغعهخحجدًٌَُلإإشسيبلاتنمكطٍِلأأـئءؤرلاىةوزظْلآآ]+$")
altSpaceRE = "[^ٱء-ي]+"


# 1. loading load gazetteer


def listTest(listVar, indexPos):
    try:
        var = listVar[indexPos]
        if var == "":
            var = "NOITEM"
    except:
        var = "NOITEM"
    return (var)


# 1. loading load gazetteer
def loadGazetteer(gazetteer):
    print("=" * 82)
    print("===>now, loading the gazetteer\n\t\t%s" % gazetteer)
    print("===>" + str(datetime.now() - startTime))

    with open(schemeFolder + gazetteer, "r", encoding="utf8") as f1:
        tags = f1.read().split("\n")[1:]
        count = len(tags)

        gazDic = {}
        for t in tags:
            t = t.split("\t")
            gazDic[t[0]] = t
            # input(gazDic)
    print("%d items in the gazetteer..." % len(gazDic))
    print("===>" + str(datetime.now() - startTime))
    print("=" * 82)
    return (gazDic)


# tagging with a taggingScheme

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

def matchGazetteer(textFile, gazetteer):
    print("===>now, starting processing the file\n\t\t%s" % textFile)
    print("===>" + str(datetime.now() - startTime))

    gaz = loadGazetteer(gazetteer)

    # loading process report
    suffix = gazetteer.split(".")[0]
    reportDA = textFile + "." + suffix + "progressReport"

    reportDic = {}
    if os.path.isfile(generated + reportDA):
        with open(generated + reportDA, "r", encoding="utf8") as f1a:
            reportData = f1a.read().split("\n")
            for r in reportData:
                r = r.split("\t")
                reportDic[r[0]] = r
    else:
        with open(generated + reportDA, "w", encoding="utf8") as f9a:
            f9a.write("")

    # open text file
    with open(dataFolder + textFile, "r", encoding="utf8") as f1:

        t = f1.read().split(splitter)
        text0 = t[0]
        text1 = t[1]

        text1 = text1.replace("\n~~", " ")
        text1 = re.sub(" +", " ", text1)

        text1 = text1.replace("\n", "::@::")

        print("===>" + str(datetime.now() - startTime))
        print("===> splitting text...")
        altSpaceRE = "[^ٱء-ي]+"
        tl = re.split(r"(%s)" % altSpaceRE, text1)
        print("===>" + str(datetime.now() - startTime))

        length = len(tl)
        print("===> looping through %s items of a text..." % "{:,}".format(len(tl)))
        for i in range(0, len(tl) + 1):
            # print("".join(tl[i:i+10]))
            # 1,-2,3,-4,5,-6,7,-8,9,-10,11
            m1 = ara.normalizeArabicLight("".join(tl[i:i + 1:2]))
            m2 = ara.normalizeArabicLight("".join(tl[i:i + 3:2]))
            m3 = ara.normalizeArabicLight("".join(tl[i:i + 5:2]))
            m4 = ara.normalizeArabicLight("".join(tl[i:i + 7:2]))

            mList = [m1, m2, m3, m4]

            if i % 500000 == 0:
                print("\t\t%s processed..." % "{:,}".format(i))
            if i % 1000000 == 0:
                print("\t===>\t" + str(datetime.now() - startTime))

            for m in mList:
                if m in gaz:
                    match = " ".join(
                        [tl[i - 8], tl[i - 6], tl[i - 4], tl[i - 2], "[[%s]]" % tl[i], tl[i + 2], tl[i + 4], tl[i + 6],
                         tl[i + 8]])
                    display = "".join(tl[i - 25:i] + ["[[%s]]" % tl[i]] + tl[i + 1:i + 25])
                    display = re.sub("[a-zA-Z0-9]", "", display)

                    ng1 = ara.normalizeArabicLight(tl[i - 6])
                    ng2 = ara.normalizeArabicLight(tl[i - 4])
                    ng3 = ara.normalizeArabicLight(tl[i - 2])
                    ng4 = ara.normalizeArabicLight(tl[i])  # TAGGED
                    ng5 = ara.normalizeArabicLight(tl[i + 2])
                    ng6 = ara.normalizeArabicLight(tl[i + 4])
                    ng7 = ara.normalizeArabicLight(tl[i + 6])
                    status = "0"
                    probability = "0"
                    ngram = "00"
                    position = str(i)
                    middleTag = gaz[m][1]
                    gazForm = gaz[m][2]

                    key = match
                    val = [match, display, ng1, ng2, ng3, ng4, ng5, ng6, ng7, status, probability, ngram, position,
                           middleTag, gazForm]

                    if key in reportDic:
                        # some other fields must be updated
                        reportDic[key][1] = display
                        reportDic[key][12] = position
                        reportDic[key][13] = middleTag
                    else:
                        reportDic[key] = val


                        # print("tl[%d] = %s" % (i, tl[i]))
                        # print(match)
                        # print(display)
                        # print("===")
                        # print("\n".join([ng1,ng2,ng3,ng4,ng5,ng6,ng7]))
                        # print("===")
                        # print(i)
                        # print(m)
                        # print("".join(tl[i-10:i+10]))
                        # print(gaz[m])
                        #
                        # input("=^=^=")

        print("===>all items processed: %d items collected..." % len(reportDic))
        print("===>" + str(datetime.now() - startTime))
        # input("STOPPED...")

    # generate/update report
    # arabic     = "[ٱء-ي]+"
    # altSpaceRE = "[^ٱء-ي.\n]+"
    altSpaceRE = "[^ٱء-ي]+"
    arWord = "\b[ٱء-ي]+[^ٱء-ي]+"
    tag = r"@[A-Z]+@[A-Za-z0-9_:]+#_"
    # -{1,5}[TAGGED]+{1,5}
    complete = r"((\b[ٱء-ي]+[^ٱء-ي]+){1,5}@[A-Z]+@[A-Za-z0-9_:]+#\w+[^ٱء-ي]+(\b[ٱء-ي]+[^ٱء-ي]+){1,5})"

    # save report
    toSave = []
    for k, v in reportDic.items():
        toSave.append("\t".join(v))

    toSave = [x for x in toSave if x != ""]
    print("=" * 25 + "\n== %s results in the report...\n" % "{:,}".format(len(toSave)) + "=" * 25)
    with open(generated + reportDA, "w", encoding="utf8") as f9a:
        f9a.write("\n".join(toSave))


dataFolder = "./data/"
schemeFolder = "./interpretative_schemes/"
generated = "./generated/"

textFile  = "0578IbnBashkuwal.Sila.Shamela0022788-ara1.mARkdown"
gazetteer = "ToponymsML.csv"

limit = 0

matchGazetteer(textFile, gazetteer)
print("===>" + str(datetime.now() - startTime))
print("Done!")
