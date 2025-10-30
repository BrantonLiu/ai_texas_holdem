"""
德州扑克牌桌输出简单演示
展示终端输出效果，无需用户交互
"""
from poker_table_simulator import PokerTableSimulator, create_sample_table
from colorama import init, Fore, Style

# 初始化colorama
init()

def simple_demo():
    """简单演示德州扑克牌桌输出"""
    
    print(f"{Fore.CYAN}*** 德州扑克牌桌终端输出演示 ***{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}======================================={Style.RESET_ALL}")
    
    # 创建示例牌桌
    table = create_sample_table()
    
    print(f"\n{Fore.GREEN}[演示] 翻牌前阶段 (发手牌后){Style.RESET_ALL}")
    print("=" * 50)
    table.setup_new_hand()
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.GREEN}[演示] 翻牌阶段{Style.RESET_ALL}")
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
    
    print(f"\n{Fore.GREEN}[演示] 河牌阶段{Style.RESET_ALL}")
    print("=" * 50)
    table.deal_turn()
    table.deal_river()
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.MAGENTA}*** 演示完成! ***{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}特色功能:{Style.RESET_ALL}")
    print("+ 彩色扑克牌显示 (红桃H/方块D为红色，黑桃S/梅花C为黑色)")
    print("+ 玩家状态标识 (庄家D、小盲注SB、大盲注BB、弃牌FOLD、全下ALL-IN)")
    print("+ 筹码状态颜色 (充足=绿色、不足=黄色、全下=红色)")
    print("+ 行动状态颜色 (弃牌=红色、加注=青色、跟注=绿色)")
    print("+ 完整的游戏信息 (底池、当前下注、盲注、公共牌、手牌)")
    print("+ 支持隐藏/显示手牌模式")
    print("+ 弃牌后仍显示手牌 (弃牌玩家的手牌显示为灰色)")
    
    print(f"\n{Fore.CYAN}牌桌信息说明:{Style.RESET_ALL}")
    print("位置: 玩家在牌桌上的座位号 (0-5)")
    print("玩家名: AI模型名称 + 状态标识")
    print("筹码: 当前持有的筹码数量")
    print("当前下注: 本轮已下注的金额")
    print("手牌: 玩家的两张底牌 (格式: [牌面花色])")
    print("最后行动: 玩家的最近一次行动")
    
    print(f"\n{Fore.CYAN}扑克牌表示:{Style.RESET_ALL}")
    print("花色: S=黑桃, H=红桃, D=方块, C=梅花")
    print("牌面: 2-10, J=Jack, Q=Queen, K=King, A=Ace")
    print("颜色: 红桃和方块显示为红色，黑桃和梅花显示为黑色")

if __name__ == "__main__":
    simple_demo()
