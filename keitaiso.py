# coding: UTF-8
from os import error
from numpy import reciprocal, result_type
import pandas as pd
import MeCab
import csv
import requests, json, time
import matplotlib.pyplot as plt
import japanize_matplotlib
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from pyproj import Transformer
import spacy
from spacy.pipeline import EntityRuler
import functools
import collections

from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

def extractChoumeiFromCsv(keyword):
    if keyword == "choumei":
        choumei_data = pd.read_csv('data/read/choumei_idokeido.csv')
        return choumei_data.astype(str)
    elif keyword == "jinbutu":
        jinbutu_data = pd.read_csv('data/read/jinbutu.csv')
        return jinbutu_data.astype(str)
    elif keyword == "bunkazai":
        bunkazai_data = pd.read_csv('data/read/bunkazai_idokeido.csv')
        return bunkazai_data.astype(str)
    else:
        print("キーワード間違えてるよ")

def outputChoumeiDic(choumei):
    choumei_num = choumei.shape[0]
    f = open('data/dic/choumei.csv', 'w')

    for i in range(choumei_num):
        f.write(choumei.iat[i, 0]+ ",,,10,名詞,固有名詞,地域,一般,*,*,*,*,*"+ "\n")

    f.close()

def outputAllDic(choumei,jinbutu,bunkazai):
    choumei_num = choumei.shape[0]
    jinbutu_num = jinbutu.shape[0]
    bunkazai_num = bunkazai.shape[0]
    f = open('data/dic/place.csv', 'w')

    for i in range(choumei_num):
        f.write(choumei.iat[i, 0]+ ",,,10,名詞,固有名詞,地域,一般,*,*,"+ choumei.iat[i, 0] +",*,*"+ "\n")

    for i in range(bunkazai_num):
        f.write(bunkazai.iat[i, 0]+ ",,,10,名詞,固有名詞,地域,一般,*,*,"+ bunkazai.iat[i, 0] +",*,*"+ "\n")
    
    for i in range(jinbutu_num):
        jinbutus = jinbutu.iat[i, 0]
        person = jinbutus.strip()
        if "、" in person:
            people = person.split("、")
            print(people)
        else:
            f.write(person + ",,,10,名詞,固有名詞,人名,一般,*,*,"+ person +",*,*"+ "\n")
    
    f.close()

def readDescriptionFromTxt(keyword):
    f = open('data/read/description/' + keyword + '.txt', 'r', encoding='UTF-8')
    data = f.read()
    f.close()
    return str(data)

def readHakodateShishi():
    f = open('data/read/hakodate_shishi.csv', 'r', encoding='UTF-8')
    data = f.read()
    f.close()
    return data

def convertWGS84ToJGD2011(lat, lng):
    wgs84_epsg = 4326
    rect_epsg = 6679
    coordinate = Transformer.from_proj(wgs84_epsg, rect_epsg)
    convert_x, convert_y = coordinate.transform(lat, lng)
    
    return convert_x,convert_y

def createDataFrame(data):
    df = pd.read_csv('data/read/hakodate_shishi.csv', index_col = 0)
    return df.astype(str)

def splitSentence(string):
    split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
    concat_tail_te = functools.partial(concatenate_matching, former_matching_rule=r"^(?P<result>.+)(て)$", remove_former_matched=False)
    segmenter = make_pipeline(normalize, split_newline, concat_tail_te, split_punc2)
    result = list(segmenter(string))
    return result

