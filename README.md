# 想一想樂園

給 2 歲半～5 歲小朋友的邏輯遊戲：這東西應該放哪裡？是誰的？和誰是一對？哪個不一樣？接下來是什麼？誰做的？跟著小狐狸偵探阿布逛樂園的三個園區（卡通城、紙片森林、積木王國，每區一種卡通畫風），一邊玩一邊練分類、配對、規律和推理。

- 設計：[docs/design.md](docs/design.md)，草圖在 `docs/mockups/`。
- 和「[畫畫小鎮](https://github.com/yaufan/APP_Kids_Paint)」「[字母寵物](https://github.com/yaufan/APP_Kids_Paint_for_learning_writing)」「[動物小餐廳](https://github.com/yaufan/APP_Kids_Cook)」「[小卡認天下](https://github.com/yaufan/APP_Kids_Card_Game)」是兄弟 APP：同一個作者、同一套技術、不同畫風。
- 不連網、不定位、沒有廣告、沒有帳號。

## 目前進度
- 0.1 做好了，還沒發布：三個園區（三種卡通畫風）、六個遊戲、三個難度、偵探手冊、休息時間、家長模式、音樂和音效、APP 圖示。版本紀錄在 [CHANGELOG.md](CHANGELOG.md)。

## 程式和素材在哪裡
- `app/`：Flutter 程式。`lib/core/` 是題目、出題規則、存檔、聲音、語音；`lib/features/` 是樂園地圖、六個遊戲（`play/`）、偵探手冊、休息、家長模式。
- `design/art/`：用 Python 畫的圖，三種畫風各一套（`city_*`、`forest_*`、`blocks_*`），阿布和樂園地圖在 `park_art.py`，APP 圖示在 `icon.py`。
- `design/sounds/make_sounds.py`：合成全部的音樂和聲音。
- 測試：在 `app/` 裡 `flutter test`；完整流程 `flutter test test/flow_test.dart`，截圖在 `app/build/screenshots/`。

## 授權
- 非商業使用授權：自己、家人使用，或學校、非營利團體的教學，都可以免費使用、修改、分享，要註明出處。
- 商業用途（販賣、收費、廣告、上架）要先取得作者書面同意。也不可以拿來訓練 AI。
- 細節見 [LICENSE](LICENSE)；別人做的部分（字型）見 [NOTICE.md](NOTICE.md)。
