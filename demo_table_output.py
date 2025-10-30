"""
德州扑克牌桌输出演示脚本
展示各种牌桌状态的终端输出效果
"""
from poker_table_simulator import PokerTableSimulator, create_sample_table
from colorama import init, Fore, Style
import time

# 初始化colorama
init()

def demo_table_states():
    """演示不同的牌桌状态"""
    
    print(f"{Fore.CYAN}*** 德州扑克牌桌终端输出演示 ***{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}======================================={Style.RESET_ALL}")
    
    # 创建示例牌桌
    table = create_sample_table()
    
    print(f"\n{Fore.GREEN}[演示1] 初始牌桌状态{Style.RESET_ALL}")
    print("=" * 50)
    table.print_table(show_hole_cards=False)
    
    print(f"\n{Fore.GREEN}[演示2] 翻牌前阶段 (发手牌后){Style.RESET_ALL}")
    print("=" * 50)
    table.setup_new_hand()
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.GREEN}[演示3] 翻牌阶段{Style.RESET_ALL}")
    print("=" * 50)
    table.deal_flop()
    # 模拟一些玩家行动
    table.players[0].last_action = "跟注 20"
    table.players[0].current_bet = 20
    table.players[0].chips -= 20
    table.players[1].last_action = "加注至 60"
    table.players[1].current_bet = 60
    table.players[1].chips -= 60
    table.players[2].last_action = "弃牌"
    table.players[2].is_folded = True
    table.players[3].last_action = "跟注 60"
    table.players[3].current_bet = 60
    table.players[3].chips -= 60
    table.players[4].last_action = "全下"
    table.players[4].is_all_in = True
    table.players[4].current_bet = table.players[4].chips
    table.players[4].chips = 0
    table.players[5].last_action = "跟注 60"
    table.players[5].current_bet = 60
    table.players[5].chips -= 60
    
    table.pot = 20 + 60 + 60 + table.players[4].current_bet + 60 + table.small_blind + table.big_blind
    table.current_bet = 60
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.GREEN}[演示4] 转牌阶段{Style.RESET_ALL}")
    print("=" * 50)
    table.deal_turn()
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.GREEN}[演示5] 河牌阶段{Style.RESET_ALL}")
    print("=" * 50)
    table.deal_river()
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.MAGENTA}*** 演示完成! ***{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}特色功能:{Style.RESET_ALL}")
    print("+ 彩色扑克牌显示 (红桃/方块为红色，黑桃/梅花为黑色)")
    print("+ 玩家状态标识 (庄家、小盲注SB、大盲注BB、弃牌、全下)")
    print("+ 筹码状态颜色 (充足=绿色、不足=黄色、全下=红色)")
    print("+ 行动状态颜色 (弃牌=红色、加注=青色、跟注=绿色)")
    print("+ 完整的游戏信息 (底池、当前下注、盲注、公共牌、手牌)")
    print("+ 支持隐藏/显示手牌模式")

def demo_single_hand():
    """演示完整的一手牌流程"""
    print(f"\n{Fore.CYAN}*** 完整一手牌演示 ***{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}======================================={Style.RESET_ALL}")
    
    table = create_sample_table()
    table.simulate_hand(show_hole_cards=True, auto_play=False)

if __name__ == "__main__":
    # 演示不同的牌桌状态
    demo_table_states()
    
    # 询问是否演示完整一手牌
    print(f"\n{Fore.YELLOW}是否演示完整的一手牌流程? (y/n): {Style.RESET_ALL}", end="")
    if input().strip().lower() in ['y', 'yes', '']:
        demo_single_hand()
