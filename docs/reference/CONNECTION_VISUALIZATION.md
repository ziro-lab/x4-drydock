# Egosoft Connection Visualization Reference v0.4

## Purpose

X4艦の設計で必要なのは、装備モデルの精密Bounding Boxを毎回調べることではなく、**船体側が予約すべき配置空間を把握すること**。

Egosoft Blender Mod ToolsはConnection tagに応じてViewportへbox / cylinder等のVisualizationを描画する。このVisualizationをX4艦設計のClearance Authorityとして優先する。

## Authority rule

**実際に使う現行ツールの `Blender_Properties.xml` をAuthorityにする。** この文書の数値は調査時点のsnapshotであり、validatorへ固定値として埋め込むための仕様ではない。

## Reader availability — corrected 2026-09-24

以前のこの文書には `tools/connection_visualization.py` を「Implemented reader」として呼び出す説明がありましたが、x4-drydockのファイル一覧には実装がありません。関連parser testsの存在もこのrepoでは確認できません。コピー元の説明を、このrepoの実装証拠として扱ってはいけません。

DX500 pilotは独自の設計用AABB予約を使います。`tools/dx500_pipeline.py` の検査は **Blenderモデルと仮予約との明白な干渉を確認するだけ** で、公式Visualizationの代用品ではありません。

今回、現行ツールのデータなしでparserを推測実装することはしません。手元で公式ツールが使える場合は、まずそのVisualizationで確認してください。自動readerが必要になったら、以下を実装・検証する候補にします。

### Proposed reader behavior

1. queryのtag集合にruleのrequired tagsが全て含まれるruleを候補とする。
2. required tag数が最大のruleを最も具体的な候補とする。ただし実ツールの解決挙動と照合する。
3. 同specificityのruleが複数なら、未確認の順序を推測せず `AMBIGUOUS` とする。
4. primitive/dimensionを正規化できないときはraw属性を保持し、黙ってsnapshotへfallbackしない。
5. 入力XMLのSHA-256、Blender版、Egosoft Tools版、検証時刻を記録する。

synthetic fixtureのテストと、実際の配布XMLへの適用確認は別のAcceptance。将来parserのテストが通っても、公式ツールでの描画・解決規則の一致は別途検証する。

## Snapshot observed during research

Research date: 2026-09-12. 以下は引き継いだ調査メモであり、今回のpilotでは実ツールへ再照合していません。

| Equipment | Standard snapshot | Advanced/Boron snapshot |
| --- | --- | --- |
| L Engine | cylinder 50 x 50 x 50 m | cylinder 25 x 25 x 25 m |
| XL Engine | cylinder 150 x 150 x 150 m | cylinder 75 x 75 x 75 m |
| L Shield | box 32 x 64 x 16 m | box 16 x 32 x 8 m |
| XL Shield | box 96 x 192 x 48 m | box 48 x 96 x 24 m |
| L Turret | box 64 x 64 x 64 m | box 32 x 32 x 32 m |

Dock/exclusion snapshots:

```text
ship_s exclusion zone: 70 x 400 x 70 m
ship_m exclusion zone: 180 x 500 x 180 m
```

向き、原点、primitiveの解釈を含め、active tool dataから読み直すこと。値だけを新しい船体へ貼り付けない。

## Design interpretation

Visualization should answer whether equipment can fit and whether the ship's reserved approach/departure space is obstructed. It is not intended to reproduce every visual protrusion of the final equipment model.

Visualizationだけでは次を証明できません。

- component Connectionとship macroのbinding
- binding先macroのattachment connection
- Connection名/IDの維持
- custom turretのIK・articulation・muzzle/firing
- Dock・animationの実挙動
- save互換とX4 runtime解釈

```text
Current Visualization check
→ Binding / Identity validation
→ Fresh Export / Package validation
→ X4 Runtime Corroboration
```

## Future Workbench integration

必要になったときにactive XMLの探索、reader、tag解決、予約空間、船体との検査、証拠出力を統合する。汎用3D CoreへX4固有tag名を持ち込まない。

古いsnapshotを、現行ツールの値より優先してはいけません。
