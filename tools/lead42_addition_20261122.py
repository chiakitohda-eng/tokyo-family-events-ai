#!/usr/bin/env python3
"""2 weekly records (Komae city x2) from committed official pages (2026-11-21).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/. The gate validator re-derives every record and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'eb1facf6035092f7991cb81cf90cc3e10b382eb1'   # data-production after image-fill4 (784 active week records)
CHECKED = '2026-11-22'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この8件は二子玉川ライズの公式ページの個別確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no early <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if 0 <= i < 20000 else raw   # SPA pages (event site) put the only <h1> after the body; use the whole document
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))



def _ax(ct, it, af, st, bu, co, re_, fv):
    return {'child_target': ct, 'interactivity': it, 'age_fit': af, 'stay_flexibility': st, 'burden': bu, 'cost': co, 'reservation': re_, 'family_value': fv}


_TAMA = 'https://www.city.tama.lg.jp/kosodate/1008019/1008033'

SPECS_RAW = [{'id': 'verified-20261205-setagaya-futakotamagawa-rise-skate-garden-2026',
  'week': '2026-12-05',
  'ward': '世田谷区',
  'page': 'futako_rise_skate_20261122.html',
  'name': '二子玉川ライズ スケートガーデン 2026',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001500',
  'date': '2026-12-05',
  'end': '2027-02-28',
  'period': '〜2/28(日)の毎日（12/5開幕）',
  'time': '平日13:00〜19:00／土日祝11:00〜19:00（受付は18:30まで。12/5は13:00〜）',
  'venue': '二子玉川ライズ 中央広場（世田谷区玉川2-21-1）',
  'price': '未就学児1,200円・小学生1,700円・学生2,000円・大人2,200円（貸靴代込）。17時以降は500円引',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/02aff602.png',
  'description': '本物の氷を張った期間限定の屋外スケートリンク。ワンポイントレッスン（10分1,000円）やスケート遊具（20分500円）もあり、初めての子どもも滑れる。',
  'categories': ['体験・ワークショップ', 'スポーツ・体を動かす'],
  'indoor_outdoor': '屋外',
  'reservation': {'required': False, 'note': '当日券売機で購入。手袋着用が必須。混雑時は入場制限あり。'},
  'quotes': ['本物の氷を張った、期間限定の屋外スケートリンク「二子玉川ライズ スケートガーデン」が今年も開催します！', '1,200円（貸靴代込）', '土日祝 11：00～19：00（18：30受付終了）'],
  'overall': 'B',
  'basis': 'all_ages',
  'child_activity': False,
  'reason': '二子玉川ライズの中央広場で2027年2月28日まで続く屋外スケートリンク。未就学児から滑れる料金設定があり、初心者向けのワンポイントレッスンもある。',
  'axes': {'child_target': 'B', 'interactivity': 'B', 'age_fit': 'B', 'stay_flexibility': 'A', 'burden': 'B', 'cost': 'C', 'reservation': 'A', 'family_value': 'B'},
  'strengths': ['未就学児から料金が設定され、初心者向けレッスンもある', '期間が長く、好きな日に行ける'],
  'limitations': ['料金は1人1,200〜2,200円と高め', '手袋が必須で、混雑時は入場制限がある'],
  'comparison': '総合B：屋外の本格スケートで、未就学児から滑れる。1人1,200円〜の費用と混雑に注意。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed']},
 {'id': 'verified-20261219-setagaya-futakotamagawa-rise-skate-class',
  'week': '2026-12-19',
  'ward': '世田谷区',
  'page': 'futako_rise_skateclass_20261122.html',
  'name': '二子玉川ライズ スケートガーデン スケート教室',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001539',
  'date': '2026-12-19',
  'end': '2027-02-27',
  'period': '12/19〜2/27の教室日（はじめて・初級・親子ほか）',
  'time': '9:30〜10:30が中心（親子教室は11:30〜12:30の回もあり）',
  'venue': '二子玉川ライズ 中央広場（世田谷区玉川2-21-1）',
  'price': '1回3,000円〜（はじめて教室。親子教室は大人1名＋子ども1名で5,000円、貸靴代含む）',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/4a3b3525.png',
  'description': '未経験の3歳以上が受けられる「はじめて教室」と、3歳以上〜小学校低学年の「親子教室」などがあるスケート教室。',
  'categories': ['体験・ワークショップ', 'スポーツ・体を動かす'],
  'indoor_outdoor': '屋外',
  'reservation': {'required': True, 'note': '予約サイトで12/2 10:00から順次受付。各回の定員は先着15〜40名（親子教室は15組）。'},
  'quotes': ['二子玉川ライズ スケートガーデン スケート教室', '■お父さんお母さんとお子さんが一緒に楽しめる教室', '・参加資格：3歳以上のスケート未経験、初心者の方'],
  'overall': 'B',
  'basis': 'child_program',
  'child_activity': True,
  'reason': 'スケート未経験の3歳以上向けの教室と、大人1名＋子ども1名で参加する親子教室がある。12/2から予約サイトで順次受付。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'A', 'stay_flexibility': 'C', 'burden': 'B', 'cost': 'C', 'reservation': 'C', 'family_value': 'A'},
  'strengths': ['3歳以上の未経験から参加できる', '親子で参加できる教室がある'],
  'limitations': ['事前予約が必要で定員が小さい', '1回3,000円〜と費用がかかる'],
  'comparison': '総合B：未経験の幼児から参加できる子ども向けの教室。事前予約と1回3,000円〜の費用が条件。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed']},
 {'id': 'verified-20261205-setagaya-futakotamagawa-rise-skate-opening',
  'week': '2026-12-05',
  'ward': '世田谷区',
  'page': 'futako_rise_skateopen_20261122.html',
  'name': '二子玉川ライズ スケートガーデン オープニングイベント',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001535',
  'date': '2026-12-05',
  'end': '2026-12-05',
  'period': '12/5(土)',
  'time': '12:00〜12:45',
  'venue': '二子玉川ライズ 中央広場（世田谷区玉川2-21-1）',
  'price': 'オープン初日の12月5日（土）は豪華なゲストを招いたオープニングイベントを実施！',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/00e8f947.png',
  'description': 'プロスケーターの織田信成さんのパフォーマンスとスケートクイズ対決があるスケートガーデンの開幕イベント。',
  'categories': ['まつり・イベント', 'スポーツ・体を動かす'],
  'indoor_outdoor': '屋外',
  'reservation': {'required': False, 'note': '申込・予約の記載なし。'},
  'quotes': ['オープン初日の12月5日（土）は豪華なゲストを招いたオープニングイベントを実施！', '開催日時：2026年12月5日（土）12：00～12：45', '織田さんの演技の後は是非みんなでスケートにチャレンジしてみましょう♪'],
  'overall': 'B',
  'basis': 'all_ages',
  'child_activity': False,
  'reason': 'スケートガーデンの開幕日に、織田信成さんのパフォーマンスとスケートクイズ対決を無料で観られる。',
  'axes': {'child_target': 'B', 'interactivity': 'B', 'age_fit': 'B', 'stay_flexibility': 'C', 'burden': 'B', 'cost': 'A', 'reservation': 'A', 'family_value': 'B'},
  'strengths': ['観覧無料', 'クイズ対決で観客も参加できる'],
  'limitations': ['45分の短いステージ', 'メディア取材で撮影に映り込むことがある'],
  'comparison': '総合B：無料のステージ。短時間で、同じ日にスケートも楽しめる。',
  'status': 'verified',
  'price_field': 'pass',
  'positive': ['official_date_confirmed']},
 {'id': 'verified-20261121-setagaya-futakotamagawa-rise-winter-illumination-2026',
  'week': '2026-11-21',
  'ward': '世田谷区',
  'page': 'futako_rise_illumination_20261122.html',
  'name': '二子玉川ライズ ウィンターイルミネーション',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001513',
  'date': '2026-11-21',
  'end': '2027-02-28',
  'period': '〜2/28(日)の毎日（11/7から開催中）',
  'time': '16:00〜23:00',
  'venue': 'リボンストリート周辺・オークモール・バーズモール（二子玉川ライズ、世田谷区玉川2-21-1）',
  'price': '公式ページに観覧料の記載なし（要確認）',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/cb6dc22c.png',
  'description': 'LED約11.4万球のシャンパンゴールドの光とボールライトで、二子玉川ライズのまち並みを彩る冬のイルミネーション。',
  'categories': ['まつり・イベント', '自然・散歩'],
  'indoor_outdoor': '屋外',
  'reservation': {'required': False, 'note': '申込・予約の記載なし。'},
  'quotes': ['LED約11.4万球が放つシャンパンゴールドの輝き', '2026年11月7日（土）～2027年2月28日（日）', ],
  'overall': 'B',
  'basis': 'all_ages',
  'child_activity': False,
  'reason': '二子玉川ライズのまち並みで2027年2月28日まで続く冬のイルミネーション。約11.4万球で、16時から23時まで点灯する。',
  'axes': {'child_target': 'B', 'interactivity': 'C', 'age_fit': 'B', 'stay_flexibility': 'A', 'burden': 'B', 'cost': 'unknown', 'reservation': 'A', 'family_value': 'B'},
  'strengths': ['期間が長く、好きな時間に立ち寄れる', 'ツリーやスケートリンクと合わせて回れる'],
  'limitations': ['観覧料が公式ページに記載がない', '屋外で夜間のため、防寒と帰りの時間に注意'],
  'comparison': '総合B：長期間のイルミネーション。観覧料は要確認。',
  'status': 'verified',
  'price_field': 'unknown',
  'positive': ['official_date_confirmed']},
 {'id': 'verified-20261121-setagaya-futakotamagawa-rise-christmas-tree-2026',
  'week': '2026-11-21',
  'ward': '世田谷区',
  'page': 'futako_rise_christmas_20261122.html',
  'name': '二子玉川ライズ クリスマス2026「CHRISTMAS WORLD TREE」',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001509',
  'date': '2026-11-21',
  'end': '2026-12-25',
  'period': '〜12/25(金)の毎日（11/7から点灯）',
  'time': '16:00〜23:00に15分ごとに音と光の演出',
  'venue': 'ガレリア（二子玉川ライズ、世田谷区玉川2-21-1）',
  'price': '公式ページに観覧料の記載なし（要確認）',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/dfa1b482.jpg',
  'description': '高さ約9m・約2万6千球のクリスマスツリーがガレリアに登場し、15分ごとに音と光の特別演出がある。',
  'categories': ['まつり・イベント'],
  'indoor_outdoor': '屋外',
  'reservation': {'required': False, 'note': '申込・予約の記載なし。'},
  'quotes': ['高さ約9ｍ・約2万6千球の光をまとうツリーがガレリアに登場。', '点灯期間：2026年11月7日（土）～12月25日（金）'],
  'overall': 'B',
  'basis': 'all_ages',
  'child_activity': False,
  'reason': 'ガレリアの高さ約9mのツリーが、12月25日まで点灯する。16時から15分ごとに音と光の演出がある。',
  'axes': {'child_target': 'B', 'interactivity': 'C', 'age_fit': 'B', 'stay_flexibility': 'A', 'burden': 'A', 'cost': 'unknown', 'reservation': 'A', 'family_value': 'B'},
  'strengths': ['15分ごとの演出で、短い時間でも立ち寄れる', 'ツリーとイルミネーションを合わせて見られる'],
  'limitations': ['観覧料が公式ページに記載がない', '夕方以降は人が多い可能性がある'],
  'comparison': '総合B：短時間で見られるクリスマスツリー。料金は要確認。',
  'status': 'verified',
  'price_field': 'unknown',
  'positive': ['official_date_confirmed']},
 {'id': 'verified-20261121-setagaya-futakotamagawa-rise-clear-sky-science-live',
  'week': '2026-11-21',
  'ward': '世田谷区',
  'page': 'futako_rise_clearsky_20261122.html',
  'name': '東京の空について考えよう！Clear Skyサイエンスライブ',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001566',
  'date': '2026-11-23',
  'end': '2026-11-23',
  'period': '11/23(月・祝)',
  'time': '13:00〜、15:00〜（各回）',
  'venue': 'ガレリア（二子玉川ライズ、世田谷区玉川2-21-1）',
  'price': '公式ページに参加費の記載なし（要確認）',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/134d99e5.png',
  'description': 'サイエンスアーティストの市岡元気先生と、東京の空について楽しく学べるサイエンスライブ。ブースイベントに参加するとノベルティがもらえる。',
  'categories': ['科学・自然', '体験・ワークショップ'],
  'indoor_outdoor': '屋内',
  'reservation': {'required': False, 'note': '申込・予約の記載なし。'},
  'quotes': ['YouTubeなどで活躍しているサイエンスアーティスト、市岡元気先生と一緒に東京の空について楽しく学べるサイエンスライブを開催します！', '11月23日（月・祝）13:00～、15:00～'],
  'overall': 'B',
  'basis': 'child_program',
  'child_activity': True,
  'reason': 'ガレリアで11/23の13時と15時に開く、東京の空について学ぶサイエンスライブ。ブースの参加でノベルティがもらえる。',
  'axes': {'child_target': 'B', 'interactivity': 'B', 'age_fit': 'B', 'stay_flexibility': 'C', 'burden': 'A', 'cost': 'unknown', 'reservation': 'A', 'family_value': 'B'},
  'strengths': ['実験形式のサイエンスライブで、子どもも見て学べる', 'ブース参加でノベルティがもらえる'],
  'limitations': ['2回のみの開催で、参加費は公式ページに記載がない'],
  'comparison': '総合B：1日限りのサイエンスライブ。参加費は要確認。',
  'status': 'verified',
  'price_field': 'unknown',
  'positive': ['official_date_confirmed']},
 {'id': 'verified-20261128-setagaya-futakotamagawa-rise-green-sky-festa-2026',
  'week': '2026-11-28',
  'ward': '世田谷区',
  'page': 'futako_rise_greenskyfesta_20261122.html',
  'name': 'ソラシドエア presents グリーンスカイフェスタ2026',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001533',
  'date': '2026-11-28',
  'end': '2026-11-29',
  'period': '11/28(土)・11/29(日)',
  'time': '11/28 11:00〜18:00／11/29 10:00〜16:00',
  'venue': 'ガレリア（二子玉川ライズ、世田谷区玉川2-21-1）',
  'price': '公式ページに参加費の記載なし（要確認）',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/3f9f9601.png',
  'description': '九州・沖縄の観光PRブースと特産品販売、お子さま向けの制服試着会、くまモンなどのステージ、スタンプラリー、ガラポン抽選会がある。',
  'categories': ['まつり・イベント', '体験・ワークショップ'],
  'indoor_outdoor': '屋外',
  'reservation': {'required': False, 'note': '申込・予約の記載なし。'},
  'quotes': ['お子さま限定の制服着用体験など、', '2026年11月28日（土）11:00～18:00', '2026年11月29日（日）10:00～16:00'],
  'overall': 'A',
  'basis': 'child_program',
  'child_activity': True,
  'reason': '二子玉川ライズのガレリアで11/28・29に開く、九州・沖縄のフェスタ。お子さま向けの制服試着会、くまモンのステージ、スタンプラリーがある。',
  'axes': {'child_target': 'A', 'interactivity': 'A', 'age_fit': 'B', 'stay_flexibility': 'A', 'burden': 'B', 'cost': 'unknown', 'reservation': 'A', 'family_value': 'A'},
  'strengths': ['お子さま向けの制服試着会とスタンプラリーがある', 'くまモンなどのステージが見られる'],
  'limitations': ['参加費が公式ページに記載がない', '2日間の開催で混雑する可能性がある'],
  'comparison': '総合A：子ども向けの体験とステージがそろう週末イベント。参加費は要確認。',
  'status': 'verified',
  'price_field': 'unknown',
  'positive': ['official_date_confirmed']},
 {'id': 'verified-20261205-setagaya-futakotamagawa-rise-black-rams-send-off',
  'week': '2026-12-05',
  'ward': '世田谷区',
  'page': 'futako_rise_blackrams_20261122.html',
  'name': 'ブラックラムズ東京 2026-27シーズン 出陣式',
  'url': 'https://www.rise.sc/eventnews/detail/?cd=001512',
  'date': '2026-12-05',
  'end': '2026-12-05',
  'period': '12/5(土)',
  'time': '選手登壇出陣式 11:00〜11:30（予定）',
  'venue': 'ガレリア（二子玉川ライズ、世田谷区玉川2-21-1）',
  'price': '公式ページに参加費の記載なし（要確認）',
  'image': 'https://www.rise.sc/uploads/images/resized/0x0/rise/000008/000008/b04435de.png',
  'description': 'ラグビーチームの選手が登壇する出陣式に加え、ラグビー体験会、グッズ販売、マスコットのラムまるグリーティングがある。',
  'categories': ['まつり・イベント', 'スポーツ・体を動かす'],
  'indoor_outdoor': '屋外',
  'reservation': {'required': False, 'note': '申込・予約の記載なし。'},
  'quotes': ['選手登壇出陣式（11:00～11:30予定）', 'ラグビー体験会、グッズ販売、ラムまるグリーティング 他', '2026年12月5日（土）'],
  'overall': 'B',
  'basis': 'all_ages',
  'child_activity': False,
  'reason': '世田谷区のラグビーチームの出陣式で、ラグビー体験会とマスコットのグリーティングがある。内容は予定で、詳細は決まり次第案内される。',
  'axes': {'child_target': 'B', 'interactivity': 'B', 'age_fit': 'B', 'stay_flexibility': 'C', 'burden': 'B', 'cost': 'unknown', 'reservation': 'A', 'family_value': 'B'},
  'strengths': ['ラグビー体験会とマスコットのグリーティングがある', '選手を間近で見られる'],
  'limitations': ['内容は予定で、体験会の時間は未発表', '参加費は公式ページに記載がない'],
  'comparison': '総合B：スポーツ体験つきの出陣式。時間と内容は公式の続報を確認。',
  'status': 'verified',
  'price_field': 'unknown',
  'positive': ['official_date_confirmed']}]
AXIS_REASON = {
    'child_target': {'A': '子ども・家族向けの内容', 'B': '対象の限定はなく、家族で楽しめる'},
    'interactivity': {'A': '体験や参加ができる', 'B': 'ステージを見ながら参加できる部分がある', 'C': '見て楽しむ内容が中心'},
    'age_fit': {'A': '幼児から参加できる', 'B': '年齢の限定はない'},
    'stay_flexibility': {'A': '期間が長く、好きな時間に行ける', 'C': '決まった日・回に合わせる必要がある'},
    'burden': {'A': '短時間で気軽に立ち寄れる', 'B': '屋外のため、寒さと混雑に注意'},
    'cost': {'C': '有料で、費用がかかる', 'A': '無料', 'unknown': '公式ページに記載がない'},
    'reservation': {'A': '申込・予約の記載なし。当日行ける', 'C': '事前予約が必要'},
    'family_value': {'A': '子どもが楽しめる体験がある', 'B': '家族で楽しめる'},
}
for _s in SPECS_RAW:
    _s['axes'] = {k: (v, AXIS_REASON[k][v]) for k, v in _s['axes'].items()}

SPECS = [dict(_r) for _r in SPECS_RAW]
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead42-20261122.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26')}
HELD = {
    'rise-czech-festival-20261204': '二子玉川ライズ チェコフェスティバル（12/4〜6）：本場のビール・料理が中心の大人向けで、時間未定のため保留。',
    'rise-kimono-festa-20261120': '二子玉川ライズ Autumn KIMONO FESTA（11/20〜24）：きものの販売・講座が中心で、子連れ向けではないため対象外。',
    'rise-hotel-chef-cooking-20261206': '二子玉川ライズ ホテルシェフとクッキング体験（12/6）：抽選申込が11/21で終了しているため掲載しない。',
    'rise-futakoza-street-market-20261130': '二子玉川ライズ ふたこ座（11/30〜12/4）：平日開催のため週末対象外。',
    'rise-busking-20261126': '二子玉川ライズ バスキング（11/26・27）：平日開催のため週末対象外。',
    'rise-mens-fudge-20261127': 'men\'sFUDGE MEETING（11/27・28）：ファッション企画で、子連れ向けではないため対象外。',
    'rise-hoikushi-fair-20261129': '保育士就職イベント せたがやフェア（11/29）：就職イベントで、子連れ向けの催しではないため対象外。',
    'rise-kimchi-boroc-mission-20261122': '韓国キムチまつり・坊ロックフェス・ミッションツアー（11/21〜22）：公式の詳細ページが終了・削除済みのため対象外。',
}


def evidence(spec, pages_dir):
    text = _page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for q in spec['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': spec['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-22にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"公式ページ（2026-11-22にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
    return out


def derive(pages_dir):
    out = {}
    for s in SPECS:
        ev = evidence(s, pages_dir)
        if s.get('image'):
            _raw = (pathlib.Path(pages_dir) / s['page']).read_text(encoding='utf-8', errors='ignore')
            if s['image'] not in _raw and S.re.sub(r'^https?://[^/]+', '', s['image']) not in _raw:
                raise ValueError(f"{s['id']}: image URL is not declared on the committed official page")
        fit = S.family_fit(s, ev)
        event = {
            'id': s['id'], 'ward': s['ward'], 'name': s['name'], 'url': s['url'], 'official_url': s['url'], 'source': s['url'],
            'image': s.get('image', ''), 'period': s['period'], 'date_start': s['date'], 'date_end': s.get('end', s['date']), 'time': s['time'],
            'venue': s['venue'], 'price': s['price'], 'description': s['description'], 'categories': s['categories'],
            'indoor_outdoor': s['indoor_outdoor'], 'reservation': s['reservation'], 'family_fit': fit,
            'audit': {'checked_on': CHECKED, 'calendar_index_url': None, 'source_claim': 'verified',
                      'global_23_ward_source_audit_complete': False},
        }
        ver = {'id': s['id'], 'status': 'verified', 'source': s['url'], 'source_kind': 'public_official', 'verified_on': CHECKED,
               'fields': {'name': 'pass', 'date': 'pass', 'venue': 'pass', 'time': 'pass', 'price': s['price_field'],
                          'reservation': 'pass' if s['reservation']['required'] is not None else 'unknown', 'official_url': 'pass'},
               'corrections': {}, 'note': NOTE_AUDIT, 'evidence': ev}
        dec = {'candidate_id': s['id'], 'name': s['name'], 'ward': s['ward'], 'decision': 'published', 'family_fit': fit,
               'positive_signals': s['positive'], 'negative_signals': ['global_source_audit_pending'],
               'hard_exclusion': None, 'exclusion_type': None, 'primary_reason_code': 'family_value_high',
               'reason_codes': ['family_value_high'], 'reasons': [s['reason']],
               'evidence': [{'url': s['url'], 'basis': '2026-11-22 official individual event page (HTTP200); 23 ward completeness not asserted'}],
               'override_reason': '',
               'discovery_sources': [{'channel': 'ai_cross', 'kind': 'ai_cross_search', 'url': s['url']}]}
        out.setdefault(s['week'], []).append((event, ver, dec))
    return out


def build(data_dir, pages_dir):
    d = pathlib.Path(data_dir)
    derived = derive(pages_dir)
    m = S.jload(d / 'manifest.json')
    for week, items in derived.items():
        n = len(items)
        S.jdump(d / SHARDS[week], [i[0] for i in items])
        w = S.jload(d / f'{week}.json')
        w['event_files'] = list(w['event_files']) + [SHARDS[week]]
        cov = w['coverage']
        cov['candidate_count'] += n
        cov['published_count'] += n
        munis = cov.setdefault('municipalities', [])
        for ward in sorted({i[0]['ward'] for i in items}):
            k = sum(1 for i in items if i[0]['ward'] == ward)
            is_ward = ward.endswith('区')
            row = next((r for r in (cov['wards'] if is_ward else munis) if r['ward'] == ward), None)
            if row is None and is_ward:
                raise SystemExit(f'ward row missing: {ward}')
            if row is None:
                row = {'ward': ward, 'candidate_count': 0, 'published_count': 0, 'note': '多摩拡張（v1.41）の初回。'}
                munis.append(row)
            row['candidate_count'] += k
            row['published_count'] += k
            row['note'] += f' 2026-11-22 公式個別ページ確認済み{k}件を非破壊追加。'
        S.jdump(d / f'{week}.json', w)
        v = S.jload(d / f'{week}-verification.json')
        v['events'] += [i[1] for i in items]
        v['summary'] = dict(v['summary'], total=v['summary']['total'] + n, verified=v['summary']['verified'] + n)
        S.jdump(d / f'{week}-verification.json', v)
        dec = S.jload(d / f'{week}-decisions.json')
        dec['decisions'] += [i[2] for i in items]
        dec['summary'] = dict(dec['summary'], candidate_total=dec['summary']['candidate_total'] + n,
                              published=dec['summary']['published'] + n)
        S.jdump(d / f'{week}-decisions.json', dec)
        run = S.jload(d / f'{week}-run.json')
        run['summary'] = dict(run['summary'], candidates=run['summary']['candidates'] + n,
                              published=run['summary']['published'] + n, verified=run['summary']['verified'] + n)
        run['lead42_addition_20261122'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-22T15:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead42-addition-20261122', 'run_type': 'manual_verified_lead42_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-22', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 784, 'candidate_active_week_records': 792, 'added_weekly_records': 8,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '二子玉川ライズの公式イベント一覧から、家族向けの記載がある8件を個別ページで確認して追加。チェコフェスティバル・きもの市・抽選申込の終了した料理体験・平日開催のものは掲載しない。'
    })
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True)
    ap.add_argument('--pages-dir', default='research/2026-11-20-thin-wards/pages')
    a = ap.parse_args()
    try:
        build(a.data_dir, a.pages_dir)
    except ValueError as exc:
        print('ERROR:', exc, file=sys.stderr)
        sys.exit(1)
