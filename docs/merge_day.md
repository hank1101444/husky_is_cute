# Merge Day：團隊工作單
## 一次會議，四人一起 | 約 60 分鐘（另加 steward 準備約 15 分鐘）| 每隊一份

> **狀態：已完成（2026-11-28），比原訂的 11/29 早一天。** Part 0 由 hank1101444（現任 code steward）
> 用 Claude Code 依 2026-11-28 的 repo 狀態準備，同一份計畫也已寫進 `DECISIONS.md`（2026-11-28 — Merge day plan）。
> Part 1–4 由 hank1101444 用 Claude Code 依 git／GitHub 紀錄（merge commit、PR review 與留言）和 hank1101444 的
> 說明填寫；紀錄裡沒有的欄位標「（待填）」，不猜。

**這是什麼：** 在交 CP2 之前讓 `main` 變乾淨、能跑：所有開著的 PR 都合併或附理由關掉，衝突大家一起解，最後在全新的 clone 上從頭跑到尾。
**這不是什麼：** 不是趕功能。**今天不加任何新東西。** 會議中做完的新功能，等 merge day 之後再開 PR。

**時間：** 2026-11-28 00:57（#26 合併）、01:07（#27 合併）；刪除 branch、fresh clone 測試在同日稍後
**地點／通話連結：** 線上
**出席：** ☑ hank1101444 ☑ TiffanyChen-tc ☑ ChingChingKao ☑ ShenChiaoXiuan
**缺席者與原因：** 無

**CP2 要交的：**
1. `DECISIONS.md` 中的合併計畫條目（Part 0），並在最後補上**結果**（Part 4）
2. 這份文件，存成 `docs/merge_day.md`

**用法：** 一個人打字、其他人講，每個 Part 換打字的人。★ 是時間不夠時要保住的部分。時間用完就寫下還剩什麼，交出現有的內容。

---

## Part 0 ★ | Steward 的合併計畫（會前，約 15 分鐘，現任 code steward）

**會前**寫成 `DECISIONS.md` 的新條目，讓大家先讀。（已寫：`DECISIONS.md` → 2026-11-28 — Merge day plan）

**2026-11-28 的 repo 狀態：**
- `main` 在 `324edd1`（PR #25，walking skeleton 已合併），`pytest` → 161 passed、13 deselected。
- GitHub 上**沒有開著的 PR**。PR #1–#12、#16–#21、#25 都已合併。
- 開著的 issue：#22、#24（Group 10 review 的發現，Phase 3 工作，目標日期在 12 月）。#23 已由 PR #25 關閉。

**所有開著的 branch 與 PR：**

| # | Branch / PR | 做什麼（一行） | 作者 | 準備好了嗎？（是／還要修／關掉） | 跟誰改到同樣的檔案 |
|---|---|---|---|---|---|
| 1 | `docs/team-sessions`（PR 待開；**由 Hank 以外的人開**，Hank 才能以 steward 身分 approve） | 兩份 worksheet、evaluation report、合併計畫與統計定義的 DECISIONS 條目 | hank1101444（Claude Code 協助），四人填寫 worksheet | 是（使用者測試結果除外） | #2：`DECISIONS.md`、`docs/prompt_log.md`、`docs/evaluation_report.md` |
| 2 | `docs/user-testing`（尚未建立；從 `docs/team-sessions` 開） | 兩場團隊外使用者測試：`design_rationale.md` §3、evaluation report 的結果、在 `DECISIONS.md` 引用 | 主持測試的組員 | 測試完成、寫好後才算準備好 | #1：同上 |
| 3 | 已合併、可刪除的遠端 branch | `skeleton/tests`、`skeleton/model`、`skeleton/label`、`skeleton/original`、`walking-skeleton`，以及 PR #1–#21 留下的 16 個 branch | — | 刪除（先用 `git branch -r --merged origin/main` 確認） | — |

**合併順序與原因：**

> 1. `docs/team-sessions`：它帶著這份合併計畫和 evaluation report 的架構，#2 是從它開出來的，所以先進。
> 2. `docs/user-testing`：補上測試結果；更新到最新的 `main` 之後，只剩它自己新增的內容。
> 3. 刪除已合併的 branch，最後在 `main` 上做 fresh clone 測試。
>
> 當天如果有其他 PR，排在這兩個之後；若會影響 fresh clone 測試，就不合併，改開 issue。

