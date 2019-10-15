import RSPpredict
import RSPtrain
import json

if __name__ == "__main__":
    # extent = "116.293791,39.943535,116.297653,39.946603" #青东商务区
    # extent = ""119.29679274559021,26.06680633905522,119.30007576942445,26.070054139449656"" #
    extent = "118.87,25.39, 118.88,25.40"

    RSPtrain.main(extent)

    # result = RSPpredict.main(extent)
