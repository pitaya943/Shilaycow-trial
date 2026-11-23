# Plan: priority

| 票 | 內容 | 情境 | 依賴 | 區域 | Risk |
|---|---|---|---|---|---|
| T-01 | 儲存層:priority 欄位與舊檔就地升級 | S-4、S-5 | — | `todo_api/store.py` | high |
| T-02 | HTTP:新增時收 priority、驗證、所有回應帶出;`try-todo-api` 加上 priority | S-1、S-2、S-3、S-6 | T-01 | `todo_api/app.py`、`.claude/skills/try-todo-api/` | medium |

依序做:T-02 需要 T-01 的欄位。T-01 是 high,併入 task 分支前先獨立驗收。

每張票的檢查都在交票前對目前的程式跑過,看到失敗(pitfall「票的驗收條件沒修時不一定會失敗」)。
