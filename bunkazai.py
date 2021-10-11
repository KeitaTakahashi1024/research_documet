from os import error
import pandas as pd


def main():
    bunkazai = extractBunkazaiFromCsv()
    writeBunkazaiToCsv(bunkazai)
    print(bunkazai)


def extractBunkazaiFromCsv():
    bunkazaiData = pd.read_csv('data/read/bunkazai_idokeido.csv').dropna(how='any')
    return bunkazaiData.astype(str)

def writeBunkazaiToCsv(bunkazai):
    bunkazaiNum = bunkazai.shape[0]
    f = open('data/bunkazai/bunkazai_idokeido.csv', 'w')

    for i in range(bunkazaiNum):
        f.write(bunkazai.iat[i, 0] + "," + bunkazai.iat[i, 1] + "," + bunkazai.iat[i, 2] + "\n")

    f.close()




if __name__ == "__main__":
    main()