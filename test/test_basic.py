"""
基础功能测试脚本
"""
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_imports():
    """测试模块导入"""
    print("测试模块导入...")
    
    try:
        from pypokerengine.players import BasePokerPlayer
        print("✓ PyPokerEngine导入成功")
    except ImportError as e:
        print(f"✗ PyPokerEngine导入失败: {e}")
        return False
    
    try:
        import requests
        print("✓ requests导入成功")
    except ImportError as e:
        print(f"✗ requests导入失败: {e}")
        return False
    
    try:
        from ai_client import AI302Client
        from ai_poker_player import AIPokerPlayer
        from game_state_analyzer import GameStateAnalyzer
        print("✓ 自定义模块导入成功")
    except ImportError as e:
        print(f"✗ 自定义模块导入失败: {e}")
        return False
    
    return True


def test_config():
    """测试配置"""
    print("\n测试配置...")
    
    from config import API_KEY, SUPPORTED_MODELS, GAME_CONFIG
    
    if not API_KEY:
        print("✗ API密钥未设置，请在.env文件中设置API_302_KEY")
        return False
    else:
        print(f"✓ API密钥已设置 (长度: {len(API_KEY)})")
    
    print(f"✓ 支持的模型数量: {len(SUPPORTED_MODELS)}")
    print(f"✓ 游戏配置: {GAME_CONFIG}")
    
    return True


def test_ai_client():
    """测试AI客户端"""
    print("\n测试AI客户端...")
    
    try:
        from ai_client import AI302Client
        
        # 测试客户端创建
        client = AI302Client("claude")
        print("✓ AI客户端创建成功")
        
        # 测试游戏状态分析
        test_game_state = {
            'hole_cards': 'A♠ K♥',
            'community_cards': [],
            'street': 'preflop',
            'my_stack': 1000,
            'pot_size': 30,
            'call_amount': 20,
            'opponents': [
                {'name': 'TestPlayer', 'stack': 980, 'last_action': '跟注 20'}
            ],
            'valid_actions': [
                {'action': 'fold', 'amount': 0},
                {'action': 'call', 'amount': 20},
                {'action': 'raise', 'amount': {'min': 40, 'max': 1000}}
            ]
        }
        
        print("✓ 测试游戏状态构建完成")
        
        # 注意：这里不实际调用API以避免费用
        print("ℹ AI决策测试跳过（避免API费用）")
        
        return True
        
    except Exception as e:
        print(f"✗ AI客户端测试失败: {e}")
        return False


def test_game_state_analyzer():
    """测试游戏状态分析器"""
    print("\n测试游戏状态分析器...")
    
    try:
        from game_state_analyzer import GameStateAnalyzer
        
        # 测试卡牌格式化
        test_cards = ['AS', 'KH', 'QD', 'JC']
        formatted = GameStateAnalyzer._format_cards(test_cards)
        print(f"✓ 卡牌格式化: {test_cards} -> {formatted}")
        
        # 测试手牌强度描述
        hole_cards = ['AS', 'KH']
        community_cards = []
        strength = GameStateAnalyzer.get_hand_strength_description(hole_cards, community_cards)
        print(f"✓ 手牌强度分析: {hole_cards} -> {strength}")
        
        return True
        
    except Exception as e:
        print(f"✗ 游戏状态分析器测试失败: {e}")
        return False


def test_ai_player():
    """测试AI玩家"""
    print("\n测试AI玩家...")
    
    try:
        from ai_poker_player import AIPokerPlayer
        
        # 创建AI玩家（不调用API）
        player = AIPokerPlayer("TestAI", "claude", debug=False)
        print("✓ AI玩家创建成功")
        
        # 测试备用策略
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 20}
        ]
        hole_card = ['AS', 'KH']
        round_state = {
            'street': 'preflop',
            'community_card': [],
            'seats': [{'uuid': 'test-uuid', 'stack': 1000}]
        }
        
        player.player_uuid = 'test-uuid'
        action, amount = player._fallback_strategy(valid_actions, hole_card, round_state)
        print(f"✓ 备用策略测试: {action}, {amount}")
        
        return True
        
    except Exception as e:
        print(f"✗ AI玩家测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("AI德州扑克Demo - 基础功能测试")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_ai_client,
        test_game_state_analyzer,
        test_ai_player
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print(f"测试失败，请检查相关配置")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有基础功能测试通过！可以运行demo.py")
    else:
        print("✗ 部分测试失败，请检查配置和依赖")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
