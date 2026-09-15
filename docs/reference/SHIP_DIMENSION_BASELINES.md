# X4 Ship Dimension Baselines v0.1

## Purpose

オリジナル艦のBlockout時に、X4の既存艦から大きく外れたスケールへ無自覚に進まないための寸法リファレンス。

この資料は **ship classを決める仕様書ではない**。S / M / L / XLの実際のclass、dock、equipment、connection互換はCurrent X4 dataをAuthorityとする。

寸法は主に次の用途で使う。

- 初期Blockoutの全長・全幅・全高の妥当性確認
- 同class内での「小型寄り / 標準寄り / 巨大寄り」の判断
- Dock / Engine / Turret等を配置する前のvolume予算
- 完成後に「性能はLなのに見た目だけXL級」などの不自然なscale driftを検出

---

## Measurement sources

### Community full-length measurement — X4 5.00

2022年の `Unofficial Ship Length List` は、5.00時点の艦船モデルをBlenderへ読み込み、bow-to-sternの水平全長を計測したもの。

Source:
- https://www.reddit.com/r/X4Foundations/comments/thpc1v/unofficial_ship_length_list/
- https://docs.google.com/spreadsheets/d/1487ACI3f-Y5iHBG9dSBfNHA3sbS_zjm0ahgdnEPpQ0A/edit

測定者の説明では:

- raw hullを測定
- weapon / engineは原則として全長へ含めない
- hull付属のantenna等は含める
- Sentinel / Vanguard等、同一model variantも表に残す
- 当時のimport workflowではBlender Measure値とゲーム内実測のscale差を校正し、全艦を同条件で測定

したがって、**5.00の相対scale分布を知る資料として強い**。

ただしCurrent Egosoft Blender Mod Toolsのauthoring guideでは1 Blender meter = 1 X4 meterとして扱うため、2022年当時のimport scale係数をCurrent pipelineへ固定しない。現行tool/importerごとにscaleをprobeする。

### 2025 combat-ship measurement

2025年には別のコミュニティ計測で、全combat shipをBlenderへ読み込み、Length / Width / Heightを取り、S/MについてTop / Side / Frontの投影面積までraycastで算出した報告がある。

Source:
- https://www.reddit.com/r/X4Foundations/comments/1j969sl/

公開Excelの一時配布先は恒久保存ではないため、本repoでは値そのものをAuthorityとして固定しない。ただし **3軸寸法＋投影面積を自動取得する方向性の先行例**として採用する。

### 2025 visual scale comparison

2025年のdestroyer / battleship比較では、各modelをBlenderのorthographic viewへ同scaleで並べ、100m gridで比較している。Xenon Iは約5.1kmと報告され、5.00の実測list（5,178m）とも概ね整合する。

Source:
- https://www.reddit.com/r/X4Foundations/comments/1j5vezz/

---

# 5.00 measured length baseline

以下は5.00実測sheetをclassごとに集計したもの。

`Central 80%` は表に残っているvariant行をそのまま使った10th–90th percentileであり、厳密な「unique hull distribution」ではない。**設計時の目安**として使う。

| Size | Observed Min | Median | Central 80% | Observed Max | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| S | 15.1 m | 30.8 m | 21.6–34.2 m | 52.8 m | Nova → Shih |
| M | 54.5 m | 137.0 m | 114.4–147.0 m | 149.5 m | Hive/Queen's Guard → Astrid。Manticoreは57.4m |
| L | 464.3 m | 610.6 m | 504.6–918.9 m | 1,485 m | Heron → Teuta |
| XL | 1,607 m | 1,822 m* | 1,642.5–2,982.4 m* | 5,178 m | Condor → Xenon I。極端なNPC/plot艦を含む |

`*` XLの統計はXenon IやUnknown Ship等の極端な値に影響される。

通常のplayer-facing 5.00 XLだけを見ると、Raptorが3,191m。`Unknown Ship`（Deca CPU）は3,849m、Xenon Iは5,178mで、明確なoutlierとして別扱いした方がよい。

極端なNPC/plot艦を除いたXLの参考帯は:

```text
Observed: 1607–3191 m
Median:   1775 m
P10–P90:  1637.5–2459 m
```

---

## Important class gaps

5.00実測ではclass間にかなり大きなphysical gapがある。

```text
S max    52.8 m
M min    54.5 m
M max   149.5 m
L min   464.3 m
L max  1485.0 m
XL min 1607.0 m
```

特に **M → L** は約3倍の空白があり、L艦を200〜300m程度で作ると、既存X4艦のscale感からかなり外れる可能性が高い。

一方、L上限とXL下限は近く、Sonra / Teuta等の巨大L艦はsmall XLに近い見た目になり得る。2025年のlarge transport比較でもIncarcatura / Shuyaku / Sonra等の巨大さが指摘されている。

---

# Provisional design bands

Current 9.xの全艦3軸再計測が完了するまでの **Blockout用soft guardrail**。

Hard limitではない。

