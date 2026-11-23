# Final report: title-limit

依我自己的檢查,簡述的五個情境都做到了。

## What was done

新增待辦時,標題去掉前後空白後最多 200 個字;超過就回 422 `title must be at most 200 characters`,不新增、不截短。已經存著的較長標題照常列出與標為完成。另外加了 `shilaycow-correct` 的防護:新增待辦的每個欄位都要在 `INPUT_LIMITS` 宣告上限,少了或宣告了卻沒檢查,測試都會失敗。

## How to try it

1. `git clone https://github.com/pitaya943/Shilaycow-trial && cd Shilaycow-trial && git checkout task/title-limit && pip install -r requirements.txt`
2. `TODO_DB=/tmp/t.db python -m uvicorn todo_api.app:create_app --factory --port 8765`
3. 另一個終端機:`python -c "import json;print(json.dumps({'title':'字'*200}))" > /tmp/ok.json`,`curl -X POST localhost:8765/todos -H 'content-type: application/json' -d @/tmp/ok.json` → 201,標題完整。
4. 把 200 改成 201 再送 → 422,`{"detail":"title must be at most 200 characters"}`;`curl localhost:8765/todos` 只有一筆。
5. 在 `todo_api/app.py` 的 `NewTodo` 加一行 `note: str | None = None`,`python -m pytest -q` → 一個測試失敗並指出 `note`;拿掉後全過。

測試沒涵蓋、值得試的:
- 由多個 code point 組成的 emoji(例如 👨‍👩‍👧)算 5 個字,所以 40 個這種 emoji 就超過上限。
- 空白標題配上過長的其他欄位:只回第一個錯(#22)。

## Decisions I made

- 一張票,由 Chief 自己做,不派 builder;不單獨驗收,由這個 PR 的驗收判([trail](../trail.tsv) plan 列)。
- 上限以 `INPUT_LIMITS` 宣告、路由自己檢查,不用 pydantic 的 `max_length`:後者在去空白前算長度,且錯誤格式不同([Ready](https://github.com/pitaya943/Shilaycow-trial/pull/24#issuecomment-7096773739))。
- `due_date`、`priority` 也宣告上限(10、6),由既有的格式檢查擋下(同上)。
- 防護測試除了檢查宣告,也送出上限 +1 的值,這樣才擋得住 #5 那種「有上限卻沒檢查」(同上)。
- pitfall「簡述沒說的邊界」沒有移到 `## Guarded`:防護只涵蓋 #5 那一次,#16 的三類仍要靠人記得;條目加了一行說明已有的防護。

## Not done or in doubt

- pitfall「票的驗收條件沒修時不一定會失敗」次數 2,Owner 這次決定不做 correct(#12 已判斷沒有比文件更高又有效的一級)。

## Verification

獨立的驗收判定會以留言貼在這個 PR 上。

## Scenarios

| 情境 | 結果 | 證據 |
|---|---|---|
| S-1 剛好 200 字可以新增 | 做到 | `tests/test_title_limit.py`;[Ready](https://github.com/pitaya943/Shilaycow-trial/pull/24#issuecomment-7096773739) |
| S-2 201 字被拒絕 | 做到 | 同上;`evidence/T-01-drive.txt` 第 91–94 行 |
| S-3 前後空白不算在內 | 做到 | `tests/test_title_limit.py` |
| S-4 已經存在的長標題照常可用 | 做到 | `tests/test_title_limit.py`;`T-01-check.py` |
| S-5 文字欄位都要有長度上限 | 做到 | `tests/test_field_limits.py`;Ready 表格的兩種破壞 |

## Tickets

| 票 | 最後的風險 | 依據 | 驗收 |
|---|---|---|---|
| T-01 標題上限與欄位上限的防護 | medium | 改「新增待辦」HTTP 介面的驗證 | 沒有單獨驗收;由這個 PR 的驗收判 |
