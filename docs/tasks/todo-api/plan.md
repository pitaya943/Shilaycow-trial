# 待辦事項服務:計畫

一個里程碑,兩張票,依序進行(兩張都會動 `todo_api/app.py` 與 `todo_api/store.py`,而且 T-02 依賴 T-01,所以不能平行)。

| 順序 | 票 | 情境 | 依賴 | 可平行 |
|---|---|---|---|---|
| 1 | [T-01](tickets/T-01.md) 新增與列出待辦,並建立 `drive-todo-api` | S-1、S-2、S-4 | 無 | — |
| 2 | [T-02](tickets/T-02.md) 標為完成 | S-3、S-5 | T-01 | 否 |

## 里程碑 M1:完整的待辦服務

結束時可以完整試的情境:S-1 到 S-5(照 brief 的「怎麼試」,或照 `.claude/skills/drive-todo-api/SKILL.md`)。

`merge_unit: task`,所以 M1 結束就是任務結束:整體驗證 → retro → 最終報告 → 一個往 `main` 的 pull request。
