# Design: priority

T-01 是 high(資料檔格式在 Critical areas),所以先設計、比較兩個形狀。

## 形狀 A(採用):就地加欄位

- `todos` 表加 `priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('low','normal','high'))`。
- 開檔時讀欄位集合:
  - 等於新的五欄 → 正常使用;
  - 等於舊的四欄(`id, title, done, due_date`)→ 在同一個寫入交易裡 `ALTER TABLE todos ADD COLUMN ...`,舊列自動得到 `normal`;
  - 其他 → 照舊 `StoreUnreadable`,什麼都不寫。
- 檢查欄位與 ALTER 包在 `BEGIN IMMEDIATE` 裡:兩個服務同時用舊檔啟動時,第二個等第一個做完,再看到五欄,不會因為「欄位已存在」而拒絕啟動。
- `application_id` 的檢查維持在最前面:不是這個服務寫的檔案不會被升級。

## 形狀 B(沒選):建新表、複製、改名

`CREATE TABLE todos_new ... ; INSERT INTO todos_new SELECT ..., 'normal' FROM todos; DROP; RENAME`。可以同時改欄位型別與限制,但要重寫每一列、要保留 `AUTOINCREMENT` 的序號(`sqlite_sequence`),出錯的面比較大。這次只加一個有預設值的欄位,SQLite 的 `ADD COLUMN` 不重寫資料、在交易內可回復,A 足夠。

## 介面

- `Todo` 多一個 `priority: str = "normal"`;`TodoStore.add(title, due_date=None, priority="normal")`。
- 值的合法性由 HTTP 層檢查並回 422(T-02);資料表的 `CHECK` 是第二道防線。
- 回應一律有 `priority`。既有測試裡比對整個 JSON 的地方要加上 `"priority": "normal"`:這是簡述核准的行為改變。
