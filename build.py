#!/usr/bin/env python3
"""
Build script to generate the Tokyo Rental Map HTML application.
Embeds GeoJSON data and rental information into a single self-contained HTML file.
"""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_PATH = os.path.join(SCRIPT_DIR, "data", "tokyo_municipalities.geojson")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "index.html")

# Tokyo municipality data: rent, population, description, etc.
# Rent: average monthly rent for 1K/1DK apartment in万円 (ten-thousands of yen)
# Population: approximate as of 2024
MUNICIPALITY_DATA = {
    "13101": {
        "name": "千代田区",
        "rent": 12.8,
        "population": 67000,
        "area_km2": 11.66,
        "stations": "東京, 秋葉原, 神保町, 大手町",
        "description": "皇居を中心とした東京の政治・経済の中心地。丸の内・大手町のオフィス街、秋葉原の電気街、神保町の古書店街など多彩な顔を持つ。住民は少ないが、昼間人口は約85万人に達する。",
        "highlights": "皇居, 東京駅, 秋葉原電気街, 神保町古書店街"
    },
    "13102": {
        "name": "中央区",
        "rent": 12.5,
        "population": 187000,
        "area_km2": 10.21,
        "stations": "銀座, 日本橋, 築地, 人形町",
        "description": "銀座・日本橋を擁する商業の中心地。築地場外市場や月島のもんじゃストリートなど食文化も豊か。近年はタワーマンションの建設が進み、人口が急増している。",
        "highlights": "銀座, 日本橋, 築地場外市場, 月島もんじゃ"
    },
    "13103": {
        "name": "港区",
        "rent": 13.5,
        "population": 260000,
        "area_km2": 20.37,
        "stations": "六本木, 赤坂, 品川, 新橋, 表参道",
        "description": "六本木・赤坂・青山など華やかなエリアを多数抱える高級住宅地。大使館が多く国際色豊か。東京タワーやお台場など観光スポットも充実。IT企業の集積地でもある。",
        "highlights": "東京タワー, 六本木ヒルズ, お台場, 大使館街"
    },
    "13104": {
        "name": "新宿区",
        "rent": 10.8,
        "population": 349000,
        "area_km2": 18.22,
        "stations": "新宿, 高田馬場, 四ツ谷, 神楽坂",
        "description": "世界一の乗降客数を誇る新宿駅を中心とした一大ターミナル。歌舞伎町の繁華街から神楽坂の情緒ある街並みまで、多様な表情を持つ。早稲田大学など学生の街でもある。",
        "highlights": "新宿御苑, 歌舞伎町, 都庁展望台, 神楽坂"
    },
    "13105": {
        "name": "文京区",
        "rent": 10.5,
        "population": 240000,
        "area_km2": 11.29,
        "stations": "後楽園, 本郷三丁目, 茗荷谷, 千駄木",
        "description": "東京大学をはじめとする教育機関が集中する文教地区。治安が良く、落ち着いた住環境が魅力。小石川後楽園や六義園など名園も多い。子育て世帯に人気のエリア。",
        "highlights": "東京大学, 東京ドーム, 六義園, 小石川後楽園"
    },
    "13106": {
        "name": "台東区",
        "rent": 10.0,
        "population": 213000,
        "area_km2": 10.11,
        "stations": "上野, 浅草, 御徒町, 蔵前",
        "description": "浅草寺・上野公園など東京の下町文化を色濃く残すエリア。アメ横の活気、谷根千の情緒、蔵前のクリエイティブタウンなど新旧が融合。面積は23区最小。",
        "highlights": "浅草寺, 上野公園, アメ横, 東京国立博物館"
    },
    "13107": {
        "name": "墨田区",
        "rent": 9.5,
        "population": 275000,
        "area_km2": 13.77,
        "stations": "錦糸町, 押上, 両国, 曳舟",
        "description": "東京スカイツリーのお膝元。両国の相撲文化、向島の花街文化など伝統が息づく下町。錦糸町は商業の中心で利便性が高い。近年は再開発で若い世代の流入が増加。",
        "highlights": "東京スカイツリー, 両国国技館, 江戸東京博物館"
    },
    "13108": {
        "name": "江東区",
        "rent": 10.2,
        "population": 524000,
        "area_km2": 40.16,
        "stations": "豊洲, 門前仲町, 亀戸, 清澄白河",
        "description": "豊洲市場の移転で注目を集めるウォーターフロントエリア。有明・お台場のベイエリアから深川の下町まで幅広い魅力。清澄白河はカフェの街として人気急上昇中。",
        "highlights": "豊洲市場, 清澄白河カフェ街, 有明アリーナ"
    },
    "13109": {
        "name": "品川区",
        "rent": 10.8,
        "population": 422000,
        "area_km2": 22.84,
        "stations": "品川, 目黒, 大井町, 武蔵小山",
        "description": "品川駅を中心にリニア中央新幹線の始発駅として将来性が高い。天王洲アイルの運河沿い、戸越銀座商店街の下町情緒、武蔵小山のアーケードなど多彩なエリア。",
        "highlights": "品川駅, 戸越銀座商店街, 天王洲アイル, しながわ水族館"
    },
    "13110": {
        "name": "目黒区",
        "rent": 11.2,
        "population": 282000,
        "area_km2": 14.67,
        "stations": "中目黒, 自由が丘, 学芸大学, 都立大学",
        "description": "中目黒・自由が丘を擁するおしゃれエリアの代表格。目黒川の桜並木は東京屈指の花見スポット。学芸大学・祐天寺周辺は落ち着いた住宅街で人気が高い。",
        "highlights": "中目黒, 自由が丘, 目黒川の桜, 東京都写真美術館"
    },
    "13111": {
        "name": "大田区",
        "rent": 8.8,
        "population": 741000,
        "area_km2": 60.83,
        "stations": "蒲田, 大森, 田園調布, 羽田空港",
        "description": "羽田空港を擁する23区最大の面積を持つ区。田園調布の高級住宅街から蒲田の庶民的な街まで多様。町工場が集積するモノづくりの街としても有名。",
        "highlights": "羽田空港, 田園調布, 蒲田温泉街, 池上本門寺"
    },
    "13112": {
        "name": "世田谷区",
        "rent": 9.5,
        "population": 920000,
        "area_km2": 58.05,
        "stations": "三軒茶屋, 下北沢, 二子玉川, 成城学園前",
        "description": "23区最大の人口を誇る住宅都市。三軒茶屋・下北沢のカルチャータウン、二子玉川の商業施設、成城の高級住宅街など個性豊かなエリアが点在する。緑も多い。",
        "highlights": "下北沢, 三軒茶屋, 二子玉川ライズ, 等々力渓谷"
    },
    "13113": {
        "name": "渋谷区",
        "rent": 12.0,
        "population": 243000,
        "area_km2": 15.11,
        "stations": "渋谷, 原宿, 恵比寿, 代官山",
        "description": "若者文化とIT企業の中心地。渋谷スクランブル交差点は世界的に有名。原宿・表参道のファッション、恵比寿・代官山の洗練された雰囲気など、トレンドの発信地。",
        "highlights": "渋谷スクランブル, 原宿竹下通り, 代官山, 明治神宮"
    },
    "13114": {
        "name": "中野区",
        "rent": 8.5,
        "population": 344000,
        "area_km2": 15.59,
        "stations": "中野, 東中野, 新中野, 中野坂上",
        "description": "中野ブロードウェイのサブカルチャー聖地として知られる。新宿へのアクセスが良く、家賃も比較的手頃で単身者に人気。中野サンプラザ跡地の再開発が進行中。",
        "highlights": "中野ブロードウェイ, 中野サンプラザ, 哲学堂公園"
    },
    "13115": {
        "name": "杉並区",
        "rent": 8.2,
        "population": 580000,
        "area_km2": 34.06,
        "stations": "荻窪, 阿佐ヶ谷, 高円寺, 西荻窪",
        "description": "中央線沿線の個性豊かな街が連なる。高円寺の古着とライブハウス、阿佐ヶ谷のジャズと商店街、荻窪のラーメン激戦区。住環境と文化的魅力を兼ね備えた人気エリア。",
        "highlights": "高円寺阿波おどり, 阿佐ヶ谷商店街, 善福寺公園"
    },
    "13116": {
        "name": "豊島区",
        "rent": 9.8,
        "population": 301000,
        "area_km2": 13.01,
        "stations": "池袋, 巣鴨, 大塚, 目白",
        "description": "池袋を中心としたターミナル区。サンシャインシティ、乙女ロードなどエンターテイメントが充実。巣鴨の「おばあちゃんの原宿」も有名。国際アート・カルチャー都市を標榜。",
        "highlights": "池袋サンシャインシティ, 巣鴨地蔵通り, 雑司が谷"
    },
    "13117": {
        "name": "北区",
        "rent": 8.3,
        "population": 355000,
        "area_km2": 20.61,
        "stations": "赤羽, 王子, 十条, 田端",
        "description": "赤羽の飲み屋街が「せんべろ」の聖地として注目を集める。十条商店街は東京屈指の安さを誇る。王子の飛鳥山公園は桜の名所。都心へのアクセスが良く、コスパの高い街。",
        "highlights": "赤羽飲み屋街, 飛鳥山公園, 十条商店街"
    },
    "13118": {
        "name": "荒川区",
        "rent": 8.5,
        "population": 217000,
        "area_km2": 10.16,
        "stations": "日暮里, 西日暮里, 町屋, 南千住",
        "description": "都電荒川線が走る下町情緒あふれるエリア。日暮里は繊維街と成田空港へのアクセスが魅力。南千住は再開発で住環境が向上。あらかわ遊園は都内唯一の区営遊園地。",
        "highlights": "都電荒川線, 日暮里繊維街, あらかわ遊園"
    },
    "13119": {
        "name": "板橋区",
        "rent": 7.8,
        "population": 584000,
        "area_km2": 32.22,
        "stations": "板橋, 成増, 志村三丁目, 大山",
        "description": "大山商店街ハッピーロードは都内有数の活気ある商店街。都心へのアクセスが良く、家賃もリーズナブルで若い世代に人気。光学・精密機器のメーカーが多い工業の街でもある。",
        "highlights": "大山ハッピーロード, 板橋区立美術館, 赤塚植物園"
    },
    "13120": {
        "name": "練馬区",
        "rent": 7.5,
        "population": 750000,
        "area_km2": 48.08,
        "stations": "練馬, 石神井公園, 光が丘, 大泉学園",
        "description": "23区で2番目に人口が多い住宅区。日本のアニメ産業発祥の地で多くのアニメスタジオが所在。石神井公園や光が丘公園など緑豊かな環境。都心へのアクセスも改善中。",
        "highlights": "石神井公園, 練馬区立美術館, としまえん跡地"
    },
    "13121": {
        "name": "足立区",
        "rent": 7.0,
        "population": 695000,
        "area_km2": 53.25,
        "stations": "北千住, 綾瀬, 西新井, 竹ノ塚",
        "description": "北千住は5路線が乗り入れる交通の要所で、「穴場の街」ランキング常連。大学キャンパスの誘致で街のイメージが刷新。家賃の安さと利便性のバランスが良い。",
        "highlights": "北千住, 西新井大師, 舎人公園, 足立の花火"
    },
    "13122": {
        "name": "葛飾区",
        "rent": 7.2,
        "population": 453000,
        "area_km2": 34.80,
        "stations": "亀有, 金町, 新小岩, 柴又",
        "description": "「こちら葛飾区亀有公園前派出所」や「男はつらいよ」の舞台として知られる。柴又帝釈天の門前町は昭和の風情を残す。家賃が手頃で、下町の温かみがある住環境。",
        "highlights": "柴又帝釈天, 亀有こち亀像, 水元公園"
    },
    "13123": {
        "name": "江戸川区",
        "rent": 7.3,
        "population": 698000,
        "area_km2": 49.90,
        "stations": "小岩, 葛西, 西葛西, 船堀",
        "description": "インド人コミュニティで知られる西葛西など、多文化共生が進むエリア。葛西臨海公園は水族園もある人気スポット。子育て支援が充実し、ファミリー層に人気。",
        "highlights": "葛西臨海公園, 葛西臨海水族園, 小岩商店街"
    },
    "13201": {
        "name": "八王子市",
        "rent": 5.2,
        "population": 578000,
        "area_km2": 186.38,
        "stations": "八王子, 高尾, 南大沢, めじろ台",
        "description": "東京都で最大の面積を持つ多摩地域の中核都市。23の大学が集まる学園都市。高尾山は年間300万人が訪れるハイキングの名所。アウトレットモールなど商業施設も充実。",
        "highlights": "高尾山, 三井アウトレットパーク, 八王子城跡"
    },
    "13202": {
        "name": "立川市",
        "rent": 6.5,
        "population": 185000,
        "area_km2": 24.36,
        "stations": "立川, 西国立, 玉川上水",
        "description": "多摩地域の商業・業務の中心地。立川駅周辺は大型商業施設が林立。国営昭和記念公園は広大な緑地空間。多摩モノレールの結節点でもあり、交通利便性が高い。",
        "highlights": "国営昭和記念公園, ららぽーと立川立飛, IKEA立川"
    },
    "13203": {
        "name": "武蔵野市",
        "rent": 8.0,
        "population": 150000,
        "area_km2": 10.98,
        "stations": "吉祥寺, 三鷹, 武蔵境",
        "description": "「住みたい街ランキング」常連の吉祥寺を擁する。井の頭恩賜公園の豊かな自然、ハモニカ横丁の昭和レトロ、おしゃれなカフェや雑貨店が共存する魅力的な街。",
        "highlights": "吉祥寺, 井の頭恩賜公園, ハモニカ横丁"
    },
    "13204": {
        "name": "三鷹市",
        "rent": 7.3,
        "population": 195000,
        "area_km2": 16.42,
        "stations": "三鷹, 井の頭公園, つつじヶ丘",
        "description": "太宰治や山本有三ゆかりの文学の街。三鷹の森ジブリ美術館は世界中からファンが訪れる。井の頭公園に隣接し、緑豊かで落ち着いた住環境。都心へのアクセスも良好。",
        "highlights": "三鷹の森ジブリ美術館, 井の頭恩賜公園, 山本有三記念館"
    },
    "13205": {
        "name": "青梅市",
        "rent": 4.8,
        "population": 132000,
        "area_km2": 103.31,
        "stations": "青梅, 河辺, 東青梅",
        "description": "奥多摩への玄関口で自然が豊か。御岳山や多摩川の渓谷美が楽しめる。青梅マラソンは日本最古の市民マラソン。昭和レトロな映画看板の街並みでも知られる。",
        "highlights": "御岳山, 青梅マラソン, 吉川英治記念館"
    },
    "13206": {
        "name": "府中市",
        "rent": 6.3,
        "population": 262000,
        "area_km2": 29.43,
        "stations": "府中, 分倍河原, 府中本町",
        "description": "大國魂神社の門前町として栄えた歴史ある街。東京競馬場やサントリーのビール工場など見どころ多数。けやき並木は国の天然記念物。住環境と利便性のバランスが良い。",
        "highlights": "大國魂神社, 東京競馬場, サントリー武蔵野ビール工場"
    },
    "13207": {
        "name": "昭島市",
        "rent": 5.5,
        "population": 113000,
        "area_km2": 17.34,
        "stations": "昭島, 拝島, 中神",
        "description": "地下水100%の水道水が自慢の街。モリタウンなど大型商業施設があり買い物に便利。多摩川沿いの緑地が充実。くじら運動公園はアキシマクジラの化石発見地にちなむ。",
        "highlights": "モリタウン, 昭和の森, 多摩川緑地"
    },
    "13208": {
        "name": "調布市",
        "rent": 6.8,
        "population": 243000,
        "area_km2": 21.58,
        "stations": "調布, 仙川, つつじヶ丘, 国領",
        "description": "映画の街として知られ、日活撮影所や角川大映スタジオが所在。深大寺はそばの名所で観光地としても人気。味の素スタジアムはFC東京のホームグラウンド。",
        "highlights": "深大寺, 味の素スタジアム, 神代植物公園"
    },
    "13209": {
        "name": "町田市",
        "rent": 5.8,
        "population": 432000,
        "area_km2": 71.80,
        "stations": "町田, 鶴川, 成瀬, 多摩境",
        "description": "神奈川県に食い込むように位置する東京都南部の中核都市。駅前は百貨店や商業施設が立ち並ぶ一大ショッピングタウン。薬師池公園は「新東京百景」に選ばれている。",
        "highlights": "町田駅前商業エリア, 薬師池公園, リス園"
    },
    "13210": {
        "name": "小金井市",
        "rent": 6.5,
        "population": 127000,
        "area_km2": 11.30,
        "stations": "武蔵小金井, 東小金井, 新小金井",
        "description": "小金井公園は都立公園でも最大級の広さを誇り、桜の名所として有名。東京学芸大学や法政大学のキャンパスがある学園都市。中央線沿線で都心へのアクセスも便利。",
        "highlights": "小金井公園, 江戸東京たてもの園, はけの森美術館"
    },
    "13211": {
        "name": "小平市",
        "rent": 5.5,
        "population": 198000,
        "area_km2": 20.51,
        "stations": "小平, 花小金井, 一橋学園",
        "description": "ブリヂストン技術センターなど企業の研究施設が集まる。玉川上水沿いの緑道は散策に最適。小平うどんは地元のソウルフード。一橋大学の小平キャンパスがある。",
        "highlights": "小平ふるさと村, 玉川上水, ブリヂストンTODAY"
    },
    "13212": {
        "name": "日野市",
        "rent": 5.5,
        "population": 190000,
        "area_km2": 27.55,
        "stations": "日野, 豊田, 高幡不動",
        "description": "新選組のふるさととして知られる歴史の街。高幡不動尊は関東三大不動の一つ。日野自動車の企業城下町。多摩動物公園は広大な敷地に約300種の動物を飼育。",
        "highlights": "高幡不動尊, 多摩動物公園, 新選組のふるさと"
    },
    "13213": {
        "name": "東村山市",
        "rent": 5.3,
        "population": 151000,
        "area_km2": 17.14,
        "stations": "東村山, 久米川, 秋津",
        "description": "志村けんの出身地として「東村山音頭」で全国に知られる。正福寺地蔵堂は国宝建造物。北山公園の菖蒲まつりは初夏の風物詩。自然豊かな住環境が魅力。",
        "highlights": "正福寺地蔵堂（国宝）, 北山公園菖蒲苑, 八国山"
    },
    "13214": {
        "name": "国分寺市",
        "rent": 6.2,
        "population": 130000,
        "area_km2": 11.46,
        "stations": "国分寺, 西国分寺, 恋ヶ窪",
        "description": "奈良時代の武蔵国分寺跡が市名の由来。崖線沿いの湧水群は「お鷹の道・真姿の池」として名水百選に選定。駅前再開発で商業施設が充実し、利便性が向上。",
        "highlights": "武蔵国分寺跡, お鷹の道, 殿ヶ谷戸庭園"
    },
    "13215": {
        "name": "国立市",
        "rent": 6.0,
        "population": 77000,
        "area_km2": 8.15,
        "stations": "国立, 谷保, 矢川",
        "description": "一橋大学を中心とした文教都市。大学通りの並木道は桜と紅葉の名所。谷保天満宮は東日本最古の天満宮。文教地区指定により景観が守られた美しい街並み。",
        "highlights": "一橋大学, 大学通り並木道, 谷保天満宮"
    },
    "13218": {
        "name": "福生市",
        "rent": 4.8,
        "population": 57000,
        "area_km2": 10.16,
        "stations": "福生, 牛浜, 拝島",
        "description": "横田基地に隣接しアメリカンな雰囲気が漂う街。国道16号沿いにはアメリカンテイストの店が並ぶ。多摩川中央公園など自然も豊か。七夕まつりは毎年40万人が訪れる。",
        "highlights": "横田基地周辺, 福生七夕まつり, 多摩川中央公園"
    },
    "13219": {
        "name": "狛江市",
        "rent": 6.5,
        "population": 84000,
        "area_km2": 6.39,
        "stations": "狛江, 和泉多摩川, 喜多見",
        "description": "東京都で最も面積が小さい市。多摩川沿いの穏やかな住環境が魅力。絵手紙発祥の地としてアートの街づくりを推進。新宿まで約20分とアクセスも良好。",
        "highlights": "多摩川河川敷, 絵手紙発祥の地, 和泉多摩川"
    },
    "13220": {
        "name": "東大和市",
        "rent": 5.0,
        "population": 85000,
        "area_km2": 13.42,
        "stations": "東大和市, 上北台, 玉川上水",
        "description": "多摩湖（村山貯水池）に面した自然豊かな街。旧日立航空機立川工場変電所は戦争遺跡として保存。多摩モノレールで立川へのアクセスが便利。",
        "highlights": "多摩湖, 東大和南公園, 旧日立航空機変電所"
    },
    "13221": {
        "name": "清瀬市",
        "rent": 5.0,
        "population": 76000,
        "area_km2": 10.19,
        "stations": "清瀬, 秋津",
        "description": "ひまわりフェスティバルの約10万本のひまわり畑が有名。結核療養所の歴史を持つ医療の街。柳瀬川沿いの緑地や市内各所の農地など、のどかな田園風景が残る。",
        "highlights": "清瀬ひまわりフェスティバル, 柳瀬川回廊, 中里富士"
    },
    "13222": {
        "name": "東久留米市",
        "rent": 5.2,
        "population": 117000,
        "area_km2": 12.88,
        "stations": "東久留米, ひばりヶ丘",
        "description": "落合川と南沢湧水群は東京都で唯一の「平成の名水百選」に選定。黒目川沿いは桜の名所。都心のベッドタウンとして発展しながら、豊かな水と緑が残る。",
        "highlights": "落合川・南沢湧水群, 黒目川桜並木, 竹林公園"
    },
    "13223": {
        "name": "武蔵村山市",
        "rent": 4.5,
        "population": 72000,
        "area_km2": 15.32,
        "stations": "（鉄道駅なし・多摩モノレール延伸予定）",
        "description": "東京都で唯一鉄道駅がない市。多摩モノレール延伸が待望される。かたくりの湯は天然温泉として人気。狭山丘陵の自然が残り、武蔵村山みかん園など農業体験も楽しめる。",
        "highlights": "かたくりの湯, 野山北・六道山公園, 狭山丘陵"
    },
    "13224": {
        "name": "多摩市",
        "rent": 5.5,
        "population": 148000,
        "area_km2": 21.01,
        "stations": "多摩センター, 聖蹟桜ヶ丘, 永山",
        "description": "多摩ニュータウンの中心地。サンリオピューロランドは年間を通じて人気のテーマパーク。聖蹟桜ヶ丘は映画「耳をすませば」の舞台として知られる。",
        "highlights": "サンリオピューロランド, 聖蹟桜ヶ丘, 多摩中央公園"
    },
    "13225": {
        "name": "稲城市",
        "rent": 5.5,
        "population": 93000,
        "area_km2": 17.97,
        "stations": "稲城, 稲城長沼, 南多摩, 若葉台",
        "description": "多摩丘陵に位置し、よみうりランドがある行楽の街。梨の産地として有名で、秋には梨狩りが楽しめる。南山の再開発で新しい住宅地も誕生。Jリーグの東京ヴェルディゆかり。",
        "highlights": "よみうりランド, 稲城の梨, 城山公園"
    },
    "13227": {
        "name": "羽村市",
        "rent": 4.5,
        "population": 55000,
        "area_km2": 9.90,
        "stations": "羽村, 小作",
        "description": "玉川上水の取水口がある「水のまち」。羽村堰は江戸時代からの歴史的構造物。チューリップまつりは約40万本の花が咲き誇る。羽村市動物公園は手頃な入園料で人気。",
        "highlights": "羽村堰, チューリップまつり, 羽村市動物公園"
    },
    "13228": {
        "name": "あきる野市",
        "rent": 4.5,
        "population": 80000,
        "area_km2": 73.47,
        "stations": "秋川, 武蔵引田, 武蔵増戸",
        "description": "秋川渓谷はBBQや川遊びの人気スポット。都心から1時間程度でアクセスできる自然豊かなエリア。瀬音の湯は天然温泉で日帰り入浴が楽しめる。",
        "highlights": "秋川渓谷, 瀬音の湯, 東京サマーランド"
    },
    "13229": {
        "name": "西東京市",
        "rent": 6.0,
        "population": 207000,
        "area_km2": 15.75,
        "stations": "田無, ひばりヶ丘, 保谷, 東伏見",
        "description": "田無市と保谷市が合併して誕生した市。スカイタワー西東京（田無タワー）がランドマーク。武蔵関公園など水辺の緑が豊か。都心へのアクセスが良く住みやすい街。",
        "highlights": "スカイタワー西東京, 武蔵関公園, いこいの森公園"
    },
    "13303": {
        "name": "瑞穂町",
        "rent": 4.2,
        "population": 33000,
        "area_km2": 16.85,
        "stations": "箱根ケ崎",
        "description": "狭山丘陵の南麓に位置する自然豊かな町。狭山池公園やさやま花多来里の郷のカタクリ群落が見どころ。横田基地の一部が町内にあり、日米友好祭も開催される。",
        "highlights": "狭山池公園, さやま花多来里の郷, 六道山公園"
    },
    "13305": {
        "name": "日の出町",
        "rent": 4.0,
        "population": 17000,
        "area_km2": 28.07,
        "stations": "武蔵引田（最寄り）",
        "description": "イオンモール日の出は西多摩地域最大の商業施設。つるつる温泉は日帰り温泉として人気。日の出山は初日の出スポットとして知られ、元旦には多くの登山者が訪れる。",
        "highlights": "イオンモール日の出, つるつる温泉, 日の出山"
    },
    "13307": {
        "name": "檜原村",
        "rent": 3.5,
        "population": 2000,
        "area_km2": 105.41,
        "stations": "（鉄道駅なし・武蔵五日市駅からバス）",
        "description": "東京都本土で唯一の村。面積の約93%が森林で、都民の水源地として重要。払沢の滝は日本の滝百選に選定。東京とは思えない大自然の中でキャンプや渓流釣りが楽しめる。",
        "highlights": "払沢の滝, 都民の森, 神戸岩"
    },
    "13308": {
        "name": "奥多摩町",
        "rent": 3.5,
        "population": 5000,
        "area_km2": 225.53,
        "stations": "奥多摩, 白丸, 鳩ノ巣, 古里",
        "description": "東京都最西端に位置する山岳の町。雲取山（東京都最高峰2,017m）を擁する。奥多摩湖は都民の水がめ。日原鍾乳洞や氷川渓谷など自然観光資源が豊富。",
        "highlights": "奥多摩湖, 雲取山, 日原鍾乳洞, 氷川渓谷"
    }
}


