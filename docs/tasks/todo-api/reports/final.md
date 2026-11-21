# 待辦事項服務:最終報告

brief 的五個情境(S-1 到 S-5)全部做到,獨立驗證者對整個任務分支的裁決是 PASS([裁決](https://github.com/pitaya943/Shilaycow-trial/issues/1#issuecomment-7065884506),針對 f091b8a)。

## 做了什麼

做了一個 FastAPI 的小服務:`POST /todos` 新增待辦、`GET /todos` 依新增順序列出、`POST /todos/{id}/complete` 標為完成;資料放在記憶體([#2](https://github.com/pitaya943/Shilaycow-trial/pull/2)、[#3](https://github.com/pitaya943/Shilaycow-trial/pull/3))。空白標題回 422,不存在的編號回 404。另外做了 `drive-todo-api`:一支腳本啟動真的服務、用 curl 走完五個情境並留下紀錄。共 10 個測試,全部通過。

## 怎麼試

```
pip install -r requirements.txt
python -m pytest -q                                      # 應看到 10 passed
bash .claude/skills/drive-todo-api/drive.sh /tmp/try.txt  # 啟動服務,依序做 S-1 到 S-5
```

第三行的輸出應與 [`evidence/T-02-drive.txt`](../evidence/T-02-drive.txt) 相同(第一行的時間與 commit 除外)。想手動試:`python -m uvicorn todo_api.app:app --port 8765`,再用 curl 照 brief 的情境做。

## 我自己做的決定

全部在 [`trail.tsv`](../trail.tsv),比較重要的:

- 形狀:`create_app()` 工廠加每個 app 一個 `TodoStore`,不用全域清單;狀態才有唯一擁有者(trail 第 1 列,[design](../design.md))。
- 完成用專屬動作 `POST /todos/{id}/complete`,不用 `PATCH`;brief 不做改回未完成與編輯標題(第 2 列)。
- brief 只說「被告知」,我定成:空白標題 422 `title must not be blank`、找不到 404 `todo not found`(第 3 列)。
- brief 沒說的行為:標題存入前去掉頭尾空白(全形空白也算空白);對已完成的再標一次回 200(第 4 列、builder 的列)。
- 切成兩張依序的票,不平行;`drive-todo-api` 併在第一張票的最後(plan 的列)。
- 倉庫沒有 CI,由驗證者自己跑 `python -m pytest -q` 代替(plan 的列)。
- 兩個 PR 都用 merge commit 併入,保留先測試後實作的順序(d367f99、31d61c9)。
- PR #2 的驗證者指出 `drive.sh` 的缺陷後,把修正加進 T-02 而不是另開一張票(c5da171)。
- PR #3 的 PASS 帶著兩個 TDD 順序的例外,照樣合併,沒有開修正回合([裁決](https://github.com/pitaya943/Shilaycow-trial/pull/3#issuecomment-7065811909))。

## 沒做到或有疑慮的

- `TodoStore.add` 沒有鎖。整體驗證者在強制極短的執行緒切換間隔下重現了重複編號(每 5000 次新增最多 6 個);預設設定下 200 萬次新增與 3 萬個並行請求都沒有重現([裁決](https://github.com/pitaya943/Shilaycow-trial/issues/1#issuecomment-7065884506))。沒有情境涵蓋並行,所以沒有修;要不要加鎖請 Owner 決定。
- 兩個行為沒有嚴格的「先紅後綠」:冪等測試 3c05331 一寫就綠(由驗證者用突變確認它會失敗);`drive.sh` 的修正 5243bed 沒有自動測試,只有前後實跑紀錄。
- 缺 `title`、`title` 不是字串、編號不是整數時,回的是 FastAPI 預設的 422(格式與固定訊息不同),沒有測試;多餘的欄位會被默默忽略。
- `brief.md` 第 3 行仍寫「狀態:草稿,等 Owner 核准」;我沒有改 brief。
- 這個 PR 也會把試跑用的東西帶進 `main`:`.claude/skills/` 下的 Shilaycow skills、`.shilaycow/config.yml`、`.shilaycow/pitfalls.md`、`docs/tasks/todo-api/trial-notes.md`。
- 整體驗證針對的是 f091b8a;之後這個分支只多了 retro、這份報告與試跑筆記(都是文件),沒有再驗證一次。
- builder、驗證者與 Chief 都用同一個帳號 `bullet-bots`,從 GitHub 上分不出誰貼了哪則留言。

## 驗證結果

- [PR #2 的裁決](https://github.com/pitaya943/Shilaycow-trial/pull/2#issuecomment-7065724124):PASS(f410029)。7 個測試通過、實跑 drive、逐一重現每個紅與綠、破壞空白檢查做抽查;另外發現 `drive.sh` 連續執行的缺陷。
- [PR #3 的裁決](https://github.com/pitaya943/Shilaycow-trial/pull/3#issuecomment-7065811909):PASS(36b7944)。10 個測試通過;確認 `drive.sh` 修好(12 次連跑都是編號 1,埠被佔用時 exit 1);兩個突變抽查。
- [整個分支的裁決](https://github.com/pitaya943/Shilaycow-trial/issues/1#issuecomment-7065884506):PASS(f091b8a)。在 17 個 commit 上重跑測試、實跑五個情境、對 `main` 做 blast-radius(上面的並行發現)。

三位驗證者都是獨立的新 session,沒有參與建造。

## 情境

| 情境 | 做到 | 證據 |
|---|---|---|
| S-1 新增一筆待辦 | 是 | `tests/test_create_list.py::test_create_returns_todo_with_id_title_not_done`;[drive 紀錄](../evidence/T-02-drive.txt);[裁決](https://github.com/pitaya943/Shilaycow-trial/issues/1#issuecomment-7065884506) |
| S-2 列出待辦 | 是 | `tests/test_create_list.py::test_list_returns_todos_in_insertion_order`;同上 |
| S-3 標為完成 | 是 | `tests/test_complete.py::test_complete_marks_only_that_todo_done`;同上 |
| S-4 空白的標題 | 是 | `tests/test_create_list.py::test_blank_title_is_rejected_and_list_unchanged`;同上 |
| S-5 不存在的待辦 | 是 | `tests/test_complete.py::test_complete_unknown_id_is_not_found`;同上 |
