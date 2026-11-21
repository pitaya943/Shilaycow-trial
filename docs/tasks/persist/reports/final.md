# 待辦事項在重啟後還在

依我自己的檢查,簡述的六個情境都做到了。

## 1. 做了什麼

待辦事項現在存進服務所在機器上的一個檔案(SQLite),服務關掉再打開,待辦、到期日、完成狀態與編號都還在。對外的行為沒有變:我用同一支腳本對 `main` 與這個分支各送 26 個請求,回應逐位元組相同。資料檔如果不是這個服務寫的,服務會拒絕啟動、指出是哪個檔案,而且不動它。**啟動指令變了**(見下一節),因為舊的寫法會在匯入模組時就建立資料檔。

## 2. 怎麼試

從零開始,需要 git 與 Python 3.11 以上:

```
git clone https://github.com/pitaya943/Shilaycow-trial.git
cd Shilaycow-trial
git checkout task/persist
pip install -r requirements.txt
python -m uvicorn todo_api.app:create_app --factory --host 127.0.0.1 --port 8765
```

服務會停在那個終端機。另開一個終端機:

| 做什麼 | 指令 | 應該看到 |
|---|---|---|
| 新增一筆帶到期日的 | `curl -s -X POST http://127.0.0.1:8765/todos -H 'Content-Type: application/json' -d '{"title": "繳電費", "due_date": "2026-12-01"}'` | `{"id":1,"title":"繳電費","done":false,"due_date":"2026-12-01"}` |
| 再新增一筆 | `curl -s -X POST http://127.0.0.1:8765/todos -H 'Content-Type: application/json' -d '{"title": "買牛奶"}'` | `{"id":2,"title":"買牛奶","done":false}` |
| 把第二筆標為完成 | `curl -s -X POST http://127.0.0.1:8765/todos/2/complete` | `"done":true` |
| 關掉服務再啟動 | 回到第一個終端機按 Ctrl-C,再執行同一行 `python -m uvicorn ...` | 服務正常啟動 |
| 列出 | `curl -s http://127.0.0.1:8765/todos` | 同樣兩筆,「買牛奶」仍是完成 |
| 再新增一筆 | 同第二列,標題換成「倒垃圾」 | 編號是 3 |

資料在你啟動服務的那個目錄下的 `todos.db`。想重來就關掉服務、刪掉它。

測試不會涵蓋、值得你親手試的三件事:

1. **把資料檔弄壞**:關掉服務,執行 `echo junk > todos.db`,再啟動。應該看到服務不啟動,最後一行是 `StoreUnreadable: cannot use the data file todos.db: file is not a database`,而且 `cat todos.db` 仍是 `junk`。試完刪掉它。
2. **換一個目錄啟動**:資料檔的預設位置是「啟動時所在的目錄」,所以從別的目錄啟動會安靜地開出一份新的空清單。這是簡述的假設,但你可能會覺得意外。要固定位置就設 `TODO_DB=/某個路徑/todos.db`。
3. **很長的標題**:仍然沒有上限(這次不做)。驗收時試過 500 萬字的標題,會被接受,資料檔變成 5 MB 並永久留著。

不想手動的話:`python -m pytest -q`(41 個測試)與 `bash .claude/skills/drive-todo-api/drive.sh /tmp/drive.txt`(整段流程,含實際重啟與亂碼檔)。

## 3. 我自己做的決定

完整的在 `docs/tasks/persist/trail.tsv`。你最可能想知道的:

- **用 SQLite,不用自己寫的 JSON 檔。** 原子寫入、鎖、不重複的編號都是現成的;代價是資料檔不能用文字編輯器看。
- **啟動指令改成 `todo_api.app:create_app --factory`。** 舊指令 `todo_api.app:app` 現在會明確報錯。前兩個任務最終報告裡寫的是舊指令,我沒有回頭改那些紀錄。
- **兩張票依序做,不平行。** 第二張需要第一張的儲存層。
- **T-01 驗收發現的退步交給 T-02 修**:編號超過 2^63 時「標為完成」從 404 變成了 500。已修,有測試。
- **T-02 驗收發現的缺口我自己修,沒有另開票**:只有 view、沒有任何資料表的資料庫會被接受並寫入。兩行程式加一個測試。
- **開檔時任何 SQLite 錯誤都算「讀不了」**,包含檔案被別的行程鎖住(會等 5 秒後拒絕啟動)。

