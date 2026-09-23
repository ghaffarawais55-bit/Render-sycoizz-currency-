import random
import discord
import asyncio
from discord.ext import commands
from database import get_player, save_player

class EconomyGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="cf")
    async def coin_flip(self, ctx, amount: str):
        p = get_player(ctx.author.id)
        if p["has_starter"] == 0:
            await ctx.send("❌ | Claim your starter pet first! Type `s start`."); return

        if amount.lower() == "all":
            bet = min(p["balance"], 250000)
        else:
            try: bet = int(amount)
            except ValueError:
                await ctx.send("❌ | Enter a valid number or use `s cf all`."); return

        if bet <= 0:
            await ctx.send("❌ | Wager must be greater than zero."); return
        if bet > 250000:
            await ctx.send("⚠️ | Maximum allowed wager limit is **250,000 sycoizz**."); return
        if p["balance"] < bet:
            await ctx.send(f"❌ | Insufficient funds. Balance: `{p['balance']:,}`."); return

        outcome = random.choice(["heads", "tails"])
        if outcome == "heads":
            p["balance"] += bet
            save_player(ctx.author.id, p)
            emb = discord.Embed(title="🪙 COINFLIP: WIN", description="Landed on **HEADS**!", color=0x4caf50)
            emb.add_field(name="Profit", value=f"**`+{bet:,}`**", inline=True)
        else:
            p["balance"] -= bet
            save_player(ctx.author.id, p)
            emb = discord.Embed(title="🪙 COINFLIP: LOSS", description="Landed on **TAILS**...", color=0xf44336)
            emb.add_field(name="Deficit", value=f"**`-{bet:,}`**", inline=True)
            
        emb.add_field(name="Balance", value=f"`{p['balance']:,}`", inline=True)
        await ctx.send(embed=emb)

    @commands.command(name="slots", aliases=["slot", "se"])
    async def slot_machine_game(self, ctx, amount: int):
        p = get_player(ctx.author.id)
        if p["has_starter"] == 0:
            await ctx.send("❌ | Claim your starter pet first! Type `s start`."); return
        if amount <= 0:
            await ctx.send("❌ | Wager must be greater than zero."); return
        if amount > 250000:
            await ctx.send("⚠️ | Maximum wager capped at **250,000 sycoizz**."); return
        if p["balance"] < amount:
            await ctx.send(f"❌ | Insufficient wallet balance."); return

        emojis = ["🍒", "🍋", "💎", "👑"]
        r1, r2, r3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
        grid = f"🎰 **[ {r1} | {r2} | {r3} ]**"
        
        if r1 == r2 == r3:
            mults = {"🍒": 3, "🍋": 4, "💎": 7, "👑": 15}
            payout = amount * mults.get(r1, 2)
            p["balance"] += payout
            emb = discord.Embed(title="🎰 SLOTS JACKPOT", description=f"{grid}\n\n🎉 Ultimate match!", color=0x4caf50)
            emb.add_field(name="Profit", value=f"**`+{payout:,}`**")
        elif r1 == r2 or r2 == r3 or r1 == r3:
            payout = int(amount * 1.5)
            p["balance"] += payout
            emb = discord.Embed(title="🎰 SLOTS MINOR WIN", description=f"{grid}\n\n✨ Two matched symbols.", color=0x8bc34a)
            emb.add_field(name="Profit", value=f"**`+{payout:,}`**")
        else:
            p["balance"] -= amount
            emb = discord.Embed(title="🎰 SLOTS BLANK", description=f"{grid}\n\n❌ No matching lines found.", color=0xf44336)
            emb.add_field(name="Deficit", value=f"**`-{amount:,}`**")
            
        save_player(ctx.author.id, p)
        emb.add_field(name="Balance", value=f"`{p['balance']:,}`")
        await ctx.send(embed=emb)

    @commands.command(name="roulette", aliases=["rl"])
    async def roulette_game(self, ctx, choice: str, amount: int):
        p = get_player(ctx.author.id)
        choice = choice.lower()
        if p["has_starter"] == 0:
            await ctx.send("❌ | Claim your starter pet first! Type `s start`."); return
        if choice not in ["red", "black", "green"]:
            await ctx.send("❌ | Pick a valid target node color: `red`, `black`, or `green`."); return
        if amount <= 0:
            await ctx.send("❌ | Wager must be greater than zero."); return
        if amount > 250000:
            await ctx.send("⚠️ | Maximum wager capped at **250,000 sycoizz**."); return
        if p["balance"] < amount:
            await ctx.send(f"❌ | Insufficient wallet balance."); return

        spin = random.randint(0, 36)
        win_color = "green" if spin == 0 else ("red" if spin % 2 == 0 else "black")

        if choice == win_color:
            multiplier = 35 if win_color == "green" else 2
            payout = amount * multiplier
            p["balance"] += payout
            emb = discord.Embed(title="🎡 ROULETTE SUCCESS", description=f"The ball settled on **{spin} ({win_color.upper()})**!", color=0x4caf50)
            emb.add_field(name="Profit", value=f"**`+{payout:,}`**")
        else:
            p["balance"] -= amount
            emb = discord.Embed(title="🎡 ROULETTE FAULT", description=f"The ball settled on **{spin} ({win_color.upper()})**.", color=0xf44336)
            emb.add_field(name="Deficit", value=f"**`-{amount:,}`**")
            
        save_player(ctx.author.id, p)
        emb.add_field(name="Balance", value=f"`{p['balance']:,}`")
        await ctx.send(embed=emb)

    @commands.command(name="dice", aliases=["roll"])
    async def dice_game(self, ctx, amount: int):
        p = get_player(ctx.author.id)
        if p["has_starter"] == 0:
            await ctx.send("❌ | Claim your starter pet first! Type `s start`."); return
        if amount <= 0:
            await ctx.send("❌ | Wager must be greater than zero."); return
        if amount > 250000:
            await ctx.send("⚠️ | Maximum wager capped at **250,000 sycoizz**."); return
        if p["balance"] < amount:
            await ctx.send(f"❌ | Insufficient wallet balance."); return

        p_roll = random.randint(1, 6) + random.randint(1, 6)
        b_roll = random.randint(1, 6) + random.randint(1, 6)

        if p_roll > b_roll:
            p["balance"] += amount
            emb = discord.Embed(title="🎲 DICE MATCH: WIN", description=f"🎲 Your Roll: `{p_roll}`\n🤖 Sycoizz Roll: `{b_roll}`\n\nYou won!", color=0x4caf50)
            emb.add_field(name="Profit", value=f"**`+{amount:,}`**")
        elif b_roll > p_roll:
            p["balance"] -= amount
            emb = discord.Embed(title="🎲 DICE MATCH: LOSS", description=f"🎲 Your Roll: `{p_roll}`\n🤖 Sycoizz Roll: `{b_roll}`\n\nYou lost.", color=0xf44336)
            emb.add_field(name="Deficit", value=f"**`-{amount:,}`**")
        else:
            emb = discord.Embed(title="🎲 DICE MATCH: PUSH", description=f"🎲 Your Roll: `{p_roll}`\n🤖 Sycoizz Roll: `{b_roll}`\n\nTied stance.", color=0xff9800)
            emb.add_field(name="Net Payload", value="**`0`**")

        save_player(ctx.author.id, p)
        emb.add_field(name="Balance", value=f"`{p['balance']:,}`")
        await ctx.send(embed=emb)

    # ========================================================
    # 🃏 NEW NODE: HIGH STAKES BLACKJACK ENGINE
    # ========================================================
    @commands.command(name="blackjack", aliases=["bj"])
    async def blackjack_game(self, ctx, amount: int):
        p = get_player(ctx.author.id)
        if p["has_starter"] == 0:
            await ctx.send("❌ | Claim your starter pet first! Type `s start`."); return
        if amount <= 0 or amount > 250000:
            await ctx.send("❌ | Wager entry invalid or exceeds **250,000 sycoizz**."); return
        if p["balance"] < amount:
            await ctx.send("❌ | Insufficient matrix liquid balance."); return

        def calc_hand(hand):
            val = 0
            aces = 0
            for card in hand:
                if card in ["J", "Q", "K"]: val += 10
                elif card == "A": aces += 1; val += 11
                else: val += int(card)
            while val > 21 and aces:
                val -= 10
                aces -= 1
            return val

        deck = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"] * 4
        p_hand = [random.choice(deck), random.choice(deck)]
        d_hand = [random.choice(deck), random.choice(deck)]

        msg = await ctx.send(f"🃏 **Blackjack Match** | Hand: {p_hand} (`{calc_hand(p_hand)}`) vs Dealer: [{d_hand[0]}, ❓]\nType `hit` or `stand`.")

        def check(m): return m.author.id == ctx.author.id and m.content.lower() in ["hit", "stand"] and m.channel.id == ctx.channel.id

        while calc_hand(p_hand) < 21:
            try:
                choice = await self.bot.wait_for("message", check=check, timeout=20.0)
                if choice.content.lower() == "hit":
                    p_hand.append(random.choice(deck))
                    if calc_hand(p_hand) > 21: break
                    await msg.edit(content=f"🃏 **Blackjack** | Hand: {p_hand} (`{calc_hand(p_hand)}`) vs Dealer: [{d_hand[0]}, ❓]\nType `hit` or `stand`.")
                else: break
            except asyncio.TimeoutError: break

        p_score = calc_hand(p_hand)
        if p_score > 21:
            p["balance"] -= amount
            await ctx.send(f"💥 BUSTED! Your Hand scored `{p_score}`. Deficit: `-{amount:,}` sycoizz.")
        else:
            while calc_hand(d_hand) < 17: d_hand.append(random.choice(deck))
            d_score = calc_hand(d_hand)
            if d_score > 21 or p_score > d_score:
                p["balance"] += amount
                await ctx.send(f"🎉 WIN! Hand: `{p_score}` vs Dealer Hand: `{d_score}`. Profit: `+{amount:,}` sycoizz!")
            elif d_score > p_score:
                p["balance"] -= amount
                await ctx.send(f"❌ LOSS! Hand: `{p_score}` vs Dealer Hand: `{d_score}`. Deficit: `-{amount:,}` sycoizz.")
            else:
                await ctx.send(f"🤝 PUSH! Tied score at `{p_score}`.")
  
