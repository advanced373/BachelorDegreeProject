import os
import cv2
from sklearn.cluster import MiniBatchKMeans
def imagesPreprocessing(folder):
    for root, dirs, files in os.walk(folder):
        for filename in files:
            img = cv2.imread(folder+"/"+filename)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            img = imageSegmentation(img)
            cv2.imwrite("dev/"+filename, img)
def imageSegmentation(image):
    (h, w) = image.shape[:2]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    image = image.reshape((image.shape[0] * image.shape[1], 3))
    clt = MiniBatchKMeans(n_clusters = 16)
    labels = clt.fit_predict(image)
    quant = clt.cluster_centers_.astype("uint8")[labels]
    quant = quant.reshape((h, w, 3))
    quant = cv2.cvtColor(quant, cv2.COLOR_LAB2BGR)
    return quant

