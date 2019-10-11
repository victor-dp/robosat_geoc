from robosat_pink.tools import params, cover, download, rasterize, predict, vectorize

if __name__ == "__main__":
    # # rsp cover --bbox 4.795,45.628,4.935,45.853 --zoom 18 ds/cover 4.842052459716797,45.76126587962455,4.854111671447754,45.770336923575734
    # params_cover = params.Cover(
    #   bbox="4.842052459716797,45.76126587962455,4.854111671447754,45.770336923575734",
    #   zoom=17, out="ds/cover")
    # cover.main(params_cover)


    # # rsp download --type XYZ 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}' ds/cover ds/images
    # params_download = params.Download(
    #     type="XYZ",
    #     url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    #     cover="ds/cover",
    #     out="ds/images",
    #     timeout=20)
    # download.main(params_download)


    # # rsp rasterize --config data/config.toml --type Building --geojson data/buildings.json  --cover ds/cover ds/labels
    # params_rasterize = params.Rasterize(
    #     config="data/config.toml",
    #     type="Building",
    #     geojson=["data/buildings.json"],
    #     cover="ds/cover",
    #     out="ds/labels"
    # )
    # rasterize.main(params_rasterize)


    # # rsp predict --checkpoint data/model/checkpoint-0.00005.pth ds ds/masks
    checkpoint = 'checkpoint-0.00'+params.Train.epochs+'.pth'
    params_predict = params.Predict(
        dataset="ds",
        checkpoint='data/model/'+checkpoint,
        config="data/config.toml",
        out="ds/masks"
    )
    predict.main(params_predict)


    # # rsp vectorize --type --config masks out
    # params_vectorize = params.Vectorize(
    #     masks="ds/masks",     
    #     type="Building",      
    #     config="data/config.toml",
    #     out="ds/vectors"
    # )
    # vectorize.main(params_vectorize)



