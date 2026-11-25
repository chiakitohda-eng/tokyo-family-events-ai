#!/usr/bin/env python3
"""Fill event-specific thumbnails (image) for records added this week whose image was empty.
Each URL is declared on the record's own official page (og:image or an image attached to that page); generic site logos/shared images are excluded.
Image-only: no record added/removed, no other field changed."""
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import suginami_addition_20261118 as S

BASE = '87baeaf5b43d74bf0a9fe202b566d0de8a8e0297'   # data-production at image-fill4-20261122 (783 published)
RUN_ID = 'image-fill4-20261122'
TARGETS = ['2026-11-21-events-lead22-20261121.json', '2026-11-21-events-lead27-20261121.json', '2026-11-21-events-lead33-20261121.json', '2026-11-21-events-lead34-20261121.json', '2026-11-21-events-lead35-20261121.json', '2026-11-21-events-lead36-20261121.json', '2026-11-21-events-lead37-20261121.json', '2026-11-21-events-lead39-20261121.json', '2026-11-21-events-lead40-20261121.json', '2026-11-28-events-lead39-20261121.json', '2026-12-05-events-lead22-20261121.json', '2026-12-05-events-lead25-20261121.json', '2026-12-05-events-lead26-20261121.json', '2026-12-05-events-lead33-20261121.json', '2026-12-05-events-lead36-20261121.json', '2026-12-05-events-lead37-20261121.json', '2026-12-05-events-lead38-20261121.json', '2026-12-12-events-lead38-20261121.json', '2026-12-19-events-lead27-20261121.json', '2026-12-19-events-lead33-20261121.json', '2026-12-19-events-lead34-20261121.json', '2026-12-19-events-lead38-20261121.json']
IMAGES = {
    'verified-20261123-itabashi-hase-nazotoki': 'https://www.mech.kanagawa-u.ac.jp/lab/hase_lab/HASE-Lab-Nazotoki.png',
    'verified-20261121-chofu-jindai-rose-festa': 'https://www.city.chofu.lg.jp/images/18497/img_5641-2.jpg',
    'verified-20261121-tachikawa-showakinen-craft-leaf-2026': 'https://www.showakinen-koen.jp/wp-content/uploads/2024/03/IMG_4563C.jpg',
    'verified-20261121-tachikawa-showakinen-greenexpo-20261123': 'https://www.showakinen-koen.jp/wp-content/uploads/2026/11/f335fc68fdb36ab92931f4d0adff894e.jpg',
    'verified-20261121-tama-puroland-illumination-xmas-2026': 'https://www.puroland.jp/wp-content/uploads/2026/10/2026_christmas_KV-840x630.jpg',
    'verified-20261121-bunkyo-asobono-ahiru-taicho-20261110': 'https://www.tokyo-dome.co.jp/files/facilities/asobono/event/ahirutaichou/Asobono_ahirut_banner_4x3.jpg',
    'verified-20261121-hino-tamazoo-africa-fair-20261122': 'https://www.tokyo-zoo.net/image/tama/news/12878/11.jpg',
    'verified-20261121-sumida-solamachi-xmasmarket-2026': 'https://www.tokyo-solamachi.jp/img/event/20261105_xmasmarket/main01.jpg',
    'verified-20261121-minato-joypolis-digitareal-illumination-2026': 'https://tokyo-joypolis.com/event/illumination2026/images/thumb_illumination.jpg',
    'verified-20261121-toshima-sunshine60-candle-workshop-2026': 'https://sunshinecity.jp/archives/003/202611/71870f098b042d2f4b1d0d23a9fb3a7b850c9a7d9be33c0f2ca8915e8da2d535.jpg',
    'verified-20261121-chofu-jindai-konomi-kusanomi-ten-2026': 'https://www.tokyo-park.or.jp/park/jindai/assets/2026kinomikusanomi_poster.webp',
    'verified-20261121-musashino-inokashira-zoo-stamp-rally-shinka-2026': 'https://www.tokyo-zoo.net/image/13386_01.jpg',
    'verified-20261121-komae-mirai-terrace-festival-2026': 'https://www.komae.ed.jp/images/content/11343/1.png',
    'verified-20261128-musashino-inokashira-zoo-ochiba-oekaki-2026': 'https://www.tokyo-zoo.net/image/inokashira/news/11011/29517_01.jpg',
    'verified-20261205-minato-ogimama-book-christmas': 'https://kodomo-smile.metro.tokyo.lg.jp/images/kodomo_ambassador/img_ogimama.png',
    'verified-20261205-inagi-giants-hometown-fes': 'https://www.city.komae.tokyo.jp/images/content/146380/20260929-194030.png',
    'verified-20261205-musashino-family-xmas-concert': 'https://www.musashino.or.jp/_res/common/event/2026/2026.8-11/family_christmas_omote.png',
    'verified-20261121-tachikawa-showakinen-sippofesta-20261205': 'https://www.showakinen-koen.jp/wp-content/uploads/2026/11/1105.jpg',
    'verified-20261205-koganei-park-bousai-festa-2026': 'https://www.tokyo-park.or.jp/park/koganei/assets/%E3%83%81%E3%83%A9%E3%82%B7%E8%A1%A8.jpg',
    'verified-20261205-shibuya-yoyogi-donguri-kosaku-20261206': 'https://www.tokyo-park.or.jp/park/yoyogi/assets/%E3%81%A9%E3%82%93%E3%81%90%E3%82%8A%E5%B7%A5%E4%BD%9C2026.png',
    'verified-20261205-meguro-ishibumi-tudoi-papa-fureai': 'https://www.city.meguro.tokyo.jp/images/20660/ishibumi1205.jpg',
    'verified-20261205-edogawa-mirai-xmas-tree-denshi': 'https://www.city.edogawa.tokyo.jp/images/75109/1205christmas.jpg',
    'verified-20261212-meguro-karasumori-tudoi-xmas-kazari': 'https://www.city.meguro.tokyo.jp/images/18414/kara.jpg',
    'verified-20261213-meguro-mukaihara-tudoi-kisetsu-kosaku': 'https://www.city.meguro.tokyo.jp/images/20284/kisetunokousaku.png',
    'verified-20261212-meguro-komaba-tudoi-athletic-kosaku': 'https://www.city.meguro.tokyo.jp/images/20361/webkirachan.png',
    'verified-20261219-chofu-family-concert-0sai-classic': 'https://www.city.chofu.lg.jp/images/18629/lupinusquartet.jpg',
    'verified-20261121-tachikawa-showakinen-craft-oshogatsu-20261219': 'https://www.showakinen-koen.jp/wp-content/uploads/2024/09/IMG_5579-1.jpg',
    'verified-20261121-bunkyo-dome-cinema-christmas-20261219': 'https://www.tokyo-dome.co.jp/files/tdc/202610/illumination/img_event_cinema.jpg',
    'verified-20261219-meguro-gohongi-tudoi-santa': 'https://www.city.meguro.tokyo.jp/images/20863/nyuyoujinotudoi.jpg',
    'verified-20261219-edogawa-mirai-shimenawa-oyako': 'https://www.city.edogawa.tokyo.jp/images/75115/12191shimenawa.jpg',
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
        'run_id': RUN_ID, 'run_type': 'manual_image_alignment', 'status': 'image_only_update', 'as_of_jst': '2026-11-22',
        'executed_at': '2026-11-22T14:30:00+09:00', 'base_data_production_sha': BASE, 'target_weekends': ['2026-11-22'],
        'prior_active_week_records': 783, 'candidate_active_week_records': 783, 'added_weekly_records': 0,
        'new_event_ids': [], 'image_updated': changed, 'existing_event_records_physically_deleted': 0,
        'image_only_updates': len(changed), 'global_source_audit_complete': False,
        'note': '今週追加した公式ページ由来の記録のうち、公式ページに掲載された行事固有の画像があるものだけサムネイルを設定。サイト共通ロゴ・共有画像は対象外。画像以外は変更なし。'})
    S.jdump(d / 'update_history.json', h)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--data-dir', required=True); a = ap.parse_args()
    try: build(a.data_dir)
    except ValueError as e: print('ERROR:', e, file=sys.stderr); sys.exit(1)
