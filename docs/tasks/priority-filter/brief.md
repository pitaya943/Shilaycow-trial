# Brief: priority-filter

## Goal

使用者列出待辦時可以只看某一個優先順序的(例如只看 `high`),其他照舊:順序仍是新增的順序,不帶篩選時看到的和現在一樣。

## Out of scope

- 依優先順序排序。
- 一次篩選多個優先順序(例如 `high` 或 `normal`)。
- 修改已存在待辦的優先順序。
- 分頁或筆數上限。
- 新增一個優先順序的值;S-8 只讓將來新增時改一個地方就夠,已存在資料檔裡的檢查不跟著改。

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
- When 使用者在同一個請求給兩次優先順序(`low` 與 `high`)
- Then 得到 422,說明一次只能篩選一個優先順序

### S-4 和「只列出逾期的」一起用(todos,新增)

- Given 有逾期的 `high`、逾期的 `low`、還沒到期的 `high`
- When 使用者同時要求逾期的與優先順序 `high`
- Then 只看到逾期的那個 `high`

### S-5 不帶篩選時和現在一樣(todos,不變)

- Given 一組固定的待辦:三種優先順序、有完成的、有逾期的
- When 使用者列出待辦、和只列出逾期的,都不帶優先順序,在這次改動之前與之後各做一次
- Then 兩次的回應逐筆相同,依新增順序

### S-6 舊資料檔的待辦算 `normal`(todos,不變)

- Given 一個加入優先順序之前的版本寫入的資料檔
- When 用目前的版本以它啟動,列出優先順序為 `normal` 的待辦
- Then 看到舊檔裡的每一個待辦

### S-7 列表的查詢參數都要宣告允許的值(`shilaycow-correct`,pitfall「簡述沒說、使用者實際會碰到的邊界沒有人決定」)

- Given 開發者在列出待辦的請求加了一個查詢參數,沒有宣告它允許哪些值
- When 跑測試
- Then 有一個測試失敗,訊息指出那個參數;把優先順序篩選對允許值的檢查拿掉,同一個測試也會失敗

這是往前的防護:它擋的是新的查詢參數,擋不住這條 pitfall 過去的 #21、#22 那幾類,所以條目留著、不移到 `## Guarded`。

### S-8 優先順序的允許值只在一個地方(`later` #20)

- Given 允許的優先順序只在一個地方定義,新增、篩選與新資料檔的檢查都從那裡讀
- When 開發者在一份複本裡只改那一個地方,加上 `urgent`,以全新的資料檔啟動
- Then 新增 `urgent` 的待辦得到 201(不是 500),以 `urgent` 篩選看得到它

## How to try it

1. `git clone https://github.com/pitaya943/Shilaycow-trial && cd Shilaycow-trial && git checkout task/priority-filter && pip install -r requirements.txt`
2. `TODO_DB=/tmp/pf.db python -m uvicorn todo_api.app:create_app --factory --port 8765`
3. 另一個終端機新增三個:`curl -X POST localhost:8765/todos -H 'content-type: application/json' -d '{"title":"a","priority":"high"}'`,再以 `low`、`high` 各新增一個(標題 `b`、`c`)。
4. `curl 'localhost:8765/todos?priority=high'` → 只有 `a` 和 `c`;`curl 'localhost:8765/todos?priority=normal'` → `[]`。
5. `curl -i 'localhost:8765/todos?priority=High'` → 422,`priority must be one of: low, normal, high`。
6. `curl -i 'localhost:8765/todos?priority=low&priority=high'` → 422。
7. `curl localhost:8765/todos` → 三個都在,依新增順序。
8. S-7:在列表的路由加一個參數 `tag: str | None = None`,跑 `python -m pytest -q`,看到一個測試失敗並指出 `tag`;拿掉後全過。

## Critical areas

None.

## Assumptions

- 優先順序的值和新增時一樣嚴格:只接受小寫的 `low`/`normal`/`high`,不去空白、不轉大小寫;其他的(包括空字串)回 422,不回空列表。
- 同一個請求給了兩次優先順序時回 422(S-3),不取第一個或最後一個。
- S-8 的「全新的資料檔」:已存在的資料檔在建立時就寫下了當時的允許值,改允許值不會改它們;要讓舊檔接受新值是另一個任務。
- 和 `overdue` 同時給時兩個條件都要成立。
- 結果的順序和現在的列表一樣,依新增順序;沒有分頁,符合的全部回傳。
- 從舊資料檔升級上來的待辦是 `normal`(priority 任務已經這樣規定),所以會出現在 `normal` 的篩選裡。
