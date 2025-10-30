"""
德州扑克牌桌终端输出模拟器
显示牌桌、手牌、公牌、选手信息等
"""
import random
from typing import List, Dict, Optional
from colorama import init, Fore, Back, Style
import time

# 初始化colorama
init()

class Card:
    """扑克牌类"""
    
    SUITS = ['S', 'H', 'D', 'C']  # Spades, Hearts, Diamonds, Clubs
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        # 根据花色设置颜色
        if self.suit in ['H', 'D']:  # Hearts, Diamonds
            return f"{Fore.RED}{self.rank}{self.suit}{Style.RESET_ALL}"
        else:  # Spades, Clubs
            return f"{Fore.BLACK}{self.rank}{self.suit}{Style.RESET_ALL}"
    
    def __repr__(self):
        return f"Card({self.suit}, {self.rank})"
    
    @classmethod
    def create_deck(cls) -> List['Card']:
        """创建一副完整的扑克牌"""
        deck = []
        for suit in cls.SUITS:
            for rank in cls.RANKS:
                deck.append(cls(suit, rank))
        return deck


class Player:
    """玩家类"""
    
    def __init__(self, player_id: str, name: str, chips: int, position: int):
        self.player_id = player_id
        self.name = name
        self.chips = chips
        self.position = position  # 座位位置 (0-5)
        self.hole_cards: List[Card] = []
        self.current_bet = 0
        self.is_folded = False
        self.is_all_in = False
        self.last_action = "等待"
        self.is_dealer = False
        self.is_small_blind = False
        self.is_big_blind = False
    
    def __str__(self):
        status_icons = []
        if self.is_dealer:
            status_icons.append("D")  # 庄家按钮
        if self.is_small_blind:
            status_icons.append("SB")
        if self.is_big_blind:
            status_icons.append("BB")
        if self.is_folded:
            status_icons.append("FOLD")
        if self.is_all_in:
            status_icons.append("ALL-IN")
        
        status_str = " ".join(status_icons)
        return f"{self.name} ({status_str})" if status_icons else self.name


