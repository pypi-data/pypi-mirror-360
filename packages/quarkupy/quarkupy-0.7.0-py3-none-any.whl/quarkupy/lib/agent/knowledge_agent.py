from pydantic import BaseModel

import quarkupy as q

class KnowledgeAgent(BaseModel):
    """
    A Knowledge Agent is a specialized agent designed to manage and process knowledge bases.
    """

    base_url: str
    openai_api_key: str
    table_name: str = "nerdiox"
    search_limit: int = 50

    async def ask(self, query: str) -> q.types:
        """
        Ask the knowledge agent a question.
        This method should be implemented by subclasses to provide specific functionality.
        """
        client = q.AsyncClient(
            base_url=self.base_url
        )

        res = await client.worker.agent.chat_rag_demo(
            table_name=self.table_name,
            search_limit=self.search_limit,
            openai_api_key=self.openai_api_key,
            query=query
        )

        return res