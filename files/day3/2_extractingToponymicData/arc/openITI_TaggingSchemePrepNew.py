import re, sys

sys.path.append("/Users/romanov/GitProjects/a.UCA_Centennial/OpenArabic/pyoa/pyoa/")
import ara, maintenance

from datetime import datetime
startTime = datetime.now()

# GENERATES SIMPLIFIED TAGGING SCHEMES FROM MORE ROBUST INTERPRETATIVE SCHEMES
# STRUCTURE: Item (normalized, in all possible formes); TAG(S) (URI(s)); normative form

# 0. Generate the list of prefixes and suffuxes for [TOPONYMS] and [NISBAS]
#    - save into: ToponymML.csv; NisbaML.csv (ML: matching list)
# 1. CONVERT TOPONYMIC DATA FOR INTO A TAGGING SCHEME
#    - Item (normalized, in all possible formes); TAG(S) (URI(s)); normative form
# 2. CONVERT NISBA DATA FOR INTO A TAGGING SCHEME
#    - Item (normalized, in all possible formes); TAG(S) (URI(s)); normative form

# 0. Generate the list of prefixes and suffuxes for [TOPONYMS] and [NISBAS]
topPrefixFile = "./interpretative_schemes/toponymPrefixes.csv"
def toponymPS(file):
    regex = "أذربيجان|قرطبة|بغداد|نيسابور|الكوفة|البصرة|دمشق|إصبهان|الأندلس|سمرقند|طليطلة|شيراز"
    regex = ara.deNormalize(regex)
    with open(file, "r", encoding="utf8") as f1:
        text = f1.read()
        res = re.findall(r"(\w+)(%s)\b" % regex, text)
        resNew = {}
        for r in res:
            #input(r)
            rn = r[0]+"___"
            if rn in resNew:
                resNew[rn] += 1
            else:
                resNew[rn]  = 1

        fL = []
        num = 0
        for k,v in resNew.items():
            fL.append("%010d\t%s" % (v,k))
            num += v

        print(len(fL))
        print(num)
        with open(topPrefixFile, "w", encoding="utf8") as f9:
            f9.write("\n".join(sorted(fL, reverse=True)))
    print("toponymPS() is done!")

#toponymPS("./data/0748Dhahabi.TarikhIslam.Shamela0035100-ara1.mARkdown")

def nisbaPS():
    pass


# 1. CONVERT TOPONYMIC DATA FOR INTO A TAGGING SCHEME
#    - applies custom RE (most common prefixes with toponyms) + deNormalization

excludeTopURIs = ["ABKHAN_483E408N_R", "ABYAYN_449E131N_R", "AHWAZ_486E313N_R", "ASFUZAR_621E332N_R",
               "ASKARMUKRAM_488E316N_R", "ATRIB_311E304N_R", "ATTAR_423E171N_R",
               "BAGHLAN_687E362N_R", "BAGHNIN_650E327N_R", "BAJA_078W380N_R",
               "BAJJANA_024W369N_R", "BALANSIYYA_004W394N_R", "BALKH_668E367N_R",
               "BAMIYAN_678E348N_R", "BARQA_208E323N_R", "BATALYUS_069W388N_R",
               "BISHLANK_648E326N_R", "BUKHARA_644E398N_R", "BUSANJ_614E343N_R",
               "BUSHTAFRUSH_592E361N_R", "BUST_643E313N_R", "DAMSIS_312E308N_R",
               "DAMTH_447E141N_R", "DAWRAQ_489E308N_R", "DHIMAR_443E145N_R",
               "GHAZNA_684E335N_R", "HAMADHAN_485E347N_R", "HARA_621E343N_R",
               "HAWMAZUTT_497E310N_R", "HIRDA_427E152N_R", "HURMUZFARRAH_616E376N_R",
               "ISBAHAN_516E326N_R", "ISBIJAB_697E422N_R", "ISHBILIYYA_059W374N_R",
               "JABALBAHRA_362E352N_R", "JABALSANIR_358E334N_R", "JANAD_441E136N_R",
               "JAYZAN_498E308N_R", "JUBLAN_436E142N_R", "JUNDAYSABUR_485E322N_R",
               "JURZUWAN_658E358N_R", "KAMIN_531E301N_R", "KARAJ_495E338N_R",
               "KARWAN_718E414N_R", "KHAYWAN_440E162N_R", "KHUSHUNUBA_079W370N_R",
               "KISHSH_668E390N_R", "LIBIRA_036W372N_R", "MALIQA_044W367N_R",
               "MANDAB_434E126N_R", "MARIB_454E155N_R", "MARW_621E376N_R",
               "MARWRUDH_633E355N_R", "MUGHAN_485E393N_R", "NASAF_658E388N_R",
               "NAYRIZ_542E292N_R", "NAYSABUR_587E361N_R", "QAHIRA_312E300N_R",
               "QANDAHAR_656E316N_R", "QANNAWJ_800E271N_R", "QASHAN_515E339N_R",
               "QUBADHIYAN_681E372N_R", "QUMM_509E346N_R", "RAMHURMUZ_496E312N_R",
               "RUDHAN_560E303N_R", "RUYAN_517E363N_R", "SAGHANIYAN_678E382N_R",
               "SARAQUSA_009W416N_R", "SHADHUNA_059W364N_R", "SHAKKI_472E413N_R",
               "SHIRWAN_487E411N_R", "SIJILMASA_042W312N_R", "SIRJAN_557E294N_R",
               "SUS_482E322N_R", "TAHIRT_013E353N_R", "TALAQAN_508E361N_R",
               "THUJJA_441E139N_R", "TULAYTILA_040W398N_R", "TUS_594E364N_R",
               "TUSHUMMUS_059W350N_R", "TUSTAR_488E320N_R", "TUTILA_016W420N_R",
               "WADIHIJARA_031W406N_R", "WASHQA_003W421N_R", "WAYHIND_722E339N_R",
               "YAZD_543E319N_R",
               "BANNA_569E344N_S", # a waystation in Mafaza, that matches all "ibn" (2/3 of all toponyms!)
               "UNNA_438E140N_R",  # matches a lot of "`an-hu"
               "NA"]


