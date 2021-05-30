import math
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import colors, cm, pyplot as plt
from scipy.cluster import hierarchy
def plotImages(folder, size):
    w=20
    h=20
    columns = int(math.sqrt(size))
    rows = math.ceil(size/columns)
    fig=plt.figure(figsize=(rows, columns))
    i = 1
    for root, dirs, files in os.walk(folder):
            for filename in files:
                img = mpimg.imread(folder+ "/" +filename)
                ax = fig.add_subplot(rows, columns, i)
                ax.axis('off')
                ax.title.set_text(filename + " "+ str(os.path.getsize(folder+ "/" +filename)))
                plt.imshow(img)
                i=i+1
    plt.show()
def plotDendogram(similarityMatrix):
    Z = hierarchy.linkage(similarityMatrix, 'average')
    plt.figure()
    dn = hierarchy.dendrogram(Z)
    plt.savefig('plt.png', format='png', bbox_inches='tight')