**預期的衝突**（哪些檔案、哪些 PR 之間）：

> #1 和 #2 都可能在 `DECISIONS.md`、`docs/prompt_log.md` 尾端加內容，以前就衝突過（#16、`docs/team-sessions` 同步 `main` 時）。
> 解法：兩邊都保留，依日期排序。`docs/evaluation_report.md` 若兩邊都改，以 #2 的實際測試數字為準。

**今天「完成」的定義**（一句話：什麼要能從頭跑到尾？）：

> `main` 上 `pytest` 全部通過、Streamlit 能啟動；由 steward 以外的人只照 README，在新資料夾 clone、建環境，
> 完成 Bob 產生（或載入示範）地圖並審核、Alice 讀地圖並提問、Bob 回答、Alice 看到回答；而且沒有開著的 PR。

**不合併直接關掉的 PR 與原因：**

> 目前沒有。

---

## Part 1 | 確認計畫（5 分鐘）

一起讀 steward 的計畫，有人看到問題就調整順序。決定每次合併由誰 **driver**（打字）：輪流，至少三個人當過。

| 合併 # | Driver | 畫面上的 reviewer |
|---|---|---|
| 1：#26 `docs/team-sessions`（ShenChiaoXiuan 開） | hank1101444（按 merge） | hank1101444（steward：留言請改 *How I checked it* 的勾選，Shen 改好後 approve） |
| 2：#27 `docs/user-testing`（ChingChingKao 開） | TiffanyChen-tc（按 merge） | TiffanyChen-tc（留言後 approve） |
| 3：刪除 23 個已合併的遠端 branch | hank1101444（用 Claude Code） | — |
| 4：#__ `docs/merge-day-outcome`（這份紀錄與 Outcome） | （待填） | （待填） |

> 目前 driver 只有兩個人。#4 請 ChingChingKao 或 ShenChiaoXiuan 合併，才滿足「至少三個人當過」。

---

## Part 2 ★ | 一次合併一個（約 35 分鐘）

依計畫順序，**每一個** PR：

1. **用 `main` 更新它**（在 branch 上 `git pull origin main`，或在 GitHub 按「Update branch」）
2. **有衝突？一起解。** 把兩邊都唸出來。如果 AI 工具提出解法，driver 要在接受**之前**說明它保留了什麼、丟掉了什麼。沒人說得清楚的部分，就手動解
3. 在 branch 上**跑測試和 app**（`python -m pytest -q`，然後 `python -m streamlit run src/onboarding_map/app.py`）
4. **Review 並合併**（畫面上的 reviewer approve，有意見就至少留一則真正的留言；用 merge commit）
5. **在 `main` 上再跑一次測試和 app**，通過了才做下一個

| # | PR | 有衝突嗎？（在哪） | 怎麼解的 | 合併後測試（通過／失敗） | `main` 上 app 能跑嗎？ |
|---|---|---|---|---|---|
| 1 | #26 `docs/team-sessions` | GitHub 上沒有 | — | 通過：`main` `7f8f753`，161 passed、13 deselected | 當時沒檢查；#27 合併後確認可以 |
| 2 | #27 `docs/user-testing` | GitHub 上沒有。合併前把 `docs/team-sessions` 併進這個 branch 時，`docs/prompt_log.md` 尾端衝突：一邊在第 33 列補 #26，一邊在下一列新增一列 | 兩邊都保留（Claude Code，merge commit `c442220`），再跑 `pytest` 通過 | 通過：`main` `bdf91d1`，161 passed、13 deselected | 可以：headless 啟動，`/_stcore/health` 回 `ok` |
| 3 | 刪除已合併的 branch | — | 先用 `git branch -r --merged origin/main` 確認 23 個都已合併，記下 SHA 再刪 | — | — |
| 4 | #__ `docs/merge-day-outcome` | （待填） | | | |

> **跟計畫不同的地方：** #26、#27 在 2026-11-28 凌晨就合併了，比原訂的 merge day（11/29）早一天，沒有照 Part 2 的
> 步驟 1–5 逐一在共享畫面上做，#26 合併後也沒有檢查 app。#27 合併時 `DECISIONS.md` 的「User testing findings」還是草稿，
> 四人之後同意照草稿內容定案，在 #4 補正。`main` 沒有壞過。

