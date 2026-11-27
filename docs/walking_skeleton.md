# Walking Skeleton：團隊工作單
## 一次會議，四人一起 | 約 75 分鐘 | 每隊一份

> **狀態：會議進行中，逐步填寫。** 會前草稿由 Hank（code steward）用 Claude Code、依 `main`（`89d69b6`）
> 上的程式碼準備；Part 1、Part 2 與 Part 4 的安排已由四人確認。標示 *（預定）* 的是已分工、尚未完成的工作。
> 其餘空白欄位依實際結果填寫，不確定就留空，不要猜。

**時間：** 2026-11-27 22:00 – 2026-11-28 01:00
**地點／通話連結：** 線上，Google Meet
**出席：** ☑ hank1101444 ☑ TiffanyChen-tc ☑ ChingChingKao ☑ ShenChiaoXiuan
**缺席者與原因**（缺席者會後讀這份文件並補上一行）：無

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
| hank1101444 | 讓剛加入一個 team 的人可以快速了解現在專案的歷史以及現在的架構。 |
| TiffanyChen-tc | 新成員不用一開始就把整個 Repo 看完，可以先從系統產生的地圖找到主要模組、檔案及閱讀順序，有需要再點進去看。 |
| ChingChingKao | 我們用 AI 先整理 GitHub 專案的資訊，但不直接相信所有結果；每個說法都要有來源，舊成員也能確認、修改或標記錯誤。 |
| ShenChiaoXiuan | 這個工具把 GitHub 資料整理成入門地圖，讓舊成員先檢查內容，新成員能照著閱讀，也能直接針對模組提出問題。 |
| **共識句** | 我們的工具讓新加入專案的人更快理解現有程式碼：先整理 GitHub 的文件與開發紀錄，產生有來源的模組地圖，再由舊成員審核，新成員可以照地圖閱讀並提問。 |

**四句一致嗎？** ☐ 一致 ☑ 大致一致 ☐ 不一致

如果不一致，我們討論後解決的差異是：

> 四句的核心相同（幫新成員更快理解既有專案），強調的地方不同：Hank 講專案的歷史與架構，Tiffany 講閱讀順序，
> Ching 講「AI 不是最終權威、每個說法要有來源並由舊成員審核」，Shen 講 Bob／Alice 兩個角色與提問。共識句把四個重點合在一起。

---

## Part 2 ★ | 畫出流程並分工（10 分鐘）

**1. 流程**：

```
[Bob 貼上 repo 網址]                          app.py（或按示範地圖按鈕）
  -> [GitHub API -> RepoSnapshot]             github_fetcher.py
      （README、檔案樹、PR 與留言、Issue、Commit、DECISIONS.md）
  -> [Claude 產生地圖，我們檢查每個來源 ID]      prompts.py + mapper.py
  -> [存進 SQLite]                             store.py
  -> [Bob 確認／修改／標記錯誤；                  app.py
      Alice 讀地圖並對模組提問；Bob 回答]
```

**2. 我們在哪一步。** ☐ Route 1（還跑不起來）☑ Route 2（已經能跑）：`main` 上兩個角色的完整流程都能跑。

**Route 2 追蹤（約 5 分鐘）。** 每個框由「不是寫它的人」講解一分鐘。每個框的第一版都是 Hank 寫的，所以 Hank 不逐一講解程式框，只補充跨模組的介面。

