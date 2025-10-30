"""
模型接入测试脚本
测试config.py中配置的所有AI模型是否能正常接入
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ai_client import AI302Client
from config import SUPPORTED_MODELS, API_KEY

def test_model(model_type: str) -> bool:
    """
    测试单个模型的接入情况
    
    Args:
        model_type: 模型类型
        
    Returns:
        bool: 测试是否成功
    """
    print(f"正在测试 {model_type} 模型...")
    
    try:
        # 创建客户端
        client = AI302Client(model_type)
        
        # 发送简单的测试消息
        test_messages = [
            {
                "role": "user", 
                "content": "这是一个测试，请回复'dd11'表示测试通过"
            }
        ]
        
        # 调用API
        response = client.chat_completion(test_messages)
        
        if response:
            print(f"✅ {model_type} 模型测试成功")
            print(f"   模型名称: {SUPPORTED_MODELS[model_type]['model_name']}")
            print(f"   响应内容: {response[:100]}...")  # 只显示前100个字符
            return True
        else:
            print(f"❌ {model_type} 模型测试失败 - 无响应")
            return False
            
    except Exception as e:
        print(f"❌ {model_type} 模型测试失败 - 异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("AI模型接入测试脚本")
    print("=" * 60)
    
    # 检查API密钥
    if not API_KEY:
        print("❌ 错误: 未找到API_302_KEY环境变量")
        print("请在.env文件中设置API_302_KEY")
        return
    
    print(f"API密钥: {API_KEY[:10]}...{API_KEY[-5:] if len(API_KEY) > 15 else API_KEY}")
    print(f"支持的模型数量: {len(SUPPORTED_MODELS)}")
    print()
    
    # 测试结果统计
    success_count = 0
    total_count = len(SUPPORTED_MODELS)
    failed_models = []
    
    # 逐个测试每个模型
    for model_type in SUPPORTED_MODELS.keys():
        if "gpt" not in model_type :
            continue
        try:
            if test_model(model_type):
                success_count += 1
                print("   状态: dd11 - 测试通过! ✅")
            else:
                failed_models.append(model_type)
                print("   状态: 测试失败 ❌")
        except KeyboardInterrupt:
            print("\n用户中断测试")
            break
        except Exception as e:
            print(f"   状态: 测试异常 - {str(e)} ❌")
            failed_models.append(model_type)
            
        print("-" * 40)
    
    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"总模型数: {total_count}")
    print(f"成功数量: {success_count}")
    print(f"失败数量: {len(failed_models)}")
    print(f"成功率: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("\n🎉 所有模型测试通过! dd11")
    else:
        print(f"\n⚠️  以下模型测试失败:")
        for model in failed_models:
            print(f"   - {model}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main()
