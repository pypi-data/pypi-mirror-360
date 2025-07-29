<!-- Banner Image -->
<p align="center">
  <img src="assets/banner.png" alt="Isek Banner" width="100%" />
</p>

<h1 align="center">Isek: Decentralized Agent-to-Agent (A2A) Network</h1>

<p align="center">
  <a href="https://pypi.org/project/isek/"><img src="https://img.shields.io/pypi/v/isek" alt="PyPI version" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT" /></a>
  <a href="mailto:team@isek.xyz"><img src="https://img.shields.io/badge/contact-team@isek.xyz-blue" alt="Email" /></a>
</p>

<h4 align="center">
    <a href="README.md">English</a> |
    <a href="README_CN.md">中文</a>
</h4>

---

**Isek** is a decentralized agent network framework designed for building intelligent, collaborative agent-to-agent (A2A) systems. Agents in Isek autonomously discover peers, share context, and cooperatively solve tasks, forming a self-organizing, decentralized society.

With native integration of large language models (LLMs) and a user-friendly CLI, Isek empowers developers and researchers to quickly prototype, deploy, and manage intelligent agent networks.

> 🧪 **ISEK is under active development.** Contributions, feedback, and experiments are highly welcome.

---

## 💡 Why ISEK?

The world is shifting from human-defined workflows and centralized orchestration to autonomous, agent-driven coordination.

While most frameworks treat agents as isolated executors, **ISEK** focuses on the missing layer: **decentralized agent collaboration and coordination**. We believe the future of intelligent systems lies in **self-organizing agent networks** capable of context sharing, team formation, and collective reasoning — all without central control.

ISEK enables:

- 🔍 **Autonomous agent discovery and recruitment** across a peer-to-peer network  
- 🧠 **Model-agnostic intelligence**, allowing agents to use any LLM or backend  
- 🤝 **Composable multi-agent teamwork**, with plug-and-play collaboration protocols  
- 🌐 **Truly distributed deployments**, from local clusters to global swarms  

> ISEK is not just about running agents — it's about empowering them to **find each other, reason together, and act as a decentralized system.**

---

## 🌟 Features

- **🧠 Decentralized Cooperation:**  
  Autonomous peer discovery and agent-to-agent collaboration with no single point of failure.

- **🌐 Distributed Deployment:**  
  Seamless multi-node or cloud deployment for scalability and robustness.

- **🗣️ LLM-Enhanced Intelligence:**  
  Built-in integration with models like OpenAI for natural interaction and reasoning.

- **🔌 Modular and Extensible:**  
  Easily customize agents, add new models, or extend functionalities.

- **💻 Developer-Friendly CLI:**  
  Streamlined CLI for painless agent setup and control.

---

## 📦 Installation

### Quick Install
```bash
pip install isek
isek setup
```

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** (for P2P functionality)

> 💡 **Tip:** The `isek setup` command automatically handles both Python and JavaScript dependencies.

---

## 🚀 Quick Start

### 1️⃣ Set Up Environment

Create a `.env` file:

```env
OPENAI_MODEL_NAME=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key
```

### 2️⃣ Launch Agent

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

### 3️⃣ Try Examples

```bash
# List available examples
isek example list

# Run a simple example
isek example run lv1_single_agent

# Run a more complex example
isek example run lv5_team_agent
```

---

## 🧪 CLI Commands

```bash
isek setup       # Install Python and JavaScript dependencies
isek clean       # Clean temporary files
isek example list # List available examples
isek example run <name> # Run a specific example
isek --help      # View available commands
```

---

## 🧱 Project Structure

```
isek/
├── examples                   # Sample scripts demonstrating Isek usage
├── isek                       # Core functionality and modules
│   ├── agent                  # Agent logic and behavior
│   ├── node                   # Node orchestration
│   ├── protocol               # Inter-Agent communication Protocol Layer
│   ├── memory                 # Agent state and context
│   ├── models                 # LLM backends and interfaces
│   ├── team                   # Multi-Agent Organization Interface
│   ├── tools                  # The toolkit library for Agents
│   ├── utils                  # Utility functions
│   ├── cli.py                 # CLI entry point
│   └── isek_center.py         # Local registry and coordinator
├── docs/                      # Documentation
└── README.md                  # Project overview and documentation
```

---

## 🤝 Contributing

We welcome collaborators, researchers, and early adopters!

* 💬 Open issues or suggestions via [GitHub Issues](https://github.com/your-repo/issues)
* 📧 Contact us directly: [team@isek.xyz](mailto:team@isek.xyz)
* 📄 See our [Contribution Guidelines](CONTRIBUTING.md)

---

## 📜 License

Licensed under the [MIT License](LICENSE).

---
## ⚠️ Legal Notice

ISEK is an open-source, permissionless framework for building decentralized agent coordination systems.  
The contributors do not operate, control, or monitor any deployed agents or their behavior.  
By using this project, you accept full responsibility for your actions. See [LEGAL.md](./LEGAL.md) for more details.

---
<p align="center">
  Made with ❤️ by the <strong>Isek Team</strong><br />
  <em>Autonomy is not isolation. It's cooperation, at scale.</em>
</p>
