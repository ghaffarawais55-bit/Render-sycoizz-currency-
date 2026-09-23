import sqlite3
import os

# Create persistent partition fallback target local context directory
os.makedirs("/data", exist_ok=True)
DB_PATH = "/data/sycoizz_rpg.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trainers (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 1000,
            weapon_tier INTEGER DEFAULT 1,
            weapon_rarity TEXT DEFAULT 'Common',
            gems_count INTEGER DEFAULT 0,
            gems_rarity TEXT DEFAULT 'Common',
            account_level INTEGER DEFAULT 1,
            experience_points INTEGER DEFAULT 0,
            last_daily TEXT DEFAULT '',
            pets_list TEXT DEFAULT '',
            active_team TEXT DEFAULT '',
            pet_levels TEXT DEFAULT '',
            pet_weapons TEXT DEFAULT '',
            has_starter INTEGER DEFAULT 0,
            has_ultimate_buff INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_player(user_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT balance, weapon_tier, weapon_rarity, gems_count, gems_rarity, 
               account_level, experience_points, last_daily, pets_list, 
               active_team, pet_levels, pet_weapons, has_starter, has_ultimate_buff
        FROM trainers WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        cursor.execute("""
            INSERT INTO trainers (user_id, balance, weapon_tier, weapon_rarity, gems_count, gems_rarity, 
                                  account_level, experience_points, last_daily, pets_list, active_team, 
                                  pet_levels, pet_weapons, has_starter, has_ultimate_buff) 
            VALUES (?, 1000, 1, 'Common', 0, 'Common', 1, 0, '', '', '', '', '', 0, 0)
        """, (user_id,))
        conn.commit()
        conn.close()
        return {
            "balance": 1000, "weapon_tier": 1, "weapon": "Common", "gems": 0, "gem": "Common", 
            "level": 1, "xp": 0, "daily": "", "pets": [], "active_team": [], 
            "pet_lvls": {}, "pet_weapons": {}, "has_starter": 0, "ultimate": 0
        }
    conn.close()
    
    lvl_dict = {}
    if row[10]:
        for pair in row[10].split(","):
            if ":" in pair:
                k, v = pair.split(":")
                lvl_dict[k] = int(v)

    weap_dict = {}
    if row[11]:
        for pair in row[11].split(","):
            if ":" in pair:
                k, v = pair.split(":")
                weap_dict[k] = v

    return {
        "balance": row[0], "weapon_tier": row[1], "weapon": row[2],
        "gems": row[3], "gem": row[4], "level": row[5], "xp": row[6],
        "daily": row[7], "pets": [p for p in row[8].split(",") if p],
        "active_team": [t for t in row[9].split(",") if t.strip()],
        "pet_lvls": lvl_dict, "pet_weapons": weap_dict, "has_starter": row[12], "ultimate": row[13]
    }

def save_player(user_id: int, p: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    pets_string = ",".join(p.get("pets", []))
    team_string = ",".join(p.get("active_team", []))
    lvl_string = ",".join([f"{k}:{v}" for k, v in p.get("pet_lvls", {}).items()])
    weap_string = ",".join([f"{k}:{v}" for k, v in p.get("pet_weapons", {}).items()])
    
    cursor.execute("""
        UPDATE trainers SET balance = ?, weapon_tier = ?, weapon_rarity = ?, gems_count = ?, gems_rarity = ?, 
                            account_level = ?, experience_points = ?, last_daily = ?, pets_list = ?, active_team = ?, 
                            pet_levels = ?, pet_weapons = ?, has_starter = ?, has_ultimate_buff = ?
        WHERE user_id = ?
    """, (
        p.get("balance", 0), p.get("weapon_tier", 1), p.get("weapon", "Common"), 
        p.get("gems", 0), p.get("gem", "Common"), p.get("level", 1), p.get("xp", 0), 
        p.get("daily", ""), pets_string, team_string, lvl_string, weap_string, 
        p.get("has_starter", 0), p.get("ultimate", 0), user_id
    ))
    conn.commit()
    conn.close()
  
