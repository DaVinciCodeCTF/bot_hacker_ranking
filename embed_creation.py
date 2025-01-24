from datetime import datetime

import discord

from database.models import DailyUserData, User


class PlatformInfo:
    def __init__(self, name: str, short_name: str, logo: str, color: int, profile: str, emoji_name: str):
        self.name: str = name
        self.short_name: str = short_name
        self.logo: str = logo
        self.color: int = color
        self.profile: str = profile
        self.emoji_name: str = emoji_name


help_fields: list[dict] = [
    {
        'name': 'Display this message',
        'value': '`/help`\n\u200b',
    },
    {
        'name': 'Register you to the bot under the given pseudo',
        'value': '`/register <pseudo>[required]`\n\u200b',
    },
    {
        'name': 'After registering, update your profile with the given ids',
        'value': '`/update <pseudo>[opt] <htb_id>[opt] <rm_id>[opt] <thm_id>[opt] <birthday>[opt]`\n'
                 '• htb_id: [sign in](https://app.hackthebox.com/login) > [profile]('
                 'https://app.hackthebox.com/profile/overview) > #ID, next to your pseudo\n'
                 '• rm_id: [sign in](https://www.root-me.org/) > [profile]('
                 'https://www.root-me.org/?page=preferences&lang=en) > `uid` field, under `Modify my parameters`\n'
                 '• thm_id: [sign in](https://tryhackme.com/login) > [profile](https://tryhackme.com/profile) >\n '
                 '• birthday:  > dd/mm/yyyy\n'
                 '`username` field\n\u200b',
    },
    {
        'name': 'Display the profile of a user, or yours if no user is given',
        'value': '`/profile <user>[opt]`\n\u200b',
    },
    {
        'name': 'Display the leaderboard of the given platform',
        'value': '`/leaderboard <platform>(htb|rm|thm)[required]`',
    }
]

platforms: dict[str, PlatformInfo] = {
    'htb': PlatformInfo(
        name='HackTheBox',
        short_name='htb',
        logo='https://yt3.googleusercontent.com/ytc/APkrFKabtklDH7Goj_UUWqeKXVV6uN4_fGMQIc-v5hfR6w=s900-c-k'
             '-c0x00ffffff-no-rj',
        color=0x9fef00,
        profile='https://app.hackthebox.com/users/',
        emoji_name='HTB_logo',
    ),
    'rm': PlatformInfo(
        name='RootMe',
        short_name='rm',
        logo='https://pro.root-me.org/squelettes/images/RMP_logo_blanc.png',
        color=0xe00911,
        profile='https://www.root-me.org/',
        emoji_name='RM_logo',
    ),
    'thm': PlatformInfo(
        name='TryHackMe',
        short_name='thm',
        logo='https://pbs.twimg.com/profile_images/1478793060607832067/xGV-V2B8_400x400.jpg',
        color=0xffffff,
        profile='https://tryhackme.com/p/',
        emoji_name='THM_logo',
    )
}


def create_help_embed(author: discord.Member, organization_name: str) -> discord.Embed:
    """
    Create the help embed
    :param author: discord.Member, author of the command
    :param organization_name: str, organization name
    :return: discord.Embed, help embed
    """
    help_embed = discord.Embed(
        title=f'{organization_name} bot help',
        description=('Here\'s a list of the available commands. '
                     'Use `/help <command>` to get more information about a specific command. 🔍\n\u200b'),
        colour=discord.Colour.light_gray()
    )
    for field in help_fields:
        help_embed.add_field(name=field['name'], value=field['value'], inline=False)

    help_embed.timestamp = datetime.utcnow()
    help_embed.set_footer(
        text=f'Requested by {author.display_name}',
        icon_url=author.avatar if author.avatar else None
    )
    return help_embed


def get_ranking_emoji(rank: int) -> str:
    """
    Get the emoji corresponding to the rank
    :param rank: int, rank of the user
    :return: str, emoji corresponding to the rank
    """
    ranking_emoji: dict = {
        1: ':first_place:',
        2: ':second_place:',
        3: ':third_place:'
    }
    return ranking_emoji[rank] if rank in ranking_emoji.keys() else f'{rank}.'


def build_user_stats(user: dict, platform_info: PlatformInfo) -> str:
    """
    Build and return the stats string for a user.
    :param user: dict, user data from the leaderboard list
    :param platform_info: PlatformInfo, information about the platform
    :return: str, formatted stats string
    """
    platform_id = user['platform_id']
    global_rank = user['platform_global_rank']
    score = user['platform_score']
    score_evolution = user['score_evolution']
    score_display = 'Score' if platform_info.name in ['HackTheBox', 'RootMe'] else 'Rooms'

    stats = f'[+]({platform_info.profile}{platform_id}) '
    if platform_info.name == 'RootMe' and platform_id.startswith('?'):
        stats = f'[+](https://www.root-me.org/?page=recherche&lang=en&recherche={platform_id[1:]}) '
    stats += f'Global rank: `#{global_rank}` - {score_display}: `{score}` '

    if score_evolution > 0:
        stats += f'[+{score_evolution} :crossed_swords:]'
    elif score_evolution < 0:
        stats += f'[-{abs(score_evolution)} :shield:]'

    return stats


