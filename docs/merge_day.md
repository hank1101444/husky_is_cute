# Merge Day：團隊工作單
## 一次會議，四人一起 | 約 60 分鐘（另加 steward 準備約 15 分鐘）| 每隊一份

> **狀態：會前準備，會議尚未舉行。** 「會前準備」一節由 Hank（code steward）用 Claude Code、依
> 2026-11-27 的 repo 狀態（`main` 在 `89d69b6`）事先寫好。合併計畫本身要在會前以新條目寫進
> `DECISIONS.md`（Part 0）。Part 1 之後的內容在**會議中**填寫。

**時間：** ____（在 walking skeleton 之後；CP2 截止 2026-11-29 當天結束前，並留時間修正發現的問題）
**地點／通話連結：** ____
**出席：** ☐ hank1101444 ☐ TiffanyChen-tc ☐ ChingChingKao ☐ ShenChiaoXiuan
**缺席者與原因：**

**CP2 要交的：** `DECISIONS.md` 中的合併計畫條目，加上結果（Part 4），以及這份文件。**今天不加任何新東西。**

---

## 會前準備（2026-11-27 的 repo 狀態）

- **開著的 PR：** 無。PR #1–#12 和 #16–#21 都已合併。
- **已合併、merge day 可刪除的遠端 branch：** `ching`、`ching-fix-2`、`feat/sidebar-page-index`、
  `fix/module-id-collision`、`husky-test`、`mvp`、`mvp-setup`、`mvp-ui`、`shen-fetch-pr-reviews`、
  `shen-no-reason-normalize`、`shen-offline-demo`、`shen-steward-record`、`shen-test`、
  `shen-validate-url-first`、`week12/ai-guidelines`、`week12/pr-template`（刪之前先用
  `git branch -r --merged origin/main` 確認）。
- **開著的 issue #22、#23、#24**（Group 10 review 的發現）是 Phase 3 的工作，目標日期在 12 月。
  除非 walking skeleton 的切片關掉了其中一個，否則維持開著。
- **`main` 是綠的：** `pytest` → 154 passed，13 個 live 測試 deselected。
- **已知會衝突的地方：** 幾乎每個 PR 都會在 `DECISIONS.md` 和 `docs/prompt_log.md` 尾端加內容，以前就衝突過（#16）。
  解法：兩邊都保留，依日期排序。
- **merge day 時可能會有的 PR**（在 Part 0 確認）：這份工作單的 PR；walking skeleton 的 PR（應該在那場會議就合併）；
  `docs/design_rationale.md` §3 的使用者測試結果；更新後的 evaluation report。
- **fresh clone 測試要注意的 README 缺口：** README 沒提到「載入示範地圖（不需 API key）」按鈕，
  而這是沒有 key 時唯一能試用的方式。

---

## Part 0 ★ | Steward 的合併計畫（會前，約 15 分鐘，由現任 code steward 寫）

**會前**以新條目寫進 `DECISIONS.md`，讓大家先讀。定案的表格也複製一份到這裡。

**所有開著的 branch 與 PR：**

| # | Branch / PR | 做什麼（一行） | 作者 | 準備好了嗎？（是／還要修／關掉） | 跟誰改到同樣的檔案 |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |

**合併順序與原因：**

> 1.
> 2.
> 3.

**預期的衝突**（哪些檔案、哪些 PR 之間）：

>

**今天「完成」的定義**（一句話：什麼要能從頭跑到尾？）：

>

**不合併直接關掉的 PR 與原因：**

>

---

## Part 1 | 確認計畫（5 分鐘）

一起讀 steward 的計畫，有人看到問題就調整順序。輪流當 driver（打字的人），至少三個人當過。

| 合併 # | Driver | 畫面上的 reviewer |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

---

## Part 2 ★ | 一次合併一個（約 35 分鐘）

依計畫順序，**每一個** PR：

1. **用 `main` 更新它**（在 branch 上 `git pull origin main`，或在 GitHub 按「Update branch」）
2. **有衝突？一起解。** 把兩邊都唸出來。如果 AI 工具提出解法，driver 要在接受**之前**說明它保留了什麼、丟掉了什麼
3. 在 branch 上**跑測試和 app**（`pytest`，然後 `streamlit run src/onboarding_map/app.py`）
4. **Review 並合併**（用 merge commit；reviewer approve，有意見就至少留一則真正的留言）
5. **在 `main` 上再跑一次測試和 app**，通過了才做下一個

| # | PR | 有衝突嗎？（在哪） | 怎麼解的 | 合併後測試（通過／失敗） | `main` 上 app 能跑嗎？ |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |

**如果 `main` 壞掉：** 停止合併。立刻修（開一個小 PR），或 revert 最後一次合併
（`git revert -m 1 <merge commit>`）並寫下原因。

---

## Part 3 ★ | Fresh clone 測試（10 分鐘）

由**不是** steward 的人：

1. 把 repo clone 到一個**新資料夾**（`git clone https://github.com/hank1101444/husky_is_cute.git merge_day_check`）
2. **只照 README** 安裝和執行（新的 conda env、自己的 `.env`）
3. 從頭到尾做完**主要任務**：Bob 產生（或載入示範）地圖並審核說法；Alice 讀地圖並提問；Bob 回答；Alice 看到回答

| | |
|---|---|
| 誰做的 | |
| 只看 README 就能完成嗎？（可以／部分／不行） | |
| README 少了什麼？ | |
| 主要任務從頭到尾都成功嗎？ | |
| 有沒有只有某個人知道的 API key 或設定步驟？ | |

小的 README 缺口當場修。比較大的開成 issue。

---

## Part 4 ★ | 記錄結果（5 分鐘）

**加在 `DECISIONS.md` 合併計畫條目下方：**

> **Outcome ([日期])：** 合併了 #__、#__、#__；關掉 #__，因為 __。衝突在 __，用 __ 解決。Fresh clone 測試由 __ 執行：[成功／修了 __ 之後成功]。`main` 是 [綠的／還沒綠，因為 __]。留到 CP2 之後：issue #__、#__。

**團隊檢討**（誠實，每題一行）：

1. 什麼讓合併變得比需要的更難？

   >

2. Phase 3 我們要改的一個習慣：

   >

3. 每個人都能不靠幫忙跑起原型並完成主要任務嗎？不行的話，誰跟誰在 CP2 前一起練習？

   >

---

## 快速檢查（給我們自己，不評分）

☐ 合併計畫在會議開始前就在 `DECISIONS.md` 裡
☐ 四個人都在
☐ 每個開著的 PR 都合併了，或附理由關掉
☐ 每次合併後都在 `main` 上跑了測試和 app
☐ 由 steward 以外的人做了 fresh clone 測試
☐ 結果已寫在合併計畫下方
☐ 這份文件存成 `docs/merge_day.md`
