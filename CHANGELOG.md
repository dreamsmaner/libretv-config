# Changelog

本仓库的显著变更记录于此。版本号用于标记转换工具与仓库结构的变更；
订阅文件的日常内容更新由 Actions 自动提交，不在此逐日记录。

## [1.1.0] - 2026-11-07

### Added

- 一次转换上游三个版本并分别发布：完整版 `libretv-config.json`、
  精简+18禁 `libretv-config-jingjian.json`、精简版 `libretv-config-jin18.json`
- MIT `LICENSE` 文件
- 本 `CHANGELOG.md`

### Changed

- 每日运行时间改为 19:00 UTC（原 21:30 UTC）
- 转换改为「三份全部转换成功后才写文件」，任一份失败不覆盖已发布文件

### Removed

- `sources.json`（即原完整版产物）更名为 `libretv-config.json`，旧文件删除

## [1.0.0] - 2026-11-07

### Added

- `convert.py`：把 LunaTV-config 完整版转换为 LibreTV SourceList v2，
  含 `_comment` 坏源过滤策略
- GitHub Actions 每日自动转换并提交 `sources.json`
- `README.md`：订阅链接与运作说明