## 4. 沒做到或有疑慮的

- **欄位正確、但某一列內容不對的資料檔會通過啟動檢查**,之後列出待辦時回 500。例如有人手動把到期日改成 `soon`。啟動時檢查每一列是新的功能,簡述沒有要求,我沒有做。([T-02 的判定](https://github.com/pitaya943/Shilaycow-trial/pull/10#issuecomment-7068325347),發現 2)
- **「編號不重複使用」沒有測試守著。** 沒有刪除功能時觀察不到差別;等有刪除功能的任務再補。([T-01 的判定](https://github.com/pitaya943/Shilaycow-trial/pull/9#issuecomment-7068219689),發現 2)
- **兩個服務同時用同一個檔案**不會被擋,也沒有警告(簡述明說不在範圍)。
- **標題長度沒有上限**,而且現在會永久存下來。建議下一個任務處理。
- **檔案唯讀或沒有權限的情況沒有測到**:執行環境是 root,權限擋不住。
- 這個任務沒有用到平行的 builder。

## 5. 驗證

獨立的判定會以留言的形式貼在這個 PR 上。兩張票各自的判定:[T-01](https://github.com/pitaya943/Shilaycow-trial/pull/9#issuecomment-7068219689)、[T-02](https://github.com/pitaya943/Shilaycow-trial/pull/10#issuecomment-7068325347)。

## 情境

| 情境 | 做到 | 證據 |
|---|---|---|
| S-1 重啟後資料還在 | 是 | `tests/test_persist.py::test_todos_due_dates_and_done_survive_a_restart`;實際重啟的紀錄 `docs/tasks/persist/evidence/drive.txt` |
| S-2 完成狀態也還在 | 是 | 同上 |
| S-3 編號不會重複使用 | 是 | `tests/test_persist.py::test_ids_continue_after_a_restart`;同一份紀錄 |
| S-4 第一次啟動 | 是 | `tests/test_persist.py::test_first_start_creates_the_file_and_lists_nothing` |
| S-5 存的資料壞掉了 | 是 | `tests/test_unreadable.py`(9 個);實際啟動失敗的紀錄在 `drive.txt` 最後一段與 `evidence/blast-radius.txt` 的 Fact 4 |
| S-6 原本的功能不變 | 是 | 原有 21 個測試一行未改而通過;`evidence/blast-radius.txt` 的 Fact 6:26 個請求的回應與 `main` 逐位元組相同 |

## 這個改動安全所依賴的事實(blast-radius)

每一項都實際執行過,輸出在 `docs/tasks/persist/evidence/blast-radius.txt`。

| 事實 | 做到哪一級 | 結果 |
|---|---|---|
| 每個 HTTP 回應都和 `main` 一樣 | 4:同一支腳本對兩邊的程式跑 | 26 個請求,diff 相同 |
| 測試不共用資料,不在 repo 留下資料檔 | 4:整套跑兩種順序 | 41 passed 兩次,0 個 `todos.db` |
| 匯入模組不建立檔案 | 4:在空目錄匯入 | 目錄仍是空的 |
| 沒有別的地方還在用舊的啟動方式 | 4:搜尋加實際執行舊指令 | 只剩舊任務的報告;舊指令明確報錯 |
| 被拒絕的檔案位元組不變 | 5:真的啟動服務,三種檔案 | 都 exit 1,雜湊前後相同 |
| 多個請求同時進來不會出錯 | 5:真的服務,60 個新增與 60 個完成同時送 | 全部成功,60 個不同的編號;`kill -9` 後重啟 60 筆都在 |
