# libretv-config

把 [hafrey1/LunaTV-config](https://github.com/hafrey1/LunaTV-config) 长期维护的视频源，
自动转换成 [LibreTV](https://github.com/LibreSpark/LibreTV) 认的 SourceList v2 格式，
生成三份固定地址的订阅文件。源数据属于上游维护者，本仓库只做格式转换，供个人使用。

## 订阅链接（LibreTV 里填）

完整版（含 18 禁）：

```
https://raw.githubusercontent.com/dreamsmaner/libretv-config/main/libretv-config.json
```

精简版 + 18 禁（上游已剔除坏源与重复备用源）：

```
https://raw.githubusercontent.com/dreamsmaner/libretv-config/main/libretv-config-jingjian.json
```

精简版（无 18 禁）：

```
https://raw.githubusercontent.com/dreamsmaner/libretv-config/main/libretv-config-jin18.json
```

在 LibreTV：设置 → 源管理 → 数据源订阅 → 填入地址订阅；
再把订阅的自动刷新周期设为 1 天，之后全自动。

> 注意：v1.0 的 `sources.json` 已更名为 `libretv-config.json` 并停止更新，
> 还在用旧链接的请换成上面的完整版链接。

## 怎么运作

- GitHub Actions 每天 **19:00 UTC** 运行 `convert.py`，一次转换上游的三个版本
  （完整版 `LunaTV-config.json`、精简+18禁 `jingjian.json`、精简版 `jin18.json`），
  只有内容变化时才提交新文件。
- 也可以在 Actions 页面手动触发（workflow_dispatch）立即更新一次。

## 转换规则

| LunaTV-config | LibreTV SourceList |
| --- | --- |
| `api_site.*.name` | `sources[].name` |
| `api_site.*.api` | `sources[].url` |
| `api_site.*.detail` | `sources[].detail` |
| 名称含 🔞 | `sources[].isAdult = true` |

过滤策略：完整版里上游用 `_comment` 标坏的源（无法搜索 / 无搜索结果 /
污染搜索结果 / 403 / 禁止搜索等）会被剔除；标「备用」「不稳定」的保留。
两个精简版是上游自己已经筛过的，不带这些标记，转换时原样通过。
上游日后修好某源、去掉注释，它会在次日转换中自动回归。

## 保险丝

- 三个版本全部在内存里转换成功后才写文件；上游拉取失败、格式变化、
  或任一版本转换结果为 0 条时，脚本直接报错退出，**不覆盖**已发布的文件，
  订阅链接继续提供上一份好文件。
- 每天的版本都在 git 历史里；需要回滚时，把订阅地址临时指向某个旧 commit 的
  文件即可。

## 授权说明

本仓库为个人自用项目，不开放任何授权：除法律另有规定外，
未经许可请勿复制、分发或用于其他用途。
视频源数据来自上游 [LunaTV-config](https://github.com/hafrey1/LunaTV-config)，
其权利归上游维护者所有；本仓库仅做格式转换，供个人使用。
