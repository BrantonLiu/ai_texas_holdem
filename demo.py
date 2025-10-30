"""
AI德州扑克Demo - 多个大模型AI对战演示
"""
import sys
import time
from pypokerengine.api.game import setup_config, start_poker
from colorama import init, Fore, Style

from ai_poker_player import AIPokerPlayer
from config import GAME_CONFIG, SUPPORTED_MODELS

# 初始化colorama用于彩色输出
init()


def print_banner():
    """打印程序横幅"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║                    AI德州扑克大模型对战Demo                      ║
║                  基于PyPokerEngine + 302.AI                   ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}支持的AI模型:{Style.RESET_ALL}
"""
    
    for i, (key, model_info) in enumerate(SUPPORTED_MODELS.items(), 1):
        banner += f"{i:2d}. {key:10s} - {model_info['model_name']}\n"
    
    print(banner)


def select_models():
    """选择参与对战的AI模型"""
    model_keys = list(SUPPORTED_MODELS.keys())
    max_models = min(10, len(model_keys))  # 最多支持10个模型
    
    print(f"\n{Fore.GREEN}请选择参与对战的AI模型 (输入数字，用空格分隔，至少2个，最多{max_models}个):{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}提示: 输入 'all' 或 'a' 可选择所有模型 (共{len(model_keys)}个){Style.RESET_ALL}")
    
    while True:
        try:
            user_input = input("选择模型 (例如: 1 2 3 或 all): ").strip().lower()
            if not user_input:
                print(f"{Fore.RED}请至少选择2个模型{Style.RESET_ALL}")
                continue
            
            # 处理全选选项
            if user_input in ['all', 'a']:
                selected_models = model_keys[:max_models]
                if len(model_keys) > max_models:
                    print(f"{Fore.YELLOW}注意: 已选择前{max_models}个模型 (共{len(model_keys)}个可用){Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}已选择所有{len(selected_models)}个模型{Style.RESET_ALL}")
                return selected_models
            
            # 处理数字选择
            indices = [int(x) - 1 for x in user_input.split()]
            
            if len(indices) < 2:
                print(f"{Fore.RED}请至少选择2个模型{Style.RESET_ALL}")
                continue
            
            if len(indices) > max_models:
                print(f"{Fore.RED}最多支持{max_models}个模型同时对战{Style.RESET_ALL}")
                continue
            
            selected_models = []
            invalid_indices = []
            for idx in indices:
                if 0 <= idx < len(model_keys):
                    if model_keys[idx] not in selected_models:  # 避免重复选择
                        selected_models.append(model_keys[idx])
                    else:
                        print(f"{Fore.YELLOW}警告: 模型 {idx + 1} ({model_keys[idx]}) 已选择，已跳过{Style.RESET_ALL}")
                else:
                    invalid_indices.append(idx + 1)
            
            if invalid_indices:
                print(f"{Fore.RED}无效的选择: {', '.join(map(str, invalid_indices))}{Style.RESET_ALL}")
                continue
            
            if len(selected_models) < 2:
                print(f"{Fore.RED}请至少选择2个不同的模型{Style.RESET_ALL}")
                continue
            
            return selected_models
                
        except ValueError:
            print(f"{Fore.RED}请输入有效的数字，或输入 'all'/'a' 全选{Style.RESET_ALL}")


def setup_game_config(selected_models):
    """设置游戏配置"""
    print(f"\n{Fore.GREEN}游戏配置:{Style.RESET_ALL}")
    
    # 使用默认配置或让用户自定义
    use_default = input("使用默认配置? (y/n, 默认y): ").strip().lower()
    
    if use_default in ['', 'y', 'yes']:
        config = GAME_CONFIG.copy()
    else:
        config = {}
        config['max_round'] = int(input(f"最大轮数 (默认{GAME_CONFIG['max_round']}): ") 
                                 or GAME_CONFIG['max_round'])
        config['initial_stack'] = int(input(f"初始筹码 (默认{GAME_CONFIG['initial_stack']}): ") 
                                      or GAME_CONFIG['initial_stack'])
        config['small_blind_amount'] = int(input(f"小盲注 (默认{GAME_CONFIG['small_blind_amount']}): ") 
                                          or GAME_CONFIG['small_blind_amount'])
    
    print(f"\n{Fore.CYAN}游戏设置:{Style.RESET_ALL}")
    print(f"  最大轮数: {config['max_round']}")
    print(f"  初始筹码: {config['initial_stack']}")
    print(f"  小盲注: {config['small_blind_amount']}")
    print(f"  参与模型: {', '.join(selected_models)}")
    
    return config


def create_ai_players(selected_models):
    """创建AI玩家"""
    players = []
    
    print(f"\n{Fore.GREEN}正在初始化AI玩家...{Style.RESET_ALL}")
    
    for i, model_type in enumerate(selected_models):
        player_name = f"{model_type.upper()}_AI"
        print(f"  创建玩家: {player_name} (使用{model_type}模型)")
        
        try:
            player = AIPokerPlayer(
                name=player_name,
                model_type=model_type,
                debug=True
            )
            players.append(player)
            print(f"    ✓ {player_name} 创建成功")
            
        except Exception as e:
            print(f"    ✗ {player_name} 创建失败: {str(e)}")
            print(f"    {Fore.YELLOW}跳过该模型{Style.RESET_ALL}")
    
    return players


