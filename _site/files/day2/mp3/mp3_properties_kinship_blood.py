
##000000719	parent of
##000000551	sibling of
##000000307	relative of
##000000076	nephew of
##000000075	uncle of

kin = {
"parent of": "20",
"sibling of": "15",
"relative of": "10",
"nephew of": "5",
"uncle of": "1"
    }

def reformatKinBlood(file):
    with open(file, "r", encoding="utf8") as f1:
        raw = f1.read().split("\n")

        count = {}
        gephi = []
        for r in raw:
            #print(r)
            r = r.split("\t")

            val = "\t".join([r[0], r[2], kin[r[1]], r[1]])
            gephi.append(val)
            
    # save edges
    head = "source\ttarget\tweight\ttype\n"
    with open(file.replace(".csv", "_edges.csv"), "w", encoding="utf8") as f9:
        f9.write(head+"\n".join(gephi))


            
reformatKinBlood("mp3_properties_kinship_blood.csv")
