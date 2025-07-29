import os
import asyncio
import aiohttp
import aiohttp.client_exceptions
import aiohttp.web
import logging
import yarl
import pyee.asyncio as pyee
import secrets
import json

from datetime import (
    datetime,
    timedelta
)

from typing import (
    Literal,
    TypeVar,
    Self,
    Optional,
    Awaitable,
    Callable,
    Generic,
    Union
)

from dataclasses import dataclass
from hashlib import md5
from authlib.oauth2.rfc7636 import create_s256_code_challenge
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes

from .models import *
from ._http import (
    KickHttpClient,
    KickWebhookHandler
)
from .enum import (
    Scopes,
    LibEvents,
    CacheStrategy,
    Events
)


T = TypeVar("T", bound=BaseModel)

class _PartialEntity(Generic[T]):
    """ A generic class for partial
    entities.
    This class is used to represent an entity which might exists and can be fetched later.
    """

    @property
    def exists(self) -> bool:
        """ Check if the entity exists.
        This property returns True if the entity data is not None, indicating that the entity exists.
        :return: True if the entity exists, False otherwise.
        """
        return self.data is not None

    def __init__(self, data: Optional[T], resolve: Callable[..., Awaitable[T]]):
        self.data = data
        self._resolve = resolve

    async def resolve(self) -> T:
        """ Resolve the entity data.
        This method forces the entity to resolve its data by awaiting the resolve function.
        If the entity data is already available, it ignores it.
        :return: The entity data.
        """
        self.data = await self._resolve()
        return self.data

    async def get_or_resolve(self) -> T:
        """ Get the entity data or resolve it if not available.
        This method checks if the entity data is already available. If it is, it returns the data.
        If not, it resolves the entity by awaiting the resolve function and returns the data.
        :return: The entity data.
        """
        if self.data is not None:
            return self.data

        self.data = await self._resolve()
        return self.data

    def get_or_raise(self) -> T:
        """ Get the entity data or raise an exception if not available.
        This method checks if the entity data is available. If it is, it returns the data.
        If not, it raises a ValueError indicating that the entity does not exist.
        :return: The entity data.
        :raises ValueError: If the entity data is None.
        """
        if self.data is None:
            raise ValueError("Entity does not exist")
        
        return self.data

    def get(self) -> Optional[T]:
        """ Get the entity data if available.
        This method returns the entity data if it exists, otherwise returns None.
        :return: The entity data or None if not available.
        """
        return self.data

    def __bool__(self) -> bool:
        """ Check if the entity is truthy.
        This method returns True if the entity data is not None, indicating that the entity exists.
        :return: True if the entity exists, False otherwise.
        """
        return self.data is not None

class ApiModelWrapper:
    """ A generic wrapper for API models.
    This class provides a way to wrap API models and handle caching, data retrieval, and initialization.
    It is designed to be extended by specific API model wrappers, such as Token, Category, User, etc.
    """
    __slots__ = ("_client", "_data")

    __cache_prefix__: str = "generic"
    __cache__: bool = True

    __CACHE: dict[str, dict] = {}
    
    def cache_id(self) -> str:
        """ Get the cache ID for this model.
        This method returns a unique identifier for the model based on its class and data.
        :return: Cache ID as a string.
        """
        cache_id = self._shadowed_cache_id if self._shadowed_cache_id else self._cache_id
        return self.get_cache_id(cache_id) 

    @property
    def _cache_id(self) -> str:
        """ Get the cache ID for this model.
        This property should be overridden by subclasses to provide a unique identifier for the model.
        :return: Cache ID as a string.
        """
        raise NotImplementedError("Subclasses must implement _cache_id property")

    def __init__(self, *, client: "KickClient", data: dict, cache_strategy = CacheStrategy.UPDATE, cache_id: str = None):
        """ Initialize an ApiModelWrapper instancse.
        This method initializes the ApiModelWrapper with a KickClient instance and data.
        :param client: The KickClient instance to associate with the wrapper.
        :param data: The data to wrap, must be a dictionary.
        :param cache_strategy: The strategy to use for caching, either "update", "erase", or "ignore".
        :raises ValueError: If an invalid cache strategy is provided.
        :return: An instance of ApiModelWrapper containing the data.
        """
        assert client is None or isinstance(client, KickClient), "client must be an instance of KickClient"

        self._client = client
        self._data = data
        self._shadowed_cache_id = None

        if cache_id is not None:
            self._shadowed_cache_id = cache_id

        if self.__cache__:
            cached_data = self.save_to_cache(
                cache_id=self.cache_id(),
                data=self._data,
                cache_strategy=cache_strategy
            )

            if cached_data is not None:
                self._data = cached_data

    def freeze(self) -> None:
        """ Freeze the data of the ApiModelWrapper.
        This method converts the internal data dictionary to a deep copy to prevent further modifications.
        This is useful for ensuring that the data remains immutable even if the cache is updated.
        """
        self._data = dict(self._data)

    @classmethod
    def get_cache_id(cls, cache_id: str) -> str:
        """ Get the cache ID for this model.
        This method returns a unique identifier for the model based on its class and data.
        :return: Cache ID as a string.
        """
        return f"{cls.__cache_prefix__}_{cache_id}"

    @classmethod
    def save_to_cache(cls, cache_id: str, data: dict, cache_strategy = CacheStrategy.UPDATE) -> dict:
        """ Save data to the cache.
        This method saves data to the cache with a specified cache ID.
        :param cache_id: The ID of the cached data.
        :param data: The data to cache, must be a dictionary.
        :param cache_strategy: The strategy to use for caching, either "update", "erase", or "ignore".
        """
        assert isinstance(cache_id, str), "cache_id must be a string"
        assert isinstance(data, dict) or isinstance(data, ApiModelWrapper), "data must be a dictionary or an instance of ApiModelWrapper"
        
        if isinstance(data, ApiModelWrapper):
            data = data._data

        if cache_strategy == CacheStrategy.ERASE:
            return
        
        if cache_id not in cls.__CACHE:
            cls.__CACHE[cache_id] = data
        else:
            cls.__CACHE[cache_id].update(data)
            return cls.__CACHE[cache_id]

    @classmethod
    def from_cache(cls, client: "KickClient", cache_id: str) -> Optional[Self]:
        """ Retrieve data from the cache.
        This method retrieves data from the cache using the provided cache ID.
        :param cache_id: The ID of the cached data.
        :return: The cached data as a dictionary, or None if not found.
        """
        assert isinstance(cache_id, str), "cache_id must be a string"

        cache_id = cls.get_cache_id(cache_id)

        if cache_id in cls.__CACHE:
            return cls(client=client, data=cls.__CACHE[cache_id], cache_strategy="ignore")

        return None

    @classmethod
    def from_response(cls, client: "KickClient", response: T, extra: dict = None, cache_strategy = CacheStrategy.UPDATE) -> Self:
        """ Create an instance of ApiModelWrapper from an API response.
        This method takes an ApiResponse containing a model and returns an instance of ApiModelWrapper.
        """
        assert isinstance(response, BaseModel), "data must be an instance of BaseModel"
        
        extra = extra or {}
        
        data = response.model_dump()
        data.update(extra)

        return cls(client=client, data=data, cache_strategy=cache_strategy)

    @classmethod
    def from_dict(cls, client: "KickClient", data: dict, cache_strategy = CacheStrategy.UPDATE) -> Self:
        """ Create an instance of ApiModelWrapper from a dictionary.
        This method takes a dictionary and returns an instance of ApiModelWrapper.
        :param client: The KickClient instance to associate with the wrapper.
        :param data: The dictionary containing the data to wrap.
        :return: An instance of ApiModelWrapper containing the data.
        """
        assert isinstance(data, dict), "data must be a dictionary"

        return cls(client=client, data=data, cache_strategy=cache_strategy)

    @classmethod
    def from_file(cls, client: "KickClient", file_path: str, cache_strategy = CacheStrategy.UPDATE) -> Self:
        """ Create an instance of ApiModelWrapper from a file.
        This method reads a JSON file and returns an instance of ApiModelWrapper.
        :param client: The KickClient instance to associate with the wrapper.
        :param file_path: The path to the JSON file containing the data.
        :return: An instance of ApiModelWrapper containing the data from the file.
        """
        assert os.path.isfile(file_path), f"File {file_path} does not exist"
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(client=client, data=data, cache_strategy=cache_strategy)

    @classmethod
    def to_file(cls, instance: "ApiModelWrapper", file_path: str) -> None:
        """ Save the ApiModelWrapper instance to a file.
        This method writes the data of the ApiModelWrapper instance to a JSON file.
        :param instance: The ApiModelWrapper instance to save.
        :param file_path: The path to the file where the data will be saved.
        """
        assert isinstance(instance, ApiModelWrapper), "instance must be an instance of ApiModelWrapper"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(instance._data, f, ensure_ascii=False, indent=4)

    @classmethod
    def to_dict(cls, instance: "ApiModelWrapper") -> dict:
        """ Convert the ApiModelWrapper instance to a dictionary.
        This method returns the data of the ApiModelWrapper instance as a dictionary.
        :param instance: The ApiModelWrapper instance to convert.
        :return: The data of the ApiModelWrapper instance as a dictionary.
        """
        assert isinstance(instance, ApiModelWrapper), "instance must be an instance of ApiModelWrapper"
        
        return instance._data

    @classmethod
    def cast(cls, origin: "ApiModelWrapper") -> Self:
        """ Cast another ApiModelWrapper to this class.
        This method casts another ApiModelWrapper instance to the current class type.
        :param other: The ApiModelWrapper instance to cast.
        :return: An instance of the current class containing the data from the other instance.
        """
        assert isinstance(origin, ApiModelWrapper), "other must be an instance of ApiModelWrapper"

        return cls(client=origin._client, data=origin._data, cache_strategy="ignore")

