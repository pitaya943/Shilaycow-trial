# Pitfalls

## 驗收條件寫成靠時序才會失敗的指令

- 發生了什麼:T-02 的票把「連跑三次都是 id 1」當作修好的標準,沒修的腳本也會偶然通過(c5da171;builder 在 https://github.com/pitaya943/Shilaycow-trial/pull/3#issuecomment-7065779044 指出)。
- 怎麼避免:票的驗收條件要寫成沒修時必然失敗的步驟(例如先在埠上放一個已知的服務),不要靠競態碰運氣。
- 次數:1
- Sources: #1

## 簡述沒說、使用者實際會碰到的邊界沒有人決定

- 發生了什麼:due-dates 合併後,Owner 試用時發現標題再長服務也照單全收。簡述沒有規範長度;寫簡述的人沒想到,建置的人沒問,驗收的人沒列出來(https://github.com/pitaya943/Shilaycow-trial/issues/5#issuecomment-7067943648)。
- 怎麼避免:寫簡述時把長度、大小、數量的上限,空的與重複的輸入,同時多人,資料存多久,逐項給一個預設並寫在「假設」;驗收時試極端的輸入,沒有規範的列為 `unspecified`。
- 次數:1
- Sources: #5
