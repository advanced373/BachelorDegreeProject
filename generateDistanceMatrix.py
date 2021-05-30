import math
import subprocess
import threading

import cv2
import numpy as np
import time
import os
from nvjpeg import NvJpeg
from ctypes import *
P = 8
def thread_function(name, folder):
    global outputString, labels, files, P
    N = len(files)
    start = name * math.ceil((float)(N)/ P)
    end = min(N,(name + 1) * math.ceil((float)(N) / P))
    start_time = time.time()
    for n in range(start, end, 1):
        command = "wsl ncd -d " + folder + " -f "+folder + "/"+ files[n]
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        output = output.decode('utf-8')
        labels[n] = files[n]
        outputStringHelp1= output.split(' ')
        outputStringHelp2 = np.array(outputStringHelp1[1:len(outputStringHelp1)-1])
        for i in range(N):
            outputString[i][n] = outputStringHelp2.astype(float)[i]
    print("--- %s seconds ---" % (time.time() - start_time) + " Thread "+str(name))
    return None
    #plt.savefig('foo.png')
def NVCOMP(argv):
    so_file = "dlls/FirstTryNvcomp.dll"
    LP_c_char = POINTER(c_char)
    LP_LP_c_char = POINTER(LP_c_char)
    my_functions = CDLL(so_file)
    my_functions.NCD_NVCOMP_2.argtypes = c_int,POINTER(POINTER(c_char))
    my_functions.NCD_NVCOMP_2.restype = POINTER(POINTER(c_float))
    p = (LP_c_char*len(argv))()
    for i, arg in enumerate(argv):
        enc_arg = arg.encode('utf-8')
        p[i] = create_string_buffer(enc_arg)
    na = cast(p, LP_LP_c_char)
    entries = os.listdir(argv[0])
    A= my_functions.NCD_NVCOMP_2(len(argv), na)
    if A == None:
        print('Error!')
        return
    arr = np.ctypeslib.as_array(A[0],(1,len(entries)))
    for array in range(len(entries)-1):
        arr = np.append(arr, np.ctypeslib.as_array(A[array+1],(1,len(entries))), axis = 0)
    return arr
def FCD(argv):
    so_file = "dlls/FCD.dll"
    LP_c_char = POINTER(c_char)
    LP_LP_c_char = POINTER(LP_c_char)
    my_functions = CDLL(so_file)
    my_functions.computeFCDMultithread.argtypes = c_int,POINTER(POINTER(c_char))
    my_functions.computeFCDMultithread.restype = POINTER(POINTER(c_float))
    p = (LP_c_char*len(argv))()
    for i, arg in enumerate(argv):
        enc_arg = arg.encode('utf-8')
        p[i] = create_string_buffer(enc_arg)
    na = cast(p, LP_LP_c_char)
    entries = os.listdir(argv[0])
    A= my_functions.computeFCDMultithread(len(argv), na)
    arr = np.ctypeslib.as_array(A[0],(1,len(entries)))
    for array in range(len(entries)-1):
        arr = np.append(arr, np.ctypeslib.as_array(A[array+1],(1,len(entries))), axis = 0)
    return arr
def NCD(folder):
    global outputString, labels, files
    for root, dirs, files in os.walk(folder):
        outputString = np.zeros((len(files),len(files)), dtype=float)
        labels = np.zeros((len(files),), dtype='U50')
    threads = list()
    for index in range(P):
        x = threading.Thread(target=thread_function, args=(index,folder))
        threads.append(x)
        x.start()
    for index, thread in enumerate(threads):
        thread.join()
    return outputString, labels
def NCD_Seq(folder):
    folderName1 = folder
    folderName2 = folder
    command = "wsl ncd -c zlib -d " + folderName1 + " -d "+ folderName2
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode('utf-8')
    outputList = output.split('\n')
    labels = np.zeros((len(outputList)-1,), dtype='U50')
    outputString = np.zeros((len(outputList)-1,len(outputList)-1), dtype=float)
    for i in range(len(outputList)-1):
        outputStringHelp1= outputList[i].split(' ')
        labels[i] = outputStringHelp1[0]
        outputStringHelp2 = np.array(outputStringHelp1[1:len(outputStringHelp1)-1])
        outputString[i] = outputStringHelp2.astype(float)
    return outputString, labels
def NVCOMP_PT(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            print("Hi")
            #fileT = torch.load(folder+"/"+file)
            #plt.imshow(np.float64(fileT))
            #plt.show()
def NVJPEG(folder):
    nj = NvJpeg()
    images =[]
    for root, dirs, files in os.walk(folder):
            for file in files:
                images.append(cv2.imread(folder+"/"+file))
    out_bytes = np.zeros((len(images), len(images)))
    similarityMatrix = np.zeros((len(images), len(images)))
    for i in range(len(images)):
        for j in range(len(images)):
            if i == j:
                value = images[i]
                out_bytes[i][j] = len(nj.encode(value))
            else:
                value = cv2.vconcat([images[i],images[j]])
                out_bytes[i][j] = len(nj.encode(value))
    for i in range(len(images)):
        for j in range(len(images)):
            if i == j:
                similarityMatrix[i][j] = 0.0
            else:
                similarityMatrix[i][j] = (out_bytes[i][j] - min(out_bytes[i][j], out_bytes[j][j])) / max(out_bytes[i][i], out_bytes[j][j])
    return similarityMatrix
