# CI 說明

本專案的驗證指令：

```bash
python tools/run_all.py
```

驗證範圍：

- 24 項路由與安全單元測試
- 正式產品名稱契約
- 正式影片生成精確觸發詞
- 腳本、分鏡、生成確認三道門
- 雲端私人權限預設
- Supervisor 明確授權
- Safety Stop

GitHub Actions 工作流程位於 `.github/workflows/peter-companion-ci.yml`。
