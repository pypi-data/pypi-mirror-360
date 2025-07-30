from langchain_core.callbacks import BaseCallbackHandler
from datetime import datetime
from .db.base import BaseDBClient


class DBTokenUsageLogger(BaseCallbackHandler):
    def __init__(self, db_client: BaseDBClient, table: str = "token_usage"):
        self.db_client = db_client
        self.table = table

    def on_llm_end(self, response, **kwargs):
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage")
            if token_usage:
                record = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "provider": kwargs.get("llm", "unknown"),
                    "model_name": kwargs.get("model_name", "unknown"),
                    "token_usage": token_usage,
                }
                self.db_client.write(self.table, record)
