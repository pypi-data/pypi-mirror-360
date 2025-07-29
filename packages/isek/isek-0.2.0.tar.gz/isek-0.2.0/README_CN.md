
<!-- Banner Image -->
<p align="center">
  <img src="assets/banner_cn.png" alt="Isek Banner" width="100%" />
</p>

<h1 align="center">Isek：去中心化的 Agent-to-Agent (A2A) 网络</h1>

<p align="center">
  <a href="https://pypi.org/project/isek/"><img src="https://img.shields.io/pypi/v/isek" alt="PyPI 版本" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="许可证：MIT" /></a>
  <a href="mailto:team@isek.xyz"><img src="https://img.shields.io/badge/contact-team@isek.xyz-blue" alt="邮箱" /></a>
</p>

<h4 align="center">
    <a href="README.md">English</a> |
    <a href="README_CN.md">中文</a>
</h4>

---

**Isek** 是一个去中心化的Agent网络框架，旨在构建具备智能协作能力的 A2A (Agent-to-Agent) 去中心化网络。Isek 中的Agent能够自主发现其他网络节点、共享上下文并协同解决复杂任务，形成一个自组织的去中心化智能体社区。

Isek 通过高度集成主流大预言模型（LLM）以及Agent通讯协议，帮助开发者和用户快速开发、部署并管理自己的智能体网络。

> 🧪 **ISEK 正在持续完善中。** 欢迎大家贡献代码、参与试用并反馈建议。

---

## 🌟 功能亮点

- **🧠 去中心化协作：**  
  Agent 能自动发现伙伴协作，自组织控制，运行更可靠。

- **🌐 分布式部署：**  
  无缝支持多节点云端部署，具备可扩展性和高可用性。

- **🗣️ LLM 增强智能：**  
  开箱即用支持多个主流大模型，轻松实现智能对话与推理功能。

- **🔌 模块化与可扩展：**  
  可轻松自定义Agent、集成新模型或扩展功能。

- **💻 开发者友好 CLI：**  
  简洁命令行界面，轻松配置与控制Agent。

---

## 📦 安装方式

```bash
pip install isek
```

> 依赖 **Python 3.10+**

---

## 🚀 快速开始

### 1️⃣ 设置环境变量

创建 `.env` 文件：

```env
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key
```

### 2️⃣ 启动Agent

```python
from isek.agent.isek_agent import IsekAgent
from isek.models.openai import OpenAIModel
import dotenv
dotenv.load_dotenv()

agent = IsekAgent(
    name="My Agent",
    model=OpenAIModel(model_id="gpt-4o-mini"),
    description="A helpful assistant",
    instructions=["Be polite", "Provide accurate information"],
    success_criteria="User gets a helpful response"
)

response = agent.run("hello")
```

---

## 🧪 CLI 命令

```bash
isek clean       # 清理临时文件
isek setup       # 安装依赖
isek --help      # 查看可用命令
```

---

## 🧱 项目结构

```
isek/
├── examples                   # Isek 使用示例脚本
├── isek                       # 核心功能模块
│   ├── agent                  # Agent 的逻辑与行为定义
│   ├── node                   # 节点发现与网络编排
│   ├── protocol               # Agent 间通信的协议层
│   ├── memory                 # Agent 的上下文与状态管理
│   ├── models                 # LLM 后端模型接口
│   ├── team                   # 多 Agent 协作与组织结构
│   ├── tools                  # Agent 可调用的function工具库
│   ├── utils                  # 通用工具函数
│   ├── cli.py                 # 命令行入口
│   └── isek_center.py         # 本地注册中心与协调服务
├── script                     # 辅助脚本（如清理工具）
├── pyproject.toml             # 构建配置与依赖声明
└── README.md                  # 项目简介与文档入口
```

---

## 🤝 贡献方式

我们欢迎开发者、研究人员和早期使用者的加入！

- 💬 通过 [GitHub Issues](https://github.com/your-repo/issues) 提出建议或反馈问题
- 📧 联系我们：[team@isek.xyz](mailto:team@isek.xyz)
- 📄 查阅我们的 [贡献指南](CONTRIBUTING.md)，了解如何参与贡献

---

## 📜 开源协议

本项目采用 [MIT License](LICENSE) 开源。

---
## ⚠️ 法律声明

ISEK 是一个开源、无许可的技术框架，旨在支持去中心化智能体协作系统的构建。  
本项目的贡献者不运营、控制或监控任何已部署的智能体或其行为。  
使用本项目即表示您将为自己的行为承担全部责任。详情请参阅 [LEGAL.md](./LEGAL.md)。

---
<p align="center">
  Made with ❤️ by the <strong>Isek Team</strong><br />
  <em>Autonomy is not isolation. It's cooperation, at scale.</em>
</p>
