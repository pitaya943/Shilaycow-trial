# 第二次試跑筆記:due-dates

Chief session:`session_01LCMZdonUvBPxzrM3oHGbWn`,以 GitHub 帳號 `bullet-bots` 執行(`get_me` 確認,與 config 的 `bot` 相同)。開始於 2026-11-21T18:43:30Z。

這份檔案分兩段寫成。**驗證之前**的部分(第 1、2、3、5 節,與第 4、6 節的前半)在這個分支上。**驗證之後**的補記(裁決內容、各 session 的花費、總時間)不在 `task/due-dates` 上,因為 `go` 規定裁決後不能再推任何東西;補記在分支 `notes/due-dates-trial` 的同一個檔案,也貼在 tracking issue #5。這個安排本身就是下面「go」的第 1 個問題。

## 1. `go` 留給我判斷的事,我怎麼選

| 事情 | 我的選擇 | 為什麼(一行) |
|---|---|---|
| 要不要設計 | 不寫 `design.md`,不用 `design` | 改動是兩個檔案約 40 行;需要定的五件事(欄位名、查詢參數、無到期日時的形狀、今天怎麼取、格式多嚴)直接記在 `trail.tsv` |
| 怎麼切 | 不切,沒有票,不用 `plan` | 四個新情境共用同一個欄位,切開只會多出交接 |
| 自己做還是用 builder | Chief 自己做,0 個 builder | 讀懂現有程式碼之後,寫的成本比寫一張票再等一個 subagent 低;也省 session |
| 合併前要不要單票驗證 | 不做 | 沒有票;最終驗證看的就是全部改動。謹慎程度「一般」也不要求 |
| 最終驗證 | 做,一個新 session(`create_session`) | `go` 的邊界,不是我能選的 |
| `blast-radius` | 我沒有獨立跑;只做了一件相當的事:比對新舊實跑紀錄的前 47 行完全相同 | 謹慎程度是一般;`verify` 自己會對整個分支跑 |
| 用了的 skill | `go`、`principles`、`prove`、`trail`、`drive-todo-api`、`retro`、`report`;`verify` 交給驗證者 | |
| 讀了但沒用的 | `status`(沒有需要回報狀態的時刻)、`blast-radius`、`correct`(見 retro 一節) | |
| 完全沒開的 | `sharpen`(brief 已核准)、`design`、`plan`、`drive`(專案 skill 已存在)、`how`、`why`、`setup` | 只讀了 `go` 裡對它們的一句描述就決定不需要 |

其他我自己定、`go` 沒有說的事:

- 做法順序:一次一個情境,先寫測試、看它失敗、再寫最少的程式碼;每一步一個 commit,直接 commit 在 `task/due-dates` 上(沒有開 `work/...` 分支,因為沒有 builder 也沒有要合併的東西)。
- 因為沒有 builder,就沒有 `Ready.` 留言。我以 Chief 的身分在 pull request 上貼了一則 `Ready.` 留言(含 `Session:`),讓驗證者的第 1 步與 `go` 最後一段的檢查有東西可以比。這是猜的(見下)。
- 這次試跑的說明允許我請驗證者結束時用 `send_message` 給 `@parent` 一行。我有這樣做;skill 本身沒有這個機制。

## 2. 每個用過的 skill

### go

做了什麼:確認帳號(`get_me` → `bullet-bots`),讀 config、brief、pitfalls,開 tracking issue #5,自己做完,retro、report、開 pull request、開新 session 驗證。

不清楚、缺漏或互相矛盾的地方:

1. **「裁決後不能推」和「收尾要寫的東西」互相卡住。** `go` 說:「push nothing after the verdict: the commit the owner merges is the commit that was judged」,又說收尾的順序是「Record what is worth keeping (`retro`), write the report (`report`), open the pull request into `main` with the report as its description, then have it verified. Give every finding in the verdict a home: fixed, ticketed, or listed for the owner in the report.」
   - `report` 要求報告檔有一節「**驗證結果**: what the independent verifier ran and found」,但報告檔必須在驗證前就 commit。
   - 「listed for the owner in the report」:裁決出來之後要把 finding 寫進報告,就得再推一次,頭就不是被驗證的那個 commit 了。「fixed」也一樣,而且沒有說修完要不要重新驗證(`verify` 說「a new head needs a new verdict」,所以答案應該是要,但 `go` 沒有把這個迴圈寫出來,也沒說它算不算在 `fix_rounds` 裡)。
   - `retro` 的輸入包含「the findings attached to PASS verdicts」,但 `go` 把 retro 排在驗證之前。
   - 我怎麼做:報告檔的「驗證結果」一節寫成「請看 pull request 上的裁決留言」;裁決出來後只改 **pull request 的描述**(那不是 push)。finding 一律列在描述裡給 Owner,不修(除非是 FAIL)。這份筆記的驗證後補記放在另一個分支。這些都是猜的。
