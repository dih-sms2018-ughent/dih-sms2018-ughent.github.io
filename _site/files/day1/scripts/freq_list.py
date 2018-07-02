# This script generates a frequency list out of a text file.

import re

##################################
# Operation 0: clean Arabic ######
##################################

# deNoise(text) deletes short vowels from Arabic text
def deNoise(text):
    noise = re.compile(""" ّ    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                             ـ     # Tatwil/Kashida
                         """, re.VERBOSE)
    text = re.sub(noise, '', text)
    return(text)

def normalizeArabicLight(text):
    text = re.sub("[إأٱآا]", "ا", text)
    text = re.sub("[يى]ء", "ئ", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("(ؤ)", "ء", text)
    text = re.sub("(ئ)", "ء", text)
    #text = re.sub("(ء)", "", text)
    #text = re.sub("(ة)", "ه", text)
    return(text)

##########################################
# Operation 1: Generating freq List ######
##########################################

def freqList(sourceFolder, targetFolder, fileToProcess):

    fDictionary = {}

    with open(sourceFolder+fileToProcess, "r", encoding = "utf8") as f1:
        text = f1.read()

        text = deNoise(text)
        text = normalizeArabicLight(text)

        for r in re.findall(r"\b\w+\b", text):
            if r in fDictionary:
                fDictionary[r] += 1
            else:
                fDictionary[r]  = 1

    fList = []

    for k,v in fDictionary.items():
        fList.append("%09d\t%s" % (v,k))

    fList = sorted(fList, reverse=True)

    with open(targetFolder+"%s.freqList" % fileToProcess, "w", encoding="utf8") as f9:
        f9.write("\n".join(fList))

    print("="*80)
    print("Top 100 words are:")
    print("="*80)
    print("\n".join(fList[:100]))


##########################################
# Parameters: Generating freq List #######
##########################################

sourceFolder = "../sample_texts/"
targetFolder = "../sample_freqLists/"

fileToProcess   = "0726Yunini.DhaylMiratZaman.JK010379-ara1"

# RUNNING ################################

freqList(sourceFolder, targetFolder, fileToProcess)


    

        


