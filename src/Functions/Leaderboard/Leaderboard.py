from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands

from utils.guessr.lb import get_all_scores, get_score
from hooks.discord.use_discord import make_embed, get_user, get_user_mention
from utils.bot.utils import bot_make_icon
from const import BOT_COLOR


class Leaderboard(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="lb", description="Shows the current leaderboard.")
    @app_commands.describe(
        user="Targets a user the current server in the leaderboard",
        user_id="Targets a user in the leaderboard by their Discord's id.",
    )
    async def lb(
        self,
        ctx: commands.Context,
        user: Optional[discord.User] = None,
        user_id: Optional[str] = None,
    ):
        await ctx.defer()

        if user:
            user_stats = await get_score(user.id)

            if user_stats == None:
                raise commands.UserNotFound(user.id)
            else:
                easy, medium, hard, veryhard = user_stats["scores"].values()
                elo = sum([easy * 3, medium * 5, hard * 10, veryhard * 15])
                started_at = user_stats["createdStamp"]

                embed = make_embed(
                    description=f"{user.mention} stats",
                    color=user.accent_color or BOT_COLOR,
                )
                embed.add_field(name="ELO", value=elo, inline=False)
                embed.add_field(name="Easy", value=easy, inline=False)
                embed.add_field(name="Medium", value=medium, inline=False)
                embed.add_field(name="Hard", value=hard, inline=False)
                embed.add_field(name="Very Hard", value=veryhard, inline=False)
                embed.add_field(
                    name="Started at", value=f"<t:{started_at}:f>", inline=False
                )
                embed.set_footer(
                    text="Keep playing to improve your stats!",
                    icon_url="attachment://icon.png",
                )
                embed.set_author(name=user.name, icon_url=user.avatar.url)

                await ctx.send(embed=embed, file=bot_make_icon())
        elif user_id:
            user_id_stats = await get_score(user_id)

            if user_id_stats == None:
                raise commands.UserNotFound(user_id)
            else:
                target_user = await get_user(self.bot, user_id)
                target_user_mention = await get_user_mention(self.bot, user_id)
                target_user_color = (
                    target_user.accent_color if target_user != None else BOT_COLOR
                )
                target_user_name = target_user.name if target_user != None else "N/A"
                target_user_avatar = (
                    target_user.avatar.url
                    if target_user != None
                    else "attachment://icon.png"
                )

                easy, medium, hard, veryhard = user_id_stats["scores"].values()
                elo = sum([easy * 3, medium * 5, hard * 10, veryhard * 15])
                started_at = user_id_stats["createdStamp"]

                embed = make_embed(
                    description=f"{target_user_mention} stats",
                    color=target_user_color,
                )
                embed.add_field(name="ELO", value=elo, inline=False)
                embed.add_field(name="Easy", value=easy, inline=False)
                embed.add_field(name="Medium", value=medium, inline=False)
                embed.add_field(name="Hard", value=hard, inline=False)
                embed.add_field(name="Very Hard", value=veryhard, inline=False)
                embed.add_field(
                    name="Started at", value=f"<t:{started_at}:f>", inline=False
                )
                embed.set_footer(
                    text="Keep playing to improve your stats!",
                    icon_url="attachment://icon.png",
                )
                embed.set_author(name=target_user_name, icon_url=target_user_avatar)

                await ctx.send(embed=embed, file=bot_make_icon())
        else:
            users_stats = await get_all_scores()
            sorted_users_stat = sorted(
                users_stats,
                reverse=True,
                key=lambda user_stat: sum(
                    [
                        user_stat["scores"]["Easy"] * 3,
                        user_stat["scores"]["Medium"] * 5,
                        user_stat["scores"]["Hard"] * 10,
                        user_stat["scores"]["Very Hard"] * 15,
                    ]
                ),
            )
            users_stat_entry = []

            for rank, user_stats in enumerate(sorted_users_stat, start=1):
                user_mention = await get_user_mention(self.bot, user_stats["userId"])
                easy, medium, hard, veryhard = user_stats["scores"].values()
                elo = sum([easy * 3, medium * 5, hard * 10, veryhard * 15])

                users_stat_entry.append(f"{rank}. {user_mention} at **{elo}** ELO")

            lb_embed = make_embed(
                "Leaderboard", "\n".join(users_stat_entry) or "Empty :(", BOT_COLOR
            )
            lb_embed.set_footer(
                text=f"There are {len(users_stats)} users in the leaderboard!",
                icon_url="attachment://icon.png",
            )

            await ctx.send(embed=lb_embed, file=bot_make_icon())


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
