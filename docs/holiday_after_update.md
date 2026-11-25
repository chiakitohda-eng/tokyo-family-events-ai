# 休日明け6週間更新：日付可変計画（ステージング用）

本処理は **計画専用** であり、イベントの探索・再監査・本番更新・デプロイは実行しない。旧 tools/initial_v15_native_research.py は2026年10月の固定日付と古い判定ロジックを持つため、v1.15以降の正式な更新には使用しない。

最初に production ブランチの site/data/latest_prompt.json と prompt_history.json の整合を確認し、data-production の現行SHAを固定する。site/data のmanifestは data-production の実データを使用する。

実行例：

    python3 tools/rolling_horizon.py --as-of 2026-10-13 --base-data-production-sha <実際の40文字SHA> --output /tmp/holiday-plan.json

--as-of を省略すると日本時間の当日日付を採用。内閣府公式祝日CSV取得失敗・年度不足はBLOCKERとして失敗、休日明け以外は status=skipped。対象日なら status=eligible と42日間、6つの週末、祝日、検索URLを出力する。公式祝日は土日と別の平日祝日探索対象として扱う。

planは site/data には書き込めず、検索結果や「checked」「verified」は生成しない。計画を使い、正式プロンプトに基づく23区それぞれのAI探索、全required明示参照元、年間日程表の行単位監査、候補decision、公式照合、非退行、画像、祝日開催可否の実測を完了する。未完了なら公開不可。

変更候補は data-production の基準SHAに基づく data-staging 上のデータ許可ファイルに限定し、Strict検証後のみ既存の data専用デプロイ経路を利用する。production アプリコード・公開Versionは変更しない。

回帰テスト: npm test （Python単体は python3 -m unittest discover -s tests -p test_rolling_horizon.py）。

## 休日明け更新の履歴を必ず保存

実際の23区探索、全公式監査、画像、厳格バリデーションが終わり、未公開の data-staging 候補を作成したあと、data-production の現行SHAを基準に履歴を生成する。

    node tools/holiday_update_history.mjs --write --as-of 2026-10-13 --base-ref <data-production-SHA> --data-dir site/data

これにより既存の履歴を残したまま、更新日・6週間の対象期間・前後のユニークイベント数・追加・変更・掲載終了・対象期間外に出た数の1行が増える。イベント個票は公開アプリの eventIdentityKey と同じキー、verifications とサブファイルを読み込んで数える。実際の更新をしなかった場合は生成しない。

data-staging に上記JSONを含めてコミットする。operation=holiday-after-update のデータ本番反映時は、既存の CI で厳格監査したあと、さらに node staging-policy-src/tools/holiday_update_history.mjs --check ... を実行し、過去履歴の削除、未記録、件数差異や期間差異を検出したら公開を止める。**Pages反映成功後にのみ本番で履歴が見える**。アプリのリリースだけではデータ更新履歴に追加しない。


## 2026-10-19: 実測収集とレビュー資料（本番とは分離）

休日明け計画の次段として tools/holiday_after_collect.py と tools/holiday_after_review_packet.py を追加。
計画は内閣府公式祝日CSV、公開された production/site/data/latest_prompt.json と production/site/data/discovery_sources.json、現在の data-production SHA を正本として生成する。

読み取り専用 Holiday-after real-source evidence GitHub Actions の処理:
1. 23区それぞれに実際の月・週・土日を指定して横断検索し、平日祝日も日付を明示して独立探索する。区公式トップページも実測する。
2. 有効な明示参照元はすべて search_urls 単位で巡回する。年度表は公式一覧から年度別ページを解決し、各行を候補へ分割する。
3. HTTP成否・最終URL・日時・SHA256・検索語・候補URLを summary.json / requests.json / candidate_pool.json に残す。
4. 過去の掲載IDを保護した review_packet.json を作る。期間の重複は開催日確認済みではない。
5. GitHub Actionsの holiday-after-source-evidence に非公開レビュー資料を保存する。候補の掲載は行わない。

必須ルール:
- 有効RSSヒット0件と HTTP/パース失敗を区別する。失敗は0件扱いしない。
- 公式トップのHTTP 200と、各イベントの日時・会場・参加条件の確認は別の工程である。
- candidate_pool、review_packet は常に publication_permitted=false、掲載用JSONや更新履歴に混ぜない。
- ためまっぷなかのがHTTP 403を返した場合は必須参照元のエラーとして記録し、無断でチェック済みや別URLへ置換しない。
- 休日が過ぎた旧週のJSONは履歴保護し、変更/削除には正式な根拠と個別承認が必要。

本番データ更新へ進む条件:
全候補について公式照合・日時・会場・画像・重複・family-fit-v2・各週decisionの個別監査を完了する。
data-productionの基準SHAで data-staging に許可された日付別JSON、manifest.json、update_history.json だけを生成する。
その後 validate_data.py --strict、validate_decisions.py --strict、validate_official_schedule_audit.py、validate_non_regression.py、validate_protected_events.py、npm test と履歴一致確認を通す。
合格候補だけを既存の .github/data-deploy-trigger.txt / deploy.yml で反映し、Actions、Pages、公開件数、更新履歴、data-releaseスナップショットを照合する。
アプリコード・productionブランチ・公開Versionは定期データ更新では変えない。

注意: 調査Actionの成功は発見資料の作成成功を示すだけで、本番データ更新完了や掲載審査のPASSではない。


## 2026-10-20 ためまっぷCloudflare 403の公式情報補完

