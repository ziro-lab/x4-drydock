# X4 Ship Placement Checklist v0.1

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

---

## D. Engine

- [ ] 必要数を配置
- [ ] Sizeが正しい
- [ ] Standard / Advancedが正しい
- [ ] 必要なgroupへ所属
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
- [ ] Clearance PASS

---

## F. Weapon / Turret

### Fixed Weapon

- [ ] 必要数
- [ ] 射撃方向
- [ ] 左右対称（必要時）
- [ ] 船体による過度な射線遮蔽なし

### Turret

- [ ] 必要数
- [ ] Size
- [ ] Standard / Advanced
- [ ] Group
- [ ] Turret ↔ Hull clearance PASS
- [ ] Turret ↔ Turret clearance PASS
- [ ] 主要射界が成立

---

## G. Dock

艦載機対応時。

- [ ] `dockarea`
- [ ] `dockingbay / shipstorage`
- [ ] `storage`
- [ ] `dock_xs`（必要時）
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

---

## H. Ship Storage

Dockとは別項目として確認。

- [ ] 対応サイズを定義
- [ ] XS storage（必要時）
- [ ] S storage（必要時）
- [ ] M storage（必要時）
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

X4機能配置とReserved Clearanceが成立。

→ Layout Freezeして詳細モデリングへ。

### REVISE

Connectionは揃っているが局所干渉あり。

→ Blockout / Connectionを局所修正して再検証。

### BLOCKED

必要機能の配置空間が存在しない。

→ 艦体レイアウトから再設計。
