from __future__ import annotations

from datetime import datetime

from rgdps.common.context import Context
from rgdps.common.typing import is_set
from rgdps.common.typing import UNSET
from rgdps.common.typing import Unset
from rgdps.models.friend_request import FriendRequest


async def from_id(
    ctx: Context,
    request_id: int,
    include_deleted: bool = False,
) -> FriendRequest | None:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    friend_request_db = await ctx.mysql.fetch_one(
        "SELECT id, sender_user_id, recipient_user_id, message, post_ts, seen_ts "
        f"FROM friend_requests WHERE id = :request_id {condition}",
        {"request_id": request_id},
    )

    if not friend_request_db:
        return None

    return FriendRequest.from_mapping(friend_request_db)


async def from_target_and_recipient(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    include_deleted: bool = False,
) -> FriendRequest | None:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    friend_request_db = await ctx.mysql.fetch_one(
        "SELECT id, sender_user_id, recipient_user_id, message, post_ts, seen_ts "
        "FROM friend_requests WHERE sender_user_id = :sender_user_id AND "
        f"recipient_user_id = :recipient_user_id {condition}",
        {"sender_user_id": sender_user_id, "recipient_user_id": recipient_user_id},
    )

    if not friend_request_db:
        return None

    return FriendRequest.from_mapping(friend_request_db)


async def from_user_id(
    ctx: Context,
    user_id: int,
    is_sender_user_id: bool = False,
    include_deleted: bool = False,
) -> list[FriendRequest]:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    id_row = "recipient_user_id"
    if is_sender_user_id:
        id_row = "sender_user_id"

    friend_requests_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, message, post_ts, seen_ts "
        f"FROM friend_requests WHERE {id_row} = :user_id {condition} "
        "ORDER BY post_ts DESC",
        {"user_id": user_id},
    )

    return [
        FriendRequest.from_mapping(friend_request_db)
        for friend_request_db in friend_requests_db
    ]


async def from_user_id_paginated(
    ctx: Context,
    user_id: int,
    page: int,
    page_size: int,
    is_sender_user_id: bool = False,
    include_deleted: bool = False,
) -> list[FriendRequest]:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    id_row = "recipient_user_id"
    if is_sender_user_id:
        id_row = "sender_user_id"

    friend_requests_db = await ctx.mysql.fetch_all(
        "SELECT id, sender_user_id, recipient_user_id, message, post_ts, seen_ts "
        f"FROM friend_requests WHERE {id_row} = :user_id {condition} "
        "ORDER BY post_ts DESC LIMIT :limit OFFSET :offset",
        {
            "user_id": user_id,
            "limit": page_size,
            "offset": page * page_size,
        },
    )

    return [
        FriendRequest.from_mapping(friend_request_db)
        for friend_request_db in friend_requests_db
    ]


async def get_user_friend_request_count(
    ctx: Context,
    user_id: int,
    is_sender_user_id: bool = False,
    is_new: bool = False,
    include_deleted: bool = False,
) -> int:
    id_row = "recipient_user_id"
    if is_sender_user_id:
        id_row = "sender_user_id"

    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    if is_new:
        condition += " AND seen_ts IS NULL"

    return await ctx.mysql.fetch_val(
        f"SELECT COUNT(*) FROM friend_requests WHERE {id_row} = :user_id {condition}",
        {"user_id": user_id},
    )


async def check_request_exists(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    include_deleted: bool = False,
) -> bool:
    condition = ""
    if not include_deleted:
        condition = "AND deleted = 0"

    return await ctx.mysql.fetch_val(
        "SELECT EXISTS(SELECT 1 FROM friend_requests WHERE sender_user_id = :sender_user_id "
        f"AND recipient_user_id = :recipient_user_id {condition})",
        {"sender_user_id": sender_user_id, "recipient_user_id": recipient_user_id},
    )


async def create(
    ctx: Context,
    sender_user_id: int,
    recipient_user_id: int,
    message: str,
    post_ts: datetime = datetime.now(),
    seen_ts: None | datetime = None,
) -> FriendRequest:
    friend_request = FriendRequest(
        id=0,
        sender_user_id=sender_user_id,
        recipient_user_id=recipient_user_id,
        message=message,
        post_ts=post_ts,
        seen_ts=seen_ts,
    )

    friend_request.id = await ctx.mysql.execute(
        "INSERT INTO friend_requests (sender_user_id, recipient_user_id, message, post_ts, seen_ts) "
        "VALUES (:sender_user_id, :recipient_user_id, :message, :post_ts, :seen_ts)",
        friend_request.as_dict(include_id=False),
    )

    return friend_request


async def update_partial(
    ctx: Context,
    request_id: int,
    seen_ts: Unset | datetime = UNSET,
    deleted: Unset | bool = UNSET,
) -> FriendRequest | None:
    changed_data = {}

    if is_set(seen_ts):
        changed_data["seen_ts"] = seen_ts
    if is_set(deleted):
        changed_data["deleted"] = deleted

    if not changed_data:
        return None

    query = "UPDATE friend_requests SET "
    query += ", ".join(f"{key} = :{key}" for key in changed_data.keys())
    query += " WHERE id = :id"

    changed_data["id"] = request_id

    await ctx.mysql.execute(query, changed_data)

    return await from_id(ctx, request_id, include_deleted=True)


async def get_count(ctx: Context) -> int:
    return await ctx.mysql.fetch_val("SELECT COUNT(*) FROM friend_requests")