def keitaisokaiseki(df):
    m = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")

    data_size = df.shape[0]

    noun_list= []
    unique_noun_list = []
    noun_area_list = []
    noun_person_list = []
    desc_list = []
    sentence_list = []
    desc_split = ""

    noun_detail_area_list =[]
    noun_detail_person_list = []

    for i in range(data_size):
        title = df.iat[i, 0]
        desc = df.iat[i, 1]
        sentences = splitSentence(desc)
        sentence_list.append(desc)

        for j in range(len(sentences)):
            sentence = sentences[j]
            desc_list.append(sentence)
            keitaiso = m.parse(sentence)

            lines = keitaiso.split('\n')

            for line in lines:
                feature = line.split('\t')
                if len(feature) == 2: #'EOS'と''を省く
                    info = feature[1].split(',')
                    hinshi = info[0]
                    hinshi_detail = info[1]
                    hinshi_irex = info[2]
                    if hinshi == '名詞' and hinshi_detail == '固有名詞' and hinshi_irex == "地域":
                        noun_area_list.append(info[6])
                        noun_detail_area_list.append(info)
                    if hinshi == '名詞' and hinshi_detail == '固有名詞' and hinshi_irex == "人名":
                        noun_person_list.append(info[6])
                        noun_detail_person_list.append(info)
                    if hinshi == '名詞' and hinshi_detail == '固有名詞':
                        unique_noun_list.append(info[6])
                    if hinshi == '名詞':
                        noun_list.append(info[6])
        desc_list.append(desc_split)

    noun_array = collections.Counter(noun_list)
    noun_list = []
    noun_sum = 0
    for noun,count in noun_array.items():
        if count >= 10:
            noun_list.append(noun)
    for noun,count in noun_array.items():
        noun_sum += count

    # noun_array = collections.Counter(unique_noun_list)
    # unique_noun_list = []
    # noun_sum = 0
    # for noun,count in noun_array.items():
    #     if count >= 10:
    #         unique_noun_list.append(noun)
    # for noun,count in noun_array.items():
    #     noun_sum += count
    
    area_list = list(set(noun_area_list))
    person_list = list(set(noun_person_list))

    # writeCountAreasToCsv(df, area_list)
    # writeDescToCsv(desc_list)
    df_area = readCsv('data/hakodate_shishi/area_count.csv')
    df_desc = readCsv('data/read/fix_test_hakodate_shishi.csv')
    #df_desc = readCsv('data/read/fix_hakodate_shishi/desc.csv')
    df_noun = readCsv('data/hakodate_shishi/nouns_2.csv')
    noun_list = df_noun
    # noun_list = list(df_noun['noun'])

    # searchWords(df_desc, df_area, noun_list, sentence_list, noun_sum, noun_array)
    # df_relate = readCsv('data/hakodate_shishi/noun_dist.csv')
    # print(df_noun)
    calcRelative(df_area, df_noun, sentence_list)

def writeCountAreasToCsv(df, area_list):
    data_size = df.shape[0]
    area_count_list = []

    for area in area_list:
        count = 0
        for i in range(data_size):
            desc = df.iat[i, 1]
            count += desc.count(area)
        area_count_list.append(count)
    print(area_count_list)

    data = {
        "area": area_list,
        "count": area_count_list
    }

    df_area = pd.DataFrame(data)
    df_area.to_csv('data/hakodate_shishi/area_count.csv', index = False)


def readCsv(path):
    df = pd.read_csv(path)
    return df.astype(str)

def writeDescToCsv(desc_list):
    df_desc = pd.DataFrame(desc_list)
    df_desc.to_csv('data/hakodate_shishi/desc.csv', index = False)

