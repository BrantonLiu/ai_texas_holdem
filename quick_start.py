"""
快速启动脚本 - 使用预设配置快速开始游戏
"""
import os
from pypokerengine.api.game import setup_config, start_poker
from ai_poker_player import AIPokerPlayer
from config import GAME_CONFIG


def quick_demo():
    """快速演示 - 使用3个不同的AI模型"""
    print("🎮 AI德州扑克快速演示")
    print("=" * 40)
    
    # 检查API密钥
    from config import API_KEY
    if not API_KEY:
        print("❌ 错误: 请先设置API密钥")
        print("1. 复制 env_example.txt 为 .env")
        print("2. 在 .env 中设置 API_302_KEY=your_key")
        return
    
    # 创建3个AI玩家使用不同模型
    models = ["claude", "gpt", "gemini"]  # 选择3个较稳定的模型
    players = []
    
    print("🤖 正在创建AI玩家...")
    for model in models:
        try:
            player = AIPokerPlayer(
                name=f"{model.upper()}_AI",
                model_type=model,
                debug=True
            )
            players.append(player)
            print(f"  ✓ {model.upper()}_AI 创建成功")
        except Exception as e:
            print(f"  ❌ {model.upper()}_AI 创建失败: {e}")
    
    if len(players) < 2:
        print("❌ 需要至少2个AI玩家才能开始游戏")
        return
    
    # 设置游戏
    print(f"\n🎯 游戏设置:")
    print(f"  参与玩家: {', '.join([p.name for p in players])}")
    print(f"  最大轮数: {GAME_CONFIG['max_round']}")
    print(f"  初始筹码: {GAME_CONFIG['initial_stack']}")
    print(f"  小盲注: {GAME_CONFIG['small_blind_amount']}")
    
    # 配置PyPokerEngine
    config = setup_config(
        max_round=GAME_CONFIG['max_round'],
        initial_stack=GAME_CONFIG['initial_stack'],
        small_blind_amount=GAME_CONFIG['small_blind_amount']
    )
    
    # 注册玩家
    for player in players:
        config.register_player(name=player.name, algorithm=player)
    
    print(f"\n🚀 开始游戏...")
    print("=" * 40)
    
    # 开始游戏
    try:
        game_result = start_poker(config, verbose=1)
        
        # 显示结果
        print("\n🏆 游戏结果:")
        print("=" * 40)
        
        sorted_players = sorted(game_result['players'], key=lambda x: x['stack'], reverse=True)
        
        for i, player_info in enumerate(sorted_players, 1):
            name = player_info['name']
            stack = player_info['stack']
            initial = GAME_CONFIG['initial_stack']
            profit = stack - initial
            
            status = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"{status} {i}. {name:12s} - 筹码: {stack:4d} (盈亏: {profit:+4d})")
        
        print("=" * 40)
        print("🎉 游戏结束!")
        
    except Exception as e:
        print(f"❌ 游戏异常: {e}")


if __name__ == "__main__":
    quick_demo()

