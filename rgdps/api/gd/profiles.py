from __future__ import annotations

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import authenticate_dependency
from rgdps.common import gd_obj
from rgdps.constants.errors import ServiceError
from rgdps.constants.responses import GenericResponse
from rgdps.models.user import User
from rgdps.usecases import users


async def view_user_info(
    ctx: HTTPContext = Depends(),
    target_id: int = Form(..., alias="targetAccountID"),
    user: User = Depends(authenticate_dependency()),
) -> str:
    target = await users.get_user_perspective(ctx, target_id, user)

    if isinstance(target, ServiceError):
        logger.info(
            f"Requested to view info of non-existent account {target_id} "
            f"with error {target!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully viewed the profile of {target.user}.")

    return gd_obj.dumps(
        gd_obj.create_profile(target.user, target.friend_status, target.rank),
    )


async def update_user_info(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    stars: int = Form(...),
    demons: int = Form(...),
    display_type: int = Form(..., alias="icon"),
    diamonds: int = Form(...),
    primary_colour: int = Form(..., alias="color1"),
    secondary_colour: int = Form(..., alias="color2"),
    icon: int = Form(..., alias="accIcon"),
    ship: int = Form(..., alias="accShip"),
    ball: int = Form(..., alias="accBall"),
    ufo: int = Form(..., alias="accBird"),
    wave: int = Form(..., alias="accDart"),
    robot: int = Form(..., alias="accRobot"),
    spider: int = Form(..., alias="accSpider"),
    glow: bool = Form(..., alias="accGlow"),
    explosion: int = Form(..., alias="accExplosion"),
    coins: int = Form(...),
    user_coins: int = Form(..., alias="userCoins"),
) -> str:

    res = await users.update_stats(
        ctx,
        user,
        stars=stars,
        demons=demons,
        display_type=display_type,
        diamonds=diamonds,
        primary_colour=primary_colour,
        secondary_colour=secondary_colour,
        icon=icon,
        ship=ship,
        ball=ball,
        ufo=ufo,
        wave=wave,
        robot=robot,
        spider=spider,
        glow=glow,
        explosion=explosion,
        coins=coins,
        user_coins=user_coins,
    )

    if isinstance(res, ServiceError):
        logger.info(f"Failed to update profile of {user} with error {res!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully updated the profile of {user}.")

    return str(user.id)


async def update_settings(
    ctx: HTTPContext = Depends(),
    user: User = Depends(authenticate_dependency()),
    youtube_name: str = Form(..., alias="yt"),
    twitter_name: str = Form(..., alias="twitter"),
    twitch_name: str = Form(..., alias="twitch"),
) -> str:
    result = await users.update_stats(
        ctx,
        user,
        youtube_name=youtube_name,
        twitter_name=twitter_name,
        twitch_name=twitch_name,
    )

    if isinstance(result, ServiceError):
        logger.info(
            f"Failed to update settings of {user} with error {result!r}.",
        )
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully updated settings of {user}.")
    return str(GenericResponse.SUCCESS)