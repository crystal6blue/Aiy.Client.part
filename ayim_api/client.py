import httpx


class AyimApi:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.Client(timeout=30)

    def _request(self, method: str, endpoint: str, **kwargs):
        try:
            response = self.client.request(
                method,
                f"{self.base_url}{endpoint}",
                **kwargs
            )

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException:
            raise RuntimeError("Request timed out")

        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"HTTP error {e.response.status_code}: {e.response.text}"
            )

        except httpx.RequestError as e:
            raise RuntimeError(f"Connection error: {str(e)}")

    def health(self):
        return self._request("GET", "/health")

    def generate(self, question: str):
        return self._request(
            "POST",
            "/generate",
            json={"question": question}
        )

    def close(self):
        self.client.close()
