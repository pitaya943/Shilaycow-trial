# Design: priority-filter

只有 T-01 是 high(它碰資料檔建立時寫下的資料表定義),所以設計只談它;T-02 的形狀在票裡寫明即可。

## T-01:允許的優先順序放在哪裡

`later` #20:允許值在 `todo_api/app.py` 的 `PRIORITIES` 與 `todo_api/store.py` 的 `CHECK` 各寫一次,只改一處就變 500。T-02 的篩選又要讀一次允許值。

### 形狀 A(採用):一個 tuple,放在 store

`todo_api/store.py` 定義 `PRIORITIES = ("low", "normal", "high")`;`_PRIORITY_COLUMN` 的 `CHECK` 由它產生;`app.py` 從 store 匯入,新增與篩選都用它。

- store 擁有資料的形狀,HTTP 層依賴 store 已經是現在的方向(`app.py` 已經 import `todo_api.store`),不會出現反向依賴。
- 對三個預設值,產生出來的 `CHECK` 字串要和現在一字不差:新建的資料檔和這次之前建的完全相同,`ALTER TABLE ... ADD COLUMN` 的舊檔升級也不變。T-01 的檢查比對這個字串。
- 代價:`CHECK` 是寫進資料檔的;改 tuple 只影響之後建立的資料檔(brief 的 Out of scope 與 Assumptions 已寫明)。

### 形狀 B(不採用):`enum.Enum` 或 `Literal[...]` 交給 pydantic 驗證

- 一個型別同時給 pydantic 與 store 用,寫錯的值在型別層就擋下。
- 但 pydantic 的 422 回應是它自己的錯誤列表,不是現在的 `{"detail": "priority must be one of: low, normal, high"}`;spec 的規則「回應一律是那一句」會被打破,客戶端與 `try-todo-api` 都依賴那一句。要保住那一句,又得在路由裡自己再驗一次,等於回到兩處。

### 不變的

- 新增時的驗證規則與訊息(spec「優先順序只接受小寫的……」)。
- 舊四欄資料檔就地升級(spec「舊的四欄資料檔在啟動時就地加上優先順序」)。
