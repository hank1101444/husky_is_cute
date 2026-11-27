# Walking Skeleton：團隊工作單
## 一次會議，四人一起 | 約 75 分鐘 | 每隊一份

> **狀態：會前準備的草稿。** 由 Hank（code steward）用 Claude Code、依 `main`（`89d69b6`）上的程式碼
> 事先準備。標示 *（提案）* 的內容是**會前**寫的，請在會議中確認、修改或刪除。所有空白欄位在
> **會議中**填寫。不確定就留空，不要猜。

**時間：** ____（要在 merge day 之前；CP2 截止 2026-11-29 當天結束前）
**地點／通話連結：** ____
**出席：** ☐ hank1101444 ☐ TiffanyChen-tc ☐ ChingChingKao ☐ ShenChiaoXiuan
**缺席者與原因**（缺席者會後讀這份文件並補上一行）：

**CP2 要交的：** 這份文件，以及 Part 4 合併的 PR 連結。

**開始前（5 分鐘，所有人）：**

- [ ] 在 `main` 上 `git pull`、`conda activate husky`、`pytest` 通過（2026-11-27 為 154 passed）
- [ ] `streamlit run src/onboarding_map/app.py` 能開；按「載入示範地圖（不需 API key）」會出現地圖
- [ ] 準備一個共享畫面，給 Part 3b 和 Part 4 用
- [ ] API key 只放在 `.env`。絕不貼進這份文件、PR 或聊天室。

**每個 Part 的打字者** *（提案；每個 Part 換人）*：Part 1 Tiffany · Part 2 Hank · Part 3 Shen · Part 4 Ching · Part 5 Tiffany

---

## Part 1 ★ | 用一句話說出工具在做什麼（10 分鐘）

每個人先**獨自寫 2 分鐘**，再把四句唸出來，討論出一句共識。（刻意不事先準備：重點是看我們四人寫的是否一致。）

> 我們的工具幫助 **［誰］** 去 **［做什麼］**，方法是 **［白話說明怎麼做］**。

| | 句子 |
|---|---|
| hank1101444 | |
| TiffanyChen-tc | |
| ChingChingKao | |
| ShenChiaoXiuan | |
| **共識句** | |

**四句一致嗎？** ☐ 一致 ☐ 大致一致 ☐ 不一致

如果不一致，我們討論後解決的差異是：

>

---

## Part 2 ★ | 畫出流程並分工（10 分鐘）

**1. 流程** *（提案，依程式碼畫的；會議中修正）*：

```
[Bob 貼上 repo 網址]                          app.py（或按示範地圖按鈕）
  -> [GitHub API -> RepoSnapshot]             github_fetcher.py
  -> [Claude 產生地圖，我們檢查每個來源 ID]      prompts.py + mapper.py
  -> [存進 SQLite]                             store.py
  -> [Bob 確認／修改／標記錯誤；                  app.py
      Alice 讀地圖並對模組提問；Bob 回答]
```

**2. 我們在哪一步。** ☐ Route 1（還跑不起來）☐ Route 2（已經能跑）— *（提案：Route 2；
`main` 上兩個角色的完整流程都能跑）*

**Route 2 追蹤（約 5 分鐘）。** 每個框由「不是寫它的人」講解一分鐘。每個框的第一版都是 Hank 寫的，所以 Hank 不講。

