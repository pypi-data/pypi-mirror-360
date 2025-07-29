import enum


class LibEvents(enum.StrEnum):
    ON_MESSAGE = "chat.message.sent"
    ON_FOLLOW = "channel.followed"
    ON_SUBSCRIPTION = "channel.subscription.renewal"
    ON_SUBSCRIPTION_GIFT = "channel.subscription.gifts"
    ON_NEW_SUBSCRIPTION = "channel.subscription.new"
    ON_LIVESTREAM_UPDATED = "livestream.status.updated"
    ON_LIVESTREAM_METADATA_UPDATED = "livestream.metadata.updated"
    ON_MODERATION_BANNED = "moderation.banned"
    
    def __str__(self):
        return self.value

class Scopes(enum.StrEnum):
    USER_READ = "user:read"
    CHANNEL_READ = "channel:read"
    CHANNEL_WRITE = "channel:write"
    CHAT_WRITE = "chat:write"
    STREAMKEY_READ = "streamkey:read"
    EVENTS_SUBSCRIBE = "events:subscribe"
    MODERATION_BAN = "moderation:ban"
    
    def __str__(self):
        return self.value

class Events(enum.StrEnum):
    """ Enum for Kick API events.
    This enum defines the various events that can be subscribed to in the Kick API.
    Each event corresponds to a specific action or change in the Kick platform.
    """
    ON_OAUTH_URL = "on_oauth_url"
    ON_READY = "on_ready"
    ON_ERROR = "on_error"
    ON_DISCONNECT = "on_disconnect"
    ON_MESSAGE = "on_message"
    ON_FOLLOW = "on_follow"
    ON_SUBSCRIPTION = "on_subscription"
    ON_SUBSCRIPTION_GIFT = "on_subscription_gift"
    ON_LIVESTREAM_STARTED = "on_livestream_started"
    ON_LIVESTREAM_ENDED = "on_livestream_ended"
    ON_LIVESTREAM_UPDATED = "on_livestream_updated"
    ON_MODERATION_TIMEOUT = "on_timeout"
    ON_MODERATION_BAN = "on_ban"

class CacheStrategy(enum.StrEnum):
    """ Enum for cache strategies.
    This enum defines the strategies for caching data in the Kick API.
    """
    UPDATE = "update"
    ERASE = "erase"
    IGNORE = "ignore"

    def __str__(self):
        return self.value
