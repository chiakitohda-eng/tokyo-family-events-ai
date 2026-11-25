#!/usr/bin/env python3
"""Fill event-specific thumbnails (image) for records added this week whose image was empty.
Each URL is declared on the record's own official page (og:image or an image attached to that page); generic site logos/shared images are excluded.
Image-only: no record added/removed, no other field changed."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '702a868ec13bce2cb93fa4a4de0eda2968fc599c'   # data-production after image-fill-20261120 (704 active week records)
RUN_ID = 'image-fill2-20261120'
TARGETS = ['2026-11-21-events-lead10-20261119.json', '2026-11-21-events-lead12-20261119.json', '2026-11-21-events-lead15-20261120.json', '2026-11-21-events-lead16-20261120.json', '2026-11-21-events-lead20-20261120.json', '2026-11-21-events-lead27-20261120.json', '2026-11-21-events-lead3-20261119.json', '2026-11-21-events-lead6-20261119.json', '2026-11-21-events-lead7-20261119.json', '2026-11-21-events-leads-20261118.json', '2026-11-28-events-lead11-20261119.json', '2026-11-28-events-lead12-20261119.json', '2026-11-28-events-lead15-20261120.json', '2026-11-28-events-lead16-20261120.json', '2026-11-28-events-lead20-20261120.json', '2026-11-28-events-lead7-20261119.json', '2026-12-05-events-lead11-20261119.json', '2026-12-05-events-lead15-20261120.json', '2026-12-05-events-lead16-20261120.json', '2026-12-05-events-lead19-20261120.json', '2026-12-05-events-lead20-20261120.json', '2026-12-05-events-lead6-20261119.json', '2026-12-05-events-lead9-20261119.json', '2026-12-12-events-lead11-20261119.json', '2026-12-12-events-lead12-20261119.json', '2026-12-12-events-lead15-20261120.json', '2026-12-12-events-lead16-20261120.json', '2026-12-12-events-lead6-20261119.json', '2026-12-19-events-lead12-20261119.json', '2026-12-19-events-lead15-20261120.json', '2026-12-19-events-lead16-20261120.json', '2026-12-19-events-lead23-20261120.json', '2026-12-19-events-lead24-20261120.json', '2026-12-19-events-lead29-20261120.json', '2026-12-19-events-lead6-20261119.json']
IMAGES = {
    'verified-20261121-adachi-galaxcity-kosaku-holiday': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2023/04/94a4043a58b9f642d6b401b98345483f7ebb91cc-thumb-1024x732-9803.jpg',
    'verified-20261121-adachi-galaxcity-starday-mini': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/e2e99bd5e2d714ec2c698dfeb210dbcb168ce0e4-thumb-976x550-17758.jpg',
    'verified-20261121-adachi-galaxcity-starday-oekaki': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/0af8081703a487a78172cd547f37e8bfb640e961-thumb-976x550-17759.jpg',
    'verified-20261121-adachi-galaxcity-starday-seiza': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/6b617d3ed1f93879c9a2eb20590033077d737ab8-thumb-976x550-17757.jpg',
    'verified-20261121-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261121-edogawa-fuyusakura': 'https://www.city.edogawa.tokyo.jp/images/75153/img_2440.jpg',
    'verified-20261121-edogawa-kasai-night-watching': 'https://www.city.edogawa.tokyo.jp/images/75074/images.png',
    'verified-20261121-koto-umi-hikoki': 'https://uminomoripark.com/cms/wp-content/uploads/2026/03/ヒコーキを飛ばそう_サムネ.png',
    'verified-20261121-meguro-higashiyama-yoga': 'https://www.city.meguro.tokyo.jp/images/20724/higashiyama.jpg',
    'verified-20261121-meguro-kodomo-ongakusai': 'https://www.city.meguro.tokyo.jp/images/16934/s.jpg',
    'verified-20261122-adachi-galaxcity-kosaku-holiday': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2023/04/94a4043a58b9f642d6b401b98345483f7ebb91cc-thumb-1024x732-9803.jpg',
    'verified-20261122-adachi-galaxcity-shougai-nov22': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/05/2a220e818e79fbec4821c26afb385120f8272704-thumb-976x550-17077.jpg',
    'verified-20261122-adachi-galaxcity-starday-mini': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/e2e99bd5e2d714ec2c698dfeb210dbcb168ce0e4-thumb-976x550-17758.jpg',
    'verified-20261122-adachi-galaxcity-starday-oekaki': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/0af8081703a487a78172cd547f37e8bfb640e961-thumb-976x550-17759.jpg',
    'verified-20261122-adachi-galaxcity-starday-seiza': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/6b617d3ed1f93879c9a2eb20590033077d737ab8-thumb-976x550-17757.jpg',
    'verified-20261122-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261122-bunkyo-motomachi-fes': 'https://www.city.bunkyo.lg.jp/images/13872/photo1.jpg',
    'verified-20261122-edogawa-shinkawa-hyakkiyako': 'https://www.city.edogawa.tokyo.jp/images/74419/hyakiyakou1.jpg',
    'verified-20261122-tohaku-canbadge': 'https://www.tnm.jp/uploads/fckeditor/event/202611/uid000412_202609182007590e3c9627.jpg',
    'verified-20261122-tohaku-kimono': 'https://www.tnm.jp/uploads/fckeditor/uid000474_20261009153127361b6c20.jpg',
    'verified-20261122-tohaku-nurie': 'https://www.tnm.jp/uploads/fckeditor/uid000418_202609111507402f3fb349.jpg',
    'verified-20261122-tohaku-papercraft': 'https://www.tnm.jp/uploads/fckeditor/event/202611/uid000412_202609182013348f37d8f6.jpg',
    'verified-20261122-tohaku-tanken': 'https://www.tnm.jp/uploads/fckeditor/event/202607/uid000452_202606061640252b981a03.png',
    'verified-20261123-adachi-galaxcity-kosaku-holiday': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2023/04/94a4043a58b9f642d6b401b98345483f7ebb91cc-thumb-1024x732-9803.jpg',
    'verified-20261123-adachi-galaxcity-toshokan-nov23': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/a3ae9b72629f6cbc2db7bb1ae51e3ad650e750fc-thumb-976x550-17807.jpg',
    'verified-20261123-arakawa-film-rocket-stars': 'https://www.city.arakawa.tokyo.jp/images/46984/hosizora.jpg',
    'verified-20261123-arakawa-hoshizora-rocket': 'https://www.city.arakawa.tokyo.jp/images/46984/hosizora.jpg',
    'verified-20261123-edogawa-walking-festa': 'https://www.city.edogawa.tokyo.jp/images/49504/uokin.jpg',
    'verified-20261128-adachi-galaxcity-kosaku-holiday': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2023/04/94a4043a58b9f642d6b401b98345483f7ebb91cc-thumb-1024x732-9803.jpg',
    'verified-20261128-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261128-adachi-seibutsuen-hotaru': 'https://www.city.adachi.tokyo.jp/images/74225/seibutsuen3.jpg',
    'verified-20261128-chuo-harumi-matsuri': 'https://www.city.chuo.lg.jp/images/16093/harumirai_r.jpg',
    'verified-20261128-meguro-gohongi-oyako-asobo': 'https://www.city.meguro.tokyo.jp/images/20858/aragane.jpg',
    'verified-20261129-adachi-cruyff-parasports': 'https://www.city.adachi.tokyo.jp/images/75710/000.png',
    'verified-20261129-adachi-galaxcity-brillante-nov29': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/06/9b41d5766a6e7987d7600bc84d2e020cac1adf85-thumb-976x550-17289.jpg',
    'verified-20261129-adachi-galaxcity-kosaku-holiday': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2023/04/94a4043a58b9f642d6b401b98345483f7ebb91cc-thumb-1024x732-9803.jpg',
    'verified-20261129-adachi-galaxcity-yume-clay-nov29': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/01/eac0458dc470dc9dd2fc9f3f5bb4d3edc35b76e5-thumb-976x550-16155.jpg',
    'verified-20261129-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261129-edogawa-recycle-world-tobu': 'https://www.city.edogawa.tokyo.jp/images/75159/recycle.jpg',
    'verified-20261129-shinjuku-ttm-sugoroku': 'https://art-play.or.jp/ttm/wp/wp-content/uploads/2026/11/sugo.png',
    'verified-20261205-adachi-galaxcity-robot-yuuenchi': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/10/323083463c518c7e394f75faa79c776bc3992426-thumb-1275x442-18072.jpg',
    'verified-20261205-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261205-adachi-seibutsuen-hotaru': 'https://www.city.adachi.tokyo.jp/images/74225/seibutsuen3.jpg',
    'verified-20261205-arakawa-yuen-ornament': 'https://www.city.arakawa.tokyo.jp/images/47102/xmas_ws20261205.png',
    'verified-20261205-edogawa-fuyusakura': 'https://www.city.edogawa.tokyo.jp/images/75153/img_2440.jpg',
    'verified-20261205-minato-aiport-xmas-concert': 'https://www.city.minato.tokyo.jp/images/182122/20261029153643.jpg',
    'verified-20261205-shinjuku-ttm-harikoko': 'https://art-play.or.jp/ttm/wp/wp-content/uploads/2026/01/未干支張り子.jpg',
    'verified-20261205-shinjuku-ttm-satoyama': 'https://art-play.or.jp/ttm/wp/wp-content/uploads/2026/11/くるくるオーナメント-1.png',
    'verified-20261206-adachi-cruyff-parasports': 'https://www.city.adachi.tokyo.jp/images/61153/000.png',
    'verified-20261206-adachi-galaxcity-robot-yuuenchi': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/10/323083463c518c7e394f75faa79c776bc3992426-thumb-1275x442-18072.jpg',
    'verified-20261206-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261206-bunkyo-bosai-festa': 'https://www.city.bunkyo.lg.jp/images/9930/omote.jpg',
    'verified-20261206-minato-mizube-sanpo-nurie': 'https://www.city.minato.tokyo.jp/images/182089/20261029131551.jpg',
    'verified-20261206-shinagawa-nagisa-beach': 'https://tokyo-south-seaside-parks.com/wp-content/uploads/2026/04/event01-1280x634.png',
    'verified-20261212-adachi-galaxcity-caravan-dec12': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/08/xmas-thumb-600x454-17768.png',
    'verified-20261212-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261212-adachi-seibutsuen-hotaru': 'https://www.city.adachi.tokyo.jp/images/74225/seibutsuen3.jpg',
    'verified-20261212-edogawa-fuyusakura': 'https://www.city.edogawa.tokyo.jp/images/75153/img_2440.jpg',
    'verified-20261212-minato-plaza-shinmei-festival': 'https://www.city.minato.tokyo.jp/images/182271/20261113115101.png',
    'verified-20261213-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261213-edogawa-bunkageijutsusai-ongakusai': 'https://www.city.edogawa.tokyo.jp/images/73696/ongaku-1.jpg',
    'verified-20261219-adachi-galaxcity-babymassage-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/05/707d8c26de089e1b45fea428ebe5858db11ca4e7-thumb-976x550-17152.jpg',
    'verified-20261219-adachi-galaxcity-dakko-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/09/d3af7ff63c7a84d59eaa3bc26afaeb93ac805ddf-thumb-976x550-17932.jpg',
    'verified-20261219-adachi-galaxcity-gokko-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/11/241c29b371194b3782b7670f461ff01af9946738-thumb-600x450-18216.jpg',
    'verified-20261219-adachi-galaxcity-hihai-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2025/11/570bd817722fd587ccd5d936d71246967bbf7516-thumb-976x549-15619.jpg',
    'verified-20261219-adachi-galaxcity-oshigoto-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/11/9a136d4d9e756a6e332da2bbfa0b028e6371d2f2-thumb-1024x768-18230.png',
    'verified-20261219-adachi-galaxcity-photospot-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/11/4b25f005c4a29e917f2cd01ed686b7981283b398-thumb-500x282-18226.jpg',
    'verified-20261219-adachi-galaxcity-present-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/11/36cf4f98230825d9b4a3dee71b155494754027da-thumb-500x375-18224.jpg',
    'verified-20261219-adachi-galaxcity-santa-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/09/92029b20db57c4a0400403bbfc3881b326c095b7-thumb-1280x720-17946.jpg',
    'verified-20261219-adachi-galaxcity-undou-dec19': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/11/e7380631b1e5505730e55d17a8ce4d0477faf335-thumb-500x375-18225.jpg',
    'verified-20261219-adachi-galaxcity-xmasfes-planet': 'https://www.galaxcity.jp/future-creation-hall/assets_c/2026/11/592a0cfeb73a8547b3b70799109d6d4a862e2cca-thumb-976x550-18173.jpg',
    'verified-20261219-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261219-adachi-seibutsuen-hotaru': 'https://www.city.adachi.tokyo.jp/images/74225/seibutsuen3.jpg',
    'verified-20261219-edogawa-fuyusakura': 'https://www.city.edogawa.tokyo.jp/images/75153/img_2440.jpg',
    'verified-20261219-edogawa-kamiisshiki-magic': 'https://www.city.edogawa.tokyo.jp/images/75061/majic.jpg',
    'verified-20261219-edogawa-kodomomirai-shimenawa': 'https://www.city.edogawa.tokyo.jp/images/75115/12191shimenawa.jpg',
    'verified-20261219-meguro-higashine-xmas': 'https://www.city.meguro.tokyo.jp/images/20797/1219.jpg',
    'verified-20261219-meguro-higashiyama-english': 'https://www.city.meguro.tokyo.jp/images/20725/higashiyama.jpg',
    'verified-20261219-meguro-tairamachi-baby-xmas': 'https://www.city.meguro.tokyo.jp/images/20749/tairamati2.png',
    'verified-20261219-toshima-hinemos-concert': 'https://www.toshima-mirai.or.jp/Portals/0/images/performance/2612/WinterWonderLand_f-s.jpg',
    'verified-20261220-adachi-kuwabukuro-donguri': 'https://www.city.adachi.tokyo.jp/images/70098/kuwabukuro3.jpg',
    'verified-20261220-arakawa-ogu-library-xmas': 'https://www.city.arakawa.tokyo.jp/images/46692/202612kurisumasu.png',
    'verified-20261220-jonanjima-skateboard-class': 'https://tokyo-south-seaside-parks.com/wp-content/uploads/2026/04/20260517スケボー教室城南-960x720.jpg',
    'verified-20261220-tohaku-canbadge': 'https://www.tnm.jp/uploads/fckeditor/event/202612/uid000412_20261016132357a72da95d.jpg',
    'verified-20261220-tohaku-papercraft': 'https://www.tnm.jp/uploads/fckeditor/event/202612/uid000412_2026101613501212a50899.jpg',
    'verified-20261220-toshima-hinemos-concert': 'https://www.toshima-mirai.or.jp/Portals/0/images/performance/2612/WinterWonderLand_f-s.jpg',
}


def build(data_dir):
    d = pathlib.Path(data_dir); changed = []
    for fn in TARGETS:
        data = S.jload(d / fn); rows = data if isinstance(data, list) else data['events']
        for r in rows:
            if r.get('id') in IMAGES and r.get('image') in (None, ''):
                r['image'] = IMAGES[r['id']]; changed.append(r['id'] + '@' + fn[:10])
        S.jdump(d / fn, data)
    if len(changed) != len(IMAGES) or len(set(changed)) != len(changed):
        raise ValueError(f'expected {len(IMAGES)} image fills, got {len(changed)}')
    h = S.jload(d / 'update_history.json')
    h['history'].append({
        'run_id': RUN_ID, 'run_type': 'manual_image_alignment', 'status': 'image_only_update', 'as_of_jst': '2026-11-20',
        'executed_at': '2026-11-20T22:30:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': ['2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19'],
        'prior_active_week_records': 704, 'candidate_active_week_records': 704, 'added_weekly_records': 0,
        'new_event_ids': [], 'image_updated': changed, 'existing_event_records_physically_deleted': 0,
        'image_only_updates': len(changed), 'global_source_audit_complete': False,
        'note': '今週追加した公式ページ由来の記録のうち、公式ページに掲載された行事固有の画像があるものだけサムネイルを設定。サイト共通ロゴ・共有画像は対象外。画像以外は変更なし。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