def build_html(geojson_data):
    """Build the complete HTML application."""

    geojson_str = json.dumps(geojson_data, ensure_ascii=False, separators=(',', ':'))
    data_str = json.dumps(MUNICIPALITY_DATA, ensure_ascii=False, indent=2)

    html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>東京都 市区町村別 平均賃貸マップ</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    background: #0a0a1a;
    color: #e0e0e0;
    overflow: hidden;
    height: 100vh;
  }}

  #header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    background: linear-gradient(135deg, #1a1a3e 0%, #0d0d2b 100%);
    border-bottom: 1px solid rgba(100, 140, 255, 0.3);
    padding: 12px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    backdrop-filter: blur(10px);
    height: 56px;
  }}

  #header h1 {{
    font-size: 18px;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.5px;
  }}

  #header h1 span {{
    color: #6c8cff;
  }}

  #header .subtitle {{
    font-size: 12px;
    color: #8888aa;
    margin-left: 16px;
  }}

  #map {{
    position: fixed;
    top: 56px;
    left: 0;
    right: 340px;
    bottom: 0;
    z-index: 1;
  }}

  #sidebar {{
    position: fixed;
    top: 56px;
    right: 0;
    width: 340px;
    bottom: 0;
    background: linear-gradient(180deg, #12122e 0%, #0a0a1f 100%);
    border-left: 1px solid rgba(100, 140, 255, 0.2);
    overflow-y: auto;
    z-index: 500;
    padding: 0;
    scrollbar-width: thin;
    scrollbar-color: #333366 #1a1a3e;
  }}

  #sidebar::-webkit-scrollbar {{
    width: 6px;
  }}

  #sidebar::-webkit-scrollbar-track {{
    background: #1a1a3e;
  }}

  #sidebar::-webkit-scrollbar-thumb {{
    background: #333366;
    border-radius: 3px;
  }}

  #sidebar-default {{
    padding: 24px 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}

  #sidebar-default h2 {{
    font-size: 15px;
    color: #8888cc;
    border-bottom: 1px solid rgba(100, 140, 255, 0.15);
    padding-bottom: 8px;
  }}

  .legend {{
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}

  .legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #aaa;
  }}

  .legend-color {{
    width: 20px;
    height: 14px;
    border-radius: 3px;
    flex-shrink: 0;
  }}

  .stats-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }}

  .stat-card {{
    background: rgba(50, 50, 100, 0.3);
    border: 1px solid rgba(100, 140, 255, 0.15);
    border-radius: 8px;
    padding: 12px;
    text-align: center;
  }}

  .stat-value {{
    font-size: 20px;
    font-weight: 700;
    color: #6c8cff;
  }}

  .stat-label {{
    font-size: 11px;
    color: #888;
    margin-top: 4px;
  }}

  #sidebar-detail {{
    display: none;
    padding: 0;
  }}

  .detail-header {{
    position: sticky;
    top: 0;
    background: linear-gradient(135deg, #1a1a50 0%, #151540 100%);
    padding: 20px;
    border-bottom: 1px solid rgba(100, 140, 255, 0.2);
    z-index: 10;
  }}

  .detail-rank {{
    display: inline-block;
    background: linear-gradient(135deg, #6c8cff, #4a6cf7);
    color: #fff;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
  }}

  .detail-rank.top3 {{
    background: linear-gradient(135deg, #ff6b6b, #ee5a24);
  }}

  .detail-rank.top10 {{
    background: linear-gradient(135deg, #f9ca24, #f0932b);
    color: #333;
  }}

  .detail-name {{
    font-size: 22px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 4px;
  }}

  .detail-rent-label {{
    font-size: 11px;
    color: #8888aa;
  }}

  .detail-rent {{
    font-size: 32px;
    font-weight: 800;
    color: #6c8cff;
    line-height: 1.1;
  }}

  .detail-rent small {{
    font-size: 14px;
    font-weight: 400;
    color: #8888cc;
  }}

  .detail-body {{
    padding: 16px 20px 24px;
  }}

  .detail-section {{
    margin-bottom: 18px;
  }}

  .detail-section-title {{
    font-size: 11px;
    font-weight: 600;
    color: #6c8cff;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .detail-section-title::before {{
    content: '';
    display: inline-block;
    width: 3px;
    height: 12px;
    background: #6c8cff;
    border-radius: 2px;
  }}

  .detail-description {{
    font-size: 13px;
    line-height: 1.8;
    color: #bbb;
  }}

  .detail-info-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }}

  .detail-info-card {{
    background: rgba(50, 50, 100, 0.25);
    border: 1px solid rgba(100, 140, 255, 0.1);
    border-radius: 8px;
    padding: 10px 12px;
  }}

  .detail-info-label {{
    font-size: 10px;
    color: #777;
    margin-bottom: 2px;
  }}

  .detail-info-value {{
    font-size: 14px;
    font-weight: 600;
    color: #ddd;
  }}

  .detail-tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}

  .detail-tag {{
    background: rgba(108, 140, 255, 0.12);
    border: 1px solid rgba(108, 140, 255, 0.25);
    color: #99aadd;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 14px;
  }}

  .detail-stations {{
    font-size: 13px;
    color: #aaa;
    line-height: 1.6;
  }}

  .rent-bar {{
    margin-top: 10px;
  }}

  .rent-bar-track {{
    width: 100%;
    height: 6px;
    background: rgba(255,255,255,0.08);
    border-radius: 3px;
    overflow: hidden;
  }}

  .rent-bar-fill {{
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
  }}

  .rent-bar-labels {{
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: #666;
    margin-top: 4px;
  }}

  .ranking-list {{
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 8px;
  }}

  .ranking-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
    color: #aaa;
    cursor: pointer;
    transition: background 0.2s;
  }}

  .ranking-item:hover {{
    background: rgba(108, 140, 255, 0.1);
  }}

  .ranking-num {{
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
    font-size: 10px;
    font-weight: 700;
    color: #888;
    flex-shrink: 0;
  }}

  .ranking-num.gold {{ background: rgba(255, 215, 0, 0.2); color: #ffd700; }}
  .ranking-num.silver {{ background: rgba(192, 192, 192, 0.2); color: #c0c0c0; }}
  .ranking-num.bronze {{ background: rgba(205, 127, 50, 0.2); color: #cd7f32; }}

  .ranking-name {{
    flex: 1;
  }}

  .ranking-rent {{
    font-weight: 600;
    color: #6c8cff;
  }}

  /* Leaflet customization */
  .leaflet-container {{
    background: #0a0a1a;
  }}

  .leaflet-tile-pane {{
    filter: brightness(0.6) saturate(0.3) hue-rotate(200deg);
  }}

  .leaflet-control-zoom a {{
    background: #1a1a3e !important;
    color: #6c8cff !important;
    border-color: rgba(100, 140, 255, 0.3) !important;
  }}

  .leaflet-control-zoom a:hover {{
    background: #252560 !important;
  }}

  .leaflet-control-attribution {{
    background: rgba(10, 10, 26, 0.8) !important;
    color: #555 !important;
    font-size: 10px !important;
  }}

  .leaflet-control-attribution a {{
    color: #6c8cff !important;
  }}

  @media (max-width: 768px) {{
    #sidebar {{
      display: none;
    }}

    #map {{
      right: 0;
    }}

    #mobile-panel {{
      display: block;
    }}
  }}

  #mobile-panel {{
    display: none;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    max-height: 50vh;
    background: linear-gradient(180deg, #12122e 0%, #0a0a1f 100%);
    border-top: 1px solid rgba(100, 140, 255, 0.3);
    border-radius: 16px 16px 0 0;
    z-index: 1000;
    overflow-y: auto;
    padding: 16px;
    transform: translateY(100%);
    transition: transform 0.3s ease;
  }}

  #mobile-panel.show {{
    transform: translateY(0);
  }}

  .mobile-handle {{
    width: 40px;
    height: 4px;
    background: #444;
    border-radius: 2px;
    margin: 0 auto 12px;
  }}

  /* Density indicator */
  .density-meter {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
  }}

  .density-bar {{
    flex: 1;
    display: flex;
    gap: 2px;
  }}

  .density-segment {{
    height: 8px;
    flex: 1;
    border-radius: 2px;
    background: rgba(255,255,255,0.06);
  }}

  .density-segment.active {{
    background: #6c8cff;
  }}

  .density-label {{
    font-size: 11px;
    color: #888;
    white-space: nowrap;
  }}
