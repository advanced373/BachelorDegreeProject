headerTaxa = "#nexus\n \n BEGIN Taxa;\n DIMENSIONS ntax=%d;\n TAXLABELS\n"
footerTaxa = ";\n END; [Taxa]\n \n"
footerDistances = ";\n END; [Distances]\n \n"
def writeNEXUS(similarityMatrix, labels):
    f = open("distanceMatrix.nex", "w")
    f.write("#nexus\n \n BEGIN Taxa;\n DIMENSIONS ntax="+str(len(labels))+";\n TAXLABELS\n")
    for i in range(len(labels)):
        f.write("["+str(i+1)+"]   '"+str(labels[i])+"'\n")
    f.write(footerTaxa)
    f.write("BEGIN Distances;\n DIMENSIONS ntax="+str(len(labels))+";\n FORMAT labels=left diagonal triangle=both;\n MATRIX\n")
    for i in range(len(labels)):
        f.write("["+str(i+1)+"]   '"+str(labels[i])+"' ")
        for j in range(len(labels)):
            f.write(str(similarityMatrix[i][j])+" ")
        f.write("\n")
    f.write(footerDistances)
    f.close()
