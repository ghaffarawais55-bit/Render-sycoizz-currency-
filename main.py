import sys
import types
import os
import random
import asyncio
import discord
from discord.ext import commands
from database import init_db, get_player, save_player
from battle_system import calculate_player_damage  # Clean damage engine link
from aiohttp import web

# Compatibility layer for audioop on modern Python environments
sys.modules['audioop'] = types.ModuleType('audioop')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=["s ", "S ", "s", "S"], intents=intents, help_command=None)

# ========================================================
# 🌐 RENDER PORT BINDING & KEEP ALIVE SERVER
# ========================================================
async def handle_ping(request):
    return web.Response(text="Sycoizz Engine Online")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Keep-Alive Server initialized on port: {port}")

@bot.event
async def on_ready():
    init_db()
    try:
        await bot.load_extension("economy")
        print("📦 Modular Economy Component Linked Successfully.")
    except Exception as e:
        print(f"⚠️ Failed to link modular extension: {e}")
    print("🚀 SYCOIZZ FULL RPG PRO ENGINE ONLINE AND READY")

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    content = message.content
    if content.lower().startswith("s "):
        message.content = "s" + content[1:]
    await bot.process_commands(message)

# ========================================================
# 📖 GENERAL USER MENU DIRECTORY (HELP SYSTEM)
# ========================================================
@bot.command(name="help", aliases=["h", "commands"])
async def sycoizz_help_directory(ctx):
    emb = discord.Embed(title="📜 SYCOIZZ RPG SYSTEM UTILITIES", color=0x00abc9)
    emb.add_field(
        name="🎒 Core RPG Commands", 
        value="• `s start` ─ Claim starter.\n• `s bal` ─ View profile.\n• `s allpets` ─ View inventory.\n• `s battle` ─ Match a wild opponent.\n• `s worldboss` ─ Join Server World Boss Raid.", 
        inline=False
    )
    emb.add_field(
        name="🎲 Gambling Nodes (Max 250k)", 
        value="• `s cf [amount]` ─ Coinflip.\n• `s slots [amount]` ─ Slots.\n• `s roulette [color] [amount]` ─ Roulette.\n• `s dice [amount]` ─ Dice Roll.\n• `s bj [amount]` ─ Blackjack.\n• `s crash [amount]` ─ Crash Curve.", 
        inline=False
    )
    emb.add_field(
        name="🛒 Progression Marketplace", 
        value="• `s shop` ─ View Weaponry & Shards.\n• `s buy_weapon [rarity]` ─ Purchase upgrade tier.\n• `s buy ultimate` ─ Claims overlord module.", 
        inline=False
    )
    await ctx.send(embed=emb)

# ========================================================
# 📊 NEW ACCOUNT PROFILE PROFILE COMMAND (BALANCE SYSTEM)
# ========================================================
@bot.command(name="balance", aliases=["bal", "profile", "money"])
async def user_profile_balance(ctx, target: discord.User = None):
    target_user = target or ctx.author
    p = get_player(target_user.id)
    if p["has_starter"] == 0:
        await ctx.send("❌ | Target profile unregistered."); return

    emb = discord.Embed(title=f"📊 {target_user.name}'s ACCOUNT DATA", color=0x00e676)
    emb.set_thumbnail(url=target_user.display_avatar.url)
    emb.add_field(name="💰 Wallet Balance", value=f"**`{p['balance']:,}` sycoizz**", inline=False)
    xp_needed = p["level"] * 100
    emb.add_field(name="🌟 RPG Statistics", value=f"• **Account Level:** `{p['level']}`\n• **Progression XP:** `{p['xp']}/{xp_needed}`", inline=True)
    
    active_pet = p["active_team"] if isinstance(p["active_team"], str) else (p["active_team"] if p["active_team"] else "None")
    emb.add_field(name="⚔️ Active Loadout", value=f"• **Weapon Rarity:** `{p.get('weapon', 'Common')}`\n• **Combat Partner:** `{active_pet}`\n• **Gems Count:** `{p.get('gems', 0)}` ({p.get('gem', 'Common')})", inline=True)
    await ctx.send(embed=emb)

# ========================================================
# 🎒 STARTER SELECTION & INVENTORY MANAGEMENT
# ========================================================
@bot.command(name="start")
async def claim_starter(ctx):
    p = get_player(ctx.author.id)
    if p["has_starter"] == 1:
        await ctx.send("❌ | Starter companion already claimed!"); return
        
    emb = discord.Embed(title="🌿 CHOOSE YOUR STARTER 🌿", description="Type your choice name:", color=0x4caf50)
    emb.add_field(name="🔥 Charmander", value="High critical damage.", inline=True)
    emb.add_field(name="💧 Squirtle", value="Resilient protection.", inline=True)
    emb.add_field(name="🍃 Bulbasaur", value="Balanced health modifiers.", inline=True)
    await ctx.send(embed=emb)

    def check_choice(m): return m.author.id == ctx.author.id and m.content.lower() in ["charmander", "squirtle", "bulbasaur"] and m.channel.id == ctx.channel.id

    try:
        msg = await bot.wait_for("message", check=check_choice, timeout=30.0)
        chosen = msg.content.lower().capitalize()
        p["pets"].append(chosen)
        p["active_team"] = [chosen]
        p["pet_lvls"][chosen] = 1
        p["has_starter"] = 1
        save_player(ctx.author.id, p)
        await ctx.send(f"🎉 | Adventure Begins! You claimed **{chosen}**!")
    except asyncio.TimeoutError:
        await ctx.send("⏱️ | Selection node expired.")