| 框 | 最初作者／後來修改者 | 講解者 *（提案）* | 講得出來嗎？（可以／部分／只有作者能講） | 還有寫死或假的部分嗎？ |
|---|---|---|---|---|
| `github_fetcher.py` | Hank (#6) / Shen (#10) | ShenChiaoXiuan | | |
| `prompts.py` + `mapper.py` | Hank (#6) / Shen (#11)、Tiffany (#21) | TiffanyChen-tc | | |
| `store.py` | Hank (#6) / Ching (#9) | ChingChingKao | | |
| `app.py` | Hank (#7) / Ching (#8)、Tiffany (#16)、Shen (#18, #19) | ShenChiaoXiuan 或 ChingChingKao | | |

**挑選下一個薄切片。** 工作單列的三個 Route 2 選項在 `main` 上都已完成：

1. *流程上有假的或寫死的部分：* 正式流程上沒有。示範地圖（#18）是刻意做的假資料。
2. *第二個人：* Bob 和 Alice 兩個角色都已接上。
3. *AI 呼叫的失敗狀態：* `mapper.draft_map` 已把連線錯誤與逾時、用量上限、拒絕、被截斷或格式錯誤的輸出轉成中文訊息，
   `tests/test_mapper_call.py` 用假的 client 測過。

所以從我們的 backlog 挑下一刀。

**今天的目標** *（提案）*：

> **Issue #23：標出人工修改過的說法。** 範例：在示範地圖上，Bob 把某個模組的用途說明改寫成自己的話。
> 輸入：這次修改。輸出：Alice 看到「✅ 已確認 · ✍️ 人工修改 · <Bob 寫的句子>」，Bob 另外看到
> 「原本 AI 寫的：<AI 的原句>」。目前被修改過的說法，看起來跟 Bob 只按了確認的 AI 說法一模一樣
> （Group 10 的 review，A3）。store 已經把原文存在 `ai_text`（`tests/test_store.py` 有測），所以不用改資料庫。

**3. 分工（開工前先講好每塊收什麼、回傳什麼）** *（提案）*：

| 誰 | 任務 | 收到 | 回傳 | Branch 名稱 |
|---|---|---|---|---|
| ChingChingKao | 在 `models.py` 加 `Claim.human_edited` property，並在 `tests/test_models.py` 加測試 | 一個 `Claim` | `bool`：只有 `ai_text` 有值且 `text != ai_text` 時為 `True` | `skeleton/model` |
| TiffanyChen-tc | 在 `app.py` 加 `provenance_label(claim)`，並寫單元測試 | 一個 `Claim` | 有修改時回傳 `" · ✍️ 人工修改"`，否則 `""` | `skeleton/label` |
| ShenChiaoXiuan | 在 `app.py` 加 `original_text_note(claim)`，並寫單元測試 | 一個 `Claim` | 有修改時回傳 `"原本 AI 寫的：<ai_text>"`，否則 `None` | `skeleton/original` |
| hank1101444 | **先寫測試：** 在 `tests/test_app.py` 加兩個在 `main` 上會失敗的 AppTest（Alice 在修改過的說法上看到「人工修改」、沒修改的看不到；只有 Bob 看得到「原本 AI 寫的」） | 預先存好的地圖 + `store.review_claim(..., "edit", ...)` | 各塊接上後就會通過的失敗測試 | `skeleton/tests` |

接線（在 Part 3b 一起做，不是一個人做）：`render_claim()` 在兩個角色的狀態標籤後面加上
`provenance_label(claim)`，並只對 Bob 用 caption 顯示 `original_text_note(claim)`。

**model 那塊接上前的約定假資料** *（提案）*：Tiffany 和 Shen 先直接寫
`claim.ai_text is not None and claim.text != claim.ai_text` 判斷是否修改過，`skeleton/model` 接上後再改用
`claim.human_edited`。

**僅 Route 2：只有作者能講解的框**（會後變成配對或 review 任務）：

>

**今天刻意不做的** *（提案）*：

> 讓 Alice 看到 AI 原文；Bob 改回跟 AI 一字不差時的標示；統計框；issue #24（側欄的示範標籤）和
> issue #22（要改 prompt，需要跑 live suite）。

---

## Part 3 ★ | 各自做，再一起接起來（30 分鐘）

**3a. 各自做（20 分鐘）**，在自己的 branch 上，照 Part 2 講好的接口做。可以用 AI 工具，但留下來的東西你要講得出來。
卡住約五分鐘？就在你的邊界用約定好的格式回傳假資料，並寫下你假了什麼。

**3b. 一起接（10 分鐘，同一個共享畫面）**，依流程順序一塊一塊合進 `skeleton` branch。每一塊：
由不是作者的人說明它在做什麼；合進 `skeleton`；跑 `pytest` 和範例；失敗就一起修。

| 區塊 *（提案順序）* | 誰做的 | 誰講解 | 接上了嗎？（是／修了才接上／還沒） | 接的時候修了什麼 |
|---|---|---|---|---|
| 1. 失敗的測試（`skeleton/tests`） | | | | |
| 2. `Claim.human_edited`（`skeleton/model`） | | | | |
| 3. `provenance_label`（`skeleton/label`） | | | | |
| 4. `original_text_note`（`skeleton/original`）+ 接進 `render_claim()` | | | | |

**要跑的範例** *（提案）*：`streamlit run src/onboarding_map/app.py` → 載入示範地圖 → 以 Bob 身分修改一條用途說明 →
切到 Alice → 該說法顯示「✍️ 人工修改」；切回 Bob → 下面有「原本 AI 寫的：…」。

**第一次從頭跑到尾是什麼時候？**（時間，或「還沒」）

>

**我們假了或先寫死了什麼？**

>

---

## Part 4 ★ | 一起開 PR（15 分鐘）

1. 從 `skeleton` 開**一個 PR** 到 `main`，用我們的 PR 範本。**作者把「What this PR does」唸出來**。
   *（提案：不由 Hank 開，因為 Hank 是現任 steward，要負責 approve；GitHub 不允許作者 approve 自己的 PR）*
2. **現任 code steward** 在**共享畫面上** review，至少留一則真正的留言：問題、疑慮或具體建議。只寫「看起來不錯」不算。
3. 作者回覆留言（回答或改程式）。
4. Steward approve 並 merge（merge commit）。PR 說明寫 `Closes #23`。

| | |
|---|---|
| 合併的 PR 連結 | |
| PR 作者 | |
| Review 的 steward | hank1101444（依 `DECISIONS.md` 中 TiffanyChen-tc → hank1101444 的交接紀錄） |
| Steward 的留言（貼過來） | |
| 作者怎麼回覆 | |

**要加進 `DECISIONS.md` 的一行**，寫今天最大的決定（砍掉什麼、假了什麼、或講好的接口格式）：

>

---

## Part 5 | 團隊檢討（5 分鐘）

1. **今天合作上哪裡做得好？**

   >

2. **哪裡困難或卡卡的？**

   >

3. **誰最少機會參與？下次怎麼改善？**（有沒有只有一個人能講解的框？打算怎麼處理？）

   >

4. **Merge day 我們要改變的一件事：**

   >

5. **發現的阻礙，以及誰負責後續：**

   >

---

## 快速檢查（給我們自己，不評分）

☐ 四個人都出席了
☐ 四個人都做了一塊，而且每塊都由不是作者的人講解過
☐ 我們有一句共識，說明工具在做什麼
☐ 各塊接起來了，新切片能跑（就算有些部分是假的）
☐ PR 由 steward review、至少一則真正的留言，並已合併
☐ 這份文件存成 `docs/walking_skeleton.md`，`DECISIONS.md` 也加了那一行