class Token(ApiModelWrapper):
    """ A wrapper for the token response from the API.
    This class provides access to the token data returned by the API.
    """
    __cache_prefix__ = "token"

    @property
    def _cache_id(self) -> str:
        """ Get the cache ID for this token.
        This property returns a unique identifier for the token based on its access token.
        :return: Cache ID as a string.
        """
        return md5(self.access_token.encode("utf-8")).hexdigest()

    def __init__(self, *, client: "KickClient", data: dict, cache_strategy = CacheStrategy.UPDATE, cache_id: str = None):
        super().__init__(client=client, data=data, cache_strategy=cache_strategy, cache_id=cache_id)
        
        if "exp" not in self._data:
            self._data["exp"] = datetime.now().timestamp() + self._data.get("expires_in", 0)

    @property
    def token_scope(self) -> Literal["oauth2", "read_only"]:
        """ Get the type of the token.
        This property returns the type of the token, which is either "oauth2" or "read_only".
        :return: Token type as a string.
        """
        return self._data["token_scope"]

    @property
    def scopes(self) -> set[Scopes]:
        """ Get the scopes associated with the token.
        This property returns a set of scopes that the token has access to.
        :return: Set of Scopes associated with the token.
        """
        return set()

    @property
    def authorization(self) -> str:
        """ Get the authorization header value.
        This property returns the authorization header value in the format
        "Bearer {access_token}".
        """
        return f"Bearer {self._data['access_token']}"

    @property
    def access_token(self) -> str:
        """ Get the access token.
        This property returns the access token string.
        :return: Access token as a string.
        """
        return self._data["access_token"]

    @property
    def refresh_token(self) -> str:
        """ Get the refresh token.
        This property returns the refresh token string.
        :return: Refresh token as a string.
        """
        return self._data.get("refresh_token")

    @property
    def client_id(self) -> str:
        """ Get the client ID.
        This property returns the client ID associated with the token.
        :return: Client ID as a string.
        """
        return self._data["client_id"]

    @property
    def expires_in(self) -> int:
        """ Get the expiration time of the token.
        This property returns the number of seconds until the token expires.
        :return: Expiration time in seconds as an integer.
        """
        return self._data.get("expires_in", 0) - (datetime.now() - self.expiration_date).total_seconds()

    @property
    def expedition_date(self) -> datetime:
        return self.expiration_date - timedelta(seconds=self._data.get("expires_in", 0))

    @property
    def expiration_date(self) -> datetime:
        """ Get the expiration date of the token.
        This property returns the expiration date and time of the token as a datetime object.
        :return: Expiration date as a datetime object.
        """
        return datetime.fromtimestamp(self._data["exp"] - self._data.get("expires_in", 0))

    @property
    def expired(self) -> bool:
        """ Check if the token is expired.
        This property returns True if the token has expired, otherwise False.
        :return: True if the token is expired, False otherwise.
        """
        return self.expires_in <= 0

    async def update_info(self):
        """ Fetch token information.
        This method retrieves information about the token, such as its validity and associated user.
        :return: TokenIntrospectResponse containing token information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        if self.expired:
            logging.warning("Token is expired, attempting to refresh")
            if not await self.refresh():
                return None

        for _ in range(2):
            try:
                token_info = await self._client.oauth.fetch_token_info(
                    access_token=self.access_token
                )

                self._data.update(token_info._data)

                return ExtendedToken.cast(self)
            except aiohttp.client_exceptions.ClientResponseError as e:
                if e.status == 401:
                    if not await self.refresh():
                        return None

                raise

    async def refresh(self) -> bool:
        """ Refresh the access token.
        This method refreshes the access token using the client credentials.
        :return: TokenResponse containing the new access token.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        try:
            new_token = await self._client._kick_http_client.refresh_token(
                refresh_token=self.refresh_token,
                client_id=self._client.client_id,
                client_secret=self._client.client_secret,
                grant_type="refresh_token"
            )
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.status == 401:
                return False
            raise

        self._data.update(new_token.model_dump())

        return True

    async def revoke(self):
        """ Revoke the access token.
        This method revokes the access token, making it invalid for future requests.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        try:
            await self._client._kick_http_client.revoke_token(
                token=self.access_token,
                type="access_token"
            )
        except aiohttp.client_exceptions.ClientResponseError as e:
            if e.status == 401:
                logging.warning("Token already revoked or invalid")
                return

            raise

        self._data = None

class ExtendedToken(Token):
    """ A wrapper for the token introspection response.
    This class provides access to the token introspection data returned by the API.
    """

    @property
    def scopes(self) -> set[Scopes]:
        """ Get the scopes associated with the token.
        This property returns a set of scopes that the token has access to.
        :return: Set of Scopes associated with the token.
        """
        raw_scopes: str = self._data.get("scope", None)
        
        if raw_scopes is None:
            return set()
        
        scopes = raw_scopes.split(" ")
        return {Scopes(scope) for scope in scopes if scope in Scopes.__members__.values()}

class Category(ApiModelWrapper):
    """ A wrapper for category information.
    This class provides access to the category data returned by the API.
    """
    __cache_prefix__ = "category"
    
    @property
    def _cache_id(self) -> str:
        """ Get the cache ID for this category.
        This property returns a unique identifier for the category based on its ID.
        :return: Cache ID as a string.
        """
        return str(self.id)

    @property
    def id(self) -> int:
        """ Get the category ID.
        This property returns the unique identifier for the category.
        :return: Category ID as an integer.
        """
        return self._data["id"]

    @property
    def name(self) -> str:
        """ Get the category name.
        This property returns the name of the category.
        :return: Category name as a string.
        """
        return self._data["name"]

    @property
    def thumbnail(self) -> str:
        """ Get the category thumbnail URL.
        This property returns the URL of the category's thumbnail image.
        :return: Thumbnail URL as a string.
        """
        return self._data["thumbnail"]

class User(ApiModelWrapper):
    """ A wrapper for user information.
    This class provides access to the user data returned by the API.
    """
    __cache_prefix__ = "user"
    
    @property
    def _cache_id(self) -> str:
        """ Get the cache ID for this user.
        This property returns a unique identifier for the user based on their user ID.
        :return: Cache ID as a string.
        """
        return str(self.user_id)

    @property
    def is_anonymous(self) -> bool:
        """ Check if the user is anonymous.
        This property returns True if the user is anonymous, False otherwise.
        :return: Boolean indicating whether the user is anonymous.
        """
        return False

    @property
    def channel(self) -> _PartialEntity["Channel"]:
        """ Get the user's channel information.
        This property retrieves the channel associated with the user.
        :return: Channel object containing the user's channel information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            return (await self._client.channels.get_channels(
                broadcaster_user_ids=[self.user_id]
            ))[0]
    
        return _PartialEntity(
            data=Channel.from_cache(
                self._client,
                str(self.user_id)
            ),
            resolve=_resolve
        )

    @property
    def stream(self) -> _PartialEntity["Stream"]:
        """ Get the user's stream information.
        This property retrieves the stream associated with the user.
        :return: Stream object containing the user's stream information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            streams = await self._client.streams.get_streams(
                broadcaster_user_id=self.user_id
            )

            if not streams:
                return Stream.from_dict(
                    self._client,
                    {
                        "broadcaster_user_id": self.user_id
                    }
                )

            return streams[0]

        return _PartialEntity(
            data=Stream.from_cache(
                self._client,
                str(self.user_id)
            ),
            resolve=_resolve
        )

    @property
    def user_id(self) -> int:
        """ Get the user's unique identifier.
        This property returns the unique identifier for the user.
        :return: User ID as an integer.
        """
        return self._data["user_id"]

    @property
    def email(self) -> str | None:
        """ Get the user's email address.
        This property returns the email address associated with the user.
        :return: User's email address as a string.
        """
        return self._data.get("email")

    @property
    def name(self) -> str:
        """ Get the user's display name.
        This property returns the display name of the user.
        :return: User's display name as a string.
        """
        return self._data["name"]

    @property
    def profile_picture(self) -> str:
        """ Get the user's profile image URL.
        This property returns the URL of the user's profile image.
        :return: Profile image URL as a string.
        """
        return self._data["profile_picture"]

    async def ban(self, *, reason: str = None):
        """ Ban the user.
        This method bans the user for a specified duration and with an optional reason.
        :param duration: Duration of the ban in minutes (1 to 10080).
        :param reason: Reason for the ban (max 100 characters).
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        await self._client.moderation.ban_user(
            user_id=self.user_id,
            reason=reason
        )

    async def timeout(self, *, duration: int, reason: str = None):
        """ Timeout the user.
        This method times out the user for a specified duration and with an optional reason.
        :param duration: Duration of the timeout in minutes (1 to 10080).
        :param reason: Reason for the timeout (max 100 characters).
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        if duration < 1 or duration > 10080:
            raise ValueError("Duration must be between 1 and 10080 minutes")

        await self._client.moderation.timeout_user(
            user_id=self.user_id,
            duration=duration,
            reason=reason
        )
    
    async def unban(self):
        """ Unban the user.
        This method unbans the user, removing any existing ban.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        await self._client.moderation.unban_user(
            user_id=self.user_id
        )

