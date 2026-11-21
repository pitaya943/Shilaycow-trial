# Pitfalls

## 啟動服務的輔助腳本連到不是自己啟動的服務

- 發生了什麼:`drive.sh` 結束時只 kill 不等待,就緒檢查又接受埠上任何回應,連續執行時第二次驅動到上一次還沒關完的服務,紀錄是錯的而且 exit 0(https://github.com/pitaya943/Shilaycow-trial/pull/2#issuecomment-7065724124,修正在 5243bed)。
- 怎麼避免:腳本啟動服務前先確認埠是空的(不是就失敗),就緒後確認自己的行程還活著,結束時 wait 到行程真的退出。
- 次數:1

## 驗收條件寫成靠時序才會失敗的指令

- 發生了什麼:T-02 的票把「連跑三次都是 id 1」當作修好的標準,沒修的腳本也會偶然通過(c5da171;builder 在 https://github.com/pitaya943/Shilaycow-trial/pull/3#issuecomment-7065779044 指出)。
- 怎麼避免:票的驗收條件要寫成沒修時必然失敗的步驟(例如先在埠上放一個已知的服務),不要靠競態碰運氣。
- 次數:1
