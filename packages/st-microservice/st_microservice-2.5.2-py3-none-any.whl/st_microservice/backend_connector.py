from typing import Any

from graphql import GraphQLResolveInfo
from httpx import AsyncClient
from .request_utils import get_request, get_token


async def graphql_call(
    info: GraphQLResolveInfo,
    uri: str,
    query: str,
    variables: dict[str, Any] | None = None,
):
    client: AsyncClient = get_request(info).app.state.httpx_client
    return await send_graphql_request(client, get_token(info), uri, query, variables)


async def send_graphql_request(
    client: AsyncClient,
    token: str,
    uri: str,
    query: str,
    variables: dict[str, Any] | None,
):
    headers = {"Authorization": "bearer " + token}
    response = await client.post(
        uri, headers=headers, json={"query": query, "variables": variables}
    )
    json_dict = response.json()
    if response.is_error or "error" in json_dict or "errors" in json_dict:
        try:
            error_message = json_dict["error"]
        except KeyError:
            try:
                error_message = json_dict["errors"]
            except KeyError:
                error_message = "Unidentified error in request"
        raise Exception(error_message)
    return json_dict["data"]