class Broadcaster(User):
    """ A wrapper for broadcaster user information.
    This class extends the User class to provide additional functionality specific to broadcasters.
    """
    
    def __init__(self, *, client, data, cache_strategy=CacheStrategy.UPDATE, cache_id: str = None):
        super().__init__(client=client, data=data, cache_strategy=cache_strategy, cache_id=cache_id)
        
        if "identity" in self._data:
            if self._data["identity"] is None:
                self._data["identity"] = {}

            data = {
                "user_id": self._data["user_id"],
                **self._data["identity"]
            }

            Identity.from_dict(
                client=client,
                data=data
            )

    @property
    def name(self) -> str:
        """ Get the broadcaster's display name.
        This property returns the display name of the broadcaster.
        :return: Broadcaster's display name as a string.
        """
        return self.username

    @property
    def username(self) -> str:
        """ Get the broadcaster's username.
        This property returns the username of the broadcaster.
        :return: Broadcaster's username as a string.
        """
        return self._data.get("username", self._data.get("name"))

    @property
    def is_anonymous(self) -> bool:
        """ Check if the broadcaster is anonymous.
        This property returns True if the broadcaster is anonymous, False otherwise.
        :return: Boolean indicating whether the broadcaster is anonymous.
        """
        return self._data["is_anonymous"]

    @property
    def is_verified(self) -> bool:
        """ Check if the broadcaster is verified.
        This property returns True if the broadcaster is verified, False otherwise.
        :return: Boolean indicating whether the broadcaster is verified.
        """
        return self._data["is_verified"]

    @property
    def channel_slug(self) -> str:
        """ Get the broadcaster's channel slug.
        This property returns the slug of the broadcaster's channel.
        :return: Channel slug as a string.
        """
        return self._data["channel_slug"]

    @property
    def identity(self) -> "Identity":
        """ Get the broadcaster's identity information.
        This property retrieves the identity associated with the broadcaster.
        :return: Identity object containing the broadcaster's identity information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        return Identity.from_cache(
            self._client,
            str(self.user_id)
        )

class AnonymousUser(Broadcaster):
    __cache__ = False

    @property
    def is_anonymous(self) -> bool:
        """ Check if the user is anonymous.
        This property returns True if the user is anonymous, False otherwise.
        :return: Boolean indicating whether the user is anonymous.
        """
        return True

class EventSubscription(ApiModelWrapper):
    """ A wrapper for event subscription information.
    This class provides access to the event subscription data returned by the API.
    """
    __cache__: bool = False

    @property
    def event(self) -> Events:
        """ Get the event type of the subscription.
        This property returns the type of event that the subscription is for.
        :return: Event type as a string or None if not set.
        """
        return LibEvents(self._data["name"])

    @property
    def subscription_id(self) -> str:
        """ Get the unique identifier for the event subscription.
        This property returns the ID of the subscription.
        :return: Subscription ID as a string or None if not set.
        """
        return self._data["subscription_id"]

    @property
    def version(self) -> int:
        """ Get the version of the event subscription.
        This property returns the version number of the subscription.
        :return: Version number as an integer or None if not set.
        """
        return self._data["version"]

class ExtendedEventSubscription(EventSubscription):
    """ A wrapper for event subscription information.
    This class provides access to the event subscription data returned by the API.
    """

    @property
    def app_id(self) -> str:
        """ Get the application ID associated with the event subscription.
        This property returns the unique identifier for the application that created the subscription.
        :return: Application ID as a string or None if not set.
        """
        return self._data["app_id"]

    @property
    def broadcaster_user_id(self) -> int:
        """ Get the broadcaster's user ID associated with the event subscription.
        This property returns the unique identifier for the broadcaster whose events are being subscribed to.
        :return: Broadcaster's user ID as an integer or None if not set.
        """
        return self._data["broadcaster_user_id"]

    @property
    def created_at(self) -> datetime:
        """ Get the creation date and time of the event subscription.
        This property returns the date and time when the subscription was created.
        :return: Creation date and time as a datetime object or None if not set.
        """
        return self._data["created_at"]

    @property
    def event(self) -> Events:
        """ Get the event type of the subscription.
        This property returns the type of event that the subscription is for.
        :return: Event type as a string or None if not set.
        """
        return LibEvents(self._data["event"])

    @property
    def subscription_id(self) -> str:
        """ Get the unique identifier for the event subscription.
        This property returns the ID of the subscription.
        :return: Subscription ID as a string or None if not set.
        """
        return self._data["id"]

    @property
    def method(self) -> str:
        """ Get the method used for the event subscription.
        This property returns the method by which the events are delivered (e.g., webhook).
        :return: Method as a string or None if not set.
        """
        return self._data["method"]

    @property
    def updated_at(self) -> datetime:
        """ Get the last updated date and time of the event subscription.
        This property returns the date and time when the subscription was last updated.
        :return: Last updated date and time as a datetime object or None if not set.
        """
        return self._data["updated_at"]

class Stream(ApiModelWrapper):
    """ A wrapper for stream information.
    This class provides access to the stream data returned by the API.
    """
    __cache_prefix__ = "stream"
    
    @property
    def _cache_id(self) -> str:
        """ Get the cache ID for this stream.
        This property returns a unique identifier for the stream based on its broadcaster user ID.
        :return: Cache ID as a string.
        """
        return str(self.broadcaster_user_id)

    @property
    def category(self) -> _PartialEntity["Category"]:
        """ Get the category of the stream.
        This property retrieves the category associated with the stream.
        :return: Category object containing the stream's category information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            return (await self._client.channels.get_channels(
                broadcaster_user_ids=[self.broadcaster_user_id],
            ))[0]

        return _PartialEntity(
            data=None,
            resolve=_resolve
        )

    @property
    def broadcaster(self) -> _PartialEntity[Broadcaster]:
        """ Get the broadcaster of the stream.
        This property retrieves the broadcaster associated with the stream.
        :return: Broadcaster object containing the stream's broadcaster information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            return (await self._client.users.get_user(
                user_id=self.broadcaster_user_id
            ))

        return _PartialEntity(
            data=Broadcaster.from_cache(
                self._client,
                str(self.broadcaster_user_id)
            ),
            resolve=_resolve
        )

    @property
    def stream_title(self) -> str:
        """ Get the title of the stream.
        This property returns the title of the stream.
        :return: Stream title as a string.
        """
        return self._data.get("stream_title", "")

    @property
    def broadcaster_user_id(self) -> int:
        """ Get the broadcaster's user ID.
        This property returns the unique identifier for the broadcaster of the stream.
        :return: Broadcaster's user ID as an integer.
        """
        return self._data["broadcaster_user_id"]

    @property
    def is_live(self) -> bool:
        """ Check if the stream is currently live.
        This property returns True if the stream is live, False otherwise.
        :return: Boolean indicating whether the stream is live.
        """
        return self._data.get("is_live", False)

    @property
    def is_mature(self) -> bool:
        """ Check if the stream is marked as mature content.
        This property returns True if the stream is marked as mature, False otherwise.
        :return: Boolean indicating whether the stream is mature.
        """
        return self._data["is_mature"]

    @property
    def key(self) -> str:
        """ Get the stream key.
        This property returns the unique key for the stream.
        :return: Stream key as a string.
        """
        return self._data["key"]

    @property
    def language(self) -> str:
        """ Get the language of the stream.
        This property returns the language code for the stream.
        :return: Language code as a string.
        """
        return self._data["language"]

    @property
    def start_time(self) -> datetime:
        """ Get the start time of the stream.
        This property returns the date and time when the stream started.
        :return: Start time as a datetime object.
        """
        return self._data["start_time"]

    @property
    def end_time(self) -> datetime | None:
        """ Get the end time of the stream.
        This property returns the date and time when the stream ended, or None if it is still live.
        :return: End time as a datetime object or None if not applicable.
        """
        return self._data.get("end_time")

    @property
    def thumbnail(self) -> str:
        """ Get the thumbnail URL of the stream.
        This property returns the URL of the stream's thumbnail image.
        :return: Thumbnail URL as a string.
        """
        return self._data["thumbnail"]

    @property
    def url(self) -> str:
        """ Get the URL of the stream.
        This property returns the URL where the stream can be accessed.
        :return: Stream URL as a string.
        """
        return self._data["url"]

    @property
    def viewer_count(self) -> int:
        """ Get the current viewer count of the stream.
        This property returns the number of viewers currently watching the stream.
        :return: Viewer count as an integer.
        """
        return self._data["viewer_count"]

class Channel(ApiModelWrapper):
    """ A wrapper for channel information.
    This class provides access to the channel data returned by the API."""
    __cache_prefix__ = "channel"
    
    @property
    def _cache_id(self) -> str:
        """ Get the cache ID for this channel.
        This property returns a unique identifier for the channel based on its broadcaster user ID.
        :return: Cache ID as a string.
        """
        return str(self.broadcaster_user_id)
    
    def __init__(self, *, client: "KickClient", data: dict, cache_strategy=CacheStrategy.UPDATE, cache_id: str = None):
        """ Initialize the Channel with client and data.
        This constructor allows initializing the channel with data of type T.
        """
        super().__init__(client=client, data=data, cache_strategy=cache_strategy, cache_id=cache_id)

        if "stream" in self._data:
            if self._data["stream"] is None:
                self._data["stream"] = {}

            Stream.from_dict(
                client=client,
                data={
                    "broadcaster_user_id": self._data.get("broadcaster_user_id"),
                    "category": self._data.get("category", {}),
                    "stream_title": self._data.get("stream_title"),
                    **self._data.get("stream", {}),
                }
            )

    @property
    def broadcaster(self) -> _PartialEntity[Broadcaster]:
        """ Get the broadcaster of the channel.
        This property retrieves the broadcaster associated with the channel.
        :return: Broadcaster object containing the channel's broadcaster information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            return (await self._client.users.get_user(
                user_id=self.broadcaster_user_id
            ))

        return _PartialEntity(
            data=Broadcaster.from_cache(
                self._client,
                str(self.broadcaster_user_id)
            ),
            resolve=_resolve
        )

    @property
    def stream(self) -> _PartialEntity["Stream"]:
        """ Get the channel's stream information.
        This property retrieves the stream associated with the channel.
        :return: Stream object containing the channel's stream information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            return (await self._client.streams.get_streams(
                broadcaster_user_id=self.broadcaster_user_id
            ))[0]

        return _PartialEntity(
            data=Stream.from_cache(
                self._client,
                str(self.broadcaster_user_id)
            ),
            resolve=_resolve
        )

    @property
    def banner_picture(self) -> str:
        """ Get the channel's banner picture URL.
        This property returns the URL of the channel's banner image.
        :return: Banner picture URL as a string.
        """
        return self._data["banner_picture"]

    @property
    def channel_description(self) -> str:
        """ Get the channel's description.
        This property returns the description of the channel.
        :return: Channel description as a string.
        """
        return self._data["channel_description"]

    @property
    def broadcaster_user_id(self) -> int:
        """ Get the broadcaster's user ID.
        This property returns the unique identifier for the broadcaster of the channel.
        :return: Broadcaster's user ID as an integer.
        """
        return self._data["broadcaster_user_id"]

class Message(ApiModelWrapper):
    """ A wrapper for message information.
    This class provides access to the message data returned by the API.
    """
    
    __cache__: bool = False

    @property
    def message_id(self) -> str:
        """ Get the unique identifier for the message.
        This property returns the ID of the message.
        :return: Message ID as a string.
        """
        return self._data["message_id"]

    @property
    def content(self) -> str:
        """ Get the content of the message.
        This property returns the text content of the message.
        :return: Message content as a string.
        """
        return self._data["content"]

    @property
    def broadcaster(self) -> _PartialEntity[Broadcaster]:
        """ Get the broadcaster who sent the message.
        This property retrieves the broadcaster associated with the message.
        :return: Broadcaster object containing the message's broadcaster information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            return (await self._client.users.get_user(
                user_id=self._data["broadcaster_user_id"]
            ))

        return _PartialEntity(
            data=Broadcaster.from_cache(
                self._client,
                str(self._data["broadcaster_user_id"])
            ),
            resolve=_resolve
        )

    @property
    def sender(self) -> _PartialEntity[Broadcaster]:
        """ Get the sender of the message.
        This property retrieves the user who sent the message.
        :return: Broadcaster object containing the sender's information.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        async def _resolve():
            return (await self._client.users.get_user(
                user_id=self._data["sender_user_id"]
            ))

        return _PartialEntity(
            data=Broadcaster.from_cache(
                self._client,
                str(self._data["sender_user_id"])
            ),
            resolve=_resolve
        )
    
    @property
    def emotes(self) -> list["Emote"]:
        """ Get the emotes used in the message.
        This property returns a list of emotes present in the message content.
        :return: List of emotes as strings.
        """
        emotes = self._data.get("emotes", [])

        return [
            Emote(emote_id=emote.emote_id, position=emote.positions[0])
            for emote in emotes
        ]

    async def reply(self, content: str, as_bot: bool = False):
        """ Reply to the message.
        This method sends a reply to the message with the specified content.
        :param content: The content of the reply message.
        """
        assert self._client is not None, "KickClient must be initialized before calling this method"

        await self._client.channels.send_message(
            content=content,
            reply_to=self.message_id,
            as_bot=as_bot
        )

class Identity(ApiModelWrapper):
    """ A wrapper for identity information.
    This class provides access to the identity data returned by the API.
    """
    __cache_prefix__ = "identity"

    @property
    def _cache_id(self) -> str:
        """ Get the cache ID for this identity.
        This property returns a unique identifier for the identity based on its user ID.
        :return: Cache ID as a string.
        """
        return str(self.user_id)

    @property
    def username_color(self) -> str:
        """ Get the color of the user's username.
        This property returns the color code for the user's username.
        :return: Username color as a string.
        """
        return self._data["username_color"]

    @property
    def user_id(self) -> int:
        """ Get the user's unique identifier.
        This property returns the unique identifier for the user associated with the identity.
        :return: User ID as an integer.
        """
        return self._data["user_id"]

    @property
    def badges(self) -> list["Badge"]:
        """ Get the badges associated with the user.
        This property returns a list of badges that the user has.
        :return: List of badges as strings.
        """
        badges: list[dict] = self._data.get("badges", [])
        
        return [
            Badge(badge["text"], badge["type"], badge["count"])
            for badge in badges
        ]

@dataclass
class Subscription:
    broadcaster: Broadcaster
    subscriber: Broadcaster
    gifter: Optional[Union[Broadcaster, AnonymousUser]]
    is_gift: bool
    is_new: bool
    created_at: datetime
    expires_at: datetime

@dataclass
class Gift:
    broadcaster: Broadcaster
    gifter: Union[Broadcaster, AnonymousUser]
    subscriptions: list[Subscription]

@dataclass
class Moderation:
    broadcaster: Broadcaster
    moderator: Broadcaster
    user: Broadcaster
    reason: str
    created_at: datetime
    expires_at: Optional[datetime]

@dataclass
class Timeout(Moderation):
    expires_at: datetime
    
    @property
    def duration(self) -> int:
        """ Get the duration of the timeout in seconds.
        This property returns the duration of the timeout in seconds.
        :return: Duration in seconds as an integer.
        """
        return (self.expires_at - self.created_at).total_seconds()

@dataclass
class Ban(Moderation):
    expires_at = None

@dataclass
class Badge:
    """ A class representing a badge.
    This class is used to represent a badge with its text, type, and count.
    """
    text: str
    type: str
    count: int = 1

@dataclass
class Emote:
    emote_id: str
    position: Position

# ----------- END OF ENTITIES -----------

# ----------- API CLASSES -----------

class API:
    """ Base class for API endpoints.
    This class serves as a base for all API endpoints, providing common functionality.
    """
    
    _client: "KickClient"

    def __init__(self, *, client: "KickClient"):
        assert isinstance(client, KickClient), "client must be an instance of KickClient"
        self._client = client

    @staticmethod
    def requires_scopes(*scopes: Scopes):
        """ Decorator to require specific scopes for API methods.
        This decorator checks if the required scopes are present in the token before executing the method.
        :param scopes: List of Scopes that are required for the method.
        """
        def decorator(func):
            async def wrapper(api, *args, **kwargs):
                if not isinstance(api, API):
                    raise ValueError("First argument must be an instance of API")

                client_scopes = api._client.scopes

                if not client_scopes.issuperset(set(scopes)):
                    raise PermissionError(f"Missing required scopes: {', '.join(scopes)}")

                return await func(api, *args, **kwargs)

            return wrapper
        return decorator

class OauthAPI(API):
    """ API for handling OAuth authentication.
    This class provides methods for preparing the OAuth URL, verifying the authorization code,
    and fetching new access tokens.
    """

    def prepare_url(self, scopes: list[Scopes], state: str = None):
        """ Prepare the OAuth URL for user authorization.
        This method generates the OAuth URL that the user should visit to authorize the application.
        :param scopes: List of scopes to request access to.
        :param state: Optional state parameter to maintain state between request and callback.
        :return: Tuple containing the OAuth URL and the code challenge secret bytes.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        oauth_secret_bytes = secrets.token_urlsafe(64)
        oauth_code_challenge = create_s256_code_challenge(oauth_secret_bytes)

        return self._client._kick_http_client.get_oauth_url(
            client_id=self._client.client_id,
            response_type="code",
            redirect_uri=self._client.oauth_redirect_uri.human_repr(),
            state=state,
            scopes=scopes,
            code_challenge=oauth_code_challenge,
            code_challenge_method="S256"
        ), oauth_secret_bytes

    async def verify_code(self, code: str, code_verifier: str) -> Optional[Token]:
        """ Verify the OAuth code received from the user after authorization.
        This method exchanges the code for an access token.
        :param code: The authorization code received from the OAuth flow.
        :param code_verifier: The code verifier used in the OAuth flow.
        :return: TokenResponse containing access and refresh tokens.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        try:
            validated_token = await self._client._kick_http_client.verify_oauth_code(
                code=code,
                client_id=self._client.client_id,
                client_secret=self._client.client_secret,
                redirect_uri=self._client.oauth_redirect_uri.human_repr(),
                grant_type="authorization_code",
                code_verifier=code_verifier
            )

            return Token.from_response(
                self._client,
                validated_token,
                extra={
                    "client_id": self._client.client_id,
                    "token_scope": "oauth2"
                }
            )
        except aiohttp.client_exceptions.ClientError as e:
            logging.exception(f"Failed to verify OAuth code")
            return None

    async def new_access_token(self):
        """ Fetch a new access token using the client credentials.
        This method is used to obtain an access token for API requests.
        :return: TokenResponse containing the new access token.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        try:
            rd_access_token = await self._client._kick_http_client.fetch_access_token(
                client_id=self._client.client_id,
                client_secret=self._client.client_secret
            )

            return Token.from_response(
                self._client,
                rd_access_token,
                extra={
                    "client_id": self._client.client_id,
                    "token_scope": "read_only"
                },
                cache_strategy="erase"
            )
        except aiohttp.client_exceptions.ClientError as e:
            logging.error(f"Failed to fetch new access token: {e}")
            return None

    async def fetch_public_key(self) -> PublicKeyTypes:
        """ Fetch the public key used for verifying webhook signatures.
        This method retrieves the public key from the Kick API.
        :return: PublicKeyTypes containing the public key.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        pk_bytes = (await self._client._kick_http_client.fetch_public_key()).data.public_key

        return serialization.load_pem_public_key(
            pk_bytes.encode("utf-8")
        )
    
    async def fetch_token_info(self, access_token: str) -> ExtendedToken:
        """ Fetch information about the access token.
        This method retrieves information about the access token, such as its validity and associated user.
        :param access_token: The access token to fetch information for.
        :return: ExtendedToken containing token information.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        token_info_response = await self._client._kick_http_client.fetch_token_info(
            access_token=access_token
        )

        return ExtendedToken.from_response(
            self._client,
            token_info_response.data,
            extra={
                "access_token": access_token
            }
        )
    
    async def revoke_token(self, access_token: str):
        """ Revoke an access token.
        This method revokes the specified access token, making it invalid for future requests.
        :param access_token: The access token to revoke.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        await self._client._kick_http_client.revoke_token(
            token=access_token,
            type="access_token"
        )

    async def refresh_token(self, refresh_token: str) -> Token:
        """ Refresh an access token using the refresh token.
        This method exchanges the refresh token for a new access token.
        :param refresh_token: The refresh token to use for refreshing the access token.
        :return: ExtendedToken containing the new access token.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        new_token_response = await self._client._kick_http_client.refresh_token(
            refresh_token=refresh_token,
            client_id=self._client.client_id,
            client_secret=self._client.client_secret,
            grant_type="refresh_token"
        )

        return Token.from_response(
            self._client,
            new_token_response
        )

