# DevAI-Agent: Autonomous PR & Code Review Assistant

[![Python Version](https://shields.io)](https://python.org)
[![Framework](https://shields.io)](https://tiangolo.com)
[![Docker](https://shields.io)](https://docker.com)

An production-grade autonomous agent built to automate GitHub PR reviews, catch logical bugs, run test verification suites, and generate accurate code patches. The core architecture uses an asynchronous event-driven layout combined with a dedicated runtime container to guarantee safe code execution during testing.

---

## 📁 Repository Directory Structure

```text
ai-pr-agent/
├── app/             # Main application core (FastAPI backend & webhook routing)
├── sandbox/         # Code isolation execution layer (Docker runtime environment)
├── evaluation/      # Benchmark verification matrix & evaluation scripts
├── .env             # Global service secrets and credentials file
└── requirements.txt # Explicit third-party Python package requirements
```

---

## 🏗️ Technical Architecture & Module Design

### 1. Webhook Engine (`app/`)
* **Event Ingestion:** Built on **FastAPI**, handling streaming webhooks from GitHub seamlessly with asynchronous background routines.
* **Payload Verification:** Validates automated request payloads natively against SHA-256 signing headers (`X-Hub-Signature-256`).
* **Workflow Delivery:** Extracts pull request diff contexts, issue descriptions, and repository state metadata to dispatch agent operations.

### 2. Isolated Execution Sandbox (`sandbox/`)
* **Volatility Safeguard:** Ensures code mutations are run inside an isolated **Docker** container.
* **Automated Static Analysis:** Runs standard linting configurations, syntax trees checks, and logical unit validation routines.
* **Stdout/Stderr Feedback:** Pipes error stack traces back to the primary LLM processing routine to facilitate multi-turn patch self-correction loops.

### 3. Metric Evaluation (`evaluation/`)
* **Regression Matrix:** Houses targeted benchmarks to evaluate code edit success rates.
* **Accuracy Metrics:** Measures code alignment, pipeline execution success rates, and token ingestion optimization thresholds.

---

## 💻 Hardware & Software Requirements

* **Operating System:** Ubuntu 22.04 LTS / macOS 14+ / Windows 11 with WSL2
* **Container Environment:** Docker Engine v24.0+ / Docker Desktop
* **Runtime Ecosystem:** Python 3.10 or Python 3.11

---

## 🚀 Installation & Local Environment Setup

### 1. Clone & Set Up the Repository Directory
```bash
git clone https://github.com
cd DevAI-Agent/ai-pr-agent
```

### 2. Configure the Security Environment Variables
Initialize your local setup by copying the configuration layout:
```bash
cp .env.example .env
```
Open `.env` and assign your developer credentials:
```env
GITHUB_TOKEN=ghp_your_secure_personal_access_token_here
GITHUB_WEBHOOK_SECRET=your_configured_webhook_signing_secret
OPENAI_API_KEY=sk-proj-your_llm_provider_key
FASTAPI_PORT=8000
```

### 3. Dependency Environment Installation
We recommend using an isolated virtual environment (`venv`) to separate system packages:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🛠️ Usage Instructions

### Run the FastAPI Hook Ingestion Server Local Node
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Evaluation Scripts Independently
To run your benchmarking suite and evaluate your model setup's accuracy thresholds, execute:
```bash
python -m evaluation.run_evals
```

---

## 🛡️ Sandbox Security Boundaries

1. **Ephemeral Lifecycles:** The Docker containers spun up by the `sandbox/` engine are temporary and wiped clear upon execution completion.
2. **Network Egress Block:** Containers are locked down to prevent random remote data leakage during code compilation scripts.
3. **Privilege Limitation:** Host root paths are protected from execution modifications by running container tasks on unprivileged user spaces.
