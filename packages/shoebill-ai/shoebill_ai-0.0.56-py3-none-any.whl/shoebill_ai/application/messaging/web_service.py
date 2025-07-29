import asyncio
import logging
from typing import Dict, Any

from h_message_bus import NatsPublisherAdapter

from ...domain.messaging.flows.init_knowledgebase_request import InitKnowledgeBaseRequestMessage
from ...domain.messaging.web.web_get_docs_request_message import WebGetDocsRequestMessage
from ...domain.messaging.web.web_get_docs_response_message import WebGetDocsResponseMessage
from ...domain.messaging.web.web_search_request_message import WebSearchRequestMessage


class WebService:
    def __init__(self, nats_publisher_adapter: NatsPublisherAdapter):
        self.nats_publisher_adapter = nats_publisher_adapter
        self.logger = logging.getLogger(__name__)


    async def get_docs_from_web(self, url: str, timeout: float = 30.0)-> list[Dict[str, Any]] :
        request = WebGetDocsRequestMessage.create_message(
            root_url=url)

        response = await self.nats_publisher_adapter.request(request, timeout=timeout)
        response_message = WebGetDocsResponseMessage.from_hai_message(response)
        self.logger.info("Requested get docs for url")
        return response_message.docs

    async def discover_ecosystem(self, query: str):
        request = WebSearchRequestMessage.create_message(query=query)
        await self.nats_publisher_adapter.publish(request)
        self.logger.info("Requested initial websearch")
        await asyncio.sleep(0.5)

    async def init_knowledge(self, user_name: str):
        request = InitKnowledgeBaseRequestMessage.create_message()
        request.payload["twitter_user"]=user_name
        await self.nats_publisher_adapter.publish(request)
        self.logger.info("Requested init knowledge")
        await asyncio.sleep(0.5)
