from __future__ import annotations

from typing import Union

from realistikgdps.constants.friends import FriendStatus
from realistikgdps.models.user import User
from realistikgdps.typing.types import GDSerialisable


def dumps(obj: GDSerialisable, sep: str = ":") -> str:
    return sep.join(str(key) + sep + str(value) for key, value in obj.items())


def create_gd_profile(
    user: User,
    friend_status: FriendStatus = FriendStatus.NONE,
) -> GDSerialisable:
    return {
        1: user.username,
        2: user.id,
        3: user.stars,
        4: user.demons,
        6: 0,  # TODO: Implement rank
        7: user.id,
        8: user.creator_points,
        9: user.display_type,
        10: user.primary_colour,
        11: user.secondary_colour,
        13: user.coins,
        14: user.icon,
        15: 0,
        16: user.id,
        17: user.user_coins,
        18: user.message_privacy.value,
        19: user.friend_privacy.value,
        20: user.youtube_name or "",
        21: user.icon,
        22: user.ship,
        23: user.ball,
        24: user.ufo,
        25: user.wave,
        26: user.robot,
        28: int(user.glow),
        29: 1,  # Is Registered
        30: 0,  # TODO: Implement rank
        31: friend_status.value,
        43: user.spider,
        44: user.twitter_name or "",
        45: user.twitch_name or "",
        46: 0,  # TODO: Diamonds, which require save data parsing....
        48: user.explosion,
        49: 0,  # TODO: Badge level with privileges.
        50: user.comment_privacy.value,
    }