class PokerTableSimulator:
    """德州扑克牌桌模拟器"""
    
    def __init__(self):
        self.players: List[Player] = []
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.small_blind = 10
        self.big_blind = 20
        self.dealer_position = 0
        self.current_street = "preflop"  # preflop, flop, turn, river
        self.deck: List[Card] = []
        
        # 街道名称映射
        self.street_names = {
            "preflop": "翻牌前",
            "flop": "翻牌",
            "turn": "转牌",
            "river": "河牌"
        }
    
    def add_player(self, player_id: str, name: str, chips: int, position: int):
        """添加玩家"""
        player = Player(player_id, name, chips, position)
        self.players.append(player)
        return player
    
    def setup_new_hand(self):
        """设置新一手牌"""
        # 重置牌桌状态
        self.deck = Card.create_deck()
        random.shuffle(self.deck)
        self.community_cards = []
        self.pot = 0
        self.current_bet = self.big_blind
        self.current_street = "preflop"
        
        # 重置玩家状态
        for player in self.players:
            player.hole_cards = []
            player.current_bet = 0
            player.is_folded = False
            player.is_all_in = False
            player.last_action = "等待"
            player.is_dealer = False
            player.is_small_blind = False
            player.is_big_blind = False
        
        # 设置盲注位置
        if len(self.players) >= 2:
            self.players[self.dealer_position].is_dealer = True
            
            sb_pos = (self.dealer_position + 1) % len(self.players)
            bb_pos = (self.dealer_position + 2) % len(self.players)
            
            self.players[sb_pos].is_small_blind = True
            self.players[sb_pos].current_bet = self.small_blind
            self.players[sb_pos].chips -= self.small_blind
            self.players[sb_pos].last_action = f"小盲注 {self.small_blind}"
            
            self.players[bb_pos].is_big_blind = True
            self.players[bb_pos].current_bet = self.big_blind
            self.players[bb_pos].chips -= self.big_blind
            self.players[bb_pos].last_action = f"大盲注 {self.big_blind}"
            
            self.pot = self.small_blind + self.big_blind
        
        # 发手牌
        for _ in range(2):
            for player in self.players:
                if not player.is_folded:
                    player.hole_cards.append(self.deck.pop())
    
    def deal_flop(self):
        """发翻牌"""
        self.current_street = "flop"
        self.deck.pop()  # 烧牌
        for _ in range(3):
            self.community_cards.append(self.deck.pop())
    
    def deal_turn(self):
        """发转牌"""
        self.current_street = "turn"
        self.deck.pop()  # 烧牌
        self.community_cards.append(self.deck.pop())
    
    def deal_river(self):
        """发河牌"""
        self.current_street = "river"
        self.deck.pop()  # 烧牌
        self.community_cards.append(self.deck.pop())
    
    def simulate_action(self, player: Player):
        """模拟玩家行动"""
        if player.is_folded:
            return
        
        # 简单的随机行动模拟
        actions = ["fold", "call", "raise"]
        weights = [0.3, 0.5, 0.2]  # 弃牌30%, 跟注50%, 加注20%
        
        # 根据手牌强度调整概率
        if len(player.hole_cards) == 2:
            # 简单的手牌评估
            card1, card2 = player.hole_cards
            if card1.rank == card2.rank:  # 对子
                weights = [0.1, 0.4, 0.5]  # 更倾向于加注
            elif card1.suit == card2.suit:  # 同花
                weights = [0.2, 0.5, 0.3]
        
        action = random.choices(actions, weights=weights)[0]
        
        if action == "fold":
            player.is_folded = True
            player.last_action = "弃牌"
        elif action == "call":
            call_amount = max(0, self.current_bet - player.current_bet)
            if call_amount >= player.chips:
                # 全下
                self.pot += player.chips
                player.current_bet += player.chips
                player.chips = 0
                player.is_all_in = True
                player.last_action = "全下"
            else:
                player.chips -= call_amount
                player.current_bet += call_amount
                self.pot += call_amount
                player.last_action = f"跟注 {call_amount}" if call_amount > 0 else "过牌"
        elif action == "raise":
            # 随机加注金额
            min_raise = self.current_bet * 2
            max_raise = min(player.chips + player.current_bet, self.current_bet * 4)
            
            if max_raise > min_raise:
                raise_amount = random.randint(min_raise, max_raise)
                bet_amount = raise_amount - player.current_bet
                
                if bet_amount >= player.chips:
                    # 全下
                    self.pot += player.chips
                    player.current_bet += player.chips
                    player.chips = 0
                    player.is_all_in = True
                    player.last_action = "全下"
                else:
                    player.chips -= bet_amount
                    player.current_bet = raise_amount
                    self.pot += bet_amount
                    self.current_bet = raise_amount
                    player.last_action = f"加注至 {raise_amount}"
            else:
                # 无法加注，改为跟注
                call_amount = max(0, self.current_bet - player.current_bet)
                if call_amount > 0:
                    player.chips -= call_amount
                    player.current_bet += call_amount
                    self.pot += call_amount
                    player.last_action = f"跟注 {call_amount}"
                else:
                    player.last_action = "过牌"
    
    def print_table(self, show_hole_cards: bool = False):
        """打印牌桌状态"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"*** 德州扑克牌桌模拟 - {self.street_names[self.current_street]}阶段 ***")
        print(f"{'='*80}{Style.RESET_ALL}")
        
        # 显示底池信息
        print(f"\n{Fore.YELLOW}[底池信息]:{Style.RESET_ALL}")
        print(f"   总底池: {Fore.GREEN}{self.pot}{Style.RESET_ALL} 筹码")
        print(f"   当前下注: {Fore.CYAN}{self.current_bet}{Style.RESET_ALL} 筹码")
        print(f"   小盲注/大盲注: {self.small_blind}/{self.big_blind}")
        
        # 显示公共牌
        print(f"\n{Fore.YELLOW}[公共牌] ({len(self.community_cards)}/5):{Style.RESET_ALL}")
        if self.community_cards:
            cards_str = "   "
            for i, card in enumerate(self.community_cards):
                cards_str += f"[{card}] "
                if i == 2:  # 翻牌后加个分隔
                    cards_str += "| "
            print(cards_str)
        else:
            print("   (暂无公共牌)")
        
        # 显示玩家信息
        print(f"\n{Fore.YELLOW}[玩家信息]:{Style.RESET_ALL}")
        print(f"{'位置':<4} {'玩家名':<15} {'筹码':<8} {'当前下注':<8} {'手牌':<20} {'最后行动':<15}")
        print(f"{'-'*80}")
        
        for i, player in enumerate(self.players):
            # 位置信息
            pos_str = f"{player.position}"
            
            # 玩家名称和状态
            name_str = str(player)
            if player.is_folded:
                name_str = f"{Fore.RED}{name_str}{Style.RESET_ALL}"
            elif player.is_all_in:
                name_str = f"{Fore.MAGENTA}{name_str}{Style.RESET_ALL}"
            else:
                name_str = f"{Fore.WHITE}{name_str}{Style.RESET_ALL}"
            
            # 筹码信息
            chips_str = f"{player.chips}"
            if player.chips == 0:
                chips_str = f"{Fore.RED}{chips_str}{Style.RESET_ALL}"
            elif player.chips < 1000:
                chips_str = f"{Fore.YELLOW}{chips_str}{Style.RESET_ALL}"
            else:
                chips_str = f"{Fore.GREEN}{chips_str}{Style.RESET_ALL}"
            
            # 当前下注
            bet_str = f"{player.current_bet}" if player.current_bet > 0 else "-"
            
            # 手牌显示 - 弃牌后仍显示手牌，不覆盖
            if show_hole_cards and player.hole_cards:
                # 显示手牌，弃牌的玩家手牌用灰色显示
                if player.is_folded:
                    hole_cards_str = f"{Fore.LIGHTBLACK_EX}[{player.hole_cards[0]}] [{player.hole_cards[1]}]{Style.RESET_ALL}"
                else:
                    hole_cards_str = f"[{player.hole_cards[0]}] [{player.hole_cards[1]}]"
            elif player.hole_cards:
                # 隐藏手牌模式，弃牌的玩家用灰色背面
                if player.is_folded:
                    hole_cards_str = f"{Fore.LIGHTBLACK_EX}[**] [**]{Style.RESET_ALL}"
                else:
                    hole_cards_str = "[**] [**]"  # 背面
            else:
                hole_cards_str = "-"
            
            # 最后行动
            action_str = player.last_action
            if "弃牌" in action_str:
                action_str = f"{Fore.RED}{action_str}{Style.RESET_ALL}"
            elif "加注" in action_str or "全下" in action_str:
                action_str = f"{Fore.CYAN}{action_str}{Style.RESET_ALL}"
            elif "跟注" in action_str:
                action_str = f"{Fore.GREEN}{action_str}{Style.RESET_ALL}"
            
            print(f"{pos_str:<4} {name_str:<25} {chips_str:<8} {bet_str:<8} {hole_cards_str:<30} {action_str:<25}")
        
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
    
    def simulate_hand(self, show_hole_cards: bool = False, auto_play: bool = True):
        """模拟一手牌"""
        print(f"\n{Fore.MAGENTA}*** 开始新一手牌 ***{Style.RESET_ALL}")
        
        # 设置新手牌
        self.setup_new_hand()
        
        # 翻牌前
        self.print_table(show_hole_cards)
        
        if auto_play:
            print(f"\n{Fore.YELLOW}[ACTION] 翻牌前下注轮...{Style.RESET_ALL}")
            time.sleep(1)
            
            # 模拟翻牌前行动
            active_players = [p for p in self.players if not p.is_folded]
            for player in active_players:
                if not player.is_big_blind:  # 大盲注已经行动过了
                    self.simulate_action(player)
            
            self.print_table(show_hole_cards)
        
        # 翻牌
        if len([p for p in self.players if not p.is_folded]) > 1:
            if auto_play:
                print(f"\n{Fore.YELLOW}[DEAL] 发翻牌...{Style.RESET_ALL}")
                time.sleep(1)
            
            self.deal_flop()
            self.current_bet = 0
            for player in self.players:
                player.current_bet = 0
            
            self.print_table(show_hole_cards)
            
            if auto_play:
                print(f"\n{Fore.YELLOW}[ACTION] 翻牌后下注轮...{Style.RESET_ALL}")
                time.sleep(1)
                
                # 模拟翻牌后行动
                active_players = [p for p in self.players if not p.is_folded]
                for player in active_players:
                    self.simulate_action(player)
                
                self.print_table(show_hole_cards)
        
        # 转牌
        if len([p for p in self.players if not p.is_folded]) > 1:
            if auto_play:
                print(f"\n{Fore.YELLOW}[DEAL] 发转牌...{Style.RESET_ALL}")
                time.sleep(1)
            
            self.deal_turn()
            self.current_bet = 0
            for player in self.players:
                player.current_bet = 0
            
            self.print_table(show_hole_cards)
            
            if auto_play:
                print(f"\n{Fore.YELLOW}[ACTION] 转牌后下注轮...{Style.RESET_ALL}")
                time.sleep(1)
                
                # 模拟转牌后行动
                active_players = [p for p in self.players if not p.is_folded]
                for player in active_players:
                    self.simulate_action(player)
                
                self.print_table(show_hole_cards)
        
        # 河牌
        if len([p for p in self.players if not p.is_folded]) > 1:
            if auto_play:
                print(f"\n{Fore.YELLOW}[DEAL] 发河牌...{Style.RESET_ALL}")
                time.sleep(1)
            
            self.deal_river()
            self.current_bet = 0
            for player in self.players:
                player.current_bet = 0
            
            self.print_table(show_hole_cards)
            
            if auto_play:
                print(f"\n{Fore.YELLOW}[ACTION] 河牌后下注轮...{Style.RESET_ALL}")
                time.sleep(1)
                
                # 模拟河牌后行动
                active_players = [p for p in self.players if not p.is_folded]
                for player in active_players:
                    self.simulate_action(player)
                
                self.print_table(show_hole_cards)
        
        # 显示最终结果
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) > 1:
            print(f"\n{Fore.GREEN}[SHOWDOWN] 摊牌阶段 - 显示所有手牌:{Style.RESET_ALL}")
            self.print_table(show_hole_cards=True)
            
            # 随机选择获胜者
            winner = random.choice(active_players)
            winner.chips += self.pot
            print(f"\n{Fore.GREEN}[WINNER] 获胜者: {winner.name} 赢得 {self.pot} 筹码!{Style.RESET_ALL}")
        elif len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.pot
            print(f"\n{Fore.GREEN}[WINNER] {winner.name} 赢得底池 {self.pot} 筹码! (其他玩家弃牌){Style.RESET_ALL}")
        
        # 移动庄家按钮
        self.dealer_position = (self.dealer_position + 1) % len(self.players)


def create_sample_table():
    """创建示例牌桌"""
    simulator = PokerTableSimulator()
    
    # 添加6个玩家
    players_data = [
        ("P1", "Claude_AI", 15000, 0),
        ("P2", "GPT_AI", 18500, 1), 
        ("P3", "Gemini_AI", 12300, 2),
        ("P4", "Grok_AI", 22100, 3),
        ("P5", "DeepSeek_AI", 9800, 4),
        ("P6", "Qwen_AI", 16400, 5)
    ]
    
    for player_id, name, chips, position in players_data:
        simulator.add_player(player_id, name, chips, position)
    
    return simulator


def main():
    """主函数 - 演示模拟器"""
    print(f"{Fore.CYAN}*** 德州扑克牌桌终端模拟器 ***{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}======================================={Style.RESET_ALL}")
    
    # 创建示例牌桌
    table = create_sample_table()
    
    print(f"\n{Fore.GREEN}[OK] 牌桌创建完成，6名AI玩家就位{Style.RESET_ALL}")
    
    while True:
        print(f"\n{Fore.YELLOW}请选择操作:{Style.RESET_ALL}")
        print("1. 模拟一手牌 (隐藏手牌)")
        print("2. 模拟一手牌 (显示手牌)")
        print("3. 只显示当前牌桌状态")
        print("4. 重置牌桌")
        print("5. 退出")
        
        choice = input(f"\n{Fore.CYAN}请输入选择 (1-5): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            table.simulate_hand(show_hole_cards=False, auto_play=True)
        elif choice == "2":
            table.simulate_hand(show_hole_cards=True, auto_play=True)
        elif choice == "3":
            table.print_table(show_hole_cards=True)
        elif choice == "4":
            table = create_sample_table()
            print(f"{Fore.GREEN}[OK] 牌桌已重置{Style.RESET_ALL}")
        elif choice == "5":
            print(f"{Fore.YELLOW}感谢使用德州扑克模拟器!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}[ERROR] 无效选择，请重新输入{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
