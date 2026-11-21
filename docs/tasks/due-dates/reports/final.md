# 待辦事項的到期日:最終報告

brief 的五個情境(S-1 到 S-5)全部做到;獨立驗證的裁決會以留言貼在這個 pull request 上,這份報告寫在驗證之前(見「驗證結果」)。

## 做了什麼

`POST /todos` 現在可以多帶一個 `due_date`(`YYYY-MM-DD`),回應會帶著它;不帶的話,回應和以前逐位元組相同。`GET /todos?overdue=true` 只列出「還沒完成、到期日早於今天」的待辦;不帶參數時和以前一樣列出全部。格式不對的到期日回 422 與固定訊息,清單不會多東西。`drive-todo-api` 多了四個到期日情境,並修掉我在這次改動裡引進的一個腳本缺陷。上一個任務的 10 個測試一行都沒改,新增 11 個,共 21 個全部通過。

## 怎麼試

```
pip install -r requirements.txt
python -m pytest -q                                      # 應看到 21 passed
bash .claude/skills/drive-todo-api/drive.sh /tmp/try.txt  # 先跑原本的五個情境,再跑 S-1、S-2、S-4,重啟後跑 S-3
```

第三行的輸出應與 [`evidence/drive.txt`](../evidence/drive.txt) 相同(第一行的時間與 commit、以及 S-3 裡依當天算出的日期除外)。最後一個回應應該只有 A 一筆。

手動試:`python -m uvicorn todo_api.app:app --port 8765`,然後

```
curl -s -X POST localhost:8765/todos -H 'Content-Type: application/json' -d '{"title": "繳電費", "due_date": "2026-12-01"}'
curl -s -X POST localhost:8765/todos -H 'Content-Type: application/json' -d '{"title": "報稅", "due_date": "下週五"}'
curl -s 'localhost:8765/todos?overdue=true'
```

## 我自己做的決定

全部在 [`trail.tsv`](../trail.tsv):

- 沒有另寫設計、沒有切票、沒有用 builder,Chief 自己做完(第 1 列);合併前沒有另做單票驗證(第 9 列)。
- 欄位叫 `due_date`;只列逾期用 `GET /todos?overdue=true`(第 2 列)。
- **沒有到期日的待辦,回應裡不出現 `due_date` 這個鍵,而不是 `null`**(第 3 列)。這是為了讓 S-5「和以前一樣」成立到逐位元組;代價是兩種待辦的形狀不同。Owner 若比較想要固定出現 `"due_date": null`,改動是刪掉三個 `response_model_exclude_none=True`,但上一個任務的測試要跟著改。
- 「今天」用 `create_app(today=...)` 注入,每次查詢時才取(第 4 列)。
- 只收嚴格的 `YYYY-MM-DD`;其餘回 422 `due_date must be a date like 2026-12-01`(第 5 列)。
- brief 沒定的輸入(`null`、非字串、`overdue=false`、兩個錯同時發生、過去的日期)各取最不意外的行為(第 6 列)。
- `drive.sh` 在逾期情境前重啟服務,日期用機器的日期算(第 7 列)。
- 修掉我自己引進的 `drive.sh` subshell 缺陷(第 8 列,[2f1270f](https://github.com/pitaya943/Shilaycow-trial/commit/2f1270f))。

## 沒做到或有疑慮的

- `due_date` 不是字串(例如數字)時,回的是 FastAPI 預設的 422,訊息格式與固定訊息不同;沒有測試。
- `overdue` 給了不是布林的值(例如 `overdue=abc`)同樣是 FastAPI 預設的 422;沒有測試。
- 「今天」是服務所在機器的本地日期(假設三)。機器時區與使用者不同時,「逾期」會差一天。
- `drive.sh` 的修正(2f1270f)沒有自動測試,只有實跑:連跑兩次都 exit 0、結束後 `pgrep` 沒有殘留、埠被占用時 exit 1。`drive.sh` 用到 GNU `date -d`,macOS 內建的 `date` 不支援。
- S-3 的 feat commit(73a5f5b)在推送前被我 amend 過一次:第一版把 `overdue` 定義在 `list` 方法之後,`list[Todo]` 這個標註指到方法而不是內建型別,整個套件 import 失敗。歷史裡看不到那個壞掉的版本。
- `drive.sh` 管不好自己啟動的服務,這一類的錯在 `.shilaycow/pitfalls.md` 已經是第 2 次,照 `retro` 該交給 `correct`(例如一支會在占用埠、連跑兩次時檢查 exit code 與殘留行程的自我檢查)。`correct` 要另開一個 pull request,這個任務的層級是一個任務一個 pull request,所以我沒有做,留給 Owner 決定要不要開下一個任務。
- 上一個任務留下的疑慮仍在:`TodoStore.add` 沒有鎖;這次沒有碰。
- `brief.md` 第 3 行仍寫「狀態:草稿,等 Owner 核准」;Owner 已在對話中核准,我沒有改 brief。
- 這個 PR 也會把試跑用的檔案帶進 `main`:更新過的 `.claude/skills/`(在 cb7d2b3,不是我做的)與 `docs/tasks/due-dates/trial-notes.md`。
- 試跑筆記在驗證之後的補記(裁決內容、花費)不在這個分支上:`go` 規定裁決之後不能再推任何東西。補記放在分支 `notes/due-dates-trial` 與 tracking issue [#5](https://github.com/pitaya943/Shilaycow-trial/issues/5)。

## 驗證結果

這份檔案在驗證之前就定稿了(`go` 規定裁決之後不能再推),所以裁決不在檔案裡:請看這個 pull request 上以 `## Verification:` 開頭的留言,以及 pull request 描述最上面在裁決後補上的那一行。驗證由一個沒有參與建造的新 session 依 `verify` 進行。

## 情境

| 情境 | 做到 | 測試(都先看過它失敗) | 實跑紀錄 |
|---|---|---|---|
| S-1 新增時帶到期日 | 是 | `tests/test_due_dates.py::test_create_with_due_date_returns_it` | [`evidence/drive.txt`](../evidence/drive.txt)「due-dates S-1」 |
| S-2 不帶到期日 | 是 | `tests/test_due_dates.py::test_create_without_due_date_has_none_and_is_otherwise_as_before` | 同上「due-dates S-2」 |
| S-3 只看逾期的 | 是 | `tests/test_due_dates.py::test_overdue_lists_only_unfinished_todos_due_before_today`、`::test_a_todo_due_today_is_not_overdue` | 同上「due-dates S-3」 |
| S-4 到期日的格式不對 | 是 | `tests/test_due_dates.py::test_malformed_due_date_is_rejected_and_list_unchanged`(7 個值) | 同上「due-dates S-4」 |
| S-5 原本的功能不變 | 是 | `tests/test_create_list.py`、`tests/test_complete.py`(10 個,未更動) | 同上前 47 行,與 [`todo-api/evidence/T-02-drive.txt`](../../todo-api/evidence/T-02-drive.txt) 除第一行外相同 |
