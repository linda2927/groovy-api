from django.db import models
from softdelete.models import SoftDeleteObject

from group.models import Group
from user.models import User, TimeStampMixin

"""
그룹 채팅
"""


class GroupChatroom(TimeStampMixin, SoftDeleteObject):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_chatroom")

    class Meta:
        db_table = "group_chatroom"

    def __repr__(self):
        return f"GroupChatroom({self.id}, {self.group})"


class GroupChat(TimeStampMixin, SoftDeleteObject):
    id = models.BigAutoField(primary_key=True)
    chatroom = models.ForeignKey(
        GroupChatroom, on_delete=models.CASCADE, related_name="latest_chat"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)

    class Meta:
        db_table = "group_chat"

    def __repr__(self):
        return f"GroupChat(id={self.id}, chatroom={self.chatroom}, user={self.user})"


class GroupChatroomNotice(TimeStampMixin, SoftDeleteObject):
    id = models.BigAutoField(primary_key=True)
    chatroom = models.ForeignKey(GroupChatroom, on_delete=models.CASCADE, related_name="notice")
    pinned_chat = models.ForeignKey(GroupChat, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="pinned_chat")

    class Meta:
        db_table = "group_chatroom_notice"


"""
개인 채팅
"""


def user_inexistent():
    # TODO: 존재하지 않는 유저일 때
    pass


class PersonalChatroom(TimeStampMixin, SoftDeleteObject):
    # TODO: SET Action
    id = models.BigAutoField(primary_key=True)
    sender = models.ForeignKey(
        User,
        on_delete=models.SET(user_inexistent),
        related_name="personal_chatroom_sender",
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.SET(user_inexistent),
        related_name="personal_chatroom_receiver",
    )

    class Meta:
        db_table = "personal_chatroom"
        constraints = [
            models.UniqueConstraint(
                fields=["sender", "receiver"], name="unique_chatroom"
            )
        ]


class PersonalChat(TimeStampMixin, SoftDeleteObject):
    id = models.BigAutoField(primary_key=True)
    chatroom = models.ForeignKey(
        PersonalChatroom, on_delete=models.DO_NOTHING, related_name="chatroom"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="regular_chat_sender"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="regular_chat_receiver"
    )
    content = models.CharField(max_length=1000)
    is_join_request_message = models.BooleanField(default=False)

    class Meta:
        db_table = "personal_chat"

    def __repr__(self):
        return f"PersonalChat(id={self.id}, sender={self.sender}, receiver={self.receiver})"
