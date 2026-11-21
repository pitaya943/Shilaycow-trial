# Shilaycow 第一次試跑:筆記(todo-api)

Chief 邊做邊寫。開始時間:2026-11-21T16:24Z。行動帳號:`bullet-bots`(`get_me` 回傳,與 config 的 `bot` 相符)。

## 各 skill 的紀錄

### go(Before part two)

- 做了什麼:用 GitHub MCP `get_me` 確認帳號是 `bullet-bots`;分支已存在所以沒有再建;開了追蹤 issue #1,第一行 `Run started. Budget: 2 hours, 10 sessions.`。
- 不清楚 / 缺漏:
  - 「Check which GitHub account you act as」沒說怎麼查。雲端 session 沒有 gh,我用 MCP `get_me`。另外 git 的 commit 身分(`user.name=Claude`)與 GitHub API 身分是兩回事,skill 沒有提;這次靠試跑說明裡的 `git -c user.name=...` 才對得上。
  - 「Create `task/<slug>` from `main` ..., commit the brief and design there」:Owner 選擇在 brief 之後就放手時,設計還不存在。這一句暗示設計在 part two 之前就要 commit,但 part two 的每一輪只有「Plan if there are no tickets yet」,沒有任何一步說「沒有設計時跑 design」。我猜:在開 issue 之後、plan 之前由 Chief 跑 `design`。
  - 「Budget: <budget>」沒說格式;我寫 `2 hours, 10 sessions`。
  - brief 檔案第一行仍是「狀態:草稿,等 Owner 核准」,但 Owner 已核准。sharpen/go 都沒說核准後誰把狀態改掉。builder 被告知「never change the brief」,Chief 沒被告知。我沒有動它(情境是 Owner 的),只記在這裡。
  - 「sessions」是否包含 subagent(builder)沒有定義。我保守地把 builder subagent 也算進 10 個裡。
  - 「time and sessions used since `Run started`」:session 數沒有任何地方可查,只能靠 Chief 自己每輪寫在追蹤 issue 上;若 Chief 重啟,只能從 issue 留言重建。
  - 「CI green」:這個倉庫沒有任何 workflow。skill 沒說沒有 CI 時怎麼辦。我猜:視為由驗證者自己跑 `test_command` 來滿足(已寫入 trail)。

### design

- 做了什麼:寫了 `design.md`(Frame、Interfaces、State owners、一條 Workflow;略過 Data flow、Notifications),兩個形狀取 A,最後有情境 → 測試對照表。
- 不清楚 / 缺漏:
  - 「every element in it points back to at least one scenario」:沒說怎麼標;我在每張表加一欄「對應情境」。
  - 「Inputs: The repository as it is (`how`, `why`)」:倉庫是空的,我沒有讀 `how` / `why` 兩個 skill。空倉庫時是否仍要跑,沒有說。
  - 設計裡定了 brief 沒說的行為(狀態碼、錯誤訊息、去空白、重複完成)。design 沒說這類「代替發問的假設」放哪裡;trail 說要記,所以記在 trail。
  - go 說「You coordinate; you do not build」,但 design / plan 都由 Chief 親自跑;「Never build or verify in your own context」是否包含寫設計,沒有明說。我當作不包含。

### plan

- 做了什麼:一個里程碑、兩張依序的票(T-01:S-1/S-2/S-4 + drive;T-02:S-3/S-5)。
- 不清楚 / 矛盾:
  - 「If the project has no `drive-<app>` skill yet, the first ticket creates it with `drive`.」與 drive 的「do not write a skill you could not run」/「you have used it once, start to finish」衝突:全新專案在第一張票時還沒有可以啟動的 app。我猜:把 drive 放在 T-01 的最後一步。
  - 票檔案的欄位名稱一半英文(`Status:`、`Milestone:`、`Depends on:`)一半中文(做什麼、對應的情境、會動到的區域)。「areas it will touch」沒說粒度;我寫到檔案路徑。
  - 「Size a ticket so one builder session can finish it」沒有可以量的標準;在 session 預算只有 10 的情況下,我把票切大一點(2 張而不是 3 張),留預算給驗證者與修正回合。plan 完全沒提要看預算。
  - `parallel_builders: 2` 在這個任務用不到(所有票共用同兩個檔案)。

### trail

- 做了什麼:建立 `trail.tsv`,設計與計畫階段共 8 列。
- 不清楚:`result` 欄在決定當下只能寫 `open`;「Append only」之下,之後要更新結果只能再加一列,會很囉嗦。`phase` 的允許值沒有 `retro`。

## 環境

- fastapi、uvicorn、pytest、httpx 都沒裝,`pip install` 成功(fastapi 0.165.0,Python 3.13)。
- 沒有 gh CLI(依規定也不使用);GitHub 操作全用 MCP。

## 帳目(持續更新)

| # | 種類 | 用途 | 開始 | 約略耗時 |
|---|---|---|---|---|
| 1 | session | Chief | 16:24Z | — |