- ためまっぷなかのはCloudflareチャレンジでGitHub Actionsから403。登録済みの `tamemap_nakano` は削除・無効化・成功扱いしない。
- 新規 `policy/nakano_supplemental_sources.json` はデータ公開正本を変更せず、実測候補発見処理だけへ追加する *ステージング専用* 補完登録。
- 追加した経路：中野区公式イベント全般の月間カレンダー、子育て・教育の月間カレンダー、中野区社会福祉協議会イベント・地域活動一覧（4系列）。
- カレンダーの `{YYYY}{MM}` 詳細URLが404の場合は `list_calendar.html` を確認する。ただし本文に **指定年・指定月** がない場合は代替成功としない。0件とHTTP失敗を区別する。
- 区のHTML日付行から独立参加単位を仮候補として抽出する。同日の同一URLは全般/子育て両一覧で重複統合し、異なる日は別の参加単位とする。
- 社協の掲載物は日付未確認の候補。開催日・会場・対象年齢・予約/料金・サムネ・主催者確定を推測せず、公式個別ページによる確認待ちとする。
- `tools/holiday_after_collect.py` の `--supplemental-config` 経由で通常の23区横断Actionへ取り込む。`supplemental_sources.json` と `candidate_pool.json` をArtifact化し、`holiday_after_review_packet.py` の各週/祝日レビュー対象へ引き継ぐ。
- 追加情報源は `tamemap_nakano` の required 検査を満たすものではない。403はそのままblockerに残す。収集候補を掲載確定扱いにして `data-production` を昇格させることは禁止。
- データ掲載更新へ進むには、従来の正式プロンプトv1.15、全23区・必須固定元・公式詳細・decision・非退行・更新履歴・Strict CIをすべて充足する必要がある。
- 機械取得で問題ない一次情報サイトを優先し、セキュリティチャレンジの回避や無許可クロールは行わない。

### 再検索検証

開発ブランチ限定の1回限りのActionで `--as-of 2026-10-19` を指定し、2026-10-19〜2026-11-29の6週間と11/3・11/23の平日祝日を再検索する。公式候補の取得・収集証拠/未完了をArtifactに残す。開発検証用Actionはmainにマージせず削除する。


## 2026-10-20：ためまっぷCloudflare403を今週だけ既知障害として扱う（ユーザー承認）

ユーザー指示：『ためまっぷの不具合はいったん不具合扱いとしつつ、この状態で先に進めてください』。

- 現在のTamemap必須参照元は**残す**。初回HTTP403（`server: cloudflare`, `Just a moment...`）は取得失敗そのものとして生のURL・UTC/JST日時・ステータスとともに記録する。
- 今回の1回分だけ main側の `policy/temporary_source_exceptions.json` に承認を置き、`2026-10-19`基準の6週間探索だけで、当該URLで発生した実際のCloudflare403を `deferred`（対応待ち既知障害）として扱う。
- 例外の判定に必要なもの：HTTP 403、Cloudflareのserverヘッダー、チャレンジHTML、登録済みの `/1311401/calendar/` URL、正しい実行日と対象週、例外ID。これらを満たさない取得失敗は通常のblocker。
- 正式プロンプトv1.15や元の`discovery_sources.json`の `required=true/enabled=true` は変更しない。成功、確認済、候補0件を捏造しない。
- 補完している中野区公式イベント/子育てカレンダー・社協は、あくまで**追加探索**。Tamemap全件取得の代替や同等網羅性の保証ではない。
- その他の23区の検索・全required URL・練馬区年度表の行とdecision照合・イベント公式詳細・サムネ・重複・祝日・前回IDの保護・更新履歴・Strict CIは一切免除しない。
- Web検索RSSがクエリを無視して辞典/WhatsApp等を返すことが判明した。候補には入れず、`search_results_rejected_irrelevant` として記録する。HTTP200を関連イベント発見の成功だと断定しない。
- 今回の例外を翌回以降に自動適用してはいけない。新しい実行日では再診断、または正式なデータ連携手段を追加する。
- 本番データに反映できるのは、他のすべての検証が完了し、既存の正式なデータ専用GitHub Actionsが合格した場合のみ。`production`アプリコード・Versionは触らない。


## 2026-11-14: 総合評価の個別レビューを公開前に必須化

星は総合A/B/Cを3/2/1に変換する。8軸の平均やAの個数で算出しない。総合Bを初期値として一括代入せず、各企画の実際の活動と対象に基づく強み・留保点・その総合評価を選んだ比較理由を記録する。

新規・変更した family_fit には review（method=individual_evidence_review、8軸確認、確認日、strengths、limitations、grade_comparison、audience_basis、公式/主催者本文の引用・取得日時・SHA256）を付ける。家族向けの明確な強みがあれば、一部Bやunknownがあっても総合Aは可能。鑑賞型・通常の予約制・年齢条件だけで総合Bへ抑えない。

「どなたでも」「中学生以上」「子ども同伴可」「出演者が小学生」は、子ども向け企画の根拠とは区別する。子どもが静かに待つ親の講座を、子ども自身の体験として加点しない。対象や費用等が未記載なら、不明な軸に都合のよい評価を付けない。

全てのdata-only昇格で validate_family_fit_quality.py --base-ref <直前の本番データSHA> を実行する。未変更の過去評価は保持し、新規・変更された評価だけを検査する。同じID・同じ評価の翌週継続掲載は新規評価扱いにしない。根拠文だけが共通の一括評価、個票とdecisionの食い違い、子ども同伴と主対象の混同は公開を止める。機械チェックは引用と評価の形式・整合を検査するもので、個別の内容判断を代行しない。
