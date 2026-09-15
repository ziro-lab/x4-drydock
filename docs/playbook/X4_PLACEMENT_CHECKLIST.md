# X4 Ship Placement Checklist v0.2

このチェックリストは **Blockout → X4機能配置 → Layout Freeze** のGateとして使う。

詳細造形へ進む前にFAILを0件にする。

---

## A. Intent

- [ ] Size: S / M / L / XL
- [ ] Roleを定義
- [ ] 全長 / 全幅 / 全高の目安
- [ ] Weapon要求
- [ ] Turret要求
- [ ] Shield要求
- [ ] Dock有無
- [ ] 対応艦載機サイズ
- [ ] Ship Storage要求
- [ ] Repair / Rearm要求
- [ ] Launch Tube要求
- [ ] Standard / Advanced規格

---

## B. Blockout

- [ ] 艦首・艦尾が明確
- [ ] Main Hullの主要シルエットがある
- [ ] Bridge予定領域
- [ ] Engine予定領域
- [ ] Weapon / Turret予定領域
- [ ] Dock / Hangar予定領域
- [ ] 詳細造形をまだ固定していない

---

## C. Basic Connections

必要に応じて:

- [ ] `cockpit`
- [ ] `playercontrol`
- [ ] `aimtarget`
- [ ] `countermeasures`
- [ ] `dynamicroom`

### Connection identity / binding

Connectionを置いただけで機能成立とみなさない。

- [ ] Connection nameが艦component内で一意
- [ ] tag / size / standard・advanced等が現行データと整合
- [ ] groupを使うConnectionは、groupの意味が意図した機能と一致
- [ ] cockpit / dock / storage等、macro bindingが必要なものはship macro側にも対応bindingがある
- [ ] ship macroの`connection ref`がcomponent側の実在Connectionを指す
- [ ] binding先macroと、そのattachment connectionが実在する
- [ ] 既存saveや公開版で使ったConnection名は、理由なくrenameしない

古いMOD制作ツールにはgroupや固定武器の制約に関する有用な事例があるが、9.xのAuthorityにはしない。**現行X4データ・現行Egosoft Tools・動作済み現行例で再確認する。**

---

## D. Engine

- [ ] 必要数を配置
- [ ] Sizeが正しい
- [ ] Standard / Advancedが正しい
- [ ] 必要なgroupへ所属
- [ ] group構成が他surface elementとの意図した保護・機能関係に合う
- [ ] Engine ↔ Hull clearance PASS
- [ ] Engine ↔ Engine clearance PASS
- [ ] 後方方向が自然

---

## E. Shield

- [ ] 主船体Shield
- [ ] Surface Element保護用Shield（必要時）
- [ ] Sizeが正しい
- [ ] Standard / Advancedが正しい
- [ ] Group対応が正しい
- [ ] groupが何を保護する想定かを現行動作例で確認
- [ ] Clearance PASS

---

## F. Weapon / Turret

### Fixed Weapon

- [ ] 必要数
- [ ] 射撃方向
- [ ] 左右対称（必要時）
- [ ] 船体による過度な射線遮蔽なし
- [ ] group有無を現行の動作済み同種艦と照合
- [ ] Connection名・tagが選択する武器macroと整合

### Turret

- [ ] 必要数
- [ ] Size
- [ ] Standard / Advanced
- [ ] Group
- [ ] Turret ↔ Hull clearance PASS
- [ ] Turret ↔ Turret clearance PASS
- [ ] 主要射界が成立

Custom articulated turretを作る場合:

- [ ] socket → yaw → pitch等の親子関係が意図通り
- [ ] yaw / pitchのIK・回転制約が正しい
- [ ] muzzle / laser connectionが動くpitch側へ追従
- [ ] offline geometry一致だけでruntime PASSにしない

---

## G. Dock

艦載機対応時。

- [ ] `dockarea`
- [ ] `dockingbay / shipstorage`
- [ ] `storage`
- [ ] `dock_xs`（必要時）
- [ ] Dock Connectionとship macro側のdock macro bindingが対応
- [ ] binding先dock macroのattachment connectionが正しい
- [ ] Dock進入方向
- [ ] Approach corridor PASS
- [ ] Departure corridor PASS
- [ ] Exclusion zone PASS
- [ ] Turret / Antenna / Hull等が経路を塞がない

Dock Doorを使う場合:

