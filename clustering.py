#region Imports
import os
import subprocess
import sys
import time
from threading import Timer
import numpy as np
from sklearn import svm, metrics
from sklearn.metrics import f1_score
from sklearn.metrics import rand_score
from sklearn.cluster import AgglomerativeClustering
from sklearn_extra.cluster import KMedoids
from nexus import writeNEXUS
from parserHelper import parseCLI, parseXML, getCorrectLabels, getCorrectLabelsCSV
from sklearn.metrics import confusion_matrix
from generateDistanceMatrix import NVCOMP,NCD,FCD,NVJPEG
#endregion
#region Global Variables
instances = []
labelsCategories = {}
outputString = None
labels = None
files = None
#endregion
if __name__ == '__main__':
    args = parseCLI()
    if args['labels']:
        parseXML(args['labels'], instances,labelsCategories)
        correctLabels = []
        if args['multilabel']:
            for i in instances:
                correctLabels.append(i.labels)
        else:
            for i in instances:
                correctLabels.append(i.labels[0])
        correctLabels, filenames, labels = getCorrectLabelsCSV(args['directory'],instances)
        size = len(labels)
        sizeTotal = len(correctLabels)
    else:
        correctLabels, size, filenames = getCorrectLabels(args['directory'])
        sizeTotal = len(correctLabels)
    if args['compressor'] == "ncd":
        start_time = time.time()
        filenames=[]
        similarityMatrix, filenames = NCD(args['directory'])
        if args['verbose']:
            print("--- %s seconds ---" % (time.time() - start_time))
            print(similarityMatrix)
            print("-------------------------------------")
    elif args['compressor'] == "nvcomp":
        start_time = time.time()
        similarityMatrix = NVCOMP([args['directory']])
        if args['verbose']:
            print("--- %s seconds ---" % (time.time() - start_time))
            print(similarityMatrix)
            print("-------------------------------------")
    elif args['compressor'] == "fcd":
        start_time = time.time()
        similarityMatrix = FCD([args['directory']])
        if args['verbose']:
            print("--- %s seconds ---" % (time.time() - start_time))
            print(similarityMatrix)
            print("-------------------------------------")
    elif args['compressor'] == "nvjpeg":
        start_time = time.time()
        similarityMatrix = NVJPEG(args['directory'])
        if args['verbose']:
            print("--- %s seconds ---" % (time.time() - start_time))
            print(similarityMatrix)
            print("-------------------------------------")
    if args['type'] == "k-medoids":
        start_time = time.time()
        kmedoids = KMedoids(n_clusters=size, random_state=0).fit(similarityMatrix)
        print(kmedoids.labels_)
        labelsPredicted = kmedoids.labels_
        if args['verbose']:
            print("--- %s seconds ---" % (time.time() - start_time))
    elif args['type'] == "hierarchical":
        start_time = time.time()
        clusterB = AgglomerativeClustering(n_clusters = size, affinity='precomputed', linkage='average')
        labelsPredicted = clusterB.fit_predict(similarityMatrix)
        if args['verbose']:
            print("--- %s seconds ---" % (time.time() - start_time))
    if args['statistics']:
        print("----------------------------STATISTICS--------------------------")
        if args['type']:
            print("All Labels:")
            print(correctLabels)
            if args['multilabel']:
                correct_labels = []
                for corectLabel in correctLabels:
                    correct_labels.append(corectLabel[0])
                correctLabels = correct_labels
            print("Correct labels:")
            print(correctLabels)
            print("Predicted labels:")
            print(labelsPredicted)
            contingency_matrix = metrics.cluster.contingency_matrix(correctLabels, labelsPredicted)
            print("Contingency matrix:")
            print(contingency_matrix)
            confusion_matrix = confusion_matrix(correctLabels, labelsPredicted)
            print("Confusion matrix:")
            print(confusion_matrix)
            purity = np.sum(np.amax(contingency_matrix, axis=0)) / np.sum(contingency_matrix)
            randIndex = rand_score(correctLabels, labelsPredicted)
            print("Rand Index value is: "+ str(randIndex))
            print("F-Score value is: " + str(f1_score (correctLabels, labelsPredicted, average='micro')))
            print("Purity value is: "+ str(purity))
        else:
            sys.exit("No clustering or classification algorithm selected!")
    if args['nexus']:
        writeNEXUS(similarityMatrix,correctLabels)
        if args['verbose']:
            print("This will take some time.")
        command = "wsl maketree /mnt/c/Facultate/Licenta/proiectiLicenta/distanceMatrix.nex"
        kill = lambda process: process.kill()
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        my_timer = Timer(30, kill, [process])
        try:
            my_timer.start()
            stdout, stderr = process.communicate()
        finally:
            my_timer.cancel()
        if args['verbose']:
            print("Tree generated!")
        command = "wsl neato -Tpng -Gsize=7,7 /mnt/c/Facultate/Licenta/proiectiLicenta/treefile.dot"
        f = open("tree.png", "w")
        process = subprocess.Popen(command.split(), stdout=f)
        output, error = process.communicate()
        if args['verbose']:
            print("You can find phylogenetic tree in tree.png")
        os.remove("distanceMatrix.nex")
        os.remove("treefile.dot")
    if args['print']:
        print('Distance matrix:')
        print(similarityMatrix)
    if args['out']:
        with open(args['out'],'wb') as f:
                np.savetxt(f, similarityMatrix, fmt='%.4f')
