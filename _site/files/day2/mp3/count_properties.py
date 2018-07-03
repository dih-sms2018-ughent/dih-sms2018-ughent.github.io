### mp3_properties_kinship_blood.csv
#===================================
# 000000719	parent of
# 000000551	sibling of
# 000000307	relative of
# 000000076	nephew of
# 000000075	uncle of

### mp3_properties_patronage_all.csv
#===================================
# 000000492	patron of
# 000000484	patronized by 
# 000000219	ṣāḥib of (=)
# 000000139	patron (khāṣṣ) of
# 000000133	khāṣṣ of
# 000000091	ṣāḥib of
# 000000085	patron (ṣaḥāba) of
# 000000021	patron (mulāzama) of
# 000000020	lāzim of
# 000000011	tābiʿ of
# 000000011	patron (tabʿ) of

### mp3_interactions_niʿma_promoting+appointing_v2.csv
#=====================================================
# 000003009	appoints
# 000000659	promotes

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



            
reformatKinBlood("mp3_royalnetworks.csv", 3)
