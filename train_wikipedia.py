# 学習データの準備
import json
import spacy
import random

labels = {
    '人名':           'Person',
    '法人名':         'Juridical_Person',
    '政治的組織名':   'Political_Organization',
    'その他の組織名': 'Organization_Other',
    '地名':           'Location',
    '施設名':         'Facility',
    '製品名':         'Product',
    'イベント名':     'Event',
}

def train_ner(train_data, epoch):
    # 日本語の空モデルの生成
    nlp = spacy.blank('ja')

    # 固有表現抽出のパイプの追加
    if 'ner' not in nlp.pipe_names:
        nlp.add_pipe("ner", last=True)

    # ラベルの追加
    for _, annotations in train_data:
        for ent in annotations.get('entities'):
            nlp.add_label(ent[2])

    # 固有表現抽出のみ学習
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):
        optimizer = nlp.begin_training()
       
        # 学習ループ
        for itn in range(epoch):
            # シャッフル
            random.shuffle(train_data)
           
            # 学習
            losses = {}
            for text, annotations in train_data:
                nlp.update([text], [annotations], drop=0.2, sgd=optimizer, losses=losses)
            print('iteration'+str(itn)+': '+str(losses['ner']))
    return nlp

def main():
    json_data = json.load(open('./data/read/ner.json', 'r'))
    train_data = []
    for data in json_data:
        text = data['text']
        entities = data['entities']
        value = []
        for entity in entities:
            span = entity['span']
            label = labels[entity['type']]
            value.append((span[0], span[1], label))
        train_data.append((text, {'entities': value}))



    # 固有表現抽出モデルの学習
    nlp = train_ner(train_data, 100)

    # 固有表現抽出モデルの保存
    nlp.to_disk('ner_model')

    nlp = spacy.load('ner_model')
    doc = nlp("昭和9年3月21日午後6時53分、函館市住吉町の民家より発火した火災は、風速20余メートルにおよぶ東南の烈風に煽られて火勢劇烈を極め、瞬時にして他に延焼拡大していった。")

    for sent in doc.sents:
        for token in sent:
            if token.pos_ == "PROPN":
                print(token.orth_, token.tag_)
        print('EOS')

if __name__ == "__main__":
    main()