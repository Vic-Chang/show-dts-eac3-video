# show-dts-eac3-video

## 介紹

因為 Synology NAS 在 Video Station [專利授權](https://kb.synology.com/zh-tw/DSM/tutorial/Why_can_t_I_play_videos_with_DTS_or_EAC3_audio_format_on_Video_Station) 上的關係，導致無法撥放 DTS 與 EAC3 音訊格式。

但在 Video Station 上卻沒辦法以條列式方式顯示所有影音檔案的音頻格式，只能一個一個慢慢點開看，且 Synology 也無提供 Video Station API, 導致若有上百個影片檔案，那會非常費時。

所以寫了這個東西去抓所有影片檔案，並且去檢視該檔案的音頻格式。若是發現有包含專利授權的音頻格式，並且 **Video Station 無法撥放** 就顯示該檔案的名稱、路徑、格式並紀錄起來。( 影片若包含其它可撥放的音頻則不列入，如 AC3, AAC 格式等 )

但因為不想要全域汙染到 NAS 環境，所以決定以 **`Docker`** 的方式隔離環境。至於讀取 Host 的影片則使用掛載 `Volumes` 的方式讓他與 NAS Host 做連結，這樣就解決了汙染環境的問題。並且因為 Docker container 在程式運行結束後會關閉，若重啟該 Container 將再次重新檢查所有檔案，達成了一鍵檢查、易於使用的目的。

## 功能

檢索資料夾底下的所有檔案 ( 包含子資料夾 )，並抓出所有**只有** DTS 或是 EAC3 音軌的影片檔案，並且將執行結果儲存為檔案供查詢。

## 部屬設定與掛載 Volumes

這裡以使用 Docker image 的方式在 Synology docker 部屬為例。

在部屬 Image 時，**請務必取消選擇「啟用自動重啟」**，避免無限循環。

### 掛載 Config 以及 Results 結果資料夾

於部屬時，可選擇掛載 `Config.ini` 設定檔以及 `Results` 資料夾。

* 掛載 `Config.ini` 檔案  
部屬時選擇「新增檔案」，並選擇 `Config.ini` 檔案位置，設定掛載路徑為 「`/config.ini`」

* 掛載 `Results` 資料夾  
部屬時選擇「新增資料夾」，選擇一個存放 Log 的資料夾位置，設定掛載路徑為 「`/Results`」

#### Config 參數設定

於 ini 檔內參數有兩個，一個是 `ShowDetail`, 另一則是 `ProcessCount` 。

`ShowDetail` 預設為 0

> 設定為 0 ，執行結果將只儲存無法於 Video Station 上撥放的影片之檔案及音軌資訊  
> 設定為 1 ，執行結果將儲存所有檔案的所有音軌詳細格式資訊

`ProcessCount` 預設為 2

> 該設定為設定程式執行的 Process 數量，可依照 CPU 效能增減。**在 CPU 能負荷的程度下**，越多的 Process 數量，程式執行速度將會越快。  
> 以 DS218+ 為例子，設定為兩個 Process 剛好可將 CPU 性能榨光提以升執行效率。 ( 約莫剛好能將 CPU 效能吃到 95% 上下)  
> 可依照需求或 CPU 性能增加或減少 Process 數量。

### 設定掛載影片資料夾

可將 Host 上欲檢查的影片資料夾掛載至 「`/VideoFolder`」 資料夾即可。若有多個分散的影片資料夾，可將他們分批掛載至 「`/VideoFolder/0`」, 「`/VideoFolder/1`」, 「`/VideoFolder/2`」 ... 等。

程式執行時將會針對這些掛載的資料夾內所有檔案逐個去做確認。

## 執行與執行結果

在完成部署後，啟動 Container 時，程式將自動去檢索設定掛載的資料夾，這可能會需要一段時間，依照 CPU 性能以及 Process 設定數量而定。

在完成檢查所有檔案後，會將結果寫至掛載的 Results 資料夾上。**並自動關閉該 Container** 。

若未來有需要重新檢查影片，只要一鍵重啟該 Container 即可再次檢查。

## 執行結果截圖

![簡易輸出結果](https://user-images.githubusercontent.com/16682813/164535693-10f48265-2663-4478-9042-c32508889064.png)

> 設定簡易輸出，處理結果僅顯示 Video Station 無法撥放的檔案以及該檔案的格式

![詳細輸出結果](https://user-images.githubusercontent.com/16682813/164535713-ec27b04a-54bc-424a-a3ef-d502572525b6.png)

> 設定詳細輸出，處理結果將顯示所有影片檔案之所有音軌格式，最後並總結列出 Video Station 無法撥放的檔案以及格式
