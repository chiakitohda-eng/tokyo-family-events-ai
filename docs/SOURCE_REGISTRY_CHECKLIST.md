# 取得元チェックリスト（自動生成・手編集しない）

`site/data/discovery_sources.json` の全サイトを一覧にしたもの。サイトに載っている取得元はすべて、毎回の更新で「訪問した／取得できなかった（理由）」を記録する。
再生成: `python3 tools/gen_source_checklist.py`（`tests/source_checklist_sync.test.mjs` が一覧との一致を検査する）。

## A. 固定サイト（27件・登録済みの検索URLから機械的に取得）

| id | 名称 | 取得URL |
|---|---|---|
| `sumida` | 墨田 | https://www.sumidaevent.com/ |
| `asakusa` | 浅草 | https://www.asakusaevent.com/ |
| `ueno` | 上野公園 | https://www.uenopark.info/ |
| `akihabara` | 秋葉原 | https://www.akihabaraevent.com/ |
| `hibiya` | 日比谷公園 | https://www.hibiyapark.info/ |
| `ikebukuro` | 池袋 | https://www.ikebukuropark.info/ |
| `shinjuku` | 新宿 | https://www.shinjukuevent.com/ |
| `nakano` | 中野 | https://www.nakanoevent.com/ |
| `yoyogi` | 代々木公園 | https://www.yoyogikoen.info/ |
| `shibuya` | 渋谷 | https://www.miyashitapark.info/ |
| `roppongi` | 六本木 | https://www.roppongievents.com/ |
| `toyosu` | 豊洲 | https://www.toyosuevent.com/ |
| `odaiba` | お台場 | https://www.odaibapark.com/ |
| `shinagawa` | 品川 | https://www.shinagawaevent.com/ |
| `tachikawa` | 立川 | https://www.tachikawaevent.com/ |
| `iterrace` | アイテラス落合南長崎 | https://www.iterrace.jp/ |
| `nerimakanko` | とっておきの練馬 | https://www.nerimakanko.jp/event/ https://www.nerimakanko.jp/event/search.php?month={YYYY-MM} |
| `suginami_festival` | 杉並区イベントカレンダー（お祭り） | https://www.city.suginami.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?type=2&year={YYYY}&month={MM}&event_category=5&siteid=1 |
| `nerima_district_festivals_2026` | 練馬区公式 令和8年度地区祭開催日程 | https://www.city.nerima.tokyo.jp/kankomoyoshi/annai/omatsuri/chikusai/20260616103208700.html |
| `nakano_official_tourism` | 中野区観光協会・公式イベント | https://www.nakano-kanko.com/event/ |
| `itabashi_official_festival` | 板橋区公式・区民まつり | https://www.city.itabashi.tokyo.jp/bunka/kanko/matsuri/index.html https://www.city.itabashi.tokyo.jp/bunka/kanko/matsuri/1006858.html |
| `itabashi_tourism_festival` | 板橋区観光協会・区民まつり特集 | https://itabashi-kanko.jp/pickup/detail?id=1799 |
| `tamemap_nakano` | ためまっぷなかの（地域イベントカレンダー） | https://pc.tamemap.net/1311401/calendar/{YYYY-MM}?lat=35.7089745&lng=139.6630981&level=5000&locale=ja |
| `itabashi_times_event` | いたばしTIMES（イベント情報） | https://itabashi-times.com/category/event https://itabashi-times.com/category/event/page/2 |
| `suginami_calendar_all` | 杉並区公式イベントカレンダー（全ジャンル・日別巡回） | https://www.city.suginami.tokyo.jp/cgi-bin/event_cal_multi/calendar.cgi?type=2&year={YYYY}&month={MM} |
| `nerima_forest_festa_2026` | 練馬区公式 ねりまの森こどもフェスタ（日別行） | https://www.city.nerima.tokyo.jp/kurashi/shigoto/midori/shokai/nerimanomori.html |
| `shinjuku_sankaku_hiroba` | 新宿住友ビル三角広場（会場公式） | https://www.sumitomo-sankakuhiroba.jp/event/ |

## B. AI探索先サイト（118件・AIが候補探しの入口にする）

### 市部の自治体公式サイト（多摩20市＋浦安市）（21件）