</style>
</head>
<body>

<div id="header">
  <div style="display:flex;align-items:center;">
    <h1><span>TOKYO</span> RENTAL MAP</h1>
    <span class="subtitle">東京都 市区町村別 平均賃貸マップ（1K/1DK）</span>
  </div>
  <div style="font-size:11px;color:#666;">Data: 2024 | Source: 国土数値情報</div>
</div>

<div id="map"></div>

<div id="sidebar">
  <div id="sidebar-default">
    <h2>概要</h2>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value" id="stat-areas">53</div>
        <div class="stat-label">市区町村</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="stat-avg">--</div>
        <div class="stat-label">平均家賃（万円）</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="stat-max">--</div>
        <div class="stat-label">最高家賃（万円）</div>
      </div>
      <div class="stat-card">
        <div class="stat-value" id="stat-min">--</div>
        <div class="stat-label">最低家賃（万円）</div>
      </div>
    </div>

    <h2>凡例 - 家賃水準</h2>
    <div class="legend" id="legend"></div>

    <h2>家賃ランキング TOP 10</h2>
    <div class="ranking-list" id="ranking-list"></div>

    <div style="margin-top:16px;padding:12px;background:rgba(50,50,100,0.2);border-radius:8px;border:1px solid rgba(100,140,255,0.1);">
      <div style="font-size:11px;color:#888;line-height:1.6;">
        マップ上の市区町村にカーソルを合わせると詳細情報が表示されます。クリックで固定できます。
      </div>
    </div>
  </div>

  <div id="sidebar-detail">
    <div class="detail-header">
      <div class="detail-rank" id="detail-rank"></div>
      <div class="detail-name" id="detail-name"></div>
      <div class="detail-rent-label">平均家賃（1K/1DK）</div>
      <div class="detail-rent" id="detail-rent"></div>
      <div class="rent-bar">
        <div class="rent-bar-track">
          <div class="rent-bar-fill" id="rent-bar-fill"></div>
        </div>
        <div class="rent-bar-labels">
          <span>3.5万</span>
          <span>13.5万</span>
        </div>
      </div>
    </div>
    <div class="detail-body">
      <div class="detail-section">
        <div class="detail-section-title">エリア紹介</div>
        <div class="detail-description" id="detail-description"></div>
      </div>

      <div class="detail-section">
        <div class="detail-section-title">基本情報</div>
        <div class="detail-info-grid" id="detail-info-grid"></div>
      </div>

      <div class="detail-section">
        <div class="detail-section-title">人口密度</div>
        <div class="density-meter">
          <div class="density-bar" id="density-bar"></div>
          <div class="density-label" id="density-label"></div>
        </div>
      </div>

      <div class="detail-section">
        <div class="detail-section-title">主要駅</div>
        <div class="detail-stations" id="detail-stations"></div>
      </div>

      <div class="detail-section">
        <div class="detail-section-title">見どころ</div>
        <div class="detail-tags" id="detail-highlights"></div>
      </div>

      <div class="detail-section" style="margin-top:24px;">
        <button onclick="closeSidebar()" style="width:100%;padding:10px;background:rgba(108,140,255,0.15);border:1px solid rgba(108,140,255,0.3);color:#6c8cff;border-radius:8px;cursor:pointer;font-size:13px;">
          一覧に戻る
        </button>
      </div>
    </div>
  </div>
