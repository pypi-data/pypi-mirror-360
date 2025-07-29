import asyncio
import logging
import yarl
import aiohttp
import aiohttp.client_exceptions
import aiohttp.web

from typing import Literal

from base64 import b64decode
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes

from .models import *
from .enum import *


AUTH_URL = "https://id.kick.com"
API_URL = "https://api.kick.com/public/v1"

API_VERSION = "v1"

logger = logging.getLogger("kickpy.http")

async def on_request_start(session, context, params):
    logger.debug("Request started: %s %s", params.method, params.url)

trace_config = aiohttp.TraceConfig()
trace_config.on_request_start.append(on_request_start)

class KickHttpClient:

    @property
    def session(self):
        return self._client_session

    def __init__(self, *args, **kwargs):
        headers = {
            "User-Agent": "kick.py/1.0",
            "Accept": "application/json"
        }

        headers.update(kwargs.pop("headers", {}))

        trace_config.on_request_exception.append(self.handle_rate_limit)

        trace_configs = [trace_config]
        trace_configs.extend(kwargs.pop("trace_configs", []))

        raise_for_status = kwargs.pop("raise_for_status", True)

        self._client_session = aiohttp.ClientSession(
            *args,
            headers=headers,
            trace_configs=trace_configs,
            raise_for_status=raise_for_status,
            **kwargs
        )

        self.auth_url = AUTH_URL
        self.api_url = API_URL

        self.api_version = API_VERSION

    async def __aenter__(self):
        await self._client_session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client_session.__aexit__(exc_type, exc_val, exc_tb)

    async def handle_rate_limit(self, session, context, params):
        if params.exception.status == 429:
            logging.warning("Rate limit hit, retrying after 5 seconds")
            await asyncio.sleep(5)
            try:
                response = await session.request(
                    method=params.method,
                    url=params.url,
                    headers=params.headers,
                    params=params.params,
                    data=params.data
                )
                return response
            except aiohttp.client_exceptions.ClientResponseError as e:
                logging.error(f"Failed to retry request: {e}")
                raise e

    def get_oauth_url(self, client_id: str, response_type: Literal["code"], redirect_uri: str, state: str, scopes: list[str], code_challenge: str, code_challenge_method: Literal["plain", "S256"]):
        assert client_id is not None, "Client ID must be provided"
        assert redirect_uri is not None, "Redirect URI must be provided"
        assert state is not None, "State must be provided"
        assert scopes is not None, "Scopes must be provided"
        assert code_challenge is not None, "Code challenge must be provided"
        assert code_challenge_method is not None, "Code challenge method must be provided"

        if response_type != "code":
            raise ValueError("Response type must be 'code'")

        if code_challenge_method not in ["plain", "S256"]:
            raise ValueError("Code challenge method must be either 'plain' or 'S256'")

        url = yarl.URL(f"{self.auth_url}/oauth/authorize").with_query({
            "client_id": client_id,
            "response_type": response_type,
            "redirect_uri": redirect_uri,
            "state": state,
            "scope": ' '.join(scopes),
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method
        })

        return url

    async def verify_oauth_code(self, code: str, client_id: str, client_secret: str, redirect_uri: str, grant_type: Literal["authorization_code"], code_verifier: str):
        assert code is not None, "Code must be provided"
        assert client_id is not None, "Client ID must be provided"
        assert client_secret is not None, "Client Secret must be provided"
        assert redirect_uri is not None, "Redirect URI must be provided"
        assert code_verifier is not None, "Code verifier must be provided"

        if grant_type != "authorization_code":
            raise ValueError("Grant type must be 'authorization_code'")

        async with self._client_session.request(
            method="POST",
            url=f"{self.auth_url}/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": redirect_uri,
                "grant_type": grant_type,
                "code": code,
                "code_verifier": code_verifier
            }
        ) as response:

            raw = await response.json()

        return TokenResponse(**raw)

    async def fetch_access_token(self, client_id: str, client_secret: str):
        assert client_id is not None, "Client ID must be provided"
        assert client_secret is not None, "Client Secret must be provided"

        async with self._client_session.request(
            method="POST",
            url=f"{self.auth_url}/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            }
        ) as response:

            raw = await response.json()

        return TokenResponse(**raw)

    async def refresh_token(self, refresh_token: str, client_id: str, client_secret: str, grant_type: Literal["refresh_token"]):
        assert refresh_token is not None, "Refresh token must be provided"
        assert client_id is not None, "Client ID must be provided"
        assert client_secret is not None, "Client Secret must be provided"

        if grant_type != "refresh_token":
            raise ValueError("Grant type must be 'refresh_token'")

        async with self._client_session.request(
            method="POST",
            url=f"{self.auth_url}/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            params={
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": grant_type,
                "refresh_token": refresh_token
            }
        ) as response:

            raw = await response.json()

        return TokenResponse(**raw)

    async def revoke_token(self, token: str, type: Literal["access_token", "refresh_token"]):
        assert token is not None, "Token must be provided"

        async with self._client_session.request(
            method="POST",
            url=f"{self.auth_url}/oauth/revoke",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            params={
                "token": token,
                "token_type_hint": type
            }
        ) as response:

            await response.read()

    async def fetch_categories(self, q: str, page: int = 1):
        if len(q) < 3:
            raise ValueError("Query must be at least 3 characters long")
        
        if page < 1:
            raise ValueError("Page number must be 1 or greater")

        if page > 100:
            raise ValueError("Page number must not exceed 100")

        params = {}
        if q:
            params["q"] = q
        if page > 1:
            params["page"] = page

        async with self._client_session.request(
            method="GET",
            url=f"{self.api_url}/categories",
            params=params
        ) as response:

            raw = await response.json()

        return ApiResponse[list[CategoryModel]](**raw)

    async def fetch_category(self, category_id: int):
        assert category_id is not None, "Category ID must be provided"

        async with self._client_session.request(
            method="GET",
            url=f"{self.api_url}/categories/{category_id}"
        ) as response:

            raw = await response.json()

        return ApiResponse[CategoryModel](**raw)

    async def fetch_token_info(self, access_token: str):
        assert access_token is not None, "Access token must be provided"

        async with self._client_session.request(
            method="POST",
            url=f"{self.api_url}/token/introspect",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        ) as response:
        
            raw = await response.json()

        return ApiResponse[TokenIntrospectResponse](**raw)

    async def fetch_users_info(self, user_ids: list[int] = None):
        params = {}
        if user_ids:
            params["id"] = user_ids

        async with self._client_session.request(
            method="GET",
            url=f"{self.api_url}/users",
            params=params,
        ) as response:
        
            raw = await response.json()

        return ApiResponse[list[UserInfoResponse]](**raw)

    async def fetch_channels_info(self, broadcaster_user_id: list[int] = None, slugs: list[str] = None):
        if not broadcaster_user_id and not slugs:
            raise ValueError("At least one of broadcaster_user_id or slugs must be provided")

        if broadcaster_user_id and slugs:
            raise ValueError("Only one of broadcaster_user_id or slugs can be provided")
        
        if broadcaster_user_id:
            if len(broadcaster_user_id) > 50:
                raise ValueError("broadcaster_user_id list must not exceed 50 items")

        if slugs:
            if len(slugs) > 50 or any(len(slug) > 25 for slug in slugs):
                raise ValueError("slugs list must not exceed 50 items and each slug must not exceed 25 characters")

        params = {}

        if broadcaster_user_id:
            params["broadcaster_user_id"] = broadcaster_user_id
        
        elif slugs:
            params["slug"] = slugs

        async with self._client_session.request(
            method="GET",
            url=f"{self.api_url}/channels",
            params=params,
        ) as response:
        
            raw = await response.json()

        return ApiResponse[list[ChannelInfoResponse]](**raw)

    async def patch_channel_info(self, category_id: int = None, stream_title: str = None):
        if not category_id and not stream_title:
            raise ValueError("At least one of category_id or stream_title must be provided")

        data = {}
        
        if category_id:
            data["category_id"] = category_id
        
        if stream_title:
            data["stream_title"] = stream_title

        async with self._client_session.request(
            method="PATCH",
            url=f"{self.api_url}/channels",
            json=data
        ) as response:

            await response.read()

    async def post_chat_message(self, content: str, broadcaster_user_id: int=None, reply_to_message_id: str=None, type: Literal["user", "bot"] = "bot"):
        assert content is not None, "Content must be provided"

        if len(content) > 500:
            raise ValueError("Content must not exceed 500 characters")

        if type not in ["user", "bot"]:
            raise ValueError("Type must be either 'user' or 'bot'")

        if type == "user" and not broadcaster_user_id:
            raise ValueError("broadcaster_user_id must be provided when type is 'user'")

        data = {
            "content": content,
            "type": type
        }

        if broadcaster_user_id:
            data["broadcaster_user_id"] = broadcaster_user_id

        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id

        async with self._client_session.request(
            method="POST",
            url=f"{self.api_url}/chat",
            json=data
        ) as response:

            raw = await response.json()

        return ApiResponse[MessageResponse](**raw)

    async def post_moderation_ban(self, broadcaster_user_id: int, user_id: int, duration: int=None, reason: str = None):
        assert broadcaster_user_id is not None, "broadcaster_user_id must be provided"
        assert user_id is not None, "user_id must be provided"

        data = {
            "broadcaster_user_id": broadcaster_user_id,
            "user_id": user_id,
        }
        
        if duration:
            if duration < 1 or duration > 10080:
                raise ValueError("Duration must be between 1 and 10080 minutes (7 days)")
            data["duration"] = duration

        if reason:
            if len(reason) > 100:
                raise ValueError("Reason must not exceed 100 characters")
            data["reason"] = reason

        async with self._client_session.request(
            method="POST",
            url=f"{self.api_url}/moderation/bans",
            json=data
        ) as response:

            await response.read()

    async def delete_moderation_ban(self, broadcaster_user_id: int, user_id: int):
        assert broadcaster_user_id is not None, "broadcaster_user_id must be provided"
        assert user_id is not None, "user_id must be provided"

        async with self._client_session.request(
            method="DELETE",
            url=f"{self.api_url}/moderation/bans",
            json={
                "broadcaster_user_id": broadcaster_user_id,
                "user_id": user_id
            }
        ) as response:

            await response.read()

    async def fetch_streams(self, broadcaster_user_id: int = None, category_id: int = None, language: str = None, limit: int = None, sort: Literal["viewer_count", "started_at"] = None):
        assert not (broadcaster_user_id is None and category_id is None and language is None and limit is None and sort is None), "At least one of broadcaster_user_id, category_id, language, limit, or sort must be provided"

        params = {}
        
        if broadcaster_user_id:
            params["broadcaster_user_id"] = broadcaster_user_id

        if category_id:
            params["category_id"] = category_id

        if language:
            params["language"] = language

        if limit:
            if limit < 1 or limit > 100:
                raise ValueError("Limit must be between 1 and 100")
            params["limit"] = limit

        if sort:
            if sort not in ["viewer_count", "started_at"]:
                raise ValueError("Sort must be either 'viewer_count' or 'started_at'")
            params["sort"] = sort

        async with self._client_session.request(
            method="GET",
            url=f"{self.api_url}/livestreams",
            params=params
        ) as response:

            raw = await response.json()
        
        return ApiResponse[list[StreamResponse]](**raw)

    async def fetch_public_key(self):
        async with self._client_session.request(
            method="GET",
            url=f"{self.api_url}/public-key"
        ) as response:

            raw = await response.json()

        return ApiResponse[PublicKeyResponse](**raw)

    async def fetch_event_subscriptions(self):
        async with self._client_session.request(
            method="GET",
            url=f"{self.api_url}/events/subscriptions"
        ) as response:

            raw = await response.json()

        return ApiResponse[list[EventSubscriptionInfoResponse]](**raw)

    async def post_event_subscriptions(self, events: list[str], broadcaster_user_id: int = None, method: Literal["webhook"] = None):
        if not events:
            raise ValueError("Events must be a non-empty list")

        data = {
            "events": list(map(
                lambda event: 
                    {
                        "name": str(event),
                        "version": 1
                    }, events))}

        if method:
            if method != "webhook":
                raise ValueError("Method must be 'webhook'")
            data["method"] = method

        if broadcaster_user_id:
            data["broadcaster_user_id"] = broadcaster_user_id

        async with self._client_session.request(
            method="POST",
            url=f"{self.api_url}/events/subscriptions",
            json=data
        ) as response:

            raw = await response.json()

        return ApiResponse[list[EventSubscriptionCreateResponse]](**raw)

    async def delete_event_subscriptions(self, ids: list[str]):
        assert isinstance(ids, list), "IDs must be a list"

        if not ids:
            return

        async with self._client_session.request(
            method="DELETE",
            url=f"{self.api_url}/events/subscriptions",
            params={"id": ids}
        ) as response:

            await response.read()

