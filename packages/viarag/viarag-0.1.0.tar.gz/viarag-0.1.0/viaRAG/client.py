import json
from typing import Optional, List, Dict, Any
from pathlib import Path

import requests


class ViaRAGClient:
    """
    Minimal SDK for ViaRAG API.
    """

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Args:
            api_key: Bearer token for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = "https://viarag-backend-prod-104241861537.us-central1.run.app"
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def health_check(self) -> Dict[str, Any]:
        """
        Returns API health status.
        """
        url = f"{self.api_url}/api/v1/simple/health"
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def simple_query(self, prompt: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Runs a retrieval-augmented generation query.
        """
        url = f"{self.api_url}/api/v1/simple/query/"
        payload = {"prompt": prompt, "top_k": top_k}
        resp = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def direct_query(self, prompt: str) -> Dict[str, Any]:
        """
        Runs prompt directly through LLM without retrieval.
        """
        url = f"{self.api_url}/api/v1/simple/query/direct"
        payload = {"prompt": prompt}
        resp = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def match_context(self, prompt: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves top-k matching context chunks.
        """
        url = f"{self.api_url}/api/v1/simple/query/match"
        payload = {"prompt": prompt, "top_k": top_k}
        resp = requests.post(url, json=payload, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def upload_document(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        chunking_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Uploads and processes a document.

        Args:
            file_path: Path to the file (PDF, DOCX, TXT)
            metadata: Optional metadata dict
            chunking_config: Optional chunking config dict
        """
        url = f"{self.api_url}/api/v1/simple/upload"
        data = {}

        if metadata is not None:
            data["metadata"] = json.dumps(metadata)
        if chunking_config is not None:
            data["chunking_config"] = json.dumps(chunking_config)

        # Use 'with' to ensure file is closed automatically
        with open(file_path, "rb") as f:
            files = {"file": (Path(file_path).name, f)}
            resp = requests.post(
                url,
                headers=self.headers,
                files=files,
                data=data,
                timeout=self.timeout,
            )

        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # Print server error details for easier debugging
            print("Upload failed.")
            print("Status Code:", resp.status_code)
            print("Response Body:", resp.text)
            raise

        return resp.json()

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        splitter: str = "recursive",
    ) -> List[str]:
        """
        Splits raw text into chunks.
        """
        url = f"{self.api_url}/api/v1/simple/chunk"
        payload = {
            "text": text,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "splitter": splitter,
        }
        resp = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()["chunks"]

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        Lists all uploaded documents.
        """
        url = f"{self.api_url}/api/v1/advanced/documents/list"
        resp = requests.get(url, headers=self.headers, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()["documents"]

    def delete_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """
        Deletes all vectorstore chunks for a document ID.
        """
        url = f"{self.api_url}/api/v1/advanced/delete/delete/by-doc-id"
        payload = {"doc_id": doc_id}
        resp = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
