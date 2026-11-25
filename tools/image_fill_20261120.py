#!/usr/bin/env python3
"""Fill event-specific thumbnails (image) for records added this week whose image was empty.
Each URL is declared on the record's own official page (og:image or an image attached to that page); generic site logos/shared images are excluded.
Image-only: no record added/removed, no other field changed."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = 'aebd327ce6d2fe06f23d410a0e0e4613ed33a5aa'   # data-production after lead29 (704 active week records)
RUN_ID = 'image-fill-20261120'
TARGETS = ['2026-11-21-events-audit-20261119.json', '2026-11-21-events-lead10-20261119.json', '2026-11-21-events-lead12-20261119.json', '2026-11-21-events-lead14-20261119.json', '2026-11-21-events-lead22-20261120.json', '2026-11-21-events-lead26-20261120.json', '2026-11-21-events-lead3-20261119.json', '2026-11-21-events-lead7-20261119.json', '2026-11-21-events-lead9-20261119.json', '2026-11-28-events-lead10-20261119.json', '2026-11-28-events-lead22-20261120.json', '2026-11-28-events-lead5-20261119.json', '2026-11-28-events-lead7-20261119.json', '2026-11-28-events-lead9-20261119.json', '2026-12-05-events-audit-20261119.json', '2026-12-05-events-lead21-20261120.json', '2026-12-05-events-lead22-20261120.json', '2026-12-05-events-lead9-20261119.json', '2026-12-05-events-leads-20261118.json', '2026-12-12-events-lead14-20261119.json', '2026-12-12-events-lead26-20261120.json', '2026-12-12-events-lead9-20261119.json', '2026-12-19-events-lead12-20261119.json', '2026-12-19-events-lead26-20261120.json', '2026-12-26-events-lead18-20261120.json']
IMAGES = {
    'verified-20261121-meguro-shinobu-waiwai': 'https://shinobu-kg.com/wp-content/uploads/2026/08/わいわいパーク28B2515x728-Tate.jpg',
    'verified-20261121-mizunokagaku-suitekikun_dance': 'https://www.mizunokagaku.jp/wp/wp-content/uploads/2026/10/HTVv85PacAA-YQ-.jpg',
    'verified-20261121-setagaya-ikejiri-danball': 'https://www.city.setagaya.lg.jp/images/36827/minnnadea2.png',
    'verified-20261121-setagaya-ikejiri-matcha': 'https://www.city.setagaya.lg.jp/images/36833/omattya.jpg',
    'verified-20261121-setagaya-kamikitazawa-densha': 'https://www.city.setagaya.lg.jp/images/36681/dennsya.jpg',
    'verified-20261121-setagaya-kinupiku-picnic': 'https://www.city.setagaya.lg.jp/images/35481/kamako.png',
    'verified-20261121-setagaya-kitami-tsuru-wreath': 'https://www.city.setagaya.lg.jp/images/33785/kitamijidoukan.jpeg',
    'verified-20261121-suginami-suginoko-nouen-matsuri': 'https://www.city.suginami.tokyo.jp/images/28512/suginokomatsuri_namisuke.jpg',
    'verified-20261121-sumida-smile-festival': 'https://www.city.sumida.lg.jp/kenko_fukushi/syougai/rikai_sokushin/syougaisya-syuukan/smile2026.images/R8chirashi.jpeg',
    'verified-20261122-taito-asakusabashi-kosaku': 'https://www.city.taito.lg.jp/library/kodomo/event/event11/01583891201702041601.images/okiagari.jpeg',
    'verified-20261123-koto-midori-kosodate-kameido': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/images/01_145.jpg',
    'verified-20261123-shibuya-cocolon-xmas': 'https://co-co-lon.com/wp-content/uploads/2026/09/xmasconcert26MV.png',
    'verified-20261128-chuo-fes-contest': 'https://faincation.com/wp/wp-content/uploads/2026/10/91d8e068a46c09f80ef66892ce20c3b8.png',
    'verified-20261128-shinjuku-3r-festa': 'https://www.city.shinjuku.lg.jp/content/000387666.png',
    'verified-20261128-taito-asobo-festa': 'https://www.city.taito.lg.jp/kosodatekyouiku/kosodate/mokutei/kouzaevent/kodomo_center/combination/asobo.images/R8asobo.jpg',
    'verified-20261129-setagaya-celulas-multilingual': 'https://www.city.setagaya.lg.jp/images/34662/20260807_15483376-0001.jpg',
    'verified-20261129-setagaya-daita-inline-1129': 'https://www.city.setagaya.lg.jp/images/31290/daibirdasobo.jpg',
    'verified-20261129-setagaya-kamimachi-bosai-festa': 'https://www.city.setagaya.lg.jp/images/34286/bousaifesta.jpg',
    'verified-20261129-setagaya-seijo-chiiki-bunkasai': 'https://www.city.setagaya.lg.jp/images/20700/img_1047.jpg',
    'verified-20261205-bunkyo-noma-ornament': 'https://kodomo-smile.metro.tokyo.lg.jp/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6MjE1OTIsInB1ciI6ImJsb2JfaWQifX0=--a840344de12fb85e3a6f78cce4d398c167d51af1/%E3%82%AF%E3%83%AA%E3%82%B9%E3%83%9E%E3%82%B9%E3%82%AA%E3%83%BC%E3%83%8A%E3%83%A1%E3%83%B3%E3%83%88%E3%82%AB%E3%83%90%E3%83%BC%E7%94%BB%E5%83%8F%E7%94%A8.png',
    'verified-20261205-nakano-nogata-edit': 'https://kodomo-smile.metro.tokyo.lg.jp/rails/active_storage/blobs/redirect/eyJfcmFpbHMiOnsiZGF0YSI6MjE2NTYsInB1ciI6ImJsb2JfaWQifX0=--d08d578f52744a2bf7fbfa6ec634495d4ae7a60d/%E3%80%90%E3%81%93%E3%81%A9%E3%82%82%E3%81%AE%E7%B7%A8%E9%9B%86%E6%95%99%E5%AE%A4%E3%80%9120251220%E3%82%A2%E3%83%B3%E3%83%87%E3%83%AB%E3%82%BB%E3%83%B3%E3%83%87%E3%83%B3%E3%83%9E%E3%83%BC%E3%82%AF220%20(A4).jpg',
    'verified-20261205-nerima-shogaisha-festival': 'https://www.city.nerima.tokyo.jp/hokenfukushi/shogai/koryu/syogai_festival.images/photo_mogiten1.jpg',
    'verified-20261205-setagaya-daita-decoparfait': 'https://www.city.setagaya.lg.jp/images/36759/daibirdasobo.jpg',
    'verified-20261205-setagaya-kasuya-guitar': 'https://www.city.setagaya.lg.jp/images/36977/guitar.jpg',
    'verified-20261205-setagaya-kitami-shokudo': 'https://www.city.setagaya.lg.jp/images/36877/kitami.png',
    'verified-20261205-suginami-ochiba-kanshasai': 'https://www.city.suginami.tokyo.jp/images/23008/2.jpg',
    'verified-20261206-setagaya-daita-inline-1206': 'https://www.city.setagaya.lg.jp/images/31290/daibirdasobo.jpg',
    'verified-20261206-suginami-fureai-festa': 'https://www.city.suginami.tokyo.jp/images/23030/dant.jpg',
    'verified-20261212-mizunokagaku-original_garland': 'https://www.mizunokagaku.jp/wp/wp-content/uploads/2026/01/20250926104543-scaled.jpeg',
    'verified-20261212-setagaya-kamimachi-saturday': 'https://www.city.setagaya.lg.jp/images/36891/shiroba.jpg',
    'verified-20261213-koto-papa-happy-xmas-tree-art': 'https://www.city.koto.lg.jp/011501/kuse/koho/kuho/r08/text/images/01_145.jpg',
    'verified-20261213-setagaya-futakotamagawa-xmas-concert': 'https://www.city.setagaya.lg.jp/images/35905/xmasconcert2026_chirashi.jpg',
    'verified-20261219-setagaya-daita-candle': 'https://www.city.setagaya.lg.jp/images/36758/daibirdasobo.jpg',
    'verified-20261219-setagaya-kasuya-baton': 'https://www.city.setagaya.lg.jp/images/36978/baton.jpg',
    'verified-20261219-setagaya-seijo-sakura-candle': 'https://www.city.setagaya.lg.jp/images/36774/hpkeisaiyou.jpg',
    'verified-20261220-mizunokagaku-tubc_free_throw': 'https://www.mizunokagaku.jp/wp/wp-content/uploads/2025/11/IMG_0683-scaled.jpg',
    'verified-20261226-nerima-oshigoto-nishihonmura': 'https://www.city.nerima.tokyo.jp/kurashi/shigoto/midori/shokai/nerimanomori.images/kodomofesurogo.png',
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
        'executed_at': '2026-11-20T20:00:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': ['2026-11-21', '2026-11-28', '2026-12-05', '2026-12-12', '2026-12-19', '2026-12-26'],
        'prior_active_week_records': 704, 'candidate_active_week_records': 704, 'added_weekly_records': 0,
        'new_event_ids': [], 'image_updated': changed, 'existing_event_records_physically_deleted': 0,
        'image_only_updates': len(changed), 'global_source_audit_complete': False,
        'note': '今週追加した公式ページ由来の記録のうち、公式ページに掲載された行事固有の画像があるものだけサムネイルを設定。サイト共通ロゴ・共有画像は対象外。画像以外は変更なし。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
