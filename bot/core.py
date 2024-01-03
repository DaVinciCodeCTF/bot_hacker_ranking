import logging
import re
from datetime import datetime

import discord
from discord.ext import tasks

from bot.embed_creation import create_profile_embed, create_help_embed
from bot.pagination_view import PaginationView
from database.crud_data import (get_data, update_data, get_data_organization_leaderboard, get_organization_rank)
from database.crud_user import (get_user, update_user, insert_user)
from database.models import User, DailyUserData
from utils.api import (get_htb_data, get_rm_data, get_thm_data)
from utils.ressources import setup_emoji
from utils.services import update_all_daily_data

logger = logging.getLogger(__name__)


def setup_bot(
        guild_id: int,
        channel_id: list[int],
        update_interval: int,
        organization_name: str,
        dev_mode: bool = False
) -> discord.Bot:
    intents = discord.Intents.default()
    intents.members = True
    bot = discord.Bot(intents=intents)

    guild_emojis: dict = {}

    @bot.event
    async def on_ready() -> None:
        """
        Function launched after bot.run()
        :return:
        """
        await bot.wait_until_ready()

        await setup_emoji(bot, guild_id)
        guild_emojis.update({'HTB_logo': discord.utils.get(bot.emojis, name='HTB_logo')})
        guild_emojis.update({'RM_logo': discord.utils.get(bot.emojis, name='RM_logo')})
        guild_emojis.update({'THM_logo': discord.utils.get(bot.emojis, name='THM_logo')})

        logger.info(f'{bot.user} is ready and online!')

        update_users_score.start()

    @bot.event
    async def on_application_command_error(ctx, error) -> None:
        """
        Function launched when an error occurs
        Used to handle the CheckFailure error when the command is launched in the wrong channel
        :param ctx: ApplicationContext, automatically passed
        :param error: error, automatically passed
        :return: none
        """
        if isinstance(error, discord.errors.CheckFailure):
            await ctx.respond(
                f':no_entry_sign: You can\'t use this command in this channel. '
                f'Please use the <#{channel_id[0]}> channel.',
                ephemeral=True
            )

    @bot.check
    async def check_channel(ctx) -> bool:
        """
        Check if the command is launched in the right channel
        :param ctx: ApplicationContext, automatically passed
        :return: bool, True if the command is launched in the right channel, False otherwise
        """
        return ctx.channel.id in channel_id

    @tasks.loop(minutes=update_interval)
    async def update_users_score() -> None:
        """
        Every hour, update all users score,
        will create a new DailyUserData if it doesn't exist
        and will delete the user if it doesn't exist anymore
        :return: None
        """
        members_ids: list[int] = [member.id for member in bot.get_guild(guild_id).members]

        logger.debug('Updating users score...')
        await update_all_daily_data(members_ids, dev_mode)
        logger.debug('Users score updated!')

    @bot.slash_command(
        name='register',
        description='Register yourself to the database, you need to do this before using the bot',
        guild_ids=[guild_id]
    )
    async def register(
            ctx,
            username: discord.Option(
                str,
                description='Your leaderboard username (alphanumeric, -, _, . between 3 and 25 characters)',
                required=True
            )
    ) -> None:
        """
        Register a new user to the database
        :param ctx: ApplicationContext, automatically passed
        :param username: str, username of the user
        :return: None
        """
        author_id: int = ctx.author.id

        if re.match(pattern=r'^([a-zA-Z0-9-_.]{3,25})$', string=username) is None:
            await ctx.respond(
                f':closed_lock_with_key: Hmm... `{username}` doesn\'t seem like a valid username.\n'
                'Make sure to use alphanumeric characters, -, _, or . and keep it between 3 and 25 characters.',
                ephemeral=True
            )
        elif (user := get_user(discord_id=author_id)) is not None:
            await ctx.respond(
                f':detective: Hey `{user.username}`! Looks like you\'re already registered. Ready for another mission?',
                ephemeral=True
            )
        elif get_user(username=username) is not None:
            await ctx.respond(
                f':no_entry_sign: Oops! The username `{username}` is already taken. Maybe a hacker alias?',
                ephemeral=True
            )
        else:
            insert_user({'discord_id': author_id, 'username': username})
            logger.debug(f'New user registered: {username} by {author_id}')
            await ctx.respond(
                f':tada: Welcome aboard, `{username}`! Gear up for some cybersecurity challenges!',
                ephemeral=True
            )

    @bot.slash_command(
        name='update',
        description='Update your profile (username & website token)',
        guild_ids=[guild_id]
    )
    async def update(
            ctx,
            username: discord.Option(
                str,
                description='Your leaderboard username (alphanumeric, -, _, . between 3 and 25 characters)',
                required=False
            ),
            htb_id: discord.Option(
                int,
                description='Your HackTheBox user ID',
                required=False
            ),
            rm_id: discord.Option(
                int,
                description='Your RootMe user ID',
                required=False
            ),
            thm_id: discord.Option(
                str,
                description='Your TryHackMe user ID',
                required=False
            ),
    ) -> None:
        """
        Update the user profile
        :param ctx: ApplicationContext, automatically passed
        :param username: str, username of the user
        :param htb_id: int, HackTheBox user ID of the user
        :param rm_id: int, RootMe user ID of the user
        :param thm_id: str, TryHackMe user ID of the user
        """
        logger.debug(f'User @{ctx.author} updating profile: {username=}, {htb_id=}, {rm_id=}, {thm_id=}')

        if not username and not htb_id and not rm_id and not thm_id:
            await ctx.respond(
                ':warning: You need to provide at least one argument.',
                ephemeral=True
            )
            return None

        author_id: int = ctx.author.id
        user: User = get_user(discord_id=author_id)
        updates_user: dict = {}
        updates_daily_data: dict = {}

        await ctx.defer(ephemeral=True)

        if not user:
            await ctx.respond(
                ':no_entry_sign: You need to register using the `/register` command first.',
                ephemeral=True
            )
            return None
        else:
            if username:
                if re.match(r'^([a-zA-Z0-9-_.]{3,25})$', username) is None:
                    await ctx.respond(
                        f':closed_lock_with_key: Hmm... `{username}` doesn\'t seem like a valid username.\n'
                        'Make sure to use alphanumeric characters, -, _, or . and keep it between 3 and 25 characters.',
                        ephemeral=True
                    )
                    return None
                elif get_user(username=username) is not None:
                    await ctx.respond(
                        f':no_entry_sign: Oops! The username `{username}` is already taken. Maybe a hacker alias?',
                        ephemeral=True
                    )
                    return None
                else:
                    updates_user['username']: str = username

            if htb_id:
                if re.match(r'^([0-9]{1,9})$', str(htb_id)) is None:
                    await ctx.respond(
                        f':closed_lock_with_key: Hmm... `{htb_id}` doesn\'t seem like a valid HackTheBox ID.',
                        ephemeral=True
                    )
                    return None
                else:
                    htb_data = await get_htb_data(htb_id)
                    if not htb_data:
                        await ctx.respond(
                            f':no_entry_sign: Oops! The HackTheBox ID `{htb_id}` doesn\'t exist.',
                            ephemeral=True
                        )
                        return None
                    else:
                        updates_user['htb_id']: int = htb_id
                        updates_daily_data['htb_rank']: int = htb_data['htb_rank']
                        updates_daily_data['htb_score']: int = htb_data['htb_score']

            if rm_id:
                if re.match(r'^[0-9]{1,9}$', str(rm_id)) is None:
                    await ctx.respond(
                        f':closed_lock_with_key: Hmm... `{rm_id}` doesn\'t seem like a valid RootMe ID.',
                        ephemeral=True
                    )
                    return None
                else:
                    rm_data = await get_rm_data(rm_id, rm_name_check=True)
                    if not rm_data:
                        await ctx.respond(
                            f':no_entry_sign: Oops! The RootMe ID `{rm_id}` doesn\'t exist.',
                            ephemeral=True
                        )
                        return None
                    else:
                        updates_user['rm_id']: int = rm_id
                        updates_daily_data['rm_rank']: int = rm_data['rm_rank']
                        updates_daily_data['rm_score']: int = rm_data['rm_score']
                        updates_user['rm_name']: str = rm_data['rm_name']

            if thm_id:
                if re.match(r'^([a-zA-Z0-9-_.]{2,16})$', thm_id) is None:
                    await ctx.respond(
                        f':closed_lock_with_key: Hmm... `{thm_id}` doesn\'t seem like a valid TryHackMe ID.',
                        ephemeral=True
                    )
                    return None
                else:
                    thm_data = await get_thm_data(thm_id)
                    if not thm_data:
                        await ctx.respond(
                            f':no_entry_sign: Oops! The TryHackMe ID `{thm_id}` doesn\'t exist.',
                            ephemeral=True
                        )
                        return None
                    else:
                        updates_user['thm_id']: str = thm_id
                        updates_daily_data['thm_rank']: int = thm_data['thm_rank']
                        updates_daily_data['thm_rooms']: int = thm_data['thm_rooms']

            if updates_user or updates_daily_data:
                user: User = update_user(user, updates_user)
                daily_user_data: DailyUserData = update_data(user.discord_id, updates_daily_data)
                orga_user_rank: dict = get_organization_rank(user.discord_id)

                logger.debug(f'User @{user.username} updated: {user=}, {daily_user_data=}, {orga_user_rank=}')

                profile_embed: discord.Embed = create_profile_embed(
                    user, daily_user_data, orga_user_rank, ctx.author, ctx.author, guild_emojis, organization_name
                )

                await ctx.respond(
                    ':white_check_mark: Your profile has been updated!',
                    embed=profile_embed,
                    ephemeral=True
                )

                return None

    @bot.slash_command(
        name='profile',
        description='Display hacker profile of a user',
        guild_ids=[guild_id]
    )
    async def profile(
            ctx,
            member: discord.Option(
                discord.Member,
                description='The username of the user you want to display, leave empty to display your profile',
                required=False,
            )
    ) -> None:
        """
        Display the profile of a user
        :param ctx: ApplicationContext, automatically passed
        :param member: discord.Member, username of the user
        :return: None
        """

        author: discord.Member = ctx.author
        member: discord.Member = author if not member else member
        user: User = get_user(discord_id=member.id)
        is_author: bool = member == author
        display_name: str = "You" if is_author else member.display_name

        if not user:
            message = (f':no_entry_sign: {display_name} need{"s" if not is_author else ""} to register using '
                       f'the `/register` command first.')
            await ctx.respond(message, ephemeral=True)
            return None

        if not user.htb_id and not user.rm_id and not user.thm_id:
            message = (f':no_entry_sign: {display_name} need{"s" if not is_author else ""} to update '
                       f'{"their" if not is_author else "your"} profile using the `/update` command first.')
            await ctx.respond(message, ephemeral=True)
            return None

        await ctx.defer()

        updates_daily_data: dict = {}
        if user.htb_id:
            htb_data = await get_htb_data(user.htb_id)
            updates_daily_data['htb_rank']: int = htb_data['htb_rank']
            updates_daily_data['htb_score']: int = htb_data['htb_score']
        if user.rm_id:
            rm_data = await get_rm_data(user.rm_id)
            updates_daily_data['rm_rank']: int = rm_data['rm_rank']
            updates_daily_data['rm_score']: int = rm_data['rm_score']
        if user.thm_id:
            thm_data = await get_thm_data(user.thm_id)
            updates_daily_data['thm_rank']: int = thm_data['thm_rank']
            updates_daily_data['thm_rooms']: int = thm_data['thm_rooms']

        daily_user_data: DailyUserData = update_data(user.discord_id, updates_daily_data)
        orga_user_rank: dict = get_organization_rank(member.id)

        logger.debug(f'User @{user.username} profile displayed: {user=}, {daily_user_data=}, {orga_user_rank=}')

        profile_embed: discord.Embed = create_profile_embed(
            user, daily_user_data, orga_user_rank, author, member, guild_emojis, organization_name
        )

        await ctx.respond(embed=profile_embed)

    @bot.slash_command(
        name='leaderboard',
        description='Display the leaderboard of the organization members',
        guild_ids=[guild_id]
    )
    async def leaderboard(
            ctx,
            platform: discord.Option(
                str,
                description='The platform you want to display the leaderboard of',
                choices=['htb', 'rm', 'thm'],
                required=True
            )
    ) -> None:
        """
        Display the leaderboard of the organization members
        :param ctx: ApplicationContext, automatically passed
        :param platform: str, platform to display the leaderboard of
        :return: None
        """
        if not platform:
            await ctx.respond(
                ':warning: You need to provide a platform [htb, rm, thm].',
                ephemeral=True
            )
            return None

        leaderboard_list: list[dict] = get_data_organization_leaderboard(platform)
        logger.debug(f'Leaderboard {platform=} {leaderboard_list=}')

        pagination_view = PaginationView(leaderboard_list, platform, ctx.author, organization_name)
        await pagination_view.respond(ctx)

    @bot.slash_command(
        name='help',
        description='Display the help message',
        guild_ids=[guild_id]
    )
    async def help_(ctx) -> None:
        """
        Display the help message
        :param ctx: ApplicationContext, automatically passed
        :return: None
        """
        help_embed: discord.embed = create_help_embed(author=ctx.author, organization_name=organization_name)
        await ctx.respond(embed=help_embed, ephemeral=True)

    return bot
