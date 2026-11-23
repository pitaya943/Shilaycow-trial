# Todos

使用者用它記下要做的事、標出做完的、找出逾期的、只看某個優先順序的。

## Scenarios

### 新增一個待辦

- Given 服務正在執行
- When 使用者新增標題為「買牛奶」的待辦
- Then 得到 201 與這個待辦:新的編號、標題「買牛奶」、未完成、優先順序 `normal`,列表最後多出它

### 新增時給到期日

- Given 服務正在執行
- When 使用者新增待辦時給 `2026-12-01` 這樣的到期日
- Then 回應與列表裡它帶著這個到期日;沒給到期日的待辦在回應裡沒有 `due_date`

### 新增時給優先順序

- Given 服務正在執行
- When 使用者新增待辦時給 `low`、`normal` 或 `high`
- Then 回應與列表裡它的優先順序就是給的值;沒給或給 `null` 時是 `normal`

### 不合法的輸入被拒絕

- Given 服務正在執行
- When 使用者新增的標題只有空白、去掉前後空白後超過 200 個字,或到期日不是 `YYYY-MM-DD`,或優先順序不是 `low`/`normal`/`high` 三者之一
- Then 得到 422 與一句說明,列表沒有多出東西

### 列出待辦

- Given 已經新增了幾個待辦
- When 使用者列出待辦
- Then 依新增的順序看到每一個,各自帶著編號、標題、是否完成、優先順序,有到期日的帶著到期日

### 只列出逾期的

- Given 有已完成的、未完成的、今天到期的、昨天到期的待辦
- When 使用者只列出逾期的
- Then 只看到未完成而且到期日早於今天的那些,各自帶著優先順序

### 只列出某個優先順序的

- Given 有 `low`、`normal`、`high` 的待辦,交錯新增
- When 使用者列出優先順序為 `high` 的待辦
- Then 只看到 `high` 的那些,依新增的順序;沒有符合的時候是 200 與空的列表

### 優先順序和逾期一起篩

- Given 有逾期的 `high`、逾期的 `low`、還沒到期的 `high`
- When 使用者同時要求逾期的與優先順序 `high`
- Then 只看到逾期的那個 `high`

### 篩選的優先順序不合法

- Given 服務正在執行
- When 使用者以 `urgent`、`High`、前面有空白的 ` high` 或空字串篩選,或在同一個請求給兩次優先順序
- Then 得到 422:前者是 `priority must be one of: low, normal, high`,後者是 `priority may be given only once`;什麼都沒變

### 標為完成

- Given 有一個未完成的待辦
- When 使用者把它標為完成
- Then 得到它、已完成、其他欄位不變;其他待辦不受影響;再標一次也是成功

### 標一個不存在的編號

- Given 服務正在執行
- When 使用者標一個沒有的編號為完成(包含大到不可能存在的數字)
- Then 得到 404「todo not found」,什麼都沒變

### 重啟之後

- Given 使用者新增了幾個待辦、標了一個完成
- When 服務停掉再用同一個資料檔啟動
- Then 待辦、編號、到期日、完成狀態、優先順序都和之前一樣,新的待辦接著舊的編號

### 用舊版的資料檔啟動

- Given 一個加入優先順序之前的版本寫入的資料檔
- When 用目前的版本以它啟動
- Then 服務正常啟動,舊待辦內容不變、優先順序都是 `normal`,以 `normal` 篩選時都看得到

### 資料檔不是這個服務的

- Given 資料檔是別的程式寫的、壞掉的、只有一個位元組、或是一個目錄
- When 服務以它啟動
- Then 服務不啟動,訊息指出那個檔案,檔案一個位元組都沒被改

## Rules

| 規則 | 決定的任務 |
|---|---|
| 標題前後的空白會被去掉;去掉後是空的就拒絕 | todo-api |
| 標題去掉前後空白後最多 200 個字(Unicode code point);超過回 422,不截短。已經存著的較長標題照常列出與標為完成 | title-limit |
| 新增待辦的每個欄位都有宣告的長度上限(`INPUT_LIMITS`);少了上限的欄位會讓測試失敗 | title-limit |
| 到期日只接受 `YYYY-MM-DD`;`20261201` 這類也拒絕 | due-dates |
| 今天到期的不算逾期;「今天」是服務所在機器的日期 | due-dates |
| 優先順序只接受小寫的 `low`/`normal`/`high`,不去空白、不轉大小寫;沒給或 `null` 是 `normal` | priority |
| 回應一律有 `priority` | priority |
| 篩選的優先順序和新增時一樣嚴格;給兩次回 422,兩個錯同時出現時先報「只能一次」 | priority-filter |
| 優先順序與逾期一起給時兩個都要成立;不給優先順序時,列表與逾期列表和加入篩選之前一樣 | priority-filter |
| 允許的優先順序只定義在一處(`todo_api/store.py` 的 `PRIORITIES`);新增、篩選、新資料檔的 `CHECK` 都讀它。改它只影響之後新建的資料檔:舊檔保留建立時的 `CHECK`,在舊檔新增新加的值會得到 500 *(#30 的判定 Findings 1,尚未決定)* | priority-filter |
| 列表的每個查詢參數都要在 `LIST_QUERY_VALUES` 宣告允許的值,`tests/test_query_params.py` 守著 | priority-filter |
| 編號不會重複使用(AUTOINCREMENT) | persist |
| 資料檔是第一次啟動時才建立;已存在但不是這個服務寫的檔一律拒絕、不寫 | persist |
| 舊的四欄資料檔在啟動時就地加上優先順序;兩個服務同時用舊檔啟動都會成功 | priority |
| 同時多人寫入交給 SQLite 的鎖 | persist |

## Last changed by

- priority-filter(#29):依優先順序篩選、允許值只在一處
- title-limit(#23):標題上限 200 字
- priority(#16):優先順序、舊資料檔升級
- persist(#8):資料存進檔案
- due-dates(#5):到期日與逾期
- todo-api(#1):新增、列出、標為完成
