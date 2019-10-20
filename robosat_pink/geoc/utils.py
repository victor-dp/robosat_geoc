import glob
import os


def getLastPth(path):
    if not os.path.isdir(path):
        return 0
    files = glob.glob(path + "/model/*.pth")
    maxNum = 0
    for file in files:
        fileName = os.path.basename(file)
        name_and_ext = os.path.splitext(fileName)
        names = name_and_ext[0].split('-')
        if maxNum < int(names[1]):
            maxNum = int(names[1])
    return maxNum
