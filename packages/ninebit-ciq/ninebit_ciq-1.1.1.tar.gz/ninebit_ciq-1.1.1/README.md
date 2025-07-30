# Python SDK for RAG (Retrieval Augmented Generation)

![](banner.png)
[![Version](https://img.shields.io/pypi/v/ninebit-ciq)](https://pypi.org/project/ninebit-ciq)
[![License](https://img.shields.io/github/license/NineBit-Computing/ciq-py-client)](https://github.com/NineBit-Computing/ciq-py-client/blob/main/LICENSE)
[![build](https://img.shields.io/github/actions/workflow/status/NineBit-Computing/ciq-py-client/ci.yml?branch=main)](https://github.com/NineBit-Computing/ciq-py-client/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: flake8](https://img.shields.io/badge/linting-flake8-blue)](https://flake8.pycqa.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NineBit-Computing/ciq-py-client/blob/main/examples/ciq_rag_demo.ipynb)

## 🔗 ninebit-ciq

**Official Python SDK client for interacting with [NineBit CIQ](https://ciq.ninebit.in?utm_source=pypl)**, a Retrieval-Augmented Generation (RAG) workflow orchestration platform for secure, private, rapid prototyping of AI/ML ideas using enterprise data and open-source models.

Join the community:

[![Join us on Slack](https://img.shields.io/badge/Slack-join%20chat-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://join.slack.com/t/ninebit-ciq-community/shared_invite/zt-38oi663on-9R~0J8echKGQ8NV2zRKJZA)

## 🚀 Try It Out Interactively

We provide an interactive **Jupyter notebook demo** to quickly explore NineBit CIQ’s features like ingestion, summarization, taxonomy extraction, and more.

### 🧪 Run the notebook in Google Colab

Click below to launch the demo with zero setup:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NineBit-Computing/ciq-py-client/blob/main/examples/ciq_rag_demo.ipynb)

---

### 🌐 Explore Our Hugging Face Space

Try the live demo running on Hugging Face Spaces — no installation needed, just open and run:

[https://huggingface.co/spaces/ninebit/ciq-rag](https://huggingface.co/spaces/ninebit/ciq-rag)

---

For more details, see [examples/ciq_rag_demo.ipynb](./examples/ciq_rag_demo.ipynb).

## 🚀 Features

- Retrieval-Augmented Generation (RAG)
  Perform semantic search and intelligent query answering using hybrid retrieval techniques.
- Flexible Query Interface
  Send queries with configurable similarity thresholds and top_k result tuning.
- Callback Support for Asynchronous Workflows
  Pass in callbacks to handle results or errors once workflows complete — ideal for event-driven applications.
- Workflow Polling with Timeout Control
  Monitor long-running workflows with built-in polling, status checking, and customizable timeouts.
- Simple, Extensible API
  Clean, Pythonic interfaces with support for both synchronous returns and optional callbacks.
- Error-Handled Execution Flow
  Graceful handling of task failures, timeouts, and unexpected states with descriptive exceptions.
- Logging Support
  Integrated logging for easy debugging and transparency during polling or querying.

## 📦 Installation

```bash
pip install ninebit-ciq
```

Or clone and install locally:

```
git clone https://github.com/NineBit-Computing/ciq-py-client.git
cd ciq-py-client
pip install .
```

## 🧪 Quickstart (Python)

```python
from ninebit_ciq import NineBitCIQClient

client = NineBitCIQClient(
    api_key="YOUR_API_KEY"
)

def on_done(error, data):
    if error:
        print(f"Ingest_file failed: {error}")
    else:
        print(f"Ingest_file succeeded: {str(data)}")

# 1. Ingest file as datasource for performing RAG
client.ingest_file(file="files/my_file.pdf", callback=on_done)

# 2. Ask your query
query = "What are land breeze?"
response = client.rag_query(query=query)
print(f"Query response is {response}")

```

## 🔐 Authentication - You’ll Need an API Key

If you’re using the Freemium CIQ setup, you’ll just need to register at our web app and grab your API key. It’s quick, and no credit card is required.

You can sign up here [NineBit CIQ](https://ciq.ninebit.in?utm_source=pypl)

## 📚 SDK Reference

| Method          | Description                                                                     |
| --------------- | ------------------------------------------------------------------------------- |
| `ingest_file()` | Reads and uploads a PDF or DOCX file to the backend for processing.             |
| `rag_query()`   | Performs a Retrieval-Augmented Generation (RAG) query using the provided input. |
|                 |

## 🛠️ Logging

You can control logging verbosity:

```python
from ninebit_ciq import NineBitCIQClient
import logging

client = NineBitCIQClient(api_key, log_level=logging.INFO)
```

## 📁 Project Structure

```
ciq-py-client/
├── src/ninebit_ciq/
│ ├── client.py # Core SDK logic
│ ├── logger.py # Logger setup
│ ├── cli.py # CLI interface
│ └── **init**.py # Version info
├── examples/usage.py
├── examples/usage_with_thread.py
├── README.md
├── setup.py
└── version.txt
```

## 📄 License

MIT License © NineBit Computing

## 🤝 Contributing

Pull requests are welcome! Please check DEVELOPER.md and ensure:

- Tests pass
- Lint/format clean
- Coverage is not broken

## 📬 Questions?

Email us at support@ninebit.in or visit [NineBit Computing](https://ninebit.in?utm_source=pypl) or raise an issue in the GitHub repo.

© NineBit Computing, 2025
