"""
azure_search.py
Light-weight helper around Azure AI Search for the Pit-Voids Analyser.
Environment variables required
--------------------------------
AZURE_SEARCH_ENDPOINT   e.g. https://<your-service>.search.windows.net
AZURE_SEARCH_KEY        Admin / query key for the service
AZURE_SEARCH_INDEX      Name of the index that contains Pit-Void documents
"""

import os
from typing import List, Tuple

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from azure.core.exceptions import HttpResponseError
import logging
from openai import AzureOpenAI

# basic console logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pit-voids.azure-search")


def _build_client() -> SearchClient:
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")

    if not all([endpoint, key, index_name]):
        raise EnvironmentError(
            "AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY and AZURE_SEARCH_INDEX must be set."
        )

    client = SearchClient(
        endpoint=endpoint,
        index_name=index_name,
        credential=AzureKeyCredential(key),
    )
    # logger.info("Azure SearchClient initialised for index '%s'", index_name)  # debug output disabled
    return client


# -------------------------------------------------------------
# helper: embed the query with Azure OpenAI
# -------------------------------------------------------------
def _embed(text: str) -> List[float]:
    """
    Returns a 1536-dim vector using the text-embedding-3-small deployment.
    Environment vars required:
      AZURE_OPENAI_ENDPOINT   (same format as the Foundry endpoint root)
      AZURE_OPENAI_KEY        (API key)
      EMBEDDING_DEPLOYMENT    (deployment name, e.g. text-embedding-3-small)
    """
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")
    deployment = os.getenv("EMBEDDING_DEPLOYMENT", "text-embedding-3-small")

    if not all([endpoint, api_key, deployment]):
        raise EnvironmentError(
            "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY and EMBEDDING_DEPLOYMENT must be set."
        )

    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint.rstrip("/"),
        api_version="2024-02-15-preview",
    )

    resp = client.embeddings.create(
        model=deployment,  # deployment name
        input=text,
    )
    return resp.data[0].embedding


def query_pit_voids(query_text: str, *, top: int = 5) -> List[Tuple[str, str]]:
    """
    Hybrid semantic + vector search.
    Returns (title, snippet) tuples for grounding.
    """
    client = _build_client()

    # fields that hold text
    search_fields = ["chunk", "title"]
    semantic_cfg = os.getenv("AZURE_SEMANTIC_CONFIG")

    # embed once
    vector = _embed(query_text)

    # build a vector-KNN clause (dict form avoids missing **kind** bug)
    vec_query = {
        "kind": "vector",
        "vector": vector,
        "kNearestNeighbors": top,
        "fields": "text_vector",
    }

    results = client.search(
        query_text,
        select=search_fields,
        search_fields=search_fields,
        query_type=QueryType.SEMANTIC,
        vector_queries=[vec_query],    # keep list wrapper
        top=top,
        semantic_configuration_name=semantic_cfg or None,
    )

    snippets: List[Tuple[str, str]] = []
    for doc in results:
        title = str(doc.get("title") or doc.get("chunk_id") or "unknown")
        body = str(doc.get("chunk", ""))[:500]
        if body:
            snippets.append((title, body))
    return snippets