class KickWebhookHandler:

    pk: PublicKeyTypes
    
    def __init__(self, pk: PublicKeyTypes = None, verify_signature: bool = True):
        self.pk = pk
        self._verify = verify_signature

    async def on_event(self, event: LibEvents, model: BaseModel) -> None: ...
    async def on_oauth(self, code: str, state: str) -> None: ...

    def verify_signature(self, request: aiohttp.web.Request, body: bytes) -> bool:
        signature = request.headers.get("Kick-Event-Signature")
        if not signature:
            logging.error("Signature header is missing")
            return False

        message_id = request.headers.get("Kick-Event-Message-Id")
        message_timestamp = request.headers.get("Kick-Event-Message-Timestamp")

        if not message_id or not message_timestamp:
            logging.error("Message ID or timestamp header is missing")
            return False

        message = b"%s.%s.%s" % (
            message_id.encode("utf-8"),
            message_timestamp.encode("utf-8"),
            body
        )

        try:
            self.pk.verify(
                b64decode(signature),
                message,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False

    async def handle_webhook(self, request: aiohttp.web.Request):
        try:
            #subscription_id = request.headers.get("Kick-Event-Subscription-Id")
            event_type = request.headers.get("Kick-Event-Type")
            #event_version = request.headers.get("Kick-Event-Version")

            if self._verify and not self.verify_signature(request, await request.read()):
                logging.error("Invalid signature in webhook request")
                return

            data = await request.json()

            match event_type:
                case LibEvents.ON_MESSAGE:
                    model = ChatMessageEvent(**data)
                case LibEvents.ON_FOLLOW:
                    model = ChannelFollowEvent(**data)
                case LibEvents.ON_SUBSCRIPTION:
                    model = ChannelSubscriptionEvent(**data)
                case LibEvents.ON_SUBSCRIPTION_GIFT:
                    model = ChannelGiftSubscriptionEvent(**data)
                case LibEvents.ON_NEW_SUBSCRIPTION:
                    model = ChannelSubscriptionEvent(**data)
                case LibEvents.ON_LIVESTREAM_UPDATED:
                    model = LivestreamUpdatedEvent(**data)
                case LibEvents.ON_LIVESTREAM_METADATA_UPDATED:
                    model = LivestreamMetadataUpdatedEvent(**data)
                case LibEvents.ON_MODERATION_BANNED:
                    model = ModerationBanEvent(**data)
                case _:
                    logging.warning(f"Unhandled event type: {event_type}")
                    return

            await self.on_event(event_type, model)
        except Exception as e:
            logging.exception(f"Error handling event")
        finally:
            return aiohttp.web.Response(status=200)

    async def handle_oauth_callback(self, request: aiohttp.web.Request):
        code = request.query.get("code")
        state = request.query.get("state")

        if not code or not state:
            logging.error("Missing code or state in callback request")
            return aiohttp.web.Response(status=404)

        try:
            await self.on_oauth(code, state)
        except Exception as e:
            logging.error(f"Error handling OAuth callback: {e}")
            return aiohttp.web.Response(status=404)

        return aiohttp.web.Response(text="OAuth flow completed successfully.")
