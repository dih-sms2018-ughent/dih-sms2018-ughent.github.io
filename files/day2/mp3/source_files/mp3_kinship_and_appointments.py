
import itertools

def generateNodes():
    ls = []

    with open("_mp3_properties_kinship_blood.csv", "r", encoding="utf8") as f1:
        raw = f1.read().split("\n")

        for r in raw:
            r = r.split("\t")

            ls.append(r[0])
            ls.append(r[2])

    with open("_mp3_properties_kinship_marriagerelationships.csv", "r", encoding="utf8") as f1:
        raw = f1.read().split("\n")

        for r in raw:
            r = r.split("\t")

            ls.append(r[0])
            ls.append(r[2])

    ls = list(set(ls))

    with open("mp3_kinshipNodes.csv", "w", encoding="utf8") as f9:
        f9.write("id\n"+"\n".join(sorted(ls)))
        
generateNodes()

def generateEdges(file):
    print(file)
    dic = {}
    
    with open(file, "r", encoding="utf8") as f1:
        raw = f1.read().split("\n")

        for r in raw:
            r = r.split("\t")

            if r[0] != "unknown 0":
                if r[2] != "unknown 0":

                    if r[0] in dic:
                        dic[r[0]].append(r[2])
                    else:
                        dic[r[0]] = [r[2]]

                    if r[2] in dic:
                        dic[r[2]].append(r[0])
                    else:
                        dic[r[2]] = [r[0]]


        edges_all = []

        for k,v in dic.items():
            edgesK = list(itertools.combinations(v, 2))
            #print(len(edgesK))
            edgesK = list(set(edgesK))
            #print(len(edgesK))

            #input()

            for e in edgesK:
                e = list(e)
                if e[0] != e[1]:
                    if e[0] != "":
                        if e[1] != "":
                            e = "\t".join(sorted(list(e)))+ "\t1"
                            edges_all.append(e)

            edges_all = list(set(edges_all))
            
    # save edges
    edges_all = sorted(edges_all)
    head = "source\ttarget\tweight\n"
    with open("edges_"+file, "w", encoding="utf8") as f9:
        f9.write(head+"\n".join(edges_all))

            
generateEdges("_mp3_properties_kinship_blood.csv")
generateEdges("_mp3_interactions_appointments.csv")
generateEdges("_mp3_properties_kinship_marriagerelationships.csv")

generateEdges("_mp3_royalnetworks.csv")

def mergeNetworks(nw1, nw2):
    nwd = {}

    with open(nw1, "r", encoding="utf8") as f1:
        raw1 = f1.read().split("\n")

        for r in raw1[1:]:
            nwd[r] = 0

    with open(nw2, "r", encoding="utf8") as f2:
        raw2 = f2.read().split("\n")

        for r in raw2[1:]:
            if r in nwd:
                nwd[r] = 1

    edges = []
    for k,v in nwd.items():
        if v == 0:
            edges.append(k)
    
    head = "source\ttarget\tweight\n"
    with open(nw1.replace(".csv", "_AND_")+nw2, "w", encoding="utf8") as f9:
        f9.write(head+"\n".join(edges))

# edges__appointments.csv
# edges__kinship_blood.csv
# edges__marriagerelationships.csv

mergeNetworks("edges__kinship_blood.csv", "edges__appointments.csv")
mergeNetworks("edges__marriagerelationships.csv", "edges__appointments.csv")
