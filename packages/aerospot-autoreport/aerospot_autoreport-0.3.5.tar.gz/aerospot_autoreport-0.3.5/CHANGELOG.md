# Changelog

All notable changes to AutoReportV2 will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### 🚀 Added
- 采用setuptools_scm进行自动版本管理
- 完善的CI/CD流水线，支持自动发布到PyPI
- 跨平台兼容性优化（Windows/Linux/macOS）
- 智能版本获取机制（包元数据 > _version.py > fallback）
- 多Python版本测试支持（3.10、3.11、3.12）
- 推荐使用Python 3.11以获得最佳性能和特性支持

### 🔧 Changed
- 项目名称从autoreport-v3更改为autoreport-v2
- 版本管理方式从手动维护改为Git标签驱动
- 改进了包结构和依赖管理
- 优化了COM自动化路径处理（Windows系统）

### 🐛 Fixed
- 修复了Windows系统WSL路径转换问题
- 解决了目录字体设置在不同平台的兼容性问题
- 修复了setuptools_scm在CI环境中的版本识别问题

### 📝 Documentation
- 添加了Python包版本管理最佳实践文档
- 完善了安装和使用说明
- 增加了开发环境配置指南

## [2.0.0] - 待发布

### 🎉 首次发布
- 基于AutoReportV3重构的全新版本
- 支持自动化遥感数据处理和报告生成
- 提供命令行工具和Python API
- 包含完整的CI/CD配置

---

## 版本管理说明

从此版本开始，AutoReportV2采用以下版本管理策略：

1. **语义版本控制**: 遵循 `主版本.次版本.修订版本` 格式
2. **Git标签驱动**: 版本号完全由Git标签决定
3. **自动化发布**: 推送标签自动触发CI/CD流水线
4. **多级fallback**: 确保在任何环境下都能正确获取版本号

### 发布流程

```bash
# 1. 提交代码
git add -A
git commit -m "feat: 新功能描述"

# 2. 创建标签
git tag v2.0.0

# 3. 推送代码和标签
git push origin main
git push origin v2.0.0
```

推送标签后，GitHub Actions将自动：
- 构建并测试包
- 发布到PyPI
- 创建GitHub Release
- 生成发布说明