# Final report: priority

依我自己的檢查,簡述的六個情境都做到了;唯一的保留是兩個簡述沒規範的邊界(見「Not done or in doubt」)。

## What was done

每個待辦現在帶一個優先順序(`low`/`normal`/`high`),新增時可以指定,沒指定就是 `normal`,所有回應都看得到它。不認得的值回 422 並列出可用的值。加入優先順序之前寫的資料檔,在第一次以新版啟動時就地補上欄位,舊待辦都是 `normal`。另外第一次寫了 `docs/spec/`,描述整個服務現在的行為。

## How to try it

1. `git clone https://github.com/pitaya943/Shilaycow-trial && cd Shilaycow-trial && pip install -r requirements.txt`
2. 先用舊版寫一個資料檔:`git checkout main`,`TODO_DB=/tmp/p.db python -m uvicorn todo_api.app:create_app --factory --port 8765`;另一個終端機 `curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title":"舊的"}'`;停掉服務。
3. `git checkout task/priority`,用同一個 `TODO_DB=/tmp/p.db` 再啟動。
4. `curl localhost:8765/todos` → `[{"id":1,"title":"舊的","done":false,"priority":"normal"}]`
5. `curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title":"繳房租","priority":"high"}'` → 201,`"priority":"high"`;再列出看得到它。
6. `-d '{"title":"x","priority":"urgent"}'` → 422,`priority must be one of: low, normal, high`,列表沒有多出來。

測試沒涵蓋、值得試的:
- 把資料檔設成唯讀(非 root 使用者)再啟動:舊格式的檔會拒絕啟動,新格式的照常。
- 升級後再用 `main` 的版本開同一個檔:會被拒絕(不支援降級)。
- `"priority": "High"` 或 `" high"`:422,不會被自動轉換。

## Decisions I made

- 舊檔就地 `ADD COLUMN`,不建新表再複製:只加一個有預設值的欄位,不重寫資料([trail](../trail.tsv),design 列)。
- 讀欄位與 `ALTER` 放在 `BEGIN IMMEDIATE`:兩個服務同時用舊檔啟動時都能成功(design 列;T-01 的 builder 把它寫成可重現的測試)。
- 切成 T-01(high,單獨驗收)與 T-02(medium,不單獨驗收,由最後的驗收一起判)。
- 不採用 #17 的第一份 PASS:它的 `Session:` 是 Chief 的,且那個 session 沒有 0.4 的 skill([#16](https://github.com/pitaya943/Shilaycow-trial/issues/16#issuecomment-7096042008))。
- 優先順序的請求欄位接受任何 JSON 值、由路由檢查,讓數字與布林也得到同一句列出三個值的訊息(T-02 builder,[Ready](https://github.com/pitaya943/Shilaycow-trial/pull/18#issuecomment-7096403331))。
- 第一次建立 `docs/spec/`,一個區域 `todos`。

## Not done or in doubt

- 一個本服務寫的、五個欄位名稱都對但 `priority` 型別不同(例如 INTEGER 存 7)的檔會被接受,列出 `priority=7`。開檔檢查只比欄位名稱,和以前一樣。`unspecified`([#17 判定](https://github.com/pitaya943/Shilaycow-trial/pull/17#issuecomment-7096327358))。
- 唯讀的舊格式資料檔會拒絕啟動(要寫入才能升級)。簡述沒規範。`unspecified`(同上)。
- `T-01-check.py` 需要 `origin/main` 這個 ref;只 clone 一個分支時要先 `git fetch origin main`。

## Verification

獨立的驗收判定會以留言貼在這個 PR 上。

## Scenarios

| 情境 | 結果 | 證據 |
|---|---|---|
| S-1 新增時指定優先順序 | 做到 | `tests/test_priority_http.py`;[T-02 Ready](https://github.com/pitaya943/Shilaycow-trial/pull/18#issuecomment-7096403331);`evidence/T-02-drive.txt` |
| S-2 沒有指定時是一般 | 做到 | 同上 |
| S-3 不認得的優先順序被拒絕 | 做到 | 同上;`T-02-check.py` 試了 `urgent`、`High`、` high`、空字串、`1` |
| S-4 重啟後優先順序還在 | 做到 | `tests/test_priority_store.py::test_a_priority_survives_a_reopen`;[#17 判定](https://github.com/pitaya943/Shilaycow-trial/pull/17#issuecomment-7096327358) |
| S-5 升級前的資料檔照常可用 | 做到 | `tests/test_priority_store.py::test_an_old_data_file_opens_with_its_todos_unchanged_and_normal`;#17 判定的實際操作 |
| S-6 標為完成與逾期篩選保留優先順序 | 做到 | `tests/test_priority_http.py`;`T-02-check.py` |

## Tickets

| 票 | 最後的風險 | 依據 | 驗收 |
|---|---|---|---|
| T-01 儲存層與舊檔升級 | high | 改資料檔的資料表與開檔檢查,在 Critical areas;驗收者維持 | [PASS 於 799e67f](https://github.com/pitaya943/Shilaycow-trial/pull/17#issuecomment-7096327358) |
| T-02 HTTP | medium | 改 HTTP 介面的請求與回應 | 沒有單獨驗收;由這個 PR 的驗收判 |
