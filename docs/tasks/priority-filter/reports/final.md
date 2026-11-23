# Report: priority-filter

依我自己的檢查,簡述的八個情境都做到了;T-01(high)已有獨立的 PASS,整個任務的獨立判定會貼在進 `main` 的 PR 上。

## What was done

列出待辦時可以用 `?priority=low|normal|high` 只看某一個優先順序的,也可以和 `?overdue=true` 一起用;不合法的值與重複給的值回 422。允許的優先順序現在只定義在 `todo_api/store.py` 的 `PRIORITIES` 一處,新增、篩選與新資料檔的 `CHECK` 都讀它(併入 `later` #20)。列表的查詢參數都要在 `LIST_QUERY_VALUES` 宣告允許的值,`tests/test_query_params.py` 守著(pitfall「簡述沒說的邊界」的 correct)。`try-todo-api`、README 與 `docs/spec/` 都已更新。對 `main` 的 blast radius:同樣 17 個一般與極端的請求送給 `main` 與這個分支,只有帶 `priority` 的 2 個不同([`evidence/blast-radius.txt`](../evidence/blast-radius.txt))。

## How to try it

以下每一步都在 `2bfa469` 的全新 clone 上跑過,輸出在 [`evidence/report-try.txt`](../evidence/report-try.txt)。

1. `git clone https://github.com/pitaya943/Shilaycow-trial && cd Shilaycow-trial && git checkout task/priority-filter && pip install -r requirements.txt`
2. `TODO_DB=/tmp/pf.db python -m uvicorn todo_api.app:create_app --factory --port 8765`(`/tmp/pf.db` 不存在時是空的列表)
3. 另一個終端機:
   - `curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title":"a","priority":"high"}'` → `{"id":1,"title":"a","done":false,"priority":"high"}`
   - 同樣以 `{"title":"b","priority":"low"}`、`{"title":"c","priority":"high"}` 再新增兩個
4. `curl 'localhost:8765/todos?priority=high'` → 只有 `a`(id 1)和 `c`(id 3);`curl 'localhost:8765/todos?priority=normal'` → `[]`
5. `curl -i 'localhost:8765/todos?priority=High'` → `422`,`{"detail":"priority must be one of: low, normal, high"}`
6. `curl -i 'localhost:8765/todos?priority=low&priority=high'` → `422`,`{"detail":"priority may be given only once"}`
7. `curl localhost:8765/todos` → 三個都在,依新增順序
8. 停掉服務。在 `todo_api/app.py` 的 `def list_todos(` 加一個參數 `tag: str | None = None`,跑 `python -m pytest -q`:`test_every_list_query_parameter_declares_its_values[tag]` 失敗並說 `GET /todos?tag= has no declared values`;`git checkout todo_api/app.py` 之後 `94 passed`

值得試、測試沒有涵蓋的:

- `curl 'localhost:8765/todos?Priority=high'`(參數名大寫)→ 三個全部回來,沒有篩選也沒有錯誤:FastAPI 不認得的參數名一律忽略。跑過。
- `curl 'localhost:8765/todos?priority=high&overdue=TRUE'` → `[]`(`overdue` 不分大小寫,三個都沒有到期日)。跑過。
- 已存在的資料檔裡新增一個之後才加進 `PRIORITIES` 的值:`not run`(T-01 的判定 Findings 1 跑過,得到 500)。

## Decisions I made

來自 [`trail.tsv`](../trail.tsv):

- #23 的 Retro 併入 pitfall 檔,其餘 Retro 已引用而跳過。
- correct 只做「簡述沒說的邊界」(S-7);另外兩條不做(Owner 決定)。`later` #20 併入為 S-8(Owner 決定)。
- 兩張票依序:T-02 要讀 T-01 的那一份允許值,兩張都改 `app.py`。
- T-01 採「store 的一個 tuple 產生 `CHECK`」,不採 Enum/`Literal`:後者會換掉 422 那一句訊息。
- 重複給優先順序的訊息定為 `priority may be given only once`(簡述只說要說明)。
- T-02 從 T-01 的 head 開始建置,不等 T-01 的判定。
- T-02 沒有單獨驗收,留給最終驗收(medium)。
- builder T-01:`CHECK` 以單引號直接包值、不跳脫;不另寫「只在一處」的 pytest,由票的檢查腳本負責;用字串串接以支援 3.12 以前的 Python。
- builder T-02:在路由裡用 Python 篩選,不改 store;`priority` 宣告成 list 才看得到重複,重複先於值的檢查;`LIST_QUERY_VALUES["overdue"]` 列出 FastAPI 原本接受的所有寫法,讓不帶篩選的回應和 `main` 一樣;防護測試不試大小寫變體;S-6 的測試先加一個 `high` 才篩;沒有改 `docs/spec/`(由 Chief 在收尾時改)。

## Not done or in doubt

- **在舊資料檔新增新加的允許值會得到 500**,不是 422([#30 判定 Findings 1](https://github.com/pitaya943/Shilaycow-trial/pull/30#issuecomment-7098886056))。簡述把讓舊檔接受新值列為 Out of scope;spec 的 Rules 記下了這一點,待 Owner 決定。
- **「只在一處」沒有 pytest 守著**,只有 `tickets/T-01-check.py`(同一判定 Findings 2)。
- 允許值含單引號,或 `PRIORITIES` 是空的時,服務起不來(同一判定 §5 `unspecified`)。
- 參數名寫錯(例如 `Priority`)時靜默忽略、回全部(上面「值得試」第一項);簡述沒有規範。
- T-02 只由 Chief 重跑過,獨立的判定在最終驗收。

## Verification

獨立的判定會以留言貼在這個任務進 `main` 的 PR 上。

## Scenarios

| 情境 | 結果 | 證據 |
|---|---|---|
| S-1 只列出某個優先順序的 | 做到 | `tests/test_priority_filter.py::test_only_that_priority_in_insertion_order`,[#31 Ready](https://github.com/pitaya943/Shilaycow-trial/pull/31#issuecomment-7098846004);How to try it 第 4 步 |
| S-2 沒有符合的時候是空的列表 | 做到 | `test_no_match_is_an_empty_list`;第 4 步 |
| S-3 不合法的優先順序被拒絕 | 做到 | `test_an_unknown_priority_is_refused_with_the_create_message`、`test_priority_given_twice_is_refused`;第 5、6 步 |
| S-4 和「只列出逾期的」一起用 | 做到 | `test_with_overdue_both_must_hold` |
| S-5 不帶篩選時和現在一樣 | 做到 | `tickets/T-02-check.py` 與 `origin/main` 比對;破壞時 7 個既有測試失敗([#31 Ready](https://github.com/pitaya943/Shilaycow-trial/pull/31#issuecomment-7098846004)) |
| S-6 舊資料檔的待辦算 `normal` | 做到 | `test_an_old_data_file_lists_every_todo_under_normal` |
| S-7 列表的查詢參數都要宣告允許的值 | 做到 | `tests/test_query_params.py`,兩種破壞都失敗([#31 Ready](https://github.com/pitaya943/Shilaycow-trial/pull/31#issuecomment-7098846004));第 8 步 |
| S-8 優先順序的允許值只在一個地方 | 做到 | `tickets/T-01-check.py`、`tickets/T-02-check.py`;[#30 PASS](https://github.com/pitaya943/Shilaycow-trial/pull/30#issuecomment-7098886056) |

## Tickets

| 票 | 最後的等級 | 設定它的訊號 | 驗收 |
|---|---|---|---|
| [T-01](../tickets/T-01.md)([#30](https://github.com/pitaya943/Shilaycow-trial/pull/30)) | high | 改資料檔建立時寫下的 `CHECK`;verifier 維持 high | 單獨一次:[PASS](https://github.com/pitaya943/Shilaycow-trial/pull/30#issuecomment-7098886056),7 種破壞都被抓到 |
| [T-02](../tickets/T-02.md)([#31](https://github.com/pitaya943/Shilaycow-trial/pull/31)) | medium | 改「列出待辦」的 HTTP 介面 | 最終驗收 |