class CategoriesAPI(API):
    """ API for managing categories.
    This class provides methods to fetch and manage categories on the Kick platform.
    """
    
    class _CategoryCursor:
        """ Cursor for paginating through categories.
        This class is used to paginate through categories when fetching them.
        """
        def __init__(self, client: "KickClient", q: str, limit: int):
            self._client = client
            self._q = q
            self._limit = limit
            self._page = 1
            self._i = 0

        def __aiter__(self) -> Self:
            """ Initialize the cursor for iteration.
            This method prepares the cursor for iterating through categories.
            :return: The current instance of _CategoryCursor.
            """
            assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"
            self._categories = []
            self._i = 0
            self._page = 1
            return self

        async def __anext__(self) -> Category:
            """ Fetch the next category in the cursor.
            This method retrieves the next category from the API based on the query and limit.
            :return: Category object representing the next category.
            """
            if self._limit is not None and self._i >= self._limit:
                raise StopAsyncIteration

            if self._i % 100 == 0:
                categories_response = await self._client._kick_http_client.fetch_categories(
                    q=self._q,
                    page=self._page
                )

                if not categories_response.data:
                    raise StopAsyncIteration

                self._categories = [Category.from_response(self._client, cat) for cat in categories_response.data]
                self._page += 1
                self._i = 0

            if self._i >= len(self._categories):
                raise StopAsyncIteration

            category = self._categories[self._i]
            self._i += 1

            return category

    async def fetch(self, category_id: int) -> Category:
        """ Fetch a category by its ID.
        This method retrieves a category from the API using its unique identifier.
        :param category_id: The unique identifier of the category to fetch.
        :return: Category object representing the fetched category.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not category_id:
            raise ValueError("Category ID must be provided")

        category_response = await self._client._kick_http_client.fetch_category(category_id)

        return Category.from_response(
            self._client,
            category_response.data
        )

    def query(self, q: str, limit: int = 100) -> "_CategoryCursor":
        """ Query categories by name.
        This method fetches categories that match the given query string.
        :param q: The query string to search for categories.
        :param limit: The maximum number of categories to return (default is 100).
        :return: ApiModelWrapper containing a list of Category objects.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if len(q) < 3:
            raise ValueError("Query must be at least 3 characters long")

        if limit is not None and limit < 1:
            raise ValueError("Limit must be at least 1")

        return self._CategoryCursor(self._client, q, limit)