| id | 名称 | URL |
|---|---|---|
| `ai_city_musashino` | 武蔵野市公式サイト（イベント・子育て・広報） | https://www.city.musashino.lg.jp/ |
| `ai_city_mitaka` | 三鷹市公式サイト（イベント・子育て・広報） | https://www.city.mitaka.lg.jp/ |
| `ai_city_chofu` | 調布市公式サイト（イベント・子育て・広報） | https://www.city.chofu.lg.jp/ |
| `ai_city_fuchu` | 府中市公式サイト（イベント・子育て・広報） | https://www.city.fuchu.tokyo.jp/ |
| `ai_city_koganei` | 小金井市公式サイト（イベント・子育て・広報） | https://www.city.koganei.lg.jp/ |
| `ai_city_kodaira` | 小平市公式サイト（イベント・子育て・広報） | https://www.city.kodaira.tokyo.jp/ |
| `ai_city_kokubunji` | 国分寺市公式サイト（イベント・子育て・広報） | https://www.city.kokubunji.tokyo.jp/ |
| `ai_city_kunitachi` | 国立市公式サイト（イベント・子育て・広報） | https://www.city.kunitachi.tokyo.jp/ |
| `ai_city_tachikawa` | 立川市公式サイト（イベント・子育て・広報） | https://www.city.tachikawa.lg.jp/ |
| `ai_city_akishima` | 昭島市公式サイト（イベント・子育て・広報） | https://www.city.akishima.lg.jp/ |
| `ai_city_hino` | 日野市公式サイト（イベント・子育て・広報） | https://www.city.hino.lg.jp/ |
| `ai_city_nishitokyo` | 西東京市公式サイト（イベント・子育て・広報） | https://www.city.nishitokyo.lg.jp/ |
| `ai_city_higashikurume` | 東久留米市公式サイト（イベント・子育て・広報） | https://www.city.higashikurume.lg.jp/ |
| `ai_city_kiyose` | 清瀬市公式サイト（イベント・子育て・広報） | https://www.city.kiyose.lg.jp/ |
| `ai_city_higashimurayama` | 東村山市公式サイト（イベント・子育て・広報） | https://www.city.higashimurayama.tokyo.jp/ |
| `ai_city_komae` | 狛江市公式サイト（イベント・子育て・広報） | https://www.city.komae.tokyo.jp/ |
| `ai_city_tama` | 多摩市公式サイト（イベント・子育て・広報） | https://www.city.tama.lg.jp/ |
| `ai_city_inagi` | 稲城市公式サイト（イベント・子育て・広報） | https://www.city.inagi.tokyo.jp/ |
| `ai_city_machida` | 町田市公式サイト（イベント・子育て・広報） | https://www.city.machida.tokyo.jp/ |
| `ai_city_hachioji` | 八王子市公式サイト（イベント・子育て・広報） | https://www.city.hachioji.tokyo.jp/ |
| `ai_city_urayasu` | 浦安市（千葉県）公式サイト・イベントカレンダー | https://www.city.urayasu.lg.jp/event_calendar.html |

### 23区の自治体公式サイト（26件）

| id | 名称 | URL |
|---|---|---|
| `ai_ward_chiyoda` | 千代田区公式サイト（イベント・子育て・広報） | https://www.city.chiyoda.lg.jp/ |
| `ai_ward_chuo` | 中央区公式サイト（イベント・子育て・広報） | https://www.city.chuo.lg.jp/ |
| `ai_ward_minato` | 港区公式サイト（イベント・子育て・広報） | https://www.city.minato.tokyo.jp/ |
| `ai_ward_shinjuku` | 新宿区公式サイト（イベント・子育て・広報） | https://www.city.shinjuku.lg.jp/ |
| `ai_ward_bunkyo` | 文京区公式サイト（イベント・子育て・広報） | https://www.city.bunkyo.lg.jp/ |
| `ai_ward_taito` | 台東区公式サイト（イベント・子育て・広報） | https://www.city.taito.lg.jp/ |
| `ai_ward_sumida` | 墨田区公式サイト（イベント・子育て・広報） | https://www.city.sumida.lg.jp/ |
| `ai_ward_koto` | 江東区公式サイト（イベント・子育て・広報） | https://www.city.koto.lg.jp/ |
| `ai_ward_shinagawa` | 品川区公式サイト（イベント・子育て・広報） | https://www.city.shinagawa.tokyo.jp/ |
| `ai_ward_meguro` | 目黒区公式サイト（イベント・子育て・広報） | https://www.city.meguro.tokyo.jp/ |
| `ai_ward_ota` | 大田区公式サイト（イベント・子育て・広報） | https://www.city.ota.tokyo.jp/ |
| `ai_ward_setagaya` | 世田谷区公式サイト（イベント・子育て・広報） | https://www.city.setagaya.lg.jp/ |
| `ai_ward_suginami` | 杉並区公式サイト（イベント・子育て・広報） | https://www.city.suginami.tokyo.jp/ |
| `ai_ward_toshima` | 豊島区公式サイト（イベント・子育て・広報） | https://www.city.toshima.lg.jp/ |
| `ai_ward_kita` | 北区公式サイト（イベント・子育て・広報） | https://www.city.kita.tokyo.jp/ |
| `ai_ward_arakawa` | 荒川区公式サイト（イベント・子育て・広報） | https://www.city.arakawa.tokyo.jp/ |
| `ai_ward_itabashi` | 板橋区公式サイト（イベント・子育て・広報） | https://www.city.itabashi.tokyo.jp/ |
| `ai_ward_nerima` | 練馬区公式サイト（イベント・子育て・広報） | https://www.city.nerima.tokyo.jp/ |
| `ai_ward_adachi` | 足立区公式サイト（イベント・子育て・広報） | https://www.city.adachi.tokyo.jp/ |
| `ai_ward_katsushika` | 葛飾区公式サイト（イベント・子育て・広報） | https://www.city.katsushika.lg.jp/ |
| `ai_ward_edogawa` | 江戸川区公式サイト（イベント・子育て・広報） | https://www.city.edogawa.tokyo.jp/ |
| `ai_ward_shibuya` | 渋谷区公式サイト（イベント・子育て・広報） | https://www.city.shibuya.tokyo.jp/ |
| `ai_ward_nakano` | 中野区公式サイト（イベント・子育て・広報） | https://www.city.tokyo-nakano.lg.jp/ |
| `ai_ward_nakano_kanko` | 中野区観光協会（イベント） | https://www.nakano-kanko.com/event/ |
| `ai_ward_nakano_event` | 中野のイベント情報（nakanoevent） | https://www.nakanoevent.com/ |
| `ai_ward_shibuya_pgc` | 渋谷区 プレイグラウンドシティ渋谷（子育て・遊び） | https://playgroundcity-shibuya.jp/ |

