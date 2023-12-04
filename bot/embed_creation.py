from datetime import datetime

import discord

from database.models import DailyUserData, User
from utils.env_checker import get_organization_name


def create_help_embed(author: discord.Member) -> discord.Embed:
    """
    Create the help embed
    :param author: discord.Member, author of the command
    :return: discord.Embed, help embed
    """
    orga: str = get_organization_name(log=False)

    help_embed = discord.Embed(
        title=f'{orga} bot help',
        description=('Here\'s a list of the available commands. '
                     'Use `/help <command>` to get more information about a specific command. 🔍\n\u200b'),
        colour=discord.Colour.light_gray()
    )
    help_embed.add_field(
        name='Display this message',
        value='`/help`\n\u200b',
        inline=False
    )
    help_embed.add_field(
        name='Register you to the bot under the given pseudo',
        value='`/register <pseudo>[required]`\n\u200b',
        inline=False
    )
    help_embed.add_field(
        name='After registering, update your profile with the given ids',
        value='`/update <pseudo>[opt] <htb_id>[opt] <rm_id>[opt] <thm_id>[opt]`\n'
              '• htb_id: [sign in](https://app.hackthebox.com/login) > [profile]('
              'https://app.hackthebox.com/profile/overview) > #ID, next to your pseudo\n'
              '• rm_id: [sign in](https://www.root-me.org/) > [profile]('
              'https://www.root-me.org/?page=preferences&lang=en) > `uid` field, under `Modify my parameters`\n'
              '• thm_id: [sign in](https://tryhackme.com/login) > [profile](https://tryhackme.com/profile) > '
              '`username` field\n\u200b',
        inline=False
    )
    help_embed.add_field(
        name='Display the profile of a user, or yours if no user is given',
        value='`/profile <user>[opt]`\n\u200b',
        inline=False
    )
    help_embed.add_field(
        name='Display the leaderboard of the given platform',
        value='`/leaderboard <platform>(htb|rm|thm)[required]`',
        inline=False
    )

    help_embed.timestamp = datetime.utcnow()
    help_embed.set_footer(
        text=f'Requested by {author.display_name}',
        icon_url=author.avatar if author.avatar else None
    )
    return help_embed


def create_leaderboard_embed(
        leaderboard_list: list[list[str, int, int, int, int]], platform: str, author: discord.Member
) -> discord.Embed:
    """
    Create the leaderboard embed
    :param leaderboard_list: list[list[str, int, int, int, int]], list of users to display
    :param platform: str, platform to display the leaderboard of
    :param author: discord.Member, author of the command
    :return: discord.Embed, leaderboard embed
    """
    orga: str = get_organization_name(log=False)
    platform_name: dict = {'htb': 'HackTheBox', 'rm': 'RootMe', 'thm': 'TryHackMe'}
    platform_picture: dict = {
        'htb': 'https://yt3.googleusercontent.com/ytc/APkrFKabtklDH7Goj_UUWqeKXVV6uN4_fGMQIc-v5hfR6w=s900-c-k'
               '-c0x00ffffff-no-rj',
        'rm': 'https://pro.root-me.org/squelettes/images/RMP_logo_blanc.png',
        'thm': 'https://pbs.twimg.com/profile_images/1478793060607832067/xGV-V2B8_400x400.jpg'
    }
    platform_color: dict = {'htb': 0x9fef00, 'rm': 0xe00911, 'thm': 0xffffff}
    ranking_emoji: dict = {
        1: ':first_place:',
        2: ':second_place:',
        3: ':third_place:'
    }

    leaderboard_embed = discord.Embed(
        title=f'{orga} {platform_name[platform]} leaderboard',
        description=('Here\'s a snapshot of hacking accomplishments across various platforms. '
                     'Use `/leaderboard` to explore more leaderboards. 🔍\n\u200b'),
        colour=platform_color[platform]
    )
    for username, rank, score, global_rank, score_evolution in leaderboard_list:
        if score == 0:
            continue

        if rank in ranking_emoji.keys():
            username = f'{ranking_emoji[rank]} {username}'
        else:
            username = f'{rank}. {username}'

        score_display: str = 'Score' if platform in ['htb', 'rm'] else 'Rooms'

        if score_evolution > 0:
            stats: str = (f'Global rank: `#{global_rank}` - {score_display}: `{score}` '
                          f'[+{score_evolution} :crossed_swords:]')
        else:
            stats: str = f'Global rank: `#{global_rank}` - {score_display}: `{score}`'

        leaderboard_embed.add_field(
            name=username,
            value=stats,
            inline=False
        )
    leaderboard_embed.set_thumbnail(url=platform_picture[platform])
    leaderboard_embed.timestamp = datetime.utcnow()
    leaderboard_embed.set_footer(
        text=f'Requested by {author.display_name}',
        icon_url=author.avatar if author.avatar else None
    )
    return leaderboard_embed


