"""
AI扑克玩家 - 基于大模型的扑克AI玩家实现
"""
from pypokerengine.players import BasePokerPlayer
from typing import Dict, List, Any
import time
import random
import sys

from ai_client import AI302Client
from game_state_analyzer import GameStateAnalyzer
from logger_util import LoggerUtil


class AIPokerPlayer(BasePokerPlayer):
    """基于大模型的AI扑克玩家"""
    
    def __init__(self, name: str, model_type: str = "claude", debug: bool = True):
        """
        初始化AI玩家
        
        Args:
            name: 玩家名称
            model_type: 使用的AI模型类型
            debug: 是否开启调试模式
        """
        self.name = name
        self.model_type = model_type
        self.debug = debug #false or debug
        
        # 初始化日志工具 - 将日志保存到 .\log\ 目录
        self.logger = LoggerUtil.get_logger(player_name=name, log_dir=".\\log")
        
        # 将 logger 传递给 ai_client，使其也能记录日志
        self.ai_client = AI302Client(model_type, logger=self.logger)
        self.game_history = []  # 存储游戏历史
        self.player_uuid = None
        self._is_all_in = False  # 标记是否all-in
        
        if self.debug:
            self._log(f"[{self.name}] 初始化完成，使用模型: {model_type}")
    
    def _log(self, message: str, end: str = '\n'):
        """
        记录日志（同时输出到控制台和文件）
        
        Args:
            message: 日志消息
            end: 结束字符（默认换行）
        """
        # 输出到控制台
        print(message, end=end, flush=True)
        
        # 写入日志文件
        if self.logger:
            if end == '\n' or end == '':
                self.logger.log_line(message, print_to_console=False)
            else:
                self.logger.log(message, print_to_console=False)
    
    def declare_action(self, valid_actions: List[Dict], hole_card: List, 
                      round_state: Dict) -> tuple:
        """
        声明行动 - 核心决策方法
        
        Args:
            valid_actions: 可选行动列表
            hole_card: 手牌
            round_state: 轮次状态
            
        Returns:
            (action, amount) 元组
        """
        try:
            # 分析游戏状态
            game_info = GameStateAnalyzer.extract_game_info(
                round_state, hole_card, valid_actions, self.player_uuid
            )
            
            if self.debug:
                self._print_game_state(game_info)
            
            # 获取AI决策
            decision = self.ai_client.get_poker_decision(game_info, debug=self.debug)
            
            if decision:
                action, amount = self._process_ai_decision(decision, valid_actions, round_state)
                
                if self.debug:
                    # 获取当前筹码以便判断all-in
                    my_stack = game_info.get('my_stack', 0)
                    self._print_final_decision(action, amount, decision, my_stack)
                
                # 记录决策历史
                self._record_decision(game_info, decision, action, amount)
                
                return action, amount
            else:
                # AI决策失败，使用备用策略
                if self.debug:
                    self._log(f"\n⚠️  [{self.name}] AI决策失败，启用备用策略")
                    self._log(f"{'─'*50}")
                
                action, amount = self._fallback_strategy(valid_actions, hole_card, round_state)
                
                if self.debug:
                    self._log(f"   🤖 备用策略决策: {action} {amount}")
                    self._log(f"{'─'*50}")
                
                return action, amount
                
        except Exception as e:
            if self.debug:
                self._log(f"[{self.name}] 决策异常: {str(e)}")
            
            # 异常情况下使用备用策略
            return self._fallback_strategy(valid_actions, hole_card, round_state)
    
    def _process_ai_decision(self, decision: Dict, valid_actions: List[Dict], 
                           round_state: Dict = None) -> tuple:
        """
        处理AI决策，确保决策有效
        
        Args:
            decision: AI决策
            valid_actions: 可选行动
            round_state: 轮次状态（用于检测all-in）
            
        Returns:
            (action, amount) 元组
        """
        action = decision.get('action', 'call').lower()
        amount = decision.get('amount', 0)
        
        # 验证决策是否有效
        valid_action_types = [va['action'] for va in valid_actions]
        
        if action not in valid_action_types:
            # 如果AI选择的行动无效，默认选择call或fold
            if 'call' in valid_action_types:
                action = 'call'
            elif 'fold' in valid_action_types:
                action = 'fold'
            else:
                action = valid_action_types[0]
        
        # 根据行动类型调整金额
        my_stack = 0
        if round_state:
            for seat in round_state.get('seats', []):
                if seat['uuid'] == self.player_uuid:
                    my_stack = seat['stack']
                    break
        
        for va in valid_actions:
            if va['action'] == action:
                if action in ['call', 'fold']:
                    amount = va['amount']
                elif action == 'raise':
                    # 确保加注金额在有效范围内
                    min_amount = va.get('amount', {}).get('min', 0)
                    max_amount = va.get('amount', {}).get('max', float('inf'))
                    
                    if isinstance(amount, (int, float)):
                        amount = max(min_amount, min(amount, max_amount))
                        
                        # 检测all-in：在PyPokerEngine中，raise的amount是总投入金额（不是增量）
                        # 当raise amount达到或接近max_amount（通常是stack+已投入金额）时，就是all-in
                        # 如果max_amount有限且amount >= max_amount * 0.95（允许一点误差），认为是all-in
                        if max_amount != float('inf'):
                            # 如果加注到最大可加注金额，就是all-in
                            if amount >= max_amount or (my_stack > 0 and amount >= my_stack + min_amount):
                                self._is_all_in = True
                                # 如果AI想全下，设置为最大可加注金额
                                if amount >= max_amount * 0.9:  # 如果接近全下
                                    amount = max_amount
                            else:
                                self._is_all_in = False
                        elif my_stack > 0:
                            # 如果没有max限制但有stack信息，检查是否投入所有筹码
                            # 注意：需要知道已投入的金额，这里简化处理
                            # 如果amount很大（比如超过stack的80%），可能是all-in意图
                            if amount >= my_stack:
                                self._is_all_in = True
                            else:
                                self._is_all_in = False
                        else:
                            self._is_all_in = False
                    else:
                        amount = min_amount
                        self._is_all_in = False
                break
        
        return action, amount
    
    def _fallback_strategy(self, valid_actions: List[Dict], hole_card: List, 
                          round_state: Dict) -> tuple:
        """
        备用策略 - 当AI决策失败时使用的简单策略
        
        Args:
            valid_actions: 可选行动
            hole_card: 手牌
            round_state: 轮次状态
            
        Returns:
            (action, amount) 元组
        """
        # 简单的备用策略：根据手牌强度决定
        hand_strength = GameStateAnalyzer.get_hand_strength_description(
            hole_card, round_state.get('community_card', [])
        )
        
        # 获取我的筹码信息
        my_stack = 0
        for seat in round_state.get('seats', []):
            if seat['uuid'] == self.player_uuid:
                my_stack = seat['stack']
                break
        
        # 获取call行动信息
        call_action = None
        for action in valid_actions:
            if action['action'] == 'call':
                call_action = action
                break
        
        # 根据手牌强度决策
        if hand_strength in ['强对子', '同花连牌']:
            # 强牌：尝试加注
            for action in valid_actions:
                if action['action'] == 'raise':
                    min_raise = action.get('amount', {}).get('min', 50)
                    return 'raise', min_raise
            # 如果不能加注，则跟注
            if call_action:
                return 'call', call_action['amount']
        
        elif hand_strength in ['中等对子', '同花牌', '连牌', '高牌']:
            # 中等牌：跟注
            if call_action:
                call_amount = call_action['amount']
                # 如果跟注金额过高，考虑弃牌
                my_stack = 0
                for seat in round_state.get('seats', []):
                    if seat['uuid'] == self.player_uuid:
                        my_stack = seat['stack']
                        break
                
                if call_amount > my_stack * 0.2:  # 如果跟注超过筹码的20%
                    return 'fold', 0
                else:
                    return 'call', call_amount
        
        # 弱牌或其他情况：弃牌
        return 'fold', 0
    
    def _print_game_state(self, game_info: Dict):
        """打印游戏状态信息（调试用）"""
        self._log(f"\n{'🎲'*20} [{self.name}] 游戏状态分析 {'🎲'*20}")
        self._log(f"📋 基本信息:")
        self._log(f"   🃏 手牌: {game_info['hole_cards']}")
        self._log(f"   🃏 公共牌: {game_info['community_cards']}")
        self._log(f"   🔄 轮次: {game_info['street']}")
        self._log(f"   💰 我的筹码: {game_info['my_stack']}")
        self._log(f"   🏆 底池大小: {game_info['pot_size']}")
        self._log(f"   💸 需跟注: {game_info['call_amount']}")
        
        # 计算底池赔率
        if game_info['call_amount'] > 0 and game_info['pot_size'] > 0:
            pot_odds = game_info['pot_size'] / game_info['call_amount']
            self._log(f"   📊 底池赔率: {pot_odds:.2f}:1")
        
        # 显示可选行动
        self._log(f"\n⚡ 可选行动:")
        for action in game_info.get('valid_actions', []):
            action_name = action.get('action', '未知')
            if action_name == 'fold':
                self._log(f"   ❌ 弃牌")
            elif action_name == 'call':
                self._log(f"   ✅ 跟注 {action.get('amount', 0)}")
            elif action_name == 'raise':
                amount_info = action.get('amount', {})
                if isinstance(amount_info, dict):
                    min_raise = amount_info.get('min', 0)
                    max_raise = amount_info.get('max', 0)
                    # 检查是否可以达到all-in
                    if game_info['my_stack'] <= max_raise:
                        self._log(f"   💥 全下 (ALL-IN) {game_info['my_stack']}")
                    else:
                        self._log(f"   🚀 加注 {min_raise}-{max_raise}")
                else:
                    self._log(f"   🚀 加注 {amount_info}")
        
        # 显示对手信息
        if game_info['opponents']:
            self._log(f"\n👥 对手信息:")
            for i, opp in enumerate(game_info['opponents']):
                self._log(f"   🎭 {opp['name']}: 💰{opp['stack']} | 📝{opp['last_action']}")
                
                # 显示对手行动模式（如果有）
                if 'action_pattern' in opp:
                    pattern = opp['action_pattern']
                    if pattern['total_actions'] > 0:
                        aggr_rate = pattern['aggression_rate'] * 100
                        self._log(f"      📈 激进度: {aggr_rate:.1f}% | 总行动: {pattern['total_actions']}")
        
        self._log(f"{'─'*80}")
    
    def _record_decision(self, game_info: Dict, ai_decision: Dict, 
                        final_action: str, final_amount: int):
        """记录决策历史"""
        record = {
            'timestamp': time.time(),
            'street': game_info['street'],
            'hole_cards': game_info['hole_cards'],
            'community_cards': game_info['community_cards'],
            'my_stack': game_info['my_stack'],
            'pot_size': game_info['pot_size'],
            'ai_decision': ai_decision,
            'final_action': final_action,
            'final_amount': final_amount
        }
        
        self.game_history.append(record)
    
    def _print_final_decision(self, action: str, amount: int, original_decision: Dict, my_stack: int = 0):
        """打印最终决策信息"""
        self._log(f"\n🎯 [{self.name}] 最终决策:")
        self._log(f"{'─'*50}")
        
        # 显示决策结果
        if action == 'fold':
            self._log(f"   ❌ 决策: 弃牌")
        elif action == 'call':
            self._log(f"   ✅ 决策: 跟注 {amount}")
        elif action == 'raise':
            # 检查是否是all-in：如果加注金额等于或超过全部筹码，就是all-in
            if self._is_all_in or (my_stack > 0 and amount >= my_stack):
                self._log(f"   💥💥💥 决策: 全下 (ALL-IN) {amount} 💥💥💥")
                self._log(f"   {'🔥' * 30}")
                self._log(f"   ⚡ {self.name} 全下所有筹码！")
                self._log(f"   {'🔥' * 30}")
            else:
                self._log(f"   🚀 决策: 加注至 {amount}")
        else:
            self._log(f"   ❓ 决策: {action} {amount}")
        
        # 显示原始AI决策（如果与最终决策不同）
        original_action = original_decision.get('action', '')
        original_amount = original_decision.get('amount', 0)
        
        if original_action != action or original_amount != amount:
            self._log(f"   🔄 原始AI决策: {original_action} {original_amount}")
            self._log(f"   ⚙️  已调整为有效决策")
        
        self._log(f"{'─'*50}")
        self._log(f"✨ [{self.name}] 决策完成\n")
    
    # PyPokerEngine回调方法
    def receive_game_start_message(self, game_info: Dict):
        """接收游戏开始消息"""
        if self.debug:
            self._log(f"\n🎮 [{self.name}] 游戏开始")
            self._log(f"{'─'*40}")
            self._log(f"   👥 玩家数量: {game_info['player_num']}")
            self._log(f"   🔄 最大轮数: {game_info['rule']['max_round']}")
            self._log(f"   💰 小盲注: {game_info['rule']['small_blind_amount']}")
            self._log(f"   💰 初始筹码: {game_info['rule']['initial_stack']}")
            self._log(f"   🤖 使用模型: {self.model_type}")
            self._log(f"{'─'*40}")
        
        # 找到自己的UUID
        for seat in game_info['seats']:
            if seat['name'] == self.name:
                self.player_uuid = seat['uuid']
                if self.debug:
                    self._log(f"   🆔 玩家UUID: {self.player_uuid}")
                break
    
    def receive_round_start_message(self, round_count: int, hole_card: List, seats: List):
        """接收轮次开始消息"""
        if self.debug:
            self._log(f"\n🎲 [{self.name}] 第{round_count}轮开始")
            self._log(f"   🃏 手牌: {GameStateAnalyzer._format_cards(hole_card)}")
            
            # 显示所有玩家的筹码状态
            self._log(f"   💰 筹码状态:")
            for seat in seats:
                if seat['uuid'] == self.player_uuid:
                    self._log(f"      🤖 {seat['name']}: {seat['stack']} (我)")
                else:
                    self._log(f"      👤 {seat['name']}: {seat['stack']}")
    
    def receive_street_start_message(self, street: str, round_state: Dict):
        """接收街道开始消息"""
        if self.debug:
            community_cards = GameStateAnalyzer._format_cards(
                round_state.get('community_card', [])
            )
            street_names = {
                'preflop': '翻牌前',
                'flop': '翻牌',
                'turn': '转牌', 
                'river': '河牌'
            }
            street_cn = street_names.get(street, street)
            self._log(f"\n🔄 [{self.name}] {street_cn}阶段开始")
            self._log(f"   🃏 公共牌: {community_cards}")
    
    def receive_game_update_message(self, action: Dict, round_state: Dict):
        """接收游戏更新消息"""
        if self.debug and action['player_uuid'] != self.player_uuid:
            player_name = "未知玩家"
            for seat in round_state.get('seats', []):
                if seat['uuid'] == action['player_uuid']:
                    player_name = seat['name']
                    break
            
            action_type = action['action']
            action_amount = action.get('amount', 0)
            
            # 检测all-in：检查该玩家的筹码是否已全部投入
            player_stack = 0
            for seat in round_state.get('seats', []):
                if seat['uuid'] == action['player_uuid']:
                    player_stack = seat['stack']
                    break
            
            is_all_in = False
            if action_type in ['raise', 'call'] and action_amount > 0:
                # 检测all-in：如果玩家剩余筹码为0，说明已经all-in
                # 或者如果raise/call的金额很大，可能是all-in
                # 注意：PyPokerEngine中，如果玩家all-in，amount会是总投入金额
                # 最可靠的判断是检查玩家剩余stack是否为0
                if player_stack == 0:
                    is_all_in = True
                # 另外，如果raise金额非常大（可能接近或等于全部筹码），也可能是all-in
                # 但这个判断不够准确，因为需要知道已投入金额
            
            if is_all_in:
                action_emoji = '💥'
                action_desc = f"全下 (ALL-IN) {action_amount}"
                self._log(f"   {action_emoji}{action_emoji}{action_emoji} {player_name}: {action_desc} {action_emoji}{action_emoji}{action_emoji}")
            else:
                action_emoji = {
                    'fold': '❌',
                    'call': '✅', 
                    'raise': '🚀',
                    'bet': '💰',
                    'check': '⏸️'
                }.get(action_type, '❓')
                
                action_desc = f"{action_type}"
                if action_amount > 0:
                    action_desc += f" {action_amount}"
                self._log(f"   {action_emoji} {player_name}: {action_desc}")
    
    def receive_round_result_message(self, winners: List, hand_info: List, round_state: Dict):
        """接收轮次结果消息"""
        if self.debug:
            self._log(f"\n🏆 [{self.name}] 轮次结束")
            self._log(f"{'─'*40}")
            
            # 显示获胜者
            winner_names = []
            for winner in winners:
                for seat in round_state.get('seats', []):
                    if seat['uuid'] == winner:
                        winner_names.append(seat['name'])
                        break
            
            self._log(f"   🥇 获胜者: {', '.join(winner_names)}")
            
            # 显示手牌信息（如果有）
            if hand_info:
                for info in hand_info:
                    if info['uuid'] == self.player_uuid:
                        hand_strength = info.get('hand', {}).get('hand_type', '未知')
                        self._log(f"   🃏 我的牌型: {hand_strength}")
                        break
            
            # 显示筹码变化
            for seat in round_state.get('seats', []):
                if seat['uuid'] == self.player_uuid:
                    current_stack = seat['stack']
                    self._log(f"   💰 当前筹码: {current_stack}")
                    
                    # 计算盈亏（如果有历史记录）
                    if hasattr(self, '_last_stack'):
                        profit = current_stack - self._last_stack
                        if profit > 0:
                            self._log(f"   📈 本轮盈利: +{profit}")
                        elif profit < 0:
                            self._log(f"   📉 本轮亏损: {profit}")
                        else:
                            self._log(f"   ➡️  本轮持平: 0")
                    
                    self._last_stack = current_stack
                    break
            
            self._log(f"{'─'*40}")