</div>

<div id="mobile-panel">
  <div class="mobile-handle"></div>
  <div id="mobile-content"></div>
</div>

<script>
const tokyoGeoJSON = {geojson_str};
const municipalityData = {data_str};

// Calculate rankings
const rentEntries = Object.entries(municipalityData)
  .map(([code, d]) => ({{ code, name: d.name, rent: d.rent }}))
  .sort((a, b) => b.rent - a.rent);

const rankMap = {{}};
rentEntries.forEach((entry, i) => {{
  rankMap[entry.code] = i + 1;
}});

// Calculate stats
const rents = Object.values(municipalityData).map(d => d.rent);
const avgRent = (rents.reduce((a, b) => a + b, 0) / rents.length).toFixed(1);
const maxRent = Math.max(...rents).toFixed(1);
const minRent = Math.min(...rents).toFixed(1);

document.getElementById('stat-avg').textContent = avgRent;
document.getElementById('stat-max').textContent = maxRent;
document.getElementById('stat-min').textContent = minRent;

// Color scale
function getRentColor(rent) {{
  if (rent >= 12.0) return '#ff4757';
  if (rent >= 10.0) return '#ff6b81';
  if (rent >= 8.5) return '#ffa502';
  if (rent >= 7.0) return '#ffd43b';
  if (rent >= 6.0) return '#7bed9f';
  if (rent >= 5.0) return '#2ed573';
  if (rent >= 4.0) return '#1e90ff';
  return '#5352ed';
}}

