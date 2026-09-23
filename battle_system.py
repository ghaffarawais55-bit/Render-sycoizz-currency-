import random

def calculate_player_damage(player_data: dict) -> int:
    """
    Handles the entire weapon progression tiered damage mapping logic.
    Keeps main.py clean and easily extendable for future updates.
    """
    # 🎲 Set your base random attack swing roll range
    dmg_base = random.randint(15, 30)
    
    # ⚔️ Dynamic progression inventory modifier lookups
    weapon_rarity = player_data.get("weapon", "Common")
    
    if weapon_rarity == "Uncommon": 
        dmg_base += 5
    elif weapon_rarity == "Rare": 
        dmg_base += 12
    elif weapon_rarity == "Legendary": 
        dmg_base += 25
    elif weapon_rarity == "Mythic": 
        dmg_base += 45
    elif weapon_rarity == "Sycoizz Overlord": 
        dmg_base += 80
        
    # 🆕 You can keep adding new tier entries here forever without cluttering main.py!
    # elif weapon_rarity == "Your New Tier Name":
    #     dmg_base += 120
        
    return dmg_base
  