- [ ] hatch位置
- [ ] closed時PASS
- [ ] opening中PASS
- [ ] open時PASS
- [ ] closing中PASS

Custom dock / traffic pathを使う場合:

- [ ] waypoint / pathが必要か現行バニラ例で確認
- [ ] 古いwaypoint仕様をそのままコピーせず、current dataでリンク関係を再確認

---

## H. Ship Storage

Dockとは別項目として確認。

- [ ] 対応サイズを定義
- [ ] XS storage（必要時）
- [ ] S storage（必要時）
- [ ] M storage（必要時）
- [ ] Ship Storage Connectionとship macro側のstorage macro bindingが対応
- [ ] Dock / Hangarとの位置関係が自然

Ship Storageは空母専用機能ではない。

---

## I. Repair / Rearm

対応艦のみ。

- [ ] 通常Dockが成立
- [ ] `buildmodule`
- [ ] `shiptrader`
- [ ] 対応するservice / resupply macro要求を満たす
- [ ] 通常格納とRepair/Rearmを別機能として扱っている

---

## J. Launch Tube

採用時のみ。

- [ ] 通常Dockとは別設備
- [ ] launch方向
- [ ] tube内部clearance
- [ ] 出口clearance
- [ ] 複数tubeの経路が不自然に交差しない
- [ ] 対応dock sizeが正しい
- [ ] launch用component/macro bindingが成立

通常発艦にLaunch Tubeは必須ではない。

---

## K. Interior / Room

- [ ] cockpit位置と船体外形が対応
- [ ] dynamicroom位置が自然
- [ ] window系roomが外形と対応
- [ ] Dock / Bridge / Interiorの関係が不自然でない

未確定・追加調査対象:

- Transporter Room
- Interior間移動
- ship exterior exit
- spacesuit ingress / egress

これらは基本Layout開始をblockingしない。

---

## L. Egosoft Visualization

- [ ] Engine visualization確認
- [ ] Shield visualization確認
- [ ] Turret visualization確認
- [ ] Dock / exclusion visualization確認
- [ ] Reserved ZoneとHullの干渉なし

精密な装備形状ではなく、**ゲーム側が要求する配置空間**を優先する。

ただしVisualizationが証明するのは主にclearanceであり、macro binding、animation、firing、runtime behaviorまでは証明しない。

---

## M. Reference Comparison

絶対座標をコピーしない。

確認:

- [ ] Connectionの相対位置
- [ ] Orientation
- [ ] Group構成
- [ ] Engine layout
- [ ] Weapon / Turret layout
- [ ] Dock ↔ Storage layout
- [ ] Approach direction
- [ ] Hatch位置
- [ ] Service構成
- [ ] Launch Tube方向
- [ ] component Connection ↔ ship macro bindingの対応

---

# Gate A — Layout Freeze

## Flight

- [ ] cockpit
- [ ] playercontrol
- [ ] aimtarget
- [ ] engine
- [ ] shield
- [ ] countermeasures

## Combat

- [ ] fixed weapon
- [ ] turret
- [ ] groups
- [ ] weapon clearance
- [ ] turret clearance

## Docking

対応時:

- [ ] dockarea
- [ ] dockingbay
- [ ] shipstorage
- [ ] storage
- [ ] approach clearance
- [ ] departure clearance
- [ ] hatch clearance

## Binding / Identity

- [ ] Connection名の重複なし
- [ ] 必要なmacro binding成立
- [ ] macro側から存在しないConnectionを参照していない
- [ ] group / tag / compatibilityがcurrent dataと整合
- [ ] 公開済みID/Connection名を不用意に変更していない

## Service

対応時:

- [ ] buildmodule
- [ ] shiptrader

## Carrier

対応時:

- [ ] 必要なS Dock
- [ ] 必要なM Dock
- [ ] 必要なShip Storage
- [ ] 十分な発着経路
- [ ] Launch Tube（採用時）

---

## Gate result

### PASS

X4機能配置、Binding、Reserved Clearanceが成立。

→ Layout Freezeして詳細モデリングへ。

### REVISE

Connectionは揃っているが局所干渉またはbinding不整合あり。

→ Blockout / Connection / bindingを局所修正して再検証。

### BLOCKED

必要機能の配置空間または成立するbinding構成が存在しない。

→ 艦体レイアウトまたは機能構成から再設計。