class UsersAPI(API):
    """ API for managing users.
    This class provides methods to fetch and manage user information on the Kick platform.
    """

    @API.requires_scopes(Scopes.USER_READ)
    async def get_users(self, user_ids: list[int]) -> list[User]:
        """ Fetch a user by their unique identifier.
        This method retrieves user information from the API using the user's unique identifier.
        :param user_id: The unique identifier of the user to fetch.
        :return: User object representing the fetched user.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        user_ids = user_ids or []

        users_response = await self._client._kick_http_client.fetch_users_info(user_ids=set(user_ids))

        return [
            User.from_response(
                self._client,
                user)
            for user
            in users_response.data
        ]

    @API.requires_scopes(Scopes.USER_READ)
    async def get_user(self, user_id: int = None) -> User:
        """ Fetch a user by their unique identifier.
        This method retrieves user information from the API using the user's unique identifier.
        :param user_id: The unique identifier of the user to fetch.
        :return: User object representing the fetched user.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"
        
        if not user_id:
            users_response = await self._client._kick_http_client.fetch_users_info()
        else:
            users_response = await self._client._kick_http_client.fetch_users_info(user_ids=[user_id])

        if not users_response.data:
            raise ValueError(f"User with ID {user_id} not found")

        return User.from_response(
            self._client,
            users_response.data[0]
        )

