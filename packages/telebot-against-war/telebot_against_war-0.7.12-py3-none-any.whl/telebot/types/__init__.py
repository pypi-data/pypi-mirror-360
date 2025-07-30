import logging
import os
from abc import ABC
from dataclasses import dataclass
from hashlib import md5
from io import BytesIO, IOBase
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union, get_args

import ujson as json  # type: ignore

from telebot import util
from telebot.metrics import MessageInfo, TelegramUpdateMetrics, UserInfo

DISABLE_KEYLEN_ERROR = False

logger = logging.getLogger("TeleBot")


class JsonSerializable(object):
    """
    Subclasses of this class are guaranteed to be able to be converted to JSON format.
    All subclasses of this class must override to_json.
    """

    def to_json(self):
        """
        Returns a JSON string representation of this class.

        This function must be overridden by subclasses.
        :return: a JSON formatted string.
        """
        raise NotImplementedError


class Dictionaryable(object):
    """
    Subclasses of this class are guaranteed to be able to be converted to dictionary.
    All subclasses of this class must override to_dict.
    """

    def to_dict(self) -> dict:
        """
        Returns a DICT with class field values

        This function must be overridden by subclasses.
        :return: a DICT
        """
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        if isinstance(other, Dictionaryable):
            return self.to_dict() == other.to_dict()
        else:
            return False


class JsonDeserializable(object):
    """
    Subclasses of this class are guaranteed to be able to be created from a json-style dict or json formatted string.
    All subclasses of this class must override de_json.
    """

    @classmethod
    def de_json(cls, json_string):
        """
        Returns an instance of this class from the given json dict or string.

        This function must be overridden by subclasses.
        :return: an instance of this class created from the given json dict or string.
        """
        raise NotImplementedError

    @staticmethod
    def ensure_json_dict(json_: Union[str, dict], copy_dict=True) -> dict:
        """
        Checks whether json_type is a dict or a string. If it is already a dict, it is returned as-is.
        If it is not, it is converted to a dict by means of json.loads(json_type)

        :param json_type: input json or parsed dict
        :param dict_copy: if dict is passed and it is changed outside - should be True!
        :return: Dictionary parsed from json or original dict
        """
        if isinstance(json_, dict):
            return json_.copy() if copy_dict else json_
        elif isinstance(json_, str):
            return json.loads(json_)
        else:
            raise ValueError("json_type should be a json dict or string.")

    @classmethod
    def check_json(cls, json, copy_dict=True) -> dict:
        return cls.ensure_json_dict(json, copy_dict)

    def __str__(self):
        d = {x: y.__dict__ if hasattr(y, "__dict__") else y for x, y in self.__dict__.items()}
        return f"{self.__class__.__name__}({d})"


@dataclass
class Update(JsonDeserializable):
    update_id: int
    message: Optional["Message"]
    edited_message: Optional["Message"]
    channel_post: Optional["Message"]
    edited_channel_post: Optional["Message"]
    inline_query: Optional["InlineQuery"]
    chosen_inline_result: Optional["ChosenInlineResult"]
    callback_query: Optional["CallbackQuery"]
    shipping_query: Optional["ShippingQuery"]
    pre_checkout_query: Optional["PreCheckoutQuery"]
    poll: Optional["Poll"]
    poll_answer: Optional["PollAnswer"]
    my_chat_member: Optional["ChatMemberUpdated"]
    chat_member: Optional["ChatMemberUpdated"]
    chat_join_request: Optional["ChatJoinRequest"]

    _json_dict: dict

    metrics: Optional[TelegramUpdateMetrics] = None

    @classmethod
    def de_json(
        cls,
        json_: Optional[Union[dict, str]],
        metrics: Optional[TelegramUpdateMetrics] = None,
    ) -> Optional["Update"]:
        if json_ is None:
            return None
        obj = cls.ensure_json_dict(json_, copy_dict=False)
        update_id = obj["update_id"]
        if metrics:
            metrics["update_id"] = update_id
            for update_type_name in get_args(AllowedUpdateName):
                if update_type_name != "update_id" and update_type_name in obj:
                    metrics["update_type"] = update_type_name
                    break
        message = Message.de_json(obj.get("message"), metrics=metrics)
        edited_message = Message.de_json(obj.get("edited_message"), metrics=metrics)
        channel_post = Message.de_json(obj.get("channel_post"), metrics=metrics)
        edited_channel_post = Message.de_json(obj.get("edited_channel_post"), metrics=metrics)
        inline_query = InlineQuery.de_json(obj.get("inline_query"))
        chosen_inline_result = ChosenInlineResult.de_json(obj.get("chosen_inline_result"))
        callback_query = CallbackQuery.de_json(obj.get("callback_query"))
        shipping_query = ShippingQuery.de_json(obj.get("shipping_query"))
        pre_checkout_query = PreCheckoutQuery.de_json(obj.get("pre_checkout_query"))
        poll = Poll.de_json(obj.get("poll"))
        poll_answer = PollAnswer.de_json(obj.get("poll_answer"))
        my_chat_member = ChatMemberUpdated.de_json(obj.get("my_chat_member"))
        chat_member = ChatMemberUpdated.de_json(obj.get("chat_member"))
        chat_join_request = ChatJoinRequest.de_json(obj.get("chat_join_request"))
        return Update(
            update_id,
            message,
            edited_message,
            channel_post,
            edited_channel_post,
            inline_query,
            chosen_inline_result,
            callback_query,
            shipping_query,
            pre_checkout_query,
            poll,
            poll_answer,
            my_chat_member,
            chat_member,
            chat_join_request,
            _json_dict=obj,
            metrics=metrics,
        )


