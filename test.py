import RSPpredict
import RSPtrain

if __name__ == "__main__":
    extent = "116.293791,39.943535,116.297653,39.946603"
    sql = '''SELECT geom AS TILE_GEOM FROM "BUIA" '''

    RSPtrain.main(extent, sql.format(extent=extent))
