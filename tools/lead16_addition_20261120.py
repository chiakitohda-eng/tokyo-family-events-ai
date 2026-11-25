#!/usr/bin/env python3
"""12 weekly records (3 programs) from Adachi-ward official event pages (sports centre para-sports, Kuwabukuro biotope park) (2026-11-20).

Raw official pages are committed unchanged under research/2026-11-20-thin-wards/pages/
(fetched by read-only workflows, HTTP 200). Quotes must occur verbatim in those pages.
The gate validator re-derives every record from this module and requires exact equality.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '42a4df85628e29e526f063cc8fe4fbff0b4d163a'   # data-production after the lead15 addition (597 active week records)
CHECKED = '2026-11-20'
AXES = S.AXES
NOTE_AUDIT = '週別全源照合は未完（ためまっぷ403等）。この1件は足立区公式の個別イベントページの確認に基づく。'
S.CHECKED = CHECKED


def _page_text(path):
    """Like suginami page_text, but falls back to the whole document when a page has no <h1>."""
    raw = pathlib.Path(path).read_text(encoding='utf-8', errors='ignore')
    i = raw.find('<h1')
    raw = raw[i:] if i >= 0 else raw
    raw = S.re.sub(r'<(script|style).*?</\1>', '', raw, flags=S.re.S)
    raw = S.re.sub(r'<br\s*/?>|</(p|li|tr|dt|dd|h\d|div|th|td)>', '\n', raw)
    return S.re.sub(r'\s+', '', S.html.unescape(S.re.sub(r'<[^>]+>', '', raw)))


SPECS_RAW = [{"id": "verified-20261129-adachi-cruyff-parasports", "week": "2026-11-28", "ward": "足立区", "page": "adachi_cruyff_nov29.html", "name": "クライフコート パラスポーツ×レクリエーション体験会（ボッチャ・競技用車いす）", "url": "https://www.city.adachi.tokyo.jp/sports/2026event0503.html", "date": "2026-11-29", "period": "11/29(日)", "time": "13:00〜14:30", "venue": "総合スポーツセンター スペシャルクライフコート", "price": "無料", "description": "パラリンピック種目のボッチャや競技用車いすなど、各種パラスポーツを体験できる。どなたでも参加でき、無料。雨天中止。", "cats": ["スポーツ", "体験"], "io": "屋外", "res": {"required": True, "note": "事前申込制（先着順）。窓口・電話・足立区講座予約システムで開催日前日まで。雨天中止。"}, "quotes": ["パラリンピック種目の「ボッチャ」や「競技用車いす」など各種パラスポーツを楽しめます。どなたでも参加できます。", "2026年11月29日（日曜日）13時00分から2026年11月29日（日曜日）14時30分", "名称総合スポーツセンタースペシャルクライフコート", "対象どなたでも募集人数各30名", "費用無料申込方法＜申込開始日（先着順）＞", "※雨天の場合は中止いたします", "令和8年10月26日（月曜日）から開催日前日まで"], "overall": "B", "basis": "all_ages", "child": True, "reason": "11/29(日)13:00〜14:30、スペシャルクライフコートでボッチャや競技用車いすを体験できる。対象はどなたでも、無料。事前申込（先着順・開催日前日まで）が必要で、雨天中止。", "axes": {"child_target": ["B", "対象がどなたでもで、子どもも参加できる"], "interactivity": ["A", "ボッチャや車いすを実際に体験できる"], "age_fit": ["B", "年齢制限がなくどなたでも参加できる"], "stay_flexibility": ["B", "13:00〜14:30の約90分"], "burden": ["B", "事前申込が必要で、雨天中止"], "cost": ["A", "無料"], "reservation": ["B", "先着順の事前申込。開催日前日まで"], "family_value": ["B", "パラスポーツを家族で体験できる"]}, "strengths": ["ボッチャと競技用車いすを体験", "無料でどなたでも参加可"], "limitations": ["事前申込が必要", "雨天中止"], "comparison": "総合B：11/29(日)の総合スポーツセンター スペシャルクライフコートで13:00〜14:30のパラスポーツ体験会。無料。事前申込（先着順）が必要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261206-adachi-cruyff-parasports", "week": "2026-12-05", "ward": "足立区", "page": "adachi_cruyff_dec6.html", "name": "クライフコート パラスポーツ×レクリエーション体験会（ボッチャ・競技用車いす）", "url": "https://www.city.adachi.tokyo.jp/sports/special_cruyffcoat_event20230528.html", "date": "2026-12-06", "period": "12/6(日)", "time": "13:00〜14:30", "venue": "総合スポーツセンター スペシャルクライフコート", "price": "無料", "description": "パラリンピック種目のボッチャや競技用車いすなど、各種パラスポーツを体験できる。どなたでも参加でき、無料。雨天中止。", "cats": ["スポーツ", "体験"], "io": "屋外", "res": {"required": True, "note": "事前申込制（先着順）。窓口・電話・足立区講座予約システムで開催日前日まで。雨天中止。"}, "quotes": ["パラリンピック種目の「ボッチャ」や「競技用車いす」など各種パラスポーツを楽しめます。どなたでも参加できます。", "2026年12月6日（日曜日）13時00分から2026年12月6日（日曜日）14時30分", "名称総合スポーツセンタースペシャルクライフコート", "対象どなたでも募集人数各30名", "費用無料申込方法＜申込開始日（先着順）＞", "※雨天の場合は中止いたします", "令和8年11月26日（木曜日）から開催日前日まで"], "overall": "B", "basis": "all_ages", "child": True, "reason": "12/6(日)13:00〜14:30、スペシャルクライフコートでボッチャや競技用車いすを体験できる。対象はどなたでも、無料。事前申込（先着順・開催日前日まで）が必要で、雨天中止。", "axes": {"child_target": ["B", "対象がどなたでもで、子どもも参加できる"], "interactivity": ["A", "ボッチャや車いすを実際に体験できる"], "age_fit": ["B", "年齢制限がなくどなたでも参加できる"], "stay_flexibility": ["B", "13:00〜14:30の約90分"], "burden": ["B", "事前申込が必要で、雨天中止"], "cost": ["A", "無料"], "reservation": ["B", "先着順の事前申込。開催日前日まで"], "family_value": ["B", "パラスポーツを家族で体験できる"]}, "strengths": ["ボッチャと競技用車いすを体験", "無料でどなたでも参加可"], "limitations": ["事前申込が必要", "雨天中止"], "comparison": "総合B：12/6(日)の総合スポーツセンター スペシャルクライフコートで13:00〜14:30のパラスポーツ体験会。無料。事前申込（先着順）が必要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261121-adachi-kuwabukuro-donguri", "week": "2026-11-21", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-11-21", "period": "11/21(土)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "11/21(土)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：11/21(土)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261122-adachi-kuwabukuro-donguri", "week": "2026-11-21", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-11-22", "period": "11/22(日)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "11/22(日)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：11/22(日)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261128-adachi-kuwabukuro-donguri", "week": "2026-11-28", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-11-28", "period": "11/28(土)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "11/28(土)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：11/28(土)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261129-adachi-kuwabukuro-donguri", "week": "2026-11-28", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-11-29", "period": "11/29(日)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "11/29(日)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：11/29(日)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261205-adachi-kuwabukuro-donguri", "week": "2026-12-05", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-12-05", "period": "12/5(土)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "12/5(土)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：12/5(土)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261206-adachi-kuwabukuro-donguri", "week": "2026-12-05", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-12-06", "period": "12/6(日)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "12/6(日)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：12/6(日)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261212-adachi-kuwabukuro-donguri", "week": "2026-12-12", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-12-12", "period": "12/12(土)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "12/12(土)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：12/12(土)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261213-adachi-kuwabukuro-donguri", "week": "2026-12-12", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-12-13", "period": "12/13(日)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "12/13(日)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：12/13(日)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261219-adachi-kuwabukuro-donguri", "week": "2026-12-19", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-12-19", "period": "12/19(土)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "12/19(土)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：12/19(土)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}, {"id": "verified-20261220-adachi-kuwabukuro-donguri", "week": "2026-12-19", "ward": "足立区", "page": "adachi_kuwabukuro_donguri.html", "name": "【桑袋ビオトープ公園】ドングリクラフト", "url": "https://www.city.adachi.tokyo.jp/k-iji/event/20261110kuwabukuro_donguri.html", "date": "2026-12-20", "period": "12/20(日)", "time": "9:30〜11:30／13:00〜15:30", "venue": "桑袋ビオトープ公園", "price": "無料", "description": "ドングリを使ってコマやネックレスを作るクラフト。3歳以上が対象で、就学前は保護者の参加が必要。事前申込不要で、時間内に随時受付。無料。", "cats": ["工作", "公園"], "io": "屋内・屋外", "res": {"required": False, "note": "事前申込不要。開催時間内に随時受付。"}, "quotes": ["ドングリを使ってコマやネックレスを作ります。", "11月1日から令和9年1月31日：午前9時30分から午前11時30分／午後1時から午後3時30分", "2026年11月1日（日曜日）から2027年3月31日（水曜日）", "名称桑袋ビオトープ公園所在地足立区花畑八丁目2番2号", "対象3歳以上の方※就学前の子どもは保護者の参加が必要です。", "費用無料申込方法事前の申し込みは不要です。"], "overall": "B", "basis": "age_eligible", "child": True, "reason": "12/20(日)の午前9:30〜11:30と午後1:00〜3:30に、桑袋ビオトープ公園でドングリのコマやネックレスを作れる。3歳以上が対象で、無料、申込不要。", "axes": {"child_target": ["B", "3歳以上が対象で、就学前は保護者の参加が必要と明記"], "interactivity": ["A", "ドングリでコマやネックレスを作る工作"], "age_fit": ["B", "3歳以上が対象"], "stay_flexibility": ["A", "時間内に随時参加でき、滞在時間を選べる"], "burden": ["A", "事前申込が不要"], "cost": ["A", "無料"], "reservation": ["A", "事前申込不要で、時間内に随時受付"], "family_value": ["B", "公園で自然素材の工作を楽しめる"]}, "strengths": ["無料・申込不要で随時参加", "ドングリでコマやネックレスを作る"], "limitations": ["3歳以上が対象", "天候等で変更・中止の場合あり"], "comparison": "総合B：12/20(日)の桑袋ビオトープ公園で、9:30〜11:30と13:00〜15:30にドングリクラフトを実施。無料、申込不要。", "extra": [], "pf": "pass", "pos": ["official_date_confirmed", "child_activity_confirmed"]}]
RAW = SPECS_RAW
SPECS = []
for _r in RAW:
    _s = dict(_r)
    _s['categories'] = _s.pop('cats'); _s['indoor_outdoor'] = _s.pop('io'); _s['reservation'] = _s.pop('res')
    _s['child_activity'] = _s.pop('child'); _s['price_field'] = _s.pop('pf'); _s['positive'] = _s.pop('pos')
    SPECS.append(_s)
NEW_IDS = [s['id'] for s in SPECS]
SHARDS = {w: f'{w}-events-lead16-20261120.json' for w in ('2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19')}
HELD = {'adachi-wreath-residents-closed': '【みどりのあそびば】冬のリースづくり（12/12）は区内在住の方向けで、申込期間も11/13に終了しているため掲載しない'}


def evidence(spec, pages_dir):
    text = _page_text(pathlib.Path(pages_dir) / spec['page'])
    out = []
    for q in spec['quotes']:
        if S._strip(q) not in text:
            raise ValueError(f"{spec['id']}: quote not found verbatim in the committed official page: {q}")
        out.append({'url': spec['url'], 'quote': q, 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(q.encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"足立区公式イベントページ（2026-11-20にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。引用文字列だけのUTF-8 SHA-256。"})
    for x in spec.get('extra', []):
        t2 = _page_text(pathlib.Path(pages_dir) / x['page'])
        if S._strip(x['q']) not in t2:
            raise ValueError(f"{spec['id']}: calendar quote not found verbatim in the committed official calendar page: {x['q']}")
        out.append({'url': x['url'], 'quote': x['q'], 'checked_at': CHECKED,
                    'sha256': hashlib.sha256(x['q'].encode('utf-8')).hexdigest(),
                    'hash_scope': 'quoted_text_only_not_HTTP_response_hash',
                    'description': f"足立区公式ページ（2026-11-20にHTTP200で取得、research/2026-11-20-thin-wards/pages/に不変保存）の本文引用。"})
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
               'evidence': [{'url': s['url'], 'basis': '2026-11-20 official individual event page (HTTP200); 23 ward completeness not asserted'}],
               'override_reason': ''}
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
        for ward in sorted({i[0]['ward'] for i in items}):
            k = sum(1 for i in items if i[0]['ward'] == ward)
            for row in cov['wards']:
                if row['ward'] == ward:
                    row['candidate_count'] += k
                    row['published_count'] += k
                    row['note'] += f' 2026-11-20 公式個別ページ確認済み{k}件を非破壊追加。'
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
        run['lead16_addition_20261120'] = {
            'kind': 'individually_verified_official_events_from_lead_triage', 'added_ids': [i[0]['id'] for i in items],
            'held_not_published': sorted(HELD), 'pages_committed_at': 'research/2026-11-20-thin-wards/pages/',
            'base_data_production_sha': BASE, 'global_source_audit_complete': False}
        S.jdump(d / f'{week}-run.json', run)
        for x in m['weekends']:
            if x['sat'] == week:
                x['count'] += n
    m['generated'] = '2026-11-20T11:00:00+09:00'
    S.jdump(d / 'manifest.json', m)
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': 'lead16-addition-20261120', 'run_type': 'manual_verified_lead16_addition',
        'status': 'verified_subset_publication', 'as_of_jst': '2026-11-20', 'executed_at': m['generated'],
        'base_data_production_sha': BASE, 'target_weekends': sorted(derived),
        'prior_active_week_records': 597, 'candidate_active_week_records': 609, 'added_weekly_records': 12,
        'new_event_ids': NEW_IDS, 'held_not_published': sorted(HELD),
        'existing_event_records_physically_deleted': 0, 'image_only_updates': 0,
        'source_failures_remain_unverified': True, 'global_source_audit_complete': False,
        'full_23_ward_25_source_audit_complete': False,
        'note': '足立区立足立区公式サイトのイベントページで日付・時間・会場・対象・料金・申込を確認できた12件の週別レコードのみ追加。',
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
