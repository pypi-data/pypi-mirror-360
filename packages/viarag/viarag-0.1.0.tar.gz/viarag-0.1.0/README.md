# ViaRAG SDK

Minimal Python SDK for interacting with the [ViaRAG API](https://viarag.ai).
Designed for developers building RAG pipelines, chatbots, and AI-native workflows.

---

## 📦 Installation

```bash
pip install viarag
```

---

## 🚀 Quickstart

```python
from viarag import ViaRAGClient

client = ViaRAGClient(api_key="your_api_key")
print(client.health_check())
```

---

## 🔧 Class: `ViaRAGClient`

### `ViaRAGClient(api_key: str, timeout: int = 30)`

Creates a new client.

---

## 📡 Endpoints

### ✅ 1. `health_check()`

Returns the API's current health status.

```python
client.health_check()
```

**Returns:**

```json
{"status": "ok"}
```

---

### 🤖 2. `simple_query(prompt: str, top_k: int = 5)`

Runs a **retrieval-augmented generation (RAG)** query.

```python
client.simple_query("What is ViaRAG?")
```

**Returns:**

```json
{
  "response": "ViaRAG is an API for retrieval-augmented generation...",
  "contexts": [...],
  "prompt": "..."
}
```

---

### 💬 3. `direct_query(prompt: str)`

Runs a prompt **directly through the LLM**, no retrieval.

```python
client.direct_query("Tell me a joke.")
```

---

### 🔍 4. `match_context(prompt: str, top_k: int = 5)`

Returns **top-k context chunks** that match your prompt (no generation).

```python
client.match_context("What is ViaVeri?")
```

**Returns:**

```json
[
  {"content": "...", "score": 0.92},
  {"content": "...", "score": 0.87}
]
```

---

### 📄 5. `upload_document(file_path: str, metadata: dict = None, chunking_config: dict = None)`

Uploads a document and indexes it.

```python
client.upload_document(
    file_path="my_notes.pdf",
    metadata={"source": "user-upload"},
    chunking_config={"chunk_size": 1000, "chunk_overlap": 200}
)
```

Supports: `.pdf`, `.docx`, `.txt`

---

### ✂️ 6. `chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200, splitter: str = "recursive")`

Chunks raw text without uploading a file.

```python
chunks = client.chunk_text("A long string of text...")
```

**Returns:**

```json
["Chunk 1", "Chunk 2", ...]
```

---

### 📚 7. `list_documents()`

Lists all documents you’ve uploaded.

```python
client.list_documents()
```

**Returns:**

```json
[
  {"doc_id": "abc123", "filename": "my_notes.pdf"},
  ...
]
```

---

### ❌ 8. `delete_document_by_id(doc_id: str)`

Deletes all chunks associated with a document.

```python
client.delete_document_by_id("abc123")
```

---

## 🔐 Authentication

All API calls (except `health_check`) require a **Bearer token**:

```python
client = ViaRAGClient(api_key="sk-...")
```

---

## 🧪 Development

Clone the repo and install locally:

```bash
git clone https://github.com/YOUR_USERNAME/viarag-sdk.git
cd viarag-sdk
pip install -e .
```

---

## 📄 License

GNU General Purpose License. See `LICENSE` file.

---

## 👋 About

Built by [ViaVeri Technologies](https://viaveri.co) to empower developers with simple, powerful RAG tools.
