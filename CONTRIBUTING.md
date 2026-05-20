# 🤝 贡献指南

感谢您对 AgenticSqlConverter 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 Bug 报告
- 💡 功能建议
- 📚 文档改进
- 🧪 测试用例
- 🔧 代码贡献

## 🚀 快速开始

### 1. Fork 项目
1. 访问 [AgenticSqlConverter](https://github.com/YOUR_USERNAME/AgenticSqlConverter)
2. 点击右上角的 "Fork" 按钮
3. 选择您的 GitHub 账户

### 2. 克隆仓库
```bash
git clone https://github.com/YOUR_USERNAME/AgenticSqlConverter.git
cd AgenticSqlConverter
```

### 3. 设置开发环境
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装开发依赖
pip install -e ".[dev]"
```

### 4. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

## 📝 贡献类型

### 🐛 Bug 报告

如果您发现了 Bug，请：

1. 检查是否已有相关 Issue
2. 创建新的 Issue，使用 "Bug report" 模板
3. 提供详细的复现步骤
4. 包含错误信息和堆栈跟踪
5. 说明您的环境信息（操作系统、Python 版本等）

### 💡 功能建议

如果您有功能建议，请：

1. 检查是否已有相关 Issue
2. 创建新的 Issue，使用 "Feature request" 模板
3. 详细描述功能需求
4. 说明使用场景和预期效果
5. 如果有实现思路，请一并提供

### 🔧 代码贡献

#### 代码风格

我们使用以下工具确保代码质量：

- **Black**: 代码格式化
- **isort**: 导入排序
- **flake8**: 代码检查
- **mypy**: 类型检查

在提交代码前，请运行：

```bash
# 格式化代码
black .
isort .

# 检查代码质量
flake8
mypy .

# 运行测试
pytest
```

#### 提交规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: add support for Snowflake SQL dialect

- Add Snowflake SQL parser
- Update documentation
- Add test cases

Closes #123
```

### 📚 文档贡献

文档改进同样重要！您可以：

1. 修正拼写错误
2. 改进语法和表达
3. 添加示例代码
4. 完善 API 文档
5. 翻译文档

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_core.py

# 运行测试并显示覆盖率
pytest --cov=agentic_sql_converter

# 运行测试并生成 HTML 覆盖率报告
pytest --cov=agentic_sql_converter --cov-report=html
```

### 添加测试
- 为新功能添加测试用例
- 确保测试覆盖率不降低
- 使用描述性的测试名称
- 遵循 AAA 模式（Arrange, Act, Assert）

## 🔄 工作流程

### 1. 同步上游更改
```bash
git remote add upstream https://github.com/ORIGINAL_OWNER/AgenticSqlConverter.git
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. 更新功能分支
```bash
git checkout feature/your-feature-name
git rebase main
```

### 3. 提交更改
```bash
git add .
git commit -m "feat: your feature description"
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request
1. 访问您的 Fork 仓库
2. 点击 "Compare & pull request"
3. 填写 PR 描述，使用模板
4. 等待代码审查

## 📋 Pull Request 检查清单

在创建 PR 前，请确保：

- [ ] 代码通过所有测试
- [ ] 代码符合风格指南
- [ ] 添加了必要的文档
- [ ] 更新了 CHANGELOG.md
- [ ] 提交信息符合规范
- [ ] 没有敏感信息泄露

## 🏷️ 标签说明

我们使用以下标签分类 Issue 和 PR：

- `bug`: Bug 报告
- `enhancement`: 功能增强
- `documentation`: 文档相关
- `good first issue`: 适合新手的 Issue
- `help wanted`: 需要帮助的 Issue
- `priority: high`: 高优先级
- `priority: low`: 低优先级
- `status: blocked`: 被阻塞的 Issue
- `status: in progress`: 进行中的工作

## 🎯 新手友好

如果您是新手，建议从以下开始：

1. 查看标记为 `good first issue` 的 Issue
2. 阅读现有代码，了解项目结构
3. 从文档改进开始
4. 参与讨论，提出问题

## 📞 获取帮助

如果您需要帮助：

1. 查看 [文档](docs/)
2. 搜索现有 Issue
3. 在 [Discussions](https://github.com/YOUR_USERNAME/AgenticSqlConverter/discussions) 中提问
4. 创建新的 Issue

## 🏆 贡献者

感谢所有为项目做出贡献的开发者！

<!-- 这里会显示贡献者列表 -->

## 📄 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

---

**再次感谢您的贡献！** 🎉

如果您有任何问题或建议，请随时联系我们。
