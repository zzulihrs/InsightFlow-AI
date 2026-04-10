# InsightFlow-AI

InsightFlow-AI 是一个面向 AI 行业资讯的分析日报项目。系统从多来源新闻中读取数据，完成结构化抽取、多维评分、过滤聚类和日报生成，最终输出 HTML 结果文件。

## 项目内容

仓库当前保留以下核心内容：

- `src/`：核心 Pipeline 代码
- `prompts/`：Prompt 模板
- `data/raw/raw_news.json`：原始数据文件
- `data/output/<date>/`：运行结果示例
- `docs/`：说明文档
- `.env.example`：本地环境变量配置示例

## 运行前准备

本项目依赖本地可用的 Claude CLI 才能运行真实的抽取、评分和洞察生成链路，因此不是开箱即跑。

运行前需要完成以下本地配置：

1. 安装并确保本机可以正常调用 Claude Code CLI
2. 复制 `.env.example` 为 `.env`
3. 在 `.env` 中填写本机实际可用的配置项：

- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`

如果没有完成这些本地配置，项目将无法调用 Claude，也就无法跑通真实的 AI 分析流程

## 运行方式

```bash
python main.py --date 2026-04-11
```

运行完成后，结果会写入：

```text
data/output/<date>/
```

主要输出包括：

- `structured.json`
- `scored.json`
- `report.json`
- `report.md`
- `report.html`
- `pipeline_log.json`

## 查看方式

当前项目以 HTML 报告为主，可直接在浏览器中打开：

```text
data/output/2026-04-11/report.html
```

## 说明文档

说明文档已拆分为四份，可通过以下链接查看：

1. [数据源说明](docs/1_数据源说明.md)
2. [系统设计思路](docs/2_系统设计思路.md)
3. [AI 使用方式](docs/3_AI使用方式.md)
4. [核心流程说明](docs/4_核心流程说明.md)