### 都立公園・国営公園・海上公園（37件）

| id | 名称 | URL |
|---|---|---|
| `ai_showakinen` | 国営昭和記念公園 イベント | https://www.showakinen-koen.jp/event/ |
| `ai_tokyo_park` | 東京都公園協会 公園イベント | https://www.tokyo-park.or.jp/event/ |
| `ai_tpark_yoyogi` | 代々木公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/yoyogi/ |
| `ai_tpark_hibiya` | 日比谷公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/hibiya/ |
| `ai_tpark_hikarigaoka` | 光が丘公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/hikarigaoka/ |
| `ai_tpark_kasairinkai` | 葛西臨海公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/kasairinkai/ |
| `ai_tpark_shakujii` | 石神井公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/shakujii/ |
| `ai_tpark_kiba` | 木場公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/kiba/ |
| `ai_tpark_akatsuka` | 赤塚公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/akatsuka/ |
| `ai_tpark_wadabori` | 和田堀公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/wadabori/ |
| `ai_tpark_ukima` | 浮間公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/ukima/ |
| `ai_tpark_toneri` | 舎人公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/toneri/ |
| `ai_tpark_siba` | 芝公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/siba/ |
| `ai_tpark_shinozaki` | 篠崎公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/shinozaki/ |
| `ai_tpark_mizumoto` | 水元公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/mizumoto/ |
| `ai_tpark_soshigaya` | 祖師谷公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/soshigaya/ |
| `ai_tpark_toyama` | 戸山公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/toyama/ |
| `ai_tpark_takaido` | 高井戸公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/takaido/ |
| `ai_tpark_zenpukuji` | 善福寺公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/zenpukuji/ |
| `ai_tpark_shioiri` | 汐入公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/shioiri/ |
| `ai_tpark_rinshinomori` | 林試の森公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/rinshinomori/ |
| `ai_tpark_nerimajoshi` | 練馬城址公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/nerimajoshi/ |
| `ai_tpark_komazawa` | 駒沢オリンピック公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/komazawa-olympic/ |
| `ai_tpark_kinuta` | 砧公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/kinuta/ |
| `ai_tpark_johoku_chuo` | 城北中央公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/johoku-chuo/ |
| `ai_tpark_higashishirahige` | 東白鬚公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/higashi-shirahige/ |
| `ai_tpark_aoyama` | 青山公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/aoyama/ |
| `ai_park_kasai_official` | 葛西臨海公園（公式） | https://kasaikaihinpark.com/ |
| `ai_park_seaside_south` | 東京港 南部海上公園（お台場・城南島など） | https://tokyo-south-seaside-parks.com/ |
| `ai_park_uminomori` | 海の森公園 | https://uminomoripark.com/ |
| `ai_park_tptc` | 東京港埠頭（海上公園のイベント） | https://www.tptc.co.jp/ |
| `ai_park_showakinen_top` | 国営昭和記念公園（公式） | https://www.showakinen-koen.jp/ |
| `ai_tpark_inokashira` | 井の頭恩賜公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/inokashira/ |
| `ai_tpark_ueno` | 上野恩賜公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/ueno/ |
| `ai_tpark_jindai` | 神代植物公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/jindai/ |
| `ai_tpark_koganei` | 小金井公園（東京都公園協会の公園ページ） | https://www.tokyo-park.or.jp/park/koganei/ |
| `ai_tpark_event_search` | 東京都公園協会 イベント検索（全公園） | https://www.tokyo-park.or.jp/event_search/index.html |

