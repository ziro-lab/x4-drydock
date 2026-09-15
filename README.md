# x4-drydock

X4: Foundations 向けのオリジナル艦船を、Blender と自動化スクリプトを使って制作・検証するための実験用リポジトリです。

現時点では完成した一般向けツールではなく、艦船モデル、Blender スクリプト、検証処理、GitHub Actions などを試すための作業場として使います。

## Ship-building docs

- [`docs/playbook/X4_SHIP_WORKFLOW.md`](docs/playbook/X4_SHIP_WORKFLOW.md) — BlockoutからLayout Freeze、Detail Modeling、X4 Asset Finishing、Export/XUConverterまでの制作フロー
- [`docs/playbook/X4_PLACEMENT_CHECKLIST.md`](docs/playbook/X4_PLACEMENT_CHECKLIST.md) — Connection / Clearance / Dock / Storage / Service / Launch Tubeを含む配置Gate
- [`docs/reference/PLACEMENT_PATTERNS.md`](docs/reference/PLACEMENT_PATTERNS.md) — バニラ艦・動作済みMOD艦から抽出した配置パターン
- [`docs/reference/CONNECTION_VISUALIZATION.md`](docs/reference/CONNECTION_VISUALIZATION.md) — Egosoft ToolsのConnection VisualizationをClearance Authorityとして扱うための参照

これらは2026-09-12に `X4-MOD-Builder` で作成した3D艦制作・配置監査資料を、艦制作側の作業場で再利用するためにコピーしたものです。

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
