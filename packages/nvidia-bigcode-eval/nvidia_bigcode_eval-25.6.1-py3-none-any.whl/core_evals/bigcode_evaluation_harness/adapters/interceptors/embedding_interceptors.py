import json
from typing import final

try:
    import requests
except ImportError:
    raise ImportError(
        "Please install requests, werkzeug, and flask to use the adapter! pip install requests flask werkzeug"
    )

from .types import AdapterRequest, AdapterResponse, RequestInterceptor

COHERE_INPUT_MAP = {"query": "search_query", "passage": "search_document"}


@final
class CohereEndpointInterceptor(RequestInterceptor):
    """Adapter for Cohere API."""

    _fetch_retries: int
    _nvcf_status_url: str

    api_url: str

    def __init__(self, api_url: str):
        """
        Initialize the Cohere adapter.

        Number of retries is controlled via env variables

        """

        self.api_url = api_url

    @final
    def intercept_request(self, ar: AdapterRequest) -> AdapterResponse:
        """
        Handle the NVCF request with polling logic.

        Args:
            request_data: Preprocessed request data

        Returns:
            Response from NVCF API
        """
        # NVCF specifics: it does not work with `/` trailiing. We have to trip them
        response = requests.request(
            method=ar.r.method,
            url=self.api_url.rstrip("/"),
            headers={k: v for k, v in ar.r.headers if k.lower() != "host"},
            json={
                "model": ar.r.json["model"].replace("cohere/", ""),
                "texts": ar.r.json["input"],
                "input_type": COHERE_INPUT_MAP[ar.r.json["input_type"]],
                "embedding_types": ["float"],
            },
            cookies=ar.r.cookies,
            allow_redirects=False,
        )

        response.raise_for_status()

        if response.status_code == 200:
            response_json = response.json()
            embeddings = response_json["embeddings"]["float"]

            new_response = {
                "object": "list",
                "data": [
                    {
                        "object": "embedding",
                        "embedding": embedding,
                        "index": i,
                    }
                    for i, embedding in enumerate(embeddings)
                ],
                "model": ar.r.json["model"],
            }

            response._content = json.dumps(new_response).encode()

        return AdapterResponse(
            r=response,
            meta=ar.meta,
        )
