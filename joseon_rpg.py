#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import random
import sys
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple


# 게임 상수 정의
class GameConstants:
    SAVE_FILE_PATH = "joseon_rpg_save.json"
    VERSION = "1.0.0"


class Colors:
    """ANSI 색상 코드"""
    RESET = '\033[0m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


class Origin(Enum):
    """캐릭터 출신"""
    FALLEN_NOBLE = "몰락한 양반"
    BANDIT_OUTCAST = "도적단 낙오자"
    WAR_ORPHAN = "전쟁 고아"


class Faction(Enum):
    """세력"""
    PALACE = "궁"
    CULT = "밀교파"
    SHADOW_GUILD = "암시회"
    PEOPLE_ALLIANCE = "백성연맹"
    FOREIGNER_UNION = "이방인연합"
    NEUTRAL = "중립"


class JobPath(Enum):
    """직업 경로"""
    WANDERER = "방랑자"
    WARRIOR_APPRENTICE = "무사 도제"
    WARRIOR = "정식 무사"
    BLADE_MASTER = "무형검사"
    SWORD_DEMON = "검극귀"


class ItemType(Enum):
    """아이템 종류"""
    WEAPON = "무기"
    ARMOR = "의복"
    SPECIAL = "특수 아이템"
    STORY = "서사 아이템"


class CombatAction(Enum):
    """전투 행동"""
    ATTACK = "공격"
    DODGE = "회피"
    DEFEND = "방어"
    AMBUSH = "기습"
    SKILL = "기술"


class Item:
    """아이템 클래스"""
    def __init__(self, name: str, item_type: ItemType, description: str, 
                 power: int = 0, defense: int = 0, special_effect: str = ""):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.power = power
        self.defense = defense
        self.special_effect = special_effect
        self.enhancement_level = 0
        self.durability = 100
        
    def enhance(self) -> Tuple[bool, str]:
        """아이템 강화 - 개선된 시스템"""
        success_rate = 80 - (self.enhancement_level * 15)
        roll = random.randint(1, 100)
        
        if roll <= success_rate:
            # 성공
            self.enhancement_level += 1
            self.power = int(self.power * 1.2)
            self.defense = int(self.defense * 1.2)
            return True, "normal"
        else:
            # 실패
            if roll <= success_rate + 10:
                # 일반 실패
                return False, "normal"
            elif roll <= success_rate + 20:
                # 내구도 손상
                self.durability -= 30
                return False, "damaged"
            else:
                # 파괴 또는 변이
                if random.randint(1, 100) <= 50:
                    # 파괴
                    self.durability = 0
                    return False, "destroyed"
                else:
                    # 저주/변이
                    self.name = f"저주받은 {self.name}"
                    self.special_effect = "착용자의 정신력을 갉아먹는다"
                    self.power = int(self.power * 1.5)
                    self.defense = int(self.defense * 0.5)
                    return False, "cursed"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "item_type": self.item_type.value,
            "description": self.description,
            "power": self.power,
            "defense": self.defense,
            "special_effect": self.special_effect,
            "enhancement_level": self.enhancement_level,
            "durability": self.durability
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        item = cls(
            name=data["name"],
            item_type=ItemType(data["item_type"]),
            description=data["description"],
            power=data["power"],
            defense=data["defense"],
            special_effect=data["special_effect"]
        )
        item.enhancement_level = data["enhancement_level"]
        item.durability = data["durability"]
        return item


class Skill:
    """기술 클래스"""
    def __init__(self, name: str, damage_multiplier: float, stamina_cost: int, 
                 focus_cost: int, description: str):
        self.name = name
        self.damage_multiplier = damage_multiplier
        self.stamina_cost = stamina_cost
        self.focus_cost = focus_cost
        self.description = description
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "damage_multiplier": self.damage_multiplier,
            "stamina_cost": self.stamina_cost,
            "focus_cost": self.focus_cost,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Skill':
        return cls(**data)


