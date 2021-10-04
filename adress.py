from os import error
import pandas as pd
import requests, json, time

def main():
   choumei = extractChoumeiFromCsv()
   print(choumei)
   calcLonLat(choumei)


def extractChoumeiFromCsv():
    choumeiData = pd.read_csv('data/read/hakodate-choumei.csv', header=None, names = ('管轄','町名','ふりがな','郵便番号'))
    return choumeiData.astype(str)

def calcLonLat(choumei):
    requestUrl = 'http://geoapi.heartrails.com/api/json?method=searchByPostal&postal='
    choumeiNum = choumei.shape[0] - 1
    #choumeiList = []
    #latitudeList = []
    #longtitudeList = []

    f = open('data/adress/choumei_idokeido.txt', 'w')
    for i in range(choumeiNum):
        postalCode = choumei.iat[i+1, 3]

        try:
            response = requests.get(requestUrl+postalCode)

            if 'json' in response.headers.get('content-type'):
                result = response.json()['response']['location'][0]
                print(i, choumei.iat[i+1, 1],result['x'], result['y'])
                f.write(choumei.iat[i+1, 1] + "," + result['x'] + "," + result['y'] + "\n")
                #choumeiList.append(choumei.iat[i+1, 1])
                #latitudeList.append(result['x'])
                #longtitudeList.append(result['y'])
                time.sleep(1)
            else:
                result = response.text
                print(result)

        except(error) as e:
            print(e)
        
    f.close()


if __name__ == "__main__":
    main()