class EventsAPI(API):
    """ API for managing Libevents.
    This class provides methods to fetch and manage event subscriptions on the Kick platform.
    """

    async def fetch_subscriptions(self) -> list[EventSubscription]:
        """ Fetch all event subscriptions.
        This method retrieves all event subscriptions from the API.
        :return: List of EventSubscriptionInfoResponse objects representing the fetched subscriptions.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        subscriptions_response = await self._client._kick_http_client.fetch_event_subscriptions()

        return [
            ExtendedEventSubscription.from_response(
                self._client,
                sub,
                cache_strategy="ignore"
            )
            for sub in subscriptions_response.data
        ]

    @API.requires_scopes(Scopes.EVENTS_SUBSCRIBE)
    async def subscribe(self, events: list[LibEvents], broadcaster_user_id: int = None) -> list[EventSubscription]:
        """ Subscribe to events.
        This method creates new event subscriptions for the specified events.
        :param events: List of LibEvents to subscribe to.
        :param broadcaster_user_id: Optional broadcaster user ID to filter subscriptions.
        :return: List of EventSubscriptionCreateResponse objects representing the created subscriptions.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not events:
            return []

        subscriptions_response = await self._client._kick_http_client.post_event_subscriptions(
            events=events,
            broadcaster_user_id=broadcaster_user_id,
            method="webhook"
        )

        return [
            EventSubscription.from_response(
                self._client,
                sub,
                cache_strategy="ignore"
            )
            for sub in subscriptions_response.data
        ]

    async def unsubscribe(self, subscriptions: list[EventSubscription]) -> None:
        """ Unsubscribe from events.
        This method deletes event subscriptions by their unique identifiers.
        :param subscription_ids: List of subscription IDs to unsubscribe from.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not subscriptions:
            return

        await self._client._kick_http_client.delete_event_subscriptions(
            ids=[sub.subscription_id for sub in subscriptions]
        )

class ChannelsAPI(API):   
    """ API for managing channels.
    This class provides methods to fetch and manage channel information on the Kick platform.
    """

    async def get_channels(self, broadcaster_user_ids: list[int] = None, slugs: list[str] = None) -> list[Channel]:
        """ Fetch channels by broadcaster user IDs or slugs.
        This method retrieves channel information from the API using the broadcaster's user IDs or slugs.
        :param broadcaster_user_ids: List of broadcaster user IDs to fetch channels for.
        :param slugs: List of channel slugs to fetch channels for.
        :return: List of Channel objects representing the fetched channels.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not broadcaster_user_ids and not slugs:
            raise ValueError("Either broadcaster_user_ids or slugs must be provided")

        channels_response = await self._client._kick_http_client.fetch_channels_info(
            broadcaster_user_id=broadcaster_user_ids,
            slugs=slugs
        )

        return [
            Channel.from_response(
                self._client,
                channel
            )
            for channel
            in channels_response.data
        ]

    async def get_channel(self, broadcaster_user_id: int = None, slug: str = None) -> Channel:
        """ Fetch a channel by broadcaster user ID or slug.
        This method retrieves channel information from the API using the broadcaster's user ID or slug.
        :param broadcaster_user_id: The unique identifier of the broadcaster to fetch the channel for.
        :param slug: The slug of the channel to fetch.
        :return: Channel object representing the fetched channel.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not broadcaster_user_id and not slug:
            raise ValueError("Either broadcaster_user_id or slug must be provided")

        channels_response = await self._client._kick_http_client.fetch_channels_info(
            broadcaster_user_id=[broadcaster_user_id] if broadcaster_user_id else None,
            slugs=[slug] if slug else None
        )

        if not channels_response.data:
            raise ValueError(f"Channel not found for user ID {broadcaster_user_id} or slug {slug}")

        return Channel.from_response(
            self._client,
            channels_response.data[0]
        )

    @API.requires_scopes(Scopes.CHAT_WRITE)
    async def send_message(self, content: str, reply_to: str = None, as_bot: bool = True) -> Message:
        """ Send a message to the channel.
        This method sends a message to the channel, optionally as a bot.
        :param content: The content of the message to send.
        :param reply_to: Optional message ID to reply to.
        :param as_bot: Whether to send the message as a bot (default is True).
        :return: Message object representing the sent message.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not content:
            raise ValueError("Content must be provided")

        type = "user" if not as_bot else "bot"
        broadcaster_user_id = self._client.me.user_id if not as_bot else None

        message_response = await self._client._kick_http_client.post_chat_message(
            broadcaster_user_id=broadcaster_user_id,
            content=content,
            reply_to_message_id=reply_to,
            type=type
        )

        return Message.from_dict(
            self._client,
            {
                "message_id": message_response.data.message_id,
                "content": message_response.message,
                "broadcaster_user_id": broadcaster_user_id,
                "sender_user_id": broadcaster_user_id,
                "emotes": []
            }
        )

    @API.requires_scopes(Scopes.CHANNEL_WRITE)
    async def update_channel(self, category_id: int = None, stream_title: str = None) -> None:
        """ Update channel information.
        This method updates the channel's category and/or stream title.
        :param category_id: The unique identifier of the category to set for the channel.
        :param stream_title: The title of the stream to set for the channel.
        :return: Channel object representing the updated channel.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"
        
        if not category_id and not stream_title:
            raise ValueError("Either category_id or stream_title must be provided")

        await self._client._kick_http_client.patch_channel_info(
            category_id=category_id,  # Category ID is not updated here
            stream_title=stream_title
        )

class StreamsAPI(API):
    """ API for managing streams.
    This class provides methods to fetch and manage stream information on the Kick platform.
    """

    async def get_streams(self, broadcaster_user_id: int = None,
                          language: str = None,
                          category_id: int = None,
                          limit: int = 100,
                          sort: str = "viewer_count"):
        """ Fetch streams by broadcaster user IDs.
        This method retrieves stream information from the API using the broadcaster's user IDs.
        :param broadcaster_user_ids: List of broadcaster user IDs to fetch streams for.
        :return: List of Stream objects representing the fetched streams.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        streams_response = await self._client._kick_http_client.fetch_streams(
            broadcaster_user_id=broadcaster_user_id,
            category_id=category_id,
            limit=limit,
            sort=sort,
            language=language
        )

        return [
            Stream.from_response(
                self._client,
                stream,
                extra={
                    "is_live": True
                }
            )
            for stream
            in streams_response.data
        ]

