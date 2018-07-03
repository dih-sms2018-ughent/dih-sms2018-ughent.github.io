import re
import sys, os.path, shutil

import ara, maintenance

from datetime import datetime
startTime = datetime.now()

def listTest(listVar, indexPos):
    try:
        var = listVar[indexPos]
        if var == "":
            var = "NOITEM"
    except:
        var = "NOITEM"
    return(var)


# tagging with a taggingScheme
def tagText(textFile, taggingScheme, limit, reflow):
    print("===>now, starting processing the file\n\t\t%s" % textFile)
    print("===>" + str(datetime.now() - startTime))

    # load tagging scheme
    with open(schemeFolder+taggingScheme, "r", encoding="utf8") as f1:
        tags = f1.read().split("\n")[1:]
        count = len(tags)

        tagPattern = re.search("@\w+@", tags[1]).group(0)
        print("\tTag pattern is: %s" % tagPattern)

    # loading process report
    suffix = taggingScheme.split(".")[0]
    reportDA = textFile+"."+suffix+"Progress"

    reportDic  = {}
    if os.path.isfile(generated+reportDA):
        with open(generated+reportDA, "r", encoding="utf8") as f1a:
            reportData = f1a.read().split("\n")
            for r in reportData:
                r = r.split("\t")
                reportDic[r[0]] = r

    else:
        with open(generated+reportDA, "w", encoding="utf8") as f9a:
            f9a.write("")

    # loading search report
    suffix = taggingScheme.split(".")[0]
    reportSE = textFile+"."+suffix+"Search"
    if os.path.isfile(generated+reportSE):
        with open(generated+reportSE, "r", encoding="utf8") as f1a:
            reportSearch = f1a.read().split("\n")
    else:
        with open(generated+reportSE, "w", encoding="utf8") as f9a:
            f9a.write("")
        reportSearch = []


    # process text
    splitter = "#META#Header#End#"

    # check if the tagged file already exists
    taggedFile = generated+textFile+".tagged"
    if not os.path.isfile(taggedFile):
        shutil.copyfile(dataFolder+textFile, taggedFile)

    # open tagged file
    with open(taggedFile, "r", encoding="utf8") as f1:
        t = f1.read().split(splitter)

        text0 = t[0]
        text1 = t[1]

        text1 = text1.replace("\n~~", " ")
        text1 = re.sub(" +", " ", text1)

        print("===>now, starting tagging: %d new items will be processed..." % limit)
        print("===>" + str(datetime.now() - startTime))

        countUp = 0
        for t in tags:
            t = t.split("\t")
            if t[3] in reportSearch:
                print("\t\tAlready processed: %s" % t[3])
                count = maintenance.counterDown(count, 100, startTime)
            else:
                print("\tProcessing: %s" % t[3])
                res = re.findall(r"\b(%s)\b" % t[2], text1)
                res = list(set(res)) # this is important, as it removes duplicates
                if res != []:
                    for r in res:
                        regePattern = "%s_%s" % (t[1], r.replace(" ", "_"))
                        text1 = re.sub(r"\b%s\b" % r, regePattern, text1)
                reportSearch.append(t[3])

                count = maintenance.counterDown(count, 100, startTime)

                countUp += 1
                if countUp == limit:
                    break

    # save results
    print("===>now, saving tagged file...")
    print("===>" + str(datetime.now() - startTime))
    with open(generated+textFile+".tagged", "w", encoding="utf8") as f9:
        f9.write(text0+"\n"+splitter+"\n"+text1)

    # generate/update report
    #arabic     = "[ٱء-ي]+"
    #altSpaceRE = "[^ٱء-ي.\n]+"
    altSpaceRE = "[^ٱء-ي]+"
    arWord = "\b[ٱء-ي]+[^ٱء-ي]+"
    tag    = r"@[A-Z]+@[A-Za-z0-9_:]+#_"
    # -{1,5}[TAGGED]+{1,5}
    complete = r"((\b[ٱء-ي]+[^ٱء-ي]+){1,5}@[A-Z]+@[A-Za-z0-9_:]+#\w+[^ٱء-ي]+(\b[ٱء-ي]+[^ٱء-ي]+){1,5})"

    # generate, update, save progress report
    TL = text1.replace("\n", "::n::")
    TL = TL.split(" ")
    print("===>now, processing tagged results (%s)..." %  "{:,}".format(len(TL)))

    for i in range(0, len(TL)):
        if TL[i].startswith(tagPattern):
            currentTag = re.search(r"(%s)" % tag, TL[i]).group(1)
            match  = " ".join(TL[i-7:i+7]).strip()
            before = " ".join(TL[i-7:i]).strip()
            middleTag = TL[i].strip()

            after  = " ".join(TL[i+1:i+7]).strip()

            before = re.sub(altSpaceRE, " ", before).strip()
            middle = "[[%s]]" % re.search(r"(%s)(\w+)" % tag, middleTag).group(2)
            after  = re.sub(altSpaceRE, " ", after).strip()

            before = ara.normalizeArabicLight(before)
            middle = ara.normalizeArabicLight(middle)
            after  = ara.normalizeArabicLight(after)

            before = before.split(" ")
            after  = after.split(" ")

            keyNew = " ".join(before[-5:]+[middle]+after[:5])

            if keyNew not in reportDic:
                display = re.sub(r"(%s)(\w+)" % tag, r"[[\2]]", match)
                display = re.sub("[A-Za-z]+", "", display)

                # # for testing
                # print("=====")
                # print(keyNew)
                # print(match)
                # print(display)
                # print(before)
                # print(middle)
                # print(after)
                # print("=====")
                # input()

                ng0 = listTest(before, -3) #left[-3]
                ng1 = listTest(before, -2) #left[-2]
                ng2 = listTest(before, -1) #left[-1]
                tagged = middle
                ng3 = listTest(after, 0) #right[0]
                ng4 = listTest(after, 1) #right[1]
                ng5 = listTest(after, 2) #right[2]

                val = [keyNew, display, ng0, ng1, ng2, tagged, ng3, ng4, ng5, "0", "0", "0", str(i), middleTag]

                #print("====\n"+"\n".join(val)+"\n====")
                reportDic[keyNew] = val
                #input()

            # if it is in the dictionary: update index position
            else:
                reportDic[keyNew][12] = str(i)

    # save report
    toSave = []
    for k,v in reportDic.items():
        toSave.append("\t".join(v))

    toSave = [x for x in toSave if x != ""]
    print("="*25+"\n== %d results in the report...\n" % len(toSave)+"="*25)
    with open(generated+reportDA, "w", encoding="utf8") as f9a:
        f9a.write("\n".join(toSave))

    # save SearchReport
    reportSearch = [x for x in reportSearch if x != ""]
    with open(generated+reportSE, "w", encoding="utf8") as f9a:
        f9a.write("\n".join(reportSearch))

    # reflow file
    if reflow == "reflow":
        print("===>now, reflowing the file...")
        print("===>" + str(datetime.now() - startTime))
        maintenance.reFlowFile(generated+textFile+".tagged")

dataFolder    = "./data/"
schemeFolder  = "./interpretative_schemes/"
generated = "./generated/"

with open("_fileToEdit.txt", "r", encoding="utf8") as f1:
    textFile = f1.read()

taggingScheme = "TopTagScheme.csv"
limit         = 0

reflow = "reflow" # to reflow the text
reflow = "do not reflow" # or, actually, anything else, not to reflow

tagText(textFile, taggingScheme, limit, reflow)
print("===>" + str(datetime.now() - startTime))
print("Done!")
