from robosat_pink.tools import params, cover, download, rasterize

if __name__ == "__main__":
    # rsp cover --bbox 4.795,45.628,4.935,45.853 --zoom 18 ds/cover
    # params_cover = params.Cover(
    #   bbox="4.842052459716797,45.76126587962455,4.854111671447754,45.770336923575734",
    #   zoom=18, out=["ds/cover"])
    # cover.main(params_cover)

    # rsp download --type WMS 'https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg' ds/cover ds/images
    # params_download = params.Download(
    #     type="WMS",
    #     url="https://download.data.grandlyon.com/wms/grandlyon?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0&LAYERS=Ortho2015_vue_ensemble_16cm_CC46&WIDTH=512&HEIGHT=512&CRS=EPSG:3857&BBOX={xmin},{ymin},{xmax},{ymax}&FORMAT=image/jpeg",
    #     cover="ds/cover",
    #     out="ds/images")
    # download.main(params_download)

    # wget -O ds/lyon_roofprint.json 'https://download.data.grandlyon.com/wfs/grandlyon?SERVICE=WFS&REQUEST=GetFeature&TYPENAME=ms:fpc_fond_plan_communaut.fpctoit&VERSION=1.1.0&srsName=EPSG:4326&outputFormat=application/json; subtype=geojson'

    # rsp rasterize --config ds/config.toml --type Building --geojson ds/lyon_roofprint.json --cover ds/cover ds/labels
    # params_rasterize = params.Rasterize(
    #     config="ds/config.toml",
    #     type="Building",
    #     geojson=["ds/lyon_roofprint.json"],
    #     cover="ds/cover",
    #     out="ds/labels"
    # )
    # rasterize.main(params_rasterize)

    # rsp cover --dir ds/images --splits 70/30 ds/training/cover ds/validation/cover
    params_cover2 = params.Cover()
