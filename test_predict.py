from robosat_pink.tools import params, cover, download, rasterize, predict, vectorize

if __name__ == "__main__":
    # rsp cover --bbox 4.795,45.628,4.935,45.853 --zoom 18 ds/cover 4.842052459716797,45.76126587962455,4.854111671447754,45.770336923575734
    # rsp download --type XYZ 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' dp/cover dp/images
    # rsp rasterize --config data/config.toml --type Building --geojson data/buildings.json  --cover dp/cover dp/labels
    # rsp predict --checkpoint data/model/checkpoint-0.00005.pth ds dp/masks
    # rsp vectorize --type --config masks out

    # params_cover = params.Cover(
    #     # bbox="4.842052459716797,45.76126587962455,4.854111671447754,45.770336923575734",
    #     bbox="119.29679274559021,26.06680633905522,119.30007576942445,26.070054139449656",
    #     zoom=17, out=["dp/cover"])
    # cover.main(params_cover)

    # params_download = params.Download(
    #     type="XYZ",
    #     url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    #     cover="dp/cover",
    #     out="dp/images",
    #     timeout=20)
    # download.main(params_download)

    # params_predict = params.Predict(
    #     dataset="dp",
    #     checkpoint='data/model/checkpoint-00010.pth',
    #     config="data/config.toml",
    #     out="dp/masks"
    # )
    # predict.main(params_predict)

    params_vectorize = params.Vectorize(
        masks="dp/masks",
        type="Building",
        config="data/config.toml",
        out="dp/vectors.json"
    )
    vectorize.main(params_vectorize)