**如果 `main` 壞掉：** 停止合併。立刻修（開一個小 PR），或 revert 最後一次合併（`git revert -m 1 <merge commit>`）並寫下原因。不要在壞掉的 `main` 上繼續疊合併。

---

## Part 3 ★ | Fresh clone 測試（10 分鐘）

由**不是** steward 的人：

1. 把 repo clone 到一個**新資料夾**（`git clone https://github.com/hank1101444/husky_is_cute.git merge_day_check`）
2. **只照 README** 安裝和執行（新的 conda env、自己的 `.env`）
3. 從頭到尾做完**主要任務**：Bob 產生（或按「載入示範地圖（不需 API key）」）地圖並審核說法；Alice 讀地圖並提問；Bob 回答；Alice 看到回答

| | |
|---|---|
| 誰做的 | ShenChiaoXiuan |
| 只看 README 就能完成嗎？（可以／部分／不行） | 可以 |
| README 少了什麼？ | 沒有回報缺漏 |
| 主要任務從頭到尾都成功嗎？ | 成功（依 hank1101444 轉述：「測試沒問題」） |
| 有沒有只有某個人知道的 API key 或設定步驟？ | 沒有回報；示範地圖不需要 API key |

小的 README 缺口當場修。比較大的開成 issue。

---

## Part 4 ★ | 記錄結果（5 分鐘）

**加在 `DECISIONS.md` 合併計畫條目下方：**

> **Outcome ([日期])：** 合併了 #__、#__；關掉 #__，因為 __。衝突在 __，用 __ 解決。Fresh clone 測試由 __ 執行：[成功／修了 __ 之後成功]。`main` 是 [綠的／還沒綠，因為 __]。留到 CP2 之後：issue #__、#__。

已寫入 `DECISIONS.md`（2026-11-28 — Merge day plan 下方的 **Outcome**）。

**團隊檢討**（誠實，每題一行）：

*以下 1–3 由 Claude Code 依紀錄草擬，請組員確認或改寫。*

1. 什麼讓合併變得比需要的更難？（例如：branch 放太久、PR 太大、兩個人改同一個檔案）

   > `docs/user-testing` 從 `docs/team-sessions` 開出來，兩邊都在 `docs/prompt_log.md` 尾端加內容，所以同步時衝突；
   > 另外 #27 合併時 DECISIONS 還是草稿，要再開一個 PR 補正。

2. Phase 3 我們要改的一個習慣：

   > 合併前確認 PR 裡沒有標成草稿或「待填」的內容；要合併就照 merge day 的步驟一起做，包括合併後在 `main` 上跑 app。

3. 每個人都能不靠幫忙跑起原型並完成主要任務嗎？不行的話，誰跟誰在 CP2 前一起練習？

   > 有紀錄的是兩個人：ShenChiaoXiuan 在新資料夾只照 README 完成了主要任務（Part 3），hank1101444 在內部試用
   > （`design_rationale.md` §2 P1–P2）跑過完整流程。TiffanyChen-tc 和 ChingChingKao 在 walking skeleton 時都在自己的
   > branch 上做出一塊並跑過 `pytest`，但沒有獨自跑完主要任務的紀錄。CP2 前兩人各自照 README 跑一次示範地圖的主要任務
   > （Bob 載入並審核 → Alice 提問 → Bob 回答 → Alice 看到）；卡住就和 ShenChiaoXiuan 一起看，他剛做過 fresh clone。

---

## 快速檢查（給我們自己，不評分）

☑ 合併計畫在會議開始前就在 `DECISIONS.md` 裡（在 #26 的 branch 上，隨 #26 合併）
☑ 四個人都在
☑ 每個開著的 PR 都合併了，或附理由關掉（#4 合併後）
☐ 每次合併後都在 `main` 上跑了測試和 app（測試每次都跑了；app 只在 #27 之後檢查）
☑ 由 steward 以外的人做了 fresh clone 測試（ShenChiaoXiuan）
☑ 結果已寫在合併計畫下方
☑ 這份文件存成 `docs/merge_day.md`
