import httpx

class XUIClient:
    _instance = None
    BASE_HOST: str = ""
    BASE_PORT: str = ""
    BASE_PATH: str = ""
    base_url = f"https://{BASE_HOST}:{BASE_PORT}/{BASE_PATH}"

    def __init__(self):
        self.httpclient: httpx.AsyncClient | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(XUIClient, cls).__new__(cls)
        return cls._instance

    async def __aenter__(self):
        self.httpclient = httpx.AsyncClient()
        return self.httpclient

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return self.httpclient.aclose()