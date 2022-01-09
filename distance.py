import math
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from pyproj import Geod
from pyproj import Transformer

def extractChoumeiFromCsv(keyword):
    if keyword == "choumei":
        choumei_data = pd.read_csv('data/read/choumei_idokeido.csv')
        return choumei_data.astype(str)
    elif keyword == "bunkazai":
        bunkazai_data = pd.read_csv('data/read/bunkazai_idokeido.csv')
        return bunkazai_data.astype(str)
    else:
        print("キーワード間違えてるよ")

def calcDistance(first_lat, first_lng, second_lat, second_lng):
    # ellpsは赤道半径。GPSはWGS84を使っている。距離は6,378,137m
    g = Geod(ellps='WGS84')

    result = g.inv(first_lng, first_lat, second_lng, second_lat)
    distance_2d = result[2]

    return distance_2d

def convertWGS84ToJGD2011(lat, lng):
    wgs84_epsg = 4326
    rect_epsg = 6679
    coordinate = Transformer.from_proj(wgs84_epsg, rect_epsg)
    convert_x, convert_y = coordinate.transform(lat, lng)
    #convert_x = coordinate.transform(lat)
    #convert_y = coordinate.transform(lng)
    
    return convert_x,convert_y

def main():
    # choumei_data = extractChoumeiFromCsv("choumei")
    # bunkazai_data = extractChoumeiFromCsv("bunkazai")

    # choumei_data_lnegth = choumei_data.shape[0]
    # bunkazai_data_length = bunkazai_data.shape[0]

    # #for i in range(choumei_data_lnegth - 1):
    #     #distance = calcDistance(choumei_data.iat[i, 1], choumei_data.iat[i, 2], choumei_data.iat[i + 1, 1], choumei_data.iat[i + 1, 2])
    #     #print('{0}から{1}までの直線距離は{2}m'.format(choumei_data.iat[i, 0], choumei_data.iat[i + 1, 0], distance))

    # choumei_name = []
    # convert_x = []
    # convert_y = []
    # for i in range(choumei_data_lnegth):
    #      convert_idokeido = convertWGS84ToJGD2011(choumei_data.iat[i, 1], choumei_data.iat[i, 2])
    #      choumei_name.append(choumei_data.iat[i, 0])
    #      convert_x.append(convert_idokeido[0])
    #      convert_y.append(convert_idokeido[1])
    #      #print(choumei_name[i], convert_x[i], convert_y[i])

    # data = {
    #     'name': choumei_name,
    #     'x': convert_x,
    #     'y': convert_y
    # }
    # df = pd.DataFrame(data)
    # df.to_csv('data/adress/choumei_convert.csv', index = False)
    #print(df)

    df = pd.read_csv('data/adress/choumei_convert.csv', index_col=0)

    linkage_result = linkage(df, method='ward', metric='euclidean')
    #plt.figure(num=None, figsize=(16, 9), dpi=120, facecolor='w', edgecolor='k')
    #dendrogram(linkage_result, labels=df.index)
    #plt.show()

if __name__ == "__main__":
    main()