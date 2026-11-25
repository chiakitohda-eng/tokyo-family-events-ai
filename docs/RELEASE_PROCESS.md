# RELEASE PROCESS

このリポジトリは、**アプリ改修**と**定例データ更新**を別経路で公開する。

## 1. ブランチの役割

### アプリ／UI

- `main`: ステージング・開発。通常の改修はここで何回でも行う。
- `production`: ユーザー向け本番で使うアプリ／UIの正本。
- `release/*`: 実際に本番公開成功したアプリ版の不変スナップショット。
- `.github/production-releases.json`: 公開済みアプリ版の台帳。

### 定例イベントデータ

- `data-staging`: 休日明け自動更新が作るデータ候補。ユーザー公開には直接使わない。
- `data-production`: ユーザー向け本番で使うイベントデータの正本。
- `data-release/*`: 本番データ公開成功時だけ作る不変スナップショット。

現在の初期データ断面:

- `data-release/2026-10-08-baseline`

## 2. 公開URL

- 本番: `https://toodataa-ai.github.io/tokyo-family-events-ai/`
- ステージング: `https://toodataa-ai.github.io/tokyo-family-events-ai/staging/`

ステージングには CI が `noindex,nofollow` と視覚マーカーをデプロイ時だけ付与する。マーカーは production ソースには保存しない。

## 3. アプリ改修の流れ

1. HTML/CSS/JS、検索ロジック、収集ルール、プロンプト仕様、データスキーマ等の改修は `main` だけに入れる。
2. CI で検証し、`/staging/` で確認する。
3. 必要なら `main` 上で何回でも改修する。
4. ユーザーの明示承認後だけ `production` を承認済みコミットへ進める。
5. main の Pages ゲートから本番デプロイし、成功確認後だけ `release/*` と公開版台帳へ登録する。

ステージング途中コミットはアプリのロールバック候補にはしない。

## 4. 休日明けの定例データ更新

定例データ更新はアプリ改修と異なり、**検証合格後に自動で本番へ反映する**。

1. 自動タスクは、公開済み `production` の `site/data/latest_prompt.json` を正本として読む。
2. 現在の `data-production` SHA を取得する。
3. `data-staging` をその SHA へ同期して、前回の失敗候補を持ち越さない。
4. `data-staging` 上でイベントデータだけを更新する。
5. 更新可能範囲は以下に限定する。
   - `site/data/YYYY-MM-DD*.json`
   - `site/data/manifest.json`
   - `site/data/update_history.json`
6. HTML/CSS/JS、tools、prompts、latest_prompt、prompt_history、discovery_sources、評価ルーブリック等は定例データ更新では変更しない。変更が必要なら「改修」として main → staging の承認経路へ回す。
7. 全データ書き込み後の `data-staging` SHA と、開始時の `data-production` SHA を `main/.github/data-deploy-trigger.txt` に記録する。
8. main の唯一の Pages ワークフローが、公開済み production の検証ロジックでデータ候補を再検証する。
9. 合格時だけ `data-production` を候補 SHA へ進め、本番を **production のアプリ + data-production のデータ** で再構成して公開する。
10. Pages 成功時だけ `data-release/YYYY-MM-DD-rN` を作成する。
11. デプロイに失敗した場合は `data-production` を直前 SHA に戻し、既存公開データを維持する。

これにより、ステージングで未承認の UI/コードが存在していても、定例データだけは独立して安全に本番更新できる。

## 5. 本番の合成ルール

本番 Pages は次の2系統を合成する。

- アプリ／UI: `production/site`
- 動的イベントデータ: `data-production/site/data` のうち日付別JSON、`manifest.json`、`update_history.json`

静的な収集ポリシーやプロンプト設定は production 側を使用する。

ステージング `/staging/` は **`main/site` + `data-staging/site/data` の動的データ候補**を使用する。これは更新候補の実表示と更新履歴を本番公開前に確認できるようにするためである。一方、公開ルート `/` は常に **`production/site` + `data-production/site/data`** を維持し、ステージング候補を本番へ混ぜない。

- Pagesプレビューの合成前に `data-production` と `data-staging` のコミットSHAとリモートHEADを固定確認し、ステージング候補の全Strict監査・非退行・既存レコード保護・更新履歴整合を再検証する。監査NG時は当該プレビュー配信を止め、正常表示を偽装しない。
- ステージング画面右下の帯は `STAGING <アプリSHA> / DATA <候補データSHA>` とし、どの候補が表示されているか識別する。
- 本番 `data-production` の更新は定例データ更新専用の `main/.github/data-deploy-trigger.txt` による別ゲートだけで実行する。プレビュー配信が `data-production` や `production` ブランチを更新してはいけない。
- ステージング側の169件等は更新候補の集計であり、6週間ローリングの開始日が変わるため、旧本番の264件との差をそのまま削除件数と呼ばない。

## 6. アプリのロールバック

1. `.github/production-releases.json` から公開実績のある `release/*` を選ぶ。
2. 台帳 SHA と release ブランチ SHA の一致を確認する。
3. `production` をその公開断面へ force-with-lease で戻す。
4. `.github/release-trigger.txt` を更新して main の Pages ゲートを実行する。
5. 本番成功を確認する。
6. `main` は変更しないため、新しい改修版は引き続き staging で診断できる。

任意の main コミットへ直接ロールバックしてはいけない。

## 7. データのロールバック

