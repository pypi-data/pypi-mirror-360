from ..env.models import Resource as ResourceModel
from ..env.models import BrowserDescribeResponse
from .base import Resource

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..env.base import AsyncWrapper


class AsyncBrowserResource(Resource):
    def __init__(self, resource: ResourceModel, client: "AsyncWrapper"):
        super().__init__(resource)
        self.client = client

    async def describe(self) -> BrowserDescribeResponse:
        response = await self.client.request("GET", "/resource/cdp/describe")
        return BrowserDescribeResponse(**response.json())
