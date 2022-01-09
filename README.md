# research_documet

### 辞書の追加方法
1. 追加したい単語を以下のような形式で設定する。
    表層形,左文脈ID,右文脈ID,コスト,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用型,活用形,原形,読み,発音
    例）
    ユーザ設定,,,10,名詞,一般,*,*,*,*,ユーザ設定,ユーザセッテイ,ユーザセッテイ,追加エントリ

2. 設定した形式をCSV形式で任意の場所に保存する。
3. 保存したフォルダの場所に移動する。
4. 以下のコマンドを実行する。
    mecab-dict-index -d [システム辞書があるディレクトリ] -u [オリジナル辞書.csv] -f [CSVの文字コード] -t [バイナリ辞書の文字コード]
    /usr//local/Cellar/mecab/0.996/libexec/mecab/mecab-dict-index -d /usr/local/lib/mecab/dic/ipadic -u place.dic -f utf-8 -t utf-8 place.csv
    - システム辞書があるディレクトリの探し方
        - sudo find /usr/ -name mecab-dict-index
    - オリジナル辞書.csv
        - 適当にわかりやすい名前を設定する
    - CSVの文字コード
        - 任意の文字こーど
            - 例）uff-8
    - バイナリ辞書の文字コード
        - CSVの文字コードと同じ
    実行したらcsvがあるディレクトリにdicファイルが生成される。
5. 生成されたファイルを読み込めるようにする
    vi /usr/local/etc/mecabrcを実行する。
    userdic = 生成されたdicファイルのパスを記述する。
    これで終わり。