function getRentGradient(rent) {{
  const ratio = (rent - 3.5) / (13.5 - 3.5);
  const clamped = Math.max(0, Math.min(1, ratio));

  const colors = [
    {{ pos: 0.0, r: 83, g: 82, b: 237 }},
    {{ pos: 0.15, r: 30, g: 144, b: 255 }},
    {{ pos: 0.3, r: 46, g: 213, b: 115 }},
    {{ pos: 0.5, r: 123, g: 237, b: 159 }},
    {{ pos: 0.65, r: 255, g: 212, b: 59 }},
    {{ pos: 0.8, r: 255, g: 165, b: 2 }},
    {{ pos: 0.9, r: 255, g: 107, b: 129 }},
    {{ pos: 1.0, r: 255, g: 71, b: 87 }}
  ];

  let lower = colors[0], upper = colors[colors.length - 1];
  for (let i = 0; i < colors.length - 1; i++) {{
    if (clamped >= colors[i].pos && clamped <= colors[i + 1].pos) {{
      lower = colors[i];
      upper = colors[i + 1];
      break;
    }}
  }}

  const range = upper.pos - lower.pos;
  const t = range === 0 ? 0 : (clamped - lower.pos) / range;
  const r = Math.round(lower.r + (upper.r - lower.r) * t);
  const g = Math.round(lower.g + (upper.g - lower.g) * t);
  const b = Math.round(lower.b + (upper.b - lower.b) * t);

  return `rgb(${{r}},${{g}},${{b}})`;
}}

