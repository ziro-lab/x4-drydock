# DX-500 — Blender handoff / local MOD pipeline

This is the active pilot contract. The earlier blockout README/spec is the historical silhouette input, not the final equipment layout. No generated file in this packet is an installable X4 extension.

## 今回の完成点

`X4_AWARE_BLENDER_HANDOFF`: 箱型モジュール艦を実Blenderで生成し、別プロセスで再読込・検査し、手元のMod Tools工程へ渡す。造形承認待ちで止めず、工程検証向けの簡素な形を採用する。標準装備・既存ドックの利用を前提に、独自タレット機構・独自ドックアニメーション・内装制作・修理補給・発艦チューブは今回作らない。

**Blender側のレイアウト確定は仮予約の確定。正式なX4 Functional Layout PASSではない。** 旧placement checklistのConnection/binding PASSは手元工程で使う。現行ツールがない状態でPASSへ読み替えないが、Blenderの制作は続行する。

## ファイルの使い分け

| ファイル | 用途 |
| --- | --- |
| `dx500_handoff.blend` | 通常の確認・修正用。LOD0、編集可能な部品、仮装備、予約空間、候補Emptyを収録 |
| `dx500_geometry_only.blend` | Mod Toolsへ持ち込む出発点。仮装備・ドック仮床・予約空間・カメラ・候補Emptyを除外済み。未タグ付けの素のモデル |
| `dx500_LOD0.obj`〜`dx500_LOD3.obj` | Blender版の互換問題が出た場合のgeometry/UV/normal退避経路。メートル、+Y艦首、+Z上を保持。OBJ importerの軸設定を確認 |
| `dx500_collision.obj` / `dx500_wreck.obj` | 衝突・残骸の素材。変換済みゲームデータではない |
| `design_manifest.json` | 全部品・予約空間・候補座標・向き・仮定・入力hash |
| `connection_candidates.csv` | 接続候補の一覧。JSONにはquatも収録。local +Z=取付面法線、local +Y=艦首方向の面内射影（平行なら上方向）。exporter quaternionとは未照合 |
| `material_mapping.json` | プレビュー材質と未確定のゲーム材質対応。架空のmaterial IDを入れない |
| `blender_validation.json` / `geometry_validation.json` | 実ファイル再読込の検査結果 |
| `hero/top/side/front/rear/collision.png` | 同じモデル由来の確認画像。仮装備が写る画像はゲーム内装備表示ではない |
| `build_identity.json` / `SHA256SUMS.txt` | Blender版、source commit、run、処理時間、ファイル同一性 |

材質は自作の5色の単純なBlender材質（残骸用を別途追加）。画像テクスチャやEgosoftアセットに依存しない。UV1はタイル用で、固有の描き込みや固有ベイク用の重複なしatlasではない。`col`と無効化した`paintmodmask`を準備するが、利用するゲームshaderの追加channel要求は手元で確認する。

## 形状・配置

船体の基準は500 × 320 × 180 m。薄い表面パネルを含む実寸は検査JSONを参照。装備込みの全長とは区別する。

元の−X艦首配置を `(x,y,z) -> (y,-x,z)` で+Y艦首へ移す。M05は貨物区画を左右へ分け、中央に格納用の穴を開ける。仮の昇降床は表示専用で、船体collisionに混ぜない。

配置予定はLエンジン4基、Lシールド2基、Mタレット4基、Sドック1か所、S/XS格納。これらは**予定スロット**であり、X4のConnectionとして機能していない。group文字列も意図メモで、最終の保護関係は未確定。主砲なし。

正式clearance未取得なので、予約寸法はすべて設計用のAABB。装備の実形状・可動域・ドック進入規則を保証しない。船体との明白な衝突と格納庫の塞がりは自動検査する。

LOD0〜3は同じ部品定義からdetailを減らして作り、三角形数が厳密に減少することを検査する。衝突形状は閉じた箱群、convex sourceも独立した箱。**まだJolt用にcookした物理データではない。** 残骸は同一シルエットの簡易source。破断・爆発アニメーションは作らない。

## 再生成

Actions `DX500 Blender handoff` はpublic Ubuntu runnerでBlender 5.2.1を公式配布から取得し、公式SHA256リストと照合する。外部アドオン・ゲームデータ・認証済みEgosoftダウンロードは使わない。

ローカルでもrepoルートから実行可能。出力先は新規または空フォルダを指定する。

```powershell
python -m unittest discover -s tests -v
python tools/run_dx500.py --blender "C:\path\to\blender.exe" --output "build\dx500-run-001"
```

Linuxの表示なし環境では全体を`xvfb-run -a`で包み、`LIBGL_ALWAYS_SOFTWARE=1`を指定する。各段階は別Blenderプロセスで、600秒のtimeoutを持つ。途中失敗時は最後のlogを確認。既存の成功出力を上書き・流用しない。

## 手元工程：最短の成立確認から

