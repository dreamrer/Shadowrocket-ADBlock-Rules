import json
import requests
import time
import hashlib
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from decimal import Decimal

# 尝试导入所有必要的模块
try:
    import pika
    from pika.exceptions import AMQPError, ChannelClosedByBroker
    from pika import exceptions
    PIKA_AVAILABLE = True
except ImportError:
    print("⚠️ pika 模块未安装，RabbitMQ功能将不可用")
    PIKA_AVAILABLE = False

try:
    import tronpy.exceptions
    from tronpy.providers import HTTPProvider
    from tronpy import Tron
    TRONPY_AVAILABLE = True
except ImportError:
    print("⚠️ tronpy 模块未安装，区块链监控功能将不可用")
    TRONPY_AVAILABLE = False

from mongo import qukuai, shangtext, topup, user, notifications, user_log

# 易支付配置 - 请修改为你的实际配置
EPAY_CONFIG = {
    'api_url': 'http://ruixing.wwspay.com/submit.php',
    'pid': '240983942',
    'key': 'rhgc7xkp0e0jaxose6ycmx0llihs6p04',
    'notify_url': 'http://8.209.218.35:8888/notify',  # 替换为你的真实IP
    'return_url': 'http://8.209.218.35:8888/return'   # 替换为你的真实IP
}

print("🔧 易支付配置已加载:")
print(f"   商户号: {EPAY_CONFIG['pid']}")
print(f"   回调地址: {EPAY_CONFIG['notify_url']}")

# 全局变量
client = None
connection = None
channel = None

def initialize_tron_client():
    """初始化Tron客户端，带重试机制"""
    if not TRONPY_AVAILABLE:
        print("⚠️ tronpy不可用，无法初始化Tron客户端")
        return None
        
    apikey_list = [
        "18b81073-47af-4120-b6c5-50f4cd27b882",
        "6c961f7c-29b8-4c19-bf88-fa8f4e0affed"
    ]
    
    for api_key in apikey_list:
        try:
            print(f"🔗 尝试使用API Key: {api_key[:20]}...")
            client = Tron(HTTPProvider(api_key=[api_key]))
            # 测试连接
            latest_block = client.get_latest_block()
            print(f"✅ Tron 网络连接成功，最新区块: {latest_block['block_header']['raw_data']['number']}")
            return client
        except Exception as e:
            print(f"❌ API Key {api_key[:20]} 连接失败: {e}")
            continue
    
    print("❌ 所有API Key都连接失败，尝试无 API Key连接...")
    try:
        client = Tron(HTTPProvider())
        latest_block = client.get_latest_block()
        print(f"✅ 无API Key连接成功，最新区块: {latest_block['block_header']['raw_data']['number']}")
        return client
    except Exception as e:
        print(f"❌ 无API Key连接也失败: {e}")
        return None