def searchWords(df_desc, df_area, noun_list, sentence_list, noun_sum, noun_array):
    data_desc_size = df_desc.shape[0]
    data_area_size = df_area.shape[0]

    name = [925, 413, 1477, 2343, 2448, 246, 1219, 2712, 1587, 2211]
    choumei = ["元町", "住吉町", "松風町", "新川町", "青柳町", "的場町", "二十間坂", "豊川町", "堀川町", "末広町"]
    area = df_area.iat[name[0],0]
    

    word_dist_list = []
    all_list = []
    relative_word_list = []

    # for nouns,count in noun_array.items():
    #     if area == nouns:
    #         p_timei_and_word = count / noun_sum
    #         print(p_timei_and_word)

    print(list(noun_list['noun']))

    for i in range(1):
        #area = df_area.iat[i,0]
        for i, noun in enumerate(list(noun_list['noun'])):
            word_dist = 0
            p_timei_and_word = 0
            p_timei_or_word = 0
            p_word = int(noun_list.iat[i, 1])
            for sentence in sentence_list:
                area_num_list = []
                noun_num_list = []
                if area != noun:
                    if area in sentence:
                        if noun in sentence:
                            # for nouns,count in noun_array.items():
                            #     if noun == nouns:
                            #         p_word = count / noun_sum
                            sentences = splitSentence(sentence)
                            area_num_list = inclusiveIndex(sentences, area)
                            noun_num_list = inclusiveIndex(sentences, noun)
                            dist_list = []
                            for i in range(len(area_num_list)):
                                for j in range(len(noun_num_list)):
                                    dist_list.append(abs(area_num_list[i] - noun_num_list[j]) + 1)
                            # print(area,noun, area_num_list, noun_num_list)
                            dist = min(dist_list)
                            # print(dist)
                            if dist == 1:
                                p_timei_and_word += 1
                            word_dist = word_dist + (1 / dist)
                # noun_u = list(noun_list['count'].astype(int))
                # noun_sum = sum(noun_u)
                # print(noun_sum, noun, area)
            p_timei_or_word = (p_timei_and_word / p_word)
                    # word_dist_list.append(word_dist)
            print(p_timei_or_word, int(df_area.iat[413,1]), word_dist)
            relative = (p_timei_or_word * word_dist) / int(df_area.iat[413,1])
            relative_word_list.append(relative)
                    # relative_word_list.append((word_dist / int(df_area.iat[name,1])))
            array = {
                    "noun": noun,
                    "relative": relative,
                    "dist": word_dist
                }
            all_list.append(array)

    df_text = pd.DataFrame(all_list)
    df_sorted = df_text.sort_values('relative')
    df_sorted.to_csv('data/beta/' + choumei[0] + '.csv', index = False)



def inclusiveIndex(list, string):
    dist_list = []
    for i, e in enumerate(list):
        if string in e:
            # print(e)
            # print(string)
            dist_list.append(i)
        # raise IndexError
    return dist_list