class ModerationAPI(API):
    """ API for managing moderation actions.
    This class provides methods to perform moderation actions such as banning and timing out users.
    """

    @API.requires_scopes(Scopes.MODERATION_BAN)
    async def ban_user(self, user_id: int, reason: str = None) -> None:
        """ Ban a user from the channel.
        This method bans a user from the channel with an optional reason.
        :param user_id: The unique identifier of the user to ban.
        :param reason: Optional reason for the ban.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not user_id:
            raise ValueError("User ID must be provided")

        if self._client.me.user_id == user_id:
            raise ValueError("You cannot ban yourself")

        await self._client._kick_http_client.post_moderation_ban(
            broadcaster_user_id=self._client.me.user_id,
            user_id=user_id,
            reason=reason
        )

    @API.requires_scopes(Scopes.MODERATION_BAN)
    async def timeout_user(self, user_id: int, duration: int, reason: str = None) -> None:
        """ Timeout a user in the channel.
        This method times out a user for a specified duration with an optional reason.
        :param user_id: The unique identifier of the user to timeout.
        :param duration: The duration of the timeout in seconds.
        :param reason: Optional reason for the timeout.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not user_id:
            raise ValueError("User ID must be provided")

        if self._client.me.user_id == user_id:
            raise ValueError("You cannot timeout yourself")

        if duration <= 0:
            raise ValueError("Duration must be greater than 0")

        await self._client._kick_http_client.post_moderation_ban(
            broadcaster_user_id=self._client.me.user_id,
            user_id=user_id,
            duration=duration,
            reason=reason
        )

    @API.requires_scopes(Scopes.MODERATION_BAN)
    async def unban_user(self, user_id: int):
        """ Unban a user from the channel.
        This method unbans a user from the channel.
        :param user_id: The unique identifier of the user to unban.
        """
        assert self._client._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if not user_id:
            raise ValueError("User ID must be provided")

        await self._client._kick_http_client.delete_moderation_ban(
            broadcaster_user_id=self._client.me.user_id,
            user_id=user_id
        )