## S

```text
Typical target: 20–40 m length
Observed 5.00:  15.1–52.8 m
```

50m級はかなり大柄なSとして扱う。

## M

```text
Typical target: 110–150 m length
Observed 5.00:   54.5–149.5 m
```

60〜100m級はcompact M。通常のtransport / frigate / corvetteは100m超が多い。

## L

```text
Typical target: 500–1000 m length
Observed 5.00:  464.3–1485 m
```

1km超は大型L。1.3〜1.5km級はXL境界に近い特殊な巨大Lとして扱う。

## XL

```text
Typical target: 1600–2500 m length
Large XL:       2500–3500 m
Extreme:        >3500 m
```

5.00ではRaptor 3,191m、Xenon I 5,178m。
Kingdom End後のcommunity in-game spot measurementではSharkが約3.3kmと報告されており、5.00以降もplayer-facing XLの上側は伸びている可能性がある。

---

# Historical pre-release size envelope

X-CON時代の回答としてcommunity archiveに残っている古い目安:

| Size | Width | Height | Length |
| --- | ---: | ---: | ---: |
| XS | 2.5 m | 2.5 m | 2.5 m |
| S | 35 m | 25 m | 35 m |
| M | 90 m | 90 m | 150 m |
| L | 600 m | 600 m | 600 m |
| XL | 2000 m | 2000 m | 2000 m |

Dock envelopeの同資料:

```text
S dock:  40 x 30 x 45 m
M dock: 185 x 115 x 115 m
```

Source:
- https://apocalypse.moy.su/forum/305-1235-2

これは**Current hard limitではない**。
実際の製品版にはShih 52.8m、Teuta 1485m、Raptor 3191m、Xenon I 5178mなど、この古いnominal maximumを超える艦が存在する。

使い方は「初期の設計思想を知る参考」に限定する。

---

# Length alone is not enough

最終的には次を1レコードとして保持したい。

```text
Ship / component ID
Game build
DLC/source
Ship class: S/M/L/XL
Role
Length
Width
Height
Bounding volume
Top projected area
Side projected area
Front projected area
Hull-only / equipment-included measurement policy
Measurement tool / pipeline version
```

理由:

- 同じ150mでも細長いDragonと幅広いfrigateでは体感scaleが違う
- Dock、turret、engine clearanceは幅・高さに強く依存
- combatでは投影面積も視覚・命中性へ影響
- carrier / builderは長さより横幅・高さがdesign volumeを支配する場合がある

---

# Current 9.x refresh plan

5.00 spreadsheetを永続Authorityにせず、**所有しているCurrent X4 game dataからnumeric datasetを再生成する**。

Egosoft assetsそのものはpublic repoへ置かない。

推奨pipeline:

```text
Private current X4 data
    ↓
ship component / macro enumeration
    ↓
ship_s / ship_m / ship_l / ship_xl classification
    ↓
Current mesh import into Blender
    ↓
scale calibration probe
    ↓
world-space hull bounding box
    ↓
Length / Width / Height
    ↓
optional orthographic projected area
    ↓
numeric CSV / JSON only
    ↓
public x4-drydock reference
```

## Measurement policy

Current datasetでは最低限次を固定する。

1. hull-onlyを基本値にする。
2. detachable weapon / engine / turretは基本寸法から除外。
3. permanent antenna / superstructureは含める。
4. exceptional fixed main weaponで全長が大きく変わる場合は`hull_length`と`equipped_length`を分離。
5. Sentinel / Vanguard等でgeometryが同一なら`geometry_family`を記録して統計重複を制御できるようにする。
6. plot-only / NPC-only / boss shipをflagし、通常設計帯の統計から任意に除外できるようにする。
7. Current X4 build、Blender version、importer/tool versionを必ず記録。
8. Current importerのscaleを既知sampleまたはgame-space referenceでprobeし、古いworkflowのscale係数を再利用しない。

## Statistics to publish

各classについて:

```text
absolute min / max
player-usable min / max
median
P10 / P90
role別 median/range
extreme outliers
```

これなら「最大と最小」だけに引っ張られず、Blockout時に自然なscaleを選べる。

---

# Blockout usage

Phase 0 / 2で次を記録する。

```text
Target class: L
Target role: Destroyer
Target L/W/H: 800 / 260 / 180 m
Class length band: 464–1485 m (5.00 reference)
Central reference: ~505–919 m
Scale verdict: NORMAL
```

判定例:

```text
NORMAL  : central band付近
EDGE    : observed range内だが端に近い
OUTLIER : observed range外。意図と理由を記録
```

`OUTLIER` は禁止ではない。意図せずclass scaleを外れることを防ぐためのflagとして使う。

---

# Status

- 5.00 full length baseline: AVAILABLE
- 2025 multi-axis measurement precedent: CONFIRMED
- Current 9.x full Length/Width/Height dataset: TODO — regenerate from privately held current game data
- Current 9.x role/class percentiles: TODO after full dataset generation