def create_profile_embed(
        db_user: User, db_data: DailyUserData, db_rank: dict, author: discord.Member, member: discord.Member,
        guild_emojis: dict
) -> discord.Embed:
    """
    Create the profile embed
    :param db_data: DailyUserData, daily data from the database
    :param db_rank: dict, rank of the user
    :param db_user: User, user from the database
    :param author: discord.Member, author of the command
    :param member: discord.Member, user to display
    :return:
    """
    orga: str = get_organization_name(log=False)

    profile_embed = discord.Embed(
        title=f'Hacker profile of `{db_user.username}`',
        description=('Here\'s a snapshot of hacking accomplishments across various platforms. '
                     'Use `/profile` to explore more profiles. 🔍\n\u200b'),
        colour=discord.Colour.light_gray()
    )
    if db_user.htb_id:
        profile_embed.add_field(
            name=f'{guild_emojis["HTB_logo"]} HackTheBox',
            value='-----------------\n'
                  f'{orga} rank: `#{db_rank["htb_orga_rank"] if db_rank["htb_orga_rank"] is not None else "..."}`\n\n'
                  f'Rank: `#{db_data.htb_rank if db_data.htb_rank else "..."}`\n'
                  f'Score: `{db_data.htb_score if db_data.htb_score else "..."}`\n\n'
                  f'ID: [{db_user.htb_id if db_user.htb_id else "..."}]'
                  f'(https://app.hackthebox.com/users/{db_user.htb_id if db_user.htb_id else ""})\n'
                  '-----------------',
            inline=True
        )
    if db_user.rm_id:
        profile_embed.add_field(
            name=f'{guild_emojis["RM_logo"]} RootMe',
            value='-----------------\n'
                  f'{orga} rank: `#{db_rank["rm_orga_rank"] if db_rank["rm_orga_rank"] is not None else "..."}`\n\n'
                  f'Rank: `#{db_data.rm_rank if db_data.rm_rank else "..."}`\n'
                  f'Score: `{db_data.rm_score if db_data.rm_score else "..."}`\n\n'
                  f'ID: [{db_user.rm_id if db_user.rm_id else "..."}]'
                  f'(https://www.root-me.org/{db_user.rm_name if db_user.rm_name else ""})\n'
                  '-----------------',
            inline=True
        )
    if db_user.thm_id:
        profile_embed.add_field(
            name=f'{guild_emojis["THM_logo"]} TryHackMe',
            value='-----------------\n'
                  f'{orga} rank: `#{db_rank["thm_orga_rank"] if db_rank["thm_orga_rank"] is not None else "..."}`\n\n'
                  f'Rank: `#{db_data.thm_rank if db_data.thm_rank else "..."}`\n'
                  f'Rooms: `{db_data.thm_rooms if db_data.thm_rooms else "..."}`\n\n'
                  f'ID: [{db_user.thm_id if db_user.thm_id else "..."}]'
                  f'(https://tryhackme.com/p/{db_user.thm_id if db_user.thm_id else ""})\n'
                  '-----------------',
            inline=True
        )
    if member.avatar:
        profile_embed.set_thumbnail(url=member.avatar)
    profile_embed.timestamp = datetime.utcnow()
    profile_embed.set_footer(
        text=f'Requested by {author.display_name}',
        icon_url=author.avatar if author.avatar else None
    )
    return profile_embed
