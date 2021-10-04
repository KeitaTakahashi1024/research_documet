import pandas as pd
import csv

def jinbutsudens():
    #df = pd.read_csv('data/jibutsudens.csv', header=None, names = ('id','name','nameYomi','dateBorn','dateDeath','catchWord','description','url','imageUrl'))
    #df_new = df.drop(columns='id')
    #df_new.to_csv('data/new_jinbutsudens.csv', header=False, index=False,quoting=csv.QUOTE_NONNUMERIC)
    df_csv = pd.read_csv('data/new_jinbutsudens.csv', header=None, names = ('name','nameYomi','dateBorn','dateDeath','catchWord','description','url','imageUrl'))
    print(df_csv.astype(str))
    jinbutsudens_to_sql(df_csv.astype(str))

def jinbutsudens_to_sql(df):
    sql_first = "INSERT INTO jinbutsudens (name, nameYomi, dateBorn, dateDeath, catchWord, description, url, imageUrl) VALUES "
    sql_last  = ";"

    for csv_row in range(df.shape[0]):
        sql = "("
        for csv_col in range(df.shape[1]):
            sql += "'"+ df.iat[csv_row,csv_col] + "'"

            if(csv_col != df.shape[1] - 1):
                sql += ", "
            else:
                if(csv_row != df.shape[0] - 1):
                    sql += "),"
                else:
                    sql += ")"

        sql_first += sql
    sql_main = sql_first + sql_last

    f = open('data/new_jinbutsudens.txt', 'w')

    f.write(sql_main)

    f.close()

    print(sql_main)

def locations():
    year_list = ["1878","1925","1926","1932","1936","1943","1949","1952"]
    df_list = []

    for df in range(len(year_list)):
        df_list.append(pd.read_csv('data/jinbutsudens_' + year_list[df] +'.csv').astype(str))

    df_new = df_list[0]

    for i in range(len(df_list) - 1):
        df_new = df_new.append(df_list[i + 1])

    #print(df_new)

    df_locations = df_new.drop(columns=['人物名', '年代'])

    df_locations[~df_locations.duplicated()].to_csv('data/new_jinbutsudens_locations.csv', header=False, index=False,quoting=csv.QUOTE_NONNUMERIC)
    df_csv = pd.read_csv('data/new_jinbutsudens_locations.csv', header=None).astype(str)
    jinbutsudens_lcoations_to_sql(df_csv)

def jinbutsudens_lcoations_to_sql(df):
    sql_first = "INSERT INTO locations (place, lat, lon) VALUES "
    sql_last  = ";"
    for csv_row in range(df.shape[0]):
        sql = "("
        for csv_col in range(df.shape[1]):
            sql += "'"+ df.iat[csv_row,csv_col] + "'"

            if(csv_col != df.shape[1] - 1):
                sql += ", "
            else:
                if(csv_row != df.shape[0] - 1):
                    sql += "),"
                else:
                    sql += ")"

        sql_first += sql
    sql_main = sql_first + sql_last
    #print(sql_main)

    f = open('data/new_jinbutsudens_locations.txt', 'w')

    f.write(sql_main)

    f.close()

def places():
    year_list = ["1878","1925","1926","1932","1936","1943","1949","1952"]
    df_list = []

    for df in range(len(year_list)):
        df_list.append(pd.read_csv('data/jinbutsudens_' + year_list[df] +'.csv').astype(str))

    df_new = df_list[0]

    for i in range(len(df_list) - 1):
        df_new = df_new.append(df_list[i + 1])

    #print(df_new)

    df_places = df_new.drop(columns=['緯度', '経度', '年代'])
    #print(df_places)
    df_places[~df_places.duplicated()].to_csv('data/new_jinbutsudens_places.csv', header=False, index=False,quoting=csv.QUOTE_NONNUMERIC)

    #print(df_places[~df_places.duplicated()])
    df_csv = pd.read_csv('data/new_jinbutsudens_places.csv', header=None).astype(str)
    jinbutsudens_places_to_sql(df_csv)

def jinbutsudens_places_to_sql(df):
    sql_first = "INSERT INTO places (name, place) VALUES "
    sql_last  = ";"
    for csv_row in range(df.shape[0]):
        sql = "("
        for csv_col in range(df.shape[1]):
            sql += "'"+ df.iat[csv_row,csv_col] + "'"

            if(csv_col != df.shape[1] - 1):
                sql += ", "
            else:
                if(csv_row != df.shape[0] - 1):
                    sql += "),"
                else:
                    sql += ")"

        sql_first += sql
    sql_main = sql_first + sql_last
    #print(sql_main)

    f = open('data/new_jinbutsudens_places.txt', 'w')

    f.write(sql_main)

    f.close()


