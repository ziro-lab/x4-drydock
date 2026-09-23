# DX-500 Pilot Blockout

`x4-drydock` の制作フローを、実際の1隻で最後まで通すための試験艦です。

参照イメージは「長期活動できるモジュール式の深宇宙探査船」という方向だけ使い、形状・モジュール数・エンジン数を正確に再現することは目的にしません。今回はX4向けの機能配置へ進みやすいことを優先して、**四角い機能ブロックを直列につないだ構成**へ単純化します。

## Phase 0 — Ship Intent

```text
Size: L
Role: Long-range exploration / support
Target hull L/W/H: 500 / 320 / 180 m
Scale reference: L lower edge
Scale verdict: EDGE
Engine: L Standard x4 (2x2 stern cluster)
Fixed Weapon: Blockoutでは未予約
Turret: Blockout Review後に決定
Dock: top-side S dock x1 placeholder
Ship Storage: S / XS intended
Repair/Rearm: No
Launch Tube: No
Equipment standard: Standard first
```

500 mはrepoの5.00実測L帯 `464.3–1485 m` の下側で、Central 80% `504.6–918.9 m` のすぐ外です。したがって今回は`EDGE`として扱い、意図せずM級へ小型化しないことだけ監視します。

## Blockout direction

船体は8個の箱型モジュールで構成します。

| ID | 用途 | 概要 |
| --- | --- | --- |
| M01 | Sensor / forward access | 艦首側の小型センサー・アクセス部 |
| M02 | Command | 操艦・航法 |
| M03 | Habitation | 長期航行用の居住区 |
| M04 | Life support | 生命維持・備蓄 |
| M05 | Cargo | 大容量貨物 |
| M06 | Workshop / hangar | 工作・整備・格納用の余裕 |
| M07 | Power | 電力管理 |
| M08 | Propulsion support | 艦尾の推進補機・エンジン支持 |

各モジュールは短い四角断面のトラス4本で接続します。円筒や曲面を主役にせず、最初から「箱の集合体」に見えることを優先します。

### Engine choice

初回はLエンジン4基を上下左右2x2で対称配置します。

理由は単純で、Connection、clearance、左右上下の対称性を検証しやすく、1/3/5基のような中央エンジン処理も不要だからです。Blockout Reviewで外観が重すぎる場合は2基へ減らせます。

### Dock choice

M05/M06付近の上面にS dock用の平面を1か所だけ置きます。

現時点のapproach volumeは**デザイン上の仮予約**です。Egosoftの正式なclearance値ではありません。Layout Freeze前に現行`Blender_Properties.xml`由来のConnection Visualizationへ置き換えます。

## Intentionally deferred

今回のBlockoutでは以下を作り込みません。

- ソーラーパネル / ラジエータ翼
- アンテナ群
- 装甲板とパネル分割
- greeble
- final engine geometry
- final dock / hatch geometry
- turret配置
- material / UV / collision / LOD / wreck
- X4 component / macro binding

特に参照イメージの大きなパネル翼は、シルエットを強く決める割にX4機能配置の検証には不要なので、Review 1までは外します。

## Build / validation

通常Pythonでspecだけ検査できます。

```bash
python tools/build_modular_blockout.py \
  ships/dx500_pilot/blockout_spec.json \
  --validate-only
```

Blenderでblockout sceneを生成する場合:

```bash
blender --background \
  --python tools/build_modular_blockout.py -- \
  ships/dx500_pilot/blockout_spec.json \
  --output build/dx500_pilot_blockout.blend
```

生成sceneには次のCollectionを作ります。

```text
DX500_PILOT/
  HULL_BLOCKOUT
  STRUCTURE
  EQUIPMENT_PLACEHOLDER
  RESERVED_DEBUG
  DIAGNOSTIC_CAMERAS
```

`RESERVED_DEBUG`は確認用で、最終船体geometryではありません。

## Review 1 — Blockoutで見るもの

この段階で決めたいのは4点だけです。

1. 500 m級L艦としての全体比率
2. 箱型モジュールの大小リズム
3. 艦尾4発エンジンの見え方
4. 上面S dockをこの位置に残すか

ここが通ったら`BLOCKOUT_BASELINE`とし、その次にX4 Connection / current clearanceを入れてFunctional Skeletonへ進みます。
