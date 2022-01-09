from .analyzer import Analyzer

def setup(bot):
    cog = Analyzer(bot=bot)
    bot.add_cog(cog)