2. **Chief 自己做的時候,沒有 `Ready.` 留言。** `go`:「Before relying on a PASS, check that its `Session:` line differs from the `Session:` of every Ready comment on that pull request.」`roles/verifier.md` 第 1 步也是比 Ready 留言。`go` 明說可以「do it yourself」,卻沒有說自己做的人要不要貼 `Ready.`、要不要留 `Session:`。不貼的話,這個檢查永遠成立,等於沒檢查。我猜應該貼,就貼了。
3. **沒有票的時候,驗證者該拿到什麼。** `roles/verifier.md`「You are given」:「the ticket's path (for a whole branch: the brief and every ticket) and the task's slug」。沒有票時這一項是空的;而且「一個 pull request」的情況照字面只給票的路徑,不給 brief。`merge_unit: task` 時最後那個 pull request 同時是「a pull request」也是「a whole task branch」,兩種給法哪一個適用沒有說。我給了 pull request、brief 的路徑、slug,並明說「這個任務沒有票」。
4. **「and nothing about the work itself」和實際需要之間的縫。** 驗證者需要知道 commit 用誰的名字嗎(它不 commit,不需要)、需要知道試跑的回報方式嗎(skill 沒有)。我另外加了一句「結束時傳一行給 @parent」,這是試跑說明允許的,不是 skill 給的。
5. **等別的 session 的方法沒有寫。** 「Nothing wakes you when a session you started finishes; read what it posted when you next run.」沒有說「next run」由誰觸發。在這個環境裡 Chief 是一個 session,停下來就不會再跑。
6. **Chief 自己 commit 時用誰的名字。** 只有 `roles/builder.md` 提到「the name and email to commit as」。`go` 檢查了 GitHub 帳號,但沒有提 git 的作者;這次是試跑說明告訴我的。
7. **預算寫在兩個地方。** `go` 說「the hours or sessions in the config」,brief 也有一節「預算」。這次兩邊相同;不同時聽誰的沒有說。tracking issue「first line gives the level and the budget」也沒說抄哪一個。
8. **config 在 default branch 上,但 session 只 checkout 了任務分支。** 「The level is `merge_unit` in the config on the default branch」。`git show origin/main:.shilaycow/config.yml` 一開始失敗(`fatal: invalid object name 'origin/main'`),要先 `git fetch origin main`。工作分支上也有一份 `.shilaycow/config.yml`,內容相同;兩份不同時 `go` 說了聽 main 的,但一個新人很容易直接讀到工作目錄那份。
9. **`correct` 沒有出現在 `go` 裡。** `retro` 說次數到 2 的「are for `correct`」,`correct` 要自己的 pull request;`go` 的收尾沒有提它,也沒說它算不算這個任務的一部分、`merge_unit: task` 時那個額外的 pull request 可不可以開。我沒做,寫進報告給 Owner。
10. tracking issue 的「a line each time something lands or waits」:自己做的時候沒有東西「lands」。我在開 pull request、開始驗證、結束時各留一行。

需要猜的:上面 1、2、3、9。

### principles

做了什麼:寫程式前讀一遍;影響了兩個選擇:無到期日時不輸出鍵(最小改動、舊測試不動),以及格式規則只放在一個地方(route)。

問題:沒有不清楚的句子。一個觀察:三個 route 各寫一次 `response_model_exclude_none=True`,算不算「If the same workaround appears twice, the design is wrong」?我判斷不算(它是宣告,不是繞路),但這句話沒有給界線。

### prove

做了什麼:四個新情境都是先寫測試、看它失敗、再寫程式碼。`drive.sh` 的改動用實跑代替測試。

問題:

