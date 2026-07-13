# Peter AI Companion｜雙模式語音陪跑 V1.0 RC1

這是一套可交給 Codex 驗證、擴充及整合的「語音優先」規則封裝。

## 兩層模式

### 互動層
- `voice_companion`：語音陪跑模式，預設。
- `quiet_slow`：安靜慢慢來模式，一次只給一個主要下一步。

### 執行層
- `planning`：Mode A｜企劃討論，預設。
- `formal_generation`：Mode B｜正式生成。只有精確觸發詞 `【正式生成影片】` 且三道門全部通過才可啟用。

兩層模式不得混用：語音陪跑不等於影片生成授權。

## 核心安全規則

- 雲端權限預設為私人。
- Supervisor／主管存取必須由 Peter 明確授權。
- 密碼、驗證碼、API Key、Token、私鑰等敏感資訊會觸發 Safety Stop。
- 不宣稱固定全天候後台支援。
- 未連接實際雲端或執行工具時，只能回報「已整理操作方案，尚未實際執行」。

## 執行

```bash
python tools/run_all.py
```

或：

```bash
python -m unittest discover -s tests -v
```