class KickClient:

    @property
    def me(self) -> Optional[User]:
        """ Get the authenticated user.
        This property returns the User object representing the authenticated user.
        :return: User object representing the authenticated user.
        """
        return self._me

    def __init__(
            self,
            client_id: str,
            client_secret: str,
            web_app_url: str = "http://0.0.0.0:8000",
            oauth_redirect_host: str = "localhost",
            webhook_callback_endpoint: str = "webhook",
            oauth_redirect_endpoint: str = "oauth/callback",
            cache_oauth: bool = True,
            oauth_file: str = ".oauth",
            scopes: list[Scopes] = None,
            prefetch_me: bool = True,
            development: bool = False,
            loop: asyncio.AbstractEventLoop = None,
            http_client_cls: type[KickHttpClient] = KickHttpClient):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = set(scopes) if scopes is not None else set()

        self.cache_oauth = cache_oauth
        self.oauth_file = oauth_file

        if scopes:
            self.scopes.update(scopes)

        self.web_app_url = yarl.URL(web_app_url)

        self.webhook_callback_uri = self.web_app_url \
            .with_path(webhook_callback_endpoint)
        self.oauth_redirect_uri = self.web_app_url \
            .with_host(oauth_redirect_host) \
            .with_path(oauth_redirect_endpoint)
        
        if development:
            logging.warning("Running in development mode. This MUST NOT be used in production!")

        self._prefetch_me = prefetch_me
        self._development = development
        self._loop = loop

        self.oauth = OauthAPI(client=self)
        self.categories = CategoriesAPI(client=self)
        self.users = UsersAPI(client=self)
        self.events = EventsAPI(client=self)
        self.channels = ChannelsAPI(client=self)
        self.streams = StreamsAPI(client=self)
        self.moderation = ModerationAPI(client=self)
        
        self._web_app = aiohttp.web.Application()
        self._event_emitter = pyee.AsyncIOEventEmitter(loop=self._loop)
        
        self._token: Token = None
        self._me = None

        self._oauth_codes: dict[str, asyncio.Future] = {}

        self._initialized: asyncio.Event
        self._kick_http_cls: type[KickHttpClient] = http_client_cls
        self._kick_http_client: KickHttpClient
        self._kick_wh_handler: KickWebhookHandler

    def start(self):
        """ Start the Kick client in a non-blocking manner.
        This method initializes the client and starts the event loop.
        """
        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        task = self._loop.create_task(self.__run())

        return task

    def run(self):
        """ Run the Kick client in a blocking manner.
        This method is a blocking call that starts the client and runs the event loop until stopped.
        """
        task = self.start()

        try:
            asyncio.get_event_loop().run_until_complete(task)
        except Exception as e:
            logging.exception("An error occurred while running the Kick client")
        finally:
            self.stop()

    def stop(self):
        """
        Stop the Kick client.
        This method should be called to clean up resources and stop the client.
        """
        # Here you would typically close the HTTP session, stop the webhook server, etc.
        pass

    def add_listener(self, event: str, listener):
        """
        Add a listener for a specific event.
        :param event: The name of the event to listen for.
        :param listener: The callback function to call when the event is emitted.
        """
        return self._event_emitter.add_listener(event, listener)

    def remove_listener(self, event: str, listener):
        """
        Remove a listener for a specific event.
        :param event: The name of the event to stop listening for.
        :param listener: The callback function to remove.
        """
        self._event_emitter.remove_listener(event, listener)

    def on(self, event: str):
        """
        Decorator to register a listener for a specific event.
        :param event: The name of the event to listen for.
        """
        def decorator(func):
            return self.add_listener(event, func)
        return decorator

    async def __handle_event_callback(self, event: LibEvents, model: BaseEventModel):
        args, kwargs = (), {}
        event = event

        if not self._initialized.is_set():
            return

        match event:
            case LibEvents.ON_MESSAGE:
                event = Events.ON_MESSAGE
                
                # Ensure the broadcaster and sender are cached

                Broadcaster.from_response(
                    self,
                    model.broadcaster
                )

                Broadcaster.from_response(
                    self,
                    model.sender
                )
    
                kwargs = {
                    "message": Message.from_dict(
                        self,
                        {
                            "message_id": model.message_id,
                            "content": model.content,
                            "broadcaster_user_id": model.broadcaster.user_id,
                            "sender_user_id": model.sender.user_id,
                            "emotes": model.emotes or []
                        }
                    )
                }
            case LibEvents.ON_FOLLOW:
                event = Events.ON_FOLLOW

                kwargs = {
                    "broadcaster": Broadcaster.from_response(
                        self,
                        model.broadcaster
                    ),
                    "follower": Broadcaster.from_response(
                        self,
                        model.follower
                    )
                }
            case LibEvents.ON_SUBSCRIPTION:
                event = Events.ON_SUBSCRIPTION

                kwargs = {
                    "subscription": Subscription(
                        broadcaster=Broadcaster.from_response(
                            self,
                            model.broadcaster
                        ),
                        subscriber=Broadcaster.from_response(
                            self,
                            model.subscriber
                        ),
                        gifter=None,
                        is_gift=False,
                        created_at=model.created_at,
                        expires_at=model.expires_at,
                        is_new=False
                    )
                }
            case LibEvents.ON_SUBSCRIPTION_GIFT:
                event = Events.ON_SUBSCRIPTION_GIFT

                broadcaster = Broadcaster.from_response(
                    self,
                    model.broadcaster
                )
                
                if model.gifter.is_anonymous:
                    gifter = AnonymousUser.from_response(
                        self,
                        model.gifter
                    )
                else:
                    gifter = Broadcaster.from_response(
                        self,
                        model.gifter
                    )
                
                subscriptions = [
                    Subscription(
                        broadcaster=broadcaster,
                        subscriber=Broadcaster.from_response(
                            self,
                            sub
                        ),
                        gifter=gifter,
                        is_gift=True,
                        is_new=False,
                        created_at=model.created_at,
                        expires_at=model.expires_at
                    )
                    for sub in model.giftees
                ]

                kwargs = {
                    "gift": Gift(
                        broadcaster=broadcaster,
                        gifter=gifter,
                        subscriptions=subscriptions
                    )
                }
            case LibEvents.ON_NEW_SUBSCRIPTION:
                event = Events.ON_SUBSCRIPTION

                kwargs = {
                    "subscription": Subscription(
                        broadcaster=Broadcaster.from_response(
                            self,
                            model.broadcaster
                        ),
                        subscriber=Broadcaster.from_response(
                            self,
                            model.subscriber
                        ),
                        gifter=None,
                        is_gift=False,
                        created_at=model.created_at,
                        expires_at=model.expires_at,
                        is_new=True
                    )
                }
            case LibEvents.ON_LIVESTREAM_UPDATED:
                broadcaster = Broadcaster.from_response(
                    self,
                    model.broadcaster
                )

                stream = Stream.from_dict(
                    self,
                    {
                        "broadcaster_user_id": broadcaster.user_id,
                        "is_live": model.is_live,
                        "stream_title": model.title,
                        "start_time": model.started_at,
                        "end_time": model.ended_at,
                    }
                )

                event = Events.ON_LIVESTREAM_STARTED if model.is_live else Events.ON_LIVESTREAM_ENDED

                kwargs = {
                    "stream": stream,
                }
            case LibEvents.ON_LIVESTREAM_METADATA_UPDATED:
                event = Events.ON_LIVESTREAM_UPDATED
                
                broadcaster = Broadcaster.from_response(
                    self,
                    model.broadcaster
                )

                Category.from_response(
                    self,
                    model.metadata.category
                ) # This line is just to ensure the category is fetched and cacheds

                updated_data = {
                    "broadcaster_user_id": broadcaster.user_id,
                    "language": model.metadata.language,
                    "stream_title": model.metadata.title,
                    "is_mature": model.metadata.has_mature_content
                }
                
                old_stream = broadcaster.stream
                if old_stream:
                    old_stream = old_stream.get()
                    old_stream.freeze()

                updated_stream = Stream.from_dict(
                    self,
                    updated_data
                )

                kwargs = {
                    "old_stream": old_stream or updated_stream,
                    "new_stream": updated_stream
                }
            case LibEvents.ON_MODERATION_BANNED:
                broadcaster = Broadcaster.from_response(
                    self,
                    model.broadcaster
                )
                
                moderator = Broadcaster.from_response(
                    self,
                    model.moderator
                )
                
                banned_user = Broadcaster.from_response(
                    self,
                    model.banned_user
                )
                
                expires_at = model.metadata.expires_at
                
                if expires_at is not None:
                    event = Events.ON_MODERATION_TIMEOUT
                    
                    kwargs = {
                        "moderation": Timeout(
                            broadcaster=broadcaster,
                            moderator=moderator,
                            user=banned_user,
                            reason=model.metadata.reason,
                            created_at=model.metadata.created_at,
                            expires_at=expires_at
                        )
                    }
                else:
                    event = Events.ON_MODERATION_BAN
                    
                    kwargs = {
                        "moderation": Ban(
                            broadcaster=broadcaster,
                            moderator=moderator,
                            user=banned_user,
                            reason=model.metadata.reason,
                            created_at=model.metadata.created_at,
                            expires_at=None
                        )
                    }
            case _:
                logging.warning(f"Unhandled event: {event}")
                return

        self._event_emitter.emit(event, *args, **kwargs)

    async def __handle_oauth_callback(self, code: str, state: str):
        fut = self._oauth_codes.pop(state, None)

        if not fut:
            logging.error(f"Invalid state: {state}")
            return aiohttp.web.Response(status=400)

        fut.set_result(code)

    async def __run_wb_handler(self):
        pk = await self.oauth.fetch_public_key()

        self._kick_wh_handler = KickWebhookHandler(
            pk=pk,
            verify_signature=not self._development
        )

        self._kick_wh_handler.on_event = self.__handle_event_callback
        self._kick_wh_handler.on_oauth = self.__handle_oauth_callback

        self._web_app.router.add_post(self.webhook_callback_uri.path, self._kick_wh_handler.handle_webhook)
        self._web_app.router.add_get(self.oauth_redirect_uri.path, self._kick_wh_handler.handle_oauth_callback)

        runner = aiohttp.web.AppRunner(self._web_app, handle_signals=True)
        await runner.setup()

        wh_site = aiohttp.web.TCPSite(runner, self.web_app_url.host, self.web_app_url.port)

        await wh_site.start()

        await wh_site._server.wait_closed()

    async def __run_auth_handler(self):
        token = None

        if self.cache_oauth and os.path.isfile(self.oauth_file):
            token = await Token.from_file(self, self.oauth_file).update_info()

            if not token:
                logging.warning("Cached token is invalid or expired, fetching a new one.")
            elif not all([scope in token.scopes for scope in self.scopes]):
                logging.warning("Cached token does not have all required scopes, fetching a new one.")
                token = None
            else:
                logging.info("Using cached OAuth token.")

        if token is None:
            if not self.scopes:
                token = await self.oauth.new_access_token()
            else:
                state = secrets.token_urlsafe(32)

                oauth_url, secret_bytes = self.oauth.prepare_url(
                    scopes=self.scopes,
                    state=state
                )

                fut = asyncio.Future[str]()
                self._oauth_codes[state] = fut
                
                if not self._event_emitter.emit(Events.ON_OAUTH_URL, oauth_url):
                    print(f"Visit this URL to authorize:\n{str(oauth_url)}")

                code = await fut

                token = await self.oauth.verify_code(
                    code=code,
                    code_verifier=secret_bytes
                )

                token = await token.update_info()

        if not token:
            logging.error("Unable to verify OAuth code.")
            raise RuntimeError("Access token is not set")

        logging.info("Access token obtained successfully.")

        if self.cache_oauth:
            ExtendedToken.to_file(token, self.oauth_file)

        self._token = token

        self._kick_http_client.session.headers.update({
            "Authorization": token.authorization
        })

    async def __run_fetch_me(self):
        """ Fetch the authenticated user.
        This method retrieves the authenticated user information from the API.
        :return: User object representing the authenticated user.
        """
        assert self._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if Scopes.USER_READ not in self.scopes:
            return

        if not self._prefetch_me:
            return

        user = await self.users.get_user()

        if Scopes.CHANNEL_READ in self.scopes:
            await asyncio.gather(
                user.channel.resolve(),
                user.stream.resolve()
            )
        
        self._me = user

    async def __run_subscribe_events(self):
        """ Subscribe to events.
        This method subscribes to the events specified in the client's scopes.
        """
        assert self._kick_http_client, "KickHttpClient must be initialized before calling this method"

        if Scopes.EVENTS_SUBSCRIBE not in self.scopes:
            return

        subcriptions = await self.events.fetch_subscriptions()
        await self.events.unsubscribe(subscriptions=subcriptions)
        await self.events.subscribe(events=LibEvents.__members__.values())

    async def __run(self):
        self._loop = self._loop or asyncio.get_event_loop()

        self._initialized = asyncio.Event()

        async with self._kick_http_cls(loop=self._loop) as self._kick_http_client:
            _webhook_task = self._loop.create_task(self.__run_wb_handler())

            await self.__run_auth_handler()

            await asyncio.gather(
                self.__run_fetch_me(),
                self.__run_subscribe_events()
            )

            self._initialized.set()

            self._event_emitter.emit(Events.ON_READY)

            try:
                await _webhook_task
            finally:
                self._event_emitter.emit(Events.ON_DISCONNECT)
