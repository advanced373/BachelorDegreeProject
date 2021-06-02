import argparse
import csv
import os
import numpy as np
import ast
class Instance:
    def __init__(self, filename, labels):
        self.fileName = filename
        self.labels = labels
def parseCLI():
    parser = argparse.ArgumentParser(description='Utilitary in Python to generate distance matrix and clustering')
    parser.add_argument('-d','--directory', help='Directory name', required=True, metavar='directory')
    parser.add_argument('-c','--compressor', help='Compressor Type', required=True, choices=['ncd', 'nvcomp', 'fcd', 'nvjpeg'], metavar='compressor')
    parser.add_argument('-t','--type', help='Clustering Algorithm', choices=['k-medoids', 'hierarchical'], metavar='type')
    parser.add_argument('-p','--print', help='print distance matrix', action='store_true')
    parser.add_argument('-o','--out', help='write distance matrix in file')
    parser.add_argument('-s','--statistics', help='print statistics about clusterization performance', action='store_true')
    parser.add_argument('-l','--labels', help='filename for labels document')
    parser.add_argument('-n','--nexus', help='generate pylogenetic tree', action='store_true')
    parser.add_argument('-v','--verbose', help='print extra informations', action='store_true')
    parser.add_argument('-m','--multilabel', help='flag to inform multilabel clustering, available only for labels parameter', action='store_true')
    args = vars(parser.parse_args())
    return args
def parseXML(file, instances, labelsCategories):
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            head_tail = os.path.split(row[0])
            y = np.array(ast.literal_eval(row[1]))
            z = np.fromstring(row[2][1:-1], dtype=np.int, sep=',')
            instance = Instance(head_tail[len(head_tail)-1], z)
            instances.append(instance)
            for i in range(y.size):
                if str(z[i]) not in labelsCategories:
                    labelsCategories[str(z[i])] = y[i]
def getCorrectLabels(folder):
    labels={}
    correctLabels=[]
    for root, dirs, files in os.walk(folder):
        for filename in files:
            for c in filename:
                if c.isdigit():
                    r = filename.index(c)
                    break
            if filename[0:r-1] in labels:
                correctLabels.append(labels[filename[0:r-1]])
            else:
                labels[filename[0:r-1]] = len(labels)
                correctLabels.append(labels[filename[0:r-1]])
    return correctLabels,len(labels), files
def getCorrectLabelsCSV(folder, instances):
    correctLabels = []
    labels = []
    for root, dirs, files in os.walk(folder):
        for instance in instances:
            if instance.fileName +"_all_bands.pt" in files:
                correctLabels.append(instance.labels)
                for i in instance.labels:
                    if i not in labels:
                        labels.append(i)
    return correctLabels, files, labels

