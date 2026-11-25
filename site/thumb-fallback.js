/* Fallback thumbnail for events without a usable photo: flat pastel tile + line icon + small ward label. */
(function(root){
  const ICONS={"craft": "<path d=\"M12 3a9 9 0 1 0 0 18c1.7 0 2-1 1.5-2.2-.6-1.4.2-2.8 1.8-2.8H17a4 4 0 0 0 4-4c0-5-4-9-9-9z\"/><circle cx=\"7.5\" cy=\"11\" r=\"1\"/><circle cx=\"10\" cy=\"7\" r=\"1\"/><circle cx=\"15\" cy=\"7\" r=\"1\"/>", "science": "<path d=\"M9 3h6M10 3v6L4.5 19a1.5 1.5 0 0 0 1.3 2.2h12.4a1.5 1.5 0 0 0 1.3-2.2L14 9V3\"/><path d=\"M7.5 15h9\"/>", "book": "<path d=\"M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z\"/><path d=\"M4 19V5\"/><path d=\"M9 8h6\"/>", "music": "<path d=\"M9 18V5l11-2v13\"/><circle cx=\"6\" cy=\"18\" r=\"3\"/><circle cx=\"17\" cy=\"16\" r=\"3\"/>", "sport": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 3v18\"/><path d=\"M5.5 5.5c3.5 2.5 3.5 10.5 0 13M18.5 5.5c-3.5 2.5-3.5 10.5 0 13\"/>", "nature": "<path d=\"M12 22v-6\"/><path d=\"M12 16c-4 0-6-2.5-6-5 0-2 1.5-3 2.5-3.5C8 6 9.5 3 12 3s4 3 3.5 4.5c1 .5 2.5 1.5 2.5 3.5 0 2.5-2 5-6 5z\"/>", "vehicle": "<rect x=\"5\" y=\"3\" width=\"14\" height=\"14\" rx=\"3\"/><path d=\"M5 11h14\"/><circle cx=\"9\" cy=\"14\" r=\".7\"/><circle cx=\"15\" cy=\"14\" r=\".7\"/><path d=\"M8 21l2-4M16 21l-2-4\"/>", "festival": "<path d=\"M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.5 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z\"/>", "play": "<rect x=\"3\" y=\"13\" width=\"8\" height=\"8\" rx=\"1.5\"/><rect x=\"13\" y=\"13\" width=\"8\" height=\"8\" rx=\"1.5\"/><rect x=\"8\" y=\"4\" width=\"8\" height=\"8\" rx=\"1.5\"/>", "museum": "<path d=\"M3 10l9-6 9 6\"/><path d=\"M5 10v8M9.5 10v8M14.5 10v8M19 10v8\"/><path d=\"M3 20h18\"/>", "default": "<circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M8 14c1 1.5 2.5 2 4 2s3-.5 4-2\"/><circle cx=\"9\" cy=\"9.5\" r=\".8\"/><circle cx=\"15\" cy=\"9.5\" r=\".8\"/>"};
  const COLORS={"craft": ["#fde8d8", "#c4673a"], "science": ["#dcecf8", "#2f78ab"], "book": ["#fbf0cf", "#a87a12"], "music": ["#eddff5", "#8750a8"], "sport": ["#dcf1dd", "#3b8f48"], "nature": ["#e3f1d4", "#5a8f35"], "vehicle": ["#dfe8f6", "#4a6fb0"], "festival": ["#fbdfe3", "#c4566a"], "play": ["#fdeccd", "#c07a1d"], "museum": ["#e6e2f4", "#6a5ea8"], "default": ["#e4ecf3", "#5f7f9c"]};
  const CATS=[
    ['festival',/文化祭|祭|フェス|まつり|マルシェ|縁日|クリスマス|サンタ|もちつき|餅つき|ハロウィン|フェスタ|フェスティバル/],
    ['craft',/工作|ものづくり|クラフト|ワークショップ|製作|作ろう|つくろう|作り|ぬりえ|塗り絵|折り紙|スタンプ|ペーパー|バッジ|おえかき|絵/],
    ['science',/科学|実験|理科|サイエンス|プラネタリウム|天文|星|宇宙|ロボット|プログラミング|プラネ/],
    ['book',/読み聞かせ|おはなし|お話|絵本|図書|本の|紙芝居|ブック|読書|よみきかせ|かみしばい|童話|詩/],
    ['music',/音楽|コンサート|演奏|ライブ|リズム|歌|うた|楽器|ミュージカル|合唱|ギター|オーケストラ|ピアノ|ダンス/],
    ['sport',/スポーツ|運動|体操|サッカー|野球|ヨガ|スケボー|スケート|ランニング|ウォーク|パラ|体力|ボッチャ|カヌー/],
    ['nature',/公園|自然|生き物|観察|いきもの|昆虫|ホタル|ほたる|どんぐり|植物|森|水族館|動物園|ビーチ|探鳥|バードウォッチ|探検|ガーデン/],
    ['vehicle',/電車|トレイン|プラレール|鉄道|乗り物|のりもの|バス|飛行機|ヒコーキ|新幹線|車両|ミニカー/],
    ['museum',/博物館|美術館|展|ミュージアム|アート|着物|歴史|文化|伝統|資料館|郷土/],
    ['play',/あそび|遊び|プレイ|親子|ひろば|広場|おもちゃ|ベビー|赤ちゃん|ママ|パパ|児童館|キッズ|子育て|ふれあい|体験/]
  ];
  function pick(ev){
    const name=[ev&&ev.name,ev&&ev.title].filter(Boolean).join(' ');
    const rest=[ev&&ev.description,ev&&ev.venue].filter(Boolean).join(' ');
    for(const t of [name,rest]) for(const c of CATS) if(c[1].test(t)) return c[0];
    return 'default';
  }
  function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));}
  function html(ev){
    const k=pick(ev),c=COLORS[k],ward=String((ev&&ev.ward)||'').replace(/区$/,'');
    return '<div class="thumb ph ph-cat event-list-thumb" style="background:'+c[0]+';color:'+c[1]+'" data-cat="'+k+'"><span class="ph-disc"><svg viewBox="0 0 24 24" width="34" height="34" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+ICONS[k]+'</svg></span>'+(ward?'<span class="ph-ward">'+esc(ward)+'</span>':'')+'</div>';
  }
  root.ThumbFallback={html:html,pick:pick};
})(typeof window!=='undefined'?window:globalThis);
