# 000000164	JaziratArab_RE
# 000000078	Rihab_RE
# 000000060	BadiyatArab_RE
# 000000049	Mafaza_RE
# 000000042	Barqa_RE
# 000000031	Siqiliyya_RE
# 000000016	Khazar_RE
# 000000005	NO_RE


# 000000004	al-Sham
# 000000004	al-Andalus
# 000000002	Khurasan
# 000000002	Iraq
# 000000001	al-Urdunn=&=Filastin
# 000000001	al-Rum
# 000000001	al-Qabq
# 000000001	al-Maghrib
# 000000001	al-Jazira
# 000000001	REG_MESO
# 000000001	Misr
# 000000001	Jilan=&=al-Daylam
# 000000001	Farghana

def reformatKinBlood(file, col):
    print("### %s\n" % file)
    col = col-1
    
    with open(file, "r", encoding="utf8") as f1:
        raw = f1.read().split("\n")

        count = {}
        gephi = []
        for r in raw:
            #print(r)
            r = r.split("\t")


            # count types
            if r[col] in count:
                count[r[col]] += 1
            else:
                count[r[col]]  = 1

        countList = []
        for k, v in count.items():
            countList.append("# %09d\t%s" % (v,k))

        countList = sorted(countList, reverse=True)
        print("\n".join(countList))



            
reformatKinBlood("topMicro.csv", 2)
