# Brief: priority

## Goal

新增待辦時可以給它一個優先順序(低、一般、高),之後列出待辦時看得到每一項的優先順序。升級前已經存在的待辦照常可用,優先順序是「一般」。

## Out of scope

- 改變已存在待辦的優先順序(沒有編輯待辦的功能,這次也不加)。
- 依優先順序排序或篩選列表;列表仍照新增的順序。
- 數字型或自訂的優先順序等級。

## Scenarios

### S-1 新增時指定優先順序

- Given 服務正在執行
- When 使用者新增一個標題為「繳房租」、優先順序為 `high` 的待辦
- Then 回應裡這個待辦的優先順序是 `high`,而且列出待辦時它的優先順序也是 `high`

### S-2 沒有指定時是一般

- Given 服務正在執行
- When 使用者新增一個待辦,沒有給優先順序
- Then 回應與列表裡它的優先順序是 `normal`

### S-3 不認得的優先順序被拒絕

- Given 服務正在執行
- When 使用者新增待辦時給的優先順序是 `urgent`
- Then 服務回 422 並說明可用的值是 `low`、`normal`、`high`,而且列表裡沒有多出這個待辦

### S-4 重啟後優先順序還在

- Given 使用者新增了一個優先順序為 `low` 的待辦
- When 服務重新啟動
- Then 列出待辦時它的優先順序仍是 `low`

### S-5 升級前的資料檔照常可用

- Given 一個由這次改動之前的服務寫入、裡面有兩個待辦(其中一個已完成、一個有到期日)的資料檔
- When 用新版的服務以這個資料檔啟動
- Then 服務正常啟動,兩個待辦的標題、完成狀態、到期日都和之前一樣,優先順序都是 `normal`

### S-6 標為完成與逾期篩選保留優先順序

- Given 一個優先順序為 `high`、到期日已過的待辦
- When 使用者列出逾期的待辦,然後把它標為完成
- Then 逾期列表與標為完成的回應裡,它的優先順序都是 `high`

## How to try it

1. `git clone https://github.com/pitaya943/Shilaycow-trial && cd Shilaycow-trial && git checkout task/priority && pip install -r requirements.txt`
2. 先用 `main` 的版本啟動一次並新增一個待辦:`git checkout main`,`TODO_DB=/tmp/p.db python -m uvicorn todo_api.app:create_app --factory --port 8765`,另一個終端機 `curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title":"舊的"}'`,然後停掉服務。
3. `git checkout task/priority`,用同一個 `TODO_DB=/tmp/p.db` 再啟動。
4. `curl localhost:8765/todos`:「舊的」還在,`priority` 是 `normal`。
5. `curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title":"繳房租","priority":"high"}'`,再 `curl localhost:8765/todos`:看到 `high`。
6. `-d '{"title":"x","priority":"urgent"}'`:得到 422,列表沒有多出來。

## Critical areas

- 資料檔的格式(`todo_api/store.py` 的資料表與開檔檢查):改錯會讓既有的資料檔打不開或被改壞。

## Assumptions

- 可用的值只有小寫的 `low`、`normal`、`high`;`High`、`"  high "`、空字串都當作不認得,回 422(不自動轉換)。
- 明確給 `"priority": null` 和沒給一樣,是 `normal`。
- 回應裡一律有 `priority` 欄位(不像 `due_date` 沒有時省略),因為每個待辦都有一個值。
- 升級前的資料檔在第一次以新版啟動時就地補上優先順序,舊待辦都是 `normal`;之後舊版服務能不能再開這個檔不保證(不支援降級)。
- 由別的程式寫入、或欄位不對的檔案,照舊拒絕啟動,不嘗試升級。
- 同時多人新增:沿用 SQLite 本身的鎖,不另外處理。
