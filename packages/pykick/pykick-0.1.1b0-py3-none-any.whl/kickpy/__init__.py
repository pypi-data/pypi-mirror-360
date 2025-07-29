from .client import (
    KickClient,
    Events,
    Token,
    ExtendedToken,
    Category,
    User,
    Broadcaster,
    AnonymousUser,
    Channel,
    Stream,
    Message,
    Identity,
    EventSubscription,
    ExtendedEventSubscription,
    Subscription,
    Gift,
    Moderation,
    Timeout,
    Ban,
    Badge,
    Emote
)

from .enum import Scopes

from . import meta

class lib:
    from . import _http
    from . import models

class abc:
    from .client import (
        Token,
        ExtendedToken,
        Category,
        User,
        Broadcaster,
        AnonymousUser,
        Channel,
        Stream,
        Message,
        Identity,
        EventSubscription,
        ExtendedEventSubscription,
        Subscription,
        Gift,
        Moderation,
        Timeout,
        Ban,
        Badge,
        Emote
    )

class api:
    from .client import (
        OauthAPI,
        UsersAPI,
        EventsAPI,
        StreamsAPI,
        ChannelsAPI,
        CategoriesAPI,
        ModerationAPI
    )

__version__ = meta.__version__

__all__ = [
    KickClient, abc, api, lib, Events, Token, ExtendedToken, Category, User, Broadcaster,
    AnonymousUser, Channel, Stream, Message, Identity,
    EventSubscription, ExtendedEventSubscription, Subscription, Gift,
    Moderation, Timeout, Ban, Badge, Emote, Scopes, meta
]