1. **ツール環境だけ先に確認。** 所有するX4の版・ビルド・DLC、インストールしたEgosoft Toolsの版、対応するBlender版を記録。公式同梱sampleを開いてexport/converterまで試す。sampleでも失敗する場合はDX500の造形を疑う前に環境を直す。5.2.1で生成できたことはMod Toolsとの互換証明ではない。
2. **船体だけの取り込みを先に通す。** geometry-onlyを別名のローカル作業ファイルへコピー。必要ならOBJ退避経路を使い、軸・実寸・UV名を再確認。最初は単純な現行ゲーム材質へ対応させる。公式sampleを参考にpart/LOD/wreck/collisionとclassを設定し、現行exporterが要求する作業pathからfresh exportする。
3. **正式装備・接続を追加。** candidate一覧を手元でEmptyへ変換/配置し、現行ツールでtag・group・向き・装備空間を確定。cockpit/playercontrol/dynamicroom、操縦席視界、countermeasures等を含む。既存の適合するL艦を機能参照に使い、ゲームデータはpublic repoへコピーしない。
4. **ドック・格納を追加。** 現行の既存dock/storageを利用し、船体connectionとmacro bindingを対応させる。S/XS用の格納容量・搬入出・ドア/昇降床の動作・徒歩導線が必要かを確認。既存ドック自体に含まれる機構と、船側が追加すべき機構を区別する。仮床を残して既存dockと重ねない。
5. **ゲーム向け物理と変換。** .col素材とconvex sourceを起点に、現行ツールでJolt関連の設定/生成/変換を行う。ドック穴を一つの巨大凸包で塞がない。新規DAE/XMLと変換結果が同じsourceに対応することを確認。
6. **MOD package。** 独自prefixのcomponent/macro/ware/localisation IDを決め、`content.xml`、macros/componentsのindex、ware→macro→component、material path、DLC依存を整える。研究/購入/blueprint/試験用spawnなど**ゲーム内で入手できる経路**を最低1つ作る。今回は未確認のIDを入れた見せかけの完成XMLを配らない。
7. **実X4。** 別のテストsaveでextension認識、船体表示、移動、操縦席、装備交換、射撃、シールド、ドッキング/格納/再発艦、LOD切替、衝突、破壊/残骸、save/reloadを確認。debug logと対象buildを保存。

各段階で失敗したらその段階のファイル・log・版・症状を保存し、前段のPASSまで取り消さない。普段のsaveへいきなり導入しない。

## 工程監査：埋めるべき穴

| 問題 | 今回の対処 / 残す仕事 |
| --- | --- |
| 設計JSONの検査だけでBlender生成を証明できない | 実Blender生成→2種類のblend再読込→画像→checksumに分離 |
| 艦首軸のままexportすると向きが違う | +Y艦首へ統一。XML側の軸変換は現行exporterで確認 |
| ドック用平面だけで内部が詰まっている | M05の穴と独立collision islandを検査。正式dockサイズは未確定 |
| 仮エンジン/砲塔/床が船体に混入する | view-only collectionとgeometry-only出力のwhitelistで分離 |
| Blender材質をそのままゲーム材質と思い込む | 対応表を未確定のまま明示。初回は現行の既存材質を使う |
| collision meshがあるだけで物理完成と思い込む | .col素材と未cook凸形状を明記。Joltは別工程 |
| ローカルでファイルを開けないと全部止まる | OBJ/MTLも用意。Mod Tools sampleの小さな疎通試験を先にする |
| packageはあるが艦を出せない | ID/index/ware/localisationに加えて入手経路を必須確認へ |
| ローカル修正を再生成で消す | geometry-onlyから別名コピー。修正内容は座標/仕様差分としてrepoに戻す。手編集済みblendへ生成器を直接実行しない |
| ガイド上の完成条件が食い違う | Blender仮予約の確定と、正式X4機能配置PASSを分離。本pilotはこの文書を優先 |

## References / evidence boundary

The cited guides are authoring references, not proof that this artifact works in the current game. Accessed 2026-09-24.

- Egosoft-hosted author guide (units, axes, UV/vertex channels, LOD, wreck, collision, Jolt and exporter setup): https://wiki.egosoft.com/X4%20Foundations%20Wiki/Modding%20Support/Assets%20Modding/Community%20Guides/Making%20custom%20ships/
- Egosoft dockingbay guide (dockarea dependency, lift/door states, storage and alignment): https://wiki.egosoft.com/X4%20Foundations%20Wiki/Modding%20Support/Assets%20Modding/Guides/Dockingbay/
- Egosoft modding resources: https://wiki.egosoft.com/X4%20Foundations%20Wiki/Modding%20Support/
- Official Blender release files: https://download.blender.org/release/Blender5.2/

No reference image, third-party model, extracted game geometry, proprietary add-on or tool binary is included in the handoff. Asset rights follow the repository's ASSET_LICENSE.md. Scripts remain GPL-3.0-or-later.