// Build legend
const legendData = [
  {{ label: '12.0万円以上', color: '#ff4757' }},
  {{ label: '10.0 - 11.9万円', color: '#ff6b81' }},
  {{ label: '8.5 - 9.9万円', color: '#ffa502' }},
  {{ label: '7.0 - 8.4万円', color: '#ffd43b' }},
  {{ label: '6.0 - 6.9万円', color: '#7bed9f' }},
  {{ label: '5.0 - 5.9万円', color: '#2ed573' }},
  {{ label: '4.0 - 4.9万円', color: '#1e90ff' }},
  {{ label: '3.9万円以下', color: '#5352ed' }}
];

const legendEl = document.getElementById('legend');
legendData.forEach(item => {{
  const div = document.createElement('div');
  div.className = 'legend-item';
  div.innerHTML = `<div class="legend-color" style="background:${{item.color}}"></div>${{item.label}}`;
  legendEl.appendChild(div);
}});

// Build ranking list
const rankingList = document.getElementById('ranking-list');
rentEntries.slice(0, 10).forEach((entry, i) => {{
  const div = document.createElement('div');
  div.className = 'ranking-item';
  const numClass = i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : '';
  div.innerHTML = `
    <div class="ranking-num ${{numClass}}">${{i + 1}}</div>
    <div class="ranking-name">${{entry.name}}</div>
    <div class="ranking-rent">${{entry.rent}}万円</div>
  `;
  div.addEventListener('click', () => {{
    const feat = tokyoGeoJSON.features.find(f => f.properties.code === entry.code);
    if (feat) showDetail(entry.code);
  }});
  rankingList.appendChild(div);
}});

