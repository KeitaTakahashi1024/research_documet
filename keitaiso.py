from os import error
import pandas as pd
import MeCab
import requests, json, time

def extractChoumeiFromCsv():
    choumeiData = pd.read_csv('data/read/choumei_idokeido.csv')
    return choumeiData.astype(str)

def main():
    choumei = extractChoumeiFromCsv()
    print(choumei)
    #m = MeCab.Tagger("-d /usr/local/lib/mecab/dic/ipadic")
    #data = "昭和9年3月21日午後6時53分、函館市住吉町の民家より発火した火災は、風速20余メートルにおよぶ東南の烈風に煽られて火勢劇烈を極め、瞬時にして他に延焼拡大していった。物凄い火炎は、青柳町より豊川町、鶴岡町、松風町、新川町方面を襲い、消防隊や軍隊等の必死の努力も、烈風と倒壊した家屋や電柱等の障害物に妨げられ、充分なる機能を発揮することが出来なかったのである。その後、風向が漸次西方に変化するに伴って末広町、会所町、元町方面は幸いに二十間坂によって延焼を遮断することが出来たが、反対に風下にあたる新川町、堀川町、的場町の間は全く廃墟に帰し、さらに北方に向かって延焼し、翌22日午前6時頃に鎮火することができたのである。実に、全市の3分の1を焼失したのである（『函館大火災害史』）。"
    #print(m.parse(data))


if __name__ == "__main__":
    main()