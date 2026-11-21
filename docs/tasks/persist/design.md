# 設計:待辦事項在重啟後還在

依據:`brief.md` 的 S-1 到 S-6。

## 形狀

只換儲存層。HTTP 那一層(路徑、請求、回應)一個位元組都不變。

```
HTTP 請求 → todo_api/app.py(不知道資料存在哪) → TodoStore(唯一擁有資料的地方) → SQLite 檔案
```

| 部分 | 職責 | 這次的改動 |
|---|---|---|
| `todo_api/store.py` | 唯一擁有待辦資料的地方 | 從記憶體裡的 list 換成一個 SQLite 檔案。對外的四個方法不變 |
| `todo_api/app.py` | 把 store 的結果變成 HTTP 回應 | 只多一件事:決定資料檔的路徑並交給 store |
| 資料檔 | 資料停留的地方 | 新增 |

## 介面

```python
class StoreUnreadable(Exception):
    """資料檔存在,但不是這個服務寫的。訊息裡有檔案的路徑。"""

class TodoStore:
    def __init__(self, path: str | Path) -> None: ...   # 檔案不存在就建立;讀不了就丟 StoreUnreadable,不動那個檔案
    def add(self, title: str, due_date: date | None = None) -> Todo: ...
    def overdue(self, today: date) -> list[Todo]: ...
    def list(self) -> list[Todo]: ...
    def complete(self, todo_id: int) -> Todo | None: ...

def create_app(today=date.today, db_path: str | Path | None = None) -> FastAPI: ...
```

- 資料檔的路徑只有一個決定的地方,在 `create_app`:參數 `db_path`,沒給就用環境變數 `TODO_DB`,再沒有就是啟動目錄下的 `todos.db`。
- 資料表:`todos(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, done INTEGER NOT NULL, due_date TEXT)`。到期日存成 `YYYY-MM-DD` 文字。`AUTOINCREMENT` 保證編號不重複使用(S-3)。列出的順序就是編號的順序,等於新增的順序。
- 每個操作自己開一條連線、做完就 commit 並關閉。程序裡沒有共用的可變狀態;同時寫入交給 SQLite 的鎖。SQLite 預設在 commit 回來前已經寫進磁碟,所以回覆「成功」時資料已經在檔案裡。

## 啟動方式改變

現在 `todo_api/app.py` 的最後一行 `app = create_app()` 會在「匯入這個模組」時就建立 store。換成檔案之後,這代表任何匯入(包含每一個測試檔)都會在當下的目錄建立或打開 `todos.db`。

所以拿掉模組層級的 `app`,改用工廠啟動:

```
python -m uvicorn todo_api.app:create_app --factory --host 127.0.0.1 --port 8765
```

這是唯一支援的啟動方式。README 與 `drive-todo-api` 跟著改。匯入模組不再有任何副作用。

## 讀不了的資料檔(S-5)

`TodoStore.__init__` 打開檔案後先驗證,任何一項不成立就丟 `StoreUnreadable(路徑)`,而且不寫入任何東西:

- 檔案不是 SQLite 資料庫(亂碼、文字檔)。
- 是 SQLite 資料庫,但裡面已經有別的資料表而沒有 `todos`,或 `todos` 的欄位不是上面那四個。

長度為 0 的檔案與不存在的檔案都當作第一次啟動(S-4)。驗證通過之後才 `CREATE TABLE IF NOT EXISTS`。

`create_app` 不接住這個例外:工廠啟動時 uvicorn 會印出它並以非 0 結束,最後一行是 `StoreUnreadable` 與檔案路徑。

## 測試怎麼不碰到真正的資料檔

`tests/conftest.py` 一個自動套用的 fixture,把 `TODO_DB` 指到每個測試自己的暫存目錄。現有的 21 個測試一行都不改,就各自從空的清單開始,這同時就是 S-6 的證明。重啟用「對同一個路徑呼叫兩次 `create_app`」來測;真正關掉再啟動行程由 `drive-todo-api` 做一次並留紀錄。

`drive.sh` 現在保證「每次執行從空的清單開始」,所以它要自己用一個暫存的資料檔,結束時刪掉。`todos.db` 加進 `.gitignore`。

## 每個情境怎麼證明

| 情境 | 證明 |
|---|---|
| S-1、S-2、S-3 | 測試:同一個路徑建第一個 app、操作、再建第二個 app、檢查。加上一次真的重啟行程的操作紀錄 |
| S-4 | 測試:指向不存在的路徑,清單是空的 |
| S-5 | 測試:寫入亂碼後 `TodoStore(path)` 丟 `StoreUnreadable`,檔案的位元組不變。加上一次真的啟動失敗的操作紀錄 |
| S-6 | 現有 21 個測試不修改而通過;操作腳本原本的九個情境重跑一次 |

## 考慮過的另一個形狀:一個 JSON 檔

每次寫入時把整份清單寫到暫存檔再改名蓋過去。好處:檔案人看得懂,沒有資料表。沒選它的原因:每次寫入都重寫整份(筆數沒有上限時越來越慢);要自己做鎖、自己存下一個編號、自己定義什麼叫壞掉;而 SQLite 在標準函式庫裡,原子寫入與鎖都是現成的。代價:資料檔不能用文字編輯器看。

## 這個設計安全所依賴的事實

給 `blast-radius` 用:

1. 每個測試拿到自己的資料檔,不會互相看到資料,也不會在 repo 裡留下 `todos.db`。
2. 匯入 `todo_api.app` 不會建立或打開任何檔案。
3. repo 裡沒有別的地方還在用 `todo_api.app:app`。
4. 讀不了的檔案在驗證失敗後位元組不變。
5. 請求在不同的執行緒進來時不會出錯(FastAPI 的同步路由跑在執行緒池裡)。