// Initialize map
const map = L.map('map', {{
  center: [35.68, 139.55],
  zoom: 11,
  zoomControl: true,
  attributionControl: true
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | &copy; <a href="https://carto.com/">CARTO</a> | 地図データ: 国土数値情報',
  subdomains: 'abcd',
  maxZoom: 18
}}).addTo(map);

// Remove the dark filter since we're using dark tiles
document.querySelector('.leaflet-tile-pane').style.filter = 'none';

let selectedCode = null;
let geojsonLayer = null;

function getStyle(feature) {{
  const code = feature.properties.code;
  const data = municipalityData[code];
  const rent = data ? data.rent : 0;
  const isSelected = code === selectedCode;

  return {{
    fillColor: data ? getRentGradient(rent) : '#333',
    weight: isSelected ? 3 : 1.5,
    opacity: 1,
    color: isSelected ? '#fff' : 'rgba(200, 200, 255, 0.4)',
    fillOpacity: isSelected ? 0.85 : 0.65,
    dashArray: isSelected ? '' : ''
  }};
}}

function showDetail(code) {{
  const data = municipalityData[code];
  if (!data) return;

  const rank = rankMap[code];
  const rankEl = document.getElementById('detail-rank');
  rankEl.textContent = `RANK #${{rank}} / ${{rentEntries.length}}`;
  rankEl.className = 'detail-rank' + (rank <= 3 ? ' top3' : rank <= 10 ? ' top10' : '');

  document.getElementById('detail-name').textContent = data.name;
  document.getElementById('detail-rent').innerHTML = `${{data.rent}}<small> 万円/月</small>`;
  document.getElementById('detail-description').textContent = data.description;

  // Rent bar
  const ratio = ((data.rent - 3.5) / (13.5 - 3.5)) * 100;
  const barFill = document.getElementById('rent-bar-fill');
  barFill.style.width = ratio + '%';
  barFill.style.background = `linear-gradient(90deg, #5352ed, ${{getRentGradient(data.rent)}})`;

  // Info grid
  const infoGrid = document.getElementById('detail-info-grid');
  const density = (data.population / data.area_km2).toFixed(0);
  infoGrid.innerHTML = `
    <div class="detail-info-card">
      <div class="detail-info-label">人口</div>
      <div class="detail-info-value">${{data.population.toLocaleString()}}人</div>
    </div>
    <div class="detail-info-card">
      <div class="detail-info-label">面積</div>
      <div class="detail-info-value">${{data.area_km2}}km&sup2;</div>
    </div>
    <div class="detail-info-card">
      <div class="detail-info-label">人口密度</div>
      <div class="detail-info-value">${{Number(density).toLocaleString()}}人/km&sup2;</div>
    </div>
    <div class="detail-info-card">
      <div class="detail-info-label">家賃ランク</div>
      <div class="detail-info-value">${{rank}}位 / ${{rentEntries.length}}</div>
    </div>
  `;

  // Density meter (max density ~25000)
  const densityBar = document.getElementById('density-bar');
  const densityLevel = Math.min(10, Math.ceil(Number(density) / 2500));
  densityBar.innerHTML = '';
  for (let i = 0; i < 10; i++) {{
    const seg = document.createElement('div');
    seg.className = 'density-segment' + (i < densityLevel ? ' active' : '');
    if (i < densityLevel) {{
      const hue = 230 - (i * 15);
      seg.style.background = `hsl(${{hue}}, 70%, 60%)`;
    }}
    densityBar.appendChild(seg);
  }}
  document.getElementById('density-label').textContent = `${{Number(density).toLocaleString()}}人/km²`;

  // Stations
  document.getElementById('detail-stations').textContent = data.stations;

  // Highlights
  const tagsEl = document.getElementById('detail-highlights');
  tagsEl.innerHTML = '';
  data.highlights.split(', ').forEach(tag => {{
    const span = document.createElement('span');
    span.className = 'detail-tag';
    span.textContent = tag;
    tagsEl.appendChild(span);
  }});

  document.getElementById('sidebar-default').style.display = 'none';
  document.getElementById('sidebar-detail').style.display = 'block';

  // Scroll to top of sidebar
  document.getElementById('sidebar').scrollTop = 0;

  selectedCode = code;
  if (geojsonLayer) geojsonLayer.setStyle(getStyle);
}}