### 動物園・水族館・博物館・美術館・科学館（16件）

| id | 名称 | URL |
|---|---|---|
| `ai_tokyo_zoo` | 東京動物園協会（多摩動物公園・井の頭自然文化園ほか） | https://www.tokyo-zoo.net/ |
| `ai_park_yumenoshima` | 夢の島熱帯植物館 | https://www.yumenoshima-nettai.com/ |
| `ai_fac_galaxcity` | ギャラクシティ（足立区） | https://www.galaxcity.jp/ |
| `ai_fac_sumida_aquarium` | すみだ水族館 | https://www.sumida-aquarium.com/ |
| `ai_fac_mizunokagaku` | 水の科学館 | https://www.mizunokagaku.jp/ |
| `ai_fac_tnm` | 東京国立博物館 | https://www.tnm.jp/ |
| `ai_fac_miraikan` | 日本科学未来館 | https://www.miraikan.jst.go.jp/ |
| `ai_fac_mot` | 東京都現代美術館 | https://www.mot-art-museum.jp/ |
| `ai_fac_tobikan` | 東京都美術館 | https://www.tobikan.jp/ |
| `ai_fac_edo_tokyo` | 江戸東京博物館 | https://www.edo-tokyo-museum.or.jp/ |
| `ai_fac_teien` | 東京都庭園美術館 | https://www.teien-art-museum.ne.jp/ |
| `ai_fac_fire_museum` | 新宿消防博物館 | https://www.shinjuku-fire-museum.jp/ |
| `ai_fac_chihiro` | ちひろ美術館 | https://chihiro.jp/ |
| `ai_zoo_ueno` | 上野動物園（イベント） | https://www.tokyo-zoo.net/ueno/events/index.html |
| `ai_zoo_inokashira` | 井の頭自然文化園（イベント） | https://www.tokyo-zoo.net/inokashira/events/index.html |
| `ai_zoo_kasai` | 葛西臨海水族園（イベント） | https://www.tokyo-zoo.net/kasai/events/index.html |

### テーマパーク・遊園地・大型商業施設（15件）

| id | 名称 | URL |
|---|---|---|
| `ai_yomiuriland` | よみうりランド（稲城市） | https://www.yomiuriland.com/event/ |
| `ai_puroland` | サンリオピューロランド（多摩市） | https://www.puroland.jp/ |
| `ai_tokyo_dome_city` | 東京ドームシティ（文京区） | https://www.tokyo-dome.co.jp/event/ |
| `ai_wb_studio_tour` | ワーナー ブラザース スタジオツアー東京（練馬区） | https://www.wbstudiotour.jp/ |
| `ai_fac_skytree` | 東京スカイツリー | https://www.tokyo-skytree.jp/ |
| `ai_fac_solamachi` | 東京ソラマチ（イベント） | https://www.tokyo-solamachi.jp/event/ |
| `ai_fac_hanayashiki` | 浅草花やしき | https://www.hanayashiki.net/ |
| `ai_fac_joypolis` | 東京ジョイポリス | https://tokyo-joypolis.com/ |
| `ai_fac_sunshine` | サンシャインシティ | https://sunshinecity.jp/event/ |
| `ai_fac_legoland` | レゴランド・ディスカバリー・センター東京 | https://www.legoland.jp/ |
| `ai_fac_tdl` | 東京ディズニーランド（千葉県浦安市） | https://www.tokyodisneyresort.jp/tdl/ |
| `ai_fac_tds` | 東京ディズニーシー（千葉県浦安市） | https://www.tokyodisneyresort.jp/tds/ |
| `ai_fac_tdr_christmas` | 東京ディズニーリゾート ディズニー・クリスマス（千葉県浦安市） | https://www.tokyodisneyresort.jp/treasure/christmas2026/tdl/ |
| `ai_fac_hanayashiki_event` | 浅草花やしき イベント・ステージ（台東区） | https://www.hanayashiki.net/event_this/ |
| `ai_fac_sunshine_tenbo` | サンシャイン60展望台 てんぼうパーク イベント（豊島区） | https://sunshinecity.jp/observatory/event/ |

### 東京都・観光財団（3件）

| id | 名称 | URL |
|---|---|---|
| `ai_tcvb` | 東京観光財団（都内地域のイベント） | https://www.tcvb.or.jp/ |
| `ai_metro_kodomo_smile` | 東京都こどもスマイルムーブメント | https://kodomo-smile.metro.tokyo.lg.jp/ |
| `ai_metro_metro` | 東京都（報道発表・イベント） | https://www.metro.tokyo.lg.jp/ |