def create_rabbitmq_connection():
    """创建 RabbitMQ 连接，带重试机制"""
    if not PIKA_AVAILABLE:
        return None
        
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            credentials = pika.PlainCredentials('faka', 'wDaefbJe')
            connection = pika.BlockingConnection(pika.ConnectionParameters(
                host='127.0.0.1',
                port=5672,
                virtual_host='/',
                credentials=credentials,
                heartbeat=600,  # 增加心跳时间
                blocked_connection_timeout=300,  # 增加阻塞超时时间
            ))
            print("✅ RabbitMQ 连接成功")
            return connection
        except Exception as e:
            print(f"❌ RabbitMQ 连接失败 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"⏳ {retry_delay} 秒后重试...")
                time.sleep(retry_delay)
            else:
                print("❌ RabbitMQ 连接彻底失败，程序将以本地模式运行")
                return None

def search_address():
    """获取充值地址列表"""
    try:
        print("🔍 正在查询充值地址配置...")
        dz_config = shangtext.find_one({'projectname': '充值地址'})
        
        if dz_config is None:
            print("❌ 充值地址配置不存在")
            return []
        
        if 'text' not in dz_config:
            print("❌ 充值地址配置中没有text字段")
            return []
            
        dz1 = dz_config['text']
        print(f"✅ 充值地址: {dz1}")
        
        if not dz1 or dz1.strip() == "":
            print("❌ 充值地址为空")
            return []
            
        return [dz1]
    except Exception as e:
        print(f"❌ search_address函数错误: {e}")
        return []

def verify_epay_notify(params, key):
    """验证易支付回调签名 - 完全修复版"""
    try:
        if 'sign' not in params:
            print("❌ 缺少签名参数")
            return False
            
        received_sign = params.get('sign', '')
        print(f"🔍 接收到的签名: {received_sign}")
        
        # 创建参数副本，排除sign和sign_type
        params_copy = params.copy()
        if 'sign' in params_copy:
            del params_copy['sign']
        if 'sign_type' in params_copy:
            del params_copy['sign_type']
        
        # 排序并生成签名字符串
        sorted_params = sorted(params_copy.items())
        param_str = '&'.join([f'{k}={v}' for k, v in sorted_params if v != '' and v is not None])
        sign_str = param_str + key
        calculated_sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        print(f"🔍 签名字符串: {sign_str}")
        print(f"🔍 计算的签名: {calculated_sign}")
        
        is_valid = received_sign.lower() == calculated_sign.lower()
        print(f"🔍 签名验证结果: {is_valid}")
        return is_valid
        
    except Exception as e:
        print(f"❌ 验证签名失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def process_usdt_transaction_immediately(transaction_data):
    """立即处理USDT交易，确保及时回调"""
    try:
        print(f"⚡ 立即处理USDT交易: {transaction_data['usdt_amount']} USDT")
        
        # 创建机器人通知
        create_instant_notification(transaction_data)
        
        # 发送到处理队列（如果有的话）
        if channel and PIKA_AVAILABLE:
            try:
                notification_data = {
                    "type": "usdt_received",
                    "txid": transaction_data["txid"],
                    "amount": transaction_data["usdt_amount"],
                    "from_address": transaction_data["from_address"],
                    "to_address": transaction_data["to_address"],
                    "timestamp": transaction_data["time"]
                }
                
                channel.basic_publish(
                    exchange='',
                    routing_key='usdt_notifications',
                    body=json.dumps(notification_data).encode(),
                    properties=pika.BasicProperties(delivery_mode=2)  # 持久化
                )
                print("📨 通知已发送到队列")
            except Exception as queue_error:
                print(f"⚠️ 队列发送失败: {queue_error}")
        
    except Exception as e:
        print(f"❌ 立即处理失败: {e}")

def create_instant_notification(transaction_data):
    """创建即时通知记录"""
    try:
        usdt_amount = transaction_data["usdt_amount"]
        txid = transaction_data["txid"]
        from_address = transaction_data["from_address"]
        to_address = transaction_data["to_address"]
        
        # 🔥 修复：查找匹配订单的逻辑优化
        current_time = time.time()
        time_24h_ago = current_time - (24 * 3600)
        
        # 查找24小时内的匹配订单，允许一定的金额误差
        tolerance = 0.02  # 允许2分钱的误差
        potential_orders = list(topup.find({
            "money": {
                "$gte": usdt_amount - tolerance,
                "$lte": usdt_amount + tolerance
            },
            "created_timestamp": {"$gte": time_24h_ago},
            "processed": {"$ne": True}
        }).sort("created_timestamp", 1))
        
        matched_order = None
        for order in potential_orders:
            # 原子性标记订单为已处理
            result = topup.update_one(
                {
                    '_id': order['_id'],
                    'processed': {'$ne': True}
                },
                {'$set': {
                    'processed': True,
                    'txid': txid,
                    'processing_time': current_time
                }}
            )
            
            if result.modified_count > 0:
                matched_order = order
                break
        
        if not matched_order:
            print(f"⚠️ 未找到匹配的订单: {usdt_amount} USDT")
            return
        
        user_id = matched_order['user_id']
        payment_type = matched_order.get('payment_type', 'usdt')
        
        # 🔥 修复：正确计算充值金额
        if payment_type == 'usdt_cny':
            # 基于人民币的USDT充值
            credit_amount = matched_order.get('cny_amount', usdt_amount * 7.2)
            unit = 'CNY'
        else:
            # 传统USDT充值
            credit_amount = usdt_amount
            unit = 'USDT'
        
        print(f"💰 为用户 {user_id} 充值 {credit_amount} {unit}")
        
        # 🔥 修复：安全更新用户余额
        user_info = user.find_one({'user_id': user_id})
        if not user_info:
            print(f"❌ 用户不存在: {user_id}")
            return
        
        current_balance = user_info['USDT']
        new_balance = float(current_balance) + float(credit_amount)
        
        # 原子性更新余额
        update_result = user.update_one(
            {'user_id': user_id, 'USDT': current_balance},
            {'$set': {'USDT': new_balance}}
        )
        
        if update_result.modified_count == 0:
            print(f"❌ 余额更新失败，可能存在并发冲突")
            # 恢复订单状态
            topup.update_one(
                {'_id': matched_order['_id']},
                {'$set': {'processed': False}}
            )
            return
        
        # 🔥 修复：创建通知记录
        timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        notification_data = {
            'user_id': user_id,
            'type': 'payment_success',
            'amount': credit_amount,
            'new_balance': new_balance,
            'order_no': matched_order.get('bianhao', 'auto'),
            'payment_method': 'USDT-TRC20',
            'txid': txid,
            'from_address': from_address,
            'processed': False,
            'created_at': timer,
            'timestamp': time.time(),
            'priority': 'high'  # 高优先级处理
        }
        
        # 防重复通知
        existing_notification = notifications.find_one({
            'user_id': user_id,
            'txid': txid,
            'type': 'payment_success'
        })
        
        if not existing_notification:
            notifications.insert_one(notification_data)
            print(f"📩 已创建用户通知: {user_id}")
        
        # 删除已处理的订单
        topup.delete_one({'_id': matched_order['_id']})
        
        print(f"✅ USDT交易处理完成: {user_id} -> {credit_amount} {unit}")
        
    except Exception as e:
        print(f"❌ 创建通知失败: {e}")
        import traceback
        traceback.print_exc()

def enhanced_local_process_block(block_list, block):
    """增强版本地区块处理，确保USDT交易能被正确处理"""
    global client
    try:
        if client is None:
            print("❌ Tron客户端为空，无法处理区块")
            return
            
        transactions = block_list.get('transactions', [])
        number = block_list.get('block_header', {}).get('raw_data', {}).get('number', 0)
        
        # 获取充值地址
        address_list = search_address()
        if not address_list:
            print("⚠️ 警告：未配置充值地址，跳过处理")
            return
            
        print(f"📊 处理区块: {number}, 交易数: {len(transactions)}")
        
        usdt_transactions = 0
        
        for trx in transactions:
            try:
                # 检查交易状态
                if not trx.get("ret") or not trx["ret"][0].get("contractRet") == "SUCCESS":
                    continue
                    
                contract = trx["raw_data"]["contract"][0]
                contract_type = contract["type"]
                value = contract["parameter"]["value"]
                txid = trx['txID']
                
                if contract_type == "TriggerSmartContract":
                    contract_address = client.to_base58check_address(value["contract_address"])
                    data = value.get('data', '')
                    
                    # USDT合约地址验证
                    if contract_address == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t' and len(data) >= 72:
                        if data[:8] == "a9059cbb":  # transfer方法
                            from_address = client.to_base58check_address(value["owner_address"])
                            to_address = client.to_base58check_address('41' + data[8:72][-40:])
                            
                            try:
                                quant = int(data[-64:], 16)
                                if quant == 0:
                                    continue
                            except ValueError:
                                print(f"⚠️ 无法解析交易金额: {data[-64:]}")
                                continue
                            
                            # 只处理发送到我们充值地址的交易
                            if to_address not in address_list:
                                continue
                                
                            usdt_amount = quant / 1_000_000  # 转换为USDT
                            if usdt_amount < 1.0:  # 过滤小额交易
                                continue
                            
                            timestamp = trx["raw_data"].get("timestamp", int(time.time() * 1000))
                            
                            # 检查是否已存在
                            existing = qukuai.find_one({"txid": txid})
                            if existing:
                                print(f"📋 交易已存在: {txid}")
                                continue
                            
                            message_data = {
                                "txid": txid,
                                "type": "USDT",
                                "from_address": from_address,
                                "to_address": to_address,
                                "quant": quant,
                                "usdt_amount": usdt_amount,
                                "time": timestamp,
                                "number": number,
                                "state": 0,  # 未处理
                                "confirmations": 1,  # 至少1个确认
                                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                                "processed_at": None
                            }
                            
                            # 插入数据库
                            result = qukuai.insert_one(message_data)
                            if result.inserted_id:
                                usdt_transactions += 1
                                print(f"✅ USDT交易已保存: {usdt_amount} USDT, txid: {txid[:20]}...")
                                
                                # 🔥 关键修复：立即触发处理
                                try:
                                    process_usdt_transaction_immediately(message_data)
                                except Exception as process_error:
                                    print(f"⚠️ 立即处理失败: {process_error}")
                            else:
                                print(f"❌ 保存USDT交易失败")
                        
            except Exception as tx_error:
                print(f"❌ 处理单个交易失败: {tx_error}")
                continue
                
        if usdt_transactions > 0:
            print(f"🎯 本次处理了 {usdt_transactions} 笔USDT交易")
            
    except Exception as e:
        print(f"❌ 处理区块失败: {e}")
        import traceback
        traceback.print_exc()

def get_data(block) -> None:
    """获取对应区块的交易信息，带错误处理和重试机制"""
    global client
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # 如果client为None，尝试重新初始化
            if client is None:
                print("🔄 Tron客户端为空，尝试重新初始化...")
                client = initialize_tron_client()
                if client is None:
                    print("❌ 重新初始化失败，跳过此区块")
                    return
            
            block_list = client.get_block(block)
            if 'transactions' in block_list.keys():
                break
            else:
                print(f"⚠️ 区块 {block} 没有交易数据")
                return
        except tronpy.exceptions.BlockNotFound:
            print(f"⚠️ 区块 {block} 未找到，等待1秒后重试...")
            time.sleep(1)
            continue
        except requests.exceptions.ReadTimeout as e:
            print(f"❌ 读取超时 (尝试 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                print(f"❌ 区块 {block} 读取失败，跳过")
                return
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"⚠️ API 请求频率限制，等待 {retry_delay * 2} 秒...")
                time.sleep(retry_delay * 2)
                continue
            else:
                print(f"❌ HTTP 错误: {e}")
                return
        except Exception as e:
            print(f"❌ 获取区块数据时发生未知错误: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            else:
                # 尝试重新初始化client
                print("🔄 尝试重新初始化Tron客户端...")
                client = initialize_tron_client()
                if client is None:
                    print("❌ 重新初始化失败")
                    return
                continue
    else:
        print(f"❌ 区块 {block} 获取失败，已重试 {max_retries} 次")
        return

    # 如果有 RabbitMQ 连接，发送到队列
    if channel:
        rabbitmq_connection(block_list, block)
    else:
        # 没有 RabbitMQ 连接，直接处理
        print(f"📦 本地处理区块 {block}")
        enhanced_local_process_block(block_list, block)

def rabbitmq_connection(block_list, block):
    """发送数据到 RabbitMQ"""
    if not channel:
        print("❌ RabbitMQ 频道不可用，改为本地处理")
        enhanced_local_process_block(block_list, block)
        return
        
    try:
        queue_name = 'telegram'
        channel.queue_declare(queue=queue_name, durable=True)

        message_data = {
            "block_list": block_list,
        }
        message_json = json.dumps(message_data)
        message_bytes = message_json.encode()

        channel.basic_publish(exchange='', routing_key=queue_name, body=message_bytes)
        print(f"✅ 成功发送数据到 RabbitMQ: blockNum: {block}")
        
    except Exception as e:
        print(f"❌ RabbitMQ 发送失败: {e}")
        print("🔄 改为本地处理")
        enhanced_local_process_block(block_list, block)

def callback(ch, method, properties, body) -> None:
    """处理RabbitMQ消息"""
    if not TRONPY_AVAILABLE:
        print("❌ tronpy 模块不可用，无法处理区块链消息")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
        
    try:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        text = body.decode('utf-8')
        block_list = json.loads(text)
        block_list = block_list['block_list']
        enhanced_local_process_block(block_list, block_list['block_header']['raw_data']['number'])

    except Exception as e:
        print(f"❌ 处理RabbitMQ消息失败: {e}")
        import traceback
        traceback.print_exc()

class EpayNotifyHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """重写日志方法，添加时间戳"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")
    
    def do_GET(self):
        print("=== 收到 GET 回调请求 ===")
        print(f"请求路径: {self.path}")
        print(f"请求头: {dict(self.headers)}")
        
        try:
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            params = {}
            for key, value in parse_qs(parsed_url.query).items():
                params[key] = value[0]
            
            print(f"GET参数: {params}")
            
            if parsed_url.path == '/notify' and params:
                self.handle_payment_callback(params)
            elif parsed_url.path == '/return':
                # 返回成功页面
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                html_content = '''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>支付成功</title>
                    <style>
                        body { 
                            text-align: center; 
                            padding: 50px; 
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            margin: 0;
                            min-height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                        }
                        .container {
                            background: rgba(255,255,255,0.1);
                            padding: 40px;
                            border-radius: 20px;
                            backdrop-filter: blur(10px);
                            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                        }
                        .success-icon { font-size: 64px; margin-bottom: 20px; }
                        .title { font-size: 28px; margin: 20px 0; font-weight: bold; }
                        .info { font-size: 16px; margin: 15px 0; opacity: 0.9; }
                        .close-info { font-size: 14px; margin-top: 30px; opacity: 0.7; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success-icon">🎉</div>
                        <div class="title">支付成功！</div>
                        <div class="info">您的充值已完成</div>
                        <div class="info">请返回 Telegram 查看余额</div>
                        <div class="close-info">此页面可以关闭</div>
                    </div>
                    <script>
                        // 3秒后自动提示可以关闭
                        setTimeout(function() {
                            if (window.opener || window.parent !== window) {
                                window.close();
                            }
                        }, 3000);
                    </script>
                </body>
                </html>
                '''
                self.wfile.write(html_content.encode('utf-8'))
            else:
                # 默认响应
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'GET received')
                
        except Exception as e:
            print(f"❌ 处理GET请求错误: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'error')

    def do_POST(self):
        print("=== 收到 POST 回调请求 ===")
        print(f"请求路径: {self.path}")
        print(f"请求头: {dict(self.headers)}")
        
        try:
            # 读取POST数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
            print(f"POST原始数据: {post_data}")
            
            params = {}
            if post_data:
                import urllib.parse
                params = dict(urllib.parse.parse_qsl(post_data))
                print(f"POST解析参数: {params}")
            
            # 如果POST body没有参数，尝试从URL获取
            if not params:
                from urllib.parse import urlparse, parse_qs
                parsed_url = urlparse(self.path)
                for key, value in parse_qs(parsed_url.query).items():
                    params[key] = value[0]
                print(f"URL解析参数: {params}")
            
            if params and params.get('out_trade_no'):
                self.handle_payment_callback(params)
            else:
                print("⚠️ POST请求无有效参数")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'no params')
                
        except Exception as e:
            print(f"❌ 处理POST请求错误: {e}")
            import traceback
            traceback.print_exc()
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'error')

    def handle_payment_callback(self, params):
        """统一处理支付回调 - 完整修复版"""
        try:
            print(f"🔍 开始处理支付回调")
            print(f"📋 回调参数: {params}")
            
            # 1. 验证必要参数
            required_params = ['out_trade_no', 'trade_status', 'money']
            missing_params = [p for p in required_params if p not in params]
            
            if missing_params:
                print(f"❌ 缺少必要参数: {missing_params}")
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'missing params: {missing_params}'.encode())
                return

            # 2. 验证签名
            print("🔍 开始验证签名...")
            if not verify_epay_notify(params.copy(), EPAY_CONFIG['key']):
                print("❌ 签名验证失败")
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'sign error')
                return
            
            print("✅ 签名验证成功")

            # 3. 检查支付状态
            trade_status = params.get('trade_status')
            if trade_status != 'TRADE_SUCCESS':
                print(f"⚠️ 支付状态不是成功: {trade_status}")
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'success')
                return

            # 4. 提取订单信息
            out_trade_no = params.get('out_trade_no')
            money = float(params.get('money', 0))
            trade_no = params.get('trade_no', '')
            
            print(f"💰 支付成功信息:")
            print(f"   订单号: {out_trade_no}")
            print(f"   金额: ¥{money}")
            print(f"   第三方订单号: {trade_no}")
            
            # 5. 查找对应的充值订单
            print("🔍 查找充值订单...")
            order = topup.find_one({'bianhao': out_trade_no})
            if not order:
                print(f"❌ 未找到订单: {out_trade_no}")
                # 即使找不到订单也返回success，避免第三方重复通知
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'success')
                return
            
            print(f"✅ 找到订单: {order}")
            
            # 6. 检查订单是否已处理（防重复处理）
            if order.get('epay_status') == 'success':
                print("⚠️ 订单已处理过，跳过")
                
                # 🔥 关键修复：确保已处理的订单被删除
                try:
                    # 多重删除确保成功
                    delete_result = topup.delete_one({'bianhao': out_trade_no})
                    if delete_result.deleted_count == 0:
                        # 如果按订单号删除失败，按用户ID和金额删除
                        topup.delete_many({
                            'user_id': order['user_id'],
                            'money': money
                        })
                    
                    # 兜底：标记为已处理
                    topup.update_many(
                        {'user_id': order['user_id'], 'money': money},
                        {'$set': {'epay_status': 'completed'}}
                    )
                    
                    print(f"✅ 订单 {out_trade_no} 清理完成")
                    
                except Exception as e:
                    print(f"❌ 清理订单失败: {e}")
                
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'success')
                return

            user_id = order['user_id']
            print(f"👤 订单用户: {user_id}")
            
            # 7. 验证金额是否匹配（可选，根据业务需求）
            order_amount = order.get('money', 0)
            if abs(float(order_amount) - money) > 0.01:  # 允许0.01的误差
                print(f"⚠️ 金额不匹配: 订单¥{order_amount} vs 回调¥{money}")
                # 根据业务需求决定是否继续处理
            
            # 8. 更新用户余额
            print("💰 开始更新用户余额...")
            user_doc = user.find_one({'user_id': user_id})
            if not user_doc:
                print(f"❌ 未找到用户: {user_id}")
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'user not found')
                return
            
            old_balance = float(user_doc.get('USDT', 0))
            new_balance = round(old_balance + money, 2)
            
            print(f"💰 余额变化: ¥{old_balance} -> ¥{new_balance}")
            
            # 9. 执行数据库更新（使用事务思想）
            try:
                print("🔄 开始数据库更新...")
                
                # 更新用户余额
                user_update_result = user.update_one(
                    {'user_id': user_id}, 
                    {'$set': {'USDT': new_balance}}
                )
                
                if user_update_result.modified_count == 0:
                    raise Exception("用户余额更新失败")
                
                print("✅ 用户余额更新成功")
                
                # 标记订单已处理
                order_update_result = topup.update_one(
                    {'bianhao': out_trade_no},
                    {'$set': {
                        'epay_status': 'success', 
                        'processed_time': time.time(),
                        'trade_no': trade_no,
                        'actual_amount': money
                    }}
                )
                
                print("✅ 订单状态更新成功")
                
                # 记录充值日志
                timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                user_log.insert_one({
                    'uid': out_trade_no,
                    'projectname': '易支付充值',
                    'user_id': user_id,
                    'today_money': money,
                    'today_time': timer
                })
                
                print("✅ 充值日志记录成功")
                
                # 创建通知记录（让机器人发送通知给用户）
                notification_doc = {
                    'user_id': user_id,
                    'type': 'payment_success',
                    'amount': money,
                    'old_balance': old_balance,
                    'new_balance': new_balance,
                    'order_no': out_trade_no,
                    'trade_no': trade_no,
                    'payment_method': '易支付',
                    'created_at': timer,
                    'timestamp': time.time(),
                    'processed': False
                }
                
                notifications.insert_one(notification_doc)
                print("✅ 通知记录创建成功")
                
                # 🔥 关键修复：多重删除确保订单被正确清理
                print("🗑️ 开始清理订单...")
                deleted_count = 0
                
                try:
                    # 方法1: 按订单号删除
                    result1 = topup.delete_one({'bianhao': out_trade_no})
                    deleted_count += result1.deleted_count
                    print(f"🗑️ 按订单号删除: {result1.deleted_count} 条")
                    
                    # 方法2: 如果按订单号删除失败，按用户ID和金额删除
                    if result1.deleted_count == 0:
                        print("⚠️ 按订单号删除失败，尝试按条件删除...")
                        result2 = topup.delete_many({
                            'user_id': user_id,
                            'money': money,
                            'epay_status': 'success'
                        })
                        deleted_count += result2.deleted_count
                        print(f"🗑️ 按条件删除: {result2.deleted_count} 条")
                    
                    # 方法3: 兜底方案 - 删除该用户所有相同金额的订单
                    if deleted_count == 0:
                        print("⚠️ 前面删除都失败，使用兜底方案...")
                        result3 = topup.delete_many({
                            'user_id': user_id,
                            'money': money
                        })
                        deleted_count += result3.deleted_count
                        print(f"🗑️ 兜底删除: {result3.deleted_count} 条")
                    
                    print(f"✅ 总计删除订单: {deleted_count} 条")
                    
                except Exception as delete_error:
                    print(f"❌ 删除订单过程中出错: {delete_error}")
                    # 如果删除失败，至少要标记为已完成，避免重复处理
                    try:
                        topup.update_many(
                            {'user_id': user_id, 'money': money},
                            {'$set': {'epay_status': 'completed', 'processed_time': time.time()}}
                        )
                        print("🔄 已标记相关订单为已完成")
                    except Exception as mark_error:
                        print(f"❌ 标记订单失败: {mark_error}")
                
                print(f"🎉 支付处理完全成功！")
                print(f"   用户: {user_id}")
                print(f"   订单: {out_trade_no}")
                print(f"   金额: ¥{money}")
                print(f"   余额: ¥{old_balance} -> ¥{new_balance}")
                print(f"   删除订单: {deleted_count} 条")
                
            except Exception as db_error:
                print(f"❌ 数据库更新失败: {db_error}")
                import traceback
                traceback.print_exc()
                
                # 尝试回滚（如果支持的话）
                try:
                    # 如果用户余额已更新但订单状态未更新，尝试回滚
                    current_user = user.find_one({'user_id': user_id})
                    if current_user and current_user.get('USDT') == new_balance:
                        user.update_one(
                            {'user_id': user_id}, 
                            {'$set': {'USDT': old_balance}}
                        )
                        print("🔄 已回滚用户余额")
                except Exception as rollback_error:
                    print(f"❌ 回滚失败: {rollback_error}")
                
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'database error')
                return
            
            # 10. 响应成功
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'success')
            
            print("✅ 回调处理完成，已响应success")
            
        except Exception as e:
            print(f"❌ 处理支付回调发生异常: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'internal error')

def start_epay_server():
    """启动易支付回调服务器"""
    try:
        server = HTTPServer(('0.0.0.0', 8888), EpayNotifyHandler)
        print("✅ 易支付回调服务器启动成功")
        print(f"📡 监听地址: 0.0.0.0:8888")
        print(f"🔗 回调地址: {EPAY_CONFIG['notify_url']}")
        print(f"🔙 返回地址: {EPAY_CONFIG['return_url']}")
        print("🚀 服务器运行中...")
        server.serve_forever()
    except Exception as e:
        print(f"❌ 易支付服务器启动失败: {e}")
        import traceback
        traceback.print_exc()

def test_epay_callback():
    """测试易支付回调功能"""
    print("🧪 开始测试易支付回调...")
    
    # 创建测试订单
    test_order_id = f"test_{int(time.time())}"
    test_user_id = 123456789
    test_amount = 10.0
    
    # 先在数据库中创建测试订单
    try:
        topup.insert_one({
            'bianhao': test_order_id,
            'user_id': test_user_id,
            'money': test_amount,
            'pay_type': 'test',
            'timer': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'epay_status': 'pending'
        })
        print(f"✅ 测试订单创建成功: {test_order_id}")
    except Exception as e:
        print(f"❌ 创建测试订单失败: {e}")
        return
    
    # 生成测试回调参数
    test_params = {
        'pid': EPAY_CONFIG['pid'],
        'trade_no': f'epay_test_{int(time.time())}',
        'out_trade_no': test_order_id,
        'type': 'wxpay',
        'name': '充值USDT',
        'money': str(test_amount),
        'trade_status': 'TRADE_SUCCESS'
    }
    
    # 生成签名
    sorted_params = sorted(test_params.items())
    param_str = '&'.join([f'{k}={v}' for k, v in sorted_params if v != ''])
    sign_str = param_str + EPAY_CONFIG['key']
    test_params['sign'] = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    test_params['sign_type'] = 'MD5'
    
    print(f"🧪 测试参数: {test_params}")
    
    # 验证签名
    sign_valid = verify_epay_notify(test_params.copy(), EPAY_CONFIG['key'])
    print(f"🔍 签名验证: {sign_valid}")
    
    if sign_valid:
        print("✅ 测试通过：签名验证正常")
    else:
        print("❌ 测试失败：签名验证失败")
    
    # 清理测试数据
    try:
        topup.delete_one({'bianhao': test_order_id})
        print("🗑️ 测试数据已清理")
    except Exception as e:
        print(f"⚠️ 清理测试数据失败: {e}")

def start_blockchain_monitor():
    """启动区块链监控"""
    global client
    
    if not TRONPY_AVAILABLE:
        print("❌ tronpy不可用，无法启动区块链监控")
        return
        
    client = initialize_tron_client()
    if client is None:
        print("❌ 无法初始化Tron客户端，区块链监控启动失败")
        return
        
    try:
        # 测试 Tron 连接
        latest_block = client.get_latest_block()
        print("✅ Tron 网络连接正常")
        
        # 获取最新的区块
        block = latest_block['block_header']['raw_data']['number'] - 1
        print(f"🚀 开始监控，起始区块: {block}")
        
        while True:
            try:
                get_data(block)
                block += 1
                
                # 添加适当的延迟，避免 API 频率限制
                time.sleep(0.5)  # 每次请求间隔 0.5 秒
                
            except KeyboardInterrupt:
                print("\n❌ 用户中断程序")
                break
            except Exception as e:
                print(f"❌ 区块链监控循环错误: {e}")
                time.sleep(5)  # 出错时等待5秒再继续
                continue
                
    except Exception as e:
        print(f"❌ 区块链监控启动失败: {e}")

if __name__ == '__main__':
    try:
        print("🚀 启动统一支付监控系统...")
        print("=" * 50)
        
        # 初始化连接
        print("🔌 正在初始化连接...")
        
        # 初始化 Tron 客户端
        if TRONPY_AVAILABLE:
            client = initialize_tron_client()
            if client:
                print("✅ Tron 客户端初始化成功")
            else:
                print("❌ Tron 客户端初始化失败")
        
        # 初始化 RabbitMQ
        if PIKA_AVAILABLE:
            connection = create_rabbitmq_connection()
            if connection:
                try:
                    channel = connection.channel()
                    print("✅ RabbitMQ 连接成功")
                except Exception as e:
                    print(f"❌ 创建频道失败: {e}")
                    connection = None
                    channel = None
        
        print("=" * 50)
        
        # 1. 启动易支付服务器
        print("📡 启动易支付回调服务器...")
        epay_thread = threading.Thread(target=start_epay_server, daemon=True)
        epay_thread.start()
        print("✅ 易支付服务器线程已启动")
        
        # 等待服务器启动
        time.sleep(2)
        
        # 2. 测试各个组件
        print("🧪 开始组件测试...")
        
        # 测试MongoDB连接
        try:
            from mongo import mongo_instance
            mongo_instance.client.admin.command('ping')
            print("✅ MongoDB 连接正常")
        except Exception as e:
            print(f"❌ MongoDB 连接失败: {e}")

        # 测试易支付回调
        test_epay_callback()
        
        print("=" * 50)
        
        # 3. 启动相应的监控服务
        if PIKA_AVAILABLE and connection and channel:
            print("🔄 启动 RabbitMQ 消费者模式...")
            try:
                channel.queue_declare(queue='telegram', durable=True)
                print("✅ RabbitMQ 队列准备就绪")
                print("🚀 开始监听区块链数据...")
                channel.basic_consume('telegram', callback)
                channel.start_consuming()
            except KeyboardInterrupt:
                print("\n❌ 用户中断程序")
                channel.stop_consuming()
            except Exception as e:
                print(f"❌ RabbitMQ 消费失败: {e}")
            finally:
                if connection and not connection.is_closed:
                    connection.close()
                    print("✅ RabbitMQ 连接已关闭")
        
        elif TRONPY_AVAILABLE and client:
            print("🔄 启动直接区块链监控模式...")
            blockchain_thread = threading.Thread(target=start_blockchain_monitor, daemon=True)
            blockchain_thread.start()
            print("✅ 区块链监控线程已启动")
            
            # 保持程序运行
            try:
                while True:
                    time.sleep(60)
                    print(f"💗 系统运行中... {time.strftime('%H:%M:%S')}")
            except KeyboardInterrupt:
                print("\n❌ 程序退出")
        
        else:
            print("⚠️ 区块链监控不可用，仅运行易支付服务")
            print("🔄 保持程序运行...")
            try:
                while True:
                    time.sleep(60)
                    print(f"💗 易支付服务运行中... {time.strftime('%H:%M:%S')}")
            except KeyboardInterrupt:
                print("\n❌ 程序退出")

    except Exception as e:
        print(f"❌ 系统启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理连接
        print("🧹 正在清理资源...")
        if 'connection' in locals() and connection and not connection.is_closed:
            try:
                connection.close()
                print("✅ RabbitMQ 连接已关闭")
            except:
                pass
        print("👋 程序已完全退出")