# the function creates a simplified tagging scheme for toponyms (CSV file)
# Structure: TAG pattern, Regular Expression

# TOPONYM INITIAL STRUCTURE
# =========================
#  0 - URI
#  1 - REG_MESO
#  2 - TR
#  3 - SEARCH
#  4 - EN
#  5 - TYPE
#  6 - LAT
#  7 - LON
#  8 - AR
#  9 - AR_Alt
# 10 - AR_Sort

def reformatToponymsIntoMatchingList(schemeFile):
    dic = {}

    # loading prefix list
    with open(topPrefixFile, "r", encoding="utf8") as f1:
        topPref = f1.read().split("\n")
        topPrefList = []

        for t in topPref:
            t = t.split("\t")
            if int(t[0]) > 5:
                topPrefList.append(t[1].replace("_",""))

    with open(schemeFile, "r", encoding="utf8") as f1:
        data = f1.read().split("\n")

        NAcount = 0

        for d in data[1:]:
            d = d.split()
            if d[0] not in excludeTopURIs:
                variants = d[9].split("|")
                variants = list(set(variants))
                for v in variants:
                    v = ara.normalizeArabicLight(v)
                    #print(v)
                    v = v.replace("=", "")
                    vList = [v]
                    for t in topPrefList:
                        vList.append(t+v)
                    #input(vList)
                    for v in vList:
                        # URI 0; toponym: 8
                        if v in dic:
                            dic[v]["uris"].append(d[0])
                            dic[v]["toponyms"].append(d[8].replace("=", " "))
                        else:
                            dic[v] = {"key": "", "uris": [], "toponyms": []}
                            dic[v]["key"] = v
                            dic[v]["uris"].append(d[0])
                            dic[v]["toponyms"].append(d[8].replace("=", " "))
                    #input(dic)
            elif d[0] == "NA":
                NAcount += 1

        print("%d have to be fixed" % NAcount)


        listMain = []
        for k,v in dic.items():
            matchingVal = k
            uris        = ",".join(v["uris"])
            toponyms    = " : ".join(v["toponyms"])

            #print("="*82)
            #input("\n".join([matchingVal, uris, toponyms]))

            var = "\t".join([matchingVal, uris, toponyms])
            listMain.append(var)

        print("\t%d items have been prepared for tagging." % len(listMain))
        header = "\t".join(["MATCH", "URIS", "TOPONYMS"])
        with open("./interpretative_schemes/ToponymsML.csv", "w", encoding="utf8") as f9:
            f9.write(header + "\n" +"\n".join(listMain))

reformatToponymsIntoMatchingList("./interpretative_schemes/topMicro.csv")

# 2. CONVERT NISBA DATA FOR INTO A TAGGING SCHEME
#    - applies custom RE (most common prefixes and suffixes for nisbas) + deNormalization

""" to be continued """

# 3. CONVERT CUSTOM SEARCH DATA FOR INTO A TAGGING SCHEME
#    - simply deNormalizes REGEX

""" to be continued """


print("===>" + str(datetime.now() - startTime))
print("Done!")