def calcRelative(df_area, df_noun, sentence_list):
    nlp = spacy.load('ja_ginza')
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns([
        {"label": "City", "pattern": "住吉町"}
    ])

    area_list = list(df_area['area'])
    noun_list = list(df_noun['noun'])

    data_list = []
    stop_word_list = ["函館", "道南", "函館市", "北海道", "北海", "箱館", "はこだて", "小学", "15", "14", "昭和", "明治", "大正"]

    choumei_data = readCSV('data/dic/choumei.csv')
    bunkazai_data = readCSV('data/bunkazai/bunkazai_idokeido.csv')
    chomei_list = list(choumei_data['a'])
    bunkazai_list = list(bunkazai_data['place'])
    chomei_list.extend(bunkazai_list)
    place_list = chomei_list



    desc_taika = ["昭和9年3月21日午後6時53分、函館市住吉町の民家より発火した火災は、風速20余メートルにおよぶ東南の烈風に煽られて火勢劇烈を極め、瞬時にして他に延焼拡大していった。", "物凄い火炎は、青柳町より豊川町、鶴岡町、松風町、新川町方面を襲い、消防隊や軍隊等の必死の努力も、烈風と倒壊した家屋や電柱等の障害物に妨げられ、充分なる機能を発揮することが出来なかったのである。", "その後、風向が漸次西方に変化するに伴って末広町、会所町、元町方面は幸いに二十間坂によって延焼を遮断することが出来たが、反対に風下にあたる新川町、堀川町、的場町の間は全く廃墟に帰し、さらに北方に向かって延焼し、翌22日午前6時頃に鎮火することができたのである。", "実に、全市の3分の1を焼失したのである(『函館大火災害史』)。", "大火の被害が大きかった原因を、当時の建築学会による報告書は、「一.発火より消防署に於て知覚するまでに約五分を要したこと、二.風力甚大で火災の伝播速度大且飛火多く尚風向の旋転方向亦最悪的であった事、三.火元付近は特に地形の関係に依り延焼中頻りに風の旋転、突風起りし事、四.発火地点及海岸付近は特に矮小粗悪木造家屋連担し且全市に亘り粗雑木造家屋が多かった事、五.防火地区極めて尠く、広場、公園等の都市計画上の施設が完備して居なかった事、六.発火地点は水道終点である為め水圧弱く水量乏しく、加ふるに風力強き為めに消防組の活動意の如く行われなかった事、七.道路概して狭隘にして消防組の部署変更に困難なりし事」(『函館大火災(昭和9年3月21日)調査報告』)と説明しており都市計画事業との関連性を想起させている。"]

    for sentence in range(1):
        for i in range(len(desc_taika)):
            doc = nlp(desc_taika[i])
            nouns = []
            places = []
            for tok in doc:
                if tok.pos_ in ('NOUN','PROPN'):
                    if tok.text in noun_list:
                        if tok.text not in area_list:
                            if tok.text not in stop_word_list:
                                nouns.append(tok.text)
            for place in place_list:
                if desc_taika[i].find(place) != -1:
                    if place != "柳町":
                        places.append(place)
            data = {
                "place": places,
                "nouns": nouns
            }
            if len(places) > 0 and len(nouns) > 0:
                data_list.append(data)


    sum_list = []

    for i in range(len(data_list)):
        data_place = data_list[i]
        place_data = data_place["place"]

        for place in place_data:
            sum = 0
            for j in range(len(data_list)):
                data_noun = data_list[j]
                noun_data = data_noun["nouns"]
                dist = 0
                choumei_relative = readCSVWithIndex('data/beta/'+ place +'.csv')
                for noun in noun_data:
                    relative = float(choumei_relative.loc[noun, "relative"])
                    dist = (1 / ((abs((i + 1) - (j + 1))) + 1))
                    sum += relative * dist
            relative_data = {
                "place": place,
                "relative": sum
            }
            sum_list.append(relative_data)

    data_list = []

    for sum in sum_list:
        aplha = 0.5
        beta = 2
        theta = 0.3
        cluster = 0.5

        upper_divide = (1 + ((beta ** 2) * cluster)) * sum["relative"]
        lower_divide = ((beta ** 2) * cluster) + sum["relative"]

        relation = upper_divide / lower_divide
        data = {
            "place": sum["place"],
            "relation": relation
        }
        data_list.append(data)

    writeCSV('data/beta/relation.csv', data_list)

def readCSV(path):
    df = pd.read_csv(path)
    return df.astype(str)

def readCSVWithIndex(path):
    df = pd.read_csv(path, index_col=0)
    return df.astype(str)

def writeCSV(path, data):
    df = pd.DataFrame(data)
    df.to_csv(path, index = False)


