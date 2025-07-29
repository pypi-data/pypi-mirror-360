from datetime import datetime

from pydantic import (
    BaseModel,
    Field
)

from typing import (
    TypeVar,
    Generic,
    Optional
)


T = TypeVar('T', bound=dict)

# ----------- MODELS -----------

class Position(BaseModel):
    s: int
    e: int

class ApiResponse(BaseModel, Generic[T]):
    data: T
    message: str = ""

class ApiModel(BaseModel):

    @property
    def data(self) -> T: return self

class CategoryModel(ApiModel):
    id: int | None = None
    name: str | None = None
    thumbnail: str | None = None

class EmoteModel(ApiModel):
    emote_id: str | None = None
    positions: list[Position] = Field(default_factory=list)

class ModerationMetadataModel(ApiModel):
    reason: str | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None

class PublicKeyResponse(ApiModel):
    public_key: str | None = None

class MessageResponse(ApiModel):
    is_sent: bool | None = None
    message_id: str | None = None

class EventSubscriptionCreateResponse(ApiModel):
    error: str | None = None
    name: str | None = None
    subscription_id: str | None = None
    version: int | None = None

class EventSubscriptionInfoResponse(ApiModel):
    app_id: str | None = None
    broadcaster_user_id: int | None = None
    created_at: datetime | None = None
    event: str | None = None
    id: str | None = None
    method: str | None = None
    updated_at: datetime | None = None
    version: int | None = None

class StreamInfoResponse(ApiModel):
    is_live: bool | None = None
    is_mature: bool | None = None
    key: str | None = None
    language: str | None = None
    start_time: datetime | None = None
    thumbnail: str | None = None
    url: str | None = None
    viewer_count: int | None = None

class StreamResponse(ApiModel):
    broadcaster_user_id: int | None = None
    category: CategoryModel | None = None
    channel_id: int | None = None
    has_mature_content: bool | None = None
    language: str | None = None
    slug: str | None = None
    started_at: datetime | None = None
    stream_title: str | None = None
    thumbnail: str | None = None
    viewer_count: int | None = None

class TokenIntrospectResponse(ApiModel):
    active: bool | None = None
    client_id: str | None = None
    exp: int | None = None
    scope: str | None = None
    token_type: str | None = None

class TokenResponse(ApiModel):
    access_token: str | None = None
    token_type: str | None = None
    expires_in: int | None = None
    token_scope: str | None = None
    refresh_token: str | None = None

class UserInfoResponse(ApiModel):
    email: str | None = None
    name: str | None = None
    profile_picture: str | None = None
    user_id: int | None = None

class BadgeModel(ApiModel):
    text: str | None = None
    type: str | None = None
    count: int = 1

class IdentityModel(ApiModel):
    username_color: str | None = None
    badges: list[BadgeModel] = Field(default_factory=list)

class UserModel(ApiModel):
    is_anonymous: bool | None = None
    user_id: int | None = None
    username: str | None = None
    is_verified: bool | None = None
    profile_picture: str | None = None
    channel_slug: str | None = None
    identity: IdentityModel | None = None

class LiveStreamMetadataModel(ApiModel):
    title: str | None = None
    language: str | None = None
    has_mature_content: bool | None = None
    category: CategoryModel | None = None

class ChannelInfoResponse(ApiModel):
    banner_picture: str | None = None
    broadcaster_user_id: int | None = None
    category: CategoryModel | None = None
    channel_description: str | None = None
    slug: str | None = None
    stream: StreamInfoResponse | None = None
    stream_title: str | None = None

# ----------- END OF MODELS -----------

# ----------- EVENT MODELS -----------

class BaseEventModel(BaseModel): ...

class ChatMessageEvent(BaseEventModel):
    message_id: str
    broadcaster: UserModel
    sender: UserModel
    content: str
    emotes: Optional[list[EmoteModel]] = Field(default_factory=list)

class ChannelFollowEvent(BaseEventModel):
    broadcaster: UserModel | None = None
    follower: UserModel | None = None

class ChannelSubscriptionEvent(BaseEventModel):
    broadcaster: UserModel | None = None
    subscriber: UserModel | None = None
    duration: int | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None

class ChannelGiftSubscriptionEvent(BaseEventModel):
    broadcaster: UserModel | None = None
    gifter: UserModel | None = None
    giftees: list[UserModel] = Field(default_factory=list)
    created_at: datetime | None = None
    expires_at: datetime | None = None

class LivestreamUpdatedEvent(BaseEventModel):
    broadcaster: UserModel | None = None
    is_live: bool | None = None
    title: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None

class LivestreamMetadataUpdatedEvent(BaseEventModel):
    broadcaster: UserModel | None = None
    metadata: LiveStreamMetadataModel | None = None

class ModerationBanEvent(BaseEventModel):
    broadcaster: UserModel | None = None
    moderator: UserModel | None = None
    banned_user: UserModel | None = None
    metadata: ModerationMetadataModel | None = None

# ----------- END OF EVENT MODELS -----------
