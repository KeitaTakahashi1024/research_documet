from os import read
from pandas.io.parsers import read_csv
import spacy
import pandas as pd
import re
import collections
from spacy.pipeline import EntityRuler


def main():
    # doc_data = readCSV('data/read/hakodate_shishi.csv')
    # doc_fix_data = fixData(doc_data)
    # writeCSV('data/read/fix_test_test_hakodate_shishi.csv', doc_fix_data)
    doc_data = readCSV('data/read/fix_test_hakodate_shishi.csv')
    place_data = readCSV('data/dic/place.csv')

    # nounWriteCSV(doc_data, place_data)



    choumei_data = readCSV('data/dic/choumei.csv')
    bunkazai_data = readCSV('data/bunkazai/bunkazai_idokeido.csv')
    chomei_list = list(choumei_data['a'])
    bunkazai_list = list(bunkazai_data['place'])
    chomei_list.extend(bunkazai_list)
    place_list = chomei_list
    print(place_list)
    # cityWriteCSV(doc_data, place_data)

def readCSV(path):
    df = pd.read_csv(path)
    return df.astype(str)

def writeCSV(path, data):
    df = pd.DataFrame(data)
    df.to_csv(path, index = False)

def fixData(data):
    data_size = data.shape[0]
    table = str.maketrans({
        '\u3000': '',
        ' ': '',
        '\t': ''
    })
    fix_data_list = []

    for i in range(data_size):
        desc = data.iat[i, 2].translate(table)
        desc = ''.join(desc.splitlines())
        desc = delete_brackets(desc)
        fix_data_list.append(desc)


    return fix_data_list

def delete_brackets(s):
    """
    括弧と括弧内文字列を削除
    """
    """ brackets to zenkaku """
    table = {
        "(": "（",
        ")": "）",
        "<": "＜",
        ">": "＞",
        "{": "｛",
        "}": "｝",
        "[": "［",
        "]": "］"
    }
    for key in table.keys():
        s = s.replace(key, table[key])
    """ delete zenkaku_brackets """
    l = ['（[^（|^）]*）', '【[^【|^】]*】', '＜[^＜|^＞]*＞', '［[^［|^］]*］',
         '「[^「|^」]*」', '｛[^｛|^｝]*｝', '〔[^〔|^〕]*〕', '〈[^〈|^〉]*〉']
    for l_ in l:
        s = re.sub(l_, "", s)
    """ recursive processing """
    return delete_brackets(s) if sum([1 if re.search(l_, s) else 0 for l_ in l]) > 0 else s

def namedEntityRecognition(doc_data, place_data_list):
    nlp = spacy.load('ja_ginza')
    ruler = EntityRuler(nlp)
    ruler = nlp.add_pipe("entity_ruler")
    ruler.add_patterns([
        {"label": "Era", "pattern": "昭和"},
        {"label": "Era", "pattern": "明治"},
        {"label": "Era", "pattern": "大正"},
    ])
    doc = nlp(doc_data)

    noun_list = []
    stop_word_list = ["函館", "道南", "函館市", "北海道", "北海", "箱館", "はこだて", "小学", "15", "14"]

    pattern = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]')

    for tok in doc:
        if tok.pos_ in ('NOUN','PROPN'):
            if tok.text not in place_data_list:
                strip_span = pattern.sub('', str(tok.text))
                if str(tok.text) not in place_data_list:
                    if len(str(strip_span)) >= 2:
                        noun_list.append(str(strip_span))

    # 名詞句を抽出
    # for span in doc.noun_chunks:
    #     if str(span) not in place_data_list:
    #         strip_span = pattern.sub('', str(span))
    #         noun_list.append(str(strip_span))

    # 名詞句を抽出
    # for ent in doc.ents:
    #     if ent.label_ not in ["Timex_Other", "Timeex", "Timeex_Other", "Time", "Date", "Day_Of_Week", "Era", "Periodx", "Periodx_Other", "Period_Time", "Period_Day", "Period_Week", "Period_Month", "Period_Year", "Numex_Other", "N_Person", "Temperature", "Percent", "Ordinal_Number", "Age", "Frequency", "GPE_Other", "N_Product", "Rank", "Weight", "Multiplication", "N_Location_Other", "N_Facility", "N_Organization", "Money", "N_Event", "Space", "Physical_Extent", "Calorie", "Countx_Other", "N_Country", "Point", "Measurement_Other", "Speed", "N_Animal"]:
    #         # if not ent.text.isdigit():
    #             #print(ent.text, ent.label_)
    #             if str(ent.text) not in place_data_list:
    #                 strip_span = pattern.sub('', str(ent.text))
    #                 if len(str(strip_span)) >= 2:
    #                     for j in range(len(stop_word_list)):
    #                         if str(strip_span) != stop_word_list[j]:
    #                             data = {
    #                                 "noun": str(strip_span),
    #                                 "label": ent.label_
    #                             }
    #                             print(stop_word_list[j])
    #                             noun_list.append(data)


    return noun_list

def nounWriteCSV(doc_data, place_data):
    doc_data_size = doc_data.shape[0]
    place_data_list = list(place_data['a'])

    noun_list = []
    label_list = []
    for i in range(doc_data_size):
        nouns = namedEntityRecognition(doc_data.iat[i,0], place_data_list)
        print(nouns)
        noun_list.extend(nouns)

    # cont_noun_list = [d.get('noun') for d in noun_list]
    # label_list = [d.get('label') for d in noun_list]

    # noun_array = collections.Counter(cont_noun_list)
    # noun_list = []
    # count_list = []
    # new_label_list = []
    # noun_sum = 0
    # for noun,count in noun_array.items():
    #     if count >= 10:
    #         index = cont_noun_list.index(noun)
    #         noun_list.append(noun)
    #         count_list.append(count)
    #         new_label_list.append(label_list[index])
    # for noun,count in noun_array.items():
    #     noun_sum += count

    # print(noun_list)

    # data = {
    #     "noun": noun_list,
    #     "count": count_list,
    #     "label": new_label_list
    # }
    # writeCSV('data/hakodate_shishi/nouns.csv', data)

    noun_array = collections.Counter(noun_list)
    noun_list = []
    count_list = []
    noun_sum = 0
    for noun,count in noun_array.items():
        if count >= 10:
            noun_list.append(noun)
            count_list.append(count)
    for noun,count in noun_array.items():
        noun_sum += count

    print(noun_list)

    data = {
        "noun": noun_list,
        "count": count_list,
    }
    writeCSV('data/hakodate_shishi/nouns_2.csv', data)

def cityWriteCSV(doc_data, place_data):
    doc_data_size = doc_data.shape[0]
    place_data_list = list(place_data['a'])


if __name__ == "__main__":
    main()
