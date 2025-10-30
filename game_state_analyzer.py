"""
游戏状态分析器 - 解析PyPokerEngine的游戏状态
"""
from typing import Dict, List, Any, Optional


class GameStateAnalyzer:
    """游戏状态分析器"""
    
    @staticmethod
    def extract_game_info(round_state: Dict, hole_card: List, valid_actions: List, 
                         player_uuid: str) -> Dict[str, Any]:
        """
        从PyPokerEngine的状态中提取游戏信息
        
        Args:
            round_state: 轮次状态
            hole_card: 手牌
            valid_actions: 可选行动
            player_uuid: 当前玩家UUID
            
        Returns:
            格式化的游戏状态信息
        """
        # 提取基本信息
        street = round_state.get('street', 'preflop')
        community_card = round_state.get('community_card', [])
        pot = round_state.get('pot', {})
        seats = round_state.get('seats', [])
        
        # 找到当前玩家
        current_player = None
        opponents = []
        
        for seat in seats:
            if seat['uuid'] == player_uuid:
                current_player = seat
            else:
                opponents.append(seat)
        
        # 计算底池大小
        pot_size = pot.get('main', {}).get('amount', 0)
        for side_pot in pot.get('side', []):
            pot_size += side_pot.get('amount', 0)
        
        # 计算需要跟注的金额
        call_amount = 0
        for action in valid_actions:
            if action['action'] == 'call':
                call_amount = action['amount']
                break
        
        # 分析对手行动历史
        action_histories = round_state.get('action_histories', {})
        opponents_with_actions = GameStateAnalyzer._analyze_opponents_actions(
            opponents, action_histories, street
        )
        
        return {
            'hole_cards': GameStateAnalyzer._format_cards(hole_card),
            'community_cards': GameStateAnalyzer._format_cards(community_card),
            'street': street,
            'my_stack': current_player['stack'] if current_player else 0,
            'pot_size': pot_size,
            'call_amount': call_amount,
            'opponents': opponents_with_actions,
            'valid_actions': valid_actions,
            'round_state': round_state  # 保留原始状态用于调试
        }
    
    @staticmethod
    def _format_cards(cards: List) -> str:
        """格式化卡牌显示"""
        if not cards:
            return "无"
        
        card_symbols = {
            'C': '♣', 'D': '♦', 'H': '♥', 'S': '♠'
        }
        
        formatted_cards = []
        for card in cards:
            if len(card) >= 2:
                rank = card[:-1]
                suit = card[-1].upper()
                symbol = card_symbols.get(suit, suit)
                formatted_cards.append(f"{rank}{symbol}")
            else:
                formatted_cards.append(card)
        
        return " ".join(formatted_cards)
    
    @staticmethod
    def _analyze_opponents_actions(opponents: List, action_histories: Dict, 
                                 current_street: str) -> List[Dict]:
        """分析对手的行动历史"""
        opponents_info = []
        
        for opponent in opponents:
            opponent_uuid = opponent['uuid']
            opponent_name = opponent['name']
            opponent_stack = opponent['stack']
            
            # 获取该对手在当前轮次的最后行动
            last_action = GameStateAnalyzer._get_last_action(
                action_histories, opponent_uuid, current_street
            )
            
            # 计算该对手的行动模式
            action_pattern = GameStateAnalyzer._calculate_action_pattern(
                action_histories, opponent_uuid
            )
            
            opponents_info.append({
                'name': opponent_name,
                'uuid': opponent_uuid,
                'stack': opponent_stack,
                'last_action': last_action,
                'action_pattern': action_pattern
            })
        
        return opponents_info
    
    @staticmethod
    def _get_last_action(action_histories: Dict, player_uuid: str, 
                        current_street: str) -> str:
        """获取玩家在当前轮次的最后行动"""
        street_actions = action_histories.get(current_street, [])
        
        # 从后往前查找该玩家的最后行动
        for action in reversed(street_actions):
            if action['uuid'] == player_uuid:
                action_type = action['action']
                amount = action.get('amount', 0)
                
                if action_type == 'fold':
                    return "弃牌"
                elif action_type == 'call':
                    return f"跟注 {amount}"
                elif action_type == 'raise':
                    return f"加注至 {amount}"
                elif action_type == 'bet':
                    return f"下注 {amount}"
                else:
                    return action_type
        
        return "未行动"
    
    @staticmethod
    def _calculate_action_pattern(action_histories: Dict, player_uuid: str) -> Dict:
        """计算玩家的行动模式统计"""
        pattern = {
            'total_actions': 0,
            'folds': 0,
            'calls': 0,
            'raises': 0,
            'aggression_rate': 0.0
        }
        
        for street, actions in action_histories.items():
            for action in actions:
                if action['uuid'] == player_uuid:
                    pattern['total_actions'] += 1
                    
                    action_type = action['action']
                    if action_type == 'fold':
                        pattern['folds'] += 1
                    elif action_type == 'call':
                        pattern['calls'] += 1
                    elif action_type in ['raise', 'bet']:
                        pattern['raises'] += 1
        
        # 计算激进度（加注率）
        if pattern['total_actions'] > 0:
            pattern['aggression_rate'] = pattern['raises'] / pattern['total_actions']
        
        return pattern
    
    @staticmethod
    def get_hand_strength_description(hole_cards: List, community_cards: List) -> str:
        """获取手牌强度描述（简化版本）"""
        if not hole_cards or len(hole_cards) < 2:
            return "无效手牌"
        
        # 简化的手牌强度评估
        card1, card2 = hole_cards[0], hole_cards[1]
        
        # 提取牌面值和花色
        rank1, suit1 = card1[:-1], card1[-1]
        rank2, suit2 = card2[:-1], card2[-1]
        
        # 牌面值映射
        rank_values = {
            'A': 14, 'K': 13, 'Q': 12, 'J': 11, 'T': 10,
            '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
        }
        
        val1 = rank_values.get(rank1, 0)
        val2 = rank_values.get(rank2, 0)
        
        # 判断手牌类型
        if val1 == val2:
            if val1 >= 10:
                return "强对子"
            elif val1 >= 7:
                return "中等对子"
            else:
                return "小对子"
        
        elif suit1 == suit2:
            if abs(val1 - val2) <= 4:
                return "同花连牌"
            else:
                return "同花牌"
        
        elif abs(val1 - val2) <= 4 and min(val1, val2) >= 7:
            return "连牌"
        
        elif max(val1, val2) >= 12:
            return "高牌"
        
        else:
            return "弱牌"

