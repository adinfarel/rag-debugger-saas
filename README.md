# Autonomous RAG Hallucination Debugger SaaS 

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![LangGraph](https://img.shields.io/badge/Framework-LangGraph-blue?style=for-the-badge)
![Groq](https://img.shields.io/badge/LLM-Groq-orange?style=for-the-badge)

## Project Synopsis
This project is an advanced AI system that analyzes Large Language Model (LLM) or Retrieval-Augmented Generation (RAG) outputs to detect hallucinations, evaluate answer quality, identify root causes, and automatically provide actionable suggestions for improvement. 

It leverages a **multi-agent architecture**, **memory systems**, and **self-reflection loops** to act as an Autonomous LLM Reliability Engineer.

## Core Capabilities
- **Claim Extraction & Verification:** Semantically checks claims against retrieved context.
- **Multi-Agent Orchestration:** Utilizes specialized agents (Planner, Reasoner, Critic, Evaluator, Suggestion).
- **Advanced Memory System:** Implements short-term, long-term, semantic, and failure memories to learn from past hallucinations.
- **Self-Reflection Loop:** Iteratively evaluates and refines outputs until quality thresholds are met.
- **Auto Retrieval Tuning:** Dynamically adjusts chunk size, top-k, and reranker settings based on failure analysis.

## Architecture
The system follows a frontier-grade SaaS architecture:
`Gateway API -> Planner Agent -> Task Decomposition -> Multi-Agent Workflow -> Memory Integration -> Self-Reflection -> Evaluation Output`

## Project Structure
```text
rag-debugger-saas/
├── app/                  # Backend application
│   ├── api/              # FastAPI endpoints
│   ├── core/             # Configuration, Logging, and LLM base engine
│   ├── agents/           # Multi-agent logic (LangGraph nodes & state)
│   ├── memory/           # Memory management systems
│   ├── evaluators/       # Hallucination scoring logic
│   └── tools/            # Agent tool registry
├── frontend/             # Vanilla HTML/JS/CSS demo interface
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
├── requirements.txt      # Python dependencies
└── main.py               # Application entry point
```

## Getting Started
  1. Clone the repository:
     
     ```bash
     git clone [https://github.com/yourusername/rag-debugger-saas.git](https://github.com/yourusername/rag-debugger-saas.git)
    cd rag-debugger-saas
     ```
  2. Set up virtual environment:
     
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```
  2. Install dependencies:
     ```bash
     pip install -r requirements.txt
     ```
  4. Environment Variables:
     Create a .env file in the root directory and add your Groq API key:
     ```text
     GROQ_API_KEY=your_api_key_here
     ENVIRONMENT=development
     LOG_LEVEL=INFO
     ```
  5. Run the Application:
     ```bash
     python main.py
     ```