def build_platform_info(
        db_user: User,
        db_data: DailyUserData,
        db_rank: dict,
        platform: PlatformInfo,
        org_name: str
) -> str:
    """
    Build and return the platform info string for a user.
    :param db_user: User, user from the database
    :param db_data: DailyUserData, daily data from the database
    :param db_rank: dict, rank of the user
    :param platform: PlatformInfo, information about the platform
    :param org_name: str, organization name
    :return: str, formatted platform info string
    """
    platform_s = platform.short_name
    if getattr(db_user, f'{platform_s}_id'):
        platform_rank = db_rank.get(f'{platform_s}_orga_rank', '...')
        rank = getattr(db_data, f'{platform_s}_rank', '...')
        score = getattr(db_data, f'{platform_s}_score' if platform_s in ['htb', 'rm'] else f'{platform_s}_rooms', '...')
        user_id = getattr(db_user, f'{platform_s}_id', '...')
        user_n = getattr(db_user, f'{platform_s}_id' if platform_s in ['htb', 'thm'] else f'{platform_s}_name', '...')
        user_link = f'{platform.profile}{user_n}'
        if platform.name == 'RootMe' and user_n.startswith('?'):
            user_link = f'https://www.root-me.org/?page=recherche&lang=en&recherche={user_n[1:]}'
        return ('-----------------\n'
                f'{org_name} rank: `#{platform_rank if platform_rank else "..."}`\n\n'
                f'Rank: `#{rank if rank else "..."}`\n'
                f'{"Rooms" if platform_s == "thm" else "Score"}: `{score if score else "..."}`\n\n'
                f'ID: [{user_id}]({user_link})\n'
                '-----------------')
    return ''


def create_leaderboard_embed(
        leaderboard_list: list[dict],
        platform: str,
        author: discord.Member,
        organization_name: str
) -> discord.Embed:
    """
    Create the leaderboard embed
    :param leaderboard_list: list[dict], list of users to display
    :param platform: str, platform to display the leaderboard of
    :param author: discord.Member, author of the command
    :param organization_name: str, organization name
    :return: discord.Embed, leaderboard embed
    """

    platform_info: PlatformInfo = platforms[platform]
    leaderboard_embed = discord.Embed(
        title=f'{organization_name} {platform_info.name} leaderboard',
        description=('Here\'s a snapshot of hacking accomplishments across various platforms. '
                     'Use `/leaderboard` to explore more leaderboards. 🔍\n\u200b'),
        colour=platform_info.color
    )

    for user in leaderboard_list:
        if user['platform_score'] == 0:
            continue
        username: str = f'{get_ranking_emoji(user["platform_rank"])} {user["username"]}'
        stats: str = build_user_stats(user, platform_info)
        leaderboard_embed.add_field(name=username, value=stats, inline=False)

    leaderboard_embed.set_thumbnail(url=platform_info.logo)
    leaderboard_embed.timestamp = datetime.utcnow()
    leaderboard_embed.set_footer(
        text=f'Requested by {author.display_name}',
        icon_url=author.avatar if author.avatar else None
    )
    return leaderboard_embed


def create_profile_embed(
        db_user: User,
        db_data: DailyUserData,
        db_rank: dict,
        author: discord.Member,
        member: discord.Member,
        guild_emojis: dict,
        organization_name: str
) -> discord.Embed:
    """
    Create the profile embed
    :param db_data: DailyUserData, daily data from the database
    :param db_rank: dict, rank of the user
    :param db_user: User, user from the database
    :param author: discord.Member, author of the command
    :param member: discord.Member, user to display
    :param guild_emojis: dict, guild emojis
    :param organization_name: str, organization name
    :return:
    """
    profile_embed = discord.Embed(
        title=f'Hacker profile of `{db_user.username}`',
        description=('Here\'s a snapshot of hacking accomplishments across various platforms. '
                     'Use `/profile` to explore more profiles. 🔍\n\u200b'),
        colour=discord.Colour.light_gray()
    )
    for platform in platforms.values():
        platform_info = build_platform_info(
            db_user,
            db_data,
            db_rank,
            platform,
            organization_name
        )
        if platform_info:
            profile_embed.add_field(
                name=f'{guild_emojis[platform.emoji_name]} {platform.name}',
                value=platform_info,
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

def create_birthday_embed(member: discord.Member) -> discord.Embed:
    """
    Create a happy birthday embed message.
    :param member: discord.Member, the member whose birthday it is
    :return: discord.Embed, birthday embed
    """
    birthday_embed = discord.Embed(
        title="🎉 Happy Birthday! 🎉",
        description=f"Happy Birthday, {member.display_name}! 🎂🎈",
        colour=discord.Colour.gold()
    )
    birthday_embed.set_thumbnail(url=member.avatar if member.avatar else None)
    birthday_embed.timestamp = datetime.utcnow()
    birthday_embed.set_image(url="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZWN2NHAwbjlyZGFqMjNiYWUycGN0cGszbGdmZzluYzZzbGxtc3Y5ZyZlcD12MV9naWZzX3NlYXJjaCZjdD1n/LTpmRMNSmZgIw/giphy.gif")
    birthday_embed.set_footer(
        text=f"Bon anniversaire ! - L'équipe DVC",
        icon_url=member.guild.icon if member.guild.icon else None
    )
    return birthday_embed