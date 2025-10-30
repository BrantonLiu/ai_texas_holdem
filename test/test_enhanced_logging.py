"""
增强日志功能测试脚本
"""
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_enhanced_logging():
    """测试增强的日志输出功能"""
    print("🧪 测试增强日志功能")
    print("=" * 60)
    
    try:
        from ai_client import AI302Client
        from ai_poker_player import AIPokerPlayer
        from game_state_analyzer import GameStateAnalyzer
        from config import API_KEY
        
        if not API_KEY:
            print("⚠️  警告: API密钥未设置，将跳过实际API调用测试")
            print("💡 提示: 在.env文件中设置API_302_KEY来启用完整测试")
        
        # 创建测试用的AI玩家
        print("\n🤖 创建测试AI玩家...")
        player = AIPokerPlayer("TEST_CLAUDE_AI", "claude", debug=True)
        print("✅ AI玩家创建成功")
        
        # 模拟游戏开始消息
        print("\n📋 测试游戏开始消息...")
        game_start_info = {
            'player_num': 3,
            'rule': {
                'max_round': 5,
                'small_blind_amount': 10,
                'initial_stack': 1000
            },
            'seats': [
                {'name': 'TEST_CLAUDE_AI', 'uuid': 'test-uuid-1'},
                {'name': 'TEST_GPT_AI', 'uuid': 'test-uuid-2'},
                {'name': 'TEST_GEMINI_AI', 'uuid': 'test-uuid-3'}
            ]
        }
        
        player.receive_game_start_message(game_start_info)
        
        # 模拟轮次开始消息
        print("\n🎲 测试轮次开始消息...")
        seats = [
            {'name': 'TEST_CLAUDE_AI', 'uuid': 'test-uuid-1', 'stack': 990},
            {'name': 'TEST_GPT_AI', 'uuid': 'test-uuid-2', 'stack': 980},
            {'name': 'TEST_GEMINI_AI', 'uuid': 'test-uuid-3', 'stack': 1030}
        ]
        player.receive_round_start_message(1, ['AS', 'KH'], seats)
        
        # 模拟街道开始消息
        print("\n🔄 测试街道开始消息...")
        round_state = {
            'community_card': ['JC', '9S', '2H'],
            'street': 'flop'
        }
        player.receive_street_start_message('flop', round_state)
        
        # 模拟对手行动消息
        print("\n👥 测试对手行动消息...")
        action = {
            'player_uuid': 'test-uuid-2',
            'action': 'raise',
            'amount': 50
        }
        player.receive_game_update_message(action, round_state)
        
        # 测试游戏状态分析
        print("\n📊 测试游戏状态分析...")
        test_round_state = {
            'street': 'flop',
            'community_card': ['JC', '9S', '2H'],
            'pot': {'main': {'amount': 120}},
            'seats': [
                {'uuid': 'test-uuid-1', 'name': 'TEST_CLAUDE_AI', 'stack': 940},
                {'uuid': 'test-uuid-2', 'name': 'TEST_GPT_AI', 'stack': 930},
                {'uuid': 'test-uuid-3', 'name': 'TEST_GEMINI_AI', 'stack': 1030}
            ],
            'action_histories': {
                'preflop': [
                    {'uuid': 'test-uuid-2', 'action': 'call', 'amount': 20},
                    {'uuid': 'test-uuid-3', 'action': 'raise', 'amount': 40}
                ],
                'flop': [
                    {'uuid': 'test-uuid-2', 'action': 'raise', 'amount': 50}
                ]
            }
        }
        
        valid_actions = [
            {'action': 'fold', 'amount': 0},
            {'action': 'call', 'amount': 50},
            {'action': 'raise', 'amount': {'min': 100, 'max': 940}}
        ]
        
        hole_cards = ['AS', 'KH']
        
        game_info = GameStateAnalyzer.extract_game_info(
            test_round_state, hole_cards, valid_actions, 'test-uuid-1'
        )
        
        # 显示游戏状态（这会触发增强的日志输出）
        player._print_game_state(game_info)
        
        # 测试AI客户端的调试输出（不实际调用API）
        print("\n🧠 测试AI决策调试输出...")
        if API_KEY:
            print("⚠️  注意: 以下测试将调用真实API，可能产生费用")
            user_input = input("是否继续API测试? (y/n): ").strip().lower()
            if user_input in ['y', 'yes']:
                try:
                    # 这会触发完整的AI决策流程和调试输出
                    decision = player.ai_client.get_poker_decision(game_info, debug=True)
                    if decision:
                        action, amount = player._process_ai_decision(decision, valid_actions)
                        player._print_final_decision(action, amount, decision)
                    else:
                        print("❌ AI决策失败")
                except Exception as e:
                    print(f"❌ API调用异常: {e}")
            else:
                print("⏭️  跳过API测试")
        else:
            print("⏭️  跳过API测试（未设置API密钥）")
        
        # 测试备用策略
        print("\n🛡️  测试备用策略...")
        action, amount = player._fallback_strategy(valid_actions, hole_cards, test_round_state)
        print(f"   🤖 备用策略决策: {action} {amount}")
        
        # 模拟轮次结束消息
        print("\n🏆 测试轮次结束消息...")
        winners = ['test-uuid-3']
        hand_info = [
            {
                'uuid': 'test-uuid-1',
                'hand': {'hand_type': '高牌'}
            }
        ]
        final_round_state = {
            'seats': [
                {'uuid': 'test-uuid-1', 'name': 'TEST_CLAUDE_AI', 'stack': 890},
                {'uuid': 'test-uuid-2', 'name': 'TEST_GPT_AI', 'stack': 930},
                {'uuid': 'test-uuid-3', 'name': 'TEST_GEMINI_AI', 'stack': 1180}
            ]
        }
        
        player.receive_round_result_message(winners, hand_info, final_round_state)
        
        print("\n✅ 增强日志功能测试完成!")
        print("=" * 60)
        
        print("\n📝 新增功能总结:")
        print("   🎯 详细的AI决策流程日志")
        print("   📊 丰富的游戏状态显示")
        print("   💬 模型原始响应输出")
        print("   🔧 模型配置信息显示")
        print("   📝 完整的prompt内容")
        print("   🎨 使用emoji和分割线美化输出")
        print("   ⚡ 增强的对手行动追踪")
        print("   💰 筹码变化和盈亏统计")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_enhanced_logging()
