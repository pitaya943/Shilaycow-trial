# Brief: title-limit(草稿,尚未核准)

## Goal

新增待辦時,標題最多 200 個字;超過就拒絕並說明上限。已經存在、比 200 字長的待辦照常可以列出與標為完成。

## Out of scope

- 截斷過長的標題(一律拒絕,不自動截短)。
- 修改已存在的長標題,或在啟動時檢查、清理資料檔裡的舊資料。
- 到期日、優先順序以外的新欄位。

## Scenarios

### S-1 剛好 200 字可以新增

- Given 服務正在執行
- When 使用者新增一個標題剛好 200 個字(例如 200 個「字」)的待辦
- Then 得到 201,列表裡它的標題和送出的完全一樣

### S-2 201 字被拒絕

- Given 服務正在執行
- When 使用者新增一個標題 201 個字的待辦
- Then 得到 422,說明是 `title must be at most 200 characters`,列表沒有多出東西

### S-3 前後空白不算在內

- Given 服務正在執行
- When 使用者新增的標題是 200 個字,前後各加幾個空白
- Then 得到 201,存下的標題是去掉前後空白的 200 個字

### S-4 已經存在的長標題照常可用

- Given 資料檔裡已經有一個標題 500 字的待辦(在這次改動之前新增的)
- When 使用者列出待辦,然後把它標為完成
- Then 列表看得到完整的 500 字標題,標為完成回 200

## How to try it

1. `git clone https://github.com/pitaya943/Shilaycow-trial && cd Shilaycow-trial && git checkout task/title-limit && pip install -r requirements.txt`
2. `TODO_DB=/tmp/t.db python -m uvicorn todo_api.app:create_app --factory --port 8765`
3. 另一個終端機:`python -c "import json;print(json.dumps({'title':'字'*200}))" > /tmp/ok.json`,`curl -X POST localhost:8765/todos -H 'content-type: application/json' -d @/tmp/ok.json` → 201。
4. 把 200 改成 201 再送一次 → 422,`title must be at most 200 characters`;`curl localhost:8765/todos` 只有一筆。

## Critical areas

None.

## Assumptions

- 「字」是 Unicode code point(Python 的 `len`):中文字、英文字母、一個 emoji 各算一個;由多個 code point 組成的 emoji(例如家庭 emoji)算多個。
- 先去掉前後空白再算長度,和現在「空白標題」的規則一致。
- 標題同時是空白與過長不可能發生;一個請求有多個錯時,仍只回第一個(標題的檢查在最前面)。見 #22。
- 上限只用在新增;資料檔裡已經存在的長標題不檢查、不截斷,升級時也不改。
- 上限是固定的 200,不能設定。