function closeSidebar() {{
  document.getElementById('sidebar-default').style.display = 'block';
  document.getElementById('sidebar-detail').style.display = 'none';
  selectedCode = null;
  if (geojsonLayer) geojsonLayer.setStyle(getStyle);
}}

function onEachFeature(feature, layer) {{
  const code = feature.properties.code;
  const data = municipalityData[code];

  if (data) {{
    const rank = rankMap[code];
    layer.bindTooltip(
      `<div style="font-weight:700;font-size:13px;">${{data.name}}</div>` +
      `<div style="color:#6c8cff;font-size:15px;font-weight:800;">${{data.rent}}万円<span style="font-size:11px;color:#888;">/月</span></div>` +
      `<div style="font-size:11px;color:#999;">ランキング: ${{rank}}位</div>`,
      {{
        sticky: true,
        direction: 'top',
        className: 'custom-tooltip',
        offset: [0, -10]
      }}
    );
  }}

  layer.on({{
    mouseover: function(e) {{
      if (code !== selectedCode) {{
        this.setStyle({{
          weight: 3,
          color: '#fff',
          fillOpacity: 0.85
        }});
        this.bringToFront();
      }}
    }},
    mouseout: function(e) {{
      if (code !== selectedCode) {{
        geojsonLayer.resetStyle(this);
      }}
    }},
    click: function(e) {{
      showDetail(code);
    }}
  }});
}}

geojsonLayer = L.geoJSON(tokyoGeoJSON, {{
  style: getStyle,
  onEachFeature: onEachFeature
}}).addTo(map);

// Add custom tooltip styles
const tooltipStyle = document.createElement('style');
tooltipStyle.textContent = `
  .custom-tooltip {{
    background: rgba(18, 18, 46, 0.95) !important;
    border: 1px solid rgba(108, 140, 255, 0.4) !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    color: #e0e0e0 !important;
    font-family: 'Helvetica Neue', Arial, sans-serif !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4) !important;
    backdrop-filter: blur(10px);
  }}
  .custom-tooltip::before {{
    border-top-color: rgba(108, 140, 255, 0.4) !important;
  }}
  .leaflet-tooltip-top::before {{
    border-top-color: rgba(108, 140, 255, 0.4) !important;
  }}
`;
document.head.appendChild(tooltipStyle);
</script>
</body>
</html>'''
    return html


def main():
    # Load GeoJSON
    with open(GEOJSON_PATH, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Build HTML
    html_content = build_html(geojson_data)

    # Write output
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated {OUTPUT_PATH}")
    print(f"  GeoJSON features: {len(geojson_data['features'])}")
    print(f"  Municipality data entries: {len(MUNICIPALITY_DATA)}")
    print(f"  File size: {os.path.getsize(OUTPUT_PATH):,} bytes")


if __name__ == '__main__':
    main()