1. 正常公開済みの `data-release/*` から戻したいデータ断面を選ぶ。
2. `data-production` をその snapshot SHA へ force-with-lease で戻す。
3. main のデータデプロイトリガーを更新する。
4. production アプリ + 復元した data-production データで Pages を再公開する。
5. `main` と `production` のアプリ版は変更しない。

つまり、アプリの Version 1.xx を戻さずに「データだけ前回公開分へ戻す」ことができる。

## 8. 安全ルール

- production を通常改修の作業場所にしない。
- data-production を直接編集しない。
- 定例データ更新は必ず data-staging から始める。
- `release/*` と `data-release/*` は公開成功後にだけ作り、後から書き換えない。
- データ更新がコード／ルール／スキーマ変更を必要としたら自動公開せず、改修扱いに切り替える。
- GitHub Pages の実デプロイは main のワークフローだけを使う。
- アプリ版番号とデータ更新履歴は別管理する。

## 9. 既存イベントの消失防止（2026-10-16追加）

**削除・非表示はデフォルト拒否**。新規イベントの追加、確証ある情報の訂正は可能だが、既存の公開イベントが同じ開催週から消える変更は、ユーザーによる個別の明示承認が必要。

- 以前の `data-production` SHAをベースラインとして固定し、`tools/validate_protected_events.py` で過去公開済みの各開催週・イベントIDと今回候補を1件ずつ照合する。件数合計だけの照合は不可。
- データ更新候補の決定台帳に `excluded` や `duplicate` と書いただけでは**削除の承認にならない**。明示承認が記録されていない削除はCIで失敗させる。
- 承認情報はアプリ側ポリシー `policy/approved_event_removals.json` に `week_start`、`event_id`、`approval_reference`、`official_evidence_url`、`status=approved` の組で登録する。**データ更新ブランチ自身で承認台帳を変更してはならない**。
- 6週間から外れた古い開催週のJSONファイルは削除せず、履歴として保持する。古い週が検索画面に表示されなくなることと、過去データを物理削除することは分けて扱う。
- `update_history.json` の旧エントリは追記のみ。登録済み探索元のID・URLも黙って削除・変更しない。
- 情報の訂正（開催日、場所、料金等）は従来の `field_changes` に公式根拠を明記し、既存IDと根拠を保持する。イベント自体の消去・掲載除外への変更には必ず事前承認が必要。
- 本番反映時には必ず `data-staging` と `data-production` を比較し、旧レコードの欠落・無承認の編集・旧履歴削除がゼロであることを示す。失敗時には本番公開しない。

今回の2件（KOMAFES2026・第55回板橋区民まつり）と公式観光協会・区公式祭りページは、次回の**実測を伴う**全23区の再探索で必須照合対象とする。検索履歴の「3件探索済み」等の固定値を再利用しない。未検査を `checked` として公開することは禁止する。

## 10. mainとproductionの意図した差分の統制（2026-10-17 v1.10以降）

チャットの記憶やコミット比較で「本番との差がある／ない」を推定しない。リポジトリ内の恒久規則 AGENTS.md、.github/skills/staging-production-diff/SKILL.md、docs/ENVIRONMENT_DIFF_POLICY.md と JSON台帳 .github/staging-production-diff-baseline.json を正本として使用する。

- 現在の正しい差分は、リリースv1.10本番アプリに対し、公開トリガー・台帳、main専用監査Actions、開発ツール・検証テスト・調査証跡のみ。各ファイルを理由付きで列挙したJSONを参照する。
- 本番アプリと同じ内容のコミットでも履歴は異なり得るため、`git diff` のコミット数ではなく `git ls-tree` の追跡blob SHAで比較する。
- 正式な監査は `python3 tools/audit_environment_diff.py --fetch --strict`。開発中のステージングCIでは非strictのレポートモードを使い、未承認の新機能を検出しつつステージング作業は継続可能とする。
- この台帳で意図したステージング差分と判定できるのは記録済みの正確なパス/差異種別だけ。新しい未分類差分は `unclassified`、既存例外が解消したら `resolved_allowlist` として見直す。ファイル/ディレクトリの一括ワイルドカード許可を禁止する。
- ユーザーによる明示承認がある本番公開は、**現在のproductionから派生した隔離候補ブランチ**へ承認差分だけを移植して行う。mainブランチ全体を無差別マージしない。
- 本番アプリreleaseの成功後は、公開SHAをJSON台帳に反映し、現在のmainとproductionの実際の差分をすべて再監査する。未承認差分と古い例外が混在するまま「同期済み」と言わない。
- data-productionの動的レコードは本監査と別に、各週ID・内容・履歴の無承認削除を必ずチェックする。site/が同一でもデータ同一性は保証しない。

リリースv1.10監査ではsite/とprompts/は同一で、mainだけに残すべき差分26件を確認した。新しい統制ファイル追加後は33件となる想定だが、以後は最新実値を使う。

## 手動変更の確認運用（2026-11-15 ユーザー指定）

最新のユーザー指定は「データは直接本番更新して良いです。改修はステージング経由」。公式根拠で確認したイベント追加・日時/料金/個別評価の訂正は、既存個票・履歴・取得失敗の保護とデータ専用ゲートの検証後、追加の確認を求めずdata-productionへ反映してよい。従来のステージング確認待ちはイベントデータについて解除する。UI、コード、収集先設定、評価ルール/スキーマの改修はmain→ステージングで実表示を提示し、利用者の確認・明示承認後にだけproductionへ反映する。データ更新に未承認の改修を混ぜない。削除には従来どおり個別の明示承認が必要。2026-11-15の一つ前の「すべて確認後に反映」という指定より、この最新の切り分けを優先する。