1. **「看它失敗」沒有說失敗的原因要對。**「you wrote it first and watched it fail for the missing behaviour」有說 for the missing behaviour,但我第一次跑 S-1 的測試,失敗的是 fixture(`TypeError: create_app() got an unexpected keyword argument 'today'`),不是行為。我先加了空的 `today` 參數,才看到真正的失敗(回應少了 `due_date`)。skill 沒有提醒「因為介面還不存在而失敗」不算數;上一次試跑的驗證者自己加了這條標準(「assertion failures about the missing behaviour, not import or collection errors」)。
2. **「沒有改變」這種情境怎麼證明,沒有說。** S-5(原本的功能不變)沒有新行為可以先紅後綠。我的做法:先用最直接的方式實作 S-1(回應固定帶 `due_date: null`),看到舊的 10 個測試全部失敗,再改成省略該鍵讓它們通過。這等於「把行為弄壞、看舊測試失敗、再復原」,符合 skill 的第二種方式,但是我自己想到要這樣安排的。
3. **測試為了注入而改介面,算不算「reaches inside」?** `create_app(today=...)` 是為了測試才加的參數。skill 的三種壞測試裡沒有談到「時間」這種測試搆不到的輸入該怎麼辦。

需要猜的:S-5 的證明方式。

### trail

做了什麼:9 列,欄位照上一個任務的 `trail.tsv`。

問題:

1. 「The exact columns are yours」,但上一個任務的檔案已經有七欄,其中 `result` 欄每一列都是 `open`,skill 沒有解釋它是什麼、誰會把它改成別的值。我照抄 `open`,不知道意思。
2. 「Write the row when you decide, not at the end.」我實際上是做完程式碼後一次補的(時間戳是回推的)。一個人自己做小任務時,邊做邊寫 TSV 很打斷;skill 沒有給比較輕的做法。
3. evidence 欄要「a pointer (commit, pull request, `file:line`)」:寫的當下 commit 還沒推、行號之後還會變。我補寫時修過一次行號。

### drive-todo-api(專案 skill)與 drive

做了什麼:沒有重新產生;在 `drive.sh` 加了四個到期日情境,在 `SKILL.md` 的表加了四列。

問題:

1. `SKILL.md` 說「When a ticket adds an endpoint, add its `call` lines to `drive.sh` and its row to the table above.」這次不是新 endpoint 而是新欄位與查詢參數,也沒有票;照精神做了。
2. 表裡的情境編號(S-1 到 S-5)是上一個任務的 brief 的編號,和這個任務的 S-1 到 S-5 撞號。我在新列前加了「due-dates」字樣並補一句說明。**專案 skill 用任務內的情境編號當標籤,第二個任務一來就會混淆。**
3. brief 的「怎麼試」說「依序做 S-1 到 S-4,再跑一次原本的五個情境」。我的 `drive.sh` 順序相反(先原本五個,再新的),而且 S-3 排在 S-4 之後、中間重啟服務:因為 S-3 的 Given 是「有四筆待辦」,而且 S-1 的 2026-12-01 過了那天也會變逾期。順序與 brief 字面不同,記在 trail。
4. 我改 `drive.sh` 時引進了一個缺陷(pipe 造成 subshell,服務沒關、占用埠時 exit 0 且紀錄為空),連跑第二次才發現。這和上一個任務 pitfalls 的第一條是同一類。**我開工前讀過那條 pitfall,還是犯了**:它寫的避免方法是三個具體檢查,我的改法剛好在不同的地方破壞了同一個保證。

### retro

做了什麼:讀了 issue #1 上的留言(沒有 Owner 在合併後的留言),把 `drive.sh` 那一條的次數加到 2 並改寫成涵蓋兩次的原因。

問題:

1. 排在驗證之前,卻要讀驗證的 finding(見 go 第 1 點)。
2. 「What the owner found wrong after merging earlier tasks (their comments on finished tracking issues)」:issue #1 還是 open 的,而且上一個任務的 `Finished:` 留言之後沒有任何留言。沒有留言可能表示沒問題,也可能表示 Owner 不知道要留在那裡;分不出來。
3. 「If the cause is an unclear instruction in a skill rather than something about this project, report that separately」:沒有說報到哪裡。這次有試跑筆記可以放;正常執行時沒有。
4. 次數到 2 之後「those are for `correct`」,但誰來跑、什麼時候跑,`retro` 和 `go` 都沒說(見 go 第 9 點)。

### report

做了什麼:寫了 `reports/final.md`,當作 pull request 的描述。

問題:

1. 「驗證結果」一節在寫的時候還沒有內容(見 go 第 1 點)。
2. 輸入列了 `design.md`、`plan.md`、Ready 留言、CI 結果;這次四樣都沒有(Ready 留言是我寫完報告才貼的)。skill 沒有說缺的時候怎麼辦;我照有的寫。
3. 「whose first sentence says whether every scenario is met」:驗證前我只能說「我這邊看都做到了」。第一句話的依據是誰的判斷,沒有說。
4. 「Every claim links to a pull request, commit, verdict or trail row」:寫報告時 pull request 還不存在(描述就是報告本身),所以檔案裡沒辦法連到它。