# ========================================================
# 🛒 SHOP MARKETPLACE UPGRADES
# ========================================================
@bot.command(name="shop")
async def view_rpg_shop(ctx):
    emb = discord.Embed(title="🛒 SYCOIZZ RPG UPGRADE MARKETPLACE", color=0xff9800)
    emb.add_field(name="⚔️ Weapon Tiers (`s buy_weapon [rarity]`)", value="• **Uncommon Edge** ─ `15,000` sycoizz\n• **Rare Edge** ─ `50,000` sycoizz\n• **Legendary Edge** ─ `250,000` sycoizz\n• **Mythic Edge** ─ `1,000,000` sycoizz", inline=False)
    emb.add_field(name="💎 Lucky Socket Items (`s buy shards`)", value="• **Chaos Luck Shards** ─ `75,000` sycoizz\n*Adds +1 Gem to your character data footprint for modifier loops.*", inline=False)
    emb.add_field(name="👑 Premium Endgame Overlord (`s buy ultimate`)", value="• **Ultimate Core Buff** ─ `10,000,000` sycoizz\n*Maximizes item configuration states and unlocks absolute prestige scaling.*", inline=False)
    await ctx.send(embed=emb)

@bot.command(name="buy_weapon")
async def buy_weapon(ctx, rarity: str):
    p = get_player(ctx.author.id)
    rarity = rarity.capitalize()
    prices = {"Uncommon": 15000, "Rare": 50000, "Legendary": 250000, "Mythic": 1000000}
    if rarity not in prices:
        await ctx.send("❌ | Invalid tier selection."); return
    if p["balance"] < prices[rarity]:
        await ctx.send("❌ | Insufficient balance."); return
        
    p["balance"] -= prices[rarity]
    p["weapon"] = rarity
    save_player(ctx.author.id, p)
    await ctx.send(f"⚔️ | Upgraded weapon tier asset to **{rarity} Edge**!")

@bot.command(name="buy")
async def purchase_shop_item(ctx, *, item: str):
    p = get_player(ctx.author.id)
    item = item.lower()
    if item == "ultimate":
        if p["balance"] < 10000000:
            await ctx.send("❌ | Ultimate asset requires **10,000,000** sycoizz."); return
        p["balance"] -= 10000000
        p["weapon"] = "Sycoizz Overlord"
        p["ultimate"] = 1
        save_player(ctx.author.id, p)
        await ctx.send("👑 | Configured account state to: **Ultimate Sycoizz Bot Overlord Tier**!"); return
    elif item in ["shards", "shard"]:
        if p["balance"] < 75000:
            await ctx.send("❌ | Chaos Luck Shards require **75,000** sycoizz."); return
        p["balance"] -= 75000
        p["gems"] = p.get("gems", 0) + 1
        p["gem"] = "Chaos Refined"
        save_player(ctx.author.id, p)
        await ctx.send("💎 | Chaos Luck Shards bound successfully! Your luck metrics upgraded."); return
    await ctx.send("❌ | Item name unknown. Use `s shop` to view names.")

@bot.command(name="allpets", aliases=["vault"])
async def all_pets_command(ctx):
    p = get_player(ctx.author.id)
    if p["has_starter"] == 0:
        await ctx.send("❌ | Claim your starter pet first! Type `s start`."); return
    if not p["pets"]:
        await ctx.send("🎒 | Your inventory vault is empty."); return
    counts = {}
    for pet in p["pets"]: counts[pet] = counts.get(pet, 0) + 1
    desc = "\n".join([f"• **{pet}** x{qty}" for pet, qty in counts.items()])
    emb = discord.Embed(title=f"🎒 {ctx.author.name}'s Vault", description=desc, color=0x2196f3)
    await ctx.send(embed=emb)

# ========================================================
# ⚔️ TURN-BASED WILD BATTLE FRAMEWORK
# ========================================================
@bot.command(name="battle")
async def wild_battle_combat(ctx):
    p = get_player(ctx.author.id)
    if p["has_starter"] == 0:
        await ctx.send("❌ | You need a starter companion to engage in combat matrices."); return

    active_pet = p["active_team"] if p["active_team"] else "Starter Unit"
    opponents = ["Wild Rattata", "Wild Pidgey", "Wild Zubat", "Wild Geodude"]
    enemy = random.choice(opponents)
    
    p_hp, e_hp = 100, 100
    msg = await ctx.send(f"⚔️ **COMBAT ENCOUNTER:** Trainer throws out **{active_pet}** against **{enemy}**!\nYour HP: `100` | Enemy HP: `100` \nType `attack` to execute standard damage loop.")

    def check(m): return m.author.id == ctx.author.id and m.content.lower() == "attack" and m.channel.id == ctx.channel.id

    while p_hp > 0 and e_hp > 0:
        try:
            await bot.wait_for("message", check=check, timeout=20.0)
            
            # Calculates damage dynamically via the dedicated utility system function
            dmg_base = calculate_player_damage(p)


