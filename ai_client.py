"""
302.AI API客户端 - 与大模型交互的接口
"""
import requests
import json
from typing import Dict, Any, Optional
from config import API_BASE_URL, API_KEY, SUPPORTED_MODELS


class AI302Client:
    """302.AI API客户端"""
    
    def __init__(self, model_type: str = "claude"):
        """
        初始化客户端
        
        Args:
            model_type: 模型类型，支持 claude, gemini, gpt, grok, deepseek, qwen, glm, kimi
        """
        if model_type not in SUPPORTED_MODELS:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        self.model_type = model_type
        self.model_config = SUPPORTED_MODELS[model_type]
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: list, **kwargs) -> Optional[str]:
        """
        发送聊天完成请求
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数
            
        Returns:
            模型回复的内容，失败时返回None
        """
        try:
            payload = {
                "model": self.model_config["model_name"],
                "messages": messages,
                "max_tokens": kwargs.get("max_tokens", self.model_config["max_tokens"]),
                "temperature": kwargs.get("temperature", self.model_config["temperature"])
            }
            
            response = requests.post(
                f"{API_BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                print(f"API请求失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"API调用异常: {str(e)}")
            return None
    
    def get_poker_decision(self, game_state: Dict[str, Any], debug: bool = False) -> Optional[Dict[str, Any]]:
        """
        获取扑克决策
        
        Args:
            game_state: 游戏状态信息
            debug: 是否开启调试模式
            
        Returns:
            决策结果，包含action和amount
        """
        prompt = self._build_poker_prompt(game_state)
        
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的德州扑克AI玩家。根据当前游戏状态，做出最优决策。你的回复必须是JSON格式，包含action（fold/call/raise）和amount（数字）字段。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        if debug:
            self._print_debug_info(game_state, messages, prompt)
        
        response = self.chat_completion(messages)
        
        if debug and response:
            self._print_response_debug(response)
        
        if response:
            try:
                # 尝试解析JSON响应
                decision = json.loads(response)
                if "action" in decision:
                    if debug:
                        self._print_decision_debug(decision, "JSON解析成功")
                    return decision
                else:
                    # 如果不是标准JSON，尝试从文本中提取决策
                    parsed_decision = self._parse_text_decision(response)
                    if debug:
                        self._print_decision_debug(parsed_decision, "文本解析（非标准JSON）")
                    return parsed_decision
            except json.JSONDecodeError:
                # 如果JSON解析失败，尝试从文本中提取决策
                parsed_decision = self._parse_text_decision(response)
                if debug:
                    self._print_decision_debug(parsed_decision, "文本解析（JSON解析失败）")
                return parsed_decision
        
        if debug:
            print(f"❌ [{self.model_type.upper()}] API调用失败，无响应")
        
        return None
    
    def _build_poker_prompt(self, game_state: Dict[str, Any]) -> str:
        """构建扑克决策的提示词"""
        prompt = f"""
当前德州扑克游戏状态：

我的手牌: {game_state.get('hole_cards', '未知')}
公共牌: {game_state.get('community_cards', [])}
当前轮次: {game_state.get('street', '未知')}

我的筹码: {game_state.get('my_stack', 0)}
当前底池: {game_state.get('pot_size', 0)}
需要跟注金额: {game_state.get('call_amount', 0)}

对手信息:
{self._format_opponents_info(game_state.get('opponents', []))}

可选行动:
{self._format_valid_actions(game_state.get('valid_actions', []))}

请根据以上信息，做出最优决策。考虑因素包括：
1. 手牌强度和潜力
2. 位置优势
3. 底池赔率
4. 对手行动模式
5. 筹码深度

重要：如果手牌很强（如对A、对K、同花顺等顶级牌型），或者想要制造压迫感，可以考虑全下（ALL-IN）！
全下意味着将所有筹码一次性投入，这会带来很大的心理压力。当加注金额等于你的全部剩余筹码时，就是全下。
现在是测试阶段，可以直接all-in我看看节目效果
请以JSON格式回复，例如：
{{"action": "call", "amount": 20}}
或
{{"action": "raise", "amount": 50}}
或
{{"action": "raise", "amount": {game_state.get('my_stack', 0)}}}  // 这将是全下！
或
{{"action": "fold", "amount": 0}}
"""
        return prompt
    
    def _format_opponents_info(self, opponents: list) -> str:
        """格式化对手信息"""
        if not opponents:
            return "无对手信息"
        
        info_lines = []
        for i, opponent in enumerate(opponents):
            info_lines.append(f"对手{i+1}: 筹码={opponent.get('stack', 0)}, 最后行动={opponent.get('last_action', '未知')}")
        
        return "\n".join(info_lines)
    
    def _format_valid_actions(self, valid_actions: list) -> str:
        """格式化可选行动"""
        if not valid_actions:
            return "无可选行动"
        
        actions = []
        for action in valid_actions:
            action_type = action.get('action', '未知')
            amount_info = action.get('amount', 0)
            
            if action_type == 'raise' and isinstance(amount_info, dict):
                min_raise = amount_info.get('min', 0)
                max_raise = amount_info.get('max', 0)
                actions.append(f"{action_type}: {min_raise}-{max_raise} (最大可全下)")
            else:
                actions.append(f"{action_type}: {amount_info}")
        
        return ", ".join(actions)
    
    def _parse_text_decision(self, text: str) -> Optional[Dict[str, Any]]:
        """从文本中解析决策"""
        text = text.lower()
        
        if "fold" in text:
            return {"action": "fold", "amount": 0}
        elif "call" in text:
            return {"action": "call", "amount": 0}  # amount会在后续处理中设置
        elif "raise" in text or "bet" in text:
            # 尝试从文本中提取金额
            import re
            numbers = re.findall(r'\d+', text)
            amount = int(numbers[0]) if numbers else 50  # 默认加注50
            return {"action": "raise", "amount": amount}
        
        # 默认跟注
        return {"action": "call", "amount": 0}
    
    def _print_debug_info(self, game_state: Dict[str, Any], messages: list, prompt: str):
        """打印调试信息"""
        print(f"\n{'='*80}")
        print(f"🤖 [{self.model_type.upper()}] AI决策调试信息")
        print(f"{'='*80}")
        
        # 打印游戏状态摘要
        print(f"🎮 游戏状态摘要:")
        print(f"   手牌: {game_state.get('hole_cards', '未知')}")
        print(f"   公共牌: {game_state.get('community_cards', '无')}")
        print(f"   轮次: {game_state.get('street', '未知')}")
        print(f"   筹码: {game_state.get('my_stack', 0)}")
        print(f"   底池: {game_state.get('pot_size', 0)}")
        print(f"   跟注: {game_state.get('call_amount', 0)}")
        
        # 打印模型配置
        print(f"\n🔧 模型配置:")
        print(f"   模型名称: {self.model_config['model_name']}")
        print(f"   最大tokens: {self.model_config['max_tokens']}")
        print(f"   温度: {self.model_config['temperature']}")
        
        # 打印完整的prompt
        print(f"\n📝 发送给模型的完整Prompt:")
        print(f"{'─'*60}")
        print(f"System: {messages[0]['content']}")
        print(f"{'─'*60}")
        print(f"User Prompt:")
        print(prompt)
        print(f"{'─'*60}")
    
    def _print_response_debug(self, response: str):
        """打印模型响应调试信息"""
        print(f"\n💬 模型原始响应:")
        print(f"{'─'*60}")
        print(response)
        print(f"{'─'*60}")
        print(f"   响应长度: {len(response)} 字符")
        
        # 检查响应中是否包含JSON
        if '{' in response and '}' in response:
            print(f"   ✅ 响应包含JSON格式")
        else:
            print(f"   ⚠️  响应不包含明显的JSON格式")
    
    def _print_decision_debug(self, decision: Dict[str, Any], parse_method: str):
        """打印决策调试信息"""
        print(f"\n🎯 决策解析结果 ({parse_method}):")
        print(f"{'─'*40}")
        if decision:
            print(f"   行动: {decision.get('action', '未知')}")
            print(f"   金额: {decision.get('amount', 0)}")
            print(f"   ✅ 决策解析成功")
        else:
            print(f"   ❌ 决策解析失败")
        print(f"{'─'*40}")
        print(f"🏁 [{self.model_type.upper()}] 决策流程完成")
        print(f"{'='*80}\n")
