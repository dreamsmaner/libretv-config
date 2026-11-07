# libretv-config

把 [hafrey1/LunaTV-config](https://github.com/hafrey1/LunaTV-config) 长期维护的视频源，
自动转换成 [LibreTV](https://github.com/LibreSpark/LibreTV) 认的 SourceList v2 格式，
生成一份固定地址的订阅文件。源数据属于上游维护者，本仓库只做格式转换，供个人使用。

## 订阅链接（LibreTV 里填这个）

```
https://raw.githubusercontent.com/dreamsmaner/libretv-config/main/sources.json
```

在 LibreTV：设置 → 源管理 → 数据源订阅 → 填入上面的地址订阅；
再把这条订阅的自动刷新周期设为 1 天，之后全自动。

## 怎么运作

- GitHub Actions 每天 05:30（Asia/Shanghai）运行 `convert.py`：
  拉取上游 `LunaTV-config.json` → 转换 → 只有内容变化时才提交新的 `sources.json`。
- 也可以在 Actions 页面手动触发（workflow_dispatch）立即更新一次。

## 转换规则

| LunaTV-config | LibreTV SourceList |
| --- | --- |
| `api_site.*.name` | `sources[].name` |
| `api_site.*.api` | `sources[].url` |
| `api_site.*.detail` | `sources[].detail` |
| 名称含 🔞 | `sources[].isAdult = true` |

过滤策略：上游用 `_comment` 标坏的源（无法搜索 / 无搜索结果 / 污染搜索结果 /
403 / 禁止搜索等）会被剔除；标「备用」「不稳定」的保留。
上游日后修好某源、去掉注释，它会在次日转换中自动回归。

## 保险丝

- 上游拉取失败、格式变化、或转换结果为 0 条时，脚本直接报错退出，
  **不覆盖**已发布的 `sources.json`，订阅链接继续提供上一份好文件。
- 每天的版本都在 git 历史里；需要回滚时，把订阅地址临时指向某个旧 commit 的
  `sources.json` 即可。
