# 飛書幫助中心（Feishu Help Center Skill）

把飛書（Feishu / Lark 中國版）官方幫助中心 **feishu.cn/hc/zh-CN** 鏡像成可離線檢索的 Agent Skill：
2,529 篇官方文章全文、643 組官方問答、24 條產品線索引，搭配兩支零依賴的 Python 檢索腳本。

讓 AI 回答「飛書怎麼操作／怎麼設定／為什麼報錯／有什麼限制」時，能像查過官方文件一樣，給出**帶連結、帶版本前提**的答案。

> 非官方專案。所有文章內容版權屬飛書官方，本專案僅作離線檢索索引之用。

## 資料規模

| 項目 | 內容 |
|---|---|
| 來源 | https://www.feishu.cn/hc/zh-CN/ |
| 快照日 | 2026-11-19 |
| 分類 | 364 個 |
| 文章 | 2,572 篇（其中 2,529 篇有正文，約 365 萬字） |
| 官方問答 | 643 組 |
| 產品線索引 | 24 條 |
| 體積 | 約 4.3 MB（`data/articles.jsonl.gz` 佔 2.98 MB） |

## 目錄結構

```
SKILL.md                    技能說明：使用時機、四層取用流程、產品地圖、回答規範
references/
  產品速覽.md               全產品線速覽
  目錄總覽.md               364 分類全貌
  產品-<產品線>.md          24 條產品線索引（云文档、多维表格、审批、视频会议…）
  高頻問答.md               643 組官方 FAQ 問答
scripts/
  hc_search.py              全文／FAQ／產品線檢索（純標準庫）
  hc_fetch.py               即時抓取官網單篇文章（純標準庫）
data/
  articles.jsonl.gz         2,529 篇全文語料（gzip JSONL）
  meta.json                 語料元資訊
```

## 安裝

把整個目錄放進你的 Agent skills 路徑即可，例如：

```bash
git clone https://github.com/tmnfjk6m-max/feishu-help-center-skill.git ~/.claude/skills/飛書幫助中心
# 或豆包工作模式
cp -R feishu-help-center-skill "$HOME/Library/Application Support/DoubaoWork/Default/.doubaowork/agent_mode/workspace/.skills/飛書幫助中心"
```

不需要額外套件：兩支腳本只用 Python 3 標準庫。

## 用法

四層取用，命中即停：**速答 → 產品線索引 → 全文檢索 → 即時抓取**。

```bash
# 1. 查官方問答（「為什麼／能不能／上限多少」多數在這裡）
python3 scripts/hc_search.py --faq 会议 加密

# 2. 全文檢索（回傳標題、分類、連結與命中片段）
python3 scripts/hc_search.py 多维表格 高级权限 --limit 5

# 3. 限定產品線
python3 scripts/hc_search.py --product 审批 转交 --limit 5

# 4. 語料沒有或懷疑改版，直接抓線上原文
python3 scripts/hc_fetch.py https://www.feishu.cn/hc/zh-CN/articles/410718208321-工作台介绍
```

Agent 載入 `SKILL.md` 後會自動依此流程取用，並在回答時附上原文連結與版本前提。

## 適用範圍

**適合**：功能操作步驟、權限與角色要求、人數／容量／大小等限制、報錯排查、管理後台設定、版本差異與更新記錄。

**不適合**：開放平台 API 文件（另有開發者站）、Lark 國際版（命名與計費不同）、企業內部自訂政策。

## 已知邊界

- 只鏡像文字，圖片／影片／附件未下載；純看圖的步驟需開原文。
- 極少數已下架文章正文為空。
- 「先进实践」多為客戶案例敘事，「产品更新」為更新日誌，皆不宜當操作手冊。
- 語料為 2026-11-19 快照；數字型限制與介面路徑可能已變動，建議用 `hc_fetch.py` 覆核。
- 本專案不含爬蟲本體（`crawl_feishu_hc.py`、`build_skill_data.py` 等留在原維護環境），此處僅發佈成品語料與檢索腳本。

## 授權與免責

- **程式碼**（`scripts/`）: MIT License。
- **文章內容**（`data/`、`references/`）: 版權屬北京飛書科技有限公司（飛書官方），來源為 https://www.feishu.cn/hc/zh-CN/ 。此處收錄僅為離線檢索與引用之便，轉載、商用或大量再散布前請自行確認並取得官方授權，並保留原文連結。
- 本專案與飛書官方無隸屬關係，不對內容時效性與正確性作保證；正式決策請以官網當日版本為準。

## 更新

語料建議每季重抓一次，飛書大版本（V8.x）發布後優先補。重新生成後替換 `data/` 與 `references/`，並更新 `SKILL.md` 與 `data/meta.json` 內的 `scraped_at`。
