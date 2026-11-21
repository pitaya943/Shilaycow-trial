# 計畫:persist

兩張票,依序做。T-02 需要 T-01 的 `TodoStore(path)`,而且兩張都會改 `store.py`,所以不平行。

| 票 | 情境 | 依賴 | 會動到 |
|---|---|---|---|
| T-01 資料存進檔案 | S-1、S-2、S-3、S-4、S-6 | 無 | `todo_api/store.py`、`todo_api/app.py`、`tests/`、`README.md`、`.gitignore`、`drive-todo-api` 的啟動指令 |
| T-02 讀不了的資料檔與重啟的操作紀錄 | S-5,以及 S-1 到 S-3 的實際重啟 | T-01 | `todo_api/store.py`、`tests/`、`drive-todo-api` |

每張票在併進 `task/persist` 之前由一個沒有參與建置的 session 驗收(謹慎程度:謹慎)。最後對整個分支跑 `blast-radius`,再開進 `main` 的 PR 並驗收。

預算的估計:Chief 1、builder 2、逐張驗收 2、最終驗收 1,共 6 個 session;剩下 4 個留給修正。
