# 待辦事項服務:設計

使用的視角:**Frame**、**Interfaces**、**State owners**、**Workflow**(一個情境)。
略過:**Data flow**(只有「請求 → 記憶體清單 → 回應」一條路,Interfaces 表已經說完);**Notifications**(沒有任何人需要被通知,情境裡沒有非同步事件)。

## Frame

| 部件 | 檔案 | 責任 | 對應情境 |
|---|---|---|---|
| HTTP 層 | `todo_api/app.py` | `create_app()` 建立 FastAPI app 與三條路由;把 store 的結果或錯誤轉成 HTTP 回應。模組層 `app = create_app()` 供 uvicorn 使用 | S-1 – S-5 |
| 儲存 | `todo_api/store.py` | `TodoStore`:持有清單與下一個編號;`add`、`list`、`complete` | S-1、S-2、S-3、S-5 |

邊界:HTTP 層不直接碰清單;store 不知道 HTTP。

## Interfaces

| 動作 | 請求 | 成功 | 失敗 | 情境 |
|---|---|---|---|---|
| 新增 | `POST /todos`,body `{"title": "買牛奶"}` | `201`,`{"id": 1, "title": "買牛奶", "done": false}` | 標題是空字串或只有空白:`422`,`{"detail": "title must not be blank"}`,清單不變 | S-1、S-4 |
| 列出 | `GET /todos` | `200`,待辦陣列,依新增順序 | — | S-2、S-3 |
| 標為完成 | `POST /todos/{id}/complete` | `200`,該筆待辦,`done` 為 `true` | 編號不存在:`404`,`{"detail": "todo not found"}` | S-3、S-5 |

`TodoStore`:`add(title: str) -> Todo`、`list() -> list[Todo]`、`complete(todo_id: int) -> Todo | None`。`Todo` 有 `id: int`、`title: str`、`done: bool`。

細節(brief 沒說,我定的,見 trail):編號從 1 遞增(brief 的假設);標題存入前去掉頭尾空白;對已完成的待辦再標一次完成回 `200`(冪等);「空白」包含只有空白字元。

## State owners

| 狀態 | 唯一擁有者 | 情境 |
|---|---|---|
| 待辦清單、下一個編號 | 一個 `TodoStore` 實例,由 `create_app()` 建立並綁在該 app 上 | S-1 – S-5 |

每次 `create_app()` 都得到一份全新的清單,所以每個測試可以從空清單開始(S-2、S-4 的 Then 需要知道清單裡確切有什麼)。

## Workflow:S-3 從頭到尾

1. `POST /todos {"title":"買牛奶"}` → store.add → `201 {"id":1,...,"done":false}`
2. `POST /todos {"title":"繳電費"}` → `201 {"id":2,...}`
3. `POST /todos/1/complete` → store.complete(1) → `200 {"id":1,"title":"買牛奶","done":true}`
4. `GET /todos` → `[{"id":1,...,"done":true},{"id":2,...,"done":false}]`:第一筆已完成,另一筆不變。

## 兩個形狀

**A(選這個)**:上面的形狀。`create_app()` 工廠 + 每個 app 一個 `TodoStore`;完成用專屬動作 `POST /todos/{id}/complete`。

**B(沒選)**:單一檔案,模組層全域 `todos = []`;完成用通用的 `PATCH /todos/{id}`,body `{"done": true}`。
- B 比較好的地方:檔案更少、更短;`PATCH` 是比較常見的 REST 寫法,將來要加「編輯標題」時不用換介面。
- B 輸的原因:(1) 全域清單沒有明確的擁有者,測試之間會互相污染,要靠每個測試自己記得清空;(2) `PATCH` 讓呼叫端可以送 `{"done": false}` 或 `{"title": ...}`,而 brief 明說不做「改回未完成」與「編輯標題」,等於要多寫拒絕的程式;A 的呼叫端要知道的最少,而且每件事只有一種做法。

## 情境 → 證明

| 情境 | 測試(pytest,用 FastAPI `TestClient`) | 實際驅動 |
|---|---|---|
| S-1 | `tests/test_create_list.py::test_create_returns_todo_with_id_title_not_done` | `drive-todo-api`:curl `POST /todos` |
| S-2 | `tests/test_create_list.py::test_list_returns_todos_in_insertion_order` | curl `GET /todos` |
| S-3 | `tests/test_complete.py::test_complete_marks_only_that_todo_done` | curl `POST /todos/1/complete` 後 `GET /todos` |
| S-4 | `tests/test_create_list.py::test_blank_title_is_rejected_and_list_unchanged` | curl `POST /todos` 帶 `{"title": "  "}` |
| S-5 | `tests/test_complete.py::test_complete_unknown_id_is_not_found` | curl `POST /todos/999/complete` |