def main():
    # choumei = extractChoumeiFromCsv("choumei")
    # jinbutu = extractChoumeiFromCsv("jinbutu")
    # print(jinbutu)
    # bunkazai = extractChoumeiFromCsv("bunkazai")
    # print(bunkazai)

    # desc_taika = readDescriptionFromTxt("taika")
    # desc_tokitou = readDescriptionFromTxt("tokitou")
    # desc_hiratuka = readDescriptionFromTxt("hiratuka")

    desc_shishi = readHakodateShishi()
    df = createDataFrame(desc_shishi)
    keitaisokaiseki(df)


    # outputChoumeiDic(choumei)
    # outputAllDic(choumei,jinbutu,bunkazai)

    # m = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    # print(m.parse(desc_taika))
    # result = m.parse(desc_tokitou)
    # result = m.parse(desc_taika)
    #result = m.parse(desc_hiratuka)
    # csv_text = result.split("n")
    # csv_file = open("desc_taika.csv", "w")
    # csv_file = open("desc_tokitou.csv", "w")
    # csv_file = open("desc_hiratuka.csv", "w")
    # csv_file.writelines(csv_text)
    # lines = result.split('\n')
    
    # noun_list= []
    # unique_noun_list = []
    # noun_area_list = []
    # noun_person_list = []

    # noun_detail_area_list =[]
    # noun_detail_person_list = []

    # for line in lines:
    #     feature = line.split('\t')
    #     if len(feature) == 2: #'EOS'と''を省く
    #         info = feature[1].split(',')
    #         hinshi = info[0]
    #         hinshi_detail = info[1]
    #         hinshi_irex = info[2]
    #         if hinshi == '名詞' and hinshi_detail == '固有名詞' and hinshi_irex == "地域":
    #             noun_area_list.append(info[6])
    #             noun_detail_area_list.append(info)
    #         elif hinshi == '名詞' and hinshi_detail == '固有名詞' and hinshi_irex == "人名":
    #             noun_person_list.append(info[6])
    #             noun_detail_person_list.append(info)
    #         elif hinshi == '名詞' and hinshi_detail == '固有名詞':
    #             unique_noun_list.append(info[6])
    #         elif hinshi == '名詞':
    #             noun_list.append(info[6])
    
    # # print(noun_detail_area_list)
    # # print(noun_detail_person_list)
    # # print(noun_area_list)
    # # print(noun_person_list)
    # # # data = []
    # # # data.append(noun_detail_area_list)

    # # # with open('./data/koyuhyougen/desc_hiratuka.csv', 'w') as file:
    # # #     writer = csv.writer(file, lineterminator=',')
    # # #     writer.writerows(data[0])

    # area_name_list = []
    # area_x_list = []
    # area_y_list = []
    # for noun_area in noun_area_list:
    #     for i in range(choumei.shape[0]):
    #         if noun_area == choumei.iat[i, 0]:
    #             if noun_area not in area_name_list:
    #                 convert_idokeido = convertWGS84ToJGD2011(choumei.iat[i, 1], choumei.iat[i, 2])
    #                 area_name_list.append(noun_area)
    #                 area_x_list.append(convert_idokeido[0])
    #                 area_y_list.append(convert_idokeido[1])
    #     for j in range(bunkazai.shape[0]):
    #         if noun_area == bunkazai.iat[j, 0]:
    #             if noun_area not in area_name_list:
    #                 convert_idokeido = convertWGS84ToJGD2011(bunkazai.iat[j, 1], bunkazai.iat[j, 2])
    #                 area_name_list.append(noun_area)
    #                 area_x_list.append(convert_idokeido[0])
    #                 area_y_list.append(convert_idokeido[1])

    # data = {
    #     "name": area_name_list,
    #     "x": area_x_list,
    #     "y": area_y_list
    # }

    # df = pd.DataFrame(data)
    # df.to_csv('data/adress/place_convert.csv', index = False)

    # df = pd.read_csv('data/adress/place_convert.csv', index_col=0)

    # linkage_result = linkage(df, method='ward', metric='euclidean')
    # plt.figure(num=None, figsize=(16, 9), dpi=120, facecolor='w', edgecolor='k')
    # dendrogram(linkage_result, labels=df.index)
    # plt.show()

    # clusters = fcluster(linkage_result, 10, criterion = 'distance')
 
    # plt.figure(num = None, figsize = (16, 9), dpi = 120, facecolor = 'w', edgecolor = 'k')
    # dendrogram(clusters, labels = df.index)
    # plt.show()


    #print(m.parse(desc_hiratuka))


if __name__ == "__main__":
    main()