def run_poker_game(players, game_config):
    """运行扑克游戏"""
    if len(players) < 2:
        print(f"{Fore.RED}需要至少2个玩家才能开始游戏{Style.RESET_ALL}")
        return None
    
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"开始AI德州扑克对战!")
    print(f"参与玩家: {', '.join([p.name for p in players])}")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    # 设置PyPokerEngine配置
    config = setup_config(
        max_round=game_config['max_round'],
        initial_stack=game_config['initial_stack'],
        small_blind_amount=game_config['small_blind_amount']
    )
    
    # 注册玩家
    for player in players:
        config.register_player(name=player.name, algorithm=player)
    
    # 开始游戏
    try:
        print(f"\n{Fore.CYAN}游戏开始...{Style.RESET_ALL}")
        start_time = time.time()
        
        game_result = start_poker(config, verbose=1)
        
        end_time = time.time()
        game_duration = end_time - start_time
        
        print(f"\n{Fore.GREEN}{'='*60}")
        print(f"游戏结束! 用时: {game_duration:.2f}秒")
        print(f"{'='*60}{Style.RESET_ALL}")
        
        return game_result
        
    except Exception as e:
        print(f"{Fore.RED}游戏运行异常: {str(e)}{Style.RESET_ALL}")
        return None


def display_game_results(game_result, players):
    """显示游戏结果"""
    if not game_result:
        return
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"最终结果")
    print(f"{'='*60}{Style.RESET_ALL}")
    
    # 按筹码排序
    sorted_players = sorted(game_result['players'], key=lambda x: x['stack'], reverse=True)
    
    print(f"\n{Fore.YELLOW}排名:{Style.RESET_ALL}")
    for i, player_info in enumerate(sorted_players, 1):
        name = player_info['name']
        stack = player_info['stack']
        initial_stack = game_result['rule']['initial_stack']
        profit = stack - initial_stack
        profit_rate = (profit / initial_stack) * 100
        
        # 根据盈亏设置颜色
        if profit > 0:
            color = Fore.GREEN
            symbol = "↑"
        elif profit < 0:
            color = Fore.RED
            symbol = "↓"
        else:
            color = Fore.YELLOW
            symbol = "="
        
        print(f"{i:2d}. {name:15s} - "
              f"筹码: {stack:6d} "
              f"{color}{symbol} {profit:+6d} ({profit_rate:+6.1f}%){Style.RESET_ALL}")
    
    # 显示游戏统计
    print(f"\n{Fore.CYAN}游戏统计:{Style.RESET_ALL}")
    print(f"  总轮数: {game_result['rule']['max_round']}")
    print(f"  初始筹码: {game_result['rule']['initial_stack']}")
    print(f"  小盲注: {game_result['rule']['small_blind_amount']}")
    
    # 显示AI决策统计
    print(f"\n{Fore.CYAN}AI决策统计:{Style.RESET_ALL}")
    for player in players:
        if hasattr(player, 'game_history') and player.game_history:
            history = player.game_history
            total_decisions = len(history)
            
            actions = [h['final_action'] for h in history]
            fold_count = actions.count('fold')
            call_count = actions.count('call')
            raise_count = actions.count('raise')
            
            print(f"  {player.name:15s} - "
                  f"决策次数: {total_decisions:3d}, "
                  f"弃牌: {fold_count:2d}, "
                  f"跟注: {call_count:2d}, "
                  f"加注: {raise_count:2d}")


def main():
    """主函数"""
    print_banner()
    
    # 检查API密钥
    from config import API_KEY
    if not API_KEY:
        print(f"{Fore.RED}错误: 请在.env文件中设置API_302_KEY{Style.RESET_ALL}")
        print("创建.env文件并添加: API_302_KEY=your_api_key_here")
        return
    
    try:
        # 选择模型
        selected_models = select_models()
        if not selected_models:
            print(f"{Fore.RED}未选择任何模型，退出程序{Style.RESET_ALL}")
            return
        
        # 设置游戏配置
        game_config = setup_game_config(selected_models)
        
        # 创建AI玩家
        players = create_ai_players(selected_models)
        if len(players) < 2:
            print(f"{Fore.RED}可用玩家不足，无法开始游戏{Style.RESET_ALL}")
            return
        
        # 确认开始游戏
        print(f"\n{Fore.YELLOW}准备就绪! 按Enter开始游戏，或输入'q'退出:{Style.RESET_ALL}")
        user_input = input().strip().lower()
        if user_input == 'q':
            print("退出程序")
            return
        
        # 运行游戏
        game_result = run_poker_game(players, game_config)
        
        # 显示结果
        display_game_results(game_result, players)
        
        # 询问是否再次游戏
        print(f"\n{Fore.YELLOW}是否再次游戏? (y/n):{Style.RESET_ALL}")
        if input().strip().lower() in ['y', 'yes']:
            main()
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}游戏被用户中断{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}程序异常: {str(e)}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()