class NPC:
    """NPC 클래스"""
    def __init__(self, name: str, faction: Faction, initial_trust: int = 50):
        self.name = name
        self.faction = faction
        self.trust = initial_trust
        self.memories = []
        self.is_hostile = False
        
    def remember_action(self, action: str):
        """플레이어 행동 기억"""
        self.memories.append({
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
        
    def adjust_trust(self, amount: int):
        """신뢰도 조정"""
        self.trust = max(0, min(100, self.trust + amount))
        if self.trust < 20:
            self.is_hostile = True
            
    def get_reaction(self) -> str:
        """현재 신뢰도에 따른 반응"""
        if self.is_hostile:
            return f"{self.name}이(가) 적대적으로 바라봅니다."
        elif self.trust >= 80:
            return f"{self.name}이(가) 당신을 신뢰하는 눈빛으로 바라봅니다."
        elif self.trust >= 50:
            return f"{self.name}이(가) 중립적인 표정을 짓습니다."
        else:
            return f"{self.name}이(가) 의심스러운 눈초리로 당신을 살핍니다."
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "faction": self.faction.value,
            "trust": self.trust,
            "memories": self.memories,
            "is_hostile": self.is_hostile
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'NPC':
        npc = cls(
            name=data["name"],
            faction=Faction(data["faction"]),
            initial_trust=data["trust"]
        )
        npc.memories = data["memories"]
        npc.is_hostile = data["is_hostile"]
        return npc


class Location:
    """장소 클래스"""
    def __init__(self, name: str, description: str, faction: Faction, 
                 danger_level: int = 1, is_locked: bool = False):
        self.name = name
        self.description = description
        self.faction = faction
        self.danger_level = danger_level
        self.is_locked = is_locked
        self.npcs = []
        self.items = []
        self.connected_locations = []
        
    def add_npc(self, npc: NPC):
        self.npcs.append(npc)
        
    def add_item(self, item: Item):
        self.items.append(item)
        
    def connect_location(self, location_name: str):
        if location_name not in self.connected_locations:
            self.connected_locations.append(location_name)
            
    def unlock(self):
        self.is_locked = False


class Character:
    """플레이어 캐릭터 클래스"""
    def __init__(self, name: str, origin: Origin):
        self.name = name
        self.origin = origin
        self.job = JobPath.WANDERER
        self.faction_affinity = self._get_initial_faction(origin)
        
        # 능력치
        self.max_health = 100
        self.health = self.max_health
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.max_focus = 100
        self.focus = self.max_focus
        self.defense = 10
        self.sanity = 100
        
        # 전투 능력치
        self.base_attack = self._get_initial_attack(origin)
        self.base_defense = self._get_initial_defense(origin)
        
        # 인벤토리
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.skills = []
        self.money = self._get_initial_money(origin)  # 화폐 추가
        
        # 경험 및 성장
        self.experience = 0
        self.level = 1
        
        # 전투 상태
        self.in_combat = False
        self.turn_action_taken = False
        
        # 상태 이상
        self.is_cursed = False  # 저주 상태
        self.nightmares = []    # 악몽/환각
        self.buffs = []         # 버프 리스트
        self.debuffs = []       # 디버프 리스트
        
    def _get_initial_faction(self, origin: Origin) -> Dict[Faction, int]:
        """출신에 따른 초기 세력 친화도"""
        if origin == Origin.FALLEN_NOBLE:
            return {
                Faction.PALACE: 60,
                Faction.CULT: 30,
                Faction.SHADOW_GUILD: 40,
                Faction.PEOPLE_ALLIANCE: 20,
                Faction.FOREIGNER_UNION: 30
            }
        elif origin == Origin.BANDIT_OUTCAST:
            return {
                Faction.PALACE: 10,
                Faction.CULT: 40,
                Faction.SHADOW_GUILD: 70,
                Faction.PEOPLE_ALLIANCE: 50,
                Faction.FOREIGNER_UNION: 60
            }
        else:  # WAR_ORPHAN
            return {
                Faction.PALACE: 20,
                Faction.CULT: 50,
                Faction.SHADOW_GUILD: 50,
                Faction.PEOPLE_ALLIANCE: 70,
                Faction.FOREIGNER_UNION: 40
            }
    
    def _get_initial_attack(self, origin: Origin) -> int:
        """출신에 따른 초기 공격력"""
        if origin == Origin.FALLEN_NOBLE:
            return 15
        elif origin == Origin.BANDIT_OUTCAST:
            return 20
        else:  # WAR_ORPHAN
            return 12
            
    def _get_initial_defense(self, origin: Origin) -> int:
        """출신에 따른 초기 방어력"""
        if origin == Origin.FALLEN_NOBLE:
            return 12
        elif origin == Origin.BANDIT_OUTCAST:
            return 10
        else:  # WAR_ORPHAN
            return 15
    
    def _get_initial_money(self, origin: Origin) -> int:
        """출신에 따른 초기 자금"""
        if origin == Origin.FALLEN_NOBLE:
            return 100  # 약간의 재산 보유
        elif origin == Origin.BANDIT_OUTCAST:
            return 50   # 도적 생활로 모은 돈
        else:  # WAR_ORPHAN
            return 10   # 거의 없음
    
    def take_damage(self, damage: int):
        """데미지 받기"""
        actual_damage = max(0, damage - self.defense)
        self.health -= actual_damage
        return actual_damage
        
    def heal(self, amount: int):
        """체력 회복"""
        self.health = min(self.max_health, self.health + amount)
        
    def use_stamina(self, amount: int) -> bool:
        """기력 사용"""
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
        
    def use_focus(self, amount: int) -> bool:
        """집중도 사용"""
        if self.focus >= amount:
            self.focus -= amount
            return True
        return False
        
    def rest(self):
        """휴식"""
        self.stamina = min(self.max_stamina, self.stamina + 30)
        self.focus = min(self.max_focus, self.focus + 20)
        self.health = min(self.max_health, self.health + 10)
        
    def add_item(self, item: Item):
        """아이템 획득"""
        self.inventory.append(item)
        
    def equip_weapon(self, weapon: Item):
        """무기 장착"""
        if weapon.item_type == ItemType.WEAPON and weapon.durability > 0:
            self.equipped_weapon = weapon
            
    def equip_armor(self, armor: Item):
        """방어구 장착"""
        if armor.item_type == ItemType.ARMOR and armor.durability > 0:
            self.equipped_armor = armor
            
    def learn_skill(self, skill: Skill):
        """기술 습득"""
        if skill not in self.skills:
            self.skills.append(skill)
            
    def get_total_attack(self) -> int:
        """총 공격력 계산"""
        weapon_power = self.equipped_weapon.power if self.equipped_weapon else 0
        return self.base_attack + weapon_power
        
    def get_total_defense(self) -> int:
        """총 방어력 계산"""
        armor_defense = self.equipped_armor.defense if self.equipped_armor else 0
        base_total = self.base_defense + armor_defense
        
        # 버프 적용
        for buff in self.buffs:
            if buff["type"] == "defense":
                base_total += buff["value"]
                
        return base_total
        
    def get_dodge_chance(self) -> int:
        """회피율 계산"""
        base_dodge = 10 + (self.focus // 20)
        
        # 회피 버프 적용
        for buff in self.buffs:
            if buff["type"] == "dodge":
                base_dodge += buff["value"]
                
        return min(base_dodge, 75)  # 최대 75%
        
    def advance_job(self):
        """직업 승급"""
        job_progression = {
            JobPath.WANDERER: JobPath.WARRIOR_APPRENTICE,
            JobPath.WARRIOR_APPRENTICE: JobPath.WARRIOR,
            JobPath.WARRIOR: JobPath.BLADE_MASTER,
            JobPath.BLADE_MASTER: JobPath.SWORD_DEMON
        }
        
        if self.job in job_progression and self.level >= (list(JobPath).index(self.job) + 1) * 5:
            self.job = job_progression[self.job]
            self.max_health += 20
            self.max_stamina += 20
            self.max_focus += 20
            self.base_attack += 5
            self.base_defense += 5
            return True
        return False
    
    def gain_experience(self, amount: int):
        """경험치 획득"""
        self.experience += amount
        while self.experience >= self.level * 100:
            self.experience -= self.level * 100
            self.level += 1
            self.max_health += 10
            self.max_stamina += 10
            self.max_focus += 10
            self.base_attack += 2
            self.base_defense += 2
            
    def to_dict(self) -> dict:
        """저장용 딕셔너리 변환"""
        return {
            "name": self.name,
            "origin": self.origin.value,
            "job": self.job.value,
            "faction_affinity": {k.value: v for k, v in self.faction_affinity.items()},
            "stats": {
                "max_health": self.max_health,
                "health": self.health,
                "max_stamina": self.max_stamina,
                "stamina": self.stamina,
                "max_focus": self.max_focus,
                "focus": self.focus,
                "defense": self.defense,
                "sanity": self.sanity,
                "base_attack": self.base_attack,
                "base_defense": self.base_defense
            },
            "inventory": [item.to_dict() for item in self.inventory],
            "equipped_weapon": self.equipped_weapon.to_dict() if self.equipped_weapon else None,
            "equipped_armor": self.equipped_armor.to_dict() if self.equipped_armor else None,
            "skills": [skill.to_dict() for skill in self.skills],
            "experience": self.experience,
            "level": self.level,
            "money": self.money,
            "is_cursed": self.is_cursed,
            "nightmares": self.nightmares,
            "buffs": self.buffs,
            "debuffs": self.debuffs
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Character':
        """딕셔너리에서 캐릭터 복원"""
        character = cls(data["name"], Origin(data["origin"]))
        character.job = JobPath(data["job"])
        character.faction_affinity = {Faction(k): v for k, v in data["faction_affinity"].items()}
        
        stats = data["stats"]
        character.max_health = stats["max_health"]
        character.health = stats["health"]
        character.max_stamina = stats["max_stamina"]
        character.stamina = stats["stamina"]
        character.max_focus = stats["max_focus"]
        character.focus = stats["focus"]
        character.defense = stats["defense"]
        character.sanity = stats["sanity"]
        character.base_attack = stats["base_attack"]
        character.base_defense = stats["base_defense"]
        
        character.inventory = [Item.from_dict(item) for item in data["inventory"]]
        if data["equipped_weapon"]:
            character.equipped_weapon = Item.from_dict(data["equipped_weapon"])
        if data["equipped_armor"]:
            character.equipped_armor = Item.from_dict(data["equipped_armor"])
            
        character.skills = [Skill.from_dict(skill) for skill in data["skills"]]
        character.experience = data["experience"]
        character.level = data["level"]
        character.money = data.get("money", 50)  # 구버전 호환성
        character.is_cursed = data.get("is_cursed", False)
        character.nightmares = data.get("nightmares", [])
        character.buffs = data.get("buffs", [])
        character.debuffs = data.get("debuffs", [])
        
        return character


class Enemy:
    """적 클래스"""
    def __init__(self, name: str, health: int, attack: int, defense: int, 
                 experience_reward: int, loot: List[Item] = None, 
                 combat_patterns: List[str] = None):
        self.name = name
        self.max_health = health
        self.health = health
        self.attack = attack
        self.defense = defense
        self.experience_reward = experience_reward
        self.loot = loot or []
        self.combat_patterns = combat_patterns or ["attack"]
        self.rage_mode = False
        self.stance = "normal"  # normal, defensive, aggressive
        
    def take_damage(self, damage: int) -> int:
        """데미지 받기"""
        actual_damage = max(0, damage - self.defense)
        self.health -= actual_damage
        
        # 체력이 30% 이하로 떨어지면 분노 모드
        if self.health <= self.max_health * 0.3 and not self.rage_mode:
            self.rage_mode = True
            self.attack = int(self.attack * 1.5)
            
        return actual_damage
        
    def is_alive(self) -> bool:
        """생존 여부"""
        return self.health > 0
        
    def get_attack_damage(self) -> int:
        """공격 데미지 계산"""
        base_damage = self.attack + random.randint(-5, 5)
        if self.rage_mode:
            base_damage = int(base_damage * 1.3)
        if self.stance == "aggressive":
            base_damage = int(base_damage * 1.2)
        elif self.stance == "defensive":
            base_damage = int(base_damage * 0.8)
        return base_damage
        
    def choose_action(self, player_last_action: str = None) -> str:
        """AI 행동 선택"""
        if self.rage_mode:
            # 분노 모드에서는 공격적
            return random.choice(["strong_attack", "attack", "attack"])
            
        if player_last_action == "defend":
            # 플레이어가 방어 중이면 강공격
            return "strong_attack"
        elif player_last_action == "dodge":
            # 플레이어가 회피 중이면 견제
            return "feint"
            
        # 일반 패턴
        if len(self.combat_patterns) > 0:
            return random.choice(self.combat_patterns)
        return "attack"


class Combat:
    """전투 시스템"""
    def __init__(self, player: Character, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.turn_count = 0
        self.combat_log = []
        self.is_active = True
        self.player_last_action = None
        
    def player_attack(self) -> str:
        """플레이어 공격"""
        if self.player.turn_action_taken:
            return "이미 이번 턴에 행동했습니다!"
            
        self.player.turn_action_taken = True
        self.player_last_action = "attack"
        
        # 스태미나 체크
        stamina_cost = 10
        if self.player.stamina < stamina_cost:
            return "기력이 부족합니다!"
            
        self.player.use_stamina(stamina_cost)
        
        # 명중률 계산 (집중도와 피로도 영향)
        hit_chance = 70 + (self.player.focus // 10) - ((100 - self.player.stamina) // 20)
        
        if random.randint(1, 100) <= hit_chance:
            damage = self.player.get_total_attack() + random.randint(-5, 10)
            actual_damage = self.enemy.take_damage(damage)
            
            # 무기 내구도 감소
            if self.player.equipped_weapon:
                self.player.equipped_weapon.durability -= 1
                if self.player.equipped_weapon.durability <= 0:
                    return f"공격 성공! {actual_damage}의 피해를 입혔습니다.\n{Colors.RED}무기가 파괴되었습니다!{Colors.RESET}"
                    
            # 적 분노 모드 체크
            if self.enemy.rage_mode and not hasattr(self, 'rage_announced'):
                self.rage_announced = True
                return f"공격 성공! {actual_damage}의 피해를 입혔습니다.\n{Colors.RED}{self.enemy.name}이(가) 분노합니다!{Colors.RESET}"
                
            return f"공격 성공! {actual_damage}의 피해를 입혔습니다. (적 체력: {self.enemy.health}/{self.enemy.max_health})"
        else:
            return "공격이 빗나갔습니다!"
            
    def player_dodge(self) -> str:
        """플레이어 회피"""
        if self.player.turn_action_taken:
            return "이미 이번 턴에 행동했습니다!"
            
        self.player.turn_action_taken = True
        self.player_last_action = "dodge"
        
        if not self.player.use_stamina(15):
            return "기력이 부족합니다!"
            
        # 회피 버프 추가 (2턴 지속)
        self.player.buffs.append({"type": "dodge", "turns": 2, "value": 30})
        return "회피 자세를 취했습니다. 다음 공격을 피할 확률이 증가합니다."
        
    def player_defend(self) -> str:
        """플레이어 방어"""
        if self.player.turn_action_taken:
            return "이미 이번 턴에 행동했습니다!"
            
        self.player.turn_action_taken = True
        self.player_last_action = "defend"
        
        # 방어 버프 추가 (1턴 지속)
        self.player.buffs.append({"type": "defense", "turns": 1, "value": 15})
        self.player.stamina = max(0, self.player.stamina - 5)
        return "방어 자세를 취했습니다. 받는 피해가 감소합니다."
        
    def player_ambush(self) -> str:
        """플레이어 기습"""
        if self.player.turn_action_taken:
            return "이미 이번 턴에 행동했습니다!"
            
        self.player.turn_action_taken = True
        
        if not self.player.use_stamina(20) or not self.player.use_focus(20):
            return "기력이나 집중도가 부족합니다!"
            
        success_chance = 50 + (self.player.level * 2)
        if random.randint(1, 100) <= success_chance:
            damage = self.player.get_total_attack() * 2
            actual_damage = self.enemy.take_damage(damage)
            return f"기습 성공! {actual_damage}의 큰 피해를 입혔습니다!"
        else:
            return "기습에 실패했습니다! 적에게 반격당합니다!"
            
    def player_use_skill(self, skill: Skill) -> str:
        """플레이어 기술 사용"""
        if self.player.turn_action_taken:
            return "이미 이번 턴에 행동했습니다!"
            
        self.player.turn_action_taken = True
        
        if not self.player.use_stamina(skill.stamina_cost) or not self.player.use_focus(skill.focus_cost):
            return f"{skill.name} 사용에 필요한 기력이나 집중도가 부족합니다!"
            
        damage = int(self.player.get_total_attack() * skill.damage_multiplier)
        actual_damage = self.enemy.take_damage(damage)
        return f"{skill.name} 발동! {actual_damage}의 피해를 입혔습니다!"
        
    def enemy_turn(self) -> str:
        """적 턴"""
        if not self.enemy.is_alive():
            return ""
            
        # 회피 체크
        if random.randint(1, 100) <= self.player.get_dodge_chance():
            return f"{self.enemy.name}의 공격을 회피했습니다!"
            
        # 적 AI 행동 결정
        action = self.enemy.choose_action(self.player_last_action)
        
        if action == "attack":
            damage = self.enemy.get_attack_damage()
            actual_damage = self.player.take_damage(damage)
            
            # 방어구 내구도 감소
            if self.player.equipped_armor:
                self.player.equipped_armor.durability -= 1
                if self.player.equipped_armor.durability <= 0:
                    return f"{self.enemy.name}의 공격! {actual_damage}의 피해를 받았습니다.\n{Colors.RED}방어구가 파괴되었습니다!{Colors.RESET}"
                    
            return f"{self.enemy.name}의 공격! {actual_damage}의 피해를 받았습니다. (체력: {self.player.health}/{self.player.max_health})"
            
        elif action == "strong_attack":
            damage = int(self.enemy.get_attack_damage() * 1.5)
            actual_damage = self.player.take_damage(damage)
            return f"{self.enemy.name}의 강공격! {actual_damage}의 큰 피해를 받았습니다!"
            
        elif action == "feint":
            # 견제 - 플레이어 집중도 감소
            self.player.focus = max(0, self.player.focus - 15)
            return f"{self.enemy.name}이(가) 견제합니다! 집중력이 흐트러집니다."
            
        elif action == "defend":
            self.enemy.defense += 5
            self.enemy.stance = "defensive"
            return f"{self.enemy.name}이(가) 방어 자세를 취했습니다."
            
        elif action == "taunt":
            # 도발 - 플레이어 정신력 감소
            self.player.sanity -= 5
            return f"{self.enemy.name}이(가) 당신을 조롱합니다! 정신력이 흔들립니다."
            
        else:
            return f"{self.enemy.name}이(가) 이상한 행동을 취합니다..."
            
    def end_turn(self):
        """턴 종료"""
        self.turn_count += 1
        self.player.turn_action_taken = False
        
        # 버프/디버프 턴 감소
        for buff in self.player.buffs[:]:
            buff["turns"] -= 1
            if buff["turns"] <= 0:
                self.player.buffs.remove(buff)
                
        for debuff in self.player.debuffs[:]:
            debuff["turns"] -= 1
            if debuff["turns"] <= 0:
                self.player.debuffs.remove(debuff)
            
    def check_combat_end(self) -> Optional[str]:
        """전투 종료 확인"""
        if self.player.health <= 0:
            self.is_active = False
            return "death"
        elif not self.enemy.is_alive():
            self.is_active = False
            return "victory"
        return None


class Game:
    """메인 게임 클래스"""
    def __init__(self):
        self.player = None
        self.current_location = None
        self.locations = {}
        self.npcs = {}
        self.current_combat = None
        self.is_running = True
        
        # 게임 이벤트 플래그 (딕셔너리 구조로 개선)
        self.game_flags = {
            "병사_구조": False,
            "용병_고용": False,
            "밀교_의식_정보": False,
            "암시회_지하_정보": False,
            "왕실_첩자_정보": False,
            "밀교_비밀_목격": False,
            "유곽_정보_획득": False,
            "봉기_참여": False,
            "고문_가담": False,
            "밀교_혈맹": False,
            "궁궐_지하_무기고_정보": False,
            "밀교_음모_인지": False,
            "무기_밀수_정보": False,
            "이방인_반란_정보": False,
            "호위대장_반역_정보": False,
            "혼령_퀘스트": False
        }
        self.permanent_consequences = []  # 영구적 결과 저장
        self.game_time = 12  # 게임 내 시간 (0-23)
        self.death_cause = ""  # 사망 원인
        
        # 기본 아이템 생성
        self.items_database = self._create_items()
        
        # 기본 기술 생성
        self.skills_database = self._create_skills()
        
    def _create_items(self) -> Dict[str, Item]:
        """기본 아이템 데이터베이스 생성"""
        return {
            "녹슨 검": Item("녹슨 검", ItemType.WEAPON, "오래된 녹슨 검이다.", power=10),
            "포도청 검": Item("포도청 검", ItemType.WEAPON, "포도청에서 사용하던 제식 검.", power=25),
            "명검 청홍": Item("명검 청홍", ItemType.WEAPON, "전설의 명검. 푸른 빛이 감돈다.", power=50),
            "누더기 옷": Item("누더기 옷", ItemType.ARMOR, "찢어진 누더기 옷.", defense=5),
            "가죽 갑옷": Item("가죽 갑옷", ItemType.ARMOR, "질긴 가죽으로 만든 갑옷.", defense=15),
            "철갑옷": Item("철갑옷", ItemType.ARMOR, "두꺼운 철로 만든 갑옷.", defense=30),
            "비밀 문서": Item("비밀 문서", ItemType.STORY, "암시회의 비밀이 적힌 문서.", special_effect="암시회 은신처 해금"),
            "왕실 인장": Item("왕실 인장", ItemType.SPECIAL, "왕실의 권위를 상징하는 인장.", special_effect="궁궐 출입 가능"),
            "독약": Item("독약", ItemType.SPECIAL, "치명적인 독이 든 병.", special_effect="암살 가능"),
            "회복약": Item("회복약", ItemType.SPECIAL, "체력을 회복하는 약.", special_effect="체력 50 회복")
        }
        
    def _create_skills(self) -> Dict[str, Skill]:
        """기본 기술 데이터베이스 생성"""
        return {
            "일섬": Skill("일섬", 1.5, 20, 10, "빠른 베기 공격"),
            "연환격": Skill("연환격", 2.0, 30, 20, "연속 공격"),
            "회전베기": Skill("회전베기", 2.5, 40, 30, "강력한 회전 공격"),
            "무형검": Skill("무형검", 3.0, 50, 40, "형체 없는 검기"),
            "천지개벽": Skill("천지개벽", 5.0, 80, 60, "궁극의 일격")
        }
        
    def _create_locations(self):
        """게임 월드 생성"""
        # 시작 지점
        self.locations["폐허가 된 마을"] = Location(
            "폐허가 된 마을",
            "전쟁으로 황폐해진 마을. 썩은 냄새가 진동한다.",
            Faction.NEUTRAL,
            danger_level=1
        )
        
        # 세력별 주요 거점
        self.locations["경복궁"] = Location(
            "경복궁",
            "왕권의 마지막 보루. 근위병들이 삼엄하게 경비를 서고 있다.",
            Faction.PALACE,
            danger_level=3,
            is_locked=True
        )
        
        self.locations["밀교 사원"] = Location(
            "밀교 사원",
            "이상한 주문 소리가 들려오는 음침한 사원.",
            Faction.CULT,
            danger_level=4
        )
        
        self.locations["암시회 은신처"] = Location(
            "암시회 은신처",
            "어둠 속에 숨겨진 지하 조직의 본거지.",
            Faction.SHADOW_GUILD,
            danger_level=4,
            is_locked=True
        )
        
        self.locations["민중 집회소"] = Location(
            "민중 집회소",
            "봉기를 준비하는 백성들이 모이는 곳.",
            Faction.PEOPLE_ALLIANCE,
            danger_level=2
        )
        
        self.locations["이방인 주막"] = Location(
            "이방인 주막",
            "각지에서 온 이방인들이 모이는 주막.",
            Faction.FOREIGNER_UNION,
            danger_level=2
        )
        
        # 중립 지역
        self.locations["시장"] = Location(
            "시장",
            "활기찬 시장. 온갖 물건들이 거래된다.",
            Faction.NEUTRAL,
            danger_level=1
        )
        
        self.locations["유곽"] = Location(
            "유곽",
            "화려한 등불 아래 은밀한 거래가 이루어지는 곳.",
            Faction.NEUTRAL,
            danger_level=2
        )
        
        self.locations["산속 은거지"] = Location(
            "산속 은거지",
            "세상과 단절된 은둔자의 거처.",
            Faction.NEUTRAL,
            danger_level=3
        )
        
        # 위험 지역
        self.locations["처형장"] = Location(
            "처형장",
            "피비린내가 진동하는 공개 처형장.",
            Faction.NEUTRAL,
            danger_level=5
        )
        
        self.locations["저주받은 숲"] = Location(
            "저주받은 숲",
            "들어간 자가 돌아오지 못한다는 숲.",
            Faction.NEUTRAL,
            danger_level=5,
            is_locked=True
        )
        
        # 연결 설정
        self.locations["폐허가 된 마을"].connected_locations = ["시장", "민중 집회소", "이방인 주막"]
        self.locations["시장"].connected_locations = ["폐허가 된 마을", "유곽", "처형장", "밀교 사원"]
        self.locations["민중 집회소"].connected_locations = ["폐허가 된 마을", "시장"]
        self.locations["이방인 주막"].connected_locations = ["폐허가 된 마을", "유곽", "산속 은거지"]
        self.locations["유곽"].connected_locations = ["시장", "이방인 주막", "암시회 은신처"]
        self.locations["산속 은거지"].connected_locations = ["이방인 주막", "저주받은 숲"]
        self.locations["밀교 사원"].connected_locations = ["시장", "경복궁"]
        self.locations["처형장"].connected_locations = ["시장", "경복궁"]
        self.locations["경복궁"].connected_locations = ["밀교 사원", "처형장"]
        self.locations["암시회 은신처"].connected_locations = ["유곽"]
        self.locations["저주받은 숲"].connected_locations = ["산속 은거지"]
        
        # NPC 배치
        self._place_npcs()
        
        # 아이템 배치
        self._place_items()
        
    def _place_npcs(self):
        """NPC 배치"""
        # 시장 NPC
        merchant = NPC("상인 김씨", Faction.NEUTRAL, 60)
        self.npcs["상인 김씨"] = merchant
        self.locations["시장"].add_npc(merchant)
        
        # 민중 집회소 NPC
        rebel_leader = NPC("봉기군 수장 박씨", Faction.PEOPLE_ALLIANCE, 40)
        self.npcs["봉기군 수장 박씨"] = rebel_leader
        self.locations["민중 집회소"].add_npc(rebel_leader)
        
        # 이방인 주막 NPC
        foreign_merc = NPC("서역 용병 아둘라", Faction.FOREIGNER_UNION, 50)
        self.npcs["서역 용병 아둘라"] = foreign_merc
        self.locations["이방인 주막"].add_npc(foreign_merc)
        
        # 유곽 NPC
        courtesan = NPC("기생 월향", Faction.NEUTRAL, 50)
        self.npcs["기생 월향"] = courtesan
        self.locations["유곽"].add_npc(courtesan)
        
        # 처형장 NPC
        executioner = NPC("망나니", Faction.PALACE, 20)
        self.npcs["망나니"] = executioner
        self.locations["처형장"].add_npc(executioner)
        
        # 밀교 사원 NPC
        cult_priest = NPC("밀교 사제", Faction.CULT, 30)
        self.npcs["밀교 사제"] = cult_priest
        self.locations["밀교 사원"].add_npc(cult_priest)
        
    def _place_items(self):
        """아이템 배치"""
        # 시작 지점 아이템
        self.locations["폐허가 된 마을"].add_item(self.items_database["녹슨 검"])
        self.locations["폐허가 된 마을"].add_item(self.items_database["누더기 옷"])
        
        # 시장 아이템
        self.locations["시장"].add_item(self.items_database["가죽 갑옷"])
        self.locations["시장"].add_item(self.items_database["회복약"])
        
        # 밀교 사원 아이템
        self.locations["밀교 사원"].add_item(self.items_database["독약"])
        
        # 이방인 주막 아이템
        self.locations["이방인 주막"].add_item(self.items_database["비밀 문서"])
        
    def clear_screen(self):
        """화면 지우기"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_title(self):
        """타이틀 화면"""
        self.clear_screen()
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}조선 말기: 피와 어둠의 연대기{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.DIM}극사실주의 다크 판타지 RPG{Colors.RESET}")
        print(f"{Colors.DIM}Ver {GameConstants.VERSION}{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        print()
        
    def main_menu(self) -> str:
        """메인 메뉴"""
        while True:
            self.display_title()
            print("1. 새 게임")
            print("2. 이어하기")
            print("3. 종료")
            print()
            
            choice = input(f"{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
            
            if choice in ["1", "2", "3"]:
                return choice
            else:
                print(f"{Colors.RED}올바른 선택지를 입력하세요.{Colors.RESET}")
                time.sleep(1)
                
    def create_character(self):
        """캐릭터 생성"""
        self.clear_screen()
        print(f"{Colors.BOLD}캐릭터 생성{Colors.RESET}")
        print(f"{Colors.DIM}{'='*40}{Colors.RESET}")
        
        # 이름 입력
        name = ""
        while not name:
            name = input(f"{Colors.YELLOW}이름을 입력하세요 >> {Colors.RESET}").strip()
            
        # 출신 선택
        print(f"\n{Colors.BOLD}출신 선택:{Colors.RESET}")
        origins = list(Origin)
        for i, origin in enumerate(origins, 1):
            print(f"{i}. {origin.value}")
            
        origin_choice = None
        while origin_choice is None:
            try:
                choice = int(input(f"{Colors.YELLOW}출신 선택 >> {Colors.RESET}"))
                if 1 <= choice <= len(origins):
                    origin_choice = origins[choice - 1]
                else:
                    print(f"{Colors.RED}올바른 번호를 선택하세요.{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}숫자를 입력하세요.{Colors.RESET}")
                
        # 캐릭터 생성
        self.player = Character(name, origin_choice)
        
        # 출신별 초기 스토리
        self._show_origin_story(origin_choice)
        
        # 월드 생성
        self._create_locations()
        self.current_location = self.locations["폐허가 된 마을"]
        
        print(f"\n{Colors.GREEN}캐릭터가 생성되었습니다!{Colors.RESET}")
        time.sleep(2)
        
    def _show_origin_story(self, origin: Origin):
        """출신별 배경 스토리"""
        self.clear_screen()
        print(f"{Colors.BOLD}당신의 과거...{Colors.RESET}\n")
        
        if origin == Origin.FALLEN_NOBLE:
            print("한때는 권세를 누리던 양반가의 자제였으나,")
            print("정변의 소용돌이 속에서 가문이 몰락했다.")
            print("이제 당신에게 남은 것은 낡은 자존심과 복수심뿐...")
            self.player.add_item(self.items_database["왕실 인장"])
            print(f"\n{Colors.GREEN}[왕실 인장]을 소지하고 있습니다.{Colors.RESET}")
            
        elif origin == Origin.BANDIT_OUTCAST:
            print("도적단에서 자란 당신은 동료의 배신으로 쫓겨났다.")
            print("믿었던 이들에게 등을 찔린 상처는 아직도 쓰리다.")
            print("이제 홀로 살아남아야 한다...")
            self.player.learn_skill(self.skills_database["일섬"])
            print(f"\n{Colors.GREEN}[일섬] 기술을 습득했습니다.{Colors.RESET}")
            
        else:  # WAR_ORPHAN
            print("전쟁이 모든 것을 앗아갔다.")
            print("가족도, 집도, 이름조차 잃어버린 당신.")
            print("폐허 속에서 살아남기 위해 발버둥쳤다...")
            self.player.stamina = self.player.max_stamina + 20
            self.player.max_stamina += 20
            print(f"\n{Colors.GREEN}극한의 생존력으로 최대 기력이 증가했습니다.{Colors.RESET}")
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def save_game(self):
        """게임 저장"""
        save_data = {
            "version": GameConstants.VERSION,
            "player": self.player.to_dict(),
            "current_location": self.current_location.name,
            "game_time": self.game_time,
            "npcs": {name: npc.to_dict() for name, npc in self.npcs.items()},
            "game_flags": self.game_flags,
            "permanent_consequences": self.permanent_consequences,
            "unlocked_locations": [name for name, loc in self.locations.items() if not loc.is_locked]
        }
        
        try:
            with open(GameConstants.SAVE_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"{Colors.GREEN}게임이 저장되었습니다.{Colors.RESET}")
            return True
        except Exception as e:
            print(f"{Colors.RED}저장 실패: {e}{Colors.RESET}")
            return False
            
    def load_game(self) -> bool:
        """게임 불러오기"""
        if not os.path.exists(GameConstants.SAVE_FILE_PATH):
            print(f"{Colors.RED}저장 파일이 없습니다.{Colors.RESET}")
            return False
            
        try:
            with open(GameConstants.SAVE_FILE_PATH, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                
            # 플레이어 복원
            self.player = Character.from_dict(save_data["player"])
            
            # 월드 생성
            self._create_locations()
            
            # 현재 위치 복원
            self.current_location = self.locations[save_data["current_location"]]
            
            # 게임 시간 복원
            self.game_time = save_data.get("game_time", 12)
            
            # NPC 상태 복원
            for name, npc_data in save_data["npcs"].items():
                if name in self.npcs:
                    self.npcs[name] = NPC.from_dict(npc_data)
                    
            # 게임 플래그 복원
            self.game_flags = save_data.get("game_flags", self.game_flags)
            
            # 영구 결과 복원
            self.permanent_consequences = save_data.get("permanent_consequences", [])
            
            # 잠금 해제된 장소 복원
            for location_name in save_data["unlocked_locations"]:
                if location_name in self.locations:
                    self.locations[location_name].unlock()
                    
            print(f"{Colors.GREEN}게임을 불러왔습니다.{Colors.RESET}")
            return True
            
        except Exception as e:
            print(f"{Colors.RED}불러오기 실패: {e}{Colors.RESET}")
            return False
            
    def display_status(self):
        """플레이어 상태 표시"""
        p = self.player
        print(f"\n{Colors.BOLD}=== 상태 ==={Colors.RESET}")
        print(f"이름: {p.name} | 출신: {p.origin.value} | 직업: {p.job.value}")
        print(f"레벨: {p.level} | 경험치: {p.experience}/{p.level * 100} | 금전: {p.money}냥")
        print(f"체력: {Colors.RED}{p.health}/{p.max_health}{Colors.RESET} | "
              f"기력: {Colors.YELLOW}{p.stamina}/{p.max_stamina}{Colors.RESET} | "
              f"집중: {Colors.CYAN}{p.focus}/{p.max_focus}{Colors.RESET}")
        print(f"공격력: {p.get_total_attack()} | 방어력: {p.get_total_defense()} | "
              f"정신력: {p.sanity}/100")
        
        if p.equipped_weapon:
            print(f"무기: {p.equipped_weapon.name} (+{p.equipped_weapon.enhancement_level})")
        if p.equipped_armor:
            print(f"방어구: {p.equipped_armor.name} (+{p.equipped_armor.enhancement_level})")
            
        # 상태 이상 표시
        if p.is_cursed:
            print(f"{Colors.MAGENTA}[저주받음]{Colors.RESET}")
        if p.sanity < 30:
            print(f"{Colors.RED}[정신 불안정]{Colors.RESET}")
        if p.nightmares:
            print(f"{Colors.DIM}[악몽에 시달림]{Colors.RESET}")
            
    def display_location(self):
        """현재 위치 표시"""
        loc = self.current_location
        
        # 시간대 표시
        time_str = self._get_time_string()
        print(f"\n{Colors.DIM}[{time_str}]{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}=== {loc.name} ==={Colors.RESET}")
        
        # 시간대별 설명
        if self.game_time >= 20 or self.game_time < 6:  # 밤
            print(f"{Colors.DIM}{loc.description} 어둠이 모든 것을 감싸고 있다...{Colors.RESET}")
        else:
            print(f"{Colors.DIM}{loc.description}{Colors.RESET}")
            
        print(f"위험도: {'★' * loc.danger_level}")
        
        if loc.npcs:
            print(f"\n{Colors.CYAN}인물:{Colors.RESET}")
            for npc in loc.npcs:
                # 시간대별 NPC 활동
                if self._is_npc_active(npc):
                    print(f"  - {npc.name}")
                else:
                    print(f"  - {Colors.DIM}{npc.name} (자는 중){Colors.RESET}")
                
        if loc.items:
            print(f"\n{Colors.YELLOW}아이템:{Colors.RESET}")
            for item in loc.items:
                print(f"  - {item.name}")
                
    def _get_time_string(self) -> str:
        """시간대 문자열 반환"""
        if 6 <= self.game_time < 12:
            return "아침"
        elif 12 <= self.game_time < 17:
            return "낮"
        elif 17 <= self.game_time < 20:
            return "저녁"
        else:
            return "밤"
            
    def _is_npc_active(self, npc: NPC) -> bool:
        """NPC 활동 시간 체크"""
        # 기생은 밤에만 활동
        if npc.name == "기생 월향":
            return self.game_time >= 20 or self.game_time < 4
        # 망나니는 낮에만
        elif npc.name == "망나니":
            return 10 <= self.game_time < 16
        # 밀교 사제는 밤에 더 활발
        elif npc.name == "밀교 사제":
            return self.game_time >= 22 or self.game_time < 3
        else:
            return True
            
    def location_menu(self):
        """위치 메뉴"""
        while self.is_running and not self.current_combat:
            self.clear_screen()
            self.display_status()
            self.display_location()
            
            # 암살 의뢰 확인
            self._check_assassination_contracts()
            
            # 저주 효과 적용
            if self.player.is_cursed:
                self._apply_curse_effects()
            
            print(f"\n{Colors.BOLD}행동 선택:{Colors.RESET}")
            print("1. 이동")
            print("2. 탐색")
            print("3. 대화")
            print("4. 인벤토리")
            print("5. 휴식")
            print("6. 저장")
            print("7. 특수 행동")
            print("8. 메인 메뉴로")
            
            choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
            
            if choice == "1":
                self.move_location()
            elif choice == "2":
                self.explore_location()
            elif choice == "3":
                self.talk_to_npc()
            elif choice == "4":
                self.inventory_menu()
            elif choice == "5":
                self.rest()
            elif choice == "6":
                self.save_game()
                time.sleep(1)
            elif choice == "7":
                self.special_actions()
            elif choice == "8":
                break
            else:
                print(f"{Colors.RED}올바른 선택지를 입력하세요.{Colors.RESET}")
                time.sleep(1)
                
    def _check_assassination_contracts(self):
        """암살 의뢰 진행 확인"""
        for consequence in self.permanent_consequences[:]:
            if "_암살_의뢰" in consequence and random.randint(1, 100) <= 30:
                target_name = consequence.replace("_암살_의뢰", "")
                print(f"\n{Colors.RED}암살자가 {target_name}을(를) 제거했습니다...{Colors.RESET}")
                
                # NPC 제거
                for location in self.locations.values():
                    for npc in location.npcs[:]:
                        if npc.name == target_name:
                            location.npcs.remove(npc)
                            
                # 의뢰 완료
                self.permanent_consequences.remove(consequence)
                self.permanent_consequences.append(f"{target_name}_암살_완료")
                time.sleep(2)
                
    def _apply_curse_effects(self):
        """저주 효과 적용"""
        if random.randint(1, 100) <= 10:
            print(f"\n{Colors.MAGENTA}저주가 당신을 괴롭힙니다...{Colors.RESET}")
            curse_effects = [
                ("악몽이 현실로 스며듭니다...", lambda: setattr(self.player, 'sanity', self.player.sanity - 5)),
                ("체력이 서서히 빠져나갑니다...", lambda: setattr(self.player, 'health', self.player.health - 5)),
                ("집중력이 흐트러집니다...", lambda: setattr(self.player, 'focus', max(0, self.player.focus - 10)))
            ]
            
            effect_text, effect_func = random.choice(curse_effects)
            print(f"{Colors.DIM}{effect_text}{Colors.RESET}")
            effect_func()
            time.sleep(1)
            
    def move_location(self):
        """위치 이동"""
        print(f"\n{Colors.BOLD}이동 가능한 장소:{Colors.RESET}")
        available_locations = []
        
        for i, location_name in enumerate(self.current_location.connected_locations, 1):
            location = self.locations[location_name]
            if not location.is_locked:
                available_locations.append(location)
                danger_indicator = '★' * location.danger_level
                print(f"{i}. {location.name} (위험도: {danger_indicator})")
            else:
                print(f"{i}. {Colors.DIM}??? (잠김){Colors.RESET}")
                
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}이동할 장소 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(self.current_location.connected_locations):
                destination_name = self.current_location.connected_locations[choice - 1]
                destination = self.locations[destination_name]
                
                if destination.is_locked:
                    print(f"{Colors.RED}아직 갈 수 없는 곳입니다.{Colors.RESET}")
                    time.sleep(1)
                else:
                    # 시간 경과
                    self.game_time = (self.game_time + 1) % 24
                    
                    self.current_location = destination
                    print(f"{Colors.GREEN}{destination.name}(으)로 이동했습니다.{Colors.RESET}")
                    
                    # 밤 이동 시 위험도 증가
                    danger_modifier = 1.5 if (self.game_time >= 20 or self.game_time < 6) else 1.0
                    
                    # 이동 시 랜덤 이벤트 발생 가능
                    if random.randint(1, 100) <= destination.danger_level * 10 * danger_modifier:
                        self.random_encounter()
                    else:
                        time.sleep(1)
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
    def explore_location(self):
        """현재 위치 탐색"""
        print(f"\n{Colors.CYAN}주변을 살펴봅니다...{Colors.RESET}")
        time.sleep(1)
        
        # 시간대별 특수 발견
        if self._check_time_based_discovery():
            return
        
        # 아이템 발견
        if self.current_location.items and random.randint(1, 100) <= 70:
            found_item = random.choice(self.current_location.items)
            print(f"\n{Colors.GREEN}[{found_item.name}]을(를) 발견했습니다!{Colors.RESET}")
            print(f"{Colors.DIM}{found_item.description}{Colors.RESET}")
            
            choice = input(f"\n획득하시겠습니까? (y/n) >> ").strip().lower()
            if choice == 'y':
                self.player.add_item(found_item)
                self.current_location.items.remove(found_item)
                print(f"{Colors.GREEN}[{found_item.name}]을(를) 획득했습니다.{Colors.RESET}")
                
                # 특수 효과 처리
                if found_item.special_effect == "암시회 은신처 해금":
                    self.locations["암시회 은신처"].unlock()
                    print(f"{Colors.YELLOW}암시회 은신처의 위치를 알게 되었습니다!{Colors.RESET}")
                elif found_item.special_effect == "궁궐 출입 가능":
                    self.locations["경복궁"].unlock()
                    print(f"{Colors.YELLOW}이제 경복궁에 들어갈 수 있습니다!{Colors.RESET}")
        else:
            print(f"{Colors.DIM}특별한 것은 없는 것 같다...{Colors.RESET}")
            
        # 랜덤 이벤트
        if random.randint(1, 100) <= 30:
            self.random_encounter()
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _check_time_based_discovery(self) -> bool:
        """시간대별 특수 발견"""
        # 자정 특수 이벤트
        if self.game_time == 0 and self.current_location.name == "밀교 사원":
            print(f"\n{Colors.MAGENTA}자정... 사원 깊은 곳에서 이상한 빛이 새어나옵니다...{Colors.RESET}")
            print("숨겨진 지하 통로를 발견했습니다!")
            
            choice = input("들어가시겠습니까? (y/n) >> ").strip().lower()
            if choice == 'y':
                self._secret_underground_passage()
            return True
            
        # 새벽 특수 이벤트
        elif 3 <= self.game_time <= 5 and self.current_location.name == "처형장":
            print(f"\n{Colors.DIM}새벽안개 속에서 떠도는 혼령들이 보입니다...{Colors.RESET}")
            self.player.sanity -= 10
            
            if self.player.sanity < 50:
                print(f"{Colors.RED}혼령들이 속삭입니다: '우리처럼 되어라...'{Colors.RESET}")
                self._ghost_encounter()
            return True
            
        return False
        
    def _secret_underground_passage(self):
        """비밀 지하 통로 이벤트"""
        print(f"\n{Colors.MAGENTA}지하 깊은 곳으로 내려갑니다...{Colors.RESET}")
        time.sleep(1)
        
        print("고대의 제단을 발견했습니다!")
        print("\n1. 제단에 피를 바친다")
        print("2. 제단을 파괴한다")
        print("3. 조용히 돌아간다")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            print(f"\n{Colors.RED}당신의 피가 제단에 스며듭니다...{Colors.RESET}")
            self.player.health -= 30
            
            # 강력한 아이템 획득
            legendary_weapon = Item("마검 혈귀", ItemType.WEAPON, 
                                  "피를 갈구하는 저주받은 검", power=80)
            self.player.add_item(legendary_weapon)
            print(f"\n{Colors.MAGENTA}[마검 혈귀]를 획득했습니다!{Colors.RESET}")
            
            self.player.is_cursed = True
            self.player.nightmares.append("피의 제단")
            
        elif choice == "2":
            print(f"\n{Colors.YELLOW}제단을 파괴합니다!{Colors.RESET}")
            print("갑자기 지진이 일어납니다!")
            
            # 밀교파와 영구 적대
            self.player.faction_affinity[Faction.CULT] = -100
            print(f"{Colors.RED}밀교파가 당신을 이단으로 선포했습니다!{Colors.RESET}")
            
            # 붕괴로 인한 부상
            self.player.health -= 20
            print("무너지는 돌에 맞아 부상을 입었습니다!")
            
    def _ghost_encounter(self):
        """유령 조우 이벤트"""
        print(f"\n{Colors.MAGENTA}처형당한 자들의 혼령이 나타났습니다...{Colors.RESET}")
        
        if "고문_집행자" in self.permanent_consequences:
            print(f"{Colors.RED}'네가... 네가 우리를 죽였다...!'{Colors.RESET}")
            print("혼령들이 당신을 공격합니다!")
            
            # 특수 적 - 물리 공격 효과 감소
            ghost = Enemy("원혼 무리", 100, 25, 20, 80, None,
                         ["attack", "taunt", "taunt"])
            ghost.defense = 30  # 물리 방어력 높음
            self.start_combat(ghost)
        else:
            print("혼령들이 슬픈 눈으로 당신을 바라봅니다...")
            print(f"{Colors.CYAN}'우리의 원한을 풀어주오...'{Colors.RESET}")
            
            # 퀘스트 제공
            self.game_flags["혼령_퀘스트"] = True
            
    def talk_to_npc(self):
        """NPC와 대화"""
        if not self.current_location.npcs:
            print(f"{Colors.DIM}대화할 사람이 없습니다.{Colors.RESET}")
            time.sleep(1)
            return
            
        active_npcs = [npc for npc in self.current_location.npcs if self._is_npc_active(npc)]
        if not active_npcs:
            print(f"{Colors.DIM}깨어있는 사람이 없습니다.{Colors.RESET}")
            time.sleep(1)
            return
            
        print(f"\n{Colors.BOLD}대화 상대 선택:{Colors.RESET}")
        for i, npc in enumerate(active_npcs, 1):
            print(f"{i}. {npc.name}")
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(active_npcs):
                npc = active_npcs[choice - 1]
                self.npc_interaction(npc)
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
    def npc_interaction(self, npc: NPC):
        """NPC 상호작용"""
        self.clear_screen()
        print(f"{Colors.BOLD}=== {npc.name} ==={Colors.RESET}")
        print(npc.get_reaction())
        
        # NPC 기억 표시
        if npc.memories:
            recent_memory = npc.memories[-1]
            if "배신" in recent_memory["action"]:
                print(f"{Colors.RED}(당신의 배신을 기억하고 있다...){Colors.RESET}")
            elif "도움" in recent_memory["action"]:
                print(f"{Colors.GREEN}(당신의 도움을 기억하고 있다...){Colors.RESET}")
        
        if npc.is_hostile:
            print(f"\n{Colors.RED}{npc.name}이(가) 공격해옵니다!{Colors.RESET}")
            enemy = Enemy(npc.name, 80, 15, 10, 50)
            self.start_combat(enemy)
            return
            
        # 출신별 대화 옵션
        dialogue_options = self._get_origin_based_dialogue(npc)
        
        # NPC별 특수 대화
        if npc.name == "상인 김씨":
            print("\n'어서 오시게. 무엇을 찾으시나?'")
            if npc.trust >= 50:
                print("'믿을만한 손님이군. 특별한 물건도 보여드리지.'")
                dialogue_options.extend([
                    ("거래하기", lambda: self.shop_menu(npc)),
                    ("정보 구매", lambda: self.buy_information(npc))
                ])
            else:
                dialogue_options.extend([
                    ("거래하기", lambda: self.shop_menu(npc))
                ])
                
        elif npc.name == "봉기군 수장 박씨":
            print("\n'양반놈들을 몰아내고 새 세상을 열 것이오!'")
            
            # 출신별 반응
            if self.player.origin == Origin.FALLEN_NOBLE:
                print(f"{Colors.YELLOW}(그가 당신을 의심스럽게 바라본다...){Colors.RESET}")
                npc.adjust_trust(-10)
            elif self.player.origin == Origin.WAR_ORPHAN:
                print(f"{Colors.GREEN}(동병상련의 눈빛을 보낸다...){Colors.RESET}")
                npc.adjust_trust(10)
                
            if self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] >= 60:
                dialogue_options.extend([
                    ("봉기에 참여하기", lambda: self.join_rebellion(npc)),
                    ("정보 공유", lambda: self.share_information(npc))
                ])
                
        elif npc.name == "서역 용병 아둘라":
            print("\n'돈만 준다면 뭐든 해주지.'")
            
            # 도적 출신은 특별 대우
            if self.player.origin == Origin.BANDIT_OUTCAST:
                print(f"{Colors.CYAN}'오... 같은 길을 걸었던 자군. 특별히 해주지.'{Colors.RESET}")
                dialogue_options.append(("암살 의뢰 (도적 출신 전용)", lambda: self.assassination_contract(npc)))
                
            dialogue_options.extend([
                ("용병 고용", lambda: self.hire_mercenary(npc)),
                ("전투 기술 배우기", lambda: self.learn_combat_skill(npc))
            ])
            
        elif npc.name == "기생 월향":
            print("\n'어서 오세요, 나리...'")
            
            # 양반 출신은 특별 대우
            if self.player.origin == Origin.FALLEN_NOBLE:
                print(f"{Colors.CYAN}'아... 옛 영화가 느껴지는군요. 특별히 모시겠습니다.'{Colors.RESET}")
                dialogue_options.append(("비밀 정보 거래 (양반 전용)", lambda: self.secret_info_trade(npc)))
                
            dialogue_options.extend([
                ("정보 구매 (50냥)", lambda: self.buy_courtesan_info(npc)),
                ("밤을 보내기 (100냥)", lambda: self.spend_night(npc))
            ])
            
        elif npc.name == "밀교 사제":
            print("\n'고통을 통해 초월에 이르는 길...'")
            
            dialogue_options.extend([
                ("교리에 대해 묻기", lambda: self.ask_doctrine(npc)),
                ("금지된 지식 구매 (300냥)", lambda: self.buy_forbidden_knowledge(npc))
            ])
            
            # 자정 특수 이벤트
            if self.game_time == 0:
                dialogue_options.append(("심야 의식 참여", lambda: self.midnight_ritual(npc)))
                
        elif npc.name == "망나니":
            print("\n'피의 냄새가 그리운가? 크크크...'")
            if self.current_location.name == "처형장":
                dialogue_options.append(("고문 참관", lambda: self.witness_torture()))
            
        # 기본 선택지
        dialogue_options.append(("돌아가기", None))
        
        # 선택지 표시
        print(f"\n{Colors.BOLD}선택:{Colors.RESET}")
        for i, (text, _) in enumerate(dialogue_options, 1):
            print(f"{i}. {text}")
            
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if 1 <= choice <= len(dialogue_options):
                _, action = dialogue_options[choice - 1]
                if action:
                    action()
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _get_origin_based_dialogue(self, npc: NPC):
        """출신별 기본 대화 옵션"""
        options = []
        
        if self.player.origin == Origin.FALLEN_NOBLE:
            options.append(("위엄있게 명령하기", lambda: self.noble_command(npc)))
            if npc.faction == Faction.PALACE:
                options.append(("가문의 이름으로 호소하기", lambda: self.family_appeal(npc)))
                
        elif self.player.origin == Origin.BANDIT_OUTCAST:
            options.append(("은밀히 거래 제안", lambda: self.shady_deal(npc)))
            if npc.faction in [Faction.SHADOW_GUILD, Faction.FOREIGNER_UNION]:
                options.append(("동업자 코드로 대화", lambda: self.criminal_code(npc)))
                
        elif self.player.origin == Origin.WAR_ORPHAN:
            options.append(("동정심에 호소하기", lambda: self.sympathy_appeal(npc)))
            if npc.faction == Faction.PEOPLE_ALLIANCE:
                options.append(("고통의 경험 공유", lambda: self.share_suffering(npc)))
                
        return options
        
    def noble_command(self, npc: NPC):
        """양반 출신 - 위엄있게 명령"""
        print(f"\n당신은 양반의 위엄으로 {npc.name}에게 명령합니다.")
        
        if npc.faction == Faction.PALACE or npc.trust >= 60:
            print(f"{Colors.GREEN}{npc.name}이(가) 고개를 숙입니다.{Colors.RESET}")
            npc.adjust_trust(5)
        else:
            print(f"{Colors.RED}'시대가 바뀌었소. 양반 나부랭이가...'{Colors.RESET}")
            npc.adjust_trust(-15)
            npc.remember_action("양반_명령_거부")
            
    def family_appeal(self, npc: NPC):
        """양반 출신 - 가문 호소"""
        print(f"\n당신은 몰락한 가문의 영광을 언급합니다.")
        print(f"{Colors.CYAN}'우리 가문은 한때 왕실의 신임을 받았소...'{Colors.RESET}")
        
        if "왕실 인장" in [item.name for item in self.player.inventory]:
            print(f"{Colors.GREEN}왕실 인장을 보인 {npc.name}의 태도가 달라집니다!{Colors.RESET}")
            npc.adjust_trust(20)
            npc.remember_action("왕실_인장_확인")
        else:
            print(f"{Colors.DIM}{npc.name}이(가) 시큰둥해합니다.{Colors.RESET}")
            
    def shady_deal(self, npc: NPC):
        """도적 출신 - 은밀한 거래"""
        print(f"\n당신은 {npc.name}에게 은밀히 속삭입니다.")
        
        if npc.faction in [Faction.SHADOW_GUILD, Faction.CULT]:
            print(f"{Colors.GREEN}'흥미로운 제안이군... 들어보지.'{Colors.RESET}")
            npc.adjust_trust(10)
        else:
            print(f"{Colors.RED}'수상한 놈... 꺼져!'{Colors.RESET}")
            npc.adjust_trust(-10)
            
    def criminal_code(self, npc: NPC):
        """도적 출신 - 범죄자 암호"""
        print(f"\n당신은 도적들만 아는 은어로 말합니다.")
        print(f"{Colors.CYAN}'달빛 아래 그림자가 춤춘다...'{Colors.RESET}")
        
        print(f"{Colors.GREEN}{npc.name}이(가) 같은 은어로 답합니다!{Colors.RESET}")
        print("'...그리고 칼날은 침묵한다.'")
        
        npc.adjust_trust(25)
        npc.remember_action("동업자_확인")
        
        # 특별 보상
        if "암시회 은신처" in self.locations and self.locations["암시회 은신처"].is_locked:
            print(f"\n{Colors.YELLOW}암시회 은신처의 위치를 알려줍니다!{Colors.RESET}")
            self.locations["암시회 은신처"].unlock()
            
    def sympathy_appeal(self, npc: NPC):
        """전쟁 고아 - 동정심 호소"""
        print(f"\n당신은 전쟁으로 잃은 모든 것을 이야기합니다.")
        
        if npc.trust >= 40 or npc.faction == Faction.PEOPLE_ALLIANCE:
            print(f"{Colors.GREEN}{npc.name}의 눈가가 촉촉해집니다.{Colors.RESET}")
            npc.adjust_trust(15)
            
            # 작은 도움
            if self.player.health < self.player.max_health:
                print(f"{Colors.GREEN}약초를 건네줍니다. 체력이 회복됩니다!{Colors.RESET}")
                self.player.heal(20)
        else:
            print(f"{Colors.DIM}'안타깝지만... 모두가 고통받고 있소.'{Colors.RESET}")
            
    def share_suffering(self, npc: NPC):
        """전쟁 고아 - 고통 공유"""
        print(f"\n당신은 전쟁의 참상을 생생히 묘사합니다.")
        print(f"{Colors.DIM}불타는 마을... 비명소리... 죽어가는 부모...{Colors.RESET}")
        
        self.player.sanity -= 5
        npc.adjust_trust(20)
        npc.remember_action("전쟁_경험_공유")
        
        print(f"{Colors.GREEN}{npc.name}이(가) 당신을 동지로 받아들입니다.{Colors.RESET}")
        self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] += 15
        
    def shop_menu(self, merchant: NPC):
        """상점 메뉴"""
        shop_items = {
            "포도청 검": (self.items_database["포도청 검"], 200),
            "가죽 갑옷": (self.items_database["가죽 갑옷"], 150),
            "회복약": (self.items_database["회복약"], 50),
            "철갑옷": (self.items_database["철갑옷"], 500)
        }
        
        while True:
            self.clear_screen()
            print(f"\n{Colors.BOLD}=== 상점 ==={Colors.RESET}")
            print(f"보유 금액: {Colors.YELLOW}{self.player.money}냥{Colors.RESET}\n")
            
            items_list = list(shop_items.items())
            for i, (name, (item, price)) in enumerate(items_list, 1):
                print(f"{i}. {name} - {price}냥")
                print(f"   {Colors.DIM}{item.description}{Colors.RESET}")
                
            print("0. 나가기")
            
            try:
                choice = int(input(f"\n{Colors.YELLOW}구매할 아이템 >> {Colors.RESET}"))
                if choice == 0:
                    break
                elif 1 <= choice <= len(items_list):
                    name, (item, price) = items_list[choice - 1]
                    
                    if self.player.money >= price:
                        self.player.money -= price
                        new_item = Item(item.name, item.item_type, item.description, 
                                      item.power, item.defense, item.special_effect)
                        self.player.add_item(new_item)
                        print(f"\n{Colors.GREEN}[{name}]을(를) 구매했습니다!{Colors.RESET}")
                        merchant.adjust_trust(5)
                    else:
                        print(f"\n{Colors.RED}금액이 부족합니다!{Colors.RESET}")
                    
                    time.sleep(1.5)
            except ValueError:
                print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
                time.sleep(1)
                
    def buy_information(self, npc: NPC):
        """정보 구매"""
        print("\n'이런 정보들이 있소...'")
        print("1. 저주받은 숲의 비밀 (100냥)")
        print("2. 밀교파의 음모 (200냥)")
        print("3. 돌아가기")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        if choice == "1" and self.player.money >= 100:
            self.player.money -= 100
            print(f"\n{Colors.CYAN}'저주받은 숲 깊은 곳에 전설의 무기가 숨겨져 있다고 하오.'{Colors.RESET}")
            self.locations["저주받은 숲"].unlock()
            npc.adjust_trust(5)
        elif choice == "2" and self.player.money >= 200:
            self.player.money -= 200
            print(f"\n{Colors.CYAN}'밀교파가 왕실 전복을 꾀하고 있소. 조심하시오.'{Colors.RESET}")
            self.game_flags["밀교_음모_인지"] = True
            npc.adjust_trust(5)
            
    def join_rebellion(self, npc: NPC):
        """봉기 참여"""
        print(f"\n{Colors.RED}경고: 봉기에 참여하면 왕실과 적대 관계가 됩니다!{Colors.RESET}")
        choice = input("정말 참여하시겠습니까? (y/n) >> ").strip().lower()
        
        if choice == 'y':
            self.player.faction_affinity[Faction.PALACE] -= 50
            self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] += 30
            self.game_flags["봉기_참여"] = True
            print(f"\n{Colors.GREEN}봉기군에 합류했습니다!{Colors.RESET}")
            npc.adjust_trust(20)
            npc.remember_action("봉기_참여")
            
            # 봉기군 무기 지급
            rebel_sword = Item("봉기군 검", ItemType.WEAPON, "거친 만듦새지만 단단한 검", power=20)
            self.player.add_item(rebel_sword)
            print(f"{Colors.GREEN}[봉기군 검]을 받았습니다!{Colors.RESET}")
            
    def share_information(self, npc: NPC):
        """정보 공유"""
        shared_something = False
        
        if self.game_flags.get("밀교_의식_정보", False):
            print("\n밀교파의 음모에 대해 알려주었습니다.")
            npc.adjust_trust(15)
            npc.remember_action("밀교파_정보_공유")
            shared_something = True
            
        if self.game_flags.get("무기_밀수_정보", False):
            print("\n암시회의 무기 밀수 계획을 알려주었습니다.")
            npc.adjust_trust(20)
            npc.remember_action("무기_밀수_정보_공유")
            shared_something = True
            
        if shared_something:
            print(f"\n{Colors.GREEN}신뢰도가 상승했습니다!{Colors.RESET}")
        else:
            print("\n공유할 만한 정보가 없습니다.")
            
    def assassination_contract(self, npc: NPC):
        """도적 출신 전용 - 암살 계약"""
        print(f"\n{Colors.RED}'제거해야 할 대상이 있나?'{Colors.RESET}")
        print("'200냥이면 누구든 조용히 사라지게 해주지.'")
        
        if self.player.money >= 200:
            # 암살 대상 선택
            targets = ["밀교 사제", "봉기군 수장 박씨", "상인 김씨"]
            print("\n암살 대상:")
            for i, target in enumerate(targets, 1):
                print(f"{i}. {target}")
            print("0. 취소")
            
            try:
                choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
                if 1 <= choice <= len(targets):
                    target_name = targets[choice - 1]
                    self.player.money -= 200
                    self.permanent_consequences.append(f"{target_name}_암살_의뢰")
                    print(f"\n{Colors.RED}'3일 내로 처리하겠네...'{Colors.RESET}")
                    npc.remember_action(f"암살_의뢰_{target_name}")
            except ValueError:
                pass
                
    def hire_mercenary(self, npc: NPC):
        """용병 고용"""
        print("\n'하루에 50냥. 전투에서 도움을 주지.'")
        
        if self.player.money >= 50:
            choice = input("고용하시겠습니까? (y/n) >> ").strip().lower()
            if choice == 'y':
                self.player.money -= 50
                self.game_flags["용병_고용"] = True
                print(f"{Colors.GREEN}용병을 고용했습니다! 다음 전투에서 도움을 받습니다.{Colors.RESET}")
                npc.adjust_trust(5)
                
    def learn_combat_skill(self, npc: NPC):
        """전투 기술 학습"""
        available_skills = []
        
        # 학습 가능한 기술 확인
        if "연환격" not in [s.name for s in self.player.skills]:
            available_skills.append(("연환격", 100))
        if "회전베기" not in [s.name for s in self.player.skills] and self.player.level >= 5:
            available_skills.append(("회전베기", 200))
            
        if not available_skills:
            print("더 이상 배울 기술이 없습니다.")
            return
            
        print("\n학습 가능한 기술:")
        for i, (skill_name, price) in enumerate(available_skills, 1):
            skill = self.skills_database[skill_name]
            print(f"{i}. {skill_name} - {price}냥")
            print(f"   {Colors.DIM}{skill.description}{Colors.RESET}")
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(available_skills):
                skill_name, price = available_skills[choice - 1]
                if self.player.money >= price:
                    self.player.money -= price
                    self.player.learn_skill(self.skills_database[skill_name])
                    print(f"{Colors.GREEN}[{skill_name}] 기술을 습득했습니다!{Colors.RESET}")
                    npc.adjust_trust(10)
                else:
                    print(f"{Colors.RED}금액이 부족합니다!{Colors.RESET}")
        except ValueError:
            pass
            
    def secret_info_trade(self, npc: NPC):
        """양반 전용 - 비밀 정보 거래"""
        print(f"\n{Colors.CYAN}'아, 나리께서는 특별한 정보를 원하시는군요...'{Colors.RESET}")
        print("'궁중의 비밀, 세력들의 음모... 300냥이면 알려드리죠.'")
        
        if self.player.money >= 300:
            choice = input("구매하시겠습니까? (y/n) >> ").strip().lower()
            if choice == 'y':
                self.player.money -= 300
                print(f"\n{Colors.MAGENTA}[극비 정보 획득]{Colors.RESET}")
                print("1. 왕실 내부에 밀교파 첩자가 있습니다.")
                print("2. 암시회가 대규모 무기 밀수를 준비 중입니다.")
                print("3. 이방인연합이 반란을 계획하고 있습니다.")
                
                self.game_flags["왕실_첩자_정보"] = True
                self.game_flags["무기_밀수_정보"] = True
                self.game_flags["이방인_반란_정보"] = True
                self.locations["저주받은 숲"].unlock()
                print(f"\n{Colors.YELLOW}저주받은 숲의 비밀 통로를 알게 되었습니다!{Colors.RESET}")
                
    def buy_courtesan_info(self, npc: NPC):
        """기생 정보 구매"""
        if self.player.money >= 50:
            self.player.money -= 50
            
            # 랜덤 정보 제공
            info_list = [
                ("밀교파가 매달 보름에 비밀 의식을 연다", "밀교_의식_정보"),
                ("암시회 두목이 처형장 지하에 은신처를 만들었다", "암시회_지하_정보"),
                ("왕실 호위대장이 반역을 꾀한다", "호위대장_반역_정보")
            ]
            
            info_text, event_flag = random.choice(info_list)
            print(f"\n{Colors.CYAN}'{info_text}고 하더군요...'{Colors.RESET}")
            self.game_flags[event_flag] = True
            npc.adjust_trust(10)
        else:
            print(f"{Colors.RED}금액이 부족합니다!{Colors.RESET}")
            
    def spend_night(self, npc: NPC):
        """유곽에서 밤 보내기"""
        if self.player.money >= 100:
            self.player.money -= 100
            
            print(f"\n{Colors.DIM}화려한 등불 아래, 달콤한 향이 가득한 방...{Colors.RESET}")
            time.sleep(1)
            
            # 선택적 묘사
            print("\n1. 담소를 나눈다 (안전)")
            print("2. 깊은 밤을 보낸다 (체력/정신력 대폭 회복)")
            print("3. 금기를 넘는다 (특별한 효과, 정신력 감소)")
            
            choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
            
            if choice == "1":
                print(f"\n{Colors.GREEN}편안한 대화로 마음이 안정됩니다.{Colors.RESET}")
                self.player.sanity = min(100, self.player.sanity + 10)
                self.player.stamina = self.player.max_stamina
                
            elif choice == "2":
                print(f"\n{Colors.DIM}열정적인 밤이 지나갑니다...{Colors.RESET}")
                self.player.health = self.player.max_health
                self.player.stamina = self.player.max_stamina
                self.player.focus = self.player.max_focus
                self.player.sanity = min(100, self.player.sanity + 20)
                npc.adjust_trust(20)
                
            elif choice == "3":
                print(f"\n{Colors.RED}금기의 쾌락에 빠져듭니다...{Colors.RESET}")
                print(f"{Colors.DIM}이성을 잃고 본능에 충실한 밤...{Colors.RESET}")
                
                # 특별한 효과
                self.player.max_stamina += 10
                self.player.stamina = self.player.max_stamina
                self.player.sanity -= 15
                npc.adjust_trust(30)
                npc.remember_action("금기의_밤")
                
                # 특수 능력 획득
                if random.randint(1, 100) <= 30:
                    print(f"\n{Colors.MAGENTA}타락한 쾌락 속에서 이상한 깨달음을 얻었습니다...{Colors.RESET}")
                    self.player.base_attack += 3
                    
            # 시간 경과
            self.game_time = 6  # 다음날 아침
            time.sleep(2)
        else:
            print(f"{Colors.RED}금액이 부족합니다!{Colors.RESET}")
            
    def ask_doctrine(self, npc: NPC):
        """교리 문답"""
        print(f"\n{Colors.CYAN}'우리는 고통을 통해 초월에 이른다...'{Colors.RESET}")
        print("밀교 사제가 금지된 경전을 펼칩니다.")
        
        self.player.sanity -= 5
        self.player.focus += 10
        npc.adjust_trust(5)
        
        print(f"\n{Colors.DIM}이상한 깨달음이 당신의 정신을 파고듭니다...{Colors.RESET}")
        
    def buy_forbidden_knowledge(self, npc: NPC):
        """금지된 지식 구매"""
        print("\n'300냥이면 금지된 비술을 가르쳐주지...'")
        
        if self.player.money >= 300:
            choice = input("구매하시겠습니까? (y/n) >> ").strip().lower()
            if choice == 'y':
                self.player.money -= 300
                
                # 랜덤 비술 습득
                forbidden_skills = ["무형검", "천지개벽"]
                available = [s for s in forbidden_skills if s not in [sk.name for sk in self.player.skills]]
                
                if available:
                    skill_name = random.choice(available)
                    self.player.learn_skill(self.skills_database[skill_name])
                    print(f"{Colors.MAGENTA}[{skill_name}] 비술을 전수받았습니다!{Colors.RESET}")
                    self.player.sanity -= 15
                else:
                    print("더 이상 배울 비술이 없습니다.")
                    self.player.money += 300  # 환불
        else:
            print(f"{Colors.RED}금액이 부족합니다!{Colors.RESET}")
            
    def midnight_ritual(self, npc: NPC):
        """심야 의식 이벤트"""
        print(f"\n{Colors.MAGENTA}자정의 종이 울리고, 의식이 시작됩니다...{Colors.RESET}")
        print("검은 두건의 신도들이 원을 그리며 둘러섭니다.")
        
        print("\n1. 피의 맹세를 한다 (영구적 변화)")
        print("2. 관찰만 한다")
        print("3. 의식을 방해한다")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            print(f"\n{Colors.RED}당신은 손목을 그어 피를 제단에 바칩니다...{Colors.RESET}")
            self.player.health -= 20
            self.player.is_cursed = True
            self.permanent_consequences.append("밀교_혈맹")
            
            # 영구적 능력 변화
            self.player.max_focus += 30
            self.player.base_attack += 5
            self.player.sanity = max(0, self.player.sanity - 30)
            
            print(f"{Colors.MAGENTA}어둠의 힘이 당신의 영혼에 각인됩니다...{Colors.RESET}")
            print(f"{Colors.GREEN}집중력과 공격력이 영구적으로 상승했습니다!{Colors.RESET}")
            print(f"{Colors.RED}하지만 당신의 영혼은 영원히 저주받았습니다...{Colors.RESET}")
            
            # 특수 기술 획득
            if "천지개벽" not in [s.name for s in self.player.skills]:
                print(f"\n{Colors.MAGENTA}금지된 기술 [천지개벽]을 깨달았습니다!{Colors.RESET}")
                self.player.learn_skill(self.skills_database["천지개벽"])
                
            # 다른 세력과의 관계 파탄
            self.player.faction_affinity[Faction.PALACE] = 0
            self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] = 0
            print(f"\n{Colors.RED}왕실과 백성연맹과의 모든 관계가 단절되었습니다!{Colors.RESET}")
            
            npc.adjust_trust(50)
            npc.remember_action("혈맹_체결")
            
        elif choice == "2":
            print(f"\n{Colors.CYAN}당신은 의식의 비밀을 목격했습니다.{Colors.RESET}")
            self.game_flags["밀교_비밀_목격"] = True
            self.player.sanity -= 5
            npc.adjust_trust(5)
            
        elif choice == "3":
            print(f"\n{Colors.RED}당신은 의식을 방해했습니다!{Colors.RESET}")
            print("분노한 신도들이 공격해옵니다!")
            
            # 다수의 적과 전투
            for i in range(3):
                if self.player.health <= 0:
                    break
                enemy = Enemy(f"밀교 신도 {i+1}", 60, 15, 8, 30, None,
                             ["attack", "strong_attack"])
                print(f"\n{Colors.RED}[{enemy.name}]이(가) 나타났습니다!{Colors.RESET}")
                self.start_combat(enemy)
                
            self.player.faction_affinity[Faction.CULT] -= 50
            npc.adjust_trust(-100)
            npc.is_hostile = True
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def witness_torture(self):
        """고문 참관 - 개선된 버전"""
        print(f"\n{Colors.RED}처형장에서 끔찍한 고문이 진행되고 있습니다.{Colors.RESET}")
        
        # 고문 대상 확인
        victim = "반역자" if self.game_flags.get("왕실_첩자_정보", False) else "무고한 백성"
        print(f"고문받는 자: {victim}")
        
        print("\n1. 고문을 지켜본다")
        print("2. 고문을 중단시킨다") 
        print("3. 직접 참여한다 (극도로 잔혹함)")
        print("4. 정보를 캐낸다")
        print("5. 자리를 떠난다")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            print(f"\n{Colors.DIM}비명과 신음 소리가 처형장을 가득 채웁니다...{Colors.RESET}")
            print("당신은 차가운 눈으로 광경을 지켜봅니다.")
            self.player.sanity -= 10
            self.player.faction_affinity[Faction.PALACE] += 5
            
        elif choice == "2":
            print(f"\n{Colors.GREEN}당신은 고문을 중단시켰습니다.{Colors.RESET}")
            self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] += 10
            self.player.faction_affinity[Faction.PALACE] -= 10
            
            # 망나니와 전투 가능성
            if random.randint(1, 100) <= 50:
                print(f"\n{Colors.RED}망나니가 분노하여 공격해옵니다!{Colors.RESET}")
                enemy = Enemy("분노한 망나니", 90, 22, 12, 50, None,
                             ["attack", "strong_attack", "taunt"])
                self.start_combat(enemy)
                
        elif choice == "3":
            print(f"\n{Colors.RED}당신은 직접 고문 도구를 들었습니다...{Colors.RESET}")
            print(f"{Colors.DIM}피가 당신의 손을 적십니다. 희생자의 눈에서 생기가 사라집니다...{Colors.RESET}")
            
            self.player.sanity -= 40
            self.player.nightmares.append("고문한 자의 얼굴")
            self.player.faction_affinity[Faction.PALACE] += 20
            self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] -= 30
            self.game_flags["고문_가담"] = True
            self.permanent_consequences.append("고문_집행자")
            
            # 특수 기술 습득
            if "회전베기" not in [s.name for s in self.player.skills]:
                print(f"\n{Colors.MAGENTA}잔혹한 경험으로 [회전베기] 기술을 깨달았습니다...{Colors.RESET}")
                self.player.learn_skill(self.skills_database["회전베기"])
                
            # 영구적 변화
            print(f"\n{Colors.RED}당신의 손은 이제 영원히 피로 물들었습니다...{Colors.RESET}")
            self._apply_permanent_consequence("고문_집행자")
            
        elif choice == "4":
            print(f"\n당신은 고문을 이용해 정보를 캐냅니다...")
            
            if victim == "반역자":
                print(f"{Colors.CYAN}'암시회가... 궁궐 지하에... 무기를...'{Colors.RESET}")
                self.game_flags["궁궐_지하_무기고_정보"] = True
                print(f"\n{Colors.YELLOW}중요한 정보를 얻었습니다!{Colors.RESET}")
            else:
                print(f"{Colors.DIM}희생자는 아무것도 모릅니다...{Colors.RESET}")
                self.player.sanity -= 20
                
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _apply_permanent_consequence(self, consequence: str):
        """영구 결과 적용"""
        if consequence == "고문_집행자":
            # 모든 NPC의 초기 신뢰도 감소
            for npc in self.npcs.values():
                if npc.faction != Faction.PALACE:
                    npc.adjust_trust(-20)
                    
    def inventory_menu(self):
        """인벤토리 메뉴"""
        while True:
            self.clear_screen()
            print(f"{Colors.BOLD}=== 인벤토리 ==={Colors.RESET}")
            print(f"금전: {Colors.YELLOW}{self.player.money}냥{Colors.RESET}\n")
            
            if not self.player.inventory:
                print(f"{Colors.DIM}소지품이 없습니다.{Colors.RESET}")
            else:
                for i, item in enumerate(self.player.inventory, 1):
                    enhancement = f" (+{item.enhancement_level})" if item.enhancement_level > 0 else ""
                    durability = f" (내구도: {item.durability}%)" if item.item_type in [ItemType.WEAPON, ItemType.ARMOR] else ""
                    
                    # 장착 중인 아이템 표시
                    equipped = ""
                    if item == self.player.equipped_weapon:
                        equipped = f" {Colors.GREEN}[장착중]{Colors.RESET}"
                    elif item == self.player.equipped_armor:
                        equipped = f" {Colors.GREEN}[장착중]{Colors.RESET}"
                        
                    print(f"{i}. {item.name}{enhancement}{durability}{equipped}")
                    print(f"   {Colors.DIM}{item.description}{Colors.RESET}")
                    
            print("\n1. 장비 장착")
            print("2. 아이템 사용")
            print("3. 아이템 강화")
            print("4. 아이템 버리기")
            print("0. 돌아가기")
            
            choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                self.equip_item()
            elif choice == "2":
                self.use_item()
            elif choice == "3":
                self.enhance_item()
            elif choice == "4":
                self.drop_item()
                
    def equip_item(self):
        """아이템 장착"""
        if not self.player.inventory:
            return
            
        equippable = [item for item in self.player.inventory 
                     if item.item_type in [ItemType.WEAPON, ItemType.ARMOR] and item.durability > 0]
                     
        if not equippable:
            print(f"{Colors.DIM}장착 가능한 아이템이 없습니다.{Colors.RESET}")
            time.sleep(1)
            return
            
        print("\n장착할 아이템:")
        for i, item in enumerate(equippable, 1):
            print(f"{i}. {item.name}")
            
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(equippable):
                item = equippable[choice - 1]
                
                if item.item_type == ItemType.WEAPON:
                    self.player.equip_weapon(item)
                    print(f"{Colors.GREEN}[{item.name}]을(를) 장착했습니다.{Colors.RESET}")
                elif item.item_type == ItemType.ARMOR:
                    self.player.equip_armor(item)
                    print(f"{Colors.GREEN}[{item.name}]을(를) 장착했습니다.{Colors.RESET}")
                    
                time.sleep(1)
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
    def use_item(self):
        """아이템 사용"""
        if not self.player.inventory:
            return
            
        usable_items = [item for item in self.player.inventory if item.item_type == ItemType.SPECIAL]
        if not usable_items:
            print(f"{Colors.DIM}사용할 수 있는 아이템이 없습니다.{Colors.RESET}")
            time.sleep(1)
            return
            
        print("\n사용 가능한 아이템:")
        for i, item in enumerate(usable_items, 1):
            print(f"{i}. {item.name} - {item.special_effect}")
            
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(usable_items):
                item = usable_items[choice - 1]
                
                if item.name == "회복약":
                    self.player.heal(50)
                    self.player.inventory.remove(item)
                    print(f"{Colors.GREEN}체력을 50 회복했습니다!{Colors.RESET}")
                elif item.name == "독약":
                    print(f"{Colors.RED}독약은 전투나 암살에 사용됩니다.{Colors.RESET}")
                else:
                    print(f"{Colors.DIM}여기서는 사용할 수 없습니다.{Colors.RESET}")
                    
                time.sleep(1)
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
    def enhance_item(self):
        """아이템 강화"""
        enhanceable = [item for item in self.player.inventory 
                      if item.item_type in [ItemType.WEAPON, ItemType.ARMOR] and item.durability > 0]
                      
        if not enhanceable:
            print(f"{Colors.DIM}강화할 수 있는 아이템이 없습니다.{Colors.RESET}")
            time.sleep(1)
            return
            
        print("\n강화 가능한 아이템:")
        for i, item in enumerate(enhanceable, 1):
            print(f"{i}. {item.name} (+{item.enhancement_level}) - 성공률: {80 - item.enhancement_level * 15}%")
            
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(enhanceable):
                item = enhanceable[choice - 1]
                
                print(f"\n{Colors.YELLOW}[{item.name}] 강화를 시도합니다...{Colors.RESET}")
                time.sleep(1)
                
                success, result_type = item.enhance()
                
                if success:
                    print(f"{Colors.GREEN}강화 성공! [{item.name}] (+{item.enhancement_level}){Colors.RESET}")
                else:
                    if result_type == "normal":
                        print(f"{Colors.YELLOW}강화 실패!{Colors.RESET}")
                    elif result_type == "damaged":
                        print(f"{Colors.RED}강화 실패! 내구도가 크게 감소했습니다!{Colors.RESET}")
                    elif result_type == "destroyed":
                        print(f"{Colors.RED}강화 대실패! [{item.name}]이(가) 파괴되었습니다!{Colors.RESET}")
                        self.player.inventory.remove(item)
                        if self.player.equipped_weapon == item:
                            self.player.equipped_weapon = None
                        elif self.player.equipped_armor == item:
                            self.player.equipped_armor = None
                    elif result_type == "cursed":
                        print(f"{Colors.MAGENTA}강화 실패! 아이템에 저주가 걸렸습니다!{Colors.RESET}")
                        print(f"{Colors.DIM}불길한 기운이 아이템을 감싸고 있다...{Colors.RESET}")
                        
                time.sleep(2)
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
    def drop_item(self):
        """아이템 버리기"""
        if not self.player.inventory:
            return
            
        print("\n버릴 아이템 번호를 입력하세요 (0: 취소):")
        try:
            choice = int(input(f"{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(self.player.inventory):
                item = self.player.inventory[choice - 1]
                
                confirm = input(f"\n정말 [{item.name}]을(를) 버리시겠습니까? (y/n) >> ").strip().lower()
                if confirm == 'y':
                    self.player.inventory.remove(item)
                    self.current_location.add_item(item)
                    print(f"{Colors.YELLOW}[{item.name}]을(를) 버렸습니다.{Colors.RESET}")
                    
                    # 장착 중인 아이템 체크
                    if item == self.player.equipped_weapon:
                        self.player.equipped_weapon = None
                    elif item == self.player.equipped_armor:
                        self.player.equipped_armor = None
                    
                time.sleep(1)
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
    def rest(self):
        """휴식"""
        print(f"\n{Colors.CYAN}잠시 휴식을 취합니다...{Colors.RESET}")
        
        # 악몽 체크
        if self.player.sanity < 30 or self.player.nightmares:
            print(f"\n{Colors.RED}불안한 잠에 빠집니다...{Colors.RESET}")
            self._nightmare_event()
        else:
            self.player.rest()
            
            # 휴식 중 랜덤 이벤트
            if random.randint(1, 100) <= 20:
                print(f"\n{Colors.RED}휴식 중 습격을 받았습니다!{Colors.RESET}")
                self.random_encounter()
            else:
                print(f"\n{Colors.GREEN}충분한 휴식을 취했습니다.{Colors.RESET}")
                print("체력, 기력, 집중도가 일부 회복되었습니다.")
                
                # 저주 체크
                if self.player.is_cursed:
                    print(f"{Colors.MAGENTA}저주가 당신의 정신을 갉아먹습니다...{Colors.RESET}")
                    self.player.sanity -= 5
                    
                # 시간 경과
                self.game_time = (self.game_time + 3) % 24
                time.sleep(2)
                
    def _nightmare_event(self):
        """악몽 이벤트"""
        nightmares = [
            "죽인 자들의 얼굴이 어둠 속에서 나타납니다...",
            "피로 물든 손이 씻겨지지 않습니다...",
            "비명소리가 귓가에 맴돕니다...",
            "당신이 저지른 일들이 악몽이 되어 찾아옵니다..."
        ]
        
        print(f"\n{Colors.MAGENTA}{random.choice(nightmares)}{Colors.RESET}")
        self.player.sanity -= 10
        self.player.stamina = max(0, self.player.stamina - 20)
        
        # 극심한 정신 불안정
        if self.player.sanity <= 0:
            print(f"\n{Colors.RED}정신이 완전히 붕괴했습니다!{Colors.RESET}")
            self.death_cause = "광기에 빠져 스스로 목숨을 끊었습니다..."
            self.player_death()
            
    def special_actions(self):
        """특수 행동 메뉴"""
        print(f"\n{Colors.BOLD}특수 행동:{Colors.RESET}")
        
        actions = []
        
        # 장소별 특수 행동
        if self.current_location.name == "밀교 사원" and self.game_time == 0:
            actions.append(("심야 의식 수행", self._midnight_special_ritual))
            
        if self.current_location.name == "처형장":
            actions.append(("처형 집행", self._execute_prisoner))
            
        if self.current_location.name == "유곽":
            actions.append(("정보 거래", self._information_broker))
            
        # 출신별 특수 행동
        if self.player.origin == Origin.FALLEN_NOBLE:
            actions.append(("권세 회복 시도", self._restore_authority))
            
        elif self.player.origin == Origin.BANDIT_OUTCAST:
            actions.append(("은밀한 도둑질", self._stealth_theft))
            
        elif self.player.origin == Origin.WAR_ORPHAN:
            actions.append(("생존 기술 사용", self._survival_skills))
            
        # 상태별 특수 행동
        if self.player.is_cursed:
            actions.append(("저주 해제 시도", self._attempt_curse_removal))
            
        if not actions:
            print(f"{Colors.DIM}특별한 행동이 없습니다.{Colors.RESET}")
            time.sleep(1)
            return
            
        for i, (name, _) in enumerate(actions, 1):
            print(f"{i}. {name}")
        print("0. 돌아가기")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return
            elif 1 <= choice <= len(actions):
                _, action = actions[choice - 1]
                action()
        except ValueError:
            print(f"{Colors.RED}올바른 번호를 입력하세요.{Colors.RESET}")
            time.sleep(1)
            
    def _midnight_special_ritual(self):
        """심야 특수 의식"""
        print(f"\n{Colors.MAGENTA}어둠의 힘이 절정에 달했습니다...{Colors.RESET}")
        
        # 특수 능력 일시 강화
        self.player.buffs.append({"type": "attack", "turns": 10, "value": 20})
        self.player.buffs.append({"type": "defense", "turns": 10, "value": 10})
        
        print(f"{Colors.GREEN}어둠의 축복을 받았습니다!{Colors.RESET}")
        print("일시적으로 전투력이 크게 상승했습니다!")
        
        self.player.sanity -= 15
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _execute_prisoner(self):
        """죄수 처형"""
        print(f"\n{Colors.RED}처형대에 죄수가 끌려옵니다...{Colors.RESET}")
        
        print("\n1. 직접 처형한다")
        print("2. 자비를 베푼다")
        print("3. 구경만 한다")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            print(f"\n{Colors.RED}당신의 칼날이 죄수의 목을 베었습니다...{Colors.RESET}")
            self.player.sanity -= 20
            self.player.faction_affinity[Faction.PALACE] += 15
            self.player.money += 50
            print(f"{Colors.YELLOW}처형 수당으로 50냥을 받았습니다.{Colors.RESET}")
            
            # 처형 기술 습득
            if random.randint(1, 100) <= 30:
                if "일섬" not in [s.name for s in self.player.skills]:
                    print(f"\n{Colors.MAGENTA}깨끗한 참수로 [일섬] 기술을 깨달았습니다!{Colors.RESET}")
                    self.player.learn_skill(self.skills_database["일섬"])
                    
        elif choice == "2":
            print(f"\n{Colors.GREEN}당신은 죄수를 몰래 풀어주었습니다.{Colors.RESET}")
            self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] += 20
            self.player.faction_affinity[Faction.PALACE] -= 20
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _information_broker(self):
        """정보 거래소"""
        print(f"\n{Colors.CYAN}은밀한 정보들이 오가는 곳입니다...{Colors.RESET}")
        
        if self.player.money >= 100:
            print("\n100냥으로 중요 정보를 살 수 있습니다.")
            choice = input("구매하시겠습니까? (y/n) >> ").strip().lower()
            
            if choice == 'y':
                self.player.money -= 100
                secrets = [
                    ("밀교파 지하 제단의 위치", lambda: self.locations["밀교 사원"].items.append(
                        Item("금지된 경전", ItemType.STORY, "밀교의 비밀이 담긴 책"))),
                    ("왕실 비자금 은닉처", lambda: setattr(self.player, 'money', self.player.money + 500)),
                    ("전설의 무기 소재지", lambda: self.locations["저주받은 숲"].items.append(
                        self.items_database["명검 청홍"]))
                ]
                
                secret_name, secret_func = random.choice(secrets)
                print(f"\n{Colors.YELLOW}[{secret_name}]의 정보를 얻었습니다!{Colors.RESET}")
                secret_func()
                
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _restore_authority(self):
        """양반 - 권세 회복"""
        print(f"\n{Colors.CYAN}당신은 옛 가문의 권위를 되찾으려 합니다...{Colors.RESET}")
        
        if "왕실 인장" in [item.name for item in self.player.inventory]:
            print(f"{Colors.GREEN}왕실 인장의 힘으로 일부 권한을 되찾았습니다!{Colors.RESET}")
            
            # 모든 NPC 신뢰도 소폭 상승
            for npc in self.npcs.values():
                if npc.faction == Faction.PALACE:
                    npc.adjust_trust(15)
                else:
                    npc.adjust_trust(5)
                    
            print("사람들이 당신을 다시 존중하기 시작합니다.")
        else:
            print(f"{Colors.DIM}권위를 증명할 방법이 없습니다...{Colors.RESET}")
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _stealth_theft(self):
        """도적 - 은밀한 도둑질"""
        print(f"\n{Colors.CYAN}주변을 살피며 훔칠 만한 것을 찾습니다...{Colors.RESET}")
        
        # 성공률 계산 (집중도와 레벨 영향)
        success_rate = 50 + (self.player.focus // 10) + (self.player.level * 2)
        
        if random.randint(1, 100) <= success_rate:
            print(f"{Colors.GREEN}성공적으로 물건을 훔쳤습니다!{Colors.RESET}")
            
            stolen_money = random.randint(20, 100)
            self.player.money += stolen_money
            print(f"{Colors.YELLOW}{stolen_money}냥을 획득했습니다!{Colors.RESET}")
            
            # 가끔 특별한 아이템도 훔침
            if random.randint(1, 100) <= 20:
                special_item = random.choice([
                    self.items_database["독약"],
                    self.items_database["회복약"]
                ])
                self.player.add_item(special_item)
                print(f"{Colors.GREEN}[{special_item.name}]도 함께 훔쳤습니다!{Colors.RESET}")
                
        else:
            print(f"{Colors.RED}들켰습니다!{Colors.RESET}")
            
            # 경비병과 전투
            guard = Enemy("경비병", 70, 15, 10, 30)
            self.start_combat(guard)
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _survival_skills(self):
        """전쟁고아 - 생존 기술"""
        print(f"\n{Colors.CYAN}극한의 환경에서 익힌 생존 기술을 사용합니다...{Colors.RESET}")
        
        print("\n1. 약초 채집 (체력 회복)")
        print("2. 함정 설치 (다음 전투에서 유리)")
        print("3. 은신처 만들기 (안전한 휴식)")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            print(f"\n{Colors.GREEN}치료용 약초를 찾았습니다!{Colors.RESET}")
            self.player.heal(30)
            self.player.stamina = min(self.player.max_stamina, self.player.stamina + 20)
            
        elif choice == "2":
            print(f"\n{Colors.GREEN}교묘한 함정을 설치했습니다!{Colors.RESET}")
            self.player.buffs.append({"type": "trap", "turns": 5, "value": 30})
            print("다음 전투에서 적이 함정에 걸릴 확률이 있습니다.")
            
        elif choice == "3":
            print(f"\n{Colors.GREEN}안전한 은신처를 만들었습니다!{Colors.RESET}")
            self.player.rest()
            self.player.rest()  # 두 배 회복
            self.player.sanity = min(100, self.player.sanity + 10)
            print("편안한 휴식으로 정신력도 회복되었습니다.")
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def _attempt_curse_removal(self):
        """저주 해제 시도"""
        print(f"\n{Colors.MAGENTA}저주를 풀기 위해 노력합니다...{Colors.RESET}")
        
        if self.current_location.name == "밀교 사원":
            print("밀교 사제가 당신을 바라봅니다.")
            print(f"{Colors.CYAN}'그 저주는... 스스로 받아들인 것. 쉽게 풀리지 않을 것이오.'{Colors.RESET}")
            
            if self.player.money >= 1000:
                print("\n'1000냥과 당신의 피를 바친다면... 시도는 해볼 수 있소.'")
                choice = input("시도하시겠습니까? (y/n) >> ").strip().lower()
                
                if choice == 'y':
                    self.player.money -= 1000
                    self.player.health -= 50
                    
                    if random.randint(1, 100) <= 30:
                        print(f"\n{Colors.GREEN}저주가 풀렸습니다!{Colors.RESET}")
                        self.player.is_cursed = False
                        self.player.sanity += 20
                    else:
                        print(f"\n{Colors.RED}저주가 더욱 강해졌습니다...{Colors.RESET}")
                        self.player.sanity -= 10
                        self.player.nightmares.append("실패한 정화 의식")
        else:
            print(f"{Colors.DIM}이곳에서는 저주를 풀 수 없습니다...{Colors.RESET}")
            print("밀교 사원을 찾아가보세요.")
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def random_encounter(self):
        """랜덤 조우"""
        encounter_type = random.choice(["combat", "event", "discovery"])
        
        if encounter_type == "combat":
            # 시간대와 위치에 따른 적 선택
            if self.game_time >= 20 or self.game_time < 6:  # 밤
                enemies = [
                    Enemy("도적", 50, 12, 5, 20, [self.items_database["회복약"]], 
                          ["attack", "feint", "strong_attack"]),
                    Enemy("굶주린 늑대", 40, 15, 3, 15, None,
                          ["attack", "attack", "strong_attack"]),
                    Enemy("밤의 살인귀", 80, 20, 10, 50, None,
                          ["attack", "feint", "strong_attack", "taunt"]),
                    Enemy("귀신들린 자", 60, 18, 8, 35, None,
                          ["attack", "taunt", "strong_attack"])
                ]
            else:  # 낮
                enemies = [
                    Enemy("관군 병사", 70, 16, 12, 30, [self.items_database["포도청 검"]],
                          ["attack", "defend", "strong_attack"]),
                    Enemy("탈영병", 60, 14, 8, 25, None,
                          ["attack", "feint"]),
                    Enemy("미친 수도승", 70, 18, 10, 35, None,
                          ["attack", "taunt", "strong_attack"]),
                    Enemy("노상강도", 55, 13, 7, 20, [self.items_database["회복약"]],
                          ["attack", "feint", "defend"])
                ]
            
            # 위험도에 따른 적 선택
            danger_level = self.current_location.danger_level
            suitable_enemies = enemies[:min(danger_level + 1, len(enemies))]
            enemy = random.choice(suitable_enemies)
            
            print(f"\n{Colors.RED}[{enemy.name}]이(가) 나타났습니다!{Colors.RESET}")
            
            # 특정 적의 특수 등장
            if enemy.name == "귀신들린 자":
                print(f"{Colors.MAGENTA}불길한 기운이 주변을 감쌉니다...{Colors.RESET}")
                self.player.sanity -= 5
                
            time.sleep(1)
            self.start_combat(enemy)
            
        elif encounter_type == "event":
            events = [
                ("상인을 만났습니다.", self.merchant_encounter),
                ("부상당한 병사를 발견했습니다.", self.wounded_soldier_event),
                ("수상한 문서를 발견했습니다.", self.mysterious_document_event),
                ("길 잃은 아이를 만났습니다.", self.lost_child_event)
            ]
            
            event_text, event_func = random.choice(events)
            print(f"\n{Colors.CYAN}{event_text}{Colors.RESET}")
            time.sleep(1)
            event_func()
            
        else:  # discovery
            print(f"\n{Colors.GREEN}숨겨진 무언가를 발견했습니다!{Colors.RESET}")
            time.sleep(1)
            
            discoveries = [
                ("낡은 지도", "특별한 장소가 표시된 지도다.", self._old_map_discovery),
                ("신비한 약초", "체력을 회복시키는 약초다.", self._herb_discovery),
                ("부적", "불길한 기운이 느껴지는 부적이다.", self._talisman_discovery)
            ]
            
            name, desc, func = random.choice(discoveries)
            print(f"\n[{name}]: {desc}")
            func()
            
    def _old_map_discovery(self):
        """낡은 지도 발견"""
        choice = input("\n지도를 살펴보시겠습니까? (y/n) >> ").strip().lower()
        if choice == 'y':
            # 랜덤하게 잠긴 장소 하나 해금
            locked_locations = [loc for loc in self.locations.values() if loc.is_locked]
            if locked_locations:
                unlock_loc = random.choice(locked_locations)
                unlock_loc.unlock()
                print(f"{Colors.YELLOW}[{unlock_loc.name}]의 위치를 발견했습니다!{Colors.RESET}")
            else:
                print("지도가 너무 낡아 알아볼 수 없습니다...")
                
    def _herb_discovery(self):
        """약초 발견"""
        choice = input("\n약초를 먹어보시겠습니까? (y/n) >> ").strip().lower()
        if choice == 'y':
            self.player.heal(30)
            print(f"{Colors.GREEN}체력이 30 회복되었습니다!{Colors.RESET}")
            
    def _talisman_discovery(self):
        """부적 발견"""
        choice = input("\n부적을 가져가시겠습니까? (y/n) >> ").strip().lower()
        if choice == 'y':
            if random.randint(1, 100) <= 50:
                print(f"{Colors.GREEN}부적이 당신을 보호합니다!{Colors.RESET}")
                self.player.buffs.append({"type": "defense", "turns": 10, "value": 5})
            else:
                print(f"{Colors.RED}저주받은 부적이었습니다!{Colors.RESET}")
                self.player.sanity -= 10
                self.player.nightmares.append("저주받은 부적")
                
    def merchant_encounter(self):
        """행상인 조우"""
        print("\n'여행자여, 좋은 물건이 있소!'")
        print("\n1. 거래하기")
        print("2. 무시하고 지나가기")
        print("3. 협박하기 (도적 출신)")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            # 간단한 거래
            print("\n행상인이 물건을 보여줍니다...")
            items_for_sale = [
                ("회복약", 30),
                ("독약", 50),
                ("가죽 갑옷", 100)
            ]
            
            for i, (name, price) in enumerate(items_for_sale, 1):
                print(f"{i}. {name} - {price}냥")
            print("0. 취소")
            
            try:
                buy_choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
                if 1 <= buy_choice <= len(items_for_sale):
                    item_name, price = items_for_sale[buy_choice - 1]
                    if self.player.money >= price:
                        self.player.money -= price
                        self.player.add_item(self.items_database[item_name])
                        print(f"{Colors.GREEN}[{item_name}]을(를) 구매했습니다!{Colors.RESET}")
                    else:
                        print(f"{Colors.RED}금액이 부족합니다!{Colors.RESET}")
            except ValueError:
                pass
                
        elif choice == "3" and self.player.origin == Origin.BANDIT_OUTCAST:
            print(f"\n{Colors.RED}당신은 행상인을 위협합니다!{Colors.RESET}")
            if random.randint(1, 100) <= 60:
                print(f"{Colors.GREEN}행상인이 겁에 질려 물건을 내놓습니다!{Colors.RESET}")
                self.player.add_item(self.items_database["회복약"])
                self.player.money += 20
            else:
                print(f"{Colors.RED}행상인이 숨겨둔 무기를 꺼냅니다!{Colors.RESET}")
                enemy = Enemy("무장한 행상인", 60, 14, 8, 25)
                self.start_combat(enemy)
                
        else:
            print("\n행상인을 무시하고 지나갑니다.")
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def wounded_soldier_event(self):
        """부상병 이벤트"""
        print("\n피를 흘리며 쓰러져 있는 병사를 발견했습니다.")
        print("\n1. 도와주기")
        print("2. 무시하기")
        print("3. 소지품을 뒤지기")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            if "회복약" in [item.name for item in self.player.inventory]:
                print(f"\n{Colors.GREEN}회복약을 사용해 병사를 치료했습니다.{Colors.RESET}")
                # 회복약 제거
                for item in self.player.inventory:
                    if item.name == "회복약":
                        self.player.inventory.remove(item)
                        break
                        
                print("병사가 감사를 표하며 정보를 알려줍니다.")
                print(f"{Colors.CYAN}'밀교파가 수상한 움직임을 보이고 있소. 조심하시오.'{Colors.RESET}")
                self.game_flags["병사_구조"] = True
                self.player.sanity += 5
                self.player.faction_affinity[Faction.PALACE] += 10
            else:
                print("치료할 수단이 없습니다...")
                
        elif choice == "3":
            print(f"\n{Colors.RED}죽어가는 병사의 소지품을 뒤집니다...{Colors.RESET}")
            self.player.sanity -= 10
            if random.randint(1, 100) <= 50:
                self.player.add_item(self.items_database["포도청 검"])
                print(f"{Colors.GREEN}[포도청 검]을 획득했습니다.{Colors.RESET}")
                self.player.money += 30
                print(f"{Colors.YELLOW}30냥을 획득했습니다.{Colors.RESET}")
            else:
                print("아무것도 없습니다.")
                
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def mysterious_document_event(self):
        """수상한 문서 이벤트"""
        print("\n길바닥에 떨어진 문서를 발견했습니다.")
        print("암호로 쓰여있지만, 일부 내용을 해독할 수 있을 것 같습니다.")
        
        if self.player.focus >= 50:
            print(f"\n{Colors.GREEN}문서를 해독했습니다!{Colors.RESET}")
            print("저주받은 숲에 대한 정보가 적혀있습니다.")
            self.locations["저주받은 숲"].unlock()
            self.player.use_focus(20)
            
            # 추가 정보
            print(f"{Colors.CYAN}'달이 없는 밤, 숲의 중심에서 피의 의식이...'{Colors.RESET}")
            self.game_flags["저주받은_숲_의식_정보"] = True
        else:
            print(f"\n{Colors.RED}집중력이 부족해 해독할 수 없습니다.{Colors.RESET}")
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def lost_child_event(self):
        """길 잃은 아이 이벤트"""
        print("\n울고 있는 아이를 발견했습니다.")
        print("\n1. 부모를 찾아주기")
        print("2. 무시하기")
        print("3. 아이를 이용하기 (사악함)")
        
        choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
        
        if choice == "1":
            print("\n아이의 부모를 찾아 나섭니다...")
            time.sleep(1)
            
            if random.randint(1, 100) <= 70:
                print(f"\n{Colors.GREEN}부모를 찾았습니다!{Colors.RESET}")
                print("감사의 표시로 작은 보상을 받았습니다.")
                self.player.sanity += 10
                self.player.money += 20
                self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] += 5
            else:
                print(f"\n{Colors.RED}함정이었습니다! 도적들이 나타납니다!{Colors.RESET}")
                enemy = Enemy("도적 두목", 80, 20, 12, 40)
                self.start_combat(enemy)
                
        elif choice == "3":
            print(f"\n{Colors.RED}당신은 아이를 미끼로 사용합니다...{Colors.RESET}")
            self.player.sanity -= 30
            self.player.nightmares.append("울부짖는 아이")
            
            # 사악한 보상
            self.player.money += 100
            print(f"{Colors.YELLOW}아이를 팔아 100냥을 얻었습니다...{Colors.RESET}")
            self.permanent_consequences.append("아동_인신매매")
            
            # 모든 선한 세력과의 관계 악화
            self.player.faction_affinity[Faction.PEOPLE_ALLIANCE] -= 50
            self.player.faction_affinity[Faction.PALACE] -= 20
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def start_combat(self, enemy: Enemy):
        """전투 시작"""
        self.current_combat = Combat(self.player, enemy)
        self.player.in_combat = True
        
        print(f"\n{Colors.RED}=== 전투 시작! ==={Colors.RESET}")
        
        # 용병 체크
        if self.game_flags.get("용병_고용", False):
            print(f"{Colors.GREEN}고용한 용병이 전투에 참여합니다!{Colors.RESET}")
            enemy.health = int(enemy.health * 0.8)  # 적 체력 20% 감소
            self.game_flags["용병_고용"] = False  # 1회성 소모
            
        # 함정 체크
        trap_buff = None
        for buff in self.player.buffs:
            if buff["type"] == "trap":
                trap_buff = buff
                break
                
        if trap_buff and random.randint(1, 100) <= trap_buff["value"]:
            print(f"{Colors.GREEN}적이 함정에 걸렸습니다!{Colors.RESET}")
            damage = 30
            enemy.health -= damage
            print(f"적이 {damage}의 피해를 입었습니다!")
            self.player.buffs.remove(trap_buff)
            
        time.sleep(1)
        
        while self.current_combat.is_active:
            self.combat_turn()
            
        # 전투 종료 처리
        result = self.current_combat.check_combat_end()
        if result == "victory":
            self.combat_victory(enemy)
        elif result == "death":
            self.player_death()
            
        self.current_combat = None
        self.player.in_combat = False
        
    def combat_turn(self):
        """전투 턴"""
        self.clear_screen()
        print(f"{Colors.RED}=== 전 투 ==={Colors.RESET}")
        print(f"\n{self.current_combat.enemy.name}")
        print(f"체력: {Colors.RED}{self.current_combat.enemy.health}/{self.current_combat.enemy.max_health}{Colors.RESET}")
        
        print(f"\n{self.player.name}")
        print(f"체력: {Colors.GREEN}{self.player.health}/{self.player.max_health}{Colors.RESET}")
        print(f"기력: {Colors.YELLOW}{self.player.stamina}/{self.player.max_stamina}{Colors.RESET}")
        print(f"집중: {Colors.CYAN}{self.player.focus}/{self.player.max_focus}{Colors.RESET}")
        
        if self.player.turn_action_taken:
            print(f"\n{Colors.DIM}이미 행동을 완료했습니다. 적의 턴입니다...{Colors.RESET}")
            time.sleep(1)
            enemy_action = self.current_combat.enemy_turn()
            if enemy_action:
                print(f"\n{enemy_action}")
            self.current_combat.end_turn()
            time.sleep(2)
        else:
            print(f"\n{Colors.BOLD}행동 선택:{Colors.RESET}")
            print("1. 공격")
            print("2. 회피")
            print("3. 방어")
            print("4. 기습")
            print("5. 기술")
            print("6. 아이템")
            
            choice = input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}").strip()
            
            result = ""
            if choice == "1":
                result = self.current_combat.player_attack()
            elif choice == "2":
                result = self.current_combat.player_dodge()
            elif choice == "3":
                result = self.current_combat.player_defend()
            elif choice == "4":
                result = self.current_combat.player_ambush()
            elif choice == "5":
                result = self.skill_menu_combat()
            elif choice == "6":
                result = self.combat_item_use()
            else:
                print(f"{Colors.RED}올바른 선택지를 입력하세요.{Colors.RESET}")
                time.sleep(1)
                return
                
            if result:
                print(f"\n{result}")
                time.sleep(2)
                
        # 전투 종료 확인
        end_result = self.current_combat.check_combat_end()
        if end_result:
            self.current_combat.is_active = False
            
    def skill_menu_combat(self) -> str:
        """전투 중 기술 메뉴"""
        if not self.player.skills:
            return "사용할 수 있는 기술이 없습니다!"
            
        print(f"\n{Colors.BOLD}사용 가능한 기술:{Colors.RESET}")
        for i, skill in enumerate(self.player.skills, 1):
            print(f"{i}. {skill.name} (기력: {skill.stamina_cost}, 집중: {skill.focus_cost})")
            print(f"   {Colors.DIM}{skill.description}{Colors.RESET}")
            
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return ""
            elif 1 <= choice <= len(self.player.skills):
                skill = self.player.skills[choice - 1]
                return self.current_combat.player_use_skill(skill)
            else:
                return "올바른 번호를 선택하세요."
        except ValueError:
            return "올바른 번호를 입력하세요."
            
    def combat_item_use(self) -> str:
        """전투 중 아이템 사용"""
        usable_items = [item for item in self.player.inventory 
                       if item.item_type == ItemType.SPECIAL]
                       
        if not usable_items:
            return "사용할 수 있는 아이템이 없습니다!"
            
        print(f"\n{Colors.BOLD}사용 가능한 아이템:{Colors.RESET}")
        for i, item in enumerate(usable_items, 1):
            print(f"{i}. {item.name}")
            
        print("0. 취소")
        
        try:
            choice = int(input(f"\n{Colors.YELLOW}선택 >> {Colors.RESET}"))
            if choice == 0:
                return ""
            elif 1 <= choice <= len(usable_items):
                item = usable_items[choice - 1]
                
                if item.name == "회복약":
                    self.player.heal(50)
                    self.player.inventory.remove(item)
                    self.player.turn_action_taken = True
                    return f"{Colors.GREEN}체력을 50 회복했습니다!{Colors.RESET}"
                elif item.name == "독약":
                    # 독약을 무기에 바름
                    if self.player.equipped_weapon:
                        self.player.buffs.append({"type": "poison", "turns": 3, "value": 10})
                        self.player.inventory.remove(item)
                        self.player.turn_action_taken = True
                        return f"{Colors.MAGENTA}무기에 독을 발랐습니다!{Colors.RESET}"
                    else:
                        return "무기가 없어 독을 바를 수 없습니다!"
                else:
                    return "전투 중에는 사용할 수 없습니다!"
        except ValueError:
            return "올바른 번호를 입력하세요."
            
    def combat_victory(self, enemy: Enemy):
        """전투 승리"""
        print(f"\n{Colors.GREEN}=== 승 리! ==={Colors.RESET}")
        print(f"{enemy.name}을(를) 물리쳤습니다!")
        
        # 경험치 획득
        self.player.gain_experience(enemy.experience_reward)
        print(f"경험치 +{enemy.experience_reward}")
        
        # 레벨업 확인
        if self.player.experience == 0:  # 레벨업 했다면
            print(f"{Colors.YELLOW}레벨 업! 현재 레벨: {self.player.level}{Colors.RESET}")
            
            # 직업 승급 확인
            if self.player.advance_job():
                print(f"{Colors.MAGENTA}직업이 [{self.player.job.value}](으)로 승급했습니다!{Colors.RESET}")
                
        # 전리품 획득
        if enemy.loot:
            print(f"\n{Colors.YELLOW}전리품 발견:{Colors.RESET}")
            for item in enemy.loot:
                print(f"- {item.name}")
                self.player.add_item(item)
                
        # 금전 획득
        money_reward = random.randint(10, 50) + (enemy.experience_reward // 2)
        self.player.money += money_reward
        print(f"금전 +{money_reward}냥")
        
        # 특수 승리 보상
        if enemy.name == "원혼 무리" and "혼령_퀘스트" in self.game_flags:
            print(f"\n{Colors.MAGENTA}혼령들이 성불했습니다...{Colors.RESET}")
            self.player.sanity += 20
            print(f"{Colors.GREEN}정신력이 회복되었습니다!{Colors.RESET}")
            
        input(f"\n{Colors.DIM}계속하려면 Enter...{Colors.RESET}")
        
    def player_death(self):
        """플레이어 사망"""
        self.clear_screen()
        
        # 사망 연출 강화
        death_messages = [
            "그대의 피가 차가운 땅에 스며든다...",
            "시야가 흐려진다... 모든 것이 어둠 속으로...",
            "마지막 숨결이 끊어진다...",
            "이제 모든 것이 끝났다..."
        ]
        
        # 타이핑 효과로 사망 메시지 출력
        for message in death_messages:
            for char in message:
                print(f"{Colors.RED}{char}{Colors.RESET}", end='', flush=True)
                time.sleep(0.05)
            print()
            time.sleep(0.8)
        
        print(f"\n{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.RED}{Colors.BOLD}死 亡{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        print()
        
        # 사망 원인별 메시지
        if hasattr(self, 'death_cause'):
            print(f"{Colors.DIM}{self.death_cause}{Colors.RESET}")
        else:
            print(f"{Colors.DIM}당신의 여정은 여기서 끝났습니다...{Colors.RESET}")
            
        print(f"{Colors.DIM}레벨 {self.player.level}에서 {self.current_location.name}에서 사망{Colors.RESET}")
        print()
        
        # 영구 사망 경고
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}이 죽음은 되돌릴 수 없습니다.{Colors.RESET}")
        print(f"{Colors.DIM}그대의 이야기는 역사 속으로 사라집니다...{Colors.RESET}")
        print(f"{Colors.RED}{'='*60}{Colors.RESET}")
        
        # 세이브 파일 자동 삭제 (영구 사망)
        if os.path.exists(GameConstants.SAVE_FILE_PATH):
            try:
                os.remove(GameConstants.SAVE_FILE_PATH)
                print(f"\n{Colors.RED}운명의 기록이 소멸되었습니다...{Colors.RESET}")
            except:
                pass
        
        # 페이드 아웃 효과
        time.sleep(2)
        for i in range(3):
            print(f"{Colors.DIM}{'.' * (10 - i*3)}{Colors.RESET}")
            time.sleep(1)
            
        input(f"\n{Colors.DIM}Enter를 눌러 어둠 속으로...{Colors.RESET}")
        self.is_running = False
        
    def run(self):
        """게임 실행"""
        while True:
            choice = self.main_menu()
            
            if choice == "1":  # 새 게임
                self.create_character()
                self.location_menu()
                
            elif choice == "2":  # 이어하기
                if self.load_game():
                    time.sleep(1)
                    self.location_menu()
                else:
                    input(f"\n{Colors.DIM}Enter를 눌러 계속...{Colors.RESET}")
                    
            elif choice == "3":  # 종료
                print(f"\n{Colors.DIM}조선의 어둠은 계속됩니다...{Colors.RESET}")
                time.sleep(1)
                break
                
            # 게임 오버 후 리셋
            self.__init__()  # 게임 객체 재초기화


def main():
    """메인 함수"""
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}강제 종료됨{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}오류 발생: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    game = Game()
    while game.is_running:
        choice = game.main_menu()
        if choice == "1":
            game.create_character()
            game.location_menu()
        elif choice == "2":
            if game.load_game():
                game.location_menu()
        elif choice == "3":
            print("게임을 종료합니다.")
            break