| 框 | 最初作者／後來修改者 | 講解者與重點 | 講得出來嗎？（可以／部分／只有作者能講） | 還有寫死或假的部分嗎？ |
|---|---|---|---|---|
| `github_fetcher.py` | Hank (#6) / Shen (#10) | ShenChiaoXiuan：如何取得 repo 資料；PR review 文字為何要另外抓；沒有 review 內容時怎麼處理 | 可以 | 否 |
| `prompts.py` + `mapper.py` | Hank (#6) / Shen (#11)、Tiffany (#21) | TiffanyChen-tc：地圖怎麼產生、怎麼驗證來源；重複的模組 ID 為何要重新命名、如何避免 `a`／`a-2` 碰撞 | 可以 | 否 |
| `store.py` | Hank (#6) / Ching (#9) | ChingChingKao：SQLite 怎麼存地圖、claim、review event；確認／修改／標記後的統計為何依「目前狀態」計算 | 可以 | 否 |
| `app.py` | Hank (#7) / Ching (#8)、Tiffany (#16)、Shen (#18, #19) | 三人分段：Ching 講來源連結（#8）、Tiffany 講側欄頁面索引（#16）、Shen 講示範模式與 URL 驗證（#18、#19） | 可以 | 示範地圖是刻意的假資料（#18），畫面上有標示 |
| 整體資料流 | — | hank1101444：串起前面各框，說明 Bob／Alice 各做什麼、為什麼先驗證來源再顯示 claim、完整流程怎麼測 | 可以 | 否 |

**挑選下一個薄切片。** 工作單列的三個 Route 2 選項在 `main` 上都已完成：

1. *流程上有假的或寫死的部分：* 正式流程上沒有。示範地圖（#18）是刻意做的假資料。
2. *第二個人：* Bob 和 Alice 兩個角色都已接上。
3. *AI 呼叫的失敗狀態：* `mapper.draft_map` 已把連線錯誤與逾時、用量上限、拒絕、被截斷或格式錯誤的輸出轉成中文訊息，
   `tests/test_mapper_call.py` 用假的 client 測過。

所以從我們的 backlog 挑下一刀。

**今天的目標**：

> **Issue #23：標出人工修改過的說法。** 範例：在示範地圖上，Bob 把某個模組的用途說明改寫成自己的話。
> 輸入：這次修改。輸出：Alice 看到「✅ 已確認 · ✍️ 人工修改 · <Bob 寫的句子>」，Bob 另外看到
> 「原本 AI 寫的：<AI 的原句>」。目前被修改過的說法，看起來跟 Bob 只按了確認的 AI 說法一模一樣
> （Group 10 的 review，A3）。store 已經把原文存在 `ai_text`（`tests/test_store.py` 有測），所以不用改資料庫。

**3. 分工（開工前先講好每塊收什麼、回傳什麼）**：

| 誰 | 任務 | 收到 | 回傳 | Branch 名稱 |
|---|---|---|---|---|
| ChingChingKao | 在 `models.py` 加 `Claim.human_edited` property，並在 `tests/test_models.py` 加測試（情境：改寫後不同、與 AI 原文相同、`ai_text` 為 `None`）；只做資料模型判斷，不碰 Streamlit 顯示 | 一個 `Claim` | `bool`：只有 `ai_text` 有值且 `text != ai_text` 時為 `True` | `walking-skeleton`（共用，第 1 個 commit） |
| TiffanyChen-tc | 在 `app.py` 加 `provenance_label(claim)`；驗收標準是讓 Hank 的對應 AppTest 變綠（`app.py` import 時會執行 `main()`，不適合單獨寫單元測試） | 一個 `Claim` | 有修改時回傳 `" · ✍️ 人工修改"`，否則 `""` | `walking-skeleton`（共用，第 2 個 commit） |
| ShenChiaoXiuan | 在 `app.py` 加 `original_text_note(claim)`；驗收標準是讓 Hank 的對應 AppTest 變綠（`app.py` import 時會執行 `main()`，不適合單獨寫單元測試） | 一個 `Claim` | 有修改時回傳 `"原本 AI 寫的：<ai_text>"`，否則 `None` | `walking-skeleton`（共用，第 3 個 commit） |
| hank1101444 | **先寫測試：** 在 `tests/test_app.py` 加兩個在 `main` 上會失敗的 AppTest（Alice 在修改過的說法上看到「人工修改」、沒修改的看不到；只有 Bob 看得到「原本 AI 寫的」） | 預先存好的地圖 + `store.review_claim(..., "edit", ...)` | 各塊接上後就會通過的失敗測試 | `skeleton/tests`，再成為 `walking-skeleton` 的起點 |

接線（在 Part 3b 一起做，不是一個人做）：`render_claim()` 在兩個角色的狀態標籤後面加上
`provenance_label(claim)`，並只對 Bob 用 caption 顯示 `original_text_note(claim)`。

**順序與假資料：** 三人依序在同一個 branch 上 commit（Ching → Tiffany → Shen），後面的人一開始就拿得到 `claim.human_edited`，所以不需要先寫假的判斷。

**僅 Route 2：只有作者能講解的框**（會後變成配對或 review 任務）：

> 沒有。每個框都由非初版作者講解，Hank 表示都聽懂了。

**今天刻意不做的**：

> 讓 Alice 看到 AI 原文；Bob 改回跟 AI 一字不差時的標示；審核統計和其他 UI 調整；不改資料庫結構；
> issue #24（側欄的示範標籤）和 issue #22（要改 prompt，需要跑 live suite）。避免工作範圍太大。

---

## Part 3 ★ | 各自做，再一起接起來（30 分鐘）

**3a. 各自做（20 分鐘）**，在自己的 branch 上，照 Part 2 講好的接口做。可以用 AI 工具，但留下來的東西你要講得出來。
卡住約五分鐘？就在你的邊界用約定好的格式回傳假資料，並寫下你假了什麼。

**3b. 一起接（10 分鐘，同一個共享畫面）**，依順序一塊一塊 commit 到共用的 `walking-skeleton` branch（`skeleton` 這個名字和 `skeleton/tests` 在 git 裡會衝突，所以改名）。
每一塊：由不是作者的人說明它在做什麼；push 後跑 `pytest` 和範例；失敗就一起修。預期紅燈數：2 → 2 → 1 → 0。

| 區塊 *（預定順序）* | 誰做的 | 誰講解 | 接上了嗎？（是／修了才接上／還沒） | 接的時候修了什麼 |
|---|---|---|---|---|
| 1. 失敗的測試（Hank） | hank1101444（用 Claude Code 協助；在 `main` 上 2 failed、原有 154 passed） | *（預定）* ChingChingKao | | |
| 2. `Claim.human_edited`（Ching） | *（預定）* ChingChingKao | *（預定）* TiffanyChen-tc | | |
| 3. `provenance_label`（Tiffany） | *（預定）* TiffanyChen-tc | *（預定）* ShenChiaoXiuan | | |
| 4. `original_text_note`（Shen）+ 接進 `render_claim()` | *（預定）* ShenChiaoXiuan | *（預定）* hank1101444 | | |

**每接一塊要跑的檢查：**

```bash
python -m pytest tests/test_models.py tests/test_app.py -q
python -m pytest -q
python -m streamlit run src/onboarding_map/app.py
```

**要跑的範例**：載入示範地圖 → 以 Bob 身分修改一條用途說明 → 切到 Alice → 該說法顯示「✍️ 人工修改」，
未修改的說法沒有標記；切回 Bob → 下面有「原本 AI 寫的：…」。

**事先已知要一起看的地方：** Tiffany 和 Shen 都會改 `app.py` 的 `render_claim()`，合併時可能衝突；最終一律改用
`claim.human_edited`，不留兩份判斷。

**第一次從頭跑到尾是什麼時候？**（時間，或「還沒」）

>

**我們假了或先寫死了什麼？**

>

---

## Part 4 ★ | 一起開 PR（15 分鐘）

1. 從 `walking-skeleton` 開**一個 PR** 到 `main`，用我們的 PR 範本。**作者把「What this PR does」唸出來**。
   由 ChingChingKao 開，不由 Hank 開：Hank 是現任 steward，要負責 approve，而 GitHub 不允許作者 approve 自己的 PR。
2. **現任 code steward** 在**共享畫面上** review，至少留一則真正的留言：問題、疑慮或具體建議。只寫「看起來不錯」不算。
3. 作者回覆留言（回答或改程式）。
4. Steward approve 並 merge（merge commit）。PR 說明寫 `Closes #23`。

| | |
|---|---|
| 合併的 PR 連結 | |
| PR 作者 | ChingChingKao（統整 PR 描述） |
| PR 標題 | `feat: show provenance for human-edited claims` |
| Review 的 steward | hank1101444（依 `DECISIONS.md` 中 TiffanyChen-tc → hank1101444 的交接紀錄） |
| Steward 的留言（貼過來） | |
| 作者怎麼回覆 | |

**PR 驗收事項**：修改過的 claim 有標籤、沒修改的沒有；只有 Bob 看得到 AI 原句；Bob 的確認／修改／標記
與 Alice 問答仍正常；`pytest` 和手動驗收結果附在 PR。

**要加進 `DECISIONS.md` 的一行**，寫今天最大的決定（砍掉什麼、假了什麼、或講好的接口格式）。已加在 `walking-skeleton` branch 的 `DECISIONS.md`（2026-11-27 — Walking skeleton slice），隨這個 PR 合併：

> Human-edited claim provenance：用既有 `Claim.ai_text` 和 `Claim.text` 的差異判斷人工修改，
> 不新增資料庫欄位。Alice 看得到「人工修改」標示，AI 原文只顯示給 Bob。以最小範圍處理 issue #23，不動審核與統計功能。

---

## Part 5 | 團隊檢討（5 分鐘）

*（四人於 Part 3 整合前討論確認；整合後若有不同，再補一行。）*

1. **今天合作上哪裡做得好？**

   > 開工前先講好每個人的介面（收什麼、回傳什麼），讓 `models.py` 和 `app.py` 可以分頭做再接起來；每個框都由非作者講解。

2. **哪裡困難或卡卡的？**

   > Tiffany 和 Shen 都要改 `app.py` 的 `render_claim()`，整合時是需要一起看的地方。Hank 先寫的測試讓需求比較清楚。

3. **誰最少機會參與？下次怎麼改善？**（有沒有只有一個人能講解的框？打算怎麼處理？）

   > 四個人都有負責的程式或測試，也都講解了不是自己寫的區塊。若整合後發現有人參與不足，下次安排配對。

4. **Merge day 我們要改變的一件事：**

   > 先整理每個 PR 的測試結果和可能衝突，避免當天才發現設定或 README 不完整。

5. **發現的阻礙，以及誰負責後續：**

   > Issue #22、#24 不在這次切片處理，留在 backlog。若整合中發現其他問題，當場指派組員與期限。

---

## 快速檢查（給我們自己，不評分）

☐ 四個人都出席了
☐ 四個人都做了一塊，而且每塊都由不是作者的人講解過
☐ 我們有一句共識，說明工具在做什麼
☐ 各塊接起來了，新切片能跑（就算有些部分是假的）
☐ PR 由 steward review、至少一則真正的留言，並已合併
☐ 這份文件存成 `docs/walking_skeleton.md`，`DECISIONS.md` 也加了那一行
