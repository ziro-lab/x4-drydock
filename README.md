# x4-drydock

X4: Foundations 向けのオリジナル艦船を、Blender と自動化スクリプトを使って制作・検証するための実験用リポジトリです。

現時点では完成した一般向けツールではなく、艦船モデル、Blender スクリプト、検証処理、GitHub Actions などを試すための作業場として使います。

## Current production boundary

当面、このrepoの主目標は **X4で使うことを考慮した艦船モデルをBlender上で仕上げ、手元のEgosoft Mod Tools工程へ渡せる状態にすること** です。

repo / GitHub Actions側で担当する範囲:

- Blockout / silhouette / scale
- X4 equipment・dock・hangar等のreserved volumeを考慮した配置設計
- detailed modeling
- UV / normals / material slot等のBlender側asset preparation
- collision / LOD / wreck等、Blenderだけで準備できる範囲
- diagnostic view / dimension / overlap等の自動検査
- Mod Tools工程で必要になるConnection候補位置・向き・命名のhandoff情報

手元工程へ残す範囲:

- Egosoft Blender Mod Toolsを実際に読み込んだ最終Connection調整
- current tool dataに依存するtag / group / bindingの確定
- Egosoft exporter
- XUConverter
- extension packageへの組み込み
- 実X4でのruntime確認

手元でMod Tools工程を実行できるかは現時点で未確定です。そのため、**手元工程が未実施でもrepo側の制作を止めない**方針にします。

repo側の標準完成点は `X4_AWARE_BLENDER_HANDOFF` とし、`Game-ready` / `Runtime PASS` は手元工程を実際に通せた場合だけ別途付けます。

## Active pilot — DX-500

現在の入口は **[`ships/dx500_pilot/PIPELINE.md`](ships/dx500_pilot/PIPELINE.md)** です。成果物の使い分け、再生成、手元工程、未確認事項と工程監査をまとめています。

- [`tools/dx500_pipeline.py`](tools/dx500_pipeline.py) — +Y艦首の完成モデル、実体のある格納空間、LOD0〜3、collision/convex/wreck素材、接続候補、OBJを生成。別プロセスで再読込検査と確認画像生成。
- [`tools/run_dx500.py`](tools/run_dx500.py) — 新規出力フォルダで各工程を時間制限付き実行し、手元受け渡しファイルとSHA256を作成。
- [`.github/workflows/dx500-blender.yml`](.github/workflows/dx500-blender.yml) — 公式Blender 5.2.1 LTSの取得・hash照合、テスト、生成・検査・画像、Actions Artifact。
- [`ships/dx500_pilot/blockout_spec.json`](ships/dx500_pilot/blockout_spec.json) — 初期シルエットの入力。旧−X艦首からの変換や最終配置との差分はPIPELINE.mdで明示。

Actionsの成功runから `dx500-blender-handoff-<commit>` を取得し、同梱の `START_HERE.md` を読む。確認・編集には `dx500_handoff.blend`、手元のMod Tools設定開始には `dx500_geometry_only.blend` を使う。後者にも正式なX4 tag/bindingはまだ入っていません。

旧[`Blockout README`](ships/dx500_pilot/README.md)と[`build_modular_blockout.py`](tools/build_modular_blockout.py)は初期Blockoutの記録です。完成モデルの再生成には新pipelineを使用してください。

**Blender側の仮予約レイアウト確定と、正式なX4 Functional Layout PASSは別です。** 現行Egosoft clearance未確認をPASSへ読み替えず、詳細はpilotのPIPELINE.mdを優先します。

## Ship-building docs

- [`docs/playbook/X4_SHIP_WORKFLOW.md`](docs/playbook/X4_SHIP_WORKFLOW.md) — BlockoutからLayout Freeze、Detail Modeling、X4 Asset Finishing、Export/XUConverterまでの制作フロー
- [`docs/playbook/X4_PLACEMENT_CHECKLIST.md`](docs/playbook/X4_PLACEMENT_CHECKLIST.md) — Connection / Binding / Clearance / Dock / Storage / Service / Launch Tubeを含む正式配置Gate（手元で現行ツールを使う段階）
- [`docs/playbook/X4_EXPORT_RUNTIME_CHECKLIST.md`](docs/playbook/X4_EXPORT_RUNTIME_CHECKLIST.md) — Fresh Export / XUConverter / Package / 実X4 runtime確認のGate
- [`docs/reference/SHIP_DIMENSION_BASELINES.md`](docs/reference/SHIP_DIMENSION_BASELINES.md) — S/M/L/XLの実測寸法帯とCurrent 9.x再計測方針
- [`docs/reference/PLACEMENT_PATTERNS.md`](docs/reference/PLACEMENT_PATTERNS.md) — バニラ艦・動作済みMOD艦から抽出した配置パターン
- [`docs/reference/CONNECTION_VISUALIZATION.md`](docs/reference/CONNECTION_VISUALIZATION.md) — Egosoft ToolsのConnection VisualizationをClearance Authorityとして扱うための参照
- [`docs/reference/EXTERNAL_REPO_FINDINGS_2026-09-16.md`](docs/reference/EXTERNAL_REPO_FINDINGS_2026-09-16.md) — 公開X4 modding repoとの比較と、本repoへ取り込んだ知見

基礎4資料は2026-09-12に `X4-MOD-Builder` で作成した3D艦制作・配置監査資料を再利用し、公開されている他のX4 modding実装や実測資料から確認できたfailure mode / scale referenceを追加しています。

## 方針

- 艦船本体、テクスチャ、画像などのオリジナル制作物と、制作・検証用コードの権利を分けて管理します。
- Egosoft のゲーム本体から抽出したアセット、公式 Mod Tools、`XUConverter.exe` などのプロプライエタリな配布物は、このリポジトリには含めません。
- 必要な公式ツールは正規の配布元から取得し、ローカルまたは非公開の実行環境で管理します。
- 第三者のコードや素材を導入する場合は、その配布条件と著作権表示を維持します。

## License

| 対象 | 扱い |
| --- | --- |
| 自作ソースコード / Blender スクリプト | `GPL-3.0-or-later`（個別ファイルに別記がある場合を除く） |
| 自作 3D モデル / テクスチャ / 画像 / その他の制作アセット | All Rights Reserved（明示的に別ライセンスを付けたものを除く） |
| 第三者コンポーネント | 各コンポーネント固有のライセンス |
| Egosoft のゲームアセット・公式ツール | このリポジトリでは再配布しない |

詳細は [`LICENSE`](LICENSE)、[`ASSET_LICENSE.md`](ASSET_LICENSE.md)、[`THIRD_PARTY.md`](THIRD_PARTY.md) を参照してください。

## Egosoft / X4: Foundations

This is an unofficial fan project. It is not affiliated with, endorsed, or supported by Egosoft.

利用は自己責任です。このプロジェクトについて Egosoft からの技術サポートは提供されません。X4: Foundations および関連する名称・商標・公式コンテンツの権利は、Egosoft または各権利者に帰属します。

このプロジェクトは非商用のファンプロジェクトとして運用し、Egosoft の Fan Content Policy に従います。

- Fan Content Policy: https://www.egosoft.com/community/fanpolicy_en.php
- X4: Foundations: https://www.egosoft.com/games/x4/info_en.php

## Repository safety

`.gitignore` では、公式 Mod Tools、XUConverter、ゲームデータの抽出物、ビルド中間物などを誤ってコミットしにくいよう除外しています。

公開してよいか不明なファイルは、確認が済むまでこのリポジトリへ追加しません。
