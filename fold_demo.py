"""
弃牌功能演示 - 展示弃牌后仍显示手牌的效果
"""
from poker_table_simulator import PokerTableSimulator, create_sample_table
from colorama import init, Fore, Style

# 初始化colorama
init()

def fold_demo():
    """演示弃牌功能的改进"""
    
    print(f"{Fore.CYAN}*** 弃牌功能演示 ***{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}展示弃牌后仍显示手牌的效果{Style.RESET_ALL}")
    print("=" * 50)
    
    # 创建示例牌桌
    table = create_sample_table()
    table.setup_new_hand()
    
    print(f"\n{Fore.GREEN}[步骤1] 所有玩家都有手牌{Style.RESET_ALL}")
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.YELLOW}[步骤2] 模拟部分玩家弃牌{Style.RESET_ALL}")
    # 让几个玩家弃牌
    table.players[1].is_folded = True
    table.players[1].last_action = "弃牌"
    
    table.players[3].is_folded = True  
    table.players[3].last_action = "弃牌"
    
    table.players[5].is_folded = True
    table.players[5].last_action = "弃牌"
    
    # 其他玩家有行动
    table.players[0].last_action = "跟注 20"
    table.players[2].last_action = "加注至 50"
    table.players[4].last_action = "跟注 50"
    
    print(f"\n{Fore.GREEN}[结果] 弃牌玩家仍显示手牌{Style.RESET_ALL}")
    table.print_table(show_hole_cards=True)
    
    print(f"\n{Fore.CYAN}*** 关键改进说明 ***{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}改进前:{Style.RESET_ALL}")
    print("  弃牌玩家手牌位置显示: [弃牌]")
    print("  问题: 无法看到弃牌玩家的具体手牌")
    
    print(f"\n{Fore.GREEN}改进后:{Style.RESET_ALL}")
    print("  弃牌玩家手牌位置显示: 实际手牌 (灰色)")
    print("  弃牌状态显示在: 最后行动列 (红色)")
    print("  优势: 可以看到所有玩家的手牌，便于分析")
    
    print(f"\n{Fore.MAGENTA}*** 演示完成 ***{Style.RESET_ALL}")

if __name__ == "__main__":
    fold_demo()