class ChatMemberUpdated(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["chat"] = Chat.de_json(obj["chat"])
        obj["from_user"] = User.de_json(obj.pop("from"))
        obj["old_chat_member"] = ChatMember.de_json(obj["old_chat_member"])
        obj["new_chat_member"] = ChatMember.de_json(obj["new_chat_member"])
        obj["invite_link"] = ChatInviteLink.de_json(obj.get("invite_link"))
        return cls(**obj)

    def __init__(
        self,
        chat: "Chat",
        from_user: "User",
        date: int,
        old_chat_member: "ChatMember",
        new_chat_member: "ChatMember",
        invite_link: Optional["ChatInviteLink"] = None,
        **kwargs,
    ):
        self.chat = chat
        self.from_user = from_user
        self.date = date
        self.old_chat_member = old_chat_member
        self.new_chat_member = new_chat_member
        self.invite_link = invite_link

    @property
    def difference(self) -> Dict[str, List]:
        """
        Get the difference between `old_chat_member` and `new_chat_member`
        as a dict in the following format {'parameter': [old_value, new_value]}
        E.g {'status': ['member', 'kicked'], 'until_date': [None, 1625055092]}
        """
        old: Dict = self.old_chat_member.__dict__
        new: Dict = self.new_chat_member.__dict__
        dif = {}
        for key in new:
            if key == "user":
                continue
            if new[key] != old[key]:
                dif[key] = [old[key], new[key]]
        return dif


class ChatJoinRequest(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["chat"] = Chat.de_json(obj["chat"])
        obj["from_user"] = User.de_json(obj["from"])
        obj["invite_link"] = ChatInviteLink.de_json(obj.get("invite_link"))
        return cls(**obj)

    def __init__(
        self,
        chat: "Chat",
        from_user: "User",
        user_chat_id: int,
        date: int,
        bio: Optional[str] = None,
        invite_link: Optional["ChatInviteLink"] = None,
        **kwargs,
    ):
        self.chat = chat
        self.from_user = from_user
        self.date = date
        self.bio = bio
        self.invite_link = invite_link
        self.user_chat_id = user_chat_id


class WebhookInfo(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(
        self,
        url: str,
        has_custom_certificate: bool,
        pending_update_count: int,
        ip_address=None,
        last_error_date=None,
        last_error_message=None,
        last_synchronization_error_date=None,
        max_connections=None,
        allowed_updates=None,
        **kwargs,
    ):
        self.url = url
        self.has_custom_certificate = has_custom_certificate
        self.pending_update_count = pending_update_count
        self.ip_address = ip_address
        self.last_error_date = last_error_date
        self.last_error_message = last_error_message
        self.last_synchronization_error_date = last_synchronization_error_date
        self.max_connections = max_connections
        self.allowed_updates = allowed_updates


class User(JsonDeserializable, Dictionaryable, JsonSerializable):
    @classmethod
    def de_json(cls, json_string, metrics: Optional[TelegramUpdateMetrics] = None):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        user_obj = cls(**obj)
        if metrics is not None:
            metrics["user_info"] = UserInfo(
                user_id_hash=md5(user_obj.id.to_bytes(length=64, byteorder="big")).hexdigest(),
                language_code=user_obj.language_code,
            )
        return user_obj

    def __init__(
        self,
        id: int,
        is_bot: bool,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        language_code: Optional[str] = None,
        can_join_groups: Optional[bool] = None,
        can_read_all_group_messages: Optional[bool] = None,
        supports_inline_queries: Optional[bool] = None,
        is_premium: Optional[bool] = None,
        added_to_attachment_menu: Optional[bool] = None,
        **kwargs,
    ):
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.username = username
        self.last_name = last_name
        self.language_code = language_code
        self.can_join_groups = can_join_groups
        self.can_read_all_group_messages = can_read_all_group_messages
        self.supports_inline_queries = supports_inline_queries
        self.is_premium = is_premium
        self.added_to_attachment_menu = added_to_attachment_menu

    @property
    def full_name(self):
        full_name = self.first_name
        if self.last_name:
            full_name += " {0}".format(self.last_name)
        return full_name

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "id": self.id,
            "is_bot": self.is_bot,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "language_code": self.language_code,
            "can_join_groups": self.can_join_groups,
            "can_read_all_group_messages": self.can_read_all_group_messages,
            "supports_inline_queries": self.supports_inline_queries,
            "is_premium": self.is_premium,
            "added_to_attachment_menu": self.added_to_attachment_menu,
        }

    def __hash__(self) -> int:
        # HACK: we use the fact that user id is unique
        #       more systematic solution is required
        return self.id


class GroupChat(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, id, title, **kwargs):
        self.id: int = id
        self.title: str = title


class Chat(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "photo" in obj:
            obj["photo"] = ChatPhoto.de_json(obj["photo"])
        if "pinned_message" in obj:
            obj["pinned_message"] = Message.de_json(obj["pinned_message"])
        if "permissions" in obj:
            obj["permissions"] = ChatPermissions.de_json(obj["permissions"])
        if "location" in obj:
            obj["location"] = ChatLocation.de_json(obj["location"])
        return cls(**obj)

    def __init__(
        self,
        id: int,
        type: str,
        title: Optional[str] = None,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        photo: Optional["ChatPhoto"] = None,
        bio: Optional[str] = None,
        has_private_forwards: Optional[bool] = None,
        description: Optional[str] = None,
        invite_link: Optional[str] = None,
        pinned_message: Optional["Message"] = None,
        permissions: Optional["ChatPermissions"] = None,
        slow_mode_delay: Optional[int] = None,
        message_auto_delete_time: Optional[int] = None,
        has_protected_content: Optional[bool] = None,
        sticker_set_name: Optional[str] = None,
        can_set_sticker_set: Optional[bool] = None,
        linked_chat_id: Optional[int] = None,
        location: Optional["ChatLocation"] = None,
        join_to_send_messages: Optional[bool] = None,
        join_by_request: Optional[bool] = None,
        has_restricted_voice_and_video_messages: Optional[bool] = None,
        is_forum: Optional[bool] = None,
        active_usernames: Optional[List[str]] = None,
        emoji_status_custom_emoji_id: Optional[str] = None,
        has_hidden_members: Optional[bool] = None,
        has_aggressive_anti_spam_enabled: Optional[bool] = None,
        **kwargs,
    ):
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.photo = photo
        self.bio = bio
        self.has_private_forwards = has_private_forwards
        self.description = description
        self.invite_link = invite_link
        self.pinned_message = pinned_message
        self.permissions = permissions
        self.slow_mode_delay = slow_mode_delay
        self.message_auto_delete_time = message_auto_delete_time
        self.has_protected_content = has_protected_content
        self.sticker_set_name = sticker_set_name
        self.can_set_sticker_set = can_set_sticker_set
        self.linked_chat_id = linked_chat_id
        self.location = location
        self.join_to_send_messages = join_to_send_messages
        self.join_by_request = join_by_request
        self.has_restricted_voice_and_video_messages = has_restricted_voice_and_video_messages
        self.is_forum = is_forum
        self.active_usernames = active_usernames
        self.emoji_status_custom_emoji_id = emoji_status_custom_emoji_id
        self.has_hidden_members = has_hidden_members
        self.has_aggressive_anti_spam_enabled = has_aggressive_anti_spam_enabled


class MessageID(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, message_id, **kwargs):
        self.message_id = message_id


class WebAppData(JsonDeserializable):
    def __init__(self, data, button_text):
        self.data = data
        self.button_text = button_text

    def to_dict(self):
        return {"data": self.data, "button_text": self.button_text}

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)


class Message(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string, metrics: Optional[TelegramUpdateMetrics] = None) -> "Message":
        if json_string is None:
            return None  # type: ignore
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        message_id = obj["message_id"]
        from_user = User.de_json(obj.get("from"), metrics)
        date = obj["date"]
        chat = Chat.de_json(obj["chat"])
        content_type = None
        is_forwarded = False
        is_reply = False
        opts = {}
        if "sender_chat" in obj:
            opts["sender_chat"] = Chat.de_json(obj["sender_chat"])
        if "forward_from" in obj:
            opts["forward_from"] = User.de_json(obj["forward_from"])
        if "forward_from_chat" in obj:
            opts["forward_from_chat"] = Chat.de_json(obj["forward_from_chat"])
            is_forwarded = True
        if "forward_from_message_id" in obj:
            opts["forward_from_message_id"] = obj.get("forward_from_message_id")
        if "forward_signature" in obj:
            opts["forward_signature"] = obj.get("forward_signature")
        if "forward_sender_name" in obj:
            opts["forward_sender_name"] = obj.get("forward_sender_name")
        if "forward_date" in obj:
            opts["forward_date"] = obj.get("forward_date")
        if "is_automatic_forward" in obj:
            opts["is_automatic_forward"] = obj.get("is_automatic_forward")
        if "is_topic_message" in obj:
            opts["is_topic_message"] = obj.get("is_topic_message")
        if "message_thread_id" in obj:
            opts["message_thread_id"] = obj.get("message_thread_id")
        if "reply_to_message" in obj:
            opts["reply_to_message"] = Message.de_json(obj["reply_to_message"])
            is_reply = True
        if "via_bot" in obj:
            opts["via_bot"] = User.de_json(obj["via_bot"])
        if "edit_date" in obj:
            opts["edit_date"] = obj.get("edit_date")
        if "has_protected_content" in obj:
            opts["has_protected_content"] = obj.get("has_protected_content")
        if "media_group_id" in obj:
            opts["media_group_id"] = obj.get("media_group_id")
        if "author_signature" in obj:
            opts["author_signature"] = obj.get("author_signature")
        if "text" in obj:
            opts["text"] = obj["text"]
            content_type = "text"
        if "entities" in obj:
            opts["entities"] = Message.parse_entities(obj["entities"])
        if "caption_entities" in obj:
            opts["caption_entities"] = Message.parse_entities(obj["caption_entities"])
        if "audio" in obj:
            opts["audio"] = Audio.de_json(obj["audio"])
            content_type = "audio"
        if "document" in obj:
            opts["document"] = Document.de_json(obj["document"])
            content_type = "document"
        if "animation" in obj:
            # Document content type accompanies "animation",
            # so "animation" should be checked below "document" to override it
            opts["animation"] = Animation.de_json(obj["animation"])
            content_type = "animation"
        if "game" in obj:
            opts["game"] = Game.de_json(obj["game"])
            content_type = "game"
        if "photo" in obj:
            opts["photo"] = Message.parse_photo(obj["photo"])
            content_type = "photo"
        if "sticker" in obj:
            opts["sticker"] = Sticker.de_json(obj["sticker"])
            content_type = "sticker"
        if "video" in obj:
            opts["video"] = Video.de_json(obj["video"])
            content_type = "video"
        if "video_note" in obj:
            opts["video_note"] = VideoNote.de_json(obj["video_note"])
            content_type = "video_note"
        if "voice" in obj:
            opts["voice"] = Audio.de_json(obj["voice"])
            content_type = "voice"
        if "caption" in obj:
            opts["caption"] = obj["caption"]
        if "contact" in obj:
            opts["contact"] = Contact.de_json(json.dumps(obj["contact"]))
            content_type = "contact"
        if "location" in obj:
            opts["location"] = Location.de_json(obj["location"])
            content_type = "location"
        if "venue" in obj:
            opts["venue"] = Venue.de_json(obj["venue"])
            content_type = "venue"
        if "dice" in obj:
            opts["dice"] = Dice.de_json(obj["dice"])
            content_type = "dice"
        if "new_chat_members" in obj:
            new_chat_members = []
            for member in obj["new_chat_members"]:
                new_chat_members.append(User.de_json(member))
            opts["new_chat_members"] = new_chat_members
            content_type = "new_chat_members"
        if "left_chat_member" in obj:
            opts["left_chat_member"] = User.de_json(obj["left_chat_member"])
            content_type = "left_chat_member"
        if "new_chat_title" in obj:
            opts["new_chat_title"] = obj["new_chat_title"]
            content_type = "new_chat_title"
        if "new_chat_photo" in obj:
            opts["new_chat_photo"] = Message.parse_photo(obj["new_chat_photo"])
            content_type = "new_chat_photo"
        if "delete_chat_photo" in obj:
            opts["delete_chat_photo"] = obj["delete_chat_photo"]
            content_type = "delete_chat_photo"
        if "group_chat_created" in obj:
            opts["group_chat_created"] = obj["group_chat_created"]
            content_type = "group_chat_created"
        if "supergroup_chat_created" in obj:
            opts["supergroup_chat_created"] = obj["supergroup_chat_created"]
            content_type = "supergroup_chat_created"
        if "channel_chat_created" in obj:
            opts["channel_chat_created"] = obj["channel_chat_created"]
            content_type = "channel_chat_created"
        if "migrate_to_chat_id" in obj:
            opts["migrate_to_chat_id"] = obj["migrate_to_chat_id"]
            content_type = "migrate_to_chat_id"
        if "migrate_from_chat_id" in obj:
            opts["migrate_from_chat_id"] = obj["migrate_from_chat_id"]
            content_type = "migrate_from_chat_id"
        if "pinned_message" in obj:
            opts["pinned_message"] = Message.de_json(obj["pinned_message"])
            content_type = "pinned_message"
        if "invoice" in obj:
            opts["invoice"] = Invoice.de_json(obj["invoice"])
            content_type = "invoice"
        if "successful_payment" in obj:
            opts["successful_payment"] = SuccessfulPayment.de_json(obj["successful_payment"])
            content_type = "successful_payment"
        if "connected_website" in obj:
            opts["connected_website"] = obj["connected_website"]
            content_type = "connected_website"
        if "poll" in obj:
            opts["poll"] = Poll.de_json(obj["poll"])
            content_type = "poll"
        if "passport_data" in obj:
            opts["passport_data"] = obj["passport_data"]
            content_type = "passport_data"
        if "proximity_alert_triggered" in obj:
            opts["proximity_alert_triggered"] = ProximityAlertTriggered.de_json(obj["proximity_alert_triggered"])
            content_type = "proximity_alert_triggered"
        if "video_chat_scheduled" in obj:
            opts["video_chat_scheduled"] = VideoChatScheduled.de_json(obj["video_chat_scheduled"])
            opts["voice_chat_scheduled"] = opts["video_chat_scheduled"]  # deprecated, for backward compatibility
            content_type = "video_chat_scheduled"
        if "video_chat_started" in obj:
            opts["video_chat_started"] = VideoChatStarted.de_json(obj["video_chat_started"])
            opts["voice_chat_started"] = opts["video_chat_started"]  # deprecated, for backward compatibility
            content_type = "video_chat_started"
        if "video_chat_ended" in obj:
            opts["video_chat_ended"] = VideoChatEnded.de_json(obj["video_chat_ended"])
            opts["voice_chat_ended"] = opts["video_chat_ended"]  # deprecated, for backward compatibility
            content_type = "video_chat_ended"
        if "video_chat_participants_invited" in obj:
            opts["video_chat_participants_invited"] = VideoChatParticipantsInvited.de_json(
                obj["video_chat_participants_invited"]
            )
            opts["voice_chat_participants_invited"] = opts[
                "video_chat_participants_invited"
            ]  # deprecated, for backward compatibility
            content_type = "video_chat_participants_invited"
        if "web_app_data" in obj:
            opts["web_app_data"] = WebAppData.de_json(obj["web_app_data"])
            content_type = "web_app_data"
        if "message_auto_delete_timer_changed" in obj:
            opts["message_auto_delete_timer_changed"] = MessageAutoDeleteTimerChanged.de_json(
                obj["message_auto_delete_timer_changed"]
            )
            content_type = "message_auto_delete_timer_changed"
        if "reply_markup" in obj:
            opts["reply_markup"] = InlineKeyboardMarkup.de_json(obj["reply_markup"])
        if "forum_topic_created" in obj:
            opts["forum_topic_created"] = ForumTopicCreated.de_json(obj["forum_topic_created"])
            content_type = "forum_topic_created"
        if "forum_topic_closed" in obj:
            opts["forum_topic_closed"] = ForumTopicClosed.de_json(obj["forum_topic_closed"])
            content_type = "forum_topic_closed"
        if "forum_topic_reopened" in obj:
            opts["forum_topic_reopened"] = ForumTopicReopened.de_json(obj["forum_topic_reopened"])
            content_type = "forum_topic_reopened"
        if "has_media_spoiler" in obj:
            opts["has_media_spoiler"] = obj["has_media_spoiler"]
        if "forum_topic_edited" in obj:
            opts["forum_topic_edited"] = ForumTopicEdited.de_json(obj["forum_topic_edited"])
            content_type = "forum_topic_edited"
        if "general_forum_topic_hidden" in obj:
            opts["general_forum_topic_hidden"] = GeneralForumTopicHidden.de_json(obj["general_forum_topic_hidden"])
            content_type = "general_forum_topic_hidden"
        if "general_forum_topic_unhidden" in obj:
            opts["general_forum_topic_unhidden"] = GeneralForumTopicUnhidden.de_json(
                obj["general_forum_topic_unhidden"]
            )
            content_type = "general_forum_topic_unhidden"
        if "write_access_allowed" in obj:
            opts["write_access_allowed"] = WriteAccessAllowed.de_json(obj["write_access_allowed"])
            content_type = "write_access_allowed"
        if "user_shared" in obj:
            opts["user_shared"] = UserShared.de_json(obj["user_shared"])
            content_type = "user_shared"
        if "chat_shared" in obj:
            opts["chat_shared"] = ChatShared.de_json(obj["chat_shared"])
            content_type = "chat_shared"
        if metrics is not None:
            metrics["message_info"] = MessageInfo(
                is_forwarded=is_forwarded,
                is_reply=is_reply,
                content_type=content_type or "<unset>",
            )
        return cls(
            message_id,
            from_user,
            date,
            chat,
            content_type or "<unset>",
            opts,
            json_string,
        )

    @classmethod
    def parse_chat(cls, chat):
        if "first_name" not in chat:
            return GroupChat.de_json(chat)
        else:
            return User.de_json(chat)

    @classmethod
    def parse_photo(cls, photo_size_array):
        ret = []
        for ps in photo_size_array:
            ret.append(PhotoSize.de_json(ps))
        return ret

    @classmethod
    def parse_entities(cls, message_entity_array):
        ret = []
        for me in message_entity_array:
            ret.append(MessageEntity.de_json(me))
        return ret

    def __init__(
        self,
        message_id: int,
        from_user: User,
        date: int,
        chat: Chat,
        content_type: str,
        options,
        json_string,
    ):
        self.content_type: str = content_type
        self.id: int = message_id  # Lets fix the telegram usability ####up with ID in Message :)
        self.message_id: int = message_id
        self.from_user: User = from_user
        self.date: int = date
        self.chat: Chat = chat
        self.sender_chat: Optional[Chat] = None
        self.forward_from: Optional[User] = None
        self.forward_from_chat: Optional[Chat] = None
        self.forward_from_message_id: Optional[int] = None
        self.forward_signature: Optional[str] = None
        self.forward_sender_name: Optional[str] = None
        self.forward_date: Optional[int] = None
        self.is_automatic_forward: Optional[bool] = None
        self.reply_to_message: Optional[Message] = None
        self.via_bot: Optional[User] = None
        self.edit_date: Optional[int] = None
        self.has_protected_content: Optional[bool] = None
        self.media_group_id: Optional[str] = None
        self.author_signature: Optional[str] = None
        self.text: Optional[str] = None
        self.entities: Optional[List[MessageEntity]] = None
        self.caption_entities: Optional[List[MessageEntity]] = None
        self.audio: Optional[Audio] = None
        self.document: Optional[Document] = None
        self.photo: Optional[List[PhotoSize]] = None
        self.sticker: Optional[Sticker] = None
        self.video: Optional[Video] = None
        self.video_note: Optional[VideoNote] = None
        self.voice: Optional[Voice] = None
        self.caption: Optional[str] = None
        self.contact: Optional[Contact] = None
        self.location: Optional[Location] = None
        self.venue: Optional[Venue] = None
        self.animation: Optional[Animation] = None
        self.dice: Optional[Dice] = None
        self.new_chat_member: Optional[User] = None  # Deprecated since Bot API 3.0. Not processed anymore
        self.new_chat_members: Optional[List[User]] = None
        self.left_chat_member: Optional[User] = None
        self.new_chat_title: Optional[str] = None
        self.new_chat_photo: Optional[List[PhotoSize]] = None
        self.delete_chat_photo: Optional[bool] = None
        self.group_chat_created: Optional[bool] = None
        self.supergroup_chat_created: Optional[bool] = None
        self.channel_chat_created: Optional[bool] = None
        self.migrate_to_chat_id: Optional[int] = None
        self.migrate_from_chat_id: Optional[int] = None
        self.pinned_message: Optional[Message] = None
        self.invoice: Optional[Invoice] = None
        self.successful_payment: Optional[SuccessfulPayment] = None
        self.connected_website: Optional[str] = None
        self.reply_markup: Optional[InlineKeyboardMarkup] = None
        self.message_thread_id: Optional[int] = None
        self.is_topic_message: Optional[bool] = None
        self.forum_topic_created: Optional[ForumTopicCreated] = None
        self.forum_topic_closed: Optional[ForumTopicClosed] = None
        self.forum_topic_reopened: Optional[ForumTopicReopened] = None
        self.has_media_spoiler: Optional[bool] = None
        self.forum_topic_edited: Optional[ForumTopicEdited] = None
        self.general_forum_topic_hidden: Optional[GeneralForumTopicHidden] = None
        self.general_forum_topic_unhidden: Optional[GeneralForumTopicUnhidden] = None
        self.write_access_allowed: Optional[WriteAccessAllowed] = None
        self.user_shared: Optional[UserShared] = None
        self.chat_shared: Optional[ChatShared] = None
        for key in options:
            setattr(self, key, options[key])
        self.json = json_string
        self.splitted_messages: Optional[list[Message]] = None

    def __html_text(self, text, entities):
        """
        Author: @sviat9440
        Updaters: @badiboy
        Message: "*Test* parse _formatting_, [url](https://example.com), [text_mention](tg://user?id=123456) and mention @username"

        Example:
            message.html_text
            >> "<b>Test</b> parse <i>formatting</i>, <a href=\"https://example.com\">url</a>, <a href=\"tg://user?id=123456\">text_mention</a> and mention @username"

        Custom subs:
            You can customize the substitutes. By default, there is no substitute for the entities: hashtag, bot_command, email. You can add or modify substitute an existing entity.
        Example:
            message.custom_subs = {"bold": "<strong class=\"example\">{text}</strong>", "italic": "<i class=\"example\">{text}</i>", "mention": "<a href={url}>{text}</a>"}
            message.html_text
            >> "<strong class=\"example\">Test</strong> parse <i class=\"example\">formatting</i>, <a href=\"https://example.com\">url</a> and <a href=\"tg://user?id=123456\">text_mention</a> and mention <a href=\"https://t.me/username\">@username</a>"
        """

        if not entities:
            return text

        _subs = {
            "bold": "<b>{text}</b>",
            "italic": "<i>{text}</i>",
            "pre": "<pre>{text}</pre>",
            "code": "<code>{text}</code>",
            # "url": "<a href=\"{url}\">{text}</a>", # @badiboy plain URLs have no text and do not need tags
            "text_link": '<a href="{url}">{text}</a>',
            "strikethrough": "<s>{text}</s>",
            "underline": "<u>{text}</u>",
            "spoiler": '<span class="tg-spoiler">{text}</span>',
        }

        if hasattr(self, "custom_subs"):
            for key, value in self.custom_subs.items():
                _subs[key] = value
        utf16_text = text.encode("utf-16-le")
        html_text = ""

        def func(upd_text, subst_type=None, url=None, user=None):
            upd_text = upd_text.decode("utf-16-le")
            if subst_type == "text_mention":
                subst_type = "text_link"
                url = "tg://user?id={0}".format(user.id)
            elif subst_type == "mention":
                url = "https://t.me/{0}".format(upd_text[1:])
            upd_text = upd_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            if not subst_type or not _subs.get(subst_type):
                return upd_text
            subs = _subs.get(subst_type)
            return subs.format(text=upd_text, url=url)

        offset = 0
        for entity in entities:
            if entity.offset > offset:
                html_text += func(utf16_text[offset * 2 : entity.offset * 2])
                offset = entity.offset
                html_text += func(
                    utf16_text[offset * 2 : (offset + entity.length) * 2],
                    entity.type,
                    entity.url,
                    entity.user,
                )
                offset += entity.length
            elif entity.offset == offset:
                html_text += func(
                    utf16_text[offset * 2 : (offset + entity.length) * 2],
                    entity.type,
                    entity.url,
                    entity.user,
                )
                offset += entity.length
            else:
                # Here we are processing nested entities.
                # We shouldn't update offset, because they are the same as entity before.
                # And, here we are replacing previous string with a new html-rendered text(previous string is already html-rendered,
                # And we don't change it).
                entity_string = utf16_text[entity.offset * 2 : (entity.offset + entity.length) * 2]
                formatted_string = func(entity_string, entity.type, entity.url, entity.user)
                entity_string_decoded = entity_string.decode("utf-16-le")
                last_occurence = html_text.rfind(entity_string_decoded)
                string_length = len(entity_string_decoded)
                # html_text = html_text.replace(html_text[last_occurence:last_occurence+string_length], formatted_string)
                html_text = html_text[:last_occurence] + formatted_string + html_text[last_occurence + string_length :]
        if offset * 2 < len(utf16_text):
            html_text += func(utf16_text[offset * 2 :])
        return html_text

    @property
    def html_text(self):
        return self.__html_text(self.text, self.entities)

    @property
    def html_caption(self):
        return self.__html_text(self.caption, self.caption_entities)

    @property
    def text_content(self) -> str:
        return self.text or self.caption or ""


@dataclass
class MessageEntity(Dictionaryable, JsonSerializable, JsonDeserializable):
    type: str
    offset: int
    length: int
    url: str | None = None  # for type = "text_link"
    user: User | None = None  # for type = "text_mention"
    language: str | None = None  # for type = "pre"
    custom_emoji_id: str | None = None  # for type = "custom_emoji"

    @staticmethod
    def to_list_of_dicts(entity_list) -> Union[List[Dict], None]:
        res = []
        for e in entity_list:
            res.append(MessageEntity.to_dict(e))
        return res or None

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "user" in obj:
            obj["user"] = User.de_json(obj["user"])
        return cls(**obj)

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        res = {
            "type": self.type,
            "offset": self.offset,
            "length": self.length,
        }
        if self.url is not None:
            res["url"] = self.url
        if self.user is not None:
            res["user"] = self.user.to_dict()
        if self.language is not None:
            res["language"] = self.language
        if self.custom_emoji_id is not None:
            res["custom_emoji_id"] = self.custom_emoji_id
        return res


TiedToChat = Union[ChatMemberUpdated, ChatJoinRequest, Message]


class Dice(JsonSerializable, Dictionaryable, JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, value, emoji, **kwargs):
        self.value: int = value
        self.emoji: str = emoji

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {"value": self.value, "emoji": self.emoji}


class PhotoSize(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, file_id, file_unique_id, width, height, file_size=None, **kwargs):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.width: int = width
        self.height: int = height
        self.file_size: int = file_size


class Audio(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "thumb" in obj and "file_id" in obj["thumb"]:
            obj["thumb"] = PhotoSize.de_json(obj["thumb"])
        else:
            obj["thumb"] = None
        return cls(**obj)

    def __init__(
        self,
        file_id,
        file_unique_id,
        duration,
        performer=None,
        title=None,
        file_name=None,
        mime_type=None,
        file_size=None,
        thumb=None,
        **kwargs,
    ):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.duration: int = duration
        self.performer: str = performer
        self.title: str = title
        self.file_name: str = file_name
        self.mime_type: str = mime_type
        self.file_size: int = file_size
        self.thumb: PhotoSize = thumb


class Voice(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(
        self,
        file_id,
        file_unique_id,
        duration,
        mime_type=None,
        file_size=None,
        **kwargs,
    ):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.duration: int = duration
        self.mime_type: str = mime_type
        self.file_size: int = file_size


class Document(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "thumb" in obj and "file_id" in obj["thumb"]:
            obj["thumb"] = PhotoSize.de_json(obj["thumb"])
        else:
            obj["thumb"] = None
        return cls(**obj)

    def __init__(
        self,
        file_id,
        file_unique_id,
        thumb=None,
        file_name=None,
        mime_type=None,
        file_size=None,
        **kwargs,
    ):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.thumb: PhotoSize = thumb
        self.file_name: str = file_name
        self.mime_type: str = mime_type
        self.file_size: int = file_size


class Video(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "thumb" in obj and "file_id" in obj["thumb"]:
            obj["thumb"] = PhotoSize.de_json(obj["thumb"])
        return cls(**obj)

    def __init__(
        self,
        file_id,
        file_unique_id,
        width,
        height,
        duration,
        thumb=None,
        file_name=None,
        mime_type=None,
        file_size=None,
        **kwargs,
    ):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.width: int = width
        self.height: int = height
        self.duration: int = duration
        self.thumb: PhotoSize = thumb
        self.file_name: str = file_name
        self.mime_type: str = mime_type
        self.file_size: int = file_size


class VideoNote(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "thumb" in obj and "file_id" in obj["thumb"]:
            obj["thumb"] = PhotoSize.de_json(obj["thumb"])
        return cls(**obj)

    def __init__(
        self,
        file_id,
        file_unique_id,
        length,
        duration,
        thumb=None,
        file_size=None,
        **kwargs,
    ):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.length: int = length
        self.duration: int = duration
        self.thumb: PhotoSize = thumb
        self.file_size: int = file_size


class Contact(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(
        self,
        phone_number,
        first_name,
        last_name=None,
        user_id=None,
        vcard=None,
        **kwargs,
    ):
        self.phone_number: str = phone_number
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.user_id: int = user_id
        self.vcard: str = vcard


class Location(JsonDeserializable, JsonSerializable, Dictionaryable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(
        self,
        longitude,
        latitude,
        horizontal_accuracy=None,
        live_period=None,
        heading=None,
        proximity_alert_radius=None,
        **kwargs,
    ):
        self.longitude: float = longitude
        self.latitude: float = latitude
        self.horizontal_accuracy: float = horizontal_accuracy
        self.live_period: int = live_period
        self.heading: int = heading
        self.proximity_alert_radius: int = proximity_alert_radius

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "longitude": self.longitude,
            "latitude": self.latitude,
            "horizontal_accuracy": self.horizontal_accuracy,
            "live_period": self.live_period,
            "heading": self.heading,
            "proximity_alert_radius": self.proximity_alert_radius,
        }


class Venue(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["location"] = Location.de_json(obj["location"])
        return cls(**obj)

    def __init__(
        self,
        location,
        title,
        address,
        foursquare_id=None,
        foursquare_type=None,
        google_place_id=None,
        google_place_type=None,
        **kwargs,
    ):
        self.location: Location = location
        self.title: str = title
        self.address: str = address
        self.foursquare_id: str = foursquare_id
        self.foursquare_type: str = foursquare_type
        self.google_place_id: str = google_place_id
        self.google_place_type: str = google_place_type


class UserProfilePhotos(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "photos" in obj:
            photos = [[PhotoSize.de_json(y) for y in x] for x in obj["photos"]]
            obj["photos"] = photos
        return cls(**obj)

    def __init__(self, total_count, photos=None, **kwargs):
        self.total_count: int = total_count
        self.photos: List[PhotoSize] = photos


class File(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, file_id, file_unique_id, file_size=None, file_path=None, **kwargs):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.file_size: int = file_size
        self.file_path: str = file_path


class ForceReply(JsonSerializable):
    def __init__(
        self,
        selective: Optional[bool] = None,
        input_field_placeholder: Optional[str] = None,
    ):
        self.selective = selective
        self.input_field_placeholder = input_field_placeholder

    def to_json(self):
        json_dict = {"force_reply": True}
        if self.selective is not None:
            json_dict["selective"] = self.selective
        if self.input_field_placeholder:
            json_dict["input_field_placeholder"] = self.input_field_placeholder
        return json.dumps(json_dict)


class ReplyKeyboardRemove(JsonSerializable):
    def __init__(self, selective=None):
        self.selective: bool = selective

    def to_json(self):
        json_dict = {"remove_keyboard": True}
        if self.selective:
            json_dict["selective"] = self.selective
        return json.dumps(json_dict)


class WebAppInfo(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(self, url, **kwargs):
        self.url: str = url

    def to_dict(self):
        return {"url": self.url}


class ReplyKeyboardMarkup(JsonSerializable, Dictionaryable):
    max_row_keys = 12

    def __init__(
        self,
        resize_keyboard: Optional[bool] = None,
        one_time_keyboard: Optional[bool] = None,
        selective: Optional[bool] = None,
        row_width: int = 3,
        input_field_placeholder: Optional[str] = None,
        is_persistent: Optional[bool] = None,
    ):
        if row_width > self.max_row_keys:
            # Todo: Will be replaced with Exception in future releases
            if not DISABLE_KEYLEN_ERROR:
                logger.error("Telegram does not support reply keyboard row width over %d." % self.max_row_keys)
            row_width = self.max_row_keys

        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective
        self.row_width = row_width
        self.input_field_placeholder = input_field_placeholder
        self.keyboard: list[list[KeyboardButton]] = []
        self.is_persistent = is_persistent

    def add(self, *args, row_width=None):
        """
        This function adds strings to the keyboard, while not exceeding row_width.
        E.g. ReplyKeyboardMarkup#add("A", "B", "C") yields the json result {keyboard: [["A"], ["B"], ["C"]]}
        when row_width is set to 1.
        When row_width is set to 2, the following is the result of this function: {keyboard: [["A", "B"], ["C"]]}
        See https://core.telegram.org/bots/api#replykeyboardmarkup

        :param args: KeyboardButton to append to the keyboard
        :param row_width: width of row
        :return: self, to allow function chaining.
        """
        if row_width is None:
            row_width = self.row_width

        if row_width > self.max_row_keys:
            # Todo: Will be replaced with Exception in future releases
            if not DISABLE_KEYLEN_ERROR:
                logger.error("Telegram does not support reply keyboard row width over %d." % self.max_row_keys)
            row_width = self.max_row_keys

        for row in util.chunks(args, row_width):
            button_array = []
            for button in row:
                if util.is_string(button):
                    button_array.append({"text": button})
                elif util.is_bytes(button):
                    button_array.append({"text": button.decode("utf-8")})
                else:
                    button_array.append(button.to_dict())
            self.keyboard.append(button_array)

        return self

    def row(self, *args):
        """
        Adds a list of KeyboardButton to the keyboard. This function does not consider row_width.
        ReplyKeyboardMarkup#row("A")#row("B", "C")#to_json() outputs '{keyboard: [["A"], ["B", "C"]]}'
        See https://core.telegram.org/bots/api#replykeyboardmarkup

        :param args: strings
        :return: self, to allow function chaining.
        """

        return self.add(*args, row_width=self.max_row_keys)

    def to_dict(self) -> dict:
        d: dict[str, Any] = {"keyboard": self.keyboard}
        if self.one_time_keyboard is not None:
            d["one_time_keyboard"] = self.one_time_keyboard
        if self.resize_keyboard is not None:
            d["resize_keyboard"] = self.resize_keyboard
        if self.selective is not None:
            d["selective"] = self.selective
        if self.input_field_placeholder:
            d["input_field_placeholder"] = self.input_field_placeholder
        if self.is_persistent is not None:
            d["is_persistent"] = self.is_persistent
        return d

    def to_json(self):
        """
        Converts this object to its json representation following the Telegram API guidelines described here:
        https://core.telegram.org/bots/api#replykeyboardmarkup
        :return:
        """
        return json.dumps(self.to_dict())


class KeyboardButtonPollType(Dictionaryable):
    def __init__(self, type=""):
        self.type: str = type

    def to_dict(self):
        return {"type": self.type}


class KeyboardButtonRequestUser(Dictionaryable):
    """
    This object defines the criteria used to request a suitable user.
    The identifier of the selected user will be shared with the bot when the corresponding button is pressed.
    Telegram documentation: https://core.telegram.org/bots/api#keyboardbuttonrequestuser
    :param request_id: Signed 32-bit identifier of the request, which will be received back in the UserShared object.
        Must be unique within the message
    :type request_id: :obj:`int`
    :param user_is_bot: Optional. Pass True to request a bot, pass False to request a regular user.
        If not specified, no additional restrictions are applied.
    :type user_is_bot: :obj:`bool`
    :param user_is_premium: Optional. Pass True to request a premium user, pass False to request a non-premium user.
        If not specified, no additional restrictions are applied.
    :type user_is_premium: :obj:`bool`
    :return: Instance of the class
    :rtype: :class:`telebot.types.KeyboardButtonRequestUser`
    """

    def __init__(
        self,
        request_id: int,
        user_is_bot: Optional[bool] = None,
        user_is_premium: Optional[bool] = None,
    ) -> None:
        self.request_id: int = request_id
        self.user_is_bot: Optional[bool] = user_is_bot
        self.user_is_premium: Optional[bool] = user_is_premium

    def to_dict(self) -> dict:
        data = {"request_id": self.request_id}
        if self.user_is_bot is not None:
            data["user_is_bot"] = self.user_is_bot
        if self.user_is_premium is not None:
            data["user_is_premium"] = self.user_is_premium
        return data


class KeyboardButtonRequestChat(Dictionaryable):
    """
    This object defines the criteria used to request a suitable chat. The identifier of the selected chat will
    be shared with the bot when the corresponding button is pressed.
    Telegram documentation: https://core.telegram.org/bots/api#keyboardbuttonrequestchat
    :param request_id: Signed 32-bit identifier of the request, which will be received back in the ChatShared object.
        Must be unique within the message
    :type request_id: :obj:`int`
    :param chat_is_channel: Pass True to request a channel chat, pass False to request a group or a supergroup chat.
    :type chat_is_channel: :obj:`bool`
    :param chat_is_forum: Optional. Pass True to request a forum supergroup, pass False to request a non-forum chat.
        If not specified, no additional restrictions are applied.
    :type chat_is_forum: :obj:`bool`
    :param chat_has_username: Optional. Pass True to request a supergroup or a channel with a username, pass False to request a
        chat without a username. If not specified, no additional restrictions are applied.
    :type chat_has_username: :obj:`bool`
    :param chat_is_created: Optional. Pass True to request a chat owned by the user. Otherwise, no additional restrictions are applied.
    :type chat_is_created: :obj:`bool`
    :param user_administrator_rights: Optional. A JSON-serialized object listing the required administrator rights of the user in the chat.
        The rights must be a superset of bot_administrator_rights. If not specified, no additional restrictions are applied.
    :type user_administrator_rights: :class:`telebot.types.ChatAdministratorRights`
    :param bot_administrator_rights: Optional. A JSON-serialized object listing the required administrator rights of the bot in the chat.
        The rights must be a subset of user_administrator_rights. If not specified, no additional restrictions are applied.
    :type bot_administrator_rights: :class:`telebot.types.ChatAdministratorRights`
    :param bot_is_member: Optional. Pass True to request a chat where the bot is a member. Otherwise, no additional restrictions are applied.
    :type bot_is_member: :obj:`bool`
    :return: Instance of the class
    :rtype: :class:`telebot.types.KeyboardButtonRequestChat`
    """

    def __init__(
        self,
        request_id: int,
        chat_is_channel: bool,
        chat_is_forum: Optional[bool] = None,
        chat_has_username: Optional[bool] = None,
        chat_is_created: Optional[bool] = None,
        user_administrator_rights: Optional["ChatAdministratorRights"] = None,
        bot_administrator_rights: Optional["ChatAdministratorRights"] = None,
        bot_is_member: Optional[bool] = None,
    ) -> None:
        self.request_id: int = request_id
        self.chat_is_channel: bool = chat_is_channel
        self.chat_is_forum: Optional[bool] = chat_is_forum
        self.chat_has_username: Optional[bool] = chat_has_username
        self.chat_is_created: Optional[bool] = chat_is_created
        self.user_administrator_rights: Optional[ChatAdministratorRights] = user_administrator_rights
        self.bot_administrator_rights: Optional[ChatAdministratorRights] = bot_administrator_rights
        self.bot_is_member: Optional[bool] = bot_is_member

    def to_dict(self) -> dict:
        data = {"request_id": self.request_id, "chat_is_channel": self.chat_is_channel}
        if self.chat_is_forum is not None:
            data["chat_is_forum"] = self.chat_is_forum
        if self.chat_has_username is not None:
            data["chat_has_username"] = self.chat_has_username
        if self.chat_is_created is not None:
            data["chat_is_created"] = self.chat_is_created
        if self.user_administrator_rights is not None:
            data["user_administrator_rights"] = self.user_administrator_rights.to_dict()
        if self.bot_administrator_rights is not None:
            data["bot_administrator_rights"] = self.bot_administrator_rights.to_dict()
        if self.bot_is_member is not None:
            data["bot_is_member"] = self.bot_is_member
        return data


class KeyboardButton(Dictionaryable, JsonSerializable):
    def __init__(
        self,
        text: str,
        request_contact: Optional[bool] = None,
        request_location: Optional[bool] = None,
        request_poll: Optional[KeyboardButtonPollType] = None,
        web_app: Optional[WebAppInfo] = None,
        request_user: Optional[KeyboardButtonRequestUser] = None,
        request_chat: Optional[KeyboardButtonRequestChat] = None,
    ):
        self.text = text
        self.request_contact = request_contact
        self.request_location = request_location
        self.request_poll = request_poll
        self.web_app = web_app
        self.request_user = request_user
        self.request_chat = request_chat

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = {"text": self.text}
        if self.request_contact is not None:
            json_dict["request_contact"] = self.request_contact
        if self.request_location is not None:
            json_dict["request_location"] = self.request_location
        if self.request_poll is not None:
            json_dict["request_poll"] = self.request_poll.to_dict()
        if self.web_app is not None:
            json_dict["web_app"] = self.web_app.to_dict()
        return json_dict


class InlineKeyboardMarkup(Dictionaryable, JsonSerializable, JsonDeserializable):
    max_row_keys = 8

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        keyboard = [[InlineKeyboardButton.de_json(button) for button in row] for row in obj["inline_keyboard"]]
        return cls(keyboard=keyboard)

    def __init__(self, keyboard=None, row_width=3):
        """
        This object represents an inline keyboard that appears
        right next to the message it belongs to.

        :return: None
        """
        if row_width > self.max_row_keys:
            # Todo: Will be replaced with Exception in future releases
            logger.error("Telegram does not support inline keyboard row width over %d." % self.max_row_keys)
            row_width = self.max_row_keys

        self.row_width: int = row_width
        self.keyboard: List[List[InlineKeyboardButton]] = keyboard or []

    def add(self, *args, row_width=None):
        """
        This method adds buttons to the keyboard without exceeding row_width.

        E.g. InlineKeyboardMarkup.add("A", "B", "C") yields the json result:
        {keyboard: [["A"], ["B"], ["C"]]}
        when row_width is set to 1.
        When row_width is set to 2, the result:
        {keyboard: [["A", "B"], ["C"]]}
        See https://core.telegram.org/bots/api#inlinekeyboardmarkup

        :param args: Array of InlineKeyboardButton to append to the keyboard
        :param row_width: width of row
        :return: self, to allow function chaining.
        """
        if row_width is None:
            row_width = self.row_width

        if row_width > self.max_row_keys:
            # Todo: Will be replaced with Exception in future releases
            logger.error("Telegram does not support inline keyboard row width over %d." % self.max_row_keys)
            row_width = self.max_row_keys

        for row in util.chunks(args, row_width):
            button_array = [button for button in row]
            self.keyboard.append(button_array)

        return self

    def row(self, *args):
        """
        Adds a list of InlineKeyboardButton to the keyboard.
        This method does not consider row_width.

        InlineKeyboardMarkup.row("A").row("B", "C").to_json() outputs:
        '{keyboard: [["A"], ["B", "C"]]}'
        See https://core.telegram.org/bots/api#inlinekeyboardmarkup

        :param args: Array of InlineKeyboardButton to append to the keyboard
        :return: self, to allow function chaining.
        """

        return self.add(*args, row_width=self.max_row_keys)

    def to_json(self):
        """
        Converts this object to its json representation
        following the Telegram API guidelines described here:
        https://core.telegram.org/bots/api#inlinekeyboardmarkup
        :return:
        """
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = dict()
        json_dict["inline_keyboard"] = [[button.to_dict() for button in row] for row in self.keyboard]
        return json_dict


ReplyMarkup = Union[
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    ForceReply,
]


class InlineKeyboardButton(Dictionaryable, JsonSerializable, JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "login_url" in obj:
            obj["login_url"] = LoginUrl.de_json(obj.get("login_url"))
        if "web_app" in obj:
            obj["web_app"] = WebAppInfo.de_json(obj.get("web_app"))

        return cls(**obj)

    def __init__(
        self,
        text,
        url=None,
        callback_data=None,
        web_app=None,
        switch_inline_query=None,
        switch_inline_query_current_chat=None,
        callback_game=None,
        pay=None,
        login_url=None,
        **kwargs,
    ):
        self.text: str = text
        self.url: str = url
        self.callback_data: str = callback_data
        self.web_app: WebAppInfo = web_app
        self.switch_inline_query: str = switch_inline_query
        self.switch_inline_query_current_chat: str = switch_inline_query_current_chat
        self.callback_game = callback_game  # Not Implemented
        self.pay: bool = pay
        self.login_url: LoginUrl = login_url

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = {"text": self.text}
        if self.url:
            json_dict["url"] = self.url
        if self.callback_data:
            json_dict["callback_data"] = self.callback_data
        if self.web_app:
            json_dict["web_app"] = self.web_app.to_dict()
        if self.switch_inline_query is not None:
            json_dict["switch_inline_query"] = self.switch_inline_query
        if self.switch_inline_query_current_chat is not None:
            json_dict["switch_inline_query_current_chat"] = self.switch_inline_query_current_chat
        if self.callback_game is not None:
            json_dict["callback_game"] = self.callback_game
        if self.pay is not None:
            json_dict["pay"] = self.pay
        if self.login_url is not None:
            json_dict["login_url"] = self.login_url.to_dict()
        return json_dict


class LoginUrl(Dictionaryable, JsonSerializable, JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(
        self,
        url,
        forward_text=None,
        bot_username=None,
        request_write_access=None,
        **kwargs,
    ):
        self.url: str = url
        self.forward_text: str = forward_text
        self.bot_username: str = bot_username
        self.request_write_access: bool = request_write_access

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = {"url": self.url}
        if self.forward_text:
            json_dict["forward_text"] = self.forward_text
        if self.bot_username:
            json_dict["bot_username"] = self.bot_username
        if self.request_write_access is not None:
            json_dict["request_write_access"] = self.request_write_access
        return json_dict


class CallbackQuery(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "data" not in obj:
            # "data" field is Optional in the API, but historically is mandatory in the class constructor
            obj["data"] = None
        obj["from_user"] = User.de_json(obj.pop("from"))
        if "message" in obj:
            obj["message"] = Message.de_json(obj.get("message"))
        obj["json_string"] = json_string
        return cls(**obj)

    def __init__(
        self,
        id,
        from_user,
        data,
        chat_instance,
        json_string,
        message=None,
        inline_message_id=None,
        game_short_name=None,
        **kwargs,
    ):
        self.id: int = id
        self.from_user: User = from_user
        self.message: Message = message
        self.inline_message_id: str = inline_message_id
        self.chat_instance: str = chat_instance
        self.data: str = data
        self.game_short_name: str = game_short_name
        self.json = json_string


class ChatPhoto(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(
        self,
        small_file_id,
        small_file_unique_id,
        big_file_id,
        big_file_unique_id,
        **kwargs,
    ):
        self.small_file_id: str = small_file_id
        self.small_file_unique_id: str = small_file_unique_id
        self.big_file_id: str = big_file_id
        self.big_file_unique_id: str = big_file_unique_id


class ChatMember(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["user"] = User.de_json(obj["user"])
        member_type = obj["status"]
        # Ordered according to estimated appearance frequency.
        if member_type == "member":
            return ChatMemberMember(**obj)
        elif member_type == "left":
            return ChatMemberLeft(**obj)
        elif member_type == "kicked":
            return ChatMemberBanned(**obj)
        elif member_type == "restricted":
            return ChatMemberRestricted(**obj)
        elif member_type == "administrator":
            return ChatMemberAdministrator(**obj)
        elif member_type == "creator":
            return ChatMemberOwner(**obj)
        else:
            # Should not be here. For "if something happen" compatibility
            return cls(**obj)

    def __init__(
        self,
        user,
        status,
        custom_title=None,
        is_anonymous=None,
        can_be_edited=None,
        can_post_messages=None,
        can_edit_messages=None,
        can_delete_messages=None,
        can_restrict_members=None,
        can_promote_members=None,
        can_change_info=None,
        can_invite_users=None,
        can_pin_messages=None,
        is_member=None,
        can_send_messages=None,
        can_send_audios=None,
        can_send_documents=None,
        can_send_photos=None,
        can_send_videos=None,
        can_send_video_notes=None,
        can_send_voice_notes=None,
        can_send_polls=None,
        can_send_other_messages=None,
        can_add_web_page_previews=None,
        can_manage_chat=None,
        can_manage_video_chats=None,
        until_date=None,
        can_manage_topics=None,
        **kwargs,
    ):
        self.user: User = user
        self.status: str = status
        self.custom_title: str = custom_title
        self.is_anonymous: bool = is_anonymous
        self.can_be_edited: bool = can_be_edited
        self.can_post_messages: bool = can_post_messages
        self.can_edit_messages: bool = can_edit_messages
        self.can_delete_messages: bool = can_delete_messages
        self.can_restrict_members: bool = can_restrict_members
        self.can_promote_members: bool = can_promote_members
        self.can_change_info: bool = can_change_info
        self.can_invite_users: bool = can_invite_users
        self.can_pin_messages: bool = can_pin_messages
        self.is_member: bool = is_member
        self.can_send_messages: bool = can_send_messages
        # self.can_send_media_messages: bool = can_send_media_messages
        self.can_send_polls: bool = can_send_polls
        self.can_send_other_messages: bool = can_send_other_messages
        self.can_add_web_page_previews: bool = can_add_web_page_previews
        self.can_manage_chat: bool = can_manage_chat
        self.can_manage_video_chats: bool = can_manage_video_chats
        self.can_manage_voice_chats: bool = self.can_manage_video_chats  # deprecated, for backward compatibility
        self.until_date: int = until_date
        self.can_manage_topics: bool = can_manage_topics
        self.can_send_audios: bool = can_send_audios
        self.can_send_documents: bool = can_send_documents
        self.can_send_photos: bool = can_send_photos
        self.can_send_videos: bool = can_send_videos
        self.can_send_video_notes: bool = can_send_video_notes
        self.can_send_voice_notes: bool = can_send_voice_notes


class ChatMemberOwner(ChatMember):
    pass


class ChatMemberAdministrator(ChatMember):
    pass


class ChatMemberMember(ChatMember):
    pass


class ChatMemberRestricted(ChatMember):
    pass


class ChatMemberLeft(ChatMember):
    pass


class ChatMemberBanned(ChatMember):
    pass


class ChatPermissions(JsonDeserializable, JsonSerializable, Dictionaryable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return json_string
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(
        self,
        can_send_messages=None,
        can_send_media_messages=None,
        can_send_audios=None,
        can_send_documents=None,
        can_send_photos=None,
        can_send_videos=None,
        can_send_video_notes=None,
        can_send_voice_notes=None,
        can_send_polls=None,
        can_send_other_messages=None,
        can_add_web_page_previews=None,
        can_change_info=None,
        can_invite_users=None,
        can_pin_messages=None,
        can_manage_topics=None,
        **kwargs,
    ):
        self.can_send_messages: bool = can_send_messages
        # self.can_send_media_messages: bool = can_send_media_messages
        self.can_send_polls: bool = can_send_polls
        self.can_send_other_messages: bool = can_send_other_messages
        self.can_add_web_page_previews: bool = can_add_web_page_previews
        self.can_change_info: bool = can_change_info
        self.can_invite_users: bool = can_invite_users
        self.can_pin_messages: bool = can_pin_messages
        self.can_manage_topics: bool = can_manage_topics
        self.can_send_audios: bool = can_send_audios
        self.can_send_documents: bool = can_send_documents
        self.can_send_photos: bool = can_send_photos
        self.can_send_videos: bool = can_send_videos
        self.can_send_video_notes: bool = can_send_video_notes
        self.can_send_voice_notes: bool = can_send_voice_notes

        if can_send_media_messages is not None:
            logger.warning(
                "can_send_media_messages is deprecated. Use individual parameters like can_send_audios, can_send_documents, etc."
            )
            self.can_send_audios = can_send_media_messages
            self.can_send_documents = can_send_media_messages
            self.can_send_photos = can_send_media_messages
            self.can_send_videos = can_send_media_messages
            self.can_send_video_notes = can_send_media_messages
            self.can_send_voice_notes = can_send_media_messages

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = dict()
        if self.can_send_messages is not None:
            json_dict["can_send_messages"] = self.can_send_messages
        if self.can_send_audios is not None:
            json_dict["can_send_audios"] = self.can_send_audios
        if self.can_send_documents is not None:
            json_dict["can_send_documents"] = self.can_send_documents
        if self.can_send_photos is not None:
            json_dict["can_send_photos"] = self.can_send_photos
        if self.can_send_videos is not None:
            json_dict["can_send_videos"] = self.can_send_videos
        if self.can_send_video_notes is not None:
            json_dict["can_send_video_notes"] = self.can_send_video_notes
        if self.can_send_voice_notes is not None:
            json_dict["can_send_voice_notes"] = self.can_send_voice_notes
        if self.can_send_polls is not None:
            json_dict["can_send_polls"] = self.can_send_polls
        if self.can_send_other_messages is not None:
            json_dict["can_send_other_messages"] = self.can_send_other_messages
        if self.can_add_web_page_previews is not None:
            json_dict["can_add_web_page_previews"] = self.can_add_web_page_previews
        if self.can_change_info is not None:
            json_dict["can_change_info"] = self.can_change_info
        if self.can_invite_users is not None:
            json_dict["can_invite_users"] = self.can_invite_users
        if self.can_pin_messages is not None:
            json_dict["can_pin_messages"] = self.can_pin_messages
        if self.can_manage_topics is not None:
            json_dict["can_manage_topics"] = self.can_manage_topics


class BotCommand(JsonSerializable, JsonDeserializable, Dictionaryable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, command, description):
        """
        This object represents a bot command.
        :param command: Text of the command, 1-32 characters.
            Can contain only lowercase English letters, digits and underscores.
        :param description: Description of the command, 3-256 characters.
        :return:
        """
        self.command: str = command
        self.description: str = description

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {"command": self.command, "description": self.description}


# BotCommandScopes


class BotCommandScope(ABC, JsonSerializable):
    def __init__(self, type="default", chat_id=None, user_id=None):
        """
        Abstract class.
        Use BotCommandScopeX classes to set a specific scope type:
        BotCommandScopeDefault
        BotCommandScopeAllPrivateChats
        BotCommandScopeAllGroupChats
        BotCommandScopeAllChatAdministrators
        BotCommandScopeChat
        BotCommandScopeChatAdministrators
        BotCommandScopeChatMember
        """
        self.type: str = type
        self.chat_id: Optional[Union[int, str]] = chat_id
        self.user_id: Optional[Union[int, str]] = user_id

    def to_json(self):
        json_dict = {"type": self.type}
        if self.chat_id:
            json_dict["chat_id"] = self.chat_id
        if self.user_id:
            json_dict["user_id"] = self.user_id
        return json.dumps(json_dict)


class BotCommandScopeDefault(BotCommandScope):
    def __init__(self):
        """
        Represents the default scope of bot commands.
        Default commands are used if no commands with a narrower scope are specified for the user.
        """
        super(BotCommandScopeDefault, self).__init__(type="default")


class BotCommandScopeAllPrivateChats(BotCommandScope):
    def __init__(self):
        """
        Represents the scope of bot commands, covering all private chats.
        """
        super(BotCommandScopeAllPrivateChats, self).__init__(type="all_private_chats")


class BotCommandScopeAllGroupChats(BotCommandScope):
    def __init__(self):
        """
        Represents the scope of bot commands, covering all group and supergroup chats.
        """
        super(BotCommandScopeAllGroupChats, self).__init__(type="all_group_chats")


class BotCommandScopeAllChatAdministrators(BotCommandScope):
    def __init__(self):
        """
        Represents the scope of bot commands, covering all group and supergroup chat administrators.
        """
        super(BotCommandScopeAllChatAdministrators, self).__init__(type="all_chat_administrators")


class BotCommandScopeChat(BotCommandScope):
    def __init__(self, chat_id=None):
        super(BotCommandScopeChat, self).__init__(type="chat", chat_id=chat_id)


class BotCommandScopeChatAdministrators(BotCommandScope):
    def __init__(self, chat_id=None):
        """
        Represents the scope of bot commands, covering a specific chat.
        @param chat_id: Unique identifier for the target chat
        """
        super(BotCommandScopeChatAdministrators, self).__init__(type="chat_administrators", chat_id=chat_id)


class BotCommandScopeChatMember(BotCommandScope):
    def __init__(self, chat_id=None, user_id=None):
        """
        Represents the scope of bot commands, covering all administrators of a specific group or supergroup chat
        @param chat_id: Unique identifier for the target chat
        @param user_id: Unique identifier of the target user
        """
        super(BotCommandScopeChatMember, self).__init__(type="chat_member", chat_id=chat_id, user_id=user_id)


# InlineQuery


class InlineQuery(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["from_user"] = User.de_json(obj.pop("from"))
        if "location" in obj:
            obj["location"] = Location.de_json(obj["location"])
        return cls(**obj)

    def __init__(self, id, from_user, query, offset, chat_type=None, location=None, **kwargs):
        """
        This object represents an incoming inline query.
        When the user sends an empty query, your bot could
        return some default or trending results.
        :param id: string Unique identifier for this query
        :param from_user: User Sender
        :param query: String Text of the query
        :param chat_type: String Type of the chat, from which the inline query was sent.
            Can be either “sender” for a private chat with the inline query sender,
            “private”, “group”, “supergroup”, or “channel”.
        :param offset: String Offset of the results to be returned, can be controlled by the bot
        :param location: Sender location, only for bots that request user location
        :return: InlineQuery Object
        """
        self.id: str = id
        self.from_user: User = from_user
        self.query: str = query
        self.offset: str = offset
        self.chat_type: str = chat_type
        self.location: Location = location


class InputTextMessageContent(Dictionaryable):
    def __init__(
        self,
        message_text,
        parse_mode=None,
        entities=None,
        disable_web_page_preview=None,
    ):
        self.message_text: str = message_text
        self.parse_mode: str = parse_mode
        self.entities: List[MessageEntity] = entities
        self.disable_web_page_preview: bool = disable_web_page_preview

    def to_dict(self):
        json_dict = {"message_text": self.message_text}
        if self.parse_mode:
            json_dict["parse_mode"] = self.parse_mode
        if self.entities:
            json_dict["entities"] = MessageEntity.to_list_of_dicts(self.entities)
        if self.disable_web_page_preview is not None:
            json_dict["disable_web_page_preview"] = self.disable_web_page_preview
        return json_dict


class InputLocationMessageContent(Dictionaryable):
    def __init__(
        self,
        latitude,
        longitude,
        horizontal_accuracy=None,
        live_period=None,
        heading=None,
        proximity_alert_radius=None,
    ):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.horizontal_accuracy: float = horizontal_accuracy
        self.live_period: int = live_period
        self.heading: int = heading
        self.proximity_alert_radius: int = proximity_alert_radius

    def to_dict(self):
        json_dict = {"latitude": self.latitude, "longitude": self.longitude}
        if self.horizontal_accuracy:
            json_dict["horizontal_accuracy"] = self.horizontal_accuracy
        if self.live_period:
            json_dict["live_period"] = self.live_period
        if self.heading:
            json_dict["heading"] = self.heading
        if self.proximity_alert_radius:
            json_dict["proximity_alert_radius"] = self.proximity_alert_radius
        return json_dict


class InputVenueMessageContent(Dictionaryable):
    def __init__(
        self,
        latitude,
        longitude,
        title,
        address,
        foursquare_id=None,
        foursquare_type=None,
        google_place_id=None,
        google_place_type=None,
    ):
        self.latitude: float = latitude
        self.longitude: float = longitude
        self.title: str = title
        self.address: str = address
        self.foursquare_id: str = foursquare_id
        self.foursquare_type: str = foursquare_type
        self.google_place_id: str = google_place_id
        self.google_place_type: str = google_place_type

    def to_dict(self):
        json_dict = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "title": self.title,
            "address": self.address,
        }
        if self.foursquare_id:
            json_dict["foursquare_id"] = self.foursquare_id
        if self.foursquare_type:
            json_dict["foursquare_type"] = self.foursquare_type
        if self.google_place_id:
            json_dict["google_place_id"] = self.google_place_id
        if self.google_place_type:
            json_dict["google_place_type"] = self.google_place_type
        return json_dict


class InputContactMessageContent(Dictionaryable):
    def __init__(self, phone_number, first_name, last_name=None, vcard=None):
        self.phone_number: str = phone_number
        self.first_name: str = first_name
        self.last_name: str = last_name
        self.vcard: str = vcard

    def to_dict(self):
        json_dict = {"phone_number": self.phone_number, "first_name": self.first_name}
        if self.last_name:
            json_dict["last_name"] = self.last_name
        if self.vcard:
            json_dict["vcard"] = self.vcard
        return json_dict


class InputInvoiceMessageContent(Dictionaryable):
    def __init__(
        self,
        title,
        description,
        payload,
        provider_token,
        currency,
        prices,
        max_tip_amount=None,
        suggested_tip_amounts=None,
        provider_data=None,
        photo_url=None,
        photo_size=None,
        photo_width=None,
        photo_height=None,
        need_name=None,
        need_phone_number=None,
        need_email=None,
        need_shipping_address=None,
        send_phone_number_to_provider=None,
        send_email_to_provider=None,
        is_flexible=None,
    ):
        self.title: str = title
        self.description: str = description
        self.payload: str = payload
        self.provider_token: str = provider_token
        self.currency: str = currency
        self.prices: List[LabeledPrice] = prices
        self.max_tip_amount: Optional[int] = max_tip_amount
        self.suggested_tip_amounts: Optional[List[int]] = suggested_tip_amounts
        self.provider_data: Optional[str] = provider_data
        self.photo_url: Optional[str] = photo_url
        self.photo_size: Optional[int] = photo_size
        self.photo_width: Optional[int] = photo_width
        self.photo_height: Optional[int] = photo_height
        self.need_name: Optional[bool] = need_name
        self.need_phone_number: Optional[bool] = need_phone_number
        self.need_email: Optional[bool] = need_email
        self.need_shipping_address: Optional[bool] = need_shipping_address
        self.send_phone_number_to_provider: Optional[bool] = send_phone_number_to_provider
        self.send_email_to_provider: Optional[bool] = send_email_to_provider
        self.is_flexible: Optional[bool] = is_flexible

    def to_dict(self):
        json_dict = {
            "title": self.title,
            "description": self.description,
            "payload": self.payload,
            "provider_token": self.provider_token,
            "currency": self.currency,
            "prices": [LabeledPrice.to_dict(lp) for lp in self.prices],
        }
        if self.max_tip_amount:
            json_dict["max_tip_amount"] = self.max_tip_amount
        if self.suggested_tip_amounts:
            json_dict["suggested_tip_amounts"] = self.suggested_tip_amounts
        if self.provider_data:
            json_dict["provider_data"] = self.provider_data
        if self.photo_url:
            json_dict["photo_url"] = self.photo_url
        if self.photo_size:
            json_dict["photo_size"] = self.photo_size
        if self.photo_width:
            json_dict["photo_width"] = self.photo_width
        if self.photo_height:
            json_dict["photo_height"] = self.photo_height
        if self.need_name is not None:
            json_dict["need_name"] = self.need_name
        if self.need_phone_number is not None:
            json_dict["need_phone_number"] = self.need_phone_number
        if self.need_email is not None:
            json_dict["need_email"] = self.need_email
        if self.need_shipping_address is not None:
            json_dict["need_shipping_address"] = self.need_shipping_address
        if self.send_phone_number_to_provider is not None:
            json_dict["send_phone_number_to_provider"] = self.send_phone_number_to_provider
        if self.send_email_to_provider is not None:
            json_dict["send_email_to_provider"] = self.send_email_to_provider
        if self.is_flexible is not None:
            json_dict["is_flexible"] = self.is_flexible
        return json_dict


class ChosenInlineResult(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["from_user"] = User.de_json(obj.pop("from"))
        if "location" in obj:
            obj["location"] = Location.de_json(obj["location"])
        return cls(**obj)

    def __init__(
        self,
        result_id,
        from_user,
        query,
        location=None,
        inline_message_id=None,
        **kwargs,
    ):
        """
        This object represents a result of an inline query
        that was chosen by the user and sent to their chat partner.
        :param result_id: string The unique identifier for the result that was chosen.
        :param from_user: User The user that chose the result.
        :param query: String The query that was used to obtain the result.
        :return: ChosenInlineResult Object.
        """
        self.result_id: str = result_id
        self.from_user: User = from_user
        self.location: Location = location
        self.inline_message_id: str = inline_message_id
        self.query: str = query


class InlineQueryResultBase(ABC, Dictionaryable, JsonSerializable):
    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        type,
        id,
        title=None,
        caption=None,
        input_message_content=None,
        reply_markup=None,
        caption_entities=None,
        parse_mode=None,
    ):
        self.type = type
        self.id = id
        self.title = title
        self.caption = caption
        self.input_message_content = input_message_content
        self.reply_markup = reply_markup
        self.caption_entities = caption_entities
        self.parse_mode = parse_mode

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = {"type": self.type, "id": self.id}
        if self.title:
            json_dict["title"] = self.title
        if self.caption:
            json_dict["caption"] = self.caption
        if self.input_message_content:
            json_dict["input_message_content"] = self.input_message_content.to_dict()
        if self.reply_markup:
            json_dict["reply_markup"] = self.reply_markup.to_dict()
        if self.caption_entities:
            json_dict["caption_entities"] = MessageEntity.to_list_of_dicts(self.caption_entities)
        if self.parse_mode:
            json_dict["parse_mode"] = self.parse_mode
        return json_dict


class SentWebAppMessage(JsonDeserializable, Dictionaryable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(self, inline_message_id=None):
        self.inline_message_id = inline_message_id

    def to_dict(self):
        json_dict = {}
        if self.inline_message_id:
            json_dict["inline_message_id"] = self.inline_message_id
        return json_dict


class InlineQueryResultArticle(InlineQueryResultBase):
    def __init__(
        self,
        id,
        title,
        input_message_content,
        reply_markup=None,
        url=None,
        hide_url=None,
        description=None,
        thumb_url=None,
        thumb_width=None,
        thumb_height=None,
    ):
        super().__init__(
            "article",
            id,
            title=title,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
        )
        self.url = url
        self.hide_url = hide_url
        self.description = description
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height

    def to_dict(self):
        json_dict = super().to_dict()
        if self.url:
            json_dict["url"] = self.url
        if self.hide_url:
            json_dict["hide_url"] = self.hide_url
        if self.description:
            json_dict["description"] = self.description
        if self.thumb_url:
            json_dict["thumb_url"] = self.thumb_url
        if self.thumb_width:
            json_dict["thumb_width"] = self.thumb_width
        if self.thumb_height:
            json_dict["thumb_height"] = self.thumb_height
        return json_dict


class InlineQueryResultPhoto(InlineQueryResultBase):
    def __init__(
        self,
        id,
        photo_url,
        thumb_url,
        photo_width=None,
        photo_height=None,
        title=None,
        description=None,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        """
        Represents a link to a photo.
        :param id: Unique identifier for this result, 1-64 bytes
        :param photo_url: A valid URL of the photo. Photo must be in jpeg format. Photo size must not exceed 5MB
        :param thumb_url: URL of the thumbnail for the photo
        :param photo_width: Width of the photo.
        :param photo_height: Height of the photo.
        :param title: Title for the result.
        :param description: Short description of the result.
        :param caption: Caption of the photo to be sent, 0-200 characters.
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or
        inline URLs in the media caption.
        :param reply_markup: InlineKeyboardMarkup : Inline keyboard attached to the message
        :param input_message_content: InputMessageContent : Content of the message to be sent instead of the photo
        :return:
        """
        super().__init__(
            "photo",
            id,
            title=title,
            caption=caption,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.photo_url = photo_url
        self.thumb_url = thumb_url
        self.photo_width = photo_width
        self.photo_height = photo_height
        self.description = description

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["photo_url"] = self.photo_url
        json_dict["thumb_url"] = self.thumb_url
        if self.photo_width:
            json_dict["photo_width"] = self.photo_width
        if self.photo_height:
            json_dict["photo_height"] = self.photo_height
        if self.description:
            json_dict["description"] = self.description
        return json_dict


class InlineQueryResultGif(InlineQueryResultBase):
    def __init__(
        self,
        id,
        gif_url,
        thumb_url,
        gif_width=None,
        gif_height=None,
        title=None,
        caption=None,
        caption_entities=None,
        reply_markup=None,
        input_message_content=None,
        gif_duration=None,
        parse_mode=None,
        thumb_mime_type=None,
    ):
        """
        Represents a link to an animated GIF file.
        :param id: Unique identifier for this result, 1-64 bytes.
        :param gif_url: A valid URL for the GIF file. File size must not exceed 1MB
        :param thumb_url: URL of the static thumbnail (jpeg or gif) for the result.
        :param gif_width: Width of the GIF.
        :param gif_height: Height of the GIF.
        :param title: Title for the result.
        :param caption:  Caption of the GIF file to be sent, 0-200 characters
        :param reply_markup: InlineKeyboardMarkup : Inline keyboard attached to the message
        :param input_message_content: InputMessageContent : Content of the message to be sent instead of the photo
        :return:
        """
        super().__init__(
            "gif",
            id,
            title=title,
            caption=caption,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.gif_url = gif_url
        self.gif_width = gif_width
        self.gif_height = gif_height
        self.thumb_url = thumb_url
        self.gif_duration = gif_duration
        self.thumb_mime_type = thumb_mime_type

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["gif_url"] = self.gif_url
        if self.gif_width:
            json_dict["gif_width"] = self.gif_width
        if self.gif_height:
            json_dict["gif_height"] = self.gif_height
        json_dict["thumb_url"] = self.thumb_url
        if self.gif_duration:
            json_dict["gif_duration"] = self.gif_duration
        if self.thumb_mime_type:
            json_dict["thumb_mime_type"] = self.thumb_mime_type
        return json_dict


class InlineQueryResultMpeg4Gif(InlineQueryResultBase):
    def __init__(
        self,
        id,
        mpeg4_url,
        thumb_url,
        mpeg4_width=None,
        mpeg4_height=None,
        title=None,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
        mpeg4_duration=None,
        thumb_mime_type=None,
    ):
        """
        Represents a link to a video animation (H.264/MPEG-4 AVC video without sound).
        :param id: Unique identifier for this result, 1-64 bytes
        :param mpeg4_url: A valid URL for the MP4 file. File size must not exceed 1MB
        :param thumb_url: URL of the static thumbnail (jpeg or gif) for the result
        :param mpeg4_width: Video width
        :param mpeg4_height: Video height
        :param title: Title for the result
        :param caption: Caption of the MPEG-4 file to be sent, 0-200 characters
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text
        or inline URLs in the media caption.
        :param reply_markup: InlineKeyboardMarkup : Inline keyboard attached to the message
        :param input_message_content: InputMessageContent : Content of the message to be sent instead of the photo
        :return:
        """
        super().__init__(
            "mpeg4_gif",
            id,
            title=title,
            caption=caption,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.mpeg4_url = mpeg4_url
        self.mpeg4_width = mpeg4_width
        self.mpeg4_height = mpeg4_height
        self.thumb_url = thumb_url
        self.mpeg4_duration = mpeg4_duration
        self.thumb_mime_type = thumb_mime_type

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["mpeg4_url"] = self.mpeg4_url
        if self.mpeg4_width:
            json_dict["mpeg4_width"] = self.mpeg4_width
        if self.mpeg4_height:
            json_dict["mpeg4_height"] = self.mpeg4_height
        json_dict["thumb_url"] = self.thumb_url
        if self.mpeg4_duration:
            json_dict["mpeg4_duration "] = self.mpeg4_duration
        if self.thumb_mime_type:
            json_dict["thumb_mime_type"] = self.thumb_mime_type
        return json_dict


class InlineQueryResultVideo(InlineQueryResultBase):
    def __init__(
        self,
        id,
        video_url,
        mime_type,
        thumb_url,
        title,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        video_width=None,
        video_height=None,
        video_duration=None,
        description=None,
        reply_markup=None,
        input_message_content=None,
    ):
        """
        Represents link to a page containing an embedded video player or a video file.
        :param id: Unique identifier for this result, 1-64 bytes
        :param video_url: A valid URL for the embedded video player or video file
        :param mime_type: Mime type of the content of video url, “text/html” or “video/mp4”
        :param thumb_url: URL of the thumbnail (jpeg only) for the video
        :param title: Title for the result
        :param parse_mode: Send Markdown or HTML, if you want Telegram apps to show bold, italic, fixed-width text or
        inline URLs in the media caption.
        :param video_width: Video width
        :param video_height: Video height
        :param video_duration: Video duration in seconds
        :param description: Short description of the result
        :return:
        """
        super().__init__(
            "video",
            id,
            title=title,
            caption=caption,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.video_url = video_url
        self.mime_type = mime_type
        self.thumb_url = thumb_url
        self.video_width = video_width
        self.video_height = video_height
        self.video_duration = video_duration
        self.description = description

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["video_url"] = self.video_url
        json_dict["mime_type"] = self.mime_type
        json_dict["thumb_url"] = self.thumb_url
        if self.video_height:
            json_dict["video_height"] = self.video_height
        if self.video_duration:
            json_dict["video_duration"] = self.video_duration
        if self.description:
            json_dict["description"] = self.description
        return json_dict


class InlineQueryResultAudio(InlineQueryResultBase):
    def __init__(
        self,
        id,
        audio_url,
        title,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        performer=None,
        audio_duration=None,
        reply_markup=None,
        input_message_content=None,
    ):
        super().__init__(
            "audio",
            id,
            title=title,
            caption=caption,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.audio_url = audio_url
        self.performer = performer
        self.audio_duration = audio_duration

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["audio_url"] = self.audio_url
        if self.performer:
            json_dict["performer"] = self.performer
        if self.audio_duration:
            json_dict["audio_duration"] = self.audio_duration
        return json_dict


class InlineQueryResultVoice(InlineQueryResultBase):
    def __init__(
        self,
        id,
        voice_url,
        title,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        voice_duration=None,
        reply_markup=None,
        input_message_content=None,
    ):
        super().__init__(
            "voice",
            id,
            title=title,
            caption=caption,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.voice_url = voice_url
        self.voice_duration = voice_duration

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["voice_url"] = self.voice_url
        if self.voice_duration:
            json_dict["voice_duration"] = self.voice_duration
        return json_dict


class InlineQueryResultDocument(InlineQueryResultBase):
    def __init__(
        self,
        id,
        title,
        document_url,
        mime_type,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        description=None,
        reply_markup=None,
        input_message_content=None,
        thumb_url=None,
        thumb_width=None,
        thumb_height=None,
    ):
        super().__init__(
            "document",
            id,
            title=title,
            caption=caption,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.document_url = document_url
        self.mime_type = mime_type
        self.description = description
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["document_url"] = self.document_url
        json_dict["mime_type"] = self.mime_type
        if self.description:
            json_dict["description"] = self.description
        if self.thumb_url:
            json_dict["thumb_url"] = self.thumb_url
        if self.thumb_width:
            json_dict["thumb_width"] = self.thumb_width
        if self.thumb_height:
            json_dict["thumb_height"] = self.thumb_height
        return json_dict


class InlineQueryResultLocation(InlineQueryResultBase):
    def __init__(
        self,
        id,
        title,
        latitude,
        longitude,
        horizontal_accuracy,
        live_period=None,
        reply_markup=None,
        input_message_content=None,
        thumb_url=None,
        thumb_width=None,
        thumb_height=None,
        heading=None,
        proximity_alert_radius=None,
    ):
        super().__init__(
            "location",
            id,
            title=title,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
        )
        self.latitude = latitude
        self.longitude = longitude
        self.horizontal_accuracy = horizontal_accuracy
        self.live_period = live_period
        self.heading: int = heading
        self.proximity_alert_radius: int = proximity_alert_radius
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["latitude"] = self.latitude
        json_dict["longitude"] = self.longitude
        if self.horizontal_accuracy:
            json_dict["horizontal_accuracy"] = self.horizontal_accuracy
        if self.live_period:
            json_dict["live_period"] = self.live_period
        if self.heading:
            json_dict["heading"] = self.heading
        if self.proximity_alert_radius:
            json_dict["proximity_alert_radius"] = self.proximity_alert_radius
        if self.thumb_url:
            json_dict["thumb_url"] = self.thumb_url
        if self.thumb_width:
            json_dict["thumb_width"] = self.thumb_width
        if self.thumb_height:
            json_dict["thumb_height"] = self.thumb_height
        return json_dict


class InlineQueryResultVenue(InlineQueryResultBase):
    def __init__(
        self,
        id,
        title,
        latitude,
        longitude,
        address,
        foursquare_id=None,
        foursquare_type=None,
        reply_markup=None,
        input_message_content=None,
        thumb_url=None,
        thumb_width=None,
        thumb_height=None,
        google_place_id=None,
        google_place_type=None,
    ):
        super().__init__(
            "venue",
            id,
            title=title,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
        )
        self.latitude = latitude
        self.longitude = longitude
        self.address = address
        self.foursquare_id = foursquare_id
        self.foursquare_type = foursquare_type
        self.google_place_id = google_place_id
        self.google_place_type = google_place_type
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["latitude"] = self.latitude
        json_dict["longitude"] = self.longitude
        json_dict["address"] = self.address
        if self.foursquare_id:
            json_dict["foursquare_id"] = self.foursquare_id
        if self.foursquare_type:
            json_dict["foursquare_type"] = self.foursquare_type
        if self.google_place_id:
            json_dict["google_place_id"] = self.google_place_id
        if self.google_place_type:
            json_dict["google_place_type"] = self.google_place_type
        if self.thumb_url:
            json_dict["thumb_url"] = self.thumb_url
        if self.thumb_width:
            json_dict["thumb_width"] = self.thumb_width
        if self.thumb_height:
            json_dict["thumb_height"] = self.thumb_height
        return json_dict


class InlineQueryResultContact(InlineQueryResultBase):
    def __init__(
        self,
        id,
        phone_number,
        first_name,
        last_name=None,
        vcard=None,
        reply_markup=None,
        input_message_content=None,
        thumb_url=None,
        thumb_width=None,
        thumb_height=None,
    ):
        super().__init__(
            "contact",
            id,
            input_message_content=input_message_content,
            reply_markup=reply_markup,
        )
        self.phone_number = phone_number
        self.first_name = first_name
        self.last_name = last_name
        self.vcard = vcard
        self.thumb_url = thumb_url
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["phone_number"] = self.phone_number
        json_dict["first_name"] = self.first_name
        if self.last_name:
            json_dict["last_name"] = self.last_name
        if self.vcard:
            json_dict["vcard"] = self.vcard
        if self.thumb_url:
            json_dict["thumb_url"] = self.thumb_url
        if self.thumb_width:
            json_dict["thumb_width"] = self.thumb_width
        if self.thumb_height:
            json_dict["thumb_height"] = self.thumb_height
        return json_dict


class InlineQueryResultGame(InlineQueryResultBase):
    def __init__(self, id, game_short_name, reply_markup=None):
        super().__init__("game", id, reply_markup=reply_markup)
        self.game_short_name = game_short_name

    def to_dict(self):
        json_dict = super().to_dict()
        json_dict["game_short_name"] = self.game_short_name
        return json_dict


class InlineQueryResultCachedBase(ABC, JsonSerializable):
    def __init__(self):
        self.type = None
        self.id = None
        self.title = None
        self.description = None
        self.caption = None
        self.reply_markup = None
        self.input_message_content = None
        self.parse_mode = None
        self.caption_entities = None
        self.payload_dic = {}

    def to_json(self):
        json_dict = self.payload_dic
        json_dict["type"] = self.type
        json_dict["id"] = self.id
        if self.title:
            json_dict["title"] = self.title
        if self.description:
            json_dict["description"] = self.description
        if self.caption:
            json_dict["caption"] = self.caption
        if self.reply_markup:
            json_dict["reply_markup"] = self.reply_markup.to_dict()
        if self.input_message_content:
            json_dict["input_message_content"] = self.input_message_content.to_dict()
        if self.parse_mode:
            json_dict["parse_mode"] = self.parse_mode
        if self.caption_entities:
            json_dict["caption_entities"] = MessageEntity.to_list_of_dicts(self.caption_entities)
        return json.dumps(json_dict)


class InlineQueryResultCachedPhoto(InlineQueryResultCachedBase):
    def __init__(
        self,
        id,
        photo_file_id,
        title=None,
        description=None,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "photo"
        self.id = id
        self.photo_file_id = photo_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.parse_mode = parse_mode
        self.payload_dic["photo_file_id"] = photo_file_id


class InlineQueryResultCachedGif(InlineQueryResultCachedBase):
    def __init__(
        self,
        id,
        gif_file_id,
        title=None,
        description=None,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "gif"
        self.id = id
        self.gif_file_id = gif_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.parse_mode = parse_mode
        self.payload_dic["gif_file_id"] = gif_file_id


class InlineQueryResultCachedMpeg4Gif(InlineQueryResultCachedBase):
    def __init__(
        self,
        id,
        mpeg4_file_id,
        title=None,
        description=None,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "mpeg4_gif"
        self.id = id
        self.mpeg4_file_id = mpeg4_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.parse_mode = parse_mode
        self.payload_dic["mpeg4_file_id"] = mpeg4_file_id


class InlineQueryResultCachedSticker(InlineQueryResultCachedBase):
    def __init__(self, id, sticker_file_id, reply_markup=None, input_message_content=None):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "sticker"
        self.id = id
        self.sticker_file_id = sticker_file_id
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.payload_dic["sticker_file_id"] = sticker_file_id


class InlineQueryResultCachedDocument(InlineQueryResultCachedBase):
    def __init__(
        self,
        id,
        document_file_id,
        title,
        description=None,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "document"
        self.id = id
        self.document_file_id = document_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.parse_mode = parse_mode
        self.payload_dic["document_file_id"] = document_file_id


class InlineQueryResultCachedVideo(InlineQueryResultCachedBase):
    def __init__(
        self,
        id,
        video_file_id,
        title,
        description=None,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "video"
        self.id = id
        self.video_file_id = video_file_id
        self.title = title
        self.description = description
        self.caption = caption
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.parse_mode = parse_mode
        self.payload_dic["video_file_id"] = video_file_id


class InlineQueryResultCachedVoice(InlineQueryResultCachedBase):
    def __init__(
        self,
        id,
        voice_file_id,
        title,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "voice"
        self.id = id
        self.voice_file_id = voice_file_id
        self.title = title
        self.caption = caption
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.parse_mode = parse_mode
        self.payload_dic["voice_file_id"] = voice_file_id


class InlineQueryResultCachedAudio(InlineQueryResultCachedBase):
    def __init__(
        self,
        id,
        audio_file_id,
        caption=None,
        caption_entities=None,
        parse_mode=None,
        reply_markup=None,
        input_message_content=None,
    ):
        InlineQueryResultCachedBase.__init__(self)
        self.type = "audio"
        self.id = id
        self.audio_file_id = audio_file_id
        self.caption = caption
        self.caption_entities = caption_entities
        self.reply_markup = reply_markup
        self.input_message_content = input_message_content
        self.parse_mode = parse_mode
        self.payload_dic["audio_file_id"] = audio_file_id


# Games


class Game(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["photo"] = Game.parse_photo(obj["photo"])
        if "text_entities" in obj:
            obj["text_entities"] = Game.parse_entities(obj["text_entities"])
        if "animation" in obj:
            obj["animation"] = Animation.de_json(obj["animation"])
        return cls(**obj)

    @classmethod
    def parse_photo(cls, photo_size_array):
        ret = []
        for ps in photo_size_array:
            ret.append(PhotoSize.de_json(ps))
        return ret

    @classmethod
    def parse_entities(cls, message_entity_array):
        ret = []
        for me in message_entity_array:
            ret.append(MessageEntity.de_json(me))
        return ret

    def __init__(
        self,
        title,
        description,
        photo,
        text=None,
        text_entities=None,
        animation=None,
        **kwargs,
    ):
        self.title: str = title
        self.description: str = description
        self.photo: List[PhotoSize] = photo
        self.text: str = text
        self.text_entities: List[MessageEntity] = text_entities
        self.animation: Animation = animation


class Animation(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "thumb" in obj and "file_id" in obj["thumb"]:
            obj["thumb"] = PhotoSize.de_json(obj["thumb"])
        else:
            obj["thumb"] = None
        return cls(**obj)

    def __init__(
        self,
        file_id,
        file_unique_id,
        width=None,
        height=None,
        duration=None,
        thumb=None,
        file_name=None,
        mime_type=None,
        file_size=None,
        **kwargs,
    ):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.width: int = width
        self.height: int = height
        self.duration: int = duration
        self.thumb: PhotoSize = thumb
        self.file_name: str = file_name
        self.mime_type: str = mime_type
        self.file_size: int = file_size


class GameHighScore(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["user"] = User.de_json(obj["user"])
        return cls(**obj)

    def __init__(self, position, user, score, **kwargs):
        self.position: int = position
        self.user: User = user
        self.score: int = score


# Payments


class LabeledPrice(JsonSerializable, Dictionaryable):
    def __init__(self, label, amount):
        self.label: str = label
        self.amount: int = amount

    def to_dict(self):
        return {"label": self.label, "amount": self.amount}

    def to_json(self):
        return json.dumps(self.to_dict())


class Invoice(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, title, description, start_parameter, currency, total_amount, **kwargs):
        self.title: str = title
        self.description: str = description
        self.start_parameter: str = start_parameter
        self.currency: str = currency
        self.total_amount: int = total_amount


class ShippingAddress(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, country_code, state, city, street_line1, street_line2, post_code, **kwargs):
        self.country_code: str = country_code
        self.state: str = state
        self.city: str = city
        self.street_line1: str = street_line1
        self.street_line2: str = street_line2
        self.post_code: str = post_code


class OrderInfo(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["shipping_address"] = ShippingAddress.de_json(obj.get("shipping_address"))
        return cls(**obj)

    def __init__(self, name=None, phone_number=None, email=None, shipping_address=None, **kwargs):
        self.name: str = name
        self.phone_number: str = phone_number
        self.email: str = email
        self.shipping_address: ShippingAddress = shipping_address


class ShippingOption(JsonSerializable):
    def __init__(self, id, title):
        self.id: str = id
        self.title: str = title
        self.prices: List[LabeledPrice] = []

    def add_price(self, *args):
        """
        Add LabeledPrice to ShippingOption

        :param args: LabeledPrices
        """
        for price in args:
            self.prices.append(price)
        return self

    def to_json(self):
        price_list = []
        for p in self.prices:
            price_list.append(p.to_dict())
        json_dict = json.dumps({"id": self.id, "title": self.title, "prices": price_list})
        return json_dict


class SuccessfulPayment(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["order_info"] = OrderInfo.de_json(obj.get("order_info"))
        return cls(**obj)

    def __init__(
        self,
        currency,
        total_amount,
        invoice_payload,
        shipping_option_id=None,
        order_info=None,
        telegram_payment_charge_id=None,
        provider_payment_charge_id=None,
        **kwargs,
    ):
        self.currency: str = currency
        self.total_amount: int = total_amount
        self.invoice_payload: str = invoice_payload
        self.shipping_option_id: str = shipping_option_id
        self.order_info: OrderInfo = order_info
        self.telegram_payment_charge_id: str = telegram_payment_charge_id
        self.provider_payment_charge_id: str = provider_payment_charge_id


class ShippingQuery(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["from_user"] = User.de_json(obj.pop("from"))
        obj["shipping_address"] = ShippingAddress.de_json(obj["shipping_address"])
        return cls(**obj)

    def __init__(self, id, from_user, invoice_payload, shipping_address, **kwargs):
        self.id: str = id
        self.from_user: User = from_user
        self.invoice_payload: str = invoice_payload
        self.shipping_address: ShippingAddress = shipping_address


class PreCheckoutQuery(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["from_user"] = User.de_json(obj.pop("from"))
        obj["order_info"] = OrderInfo.de_json(obj.get("order_info"))
        return cls(**obj)

    def __init__(
        self,
        id,
        from_user,
        currency,
        total_amount,
        invoice_payload,
        shipping_option_id=None,
        order_info=None,
        **kwargs,
    ):
        self.id: str = id
        self.from_user: User = from_user
        self.currency: str = currency
        self.total_amount: int = total_amount
        self.invoice_payload: str = invoice_payload
        self.shipping_option_id: str = shipping_option_id
        self.order_info: OrderInfo = order_info


# Stickers


class StickerSet(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        stickers = []
        for s in obj["stickers"]:
            stickers.append(Sticker.de_json(s))
        obj["stickers"] = stickers
        if "thumb" in obj and "file_id" in obj["thumb"]:
            obj["thumb"] = PhotoSize.de_json(obj["thumb"])
        else:
            obj["thumb"] = None
        return cls(**obj)

    def __init__(
        self,
        name,
        title,
        sticker_type,
        is_animated,
        is_video,
        stickers,
        thumb=None,
        **kwargs,
    ):
        self.name: str = name
        self.title: str = title
        self.sticker_type: str = sticker_type
        self.is_animated: bool = is_animated
        self.is_video: bool = is_video
        self.stickers: List[Sticker] = stickers
        self.thumb: PhotoSize = thumb

    @property
    def contains_masks(self):
        """
        Deprecated since Bot API 6.2, use sticker_type instead.
        """
        logger.warning("contains_masks is deprecated, use sticker_type instead")
        return self.sticker_type == "mask"


class Sticker(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "thumb" in obj and "file_id" in obj["thumb"]:
            obj["thumb"] = PhotoSize.de_json(obj["thumb"])
        else:
            obj["thumb"] = None
        if "mask_position" in obj:
            obj["mask_position"] = MaskPosition.de_json(obj["mask_position"])
        if "premium_animation" in obj:
            obj["premium_animation"] = File.de_json(obj["premium_animation"])
        return cls(**obj)

    def __init__(
        self,
        file_id,
        file_unique_id,
        type,
        width,
        height,
        is_animated,
        is_video,
        thumb=None,
        emoji=None,
        set_name=None,
        mask_position=None,
        file_size=None,
        premium_animation=None,
        custom_emoji_id=None,
        **kwargs,
    ):
        self.file_id: str = file_id
        self.file_unique_id: str = file_unique_id
        self.type: str = type
        self.width: int = width
        self.height: int = height
        self.is_animated: bool = is_animated
        self.is_video: bool = is_video
        self.thumb: PhotoSize = thumb
        self.emoji: str = emoji
        self.set_name: str = set_name
        self.mask_position: MaskPosition = mask_position
        self.file_size: int = file_size
        self.premium_animation: File = premium_animation
        self.custom_emoji_id: str = custom_emoji_id


class MaskPosition(Dictionaryable, JsonDeserializable, JsonSerializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, point, x_shift, y_shift, scale, **kwargs):
        self.point: str = point
        self.x_shift: float = x_shift
        self.y_shift: float = y_shift
        self.scale: float = scale

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "point": self.point,
            "x_shift": self.x_shift,
            "y_shift": self.y_shift,
            "scale": self.scale,
        }


# InputMedia


class InputMedia(Dictionaryable, JsonSerializable):
    def __init__(self, type, media, caption=None, parse_mode=None, caption_entities=None):
        self.type: str = type
        self.media: str = media
        self.caption: Optional[str] = caption
        self.parse_mode: Optional[str] = parse_mode
        self.caption_entities: Optional[List[MessageEntity]] = caption_entities

        if util.is_string(self.media):
            self._media_name = ""
            self._media_dic = self.media
        else:
            self._media_name = util.generate_random_token()
            self._media_dic = "attach://{0}".format(self._media_name)

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = {"type": self.type, "media": self._media_dic}
        if self.caption:
            json_dict["caption"] = self.caption
        if self.parse_mode:
            json_dict["parse_mode"] = self.parse_mode
        if self.caption_entities:
            json_dict["caption_entities"] = MessageEntity.to_list_of_dicts(self.caption_entities)
        return json_dict

    def convert_input_media(self):
        if util.is_string(self.media):
            return self.to_json(), None

        return self.to_json(), {self._media_name: self.media}


class InputMediaPhoto(InputMedia):
    def __init__(
        self,
        media: BytesIO,
        caption=None,
        parse_mode=None,
        has_spoiler: Optional[bool] = None,
    ):
        super(InputMediaPhoto, self).__init__(type="photo", media=media, caption=caption, parse_mode=parse_mode)
        self.has_spoiler = has_spoiler

    def to_dict(self):
        d = super(InputMediaPhoto, self).to_dict()
        if self.has_spoiler is not None:
            d["has_spoiler"] = self.has_spoiler
        return d


class InputMediaVideo(InputMedia):
    def __init__(
        self,
        media,
        thumb=None,
        caption=None,
        parse_mode=None,
        caption_entities=None,
        width=None,
        height=None,
        duration=None,
        supports_streaming=None,
        has_spoiler=None,
    ):
        super(InputMediaVideo, self).__init__(
            type="video",
            media=media,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.thumb = thumb
        self.width = width
        self.height = height
        self.duration = duration
        self.supports_streaming = supports_streaming
        self.has_spoiler: Optional[bool] = has_spoiler

    def to_dict(self):
        ret = super(InputMediaVideo, self).to_dict()
        if self.thumb:
            ret["thumb"] = self.thumb
        if self.width:
            ret["width"] = self.width
        if self.height:
            ret["height"] = self.height
        if self.duration:
            ret["duration"] = self.duration
        if self.supports_streaming:
            ret["supports_streaming"] = self.supports_streaming
        if self.has_spoiler is not None:
            ret["has_spoiler"] = self.has_spoiler
        return ret


class InputMediaAnimation(InputMedia):
    def __init__(
        self,
        media,
        thumb=None,
        caption=None,
        parse_mode=None,
        caption_entities=None,
        width=None,
        height=None,
        duration=None,
        has_spoiler=None,
    ):
        super(InputMediaAnimation, self).__init__(
            type="animation",
            media=media,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.thumb = thumb
        self.width = width
        self.height = height
        self.duration = duration
        self.has_spoiler: Optional[bool] = has_spoiler

    def to_dict(self):
        ret = super(InputMediaAnimation, self).to_dict()
        if self.thumb:
            ret["thumb"] = self.thumb
        if self.width:
            ret["width"] = self.width
        if self.height:
            ret["height"] = self.height
        if self.duration:
            ret["duration"] = self.duration
        if self.has_spoiler is not None:
            ret["has_spoiler"] = self.has_spoiler
        return ret


class InputMediaAudio(InputMedia):
    def __init__(
        self,
        media,
        thumb=None,
        caption=None,
        parse_mode=None,
        caption_entities=None,
        duration=None,
        performer=None,
        title=None,
    ):
        super(InputMediaAudio, self).__init__(
            type="audio",
            media=media,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.thumb = thumb
        self.duration = duration
        self.performer = performer
        self.title = title

    def to_dict(self):
        ret = super(InputMediaAudio, self).to_dict()
        if self.thumb:
            ret["thumb"] = self.thumb
        if self.duration:
            ret["duration"] = self.duration
        if self.performer:
            ret["performer"] = self.performer
        if self.title:
            ret["title"] = self.title
        return ret


class InputMediaDocument(InputMedia):
    def __init__(
        self,
        media,
        thumb=None,
        caption=None,
        parse_mode=None,
        caption_entities=None,
        disable_content_type_detection=None,
    ):
        super(InputMediaDocument, self).__init__(
            type="document",
            media=media,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
        )
        self.thumb = thumb
        self.disable_content_type_detection = disable_content_type_detection

    def to_dict(self):
        ret = super(InputMediaDocument, self).to_dict()
        if self.thumb:
            ret["thumb"] = self.thumb
        if self.disable_content_type_detection is not None:
            ret["disable_content_type_detection"] = self.disable_content_type_detection
        return ret


class PollOption(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, text, voter_count=0, **kwargs):
        self.text: str = text
        self.voter_count: int = voter_count

    # Converted in _convert_poll_options
    # def to_json(self):
    #     # send_poll Option is a simple string: https://core.telegram.org/bots/api#sendpoll
    #     return json.dumps(self.text)


class Poll(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["poll_id"] = obj.pop("id")
        options = []
        for opt in obj["options"]:
            options.append(PollOption.de_json(opt))
        obj["options"] = options or None
        if "explanation_entities" in obj:
            obj["explanation_entities"] = Message.parse_entities(obj["explanation_entities"])
        return cls(**obj)

    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        question,
        options,
        poll_id=None,
        total_voter_count=None,
        is_closed=None,
        is_anonymous=None,
        type=None,
        allows_multiple_answers=None,
        correct_option_id=None,
        explanation=None,
        explanation_entities=None,
        open_period=None,
        close_date=None,
        poll_type=None,
        **kwargs,
    ):
        self.id: str = poll_id
        self.question: str = question
        self.options: List[PollOption] = options
        self.total_voter_count: int = total_voter_count
        self.is_closed: bool = is_closed
        self.is_anonymous: bool = is_anonymous
        self.type: str = type
        if poll_type is not None:
            # Wrong param name backward compatibility
            logger.warning("Poll: poll_type parameter is deprecated. Use type instead.")
            if type is None:
                self.type: str = poll_type
        self.allows_multiple_answers: bool = allows_multiple_answers
        self.correct_option_id: int = correct_option_id
        self.explanation: str = explanation
        self.explanation_entities: List[MessageEntity] = explanation_entities
        self.open_period: int = open_period
        self.close_date: int = close_date

    def add(self, option):
        if type(option) is PollOption:
            self.options.append(option)
        else:
            self.options.append(PollOption(option))


class PollAnswer(JsonSerializable, JsonDeserializable, Dictionaryable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["user"] = User.de_json(obj["user"])
        return cls(**obj)

    def __init__(self, poll_id, user, option_ids, **kwargs):
        self.poll_id: str = poll_id
        self.user: User = user
        self.option_ids: List[int] = option_ids

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {
            "poll_id": self.poll_id,
            "user": self.user.to_dict(),
            "option_ids": self.option_ids,
        }


class ChatLocation(JsonSerializable, JsonDeserializable, Dictionaryable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return json_string
        obj = cls.ensure_json_dict(json_string)
        obj["location"] = Location.de_json(obj["location"])
        return cls(**obj)

    def __init__(self, location, address, **kwargs):
        self.location: Location = location
        self.address: str = address

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        return {"location": self.location.to_dict(), "address": self.address}


class ChatInviteLink(JsonSerializable, JsonDeserializable, Dictionaryable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        obj["creator"] = User.de_json(obj["creator"])
        return cls(**obj)

    def __init__(
        self,
        invite_link: str,
        creator: User,
        creates_join_request: bool,
        is_primary: bool,
        is_revoked: bool,
        name: Optional[str] = None,
        expire_date: Optional[int] = None,
        member_limit: Optional[int] = None,
        pending_join_request_count: Optional[int] = None,
        **kwargs,
    ):
        self.invite_link = invite_link
        self.creator = creator
        self.creates_join_request = creates_join_request
        self.is_primary = is_primary
        self.is_revoked = is_revoked
        self.name = name
        self.expire_date = expire_date
        self.member_limit = member_limit
        self.pending_join_request_count = pending_join_request_count

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        json_dict = {
            "invite_link": self.invite_link,
            "creator": self.creator.to_dict(),
            "is_primary": self.is_primary,
            "is_revoked": self.is_revoked,
            "creates_join_request": self.creates_join_request,
        }
        if self.expire_date:
            json_dict["expire_date"] = self.expire_date
        if self.member_limit:
            json_dict["member_limit"] = self.member_limit
        if self.pending_join_request_count:
            json_dict["pending_join_request_count"] = self.pending_join_request_count
        if self.name:
            json_dict["name"] = self.name
        return json_dict


class ProximityAlertTriggered(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, traveler, watcher, distance, **kwargs):
        self.traveler: User = traveler
        self.watcher: User = watcher
        self.distance: int = distance


class VideoChatStarted(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        return cls()

    def __init__(self):
        """
        This object represents a service message about a voice chat started in the chat.
        Currently holds no information.
        """
        pass


class VoiceChatStarted(VideoChatStarted):
    def __init__(self):
        logger.warning("VoiceChatStarted is deprecated. Use VideoChatStarted instead.")
        super().__init__()


class VideoChatScheduled(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, start_date, **kwargs):
        self.start_date: int = start_date


class VoiceChatScheduled(VideoChatScheduled):
    def __init__(self, *args, **kwargs):
        logger.warning("VoiceChatScheduled is deprecated. Use VideoChatScheduled instead.")
        super().__init__(*args, **kwargs)


class VideoChatEnded(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, duration, **kwargs):
        self.duration: int = duration


class VoiceChatEnded(VideoChatEnded):
    def __init__(self, *args, **kwargs):
        logger.warning("VoiceChatEnded is deprecated. Use VideoChatEnded instead.")
        super().__init__(*args, **kwargs)


class VideoChatParticipantsInvited(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        if "users" in obj:
            obj["users"] = [User.de_json(u) for u in obj["users"]]
        return cls(**obj)

    def __init__(self, users=None, **kwargs):
        self.users: List[User] = users


class VoiceChatParticipantsInvited(VideoChatParticipantsInvited):
    def __init__(self, *args, **kwargs):
        logger.warning("VoiceChatParticipantsInvited is deprecated. Use VideoChatParticipantsInvited instead.")
        super().__init__(*args, **kwargs)


class MessageAutoDeleteTimerChanged(JsonDeserializable):
    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string, copy_dict=False)
        return cls(**obj)

    def __init__(self, message_auto_delete_time, **kwargs):
        self.message_auto_delete_time = message_auto_delete_time


class MenuButton(JsonDeserializable, JsonSerializable, Dictionaryable):
    """
    Base class for MenuButtons.
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        map = {
            "commands": MenuButtonCommands,
            "web_app": MenuButtonWebApp,
            "default": MenuButtonDefault,
        }
        return map[obj["type"]](**obj)

    def to_json(self):
        raise NotImplementedError


class MenuButtonCommands(MenuButton):
    def __init__(self, type):
        self.type = type

    def to_dict(self):
        return {"type": self.type}

    def to_json(self):
        return json.dumps(self.to_dict())


class MenuButtonWebApp(MenuButton):
    def __init__(self, type, text, web_app):
        self.type: str = type
        self.text: str = text
        self.web_app: WebAppInfo = web_app

    def to_dict(self):
        return {"type": self.type, "text": self.text, "web_app": self.web_app.to_dict()}

    def to_json(self):
        return json.dumps(self.to_dict())


class MenuButtonDefault(MenuButton):
    def __init__(self, type):
        self.type: str = type

    def to_dict(self):
        return {"type": self.type}

    def to_json(self):
        return json.dumps(self.to_dict())


class ChatAdministratorRights(JsonDeserializable, JsonSerializable, Dictionaryable):
    """
    Class representation of:
    https://core.telegram.org/bots/api#chatadministratorrights
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(
        self,
        is_anonymous: bool,
        can_manage_chat: bool,
        can_delete_messages: bool,
        can_manage_video_chats: bool,
        can_restrict_members: bool,
        can_promote_members: bool,
        can_change_info: bool,
        can_invite_users: bool,
        can_post_messages: Optional[bool] = None,
        can_edit_messages: Optional[bool] = None,
        can_pin_messages: Optional[bool] = None,
        can_manage_topics: Optional[bool] = None,
    ) -> None:
        self.is_anonymous = is_anonymous
        self.can_manage_chat = can_manage_chat
        self.can_delete_messages = can_delete_messages
        self.can_manage_video_chats = can_manage_video_chats
        self.can_restrict_members = can_restrict_members
        self.can_promote_members = can_promote_members
        self.can_change_info = can_change_info
        self.can_invite_users = can_invite_users
        self.can_post_messages = can_post_messages
        self.can_edit_messages = can_edit_messages
        self.can_pin_messages = can_pin_messages
        self.can_manage_topics = can_manage_topics

    def to_dict(self):
        json_dict = {
            "is_anonymous": self.is_anonymous,
            "can_manage_chat": self.can_manage_chat,
            "can_delete_messages": self.can_delete_messages,
            "can_manage_video_chats": self.can_manage_video_chats,
            "can_restrict_members": self.can_restrict_members,
            "can_promote_members": self.can_promote_members,
            "can_change_info": self.can_change_info,
            "can_invite_users": self.can_invite_users,
        }
        if self.can_post_messages is not None:
            json_dict["can_post_messages"] = self.can_post_messages
        if self.can_edit_messages is not None:
            json_dict["can_edit_messages"] = self.can_edit_messages
        if self.can_pin_messages is not None:
            json_dict["can_pin_messages"] = self.can_pin_messages
        if self.can_manage_topics is not None:
            json_dict["can_manage_topics"] = self.can_manage_topics
        return json_dict

    def to_json(self):
        return json.dumps(self.to_dict())


class InputFile:
    """
    A class to send files through Telegram Bot API.
    You need to pass a file, which should be an instance of :class:`io.IOBase` or
    :class:`pathlib.Path`, or :obj:`str`.
    If you pass an :obj:`str` as a file, it will be opened and closed by the class.
    :param file: A file to send.
    :type file: :class:`io.IOBase` or :class:`pathlib.Path` or :obj:`str`
    .. code-block:: python3
        :caption: Example on sending a file using this class
        from telebot.types import InputFile
        # Sending a file from disk
        bot.send_document(
            chat_id,
            InputFile('/path/to/file/file.txt')
        )
        # Sending a file from an io.IOBase object
        with open('/path/to/file/file.txt', 'rb') as f:
            bot.send_document(
                chat_id,
                InputFile(f)
            )
        # Sending a file using pathlib.Path:
        bot.send_document(
            chat_id,
            InputFile(pathlib.Path('/path/to/file/file.txt'))
        )
    """

    def __init__(self, file) -> None:
        self._file, self.file_name = self._resolve_file(file)

    def _resolve_file(self, file):
        if isinstance(file, str):
            _file = open(file, "rb")
            return _file, os.path.basename(_file.name)
        elif isinstance(file, IOBase):
            return file, os.path.basename(file.name)
        elif isinstance(file, Path):
            _file = open(file, "rb")
            return _file, os.path.basename(_file.name)
        else:
            raise TypeError("File must be a string or a file-like object(pathlib.Path, io.IOBase).")

    @property
    def file(self):
        """
        File object.
        """
        return self._file


class ForumTopicCreated(JsonDeserializable):
    """
    This object represents a service message about a new forum topic created in the chat.

    Telegram documentation: https://core.telegram.org/bots/api#forumtopiccreated
    :param name: Name of the topic
    :type name: :obj:`str`
    :param icon_color: Color of the topic icon in RGB format
    :type icon_color: :obj:`int`
    :param icon_custom_emoji_id: Optional. Unique identifier of the custom emoji shown as the topic icon
    :type icon_custom_emoji_id: :obj:`str`
    :return: Instance of the class
    :rtype: :class:`telebot.types.ForumTopicCreated`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(self, name: str, icon_color: int, icon_custom_emoji_id: Optional[str] = None) -> None:
        self.name: str = name
        self.icon_color: int = icon_color
        self.icon_custom_emoji_id: Optional[str] = icon_custom_emoji_id


class ForumTopicClosed(JsonDeserializable):
    """
    This object represents a service message about a forum topic closed in the chat. Currently holds no information.

    Telegram documentation: https://core.telegram.org/bots/api#forumtopicclosed
    """

    # for future use
    @classmethod
    def de_json(cls, json_string):
        return cls()

    def __init__(self) -> None:
        pass


class ForumTopicReopened(JsonDeserializable):
    """
    This object represents a service message about a forum topic reopened in the chat. Currently holds no information.
    Telegram documentation: https://core.telegram.org/bots/api#forumtopicreopened
    """

    # for future use
    @classmethod
    def de_json(cls, json_string):
        return cls()

    def __init__(self) -> None:
        pass


class ForumTopicEdited(JsonDeserializable):
    """
    This object represents a service message about an edited forum topic.
    Telegram documentation: https://core.telegram.org/bots/api#forumtopicedited
    :param name: Optional, Name of the topic(if updated)
    :type name: :obj:`str`
    :param icon_custom_emoji_id: Optional. New identifier of the custom emoji shown as the topic icon, if it was edited;
        an empty string if the icon was removed
    :type icon_custom_emoji_id: :obj:`str`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(self, name: Optional[str] = None, icon_custom_emoji_id: Optional[str] = None) -> None:
        self.name: Optional[str] = name
        self.icon_custom_emoji_id: Optional[str] = icon_custom_emoji_id


class GeneralForumTopicHidden(JsonDeserializable):
    """
    This object represents a service message about General forum topic hidden in the chat.
    Currently holds no information.
    Telegram documentation: https://core.telegram.org/bots/api#generalforumtopichidden
    """

    @classmethod
    def de_json(cls, json_string):
        return cls()

    def __init__(self) -> None:
        pass


class GeneralForumTopicUnhidden(JsonDeserializable):
    """
    This object represents a service message about General forum topic unhidden in the chat.
    Currently holds no information.
    Telegram documentation: https://core.telegram.org/bots/api#generalforumtopicunhidden
    """

    @classmethod
    def de_json(cls, json_string):
        return cls()

    def __init__(self) -> None:
        pass


class ForumTopic(JsonDeserializable):
    """
    This object represents a forum topic.
    Telegram documentation: https://core.telegram.org/bots/api#forumtopic
    :param message_thread_id: Unique identifier of the forum topic
    :type message_thread_id: :obj:`int`
    :param name: Name of the topic
    :type name: :obj:`str`
    :param icon_color: Color of the topic icon in RGB format
    :type icon_color: :obj:`int`
    :param icon_custom_emoji_id: Optional. Unique identifier of the custom emoji shown as the topic icon
    :type icon_custom_emoji_id: :obj:`str`
    :return: Instance of the class
    :rtype: :class:`telebot.types.ForumTopic`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(
        self,
        message_thread_id: int,
        name: str,
        icon_color: int,
        icon_custom_emoji_id: Optional[str] = None,
    ) -> None:
        self.message_thread_id: int = message_thread_id
        self.name: str = name
        self.icon_color: int = icon_color
        self.icon_custom_emoji_id: Optional[str] = icon_custom_emoji_id


class WriteAccessAllowed(JsonDeserializable):
    """
    This object represents a service message about a user allowed to post messages in the chat.
    Currently holds no information.
    Telegram documentation: https://core.telegram.org/bots/api#writeaccessallowed
    """

    @classmethod
    def de_json(cls, json_string):
        return cls()

    def __init__(self) -> None:
        pass


class UserShared(JsonDeserializable):
    """
    This object contains information about the user whose identifier was shared with the bot using a
    `telebot.types.KeyboardButtonRequestUser` button.
    Telegram documentation: https://core.telegram.org/bots/api#usershared
    :param request_id: identifier of the request
    :type request_id: :obj:`int`
    :param user_id: Identifier of the shared user. This number may have more than 32 significant bits and some programming
        languages may have difficulty/silent defects in interpreting it. But it has at most 52 significant bits, so a 64-bit
        integer or double-precision float type are safe for storing this identifier. The bot may not have access to the user
        and could be unable to use this identifier, unless the user is already known to the bot by some other means.
    :type user_id: :obj:`int`
    :return: Instance of the class
    :rtype: :class:`telebot.types.UserShared`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(self, request_id: int, user_id: int) -> None:
        self.request_id: int = request_id
        self.user_id: int = user_id


class ChatShared(JsonDeserializable):
    """
    This object contains information about the chat whose identifier was shared with the bot using a
    `telebot.types.KeyboardButtonRequestChat` button.
    Telegram documentation: https://core.telegram.org/bots/api#Chatshared
    :param request_id: identifier of the request
    :type request_id: :obj:`int`
    :param chat_id: Identifier of the shared chat. This number may have more than 32 significant bits and some programming
        languages may have difficulty/silent defects in interpreting it. But it has at most 52 significant bits, so a 64-bit
        integer or double-precision float type are safe for storing this identifier. The bot may not have access to the chat
        and could be unable to use this identifier, unless the chat is already known to the bot by some other means.
    :type chat_id: :obj:`int`
    :return: Instance of the class
    :rtype: :class:`telebot.types.ChatShared`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.ensure_json_dict(json_string)
        return cls(**obj)

    def __init__(self, request_id: int, chat_id: int) -> None:
        self.request_id: int = request_id
        self.chat_id: int = chat_id


AllowedUpdateName = Literal[
    "update_id",
    "message",
    "edited_message",
    "channel_post",
    "edited_channel_post",
    "inline_query",
    "chosen_inline_result",
    "callback_query",
    "shipping_query",
    "pre_checkout_query",
    "poll",
    "poll_answer",
    "my_chat_member",
    "chat_member",
    "chat_join_request",
]


class BotDescription(JsonDeserializable):
    """
    This object represents a bot description.
    Telegram documentation: https://core.telegram.org/bots/api#botdescription
    :param description: Bot description
    :type description: :obj:`str`
    :return: Instance of the class
    :rtype: :class:`telebot.types.BotDescription`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.check_json(json_string)
        return cls(**obj)

    def __init__(self, description: str) -> None:
        self.description: str = description


class BotShortDescription(JsonDeserializable):
    """
    This object represents a bot short description.
    Telegram documentation: https://core.telegram.org/bots/api#botshortdescription
    :param short_description: Bot short description
    :type short_description: :obj:`str`
    :return: Instance of the class
    :rtype: :class:`telebot.types.BotShortDescription`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.check_json(json_string)
        return cls(**obj)

    def __init__(self, short_description: str) -> None:
        self.short_description: str = short_description


class InputSticker(Dictionaryable, JsonSerializable):
    """
    This object describes a sticker to be added to a sticker set.
    :param sticker: The added sticker. Pass a file_id as a String to send a file that already exists on the Telegram servers,
        pass an HTTP URL as a String for Telegram to get a file from the Internet, or upload a new one using multipart/form-data.
        Animated and video stickers can't be uploaded via HTTP URL.
    :type sticker: :obj:`str` or :obj:`telebot.types.InputFile`
    :param emoji_list: One or more(up to 20) emoji(s) corresponding to the sticker
    :type emoji_list: :obj:`list` of :obj:`str`
    :param mask_position: Optional. Position where the mask should be placed on faces. For “mask” stickers only.
    :type mask_position: :class:`telebot.types.MaskPosition`

    :param keywords: Optional. List of 0-20 search keywords for the sticker with total length of up to 64 characters.
        For “regular” and “custom_emoji” stickers only.
    :type keywords: :obj:`list` of :obj:`str`
    :return: Instance of the class
    :rtype: :class:`telebot.types.InputSticker`
    """

    def __init__(
        self,
        sticker: Union[str, InputFile],
        emoji_list: List[str],
        mask_position: Optional[MaskPosition] = None,
        keywords: Optional[List[str]] = None,
    ) -> None:
        self.sticker: Union[str, InputFile] = sticker
        self.emoji_list: List[str] = emoji_list
        self.mask_position: Optional[MaskPosition] = mask_position
        self.keywords: Optional[List[str]] = keywords

        if util.is_string(self.sticker):
            self._sticker_name = ""
            self._sticker_dic = self.sticker
        else:
            # work like in inputmedia: convert_input_media
            self._sticker_name = util.generate_random_token()
            # uses attach://_sticker_name for sticker param. then,
            # actual file is sent using files param of the request
            self._sticker_dic = "attach://{0}".format(self._sticker_name)

    def to_dict(self) -> dict:
        json_dict = {"sticker": self._sticker_dic, "emoji_list": self.emoji_list}

        if self.mask_position is not None:
            json_dict["mask_position"] = self.mask_position.to_dict()
        if self.keywords is not None:
            json_dict["keywords"] = self.keywords

        return json_dict

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def convert_input_sticker(self):
        if util.is_string(self.sticker):
            return self.to_json(), None

        return self.to_json(), {self._sticker_name: self.sticker}


class SwitchInlineQueryChosenChat(JsonDeserializable, Dictionaryable, JsonSerializable):
    """
    Represents an inline button that switches the current user to inline mode in a chosen chat,
    with an optional default inline query.
    Telegram Documentation: https://core.telegram.org/bots/api#inlinekeyboardbutton
    :param query: Optional. The default inline query to be inserted in the input field.
                  If left empty, only the bot's username will be inserted
    :type query: :obj:`str`
    :param allow_user_chats: Optional. True, if private chats with users can be chosen
    :type allow_user_chats: :obj:`bool`
    :param allow_bot_chats: Optional. True, if private chats with bots can be chosen
    :type allow_bot_chats: :obj:`bool`
    :param allow_group_chats: Optional. True, if group and supergroup chats can be chosen
    :type allow_group_chats: :obj:`bool`
    :param allow_channel_chats: Optional. True, if channel chats can be chosen
    :type allow_channel_chats: :obj:`bool`
    :return: Instance of the class
    :rtype: :class:`SwitchInlineQueryChosenChat`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.check_json(json_string)
        return cls(**obj)

    def __init__(
        self,
        query=None,
        allow_user_chats=None,
        allow_bot_chats=None,
        allow_group_chats=None,
        allow_channel_chats=None,
    ):
        self.query: str = query
        self.allow_user_chats: bool = allow_user_chats
        self.allow_bot_chats: bool = allow_bot_chats
        self.allow_group_chats: bool = allow_group_chats
        self.allow_channel_chats: bool = allow_channel_chats

    def to_dict(self):
        json_dict = {}

        if self.query is not None:
            json_dict["query"] = self.query
        if self.allow_user_chats is not None:
            json_dict["allow_user_chats"] = self.allow_user_chats
        if self.allow_bot_chats is not None:
            json_dict["allow_bot_chats"] = self.allow_bot_chats
        if self.allow_group_chats is not None:
            json_dict["allow_group_chats"] = self.allow_group_chats
        if self.allow_channel_chats is not None:
            json_dict["allow_channel_chats"] = self.allow_channel_chats

        return json_dict

    def to_json(self):
        return json.dumps(self.to_dict())


class BotName(JsonDeserializable):
    """
    This object represents a bot name.
    Telegram Documentation: https://core.telegram.org/bots/api#botname
    :param name: The bot name
    :type name: :obj:`str`
    :return: Instance of the class
    :rtype: :class:`BotName`
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.check_json(json_string)
        return cls(**obj)

    def __init__(self, name: str):
        self.name: str = name


class InlineQueryResultsButton(JsonSerializable, Dictionaryable):
    """
    This object represents a button to be shown above inline query results.
    You must use exactly one of the optional fields.
    Telegram documentation: https://core.telegram.org/bots/api#inlinequeryresultsbutton
    :param text: Label text on the button
    :type text: :obj:`str`
    :param web_app: Optional. Description of the Web App that will be launched when the user presses the button.
        The Web App will be able to switch back to the inline mode using the method web_app_switch_inline_query inside the Web App.
    :type web_app: :class:`telebot.types.WebAppInfo`

    :param start_parameter: Optional. Deep-linking parameter for the /start message sent to the bot when a user presses the button.
        1-64 characters, only A-Z, a-z, 0-9, _ and - are allowed.
        Example: An inline bot that sends YouTube videos can ask the user to connect the bot to their YouTube account to adapt search
        results accordingly. To do this, it displays a 'Connect your YouTube account' button above the results, or even before showing
        any. The user presses the button, switches to a private chat with the bot and, in doing so, passes a start parameter that instructs
        the bot to return an OAuth link. Once done, the bot can offer a switch_inline button so that the user can easily return to the chat
        where they wanted to use the bot's inline capabilities.
    :type start_parameter: :obj:`str`
    :return: Instance of the class
    :rtype: :class:`InlineQueryResultsButton`
    """

    def __init__(
        self,
        text: str,
        web_app: Optional[WebAppInfo] = None,
        start_parameter: Optional[str] = None,
    ) -> None:
        self.text: str = text
        self.web_app: Optional[WebAppInfo] = web_app
        self.start_parameter: Optional[str] = start_parameter

    def to_dict(self) -> dict:
        json_dict = {"text": self.text}

        if self.web_app is not None:
            json_dict["web_app"] = self.web_app.to_dict()
        if self.start_parameter is not None:
            json_dict["start_parameter"] = self.start_parameter

        return json_dict

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class Story(JsonDeserializable):
    """
    This object represents a message about a forwarded story in the chat.
    Currently holds no information.
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.check_json(json_string)
        return cls(**obj)

    def __init__(self) -> None:
        pass


# noinspection PyShadowingBuiltins
class ReactionType(JsonDeserializable, Dictionaryable, JsonSerializable):
    """
    This object represents a reaction type.

    Telegram documentation: https://core.telegram.org/bots/api#reactiontype
    """

    @classmethod
    def de_json(cls, json_string):
        if json_string is None:
            return None
        obj = cls.check_json(json_string)
        # remove type
        if obj["type"] == "emoji":
            del obj["type"]
            return ReactionTypeEmoji(**obj)
        elif obj["type"] == "custom_emoji":
            del obj["type"]
            return ReactionTypeCustomEmoji(**obj)

    def __init__(self, type: str) -> None:
        self.type: str = type

    def to_dict(self) -> dict:
        json_dict = {"type": self.type}
        return json_dict

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


# noinspection PyUnresolvedReferences
class ReactionTypeEmoji(ReactionType):
    """
    This object represents an emoji reaction type.

    Telegram documentation: https://core.telegram.org/bots/api#reactiontypeemoji
    """

    def __init__(self, emoji: str, **kwargs) -> None:
        super().__init__("emoji")
        self.emoji: str = emoji

    def to_dict(self) -> dict:
        json_dict = super().to_dict()
        json_dict["emoji"] = self.emoji
        return json_dict


# noinspection PyUnresolvedReferences,PyUnusedLocal
class ReactionTypeCustomEmoji(ReactionType):
    """
    This object represents a custom emoji reaction type.

    Telegram documentation: https://core.telegram.org/bots/api#reactiontypecustomemoji
    """

    def __init__(self, custom_emoji_id: str, **kwargs) -> None:
        super().__init__("custom_emoji")
        self.custom_emoji_id: str = custom_emoji_id

    def to_dict(self) -> dict:
        json_dict = super().to_dict()
        json_dict["custom_emoji_id"] = self.custom_emoji_id
        return json_dict


class ReactionTypePaid(ReactionType):
    """
    This object represents a paid reaction type.

    Telegram documentation: https://core.telegram.org/bots/api#reactiontypepaid

    :param type: Type of the reaction, must be paid
    :type type: :obj:`str`

    :return: Instance of the class
    :rtype: :class:`ReactionTypePaid`
    """

    def __init__(self, **kwargs) -> None:
        super().__init__("paid")

    def to_dict(self) -> dict:
        return super().to_dict()