### verify(交給驗證者;我只讀)

我讀它是為了知道會被怎麼檢查。讀的時候注意到:

1. 「For a whole task branch, also run `blast-radius` against `main`.」`merge_unit: task` 的最終 pull request 算不算「a whole task branch」沒有說(見 go 第 3 點)。
2. 第 4 項「for each scenario shown by a test, you broke the behaviour in a throwaway copy and the test failed」:S-5 的測試是上一個任務的 10 個,要不要每個都弄壞一次,沒有說。

## 3. 每個情境怎麼證明

| 情境 | 測試 | 先寫還是後寫 | 怎麼看到它失敗 |
|---|---|---|---|
| S-1 | `test_create_with_due_date_returns_it` | 先(b7e4d76 只有測試與空的 `today` 參數) | `AssertionError`:回應少了 `{'due_date': '2026-12-01'}`,`1 failed, 10 passed`。在這之前第一次跑是 fixture 的 `TypeError`,那次不算 |
| S-2 | `test_create_without_due_date_has_none_and_is_otherwise_as_before` | 先(寫在 S-1 的最直接實作之後、修正之前) | 當時回應帶 `due_date: null`:`11 failed, 1 passed`(這一個加上舊的 10 個) |
| S-3 | `test_overdue_lists_only_unfinished_todos_due_before_today`、`test_a_todo_due_today_is_not_overdue` | 先 | `2 failed, 12 passed`(`overdue=true` 被忽略,回了全部)。寫完後另外做了兩個突變:`<` 改成 `<=` → 只有「今天到期」那個失敗;拿掉 `not todo.done` → 只有主測試失敗 |
| S-4 | `test_malformed_due_date_is_rejected_and_list_unchanged`(7 個值) | 先(d288164 只有測試) | `7 failed, 14 passed` |
| S-5 | 上一個任務的 10 個測試,未更動 | 早就存在 | 在 S-1 的最直接實作下 10 個全部失敗(回應多了 `due_date: null`),改成省略該鍵後通過 |

實跑(driven check):`docs/tasks/due-dates/evidence/drive.txt`,由 `drive.sh` 在 commit 2f1270f 上產生,涵蓋原本五個情境與 S-1 到 S-4。前 47 行與上一個任務的 `T-02-drive.txt` 除第一行外相同(`diff` 只差檔尾一個空行)。

`drive.sh` 自己的兩個改動沒有測試,以實跑代替:連跑兩次都 exit 0 且之後 `pgrep -f "uvicorn todo_api"` 沒有輸出;先占住 8765 再跑,印出 `something is already answering…` 且 exit 1。修之前的樣子(第二次跑印出同一句話但 exit 0、紀錄是空的)我是實際撞到的,不是事後重現。

一個不乾淨的地方:S-3 的實作 commit 我 amend 過。第一版 import 就失敗(`TypeError: 'function' object is not subscriptable`,類別裡 `list` 方法遮住了內建的 `list`),我是在下一步跑測試時才發現,然後 amend 掉。所以「commit 之前先跑整個套件」這件事我有一次沒做到。

## 4. 最終驗證

驗證之前:由一個新 session 進行(細節與裁決見補記)。我給它的東西只有 `roles/verifier.md` 列的:pull request、brief 的路徑、slug、「沒有票」、GitHub 用哪些工具;外加試跑允許的「結束時傳一行給 @parent」。

(裁決、每個 finding、第 6 項檢查的 finding 是具體還是模糊、我怎麼處理:在補記裡。)

## 5. 這個環境裡做不到的事

- `git show origin/main:.shilaycow/config.yml` → `fatal: invalid object name 'origin/main'`。session 只帶了 `task/due-dates`;`git fetch origin main` 之後可以。
- 倉庫沒有 CI;「CI results」這個輸入不存在。
- 沒有東西會在驗證者結束時叫醒 Chief;靠試跑允許的 `@parent` 訊息。
- (驗證階段遇到的,寫在補記。)

## 6. 數字

- GitHub 帳號:`bullet-bots`。
- 到開 pull request 為止:只有 Chief 一個 session,0 個 subagent,0 個 builder。
- 從開始到程式碼與實跑紀錄完成約 3 分鐘(18:43:30Z → 18:46:37Z),到報告與這份筆記寫完約 7 分鐘。
- (驗證者 session 的編號、時間與花費、總時間:在補記裡。)
