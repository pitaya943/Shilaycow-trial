# Brief: priority-filter

## Goal

使用者列出待辦時可以只看某一個優先順序的(例如只看 `high`),其他照舊:順序仍是新增的順序,不帶篩選時看到的和現在一樣。

## Out of scope

- 依優先順序排序。
- 一次篩選多個優先順序(例如 `high` 或 `normal`)。
- 修改已存在待辦的優先順序。
- 分頁或筆數上限。

## Scenarios

### S-1 只列出某個優先順序的(todos,新增)

- Given 有 `low`、`normal`、`high` 各兩個的待辦,依序交錯新增
- When 使用者列出優先順序為 `high` 的待辦
- Then 只看到那兩個 `high`,依新增的順序,各自帶著編號、標題、是否完成、優先順序;`low` 與 `normal` 各自篩選時也一樣

### S-2 沒有符合的時候是空的列表(todos,新增)

- Given 有幾個待辦,沒有一個是 `low`
- When 使用者列出優先順序為 `low` 的待辦
- Then 得到 200 與一個空的列表

### S-3 不合法的優先順序被拒絕(todos,新增)

- Given 服務正在執行
- When 使用者以 `urgent`、`High`、` high`(前面有空白)或空字串篩選
- Then 得到 422,說明和新增時一樣:`priority must be one of: low, normal, high`

### S-4 和「只列出逾期的」一起用(todos,新增)

- Given 有逾期的 `high`、逾期的 `low`、還沒到期的 `high`
- When 使用者同時要求逾期的與優先順序 `high`
- Then 只看到逾期的那個 `high`

### S-5 不帶篩選時和現在一樣(todos,不變)

- Given 有幾個不同優先順序的待辦
- When 使用者列出待辦、或只列出逾期的,都不帶優先順序
- Then 結果和這次改動之前一樣:依新增順序的全部(或全部逾期的)

### S-6 舊資料檔的待辦算 `normal`(todos,不變)

- Given 一個加入優先順序之前的版本寫入的資料檔
- When 用目前的版本以它啟動,列出優先順序為 `normal` 的待辦
- Then 看到舊檔裡的每一個待辦

## How to try it

1. `git clone https://github.com/pitaya943/Shilaycow-trial && cd Shilaycow-trial && git checkout task/priority-filter && pip install -r requirements.txt`
2. `TODO_DB=/tmp/pf.db python -m uvicorn todo_api.app:create_app --factory --port 8765`
3. 另一個終端機新增三個:`curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title":"a","priority":"high"}'`,再以 `low`、`high` 各新增一個(標題 `b`、`c`)。
4. `curl 'localhost:8765/todos?priority=high'` → 只有 `a` 和 `c`;`curl 'localhost:8765/todos?priority=normal'` → `[]`。
5. `curl -i 'localhost:8765/todos?priority=High'` → 422,`priority must be one of: low, normal, high`。
6. `curl localhost:8765/todos` → 三個都在,依新增順序。

## Critical areas

None.

## Assumptions

- 優先順序的值和新增時一樣嚴格:只接受小寫的 `low`/`normal`/`high`,不去空白、不轉大小寫;其他的(包括空字串)回 422,不回空列表。
- 同一個請求給了兩次優先順序(`?priority=low&priority=high`)時回 422,說明一次只能篩一個;不取第一個或最後一個。
- 和 `overdue` 同時給時兩個條件都要成立。
- 結果的順序和現在的列表一樣,依新增順序;沒有分頁,符合的全部回傳。
- 從舊資料檔升級上來的待辦是 `normal`(priority 任務已經這樣規定),所以會出現在 `normal` 的篩選裡。
