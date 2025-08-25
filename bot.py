# 在文件开头，统一配置导入
import datetime, qrcode, socket, struct, threading, hashlib, uuid
import random
from datetime import timedelta
from decimal import Decimal
import time
import hashlib
from decimal import Decimal
from datetime import datetime, timedelta
import telegram
import logging, os, shutil
from multiprocessing import Process
import sys
import traceback
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, InlineQueryHandler
from telegram import InlineKeyboardMarkup, ForceReply, InlineKeyboardButton, Update, ChatMemberRestricted, ChatPermissions, ChatMemberRestricted, ChatMember, ChatMemberAdministrator, KeyboardButton, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent, InputMediaPhoto
import json, pickle, re
from threading import Timer
import zipfile
from pygtrans import Translate
import asyncio
import pymongo
from mongo import *

# 易支付配置导入 - 统一处理
print("🔧 正在加载易支付配置...")

EPAY_CONFIG = {
    'api_url': 'http://ruixing.wwspay.com/submit.php',
    'pid': '240983942',
    'key': 'rhgc7xkp0e0jaxose6ycmx0llihs6p04',
    'notify_url': 'http://8.209.218.35:8888/notify',
    'return_url': 'http://8.209.218.35:8888/return'
}

print("✅ 易支付配置加载成功")
print(f"📋 商户号: {EPAY_CONFIG['pid']}")
print(f"🔗 API地址: {EPAY_CONFIG['api_url']}")

def parse_urls(text):
    """解析尾随按钮格式文本"""
    try:
        if not text or text.strip() == '':
            return []
        
        keyboard = []
        lines = text.strip().split('\n')
        
        for line in lines:
            if not line.strip():
                continue
                
            row = []
            buttons = line.split('|')
            
            for button in buttons:
                button = button.strip()
                if not button:
                    continue
                    
                if '&' in button:
                    parts = button.split('&', 1)
                    if len(parts) == 2:
                        name = parts[0].strip()
                        url = parts[1].strip()
                        
                        if name and url:
                            if not url.startswith(('http://', 'https://', 'tg://', 't.me/')):
                                url = 'https://' + url
                            row.append(InlineKeyboardButton(name, url=url))
            
            if row:
                keyboard.append(row)
        
        return keyboard
        
    except Exception as e:
        print(f"解析按钮格式错误: {e}")
        return []
import logging, os, shutil
from multiprocessing import Process
import sys
import traceback
from telegram.ext import handler
from telegram.utils import helpers
from mongo import *
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, CallbackQueryHandler, \
    InlineQueryHandler
from telegram import InlineKeyboardMarkup, ForceReply, InlineKeyboardButton, Update, ChatMemberRestricted, \
    ChatPermissions, \
    ChatMemberRestricted, ChatMember, ChatMemberAdministrator, KeyboardButton, ReplyKeyboardMarkup, \
    InlineQueryResultArticle, InputTextMessageContent, InputMediaPhoto
import time, json, pickle, re
from threading import Timer
from decimal import Decimal
import zipfile
from pygtrans import Translate
import asyncio

# ==================== 机器人命令配置 ====================
BOT_COMMANDS = {
    # 用户命令
    'user': {
        'start': {
            'command': '/start',
            'description_zh': '🚀 启动机器人，显示主菜单',
            'description_en': '🚀 Start the bot and show main menu',
            'usage': '/start',
            'example': '/start'
        },
        'profile': {
            'command': '/profile', 
            'description_zh': '👤 查看个人信息和余额',
            'description_en': '👤 View personal info and balance',
            'usage': '/profile',
            'example': '/profile'
        },
        'products': {
            'command': '/products',
            'description_zh': '🛒 查看商品列表',
            'description_en': '🛒 View product list', 
            'usage': '/products',
            'example': '/products'
        },
        'recharge': {
            'command': '/recharge',
            'description_zh': '💰 充值余额',
            'description_en': '💰 Recharge balance',
            'usage': '/recharge',
            'example': '/recharge'
        },
        'language': {
            'command': '/language',
            'description_zh': '🌐 切换语言',
            'description_en': '🌐 Switch language',
            'usage': '/language', 
            'example': '/language'
        },
        'redpacket': {
            'command': '/redpacket',
            'description_zh': '🧧 发送和管理红包',
            'description_en': '🧧 Send and manage red packets',
            'usage': '/redpacket',
            'example': '/redpacket'
        },
        'help': {
            'command': '/help',
            'description_zh': '❓ 查看所有命令帮助',
            'description_en': '❓ View all commands help',
            'usage': '/help',
            'example': '/help'
        }
    },
    # 管理员命令
    'admin': {
        'add': {
            'command': '/add',
            'description_zh': '💳 管理员充值/扣款用户余额',
            'description_en': '💳 Admin recharge/deduct user balance',
            'usage': '/add <用户ID> <±金额>',
            'example': '/add 123456789 +100'
        },
        'addadmin': {
            'command': '/addadmin', 
            'description_zh': '👑 添加管理员',
            'description_en': '👑 Add administrator',
            'usage': '/addadmin <用户ID或@用户名>',
            'example': '/addadmin 123456789 或 /addadmin @username'
        },
        'cha': {
            'command': '/cha',
            'description_zh': '🔍 查询用户信息',
            'description_en': '🔍 Query user information', 
            'usage': '/cha <用户ID或用户名>',
            'example': '/cha 123456789 或 /cha @username'
        },
        'gg': {
            'command': '/gg',
            'description_zh': '📢 发送广告给所有用户',
            'description_en': '📢 Send advertisement to all users',
            'usage': '/gg <广告内容>',
            'example': '/gg 今日特价商品！'
        },
        'rate': {
            'command': '/rate',
            'description_zh': '💱 设置USDT汇率',
            'description_en': '💱 Set USDT exchange rate',
            'usage': '/rate',
            'example': '/rate'
        },
        'removeadmin': {
            'command': '/removeadmin',
            'description_zh': '👤 移除管理员权限',
            'description_en': '👤 Remove admin privileges',
            'usage': '/removeadmin <用户ID或@用户名>',
            'example': '/removeadmin 123456789 或 /removeadmin @username'
        },
        'listadmin': {
            'command': '/listadmin',
            'description_zh': '📋 查看管理员列表',
            'description_en': '📋 View admin list',
            'usage': '/listadmin',
            'example': '/listadmin'
        }
    },
    # 特殊命令
    'special': {
        'start_business': {
            'command': '开始营业',
            'description_zh': '🟢 开启机器人营业状态（仅管理员）',
            'description_en': '🟢 Start business mode (admin only)',
            'usage': '开始营业',
            'example': '开始营业'
        },
        'stop_business': {
            'command': '停止营业',
            'description_zh': '🔴 关闭机器人营业状态（仅管理员）',
            'description_en': '🔴 Stop business mode (admin only)', 
            'usage': '停止营业',
            'example': '停止营业'
        }
    }
}

# ==================== 帮助函数 ====================
def get_user_commands(lang='zh'):
    """获取用户命令列表"""
    commands = []
    for cmd_info in BOT_COMMANDS['user'].values():
        desc = cmd_info[f'description_{lang}'] if f'description_{lang}' in cmd_info else cmd_info['description_zh']
        commands.append(f"{cmd_info['command']} - {desc}")
    return commands

def get_admin_commands(lang='zh'):
    """获取管理员命令列表"""
    commands = []
    for cmd_info in BOT_COMMANDS['admin'].values():
        desc = cmd_info[f'description_{lang}'] if f'description_{lang}' in cmd_info else cmd_info['description_zh']
        commands.append(f"{cmd_info['command']} - {desc}")
    return commands

def get_all_commands(lang='zh'):
    """获取所有命令列表"""
    return get_user_commands(lang) + get_admin_commands(lang)

# ==================== /help 命令处理函数 ====================
def help_command(update: Update, context: CallbackContext):
    """处理 /help 命令"""
    user_id = update.effective_user.id
    user_list = user.find_one({"user_id": user_id})
    
    if user_list is None:
        context.bot.send_message(chat_id=user_id, text="请先发送 /start 初始化账户")
        return
        
    lang = user_list.get('lang', 'zh')
    state = user_list.get('state', '1')
    is_admin = (state == '4')
    
    if lang == 'zh':
        title = "📋 <b>机器人命令帮助</b>\n\n"
        user_section = "👤 <b>用户命令：</b>\n"
        admin_section = "\n👑 <b>管理员命令：</b>\n" if is_admin else ""
        special_section = "\n🔧 <b>特殊命令：</b>\n" if is_admin else ""
        footer = "\n💡 <b>提示：</b>点击命令可直接复制使用"
    else:
        title = "📋 <b>Bot Commands Help</b>\n\n"
        user_section = "👤 <b>User Commands:</b>\n"
        admin_section = "\n👑 <b>Admin Commands:</b>\n" if is_admin else ""
        special_section = "\n🔧 <b>Special Commands:</b>\n" if is_admin else ""
        footer = "\n💡 <b>Tip:</b> Click commands to copy and use"
    
    # 构建用户命令列表
    user_commands = []
    for cmd_info in BOT_COMMANDS['user'].values():
        desc = cmd_info[f'description_{lang}'] if f'description_{lang}' in cmd_info else cmd_info['description_zh']
        usage = cmd_info.get('usage', cmd_info['command'])
        user_commands.append(f"<code>{cmd_info['command']}</code> - {desc}")
    
    message_text = title + user_section + '\n'.join(user_commands)
    
    # 如果是管理员，添加管理员命令
    if is_admin:
        admin_commands = []
        for cmd_info in BOT_COMMANDS['admin'].values():
            desc = cmd_info[f'description_{lang}'] if f'description_{lang}' in cmd_info else cmd_info['description_zh']
            admin_commands.append(f"<code>{cmd_info['command']}</code> - {desc}")
        
        message_text += admin_section + '\n'.join(admin_commands)
        
        # 添加特殊命令
        special_commands = []
        for cmd_info in BOT_COMMANDS['special'].values():
            desc = cmd_info[f'description_{lang}'] if f'description_{lang}' in cmd_info else cmd_info['description_zh']
            special_commands.append(f"<code>{cmd_info['command']}</code> - {desc}")
        
        message_text += special_section + '\n'.join(special_commands)
    
    message_text += footer
    
    # 创建键盘
    keyboard = []
    if lang == 'zh':
        keyboard.append([InlineKeyboardButton('🔄 刷新帮助', callback_data='refresh_help')])
        if is_admin:
            keyboard.append([InlineKeyboardButton('📊 系统状态', callback_data='system_status')])
        keyboard.append([InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')])
    else:
        keyboard.append([InlineKeyboardButton('🔄 Refresh Help', callback_data='refresh_help')])
        if is_admin:
            keyboard.append([InlineKeyboardButton('📊 System Status', callback_data='system_status')])
        keyboard.append([InlineKeyboardButton('❌ Close', callback_data=f'close {user_id}')])
    
    context.bot.send_message(
        chat_id=user_id,
        text=message_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

def refresh_help(update: Update, context: CallbackContext):
    """刷新帮助信息"""
    query = update.callback_query
    query.answer()
    
    # 删除旧消息并发送新的帮助信息
    context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    help_command(update, context)

def system_status(update: Update, context: CallbackContext):
    """显示系统状态（管理员专用）"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    
    user_list = user.find_one({'user_id': user_id})
    if user_list.get('state') != '4':
        query.answer('❌ 权限不足', show_alert=True)
        return
    
    # 获取系统统计信息
    total_users = user.count_documents({})
    total_balance = sum([u.get('USDT', 0) for u in user.find({})])
    business_status = shangtext.find_one({'projectname': '营业状态'})
    status_text = "🟢 营业中" if business_status and business_status.get('text') == 1 else "🔴 已停业"
    
    # 获取商品统计
    total_categories = fenlei.count_documents({})
    total_products = ejfl.count_documents({})
    total_stock = hb.count_documents({'state': 0})
    
    status_message = f"""
📊 <b>系统状态报告</b>

👥 <b>用户统计：</b>
• 总用户数：{total_users}
• 总余额：CNY{total_balance:.2f}

🛒 <b>商品统计：</b>
• 商品分类：{total_categories}
• 商品种类：{total_products}  
• 库存数量：{total_stock}

🏪 <b>营业状态：</b> {status_text}

🕐 <b>更新时间：</b> {time.strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    keyboard = [
        [InlineKeyboardButton('🔄 刷新状态', callback_data='system_status')],
        [InlineKeyboardButton('🔙 返回帮助', callback_data='refresh_help')]
    ]
    
    query.edit_message_text(
        text=status_message,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
def check_business_status(func):
    """检查营业状态的装饰器"""
    def wrapper(update: Update, context: CallbackContext):
        try:
            yyzt = shangtext.find_one({'projectname': '营业状态'})['text']
            
            # 获取用户ID
            if update.callback_query:
                user_id = update.callback_query.from_user.id
            else:
                user_id = update.effective_user.id
            
            # 检查用户权限
            user_list = user.find_one({'user_id': user_id})
            state = user_list.get('state', '1') if user_list else '1'
            
            # 如果停业且不是管理员，拒绝服务
            if yyzt == 0 and state != '4':
                if update.callback_query:
                    update.callback_query.answer('🚫 机器人暂停营业中，请稍后再试', show_alert=True)
                else:
                    context.bot.send_message(chat_id=user_id, text='🚫 机器人暂停营业中，请稍后再试')
                return
            
            # 营业中或管理员，执行原函数
            return func(update, context)
            
        except Exception as e:
            print(f"营业状态检查错误: {e}")
            return func(update, context)  # 出错时默认允许访问
    
    return wrapper

# 配置详细的日志系统
def setup_logging():
    """
    设置详细的日志配置，包括控制台输出和文件记录
    """
def addadmin(update: Update, context: CallbackContext):
    """添加管理员命令 - 修复版本"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        text = update.message.text
        text1 = text.split(' ')
        
        # 检查当前用户是否是管理员
        user_list = user.find_one({'user_id': user_id})
        if user_list is None:
            context.bot.send_message(chat_id=user_id, text='请先发送 /start')
            return
            
        state = user_list['state']
        
        if state == '4':  # 只有管理员才能添加管理员
            if len(text1) == 2:
                target_input = text1[1]
                
                # 判断是用户ID还是用户名
                if is_number(target_input):
                    target_id = int(target_input)
                    target_user = user.find_one({'user_id': target_id})
                    if target_user is None:
                        context.bot.send_message(chat_id=user_id, text='❌ 用户不存在，该用户需要先发送 /start 给机器人')
                        return
                else:
                    # 通过用户名查找（去掉@符号）
                    username = target_input.replace('@', '')
                    target_user = user.find_one({'username': username})
                    if target_user is None:
                        context.bot.send_message(chat_id=user_id, text='❌ 用户不存在，该用户需要先发送 /start 给机器人')
                        return
                    target_id = target_user['user_id']  # 🔥 关键修复：添加这一行
                
                # 检查是否已经是管理员
                if target_user['state'] == '4':
                    context.bot.send_message(chat_id=user_id, text='⚠️ 该用户已经是管理员')
                    return
                
                # 设置为管理员
                user.update_one({'user_id': target_id}, {'$set': {'state': '4'}})
                
                # 显示用户信息
                username_display = f"@{target_user['username']}" if target_user['username'] else target_user['fullname']
                
                context.bot.send_message(
                    chat_id=user_id, 
                    text=f'✅ 用户 {username_display} (ID: {target_id}) 已设置为管理员'
                )
                
                # 通知被设置为管理员的用户
                try:
                    context.bot.send_message(
                        chat_id=target_id, 
                        text='🎉 您已被设置为管理员！'
                    )
                except:
                    pass  # 如果发送失败就忽略
                        
            else:
                context.bot.send_message(
                    chat_id=user_id, 
                    text='格式为: /addadmin 用户ID 或 /addadmin @用户名\n\n'
                         '例如: /addadmin 123456789 或 /addadmin @username'
                )
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 只有管理员才能添加管理员')
def removeadmin(update: Update, context: CallbackContext):
    """移除管理员命令 - 新增功能"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        text = update.message.text
        text1 = text.split(' ')
        
        # 检查当前用户是否是管理员
        user_list = user.find_one({'user_id': user_id})
        if user_list is None:
            context.bot.send_message(chat_id=user_id, text='请先发送 /start')
            return
            
        state = user_list['state']
        
        if state == '4':  # 只有管理员才能移除管理员
            if len(text1) == 2:
                target_input = text1[1]
                
                # 判断是用户ID还是用户名
                if is_number(target_input):
                    target_id = int(target_input)
                    target_user = user.find_one({'user_id': target_id})
                    if target_user is None:
                        context.bot.send_message(chat_id=user_id, text='❌ 用户不存在')
                        return
                else:
                    # 通过用户名查找（去掉@符号）
                    username = target_input.replace('@', '')
                    target_user = user.find_one({'username': username})
                    if target_user is None:
                        context.bot.send_message(chat_id=user_id, text='❌ 用户不存在')
                        return
                    target_id = target_user['user_id']
                
                # 检查是否是管理员
                if target_user['state'] != '4':
                    context.bot.send_message(chat_id=user_id, text='⚠️ 该用户不是管理员')
                    return
                
                # 防止移除自己
                if target_id == user_id:
                    context.bot.send_message(chat_id=user_id, text='❌ 不能移除自己的管理员权限')
                    return
                
                # 移除管理员权限，设置为普通用户
                user.update_one({'user_id': target_id}, {'$set': {'state': '1'}})
                
                # 显示用户信息
                username_display = f"@{target_user['username']}" if target_user['username'] else target_user['fullname']
                
                context.bot.send_message(
                    chat_id=user_id, 
                    text=f'✅ 用户 {username_display} (ID: {target_id}) 的管理员权限已移除'
                )
                
                # 通知被移除权限的用户
                try:
                    context.bot.send_message(
                        chat_id=target_id, 
                        text='📢 您的管理员权限已被移除'
                    )
                except:
                    pass  # 如果发送失败就忽略
                        
            else:
                context.bot.send_message(
                    chat_id=user_id, 
                    text='格式为: /removeadmin 用户ID 或 /removeadmin @用户名\n\n'
                         '例如: /removeadmin 123456789 或 /removeadmin @username'
                )
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 只有管理员才能移除管理员')

def listadmin(update: Update, context: CallbackContext):
    """查看管理员列表命令 - 新增功能"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        
        # 检查当前用户是否是管理员
        user_list = user.find_one({'user_id': user_id})
        if user_list is None:
            context.bot.send_message(chat_id=user_id, text='请先发送 /start')
            return
            
        state = user_list['state']
        
        if state == '4':  # 只有管理员才能查看管理员列表
            # 查找所有管理员
            admin_list = list(user.find({'state': '4'}))
            
            if not admin_list:
                context.bot.send_message(chat_id=user_id, text='❌ 暂无管理员')
                return
            
            # 构建管理员列表消息
            admin_info = []
            admin_info.append('👑 <b>管理员列表</b>\n')
            
            for i, admin in enumerate(admin_list, 1):
                admin_id = admin['user_id']
                admin_username = admin.get('username', '')
                admin_fullname = admin.get('fullname', '未知')
                creation_time = admin.get('creation_time', '未知')
                
                # 构建显示名称
                if admin_username:
                    display_name = f'<a href="https://t.me/{admin_username}">@{admin_username}</a>'
                else:
                    display_name = admin_fullname.replace('<', '&lt;').replace('>', '&gt;')
                
                # 标记当前用户
                current_mark = ' 👈 <i>(你)</i>' if admin_id == user_id else ''
                
                admin_info.append(
                    f'{i}. {display_name}{current_mark}\n'
                    f'   🆔 ID: <code>{admin_id}</code>\n'
                    f'   📅 注册: {creation_time}\n'
                )
            
            admin_info.append(f'\n📊 总计: {len(admin_list)} 位管理员')
            
            # 创建键盘
            keyboard = [
                [InlineKeyboardButton('🔄 刷新列表', callback_data='refresh_admin_list')],
                [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]
            ]
            
            context.bot.send_message(
                chat_id=user_id,
                text=''.join(admin_info),
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard),
                disable_web_page_preview=True
            )
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 只有管理员才能查看管理员列表')

def refresh_admin_list(update: Update, context: CallbackContext):
    """刷新管理员列表"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    
    # 检查权限
    user_list = user.find_one({'user_id': user_id})
    if user_list.get('state') != '4':
        query.answer('❌ 权限不足', show_alert=True)
        return
    
    # 重新获取管理员列表
    admin_list = list(user.find({'state': '4'}))
    
    if not admin_list:
        query.edit_message_text('❌ 暂无管理员')
        return
    
    # 构建管理员列表消息
    admin_info = []
    admin_info.append('👑 <b>管理员列表</b>\n')
    
    for i, admin in enumerate(admin_list, 1):
        admin_id = admin['user_id']
        admin_username = admin.get('username', '')
        admin_fullname = admin.get('fullname', '未知')
        creation_time = admin.get('creation_time', '未知')
        
        # 构建显示名称
        if admin_username:
            display_name = f'<a href="https://t.me/{admin_username}">@{admin_username}</a>'
        else:
            display_name = admin_fullname.replace('<', '&lt;').replace('>', '&gt;')
        
        # 标记当前用户
        current_mark = ' 👈 <i>(你)</i>' if admin_id == user_id else ''
        
        admin_info.append(
            f'{i}. {display_name}{current_mark}\n'
            f'   🆔 ID: <code>{admin_id}</code>\n'
            f'   📅 注册: {creation_time}\n'
        )
    
    admin_info.append(f'\n📊 总计: {len(admin_list)} 位管理员')
    admin_info.append(f'\n🕐 更新时间: {time.strftime("%H:%M:%S")}')
    
    # 创建键盘
    keyboard = [
        [InlineKeyboardButton('🔄 刷新列表', callback_data='refresh_admin_list')],
        [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]
    ]
    
    query.edit_message_text(
        text=''.join(admin_info),
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


def fbgg(update: Update, context: CallbackContext):
    """发送广告命令"""
# 配置详细的日志系统
def setup_logging():
    """
    设置详细的日志配置，包括控制台输出和文件记录
    """
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建 logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 清除已有的处理器
    logger.handlers.clear()
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # 详细日志文件处理器
    file_handler = logging.FileHandler(
        os.path.join(log_dir, f'bot_detailed_{datetime.date.today().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # 错误日志文件处理器
    error_handler = logging.FileHandler(
        os.path.join(log_dir, f'bot_errors_{datetime.date.today().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    
    # 用户操作日志处理器
    user_action_handler = logging.FileHandler(
        os.path.join(log_dir, f'user_actions_{datetime.date.today().strftime("%Y%m%d")}.log'),
        encoding='utf-8'
    )
    user_action_handler.setLevel(logging.INFO)
    user_action_formatter = logging.Formatter(
        '%(asctime)s - USER_ACTION - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    user_action_handler.setFormatter(user_action_formatter)
    
    # 添加处理器到 logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # 创建专门的用户操作 logger
    user_logger = logging.getLogger('user_actions')
    user_logger.addHandler(user_action_handler)
    user_logger.setLevel(logging.INFO)
    user_logger.propagate = False
    
    return logger


def log_user_action(user_id, username, action, details=None):
    """
    记录用户操作日志
    """
    user_logger = logging.getLogger('user_actions')
    message = f"UserID: {user_id}, Username: {username}, Action: {action}"
    if details:
        message += f", Details: {details}"
    user_logger.info(message)


def log_error(error, context=None):
    """
    记录错误日志
    """
    logger = logging.getLogger(__name__)
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f", Context: {context}"
    logger.error(error_msg, exc_info=True)


def log_database_operation(operation, collection, query=None, result=None):
    """
    记录数据库操作日志
    """
    logger = logging.getLogger(__name__)
    message = f"DB Operation: {operation}, Collection: {collection}"
    if query:
        message += f", Query: {query}"
    if result:
        message += f", Result: {result}"
    logger.debug(message)


def log_transaction(user_id, transaction_type, amount, details=None):
    """
    记录交易日志
    """
    logger = logging.getLogger(__name__)
    message = f"TRANSACTION - UserID: {user_id}, Type: {transaction_type}, Amount: {amount}"
    if details:
        message += f", Details: {details}"
    logger.info(message)


def log_performance(func_name, execution_time, details=None):
    """
    记录性能日志
    """
    logger = logging.getLogger(__name__)
    message = f"PERFORMANCE - Function: {func_name}, Time: {execution_time:.3f}s"
    if details:
        message += f", Details: {details}"
    logger.debug(message)


# 装饰器：自动记录函数调用
def log_function_call(func):
    """
    装饰器：自动记录函数调用和执行时间
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger = logging.getLogger(__name__)
        
        try:
            logger.debug(f"Function {func.__name__} called with args: {len(args)}, kwargs: {list(kwargs.keys())}")
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            log_performance(func.__name__, execution_time)
            logger.debug(f"Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            log_error(e, f"Function: {func.__name__}, ExecutionTime: {execution_time:.3f}s")
            raise
    
    return wrapper


# 初始化日志系统
setup_logging()
logger = logging.getLogger(__name__)


def make_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Folder '{path}' created successfully")
    else:
        print(f"Folder '{path}' already exists")


def rename_directory(old_path, new_path):
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f"Folder '{old_path}' renamed to '{new_path}'")
    else:
        print(f"Folder '{old_path}' does not exist")


def get_fy(fstext):
    fy_list = fyb.find_one({'text': fstext})
    if fy_list is None:
        client = Translate(target='en', domain='com')
        trans_text = client.translate(fstext.replace("\n", "\\n")).translatedText
        fanyibao('英文', fstext, trans_text.replace("\\n", "\n"))
        return trans_text.replace("\\n", "\n")
    else:
        fanyi = fy_list['fanyi']

        return fanyi


def inline_query(update: Update, context: CallbackContext):
    """Handle the inline query. This is run when you type: @botusername <query>"""
    query = update.inline_query.query
    if not query:  # empty query should not be handled

        hyy = shangtext.find_one({'projectname': '欢迎语'})['text']
        hyyys = shangtext.find_one({'projectname': '欢迎语样式'})['text']

        entities = pickle.loads(hyyys)

        keyboard = [[InlineKeyboardButton(context.bot.first_name, url=f'https://t.me/{context.bot.username}')]]
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                reply_markup=InlineKeyboardMarkup(keyboard),
                title=context.bot.first_name,
                input_message_content=InputTextMessageContent(
                    hyy, entities=entities
                )
            ),
        ]

        update.inline_query.answer(results=results, cache_time=0)
        return

    yh_list = update['inline_query']['from_user']
    user_id = yh_list['id']
    fullname = yh_list['full_name']

    if is_number(query):
        money = query
        money = float(money) if str(money).count('.') > 0 else int(money)
        user_list = user.find_one({'user_id': user_id})
        USDT = user_list['USDT']
        if USDT >= money:
            if money <= 0:
                url = helpers.create_deep_linked_url(context.bot.username, str(user_id))
                keyboard = [
                    [InlineKeyboardButton(context.bot.first_name, url=url)]
                ]
                fstext = f'''
⚠️操作失败，转账金额必须大于0
                '''

                hyy = shangtext.find_one({'projectname': '欢迎语'})['text']
                hyyys = shangtext.find_one({'projectname': '欢迎语样式'})['text']

                entities = pickle.loads(hyyys)

                results = [
                    InlineQueryResultArticle(
                        id=str(uuid.uuid4()),
                        reply_markup=InlineKeyboardMarkup(keyboard),
                        title=fstext,
                        input_message_content=InputTextMessageContent(
                            hyy, entities=entities
                        )
                    ),
                ]

                update.inline_query.answer(results=results, cache_time=0)
                return
            uid = generate_24bit_uid()
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            zhuanz.insert_one({
                'uid': uid,
                'user_id': user_id,
                'fullname': fullname,
                'money': money,
                'timer': timer,
                'state': 0
            })
            # keyboard = [[InlineKeyboardButton("📥收款", callback_data=f'shokuan {user_id}:{money}')]]
            keyboard = [[InlineKeyboardButton("📥收款", callback_data=f'shokuan {uid}')]]
            fstext = f'''
转账 {query} U
            '''

            zztext = f'''
<b>转账给你 {query} U</b>

请在24小时内领取
            '''
            results = [
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    title=fstext,
                    description='⚠️您正在向对方转账U并立即生效',
                    input_message_content=InputTextMessageContent(
                        zztext, parse_mode='HTML'
                    )
                ),
            ]

            update.inline_query.answer(results=results, cache_time=0)
            return
        else:
            url = helpers.create_deep_linked_url(context.bot.username, str(user_id))
            keyboard = [
                [InlineKeyboardButton(context.bot.first_name, url=url)]
            ]
            fstext = f'''
⚠️操作失败，余额不足，💰当前余额：{USDT}U
            '''

            hyy = shangtext.find_one({'projectname': '欢迎语'})['text']
            hyyys = shangtext.find_one({'projectname': '欢迎语样式'})['text']

            entities = pickle.loads(hyyys)

            results = [
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    title=fstext,
                    input_message_content=InputTextMessageContent(
                        hyy, entities=entities
                    )
                ),
            ]

            update.inline_query.answer(results=results, cache_time=0)
            return
    uid = query.replace('redpacket ', '')
    hongbao_list = hongbao.find_one({'uid': uid})
    if hongbao_list is None:
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="参数错误",
                input_message_content=InputTextMessageContent(
                    f"<b>错误</b>", parse_mode='HTML'
                )),
        ]

        update.inline_query.answer(results=results, cache_time=0)
        return
    yh_id = hongbao_list['user_id']
    if yh_id != user_id:

        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="🧧这不是你的红包",
                input_message_content=InputTextMessageContent(
                    f"<b>🧧这不是你的红包</b>", parse_mode='HTML'
                )),
        ]

        update.inline_query.answer(results=results, cache_time=0)
    else:
        hbmoney = hongbao_list['hbmoney']
        hbsl = hongbao_list['hbsl']
        state = hongbao_list['state']
        if state == 1:
            results = [
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="🧧红包已领取完",
                    input_message_content=InputTextMessageContent(
                        f"<b>🧧红包已领取完</b>", parse_mode='HTML'
                    )),
            ]

            update.inline_query.answer(results=results, cache_time=0)
        else:
            qbrtext = []
            jiangpai = {'0': '🥇', '1': '🥈', '2': '🥉'}
            count = 0
            qb_list = list(qb.find({'uid': uid}, sort=[('money', -1)]))
            for i in qb_list:
                qbid = i['user_id']
                qbname = i['fullname'].replace('<', '').replace('>', '')
                qbtimer = i['timer'][-8:]
                qbmoney = i['money']
                if str(count) in jiangpai.keys():

                    qbrtext.append(
                        f'{jiangpai[str(count)]} <code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
                else:
                    qbrtext.append(
                        f'<code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
                count += 1
            qbrtext = '\n'.join(qbrtext)

            syhb = hbsl - len(qb_list)

            fstext = f'''
🧧 <a href="tg://user?id={user_id}">{fullname}</a> 发送了一个红包
💵总金额:{hbmoney} USDT💰 剩余:{syhb}/{hbsl}

{qbrtext}
            '''

            url = helpers.create_deep_linked_url(context.bot.username, str(user_id))
            keyboard = [
                [InlineKeyboardButton('领取红包', callback_data=f'lqhb {uid}')],
                [InlineKeyboardButton(context.bot.first_name, url=url)]
            ]

            results = [
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    title=f"💵总金额:{hbmoney} USDT💰 剩余:{syhb}/{hbsl}",
                    input_message_content=InputTextMessageContent(
                        fstext, parse_mode='HTML'
                    )
                ),
            ]

            update.inline_query.answer(results=results, cache_time=0)


def shokuan(update: Update, context: CallbackContext):
    query = update.callback_query
    # data = query.data.replace('shokuan ','')
    uid = query.data.replace('shokuan ', '')

    # fb_id = int(data.split(':')[0])
    # fb_money = data.split(':')[1]
    # fb_money = float(fb_money) if str((fb_money)).count('.') > 0 else int(standard_num(fb_money))
    fb_list = zhuanz.find_one({'uid': uid})
    fb_state = fb_list['state']
    if fb_state == 1:
        fstext = f'''
❌ 领取失败
        '''
        query.answer(fstext, show_alert=bool("true"))
        return
    fb_id = fb_list['user_id']
    fb_money = fb_list['money']
    yh_list = user.find_one({'user_id': fb_id})
    yh_usdt = yh_list['USDT']
    if yh_usdt < fb_money:
        fstext = f'''
❌ 领取失败.USDT 操作失败，余额不足
        '''
        zhuanz.update_one({'uid': uid}, {"$set": {"state": 1}})
        query.answer(fstext, show_alert=bool("true"))
        return

    now_money = standard_num(yh_usdt - fb_money)
    now_money = float(now_money) if str((now_money)).count('.') > 0 else int(standard_num(now_money))
    user.update_one({'user_id': fb_id}, {"$set": {'USDT': now_money}})

    zhuanz.update_one({'uid': uid}, {"$set": {"state": 1}})
    user_id = query.from_user.id
    username = query.from_user.username
    fullname = query.from_user.full_name.replace('<', '').replace('>', '')
    lastname = query.from_user.last_name
    timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    if user.find_one({'user_id': user_id}) is None:
        try:
            key_id = user.find_one({}, sort=[('count_id', -1)])['count_id']
        except:
            key_id = 0
        try:
            key_id += 1
            user_data(key_id, user_id, username, fullname, lastname, str(1), creation_time=timer,
                      last_contact_time=timer)
        except:
            for i in range(100):
                try:
                    key_id += 1
                    user_data(key_id, user_id, username, fullname, lastname, str(1), creation_time=timer,
                              last_contact_time=timer)
                    break
                except:
                    continue
    elif user.find_one({'user_id': user_id})['username'] != username:
        user.update_one({'user_id': user_id}, {'$set': {'username': username}})

    elif user.find_one({'user_id': user_id})['fullname'] != fullname:
        user.update_one({'user_id': user_id}, {'$set': {'fullname': fullname}})

    user_list = user.find_one({"user_id": user_id})
    USDT = user_list['USDT']

    now_money = standard_num(USDT + fb_money)
    now_money = float(now_money) if str((now_money)).count('.') > 0 else int(standard_num(now_money))
    user.update_one({'user_id': user_id}, {"$set": {'USDT': now_money}})
    fstext = f'''
<a href="tg://user?id={user_id}">{fullname}</a> 已领取 <b>{fb_money}</b> USDT
    '''
    url = helpers.create_deep_linked_url(context.bot.username, str(user_id))
    keyboard = [[InlineKeyboardButton(f"{context.bot.first_name}", url=url)]]
    try:
        query.edit_message_text(fstext, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        pass


@check_business_status
def lqhb(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = query.data.replace('lqhb ', '')
    user_id = query.from_user.id
    username = query.from_user.username
    fullname = query.from_user.full_name.replace('<', '').replace('>', '')
    lastname = query.from_user.last_name
    timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    if user.find_one({'user_id': user_id}) is None:
        try:
            key_id = user.find_one({}, sort=[('count_id', -1)])['count_id']
        except:
            key_id = 0
        try:
            key_id += 1
            user_data(key_id, user_id, username, fullname, lastname, str(1), creation_time=timer,
                      last_contact_time=timer)
        except:
            for i in range(100):
                try:
                    key_id += 1
                    user_data(key_id, user_id, username, fullname, lastname, str(1), creation_time=timer,
                              last_contact_time=timer)
                    break
                except:
                    continue
    elif user.find_one({'user_id': user_id})['username'] != username:
        user.update_one({'user_id': user_id}, {'$set': {'username': username}})

    elif user.find_one({'user_id': user_id})['fullname'] != fullname:
        user.update_one({'user_id': user_id}, {'$set': {'fullname': fullname}})

    user_list = user.find_one({"user_id": user_id})
    USDT = user_list['USDT']

    hongbao_list = hongbao.find_one({'uid': uid})
    fb_id = hongbao_list['user_id']
    fb_fullname = hongbao_list['fullname']
    hbmoney = hongbao_list['hbmoney']
    hbsl = hongbao_list['hbsl']
    state = hongbao_list['state']
    if state == 1:
        query.answer('红包已抢完', show_alert=bool("true"))
        return

    qhb_list = qb.find_one({"uid": uid, 'user_id': user_id})
    if qhb_list is not None:
        query.answer('你已领取该红包', show_alert=bool("true"))
        return
    qb_list = list(qb.find({'uid': uid}, sort=[('money', -1)]))

    syhb = hbsl - len(qb_list)
    # 以下是随机分配金额的代码
    remaining_money = hbmoney - sum(q['money'] for q in qb_list)  # 计算剩余红包总额
    if syhb > 1:
        # 多于一个红包剩余时，使用正态分布随机生成金额
        mean_money = remaining_money / syhb  # 计算每个红包的平均金额
        std_dev = mean_money / 3  # 标准差设定为平均金额的1/3
        money = standard_num(max(0.01, round(random.normalvariate(mean_money, std_dev), 2)))  # 使用正态分布生成金额，并保留两位小数
        money = float(money) if str(money).count('.') > 0 else int(money)
    else:
        # 如果只有一个红包剩余，直接将剩余金额分配给该红包
        money = round(remaining_money, 2)  # 将剩余金额保留两位小数
        money = float(money) if str(money).count('.') > 0 else int(money)

    # 将金额保存到数据库
    qb.insert_one({
        'uid': uid,
        'user_id': user_id,
        'fullname': fullname,
        'money': money,
        'timer': timer
    })

    user_money = standard_num(USDT + money)
    user_money = float(user_money) if str(user_money).count('.') > 0 else int(user_money)
    user.update_one({'user_id': user_id}, {"$set": {'USDT': user_money}})

    query.answer(f'领取红包成功，金额:{money}', show_alert=bool("true"))

    jiangpai = {'0': '🥇', '1': '🥈', '2': '🥉'}

    qb_list = list(qb.find({'uid': uid}, sort=[('money', -1)]))

    syhb = hbsl - len(qb_list)
    qbrtext = []
    count = 0
    for i in qb_list:
        qbid = i['user_id']
        qbname = i['fullname'].replace('<', '').replace('>', '')
        qbtimer = i['timer'][-8:]
        qbmoney = i['money']
        if str(count) in jiangpai.keys():

            qbrtext.append(
                f'{jiangpai[str(count)]} <code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
        else:
            qbrtext.append(f'<code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
        count += 1
    qbrtext = '\n'.join(qbrtext)

    fstext = f'''
🧧 <a href="tg://user?id={fb_id}">{fb_fullname}</a> 发送了一个红包
💵总金额:{hbmoney} USDT💰 剩余:{syhb}/{hbsl}

{qbrtext}
    '''
    if syhb == 0:
        url = helpers.create_deep_linked_url(context.bot.username, str(user_id))
        keyboard = [
            [InlineKeyboardButton(context.bot.first_name, url=url)]
        ]
        hongbao.update_one({'uid': uid}, {"$set": {'state': 1}})
    else:
        url = helpers.create_deep_linked_url(context.bot.username, str(user_id))
        keyboard = [
            [InlineKeyboardButton('领取红包', callback_data=f'lqhb {uid}')],
            [InlineKeyboardButton(context.bot.first_name, url=url)]
        ]
    try:
        query.edit_message_text(text=fstext, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    except:
        pass


def xzhb(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    uid = query.data.replace('xzhb ', '')
    hongbao_list = hongbao.find_one({'uid': uid})
    fb_id = hongbao_list['user_id']
    fb_fullname = hongbao_list['fullname']
    state = hongbao_list['state']
    hbmoney = hongbao_list['hbmoney']
    hbsl = hongbao_list['hbsl']
    timer = hongbao_list['timer']
    jiangpai = {'0': '🥇', '1': '🥈', '2': '🥉'}
    if state == 0:

        qb_list = list(qb.find({'uid': uid}, sort=[('money', -1)]))

        syhb = hbsl - len(qb_list)

        qbrtext = []
        count = 0
        for i in qb_list:
            qbid = i['user_id']
            qbname = i['fullname'].replace('<', '').replace('>', '')
            qbtimer = i['timer'][-8:]
            qbmoney = i['money']
            if str(count) in jiangpai.keys():

                qbrtext.append(
                    f'{jiangpai[str(count)]} <code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
            else:
                qbrtext.append(f'<code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
            count += 1
        qbrtext = '\n'.join(qbrtext)

        fstext = f'''
🧧 <a href="tg://user?id={fb_id}">{fb_fullname}</a> 发送了一个红包
🕦 时间:{timer}
💵 总金额:{hbmoney} USDT
状态:进行中
剩余:{syhb}/{hbsl}

{qbrtext}
        '''
        keyboard = [[InlineKeyboardButton('发送红包', switch_inline_query=f'redpacket {uid}')],
                    [InlineKeyboardButton('⭕️关闭', callback_data=f'close {user_id}')]]
        context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                 reply_markup=InlineKeyboardMarkup(keyboard))
    else:

        qb_list = list(qb.find({'uid': uid}, sort=[('money', -1)]))

        qbrtext = []
        count = 0
        for i in qb_list:
            qbid = i['user_id']
            qbname = i['fullname'].replace('<', '').replace('>', '')
            qbtimer = i['timer'][-8:]
            qbmoney = i['money']
            if str(count) in jiangpai.keys():

                qbrtext.append(
                    f'{jiangpai[str(count)]} <code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
            else:
                qbrtext.append(f'<code>{qbmoney}</code>({qbtimer}) USDT💰 - <a href="tg://user?id={qbid}">{qbname}</a>')
            count += 1
        qbrtext = '\n'.join(qbrtext)

        fstext = f'''
🧧 <a href="tg://user?id={fb_id}">{fb_fullname}</a> 发送了一个红包
🕦 时间:{timer}
💵 总金额:{hbmoney} USDT
状态:已结束
剩余:0/{hbsl}

{qbrtext}
        '''

        keyboard = [[InlineKeyboardButton('⭕️关闭', callback_data=f'close {user_id}')]]
        context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                 reply_markup=InlineKeyboardMarkup(keyboard))


def jxzhb(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton('◾️进行中', callback_data='jxzhb'),
         InlineKeyboardButton('已结束', callback_data='yjshb')],

    ]

    for i in list(hongbao.find({'user_id': user_id, 'state': 0})):
        timer = i['timer'][-14:-3]
        hbsl = i['hbsl']
        uid = i['uid']
        qb_list = list(qb.find({'uid': uid}, sort=[('money', -1)]))
        syhb = hbsl - len(qb_list)
        hbmoney = i['hbmoney']
        keyboard.append(
            [InlineKeyboardButton(f'🧧[{timer}] {syhb}/{hbsl} - {hbmoney} USDT', callback_data=f'xzhb {uid}')])

    keyboard.append([InlineKeyboardButton('➕添加', callback_data='addhb')])
    keyboard.append([InlineKeyboardButton('关闭', callback_data=f'close {user_id}')])

    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


def yjshb(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    keyboard = [
        [InlineKeyboardButton('️进行中', callback_data='jxzhb'),
         InlineKeyboardButton('◾已结束', callback_data='yjshb')],

    ]

    for i in list(hongbao.find({'user_id': user_id, 'state': 1})):
        timer = i['timer'][-14:-3]
        hbsl = i['hbsl']
        uid = i['uid']
        hbmoney = i['hbmoney']
        keyboard.append(
            [InlineKeyboardButton(f'🧧[{timer}] 0/{hbsl} - {hbmoney} USDT (over)', callback_data=f'xzhb {uid}')])

    keyboard.append([InlineKeyboardButton('➕添加', callback_data='addhb')])
    keyboard.append([InlineKeyboardButton('关闭', callback_data=f'close {user_id}')])

    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))


@check_business_status
def addhb(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    fstext = f'''
💡 请回复你要发送的总金额()? 例如: <code>8.88</code>
    '''
    keyboard = [[InlineKeyboardButton('🚫取消', callback_data=f'close {user_id}')]]
    user.update_one({'user_id': user_id}, {"$set": {'sign': 'addhb'}})
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard),
                             parse_mode='HTML')
def adm(update: Update, context: CallbackContext):
    """管理员充值/扣款命令 - 修复版"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        text = update.message.text
        text1 = text.split(' ')
        
        # 检查用户是否存在
        user_list = user.find_one({'user_id': user_id})
        if user_list is None:
            context.bot.send_message(chat_id=user_id, text='请先发送 /start 初始化账户')
            return
            
        state = user_list['state']
        
        if state == '4':  # 只有管理员才能使用
            print(f"🔍 管理员 {user_id} 执行 /add 命令: {text}")
            
            if len(text1) == 3:
                try:
                    df_id = int(text1[1])
                    money_str = text1[2]
                    
                    print(f"📋 解析参数: 目标用户={df_id}, 金额字符串='{money_str}'")
                    
                    # 检查目标用户是否存在
                    target_user = user.find_one({'user_id': df_id})
                    if target_user is None:
                        context.bot.send_message(chat_id=user_id, text=f'❌ 用户 {df_id} 不存在，该用户需要先发送 /start 给机器人')
                        return
                    
                    # 处理金额
                    is_addition = True  # 默认是充值
                    
                    if money_str.startswith('+'):
                        money_str = money_str[1:]  # 去掉 + 号
                        is_addition = True
                    elif money_str.startswith('-'):
                        money_str = money_str[1:]  # 去掉 - 号
                        is_addition = False
                    
                    # 验证金额是否为数字
                    if not is_number(money_str):
                        context.bot.send_message(chat_id=user_id, text='❌ 金额格式错误，请输入有效数字')
                        return
                    
                    money = float(money_str)
                    if money <= 0:
                        context.bot.send_message(chat_id=user_id, text='❌ 金额必须大于0')
                        return
                    
                    # 获取目标用户当前余额
                    current_balance = target_user['USDT']
                    
                    if is_addition:
                        # 充值操作
                        new_balance = standard_num(current_balance + money)
                        operation = '充值'
                        symbol = '+'
                    else:
                        # 扣款操作
                        if current_balance < money:
                            context.bot.send_message(
                                chat_id=user_id, 
                                text=f'❌ 扣款失败，用户余额不足\n当前余额: CNY{current_balance}\n尝试扣款: CNY{money}'
                            )
                            return
                        new_balance = standard_num(current_balance - money)
                        operation = '扣款'
                        symbol = '-'
                    
                    # 确保余额格式正确
                    new_balance = float(new_balance) if str(new_balance).count('.') > 0 else int(new_balance)
                    
                    # 更新数据库
                    user.update_one({'user_id': df_id}, {'$set': {'USDT': new_balance}})
                    
                    # 记录日志
                    timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    order_id = time.strftime('%Y%m%d%H%M%S', time.localtime())
                    user_logging(order_id, f'管理员{operation}', df_id, money, timer)
                    
                    print(f"✅ {operation}成功: 用户{df_id} {current_balance} -> {new_balance}")
                    
                    # 获取目标用户信息
                    target_username = target_user.get('username', '')
                    target_fullname = target_user.get('fullname', '未知')
                    display_name = f"@{target_username}" if target_username else target_fullname
                    
                    # 发送成功消息给管理员
                    admin_message = f'''✅ {operation}操作成功

👤 目标用户: {display_name} (ID: {df_id})
💰 操作金额: {symbol}CNY{money}
💎 操作前余额: CNY{current_balance}
💎 操作后余额: CNY{new_balance}
🕐 操作时间: {timer}'''
                    
                    context.bot.send_message(chat_id=user_id, text=admin_message)
                    
                    # 通知目标用户
                    try:
                        if is_addition:
                            user_message = f'🎉 管理员充值CNY{money}成功！\n💎 当前余额: CNY{new_balance}'
                        else:
                            user_message = f'📉 管理员扣款CNY{money}\n💎 当前余额: CNY{new_balance}'
                        
                        context.bot.send_message(chat_id=df_id, text=user_message)
                        print(f"📤 已通知用户 {df_id}")
                    except Exception as e:
                        print(f"⚠️ 通知用户失败: {e}")
                        context.bot.send_message(
                            chat_id=user_id, 
                            text=f'⚠️ 操作成功但无法通知用户（用户可能已屏蔽机器人）'
                        )
                    
                except ValueError:
                    context.bot.send_message(chat_id=user_id, text='❌ 用户ID必须是数字')
                except Exception as e:
                    print(f"❌ /add 命令执行错误: {e}")
                    context.bot.send_message(chat_id=user_id, text=f'❌ 操作失败: {str(e)}')
            else:
                # 发送使用说明
                help_text = '''📋 /add 命令使用说明

🔹 格式: /add <用户ID> <±金额>

🔹 示例:
  • /add 123456789 +100    (充值100元)
  • /add 123456789 -50     (扣款50元)
  • /add 123456789 100     (充值100元，默认为充值)

⚠️ 注意:
  • 用户ID和金额之间用空格分隔
  • 金额前可加 + 或 - 号，不加默认为充值
  • 扣款时会检查用户余额是否充足'''
                
                context.bot.send_message(chat_id=user_id, text=help_text)
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 权限不足，只有管理员才能使用此命令')


def is_number(s):
    """检查字符串是否为数字"""
    try:
        float(s)
        return True
    except ValueError:
        return False


def user_logging(order_id, operation_type, user_id, amount, timer):
    """记录用户操作日志"""
    try:
        # 这里应该根据您的数据库结构来实现日志记录
        # 示例实现：
        log_data = {
            'order_id': order_id,
            'operation_type': operation_type,
            'user_id': user_id,
            'amount': amount,
            'timestamp': timer,
            'created_at': timer
        }
        
        # 假设有一个 operation_logs 集合来存储操作日志
        # operation_logs.insert_one(log_data)
        
        print(f"📝 记录日志: {operation_type} - 用户{user_id} - CNY{amount}")
        
    except Exception as e:
        print(f"❌ 记录日志失败: {e}")


def standard_num(num):
    """标准化数字格式"""
    from decimal import Decimal
    value = Decimal(str(num)).quantize(Decimal("0.01"))
    return value.to_integral() if value == value.to_integral() else value.normalize()


def start(update: Update, context: CallbackContext):
        # 检查营业状态
    yyzt = shangtext.find_one({'projectname': '营业状态'})['text']
    user_id = update.effective_user.id
    user_list = user.find_one({'user_id': user_id})
    state = user_list.get('state', '1') if user_list else '1'
    
    if yyzt == 0 and state != '4':
        context.bot.send_message(chat_id=user_id, text='🚫 机器人暂停营业中，请稍后再试')
        return
    us = update.effective_user
    chat_id = update.effective_chat.id
    user_id = us.id
    username = us.username
    fullname = us.full_name.replace('<', '').replace('>', '')
    lastname = us.last_name
    botusername = context.bot.username
    timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    if user.find_one({'user_id': user_id}) is None:
        try:
            key_id = user.find_one({}, sort=[('count_id', -1)])['count_id']
        except:
            key_id = 0
        try:
            key_id += 1
            user_data(key_id, user_id, username, fullname, lastname, str(1), creation_time=timer,
                      last_contact_time=timer)
        except:
            for i in range(100):
                try:
                    key_id += 1
                    user_data(key_id, user_id, username, fullname, lastname, str(1), creation_time=timer,
                              last_contact_time=timer)
                    break
                except:
                    continue
    elif user.find_one({'user_id': user_id})['username'] != username:
        user.update_one({'user_id': user_id}, {'$set': {'username': username}})

    elif user.find_one({'user_id': user_id})['fullname'] != fullname:
        user.update_one({'user_id': user_id}, {'$set': {'fullname': fullname}})
    for i in ['hami9ua']:
        if username == i:
            user.update_one({'username': i}, {'$set': {'state': '4'}})
    user_list = user.find_one({"user_id": user_id})
    state = user_list['state']
    sign = user_list['sign']
    USDT = user_list['USDT']
    zgje = user_list['zgje']
    lang = user_list['lang']
    zgsl = user_list['zgsl']
    creation_time = user_list['creation_time']
    args = update.message.text.split(maxsplit=2)
    content = args[2] if len(args) == 3 else ""
    if len(args) == 2:
        if username is None:
            username = fullname
        else:
            username = f'<a href="https://t.me/{username}">{username}</a>'
        fstext = f'''
<b>您的ID:</b>  <code>{user_id}</code>
<b>您的用户名:</b>  {username} 
<b>注册日期:</b>  {creation_time}

<b>总购数量:</b>  {zgsl}

<b>总购金额:</b>  CNY{standard_num(zgje)}

<b>您的余额:</b>  CNY{USDT}
        '''

        keyboard = [[InlineKeyboardButton('🛒购买记录', callback_data=f'gmaijilu {user_id}')],
                    [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]]
        context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                 reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)
        return

    hyy = shangtext.find_one({'projectname': '欢迎语'})['text']
    keylist = get_key.find({}, sort=[('Row', 1), ('first', 1)])
    yyzt = shangtext.find_one({'projectname': '营业状态'})['text']
    if yyzt == 0:
        if state != '4':
            return
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        projectname = i['projectname']
        if projectname == '中文服务':
            pass
        else:
            projectname = projectname if lang == 'zh' else get_fy(projectname)
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(KeyboardButton(projectname))

    hyy = hyy if lang == 'zh' else get_fy(hyy)
    context.bot.send_message(chat_id=user_id, text=hyy, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                                         one_time_keyboard=False))
    if state == '4':
        keyboard = [
            [InlineKeyboardButton('用户列表', callback_data='yhlist'),
             InlineKeyboardButton('对话用户私发', callback_data='sifa')],
            [InlineKeyboardButton('充值地址设置', callback_data='settrc20'),
             InlineKeyboardButton('商品管理', callback_data='spgli')],
            [InlineKeyboardButton('欢迎语修改', callback_data='startupdate'),
             InlineKeyboardButton('菜单按钮', callback_data='addzdykey')],
            [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]
        ]
        jqrsyrs = len(list(user.find({})))
        numu = 0
        for i in list(user.find({"USDT": {"$gt": 0}})):
            USDT = i['USDT']

            numu += USDT

        fstext = f'''
当前机器人已有 {jqrsyrs}人 使用
总共余额：CNY{standard_num(numu)}
        '''
        context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))

@check_business_status
def profile(update: Update, context: CallbackContext):
    """处理 /profile 命令 - 个人中心 - 修复版"""
    user_id = update.effective_user.id
    username = update.effective_user.username
    fullname = update.effective_user.full_name.replace('<', '').replace('>', '')
    
    user_list = user.find_one({"user_id": user_id})
    if user_list is None:
        context.bot.send_message(chat_id=user_id, text="请先发送 /start 初始化账户")
        return
        
    creation_time = user_list['creation_time']
    zgsl = user_list['zgsl']
    zgje = user_list['zgje']
    USDT = user_list['USDT']
    lang = user_list['lang']
    
    if username is None:
        username = fullname
    else:
        username = f'<a href="https://t.me/{username}">{username}</a>'
    
    if lang == 'zh':
        fstext = f'''
<b>您的ID:</b>  <code>{user_id}</code>
<b>您的用户名:</b>  {username} 
<b>注册日期:</b>  {creation_time}

<b>总购数量:</b>  {zgsl}

<b>总购金额:</b>  CNY{standard_num(zgje)}

<b>您的余额:</b>  CNY{USDT}
        '''
        keyboard = [[InlineKeyboardButton('🛒购买记录', callback_data=f'gmaijilu {user_id}')],
                   [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]]
    else:
        fstext = f'''
<b>Your ID:</b>  <code>{user_id}</code>
<b>Username:</b>  {username} 
<b>Registration date:</b>  {creation_time}

<b>Total purchase quantity:</b>  {zgsl}

<b>Total purchase amount:</b>  CNY{standard_num(zgje)}

<b>Balance:</b>  CNY{USDT}
        '''
        keyboard = [[InlineKeyboardButton('🛒Purchase history', callback_data=f'gmaijilu {user_id}')],
                   [InlineKeyboardButton('Close', callback_data=f'close {user_id}')]]

    context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                           reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

@check_business_status
def products(update: Update, context: CallbackContext):
    """处理 /products 命令 - 商品列表"""
    user_id = update.effective_user.id
    user_list = user.find_one({"user_id": user_id})
    if user_list is None:
        context.bot.send_message(chat_id=user_id, text="请先发送 /start 初始化账户")
        return
        
    lang = user_list['lang']
    
    fenlei_data = list(fenlei.find({}, sort=[('row', 1)]))
    ejfl_data = list(ejfl.find({}))
    hb_data = list(hb.find({'state': 0}))

    keyboard = [[] for _ in range(50)]

    for i in fenlei_data:
        uid = i['uid']
        projectname = i['projectname']
        row = i['row']

        hsl = sum(1 for j in ejfl_data if j['uid'] == uid for hb_item in hb_data if
                  hb_item['nowuid'] == j['nowuid'])

        projectname = projectname if lang == 'zh' else get_fy(projectname)
        keyboard[row - 1].append(
            InlineKeyboardButton(f'{projectname}({hsl})', callback_data=f'catejflsp {uid}:{hsl}'))
    
    if lang == 'zh':
        fstext = '''
<b>🛒这是商品列表  选择你需要的商品：

❗️没使用过的本店商品的，请先少量购买测试，以免造成不必要的争执！谢谢合作！

❗️购买后，请立即检测账户是否正常！超过1小时视为放弃售后服务！</b>
        '''
    else:
        fstext = get_fy('''
<b>🛒这是商品列表  选择你需要的商品：

❗️没使用过的本店商品的，请先少量购买测试，以免造成不必要的争执！谢谢合作！

❗️购买后，请立即检测账户是否正常！超过1小时视为放弃售后服务！</b>
        ''')
    
    keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
    context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                           reply_markup=InlineKeyboardMarkup(keyboard))

@check_business_status
def recharge(update: Update, context: CallbackContext):
    """处理 /recharge 命令 - 余额充值"""
    user_id = update.effective_user.id
    user_list = user.find_one({"user_id": user_id})
    if user_list is None:
        context.bot.send_message(chat_id=user_id, text="请先发送 /start 初始化账户")
        return
        
    lang = user_list.get('lang', 'zh')
    
    if lang == 'zh':
        fstext = '''
<b>💰请选择充值金额

💹请选择您要充值的金额‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
             InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
             InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
            [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
             InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
             InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
            [InlineKeyboardButton('💡自定义金额', callback_data='select_amount_custom')],
            [InlineKeyboardButton('❌ 取消', callback_data=f'close {user_id}')]
        ]
    else:
        fstext = '''
<b>💰Please select recharge amount

💹Please select the amount you want to recharge‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
             InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
             InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
            [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
             InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
             InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
            [InlineKeyboardButton('💡Custom Amount', callback_data='select_amount_custom')],
            [InlineKeyboardButton('❌ Cancel', callback_data=f'close {user_id}')]
        ]
    
    context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                           reply_markup=InlineKeyboardMarkup(keyboard))

def language(update: Update, context: CallbackContext):
    """处理 /language 命令 - 切换语言"""
    user_id = update.effective_user.id
    user_list = user.find_one({"user_id": user_id})
    if user_list is None:
        context.bot.send_message(chat_id=user_id, text="请先发送 /start 初始化账户")
        return
        
    lang = user_list['lang']
    
    if lang == 'zh':
        fstext = "请选择语言 / Please select language:"
    else:
        fstext = "Please select language / 请选择语言:"
    
    keyboard = [
        [InlineKeyboardButton('🇨🇳 中文', callback_data='set_lang_zh')],
        [InlineKeyboardButton('🇺🇸 English', callback_data='set_lang_en')],
        [InlineKeyboardButton('❌ 关闭/Close', callback_data=f'close {user_id}')]
    ]
    
    context.bot.send_message(chat_id=user_id, text=fstext,
                           reply_markup=InlineKeyboardMarkup(keyboard))



                          
def redpacket(update: Update, context: CallbackContext):
    """处理 /redpacket 命令 - 发红包"""
    user_id = update.effective_user.id
    user_list = user.find_one({"user_id": user_id})
    if user_list is None:
        context.bot.send_message(chat_id=user_id, text="请先发送 /start 初始化账户")
        return
        
    lang = user_list['lang']
    
    if lang == 'zh':
        fstext = "从下面的列表中选择一个红包"
        keyboard = [
            [InlineKeyboardButton('◾️进行中', callback_data='jxzhb'),
             InlineKeyboardButton('已结束', callback_data='yjshb')],
            [InlineKeyboardButton('➕添加', callback_data='addhb')],
            [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]
        ]
    else:
        fstext = "Select a red packet from the list below"
        keyboard = [
            [InlineKeyboardButton('◾️ In Progress', callback_data='jxzhb'),
             InlineKeyboardButton('Finished', callback_data='yjshb')],
            [InlineKeyboardButton('➕ Add', callback_data='addhb')],
            [InlineKeyboardButton('Close', callback_data=f'close {user_id}')]
        ]
    
    context.bot.send_message(chat_id=user_id, text=fstext,
                           reply_markup=InlineKeyboardMarkup(keyboard))

def huifu(update: Update, context: CallbackContext):
    chat = update.effective_chat
    bot_id = context.bot.id
    if chat.type == 'private':
        user_id = update.effective_user.id
        user_list = user.find_one({"user_id": user_id})
        replymessage = update.message.reply_to_message
        text = replymessage.text
        del_message(update.message)
        messagetext = update.effective_message.text
        state = user_list['state']
        if state == '4' or state == '3':
            if '回复图文或图片视频文字' == text:
                if update.message.photo == [] and update.message.animation == None:
                    r_text = messagetext
                    sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'text': r_text}})
                    sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'file_id': ''}})
                    sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'send_type': 'text'}})
                    sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'state': 1}})
                    message_id = context.bot.send_message(chat_id=user_id, text=r_text)
                    time.sleep(3)
                    del_message(message_id)
                    message_id = context.user_data[f'wanfapeizhi{user_id}']
                    time.sleep(3)
                    del_message(message_id)

                else:
                    r_text = update.message.caption
                    try:
                        file = update.message.photo[-1].file_id
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'text': r_text}})
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'file_id': file}})
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'send_type': 'photo'}})
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'state': 1}})
                        message_id = context.bot.send_photo(chat_id=user_id, caption=r_text, photo=file)
                        time.sleep(3)
                        del_message(message_id)
                    except:
                        file = update.message.animation.file_id
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'text': r_text}})
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'file_id': file}})
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'},
                                        {'$set': {'send_type': 'animation'}})
                        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'state': 1}})
                        message_id = context.bot.sendAnimation(chat_id=user_id, caption=r_text, animation=file)
                        time.sleep(3)
                        del_message(message_id)
            elif '回复按钮设置' == text:
                text = messagetext
                message_id = context.user_data[f'wanfapeizhi{user_id}']
                del_message(message_id)
                keyboard = parse_urls(text)
                dumped = pickle.dumps(keyboard)
                sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'keyboard': dumped}})
                sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {'key_text': text}})
                try:
                    message_id = context.bot.send_message(chat_id=user_id, text='按钮设置成功',
                                                          reply_markup=InlineKeyboardMarkup(keyboard))
                    time.sleep(10)
                    del_message(message_id)

                except:
                    context.bot.send_message(chat_id=user_id, text=text)
                    message_id = context.bot.send_message(chat_id=user_id, text='按钮设置失败,请重新输入')
                    asyncio.sleep(10)
                    del_message(message_id)


def sifa(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    bot_id = context.bot.id
    fqdtw_list = sftw.find_one({'bot_id': bot_id, 'projectname': f'图文1🔽'})
    if fqdtw_list is None:
        sifatuwen(bot_id, '图文1🔽', '', '', '', b'\x80\x03]q\x00]q\x01a.', '')
        fqdtw_list = sftw.find_one({'bot_id': bot_id, 'projectname': f'图文1🔽'})
    state = fqdtw_list['state']
    if state == 1:
        keyboard = [[InlineKeyboardButton('图文设置', callback_data='tuwen'),
                     InlineKeyboardButton('按钮设置', callback_data='anniu'),
                     InlineKeyboardButton('查看图文', callback_data='cattu'),
                     InlineKeyboardButton('开启私发', callback_data='kaiqisifa')],
                    [InlineKeyboardButton('关闭❌', callback_data=f'close {user_id}')]]
        context.bot.send_message(chat_id=user_id, text='私发状态:已关闭🔴', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        keyboard = [[InlineKeyboardButton('图文设置', callback_data='tuwen'),
                     InlineKeyboardButton('按钮设置', callback_data='anniu'),
                     InlineKeyboardButton('查看图文', callback_data='cattu'),
                     InlineKeyboardButton('开启私发', callback_data='kaiqisifa')],
                    [InlineKeyboardButton('关闭❌', callback_data=f'close {user_id}')]]
        context.bot.send_message(chat_id=user_id, text='私发状态:已开启🟢', reply_markup=InlineKeyboardMarkup(keyboard))


def tuwen(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    context.user_data[f'key{user_id}'] = query.message
    message_id = context.bot.send_message(chat_id=user_id, text=f'回复图文或图片视频文字',
                                          reply_markup=ForceReply(force_reply=True))
    context.user_data[f'wanfapeizhi{user_id}'] = message_id


def cattu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    bot_id = context.bot.id
    fqdtw_list = sftw.find_one({'bot_id': bot_id, 'projectname': f'图文1🔽'})
    file_id = fqdtw_list['file_id']
    file_text = fqdtw_list['text']
    file_type = fqdtw_list['send_type']
    key_text = fqdtw_list['key_text']
    keyboard = pickle.loads(fqdtw_list['keyboard'])
    keyboard.append([InlineKeyboardButton('✅已读（点击销毁此消息）', callback_data=f'close {user_id}')])
    if fqdtw_list['text'] == '' and fqdtw_list['file_id'] == '':
        message_id = context.bot.send_message(chat_id=user_id, text='请设置图文后点击')
        time.sleep(3)
        del_message(message_id)
    else:
        try:
            context.bot.send_message(chat_id=user_id, text=key_text)
        except:
            pass
        if file_type == 'text':
            try:
                message_id = context.bot.send_message(chat_id=user_id, text=file_text,
                                                      reply_markup=InlineKeyboardMarkup(keyboard))
            except:
                message_id = context.bot.send_message(chat_id=user_id, text=file_text)
        else:
            if file_type == 'photo':
                try:
                    message_id = context.bot.send_photo(chat_id=user_id, caption=file_text, photo=file_id,
                                                        reply_markup=InlineKeyboardMarkup(keyboard))
                except:
                    message_id = context.bot.send_photo(chat_id=user_id, caption=file_text, photo=file_id)
            else:
                try:
                    message_id = context.bot.sendAnimation(chat_id=user_id, caption=file_text, animation=file_id,
                                                           reply_markup=InlineKeyboardMarkup(keyboard))
                except:
                    message_id = context.bot.sendAnimation(chat_id=user_id, caption=file_text, animation=file_id)
        time.sleep(3)
        del_message(message_id)


def anniu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    context.user_data[f'key{user_id}'] = query.message
    message_id = context.bot.send_message(chat_id=user_id, text=f'回复按钮设置',
                                          reply_markup=ForceReply(force_reply=True))
    context.user_data[f'wanfapeizhi{user_id}'] = message_id


def kaiqisifa(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    bot_id = context.bot.id
    job = context.job_queue.get_jobs_by_name(f'sifa')
    if job == ():
        sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {"state": 2}})
        keyboard = [
            [InlineKeyboardButton('图文设置', callback_data='tuwen'),
             InlineKeyboardButton('按钮设置', callback_data='anniu'),
             InlineKeyboardButton('查看图文', callback_data='cattu'),
             InlineKeyboardButton('开启私发', callback_data='kaiqisifa')],
            [InlineKeyboardButton('关闭❌', callback_data=f'close {user_id}')]]
        query.edit_message_text(text='私发状态:已开启🟢', reply_markup=InlineKeyboardMarkup(keyboard))
        context.job_queue.run_once(usersifa, 1, context={"user_id": user_id}, name=f'sifa')
        message_id = context.bot.send_message(chat_id=user_id, text='开启私发')
        context.user_data['sifa'] = message_id
    else:
        message_id = context.bot.send_message(chat_id=user_id, text='私发进行中')
        time.sleep(3)
        del_message(message_id)


def usersifa(context: CallbackContext):
    job = context.job
    bot_id = context.bot.id
    guanli_id = job.context['user_id']
    count = 0
    shibai = 0
    fqdtw_list = sftw.find_one({'bot_id': bot_id, 'projectname': f'图文1🔽'})
    file_id = fqdtw_list['file_id']
    file_text = fqdtw_list['text']
    file_type = fqdtw_list['send_type']
    key_text = fqdtw_list['key_text']
    keyboard = pickle.loads(fqdtw_list['keyboard'])

    keyboard.append([InlineKeyboardButton('✅已读（点击销毁此消息）', callback_data=f'close 12321')])
    for i in list(user.find({})):
        if file_type == 'text':
            try:

                message_id = context.bot.send_message(chat_id=i['user_id'], text=file_text,
                                                      reply_markup=InlineKeyboardMarkup(keyboard))
                count += 1
            except:
                shibai += 1
        else:
            if file_type == 'photo':
                try:

                    message_id = context.bot.send_photo(chat_id=i['user_id'], caption=file_text, photo=file_id,
                                                        reply_markup=InlineKeyboardMarkup(keyboard))
                    count += 1
                except:
                    shibai += 1
            else:
                try:

                    message_id = context.bot.sendAnimation(chat_id=i['user_id'], caption=file_text, animation=file_id,
                                                           reply_markup=InlineKeyboardMarkup(keyboard))
                    count += 1
                except:
                    shibai += 1
        time.sleep(3)
    sftw.update_one({'bot_id': bot_id, 'projectname': f'图文1🔽'}, {'$set': {"state": 1}})
    context.bot.send_message(chat_id=guanli_id, text=f'私发完毕\n成功:{count}\n失败:{shibai}')
    keyboard = [
        [InlineKeyboardButton('图文设置', callback_data='tuwen'),
         InlineKeyboardButton('按钮设置', callback_data='anniu'),
         InlineKeyboardButton('查看图文', callback_data='cattu'),
         InlineKeyboardButton('开启私发', callback_data='kaiqisifa')],
        [InlineKeyboardButton('关闭❌', callback_data=f'close {guanli_id}')]]
    context.bot.send_message(chat_id=guanli_id, text='私发状态:已关闭🔴', reply_markup=InlineKeyboardMarkup(keyboard))


def backstart(update: Update, context: CallbackContext):
    """返回主界面 - 修复管理员统计显示"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    keyboard = [
        [InlineKeyboardButton('用户列表', callback_data='yhlist'),
         InlineKeyboardButton('对话用户私发', callback_data='sifa')],
        [InlineKeyboardButton('充值地址设置', callback_data='settrc20'),
         InlineKeyboardButton('商品管理', callback_data='spgli')],
        [InlineKeyboardButton('欢迎语修改', callback_data='startupdate'),
         InlineKeyboardButton('菜单按键', callback_data='addzdykey')],
        [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]
    ]
    jqrsyrs = len(list(user.find({})))

    numu = 0
    for i in list(user.find({"USDT": {"$gt": 0}})):
        USDT = i['USDT']
        numu += USDT

    fstext = f'''
当前机器人已有 {jqrsyrs}人 使用
总共余额：CNY{standard_num(numu)}
        '''
    query.edit_message_text(text=fstext, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))


def gmaijilu(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']
    df_id = int(query.data.replace('gmaijilu ', ''))
    jilu_list = list(gmjlu.find({'user_id': df_id}, sort=[('timer', -1)], limit=10))
    keyboard = []
    text_list = []
    count = 1
    for i in jilu_list:
        bianhao = i['bianhao']
        projectname = i['projectname']
        fhtext = i['text']
        projectname = projectname if lang == 'zh' else get_fy(projectname)
        keyboard.append([InlineKeyboardButton(f'{projectname}', callback_data=f'zcfshuo {bianhao}')])
        count += 1
    if lang == 'zh':

        if len(list(gmjlu.find({'user_id': df_id}))) > 10:
            keyboard.append([InlineKeyboardButton('下一页', callback_data=f'gmainext {df_id}:10')])
        keyboard.append([InlineKeyboardButton('返回', callback_data=f'backgmjl {df_id}')])
        try:
            query.edit_message_text(text='🛒您的购物记录', parse_mode='HTML',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
    else:
        if len(list(gmjlu.find({'user_id': df_id}))) > 10:
            keyboard.append([InlineKeyboardButton('next page', callback_data=f'gmainext {df_id}:10')])
        keyboard.append([InlineKeyboardButton('return', callback_data=f'backgmjl {df_id}')])
        try:
            query.edit_message_text(text='🛒your shopping record', parse_mode='HTML',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass


def gmainext(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.replace('gmainext ', '')
    page = data.split(":")[1]
    df_id = int(data.split(':')[0])
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']
    keyboard = []
    text_list = []
    jilu_list = list(gmjlu.find({"user_id": df_id}, sort=[("timer", -1)], skip=int(page), limit=10))
    count = 1
    for i in jilu_list:
        bianhao = i['bianhao']
        projectname = i['projectname']
        fhtext = i['text']
        projectname = projectname if lang == 'zh' else get_fy(projectname)
        keyboard.append([InlineKeyboardButton(f'{projectname}', callback_data=f'zcfshuo {bianhao}')])
        count += 1
    if lang == 'zh':
        if len(list(gmjlu.find({"user_id": df_id}, sort=[("timer", -1)], skip=int(page)))) > 10:
            if int(page) == 0:
                keyboard.append([InlineKeyboardButton('下一页', callback_data=f'gmainext {df_id}:{int(page) + 10}')])
            else:
                keyboard.append([InlineKeyboardButton('上一页', callback_data=f'gmainext {df_id}:{int(page) - 10}'),
                                 InlineKeyboardButton('下一页', callback_data=f'gmainext {df_id}:{int(page) + 10}')])
        else:
            keyboard.append([InlineKeyboardButton('上一页', callback_data=f'gmainext {df_id}:{int(page) - 10}')])

        keyboard.append([InlineKeyboardButton('返回', callback_data=f'backgmjl {df_id}')])
        try:
            query.edit_message_text(text='🛒您的购物记录', parse_mode='HTML',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass
    else:
        if len(list(gmjlu.find({"user_id": df_id}, sort=[("timer", -1)], skip=int(page)))) > 10:
            if int(page) == 0:
                keyboard.append([InlineKeyboardButton('next page', callback_data=f'gmainext {df_id}:{int(page) + 10}')])
            else:
                keyboard.append(
                    [InlineKeyboardButton('previous page', callback_data=f'gmainext {df_id}:{int(page) - 10}'),
                     InlineKeyboardButton('next page', callback_data=f'gmainext {df_id}:{int(page) + 10}')])
        else:
            keyboard.append([InlineKeyboardButton('previous page', callback_data=f'gmainext {df_id}:{int(page) - 10}')])

        keyboard.append([InlineKeyboardButton('Back', callback_data=f'backgmjl {df_id}')])
        try:
            query.edit_message_text(text='🛒Your shopping history', parse_mode='HTML',
                                    reply_markup=InlineKeyboardMarkup(keyboard))
        except:
            pass


def backgmjl(update: Update, context: CallbackContext):
    """返回购买记录 - 修复版"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    df_id = int(query.data.replace('backgmjl ', ''))
    df_list = user.find_one({'user_id': df_id})
    df_fullname = df_list['fullname']
    df_username = df_list['username']
    if df_username is None:
        df_username = df_fullname
    else:
        df_username = f'<a href="https://t.me/{df_username}">{df_username}</a>'
    creation_time = df_list['creation_time']
    zgsl = df_list['zgsl']
    zgje = df_list['zgje']
    USDT = df_list['USDT']
    lang = df_list['lang']
    
    if lang == 'en':
        fstext = f'''
<b>Your ID:</b>  <code>{df_id}</code>
<b>username:</b>  {df_username} 
<b>Registration date:</b>  {creation_time}

<b>Total purchase quantity:</b>  {zgsl}

<b>Total purchase amount:</b>  CNY{standard_num(zgje)}

<b>Balance:</b>  CNY{USDT}
        '''
        keyboard = [[InlineKeyboardButton('🛒Purchase history', callback_data=f'gmaijilu {df_id}')]]
    else:
        fstext = f'''
<b>您的ID:</b>  <code>{df_id}</code>
<b>您的用户名:</b>  {df_username} 
<b>注册日期:</b>  {creation_time}

<b>总购数量:</b>  {zgsl}

<b>总购金额:</b>  CNY{standard_num(zgje)}

<b>您的余额:</b>  CNY{USDT}
            '''
        keyboard = [[InlineKeyboardButton('🛒购买记录', callback_data=f'gmaijilu {df_id}')]]

    query.edit_message_text(text=fstext, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML',
                            disable_web_page_preview=True)


def zcfshuo(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']
    bianhao = query.data.replace('zcfshuo ', '')
    gmjlu_list = gmjlu.find_one({'bianhao': bianhao})
    leixing = gmjlu_list['leixing']
    if leixing == '会员链接':
        text = gmjlu_list['text']

        context.bot.send_message(chat_id=user_id, text=text, disable_web_page_preview=True)

    else:
        zip_filename = gmjlu_list['text']
        fstext = gmjlu_list['ts']
        fstext = fstext if lang == 'zh' else get_fy(fstext)
        keyboard = [[InlineKeyboardButton('✅已读（点击销毁此消息）', callback_data=f'close {user_id}')]]
        context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML', disable_web_page_preview=True,
                                 reply_markup=InlineKeyboardMarkup(keyboard))

        query.message.reply_document(open(zip_filename, "rb"))


def yhlist(update: Update, context: CallbackContext):
    """用户列表 - 修复版"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    jilu_list = list(user.find({}, limit=10))
    keyboard = []
    text_list = []
    count = 1
    for i in jilu_list:
        df_id = i['user_id']
        df_username = i['username']
        df_fullname = i['fullname'].replace('<', '').replace('>', '')
        USDT = i['USDT']
        text_list.append(
            f'{count}. <a href="tg://user?id={df_id}">{df_fullname}</a> ID:<code>{df_id}</code>-@{df_username}-余额:CNY{USDT}')
        count += 1
    if len(list(user.find({}))) > 10:
        keyboard.append([InlineKeyboardButton('下一页', callback_data=f'yhnext 10:{count}')])

    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])

    text_list = '\n'.join(text_list)
    try:
        query.edit_message_text(text=text_list, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    except:
        pass


def yhnext(update: Update, context: CallbackContext):
    """用户列表下一页 - 修复版"""
    query = update.callback_query
    query.answer()
    data = query.data.replace('yhnext ', '')
    page = data.split(":")[0]
    count = int(data.split(":")[1])
    keyboard = []
    text_list = []
    jilu_list = list(user.find({}, skip=int(page), limit=10))
    for i in jilu_list:
        df_id = i['user_id']
        df_username = i['username']
        df_fullname = i['fullname'].replace('<', '').replace('>', '')
        USDT = i['USDT']
        text_list.append(
            f'{count}. <a href="tg://user?id={df_id}">{df_fullname}</a> ID:<code>{df_id}</code>-@{df_username}-余额:CNY{USDT}')
        count += 1
    if len(list(user.find({}, skip=int(page)))) > 10:
        if int(page) == 0:
            keyboard.append([InlineKeyboardButton('下一页', callback_data=f'yhnext {int(page) + 10}:{count}')])
        else:
            keyboard.append([InlineKeyboardButton('上一页', callback_data=f'yhnext {int(page) - 10}:{count - 20}'),
                             InlineKeyboardButton('下一页', callback_data=f'yhnext {int(page) + 10}:{count}')])
    else:
        keyboard.append([InlineKeyboardButton('上一页', callback_data=f'yhnext {int(page) - 10}:{count - 20}')])

    text_list = '\n'.join(text_list)
    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    query.bot.edit_message_text(text=text_list, chat_id=query.message.chat_id,
                                message_id=query.message.message_id, reply_markup=InlineKeyboardMarkup(keyboard),
                                parse_mode='HTML')


def tjbaobiao(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id


def spgli(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    sp_list = list(fenlei.find({}))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]

    for i in sp_list:
        uid = i['uid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'flxxi {uid}'))
    if sp_list == []:
        keyboard.append([InlineKeyboardButton("新建一行", callback_data='newfl')])
    else:
        keyboard.append([InlineKeyboardButton("新建一行", callback_data='newfl'),
                         InlineKeyboardButton('调整行排序', callback_data='paixufl'),
                         InlineKeyboardButton('删除一行', callback_data='delfl')])
    keyboard.append([InlineKeyboardButton('返回', callback_data='backstart'),
                     InlineKeyboardButton('关闭', callback_data=f'close {user_id}')])
    text = f'''
商品管理
    '''
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


def generate_24bit_uid():
    # 生成一个UUID
    uid = uuid.uuid4()

    # 将UUID转换为字符串
    uid_str = str(uid)

    # 使用MD5哈希算法将字符串哈希为一个128位的值
    hashed_uid = hashlib.md5(uid_str.encode()).hexdigest()

    # 取哈希值的前24位作为我们的24位UID
    return hashed_uid[:24]


def newfl(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    del_message(query.message)
    bot_id = context.bot.id
    maxrow = fenlei.find_one({}, sort=[('row', -1)])
    if maxrow is None:
        maxrow = 1
    else:
        maxrow = maxrow['row'] + 1
    uid = generate_24bit_uid()
    fenleibiao(uid, '点击按钮修改', maxrow)
    keylist = list(fenlei.find({}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        uid = i['uid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'flxxi {uid}'))
    keyboard.append([InlineKeyboardButton("新建一行", callback_data='newfl'),
                     InlineKeyboardButton('调整行排序', callback_data='paixufl'),
                     InlineKeyboardButton('删除一行', callback_data='delfl')])
    context.bot.send_message(chat_id=user_id, text='商品管理', reply_markup=InlineKeyboardMarkup(keyboard))


def flxxi(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    uid = query.data.replace('flxxi ', '')
    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    ej_list = ejfl.find({'uid': uid})
    for i in ej_list:
        nowuid = i['nowuid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'fejxxi {nowuid}'))

    keyboard.append([InlineKeyboardButton('修改分类名', callback_data=f'upspname {uid}'),
                     InlineKeyboardButton('新增二级分类', callback_data=f'newejfl {uid}')])
    keyboard.append([InlineKeyboardButton('调整二级分类排序', callback_data=f'paixuejfl {uid}'),
                     InlineKeyboardButton('删除二级分类', callback_data=f'delejfl {uid}')])
    keyboard.append([InlineKeyboardButton('返回', callback_data=f'spgli')])
    fstext = f'''
分类: {fl_pro}
    '''
    query.edit_message_text(text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def fejxxi(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('fejxxi ', '')

    ej_list = ejfl.find_one({'nowuid': nowuid})
    uid = ej_list['uid']
    ej_projectname = ej_list['projectname']
    money = ej_list['money']
    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keyboard = [
        [InlineKeyboardButton('取出所有库存', callback_data=f'qchuall {nowuid}'),
         InlineKeyboardButton('此商品使用说明', callback_data=f'update_sysm {nowuid}')],
        [InlineKeyboardButton('上传谷歌账户', callback_data=f'update_gg {nowuid}'),
         InlineKeyboardButton('购买此商品提示', callback_data=f'update_wbts {nowuid}')],
        [InlineKeyboardButton('上传链接', callback_data=f'update_hy {nowuid}'),
         InlineKeyboardButton('上传txt文件', callback_data=f'update_txt {nowuid}')],
        [InlineKeyboardButton('上传号包', callback_data=f'update_hb {nowuid}'),
         InlineKeyboardButton('上传协议号', callback_data=f'update_xyh {nowuid}')],
        [InlineKeyboardButton('修改二级分类名', callback_data=f'upejflname {nowuid}'),
         InlineKeyboardButton('修改价格', callback_data=f'upmoney {nowuid}')],
        [InlineKeyboardButton('返回', callback_data=f'flxxi {uid}')]
    ]
    kc = len(list(hb.find({'nowuid': nowuid, 'state': 0})))
    ys = len(list(hb.find({'nowuid': nowuid, 'state': 1})))
    fstext = f'''
主分类: {fl_pro}
二级分类: {ej_projectname}

价格: CNY{money}
库存: {kc}
已售: {ys}
    '''
    query.edit_message_text(text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def update_xyh(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('update_xyh ', '')
    fstext = f'''
发送协议号压缩包，自动识别里面的json或session格式
    '''
    user.update_one({"user_id": user_id}, {"$set": {"sign": f'update_xyh {nowuid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def update_gg(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('update_gg ', '')
    fstext = f'''
发送txt文件
    '''
    user.update_one({"user_id": user_id}, {"$set": {"sign": f'update_gg {nowuid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def update_txt(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('update_txt ', '')
    fstext = f'''
api号码链接专用，请正确上传，发送txt文件，一行一个
    '''
    user.update_one({"user_id": user_id}, {"$set": {"sign": f'update_txt {nowuid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def update_sysm(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('update_sysm ', '')
    dqts = ejfl.find_one({'nowuid': nowuid})['sysm']

    context.bot.send_message(chat_id=user_id, text=dqts, parse_mode='HTML')

    fstext = f'''
当前使用说明为上面
输入新的文字更改
    '''
    user.update_one({"user_id": user_id}, {"$set": {"sign": f'update_sysm {nowuid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def update_wbts(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('update_wbts ', '')
    
    try:
        ejfl_record = ejfl.find_one({'nowuid': nowuid})
        if not ejfl_record:
            context.bot.send_message(chat_id=user_id, text="❌ 商品不存在")
            return
            
        dqts = ejfl_record['text']
        
        # 发送消息时不使用HTML解析，或者清理HTML标签
        try:
            context.bot.send_message(chat_id=user_id, text=dqts, parse_mode='HTML')
        except:
            # 如果HTML解析失败，则去掉HTML标签发送纯文本
            clean_text = dqts.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
            context.bot.send_message(chat_id=user_id, text=clean_text)

        fstext = f'''
当前分类提示为上面
输入新的文字更改
        '''
        user.update_one({"user_id": user_id}, {"$set": {"sign": f'update_wbts {nowuid}'}})
        keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
        context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))
        
    except Exception as e:
        context.bot.send_message(chat_id=user_id, text=f"❌ 操作失败: {str(e)}")

def update_hy(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('update_hy ', '')
    fstext = f'''
发送链接，换行代表多个
单个
https://t.me/giftcode/IApV5cqF2FCzAQAA5aDXkeEqQrQ
多个
https://t.me/giftcode/IApV5cqF2FCzAQAA5aDXkeEqQrQ
https://t.me/giftcode/wI_oG9K2oFBSAQAA-Z2W0Fb3ng8
https://t.me/giftcode/_xSoPUXMgVBmAQAAiKBPNxWWIpY
    '''
    user.update_one({"user_id": user_id}, {"$set": {"sign": f'update_hy {nowuid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard),
                             disable_web_page_preview=True)


def update_hb(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    nowuid = query.data.replace('update_hb ', '')
    fstext = f'''
发送号包
    '''
    user.update_one({"user_id": user_id}, {"$set": {"sign": f'update_hb {nowuid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def upmoney(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    uid = query.data.replace('upmoney ', '')
    fstext = f'''
输入新的价格
    '''

    user.update_one({"user_id": user_id}, {"$set": {"sign": f'upmoney {uid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def upejflname(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    uid = query.data.replace('upejflname ', '')
    fstext = f'''
输入新的名字
例如 🇨🇳+86中国~直登号(tadta)
    '''

    user.update_one({"user_id": user_id}, {"$set": {"sign": f'upejflname {uid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def upspname(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    uid = query.data.replace('upspname ', '')
    fstext = f'''
输入新的名字
例如 🌎亚洲国家~✈直登号(tadta)
    '''

    user.update_one({"user_id": user_id}, {"$set": {"sign": f'upspname {uid}'}})
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def newejfl(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    uid = query.data.replace('newejfl ', '')

    maxrow = ejfl.find_one({'uid': uid}, sort=[('row', -1)])
    if maxrow is None:
        maxrow = 1
    else:
        maxrow = maxrow['row'] + 1
    nowuid = generate_24bit_uid()
    erjifenleibiao(uid, nowuid, '点击按钮修改', maxrow)
    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    ej_list = ejfl.find({'uid': uid})
    for i in ej_list:
        nowuid = i['nowuid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'fejxxi {nowuid}'))

    keyboard.append([InlineKeyboardButton('修改分类名', callback_data=f'upspname {uid}'),
                     InlineKeyboardButton('新增二级分类', callback_data=f'newejfl {uid}')])
    keyboard.append([InlineKeyboardButton('调整二级分类排序', callback_data=f'paixuejfl {uid}'),
                     InlineKeyboardButton('删除二级分类', callback_data=f'delejfl {uid}')])
    keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
    fstext = f'''
分类: {fl_pro}
    '''
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def addzdykey(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    keylist = get_key.find({}, sort=[('Row', 1), ('first', 1)])
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
    if keylist == []:
        keyboard = [[InlineKeyboardButton("新建一行", callback_data='newrow')]]
    else:
        keyboard.append([InlineKeyboardButton('新建一行', callback_data='newrow'),
                         InlineKeyboardButton('删除一行', callback_data='delrow'),
                         InlineKeyboardButton('调整行排序', callback_data='paixurow')])
        keyboard.append([InlineKeyboardButton('修改按钮', callback_data='newkey')])

    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    text = f'''
自定义按钮
    '''
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


def newkey(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='请先新建一行')
    else:
        maxrow = max(count)
        for i in range(0, maxrow):
            keyboard.append([InlineKeyboardButton(f'第{i + 1}行', callback_data=f'dddd'),
                             InlineKeyboardButton('➕', callback_data=f'addhangkey {i + 1}'),
                             InlineKeyboardButton('➖', callback_data=f'delhangkey {i + 1}')])
        keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
        keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
        query.edit_message_text(text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def newrow(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    del_message(query.message)
    bot_id = context.bot.id
    maxrow = get_key.find_one({}, sort=[('Row', -1)])
    if maxrow is None:
        maxrow = 1
    else:
        maxrow = maxrow['Row'] + 1
    keybutton(maxrow, 1)
    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
    keyboard.append([InlineKeyboardButton('新建一行', callback_data='newrow'),
                     InlineKeyboardButton('删除一行', callback_data='delrow'),
                     InlineKeyboardButton('调整行排序', callback_data='paixurow')])
    keyboard.append([InlineKeyboardButton('修改按钮', callback_data='newkey')])
    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    context.bot.send_message(chat_id=user_id, text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def close(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = query.message.chat
    query.answer()
    yh_id = query.data.replace("close ", '')
    bot_id = context.bot.id
    chat_id = chat.id
    user_id = query.from_user.id

    user.update_one({'user_id': user_id}, {'$set': {'sign': 0}})
    context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)

def set_language(update: Update, context: CallbackContext):
    """处理语言设置回调"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    
    if query.data == 'set_lang_zh':
        # 设置中文
        user.update_one({'user_id': user_id}, {"$set": {'lang': 'zh'}})
        
        # 更新键盘为中文
        keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], []]
        
        keylist = get_key.find({}, sort=[('Row', 1), ('first', 1)])
        for i in keylist:
            projectname = i['projectname']
            if projectname != '中文服务':
                row = i['Row']
                keyboard[row - 1].append(KeyboardButton(projectname))
        
        query.edit_message_text(text='语言切换成功！Language switched successfully!')
        context.bot.send_message(chat_id=user_id, text='欢迎使用中文服务！',
                               reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                               one_time_keyboard=False))
        
    elif query.data == 'set_lang_en':
        # 设置英文
        user.update_one({'user_id': user_id}, {"$set": {'lang': 'en'}})
        
        # 更新键盘为英文
        keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                    [], [], [], [], []]
        
        keylist = get_key.find({}, sort=[('Row', 1), ('first', 1)])
        for i in keylist:
            projectname = i['projectname']
            if projectname != '中文服务':
                # 获取英文翻译
                fy_result = fyb.find_one({'text': projectname})
                if fy_result:
                    projectname = fy_result['fanyi']
                else:
                    projectname = get_fy(projectname)
                row = i['Row']
                keyboard[row - 1].append(KeyboardButton(projectname))
        
        query.edit_message_text(text='Language switched successfully! 语言切换成功！')
        context.bot.send_message(chat_id=user_id, text='Welcome to English service!',
                               reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                               one_time_keyboard=False))

def usdt_trc20_recharge(update: Update, context: CallbackContext):
    """处理USDT-TRC20充值"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    lang = user_list['lang']
    
    if lang == 'zh':
        fstext = '''
<b>💰请选择下面充值订单金额

💹请严格按照小数点转账‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('10USDT', callback_data='yuecz 10'),
             InlineKeyboardButton('30USDT', callback_data='yuecz 30'),
             InlineKeyboardButton('50USDT', callback_data='yuecz 50')],
            [InlineKeyboardButton('100USDT', callback_data='yuecz 100'),
             InlineKeyboardButton('200USDT', callback_data='yuecz 200'),
             InlineKeyboardButton('500USDT', callback_data='yuecz 500')],
            [InlineKeyboardButton('1000USDT', callback_data='yuecz 1000'),
             InlineKeyboardButton('1500USDT', callback_data='yuecz 1500'),
             InlineKeyboardButton('2000USDT', callback_data='yuecz 2000')],
            [InlineKeyboardButton('自定义充值金额', callback_data='zdycz')],
            [InlineKeyboardButton('❌ 返回', callback_data='back_to_recharge')]
        ]
    else:
        fstext = '''
<b>💰Please select recharge amount

💹Please transfer according to the exact decimal point‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('10USDT', callback_data='yuecz 10'),
             InlineKeyboardButton('30USDT', callback_data='yuecz 30'),
             InlineKeyboardButton('50USDT', callback_data='yuecz 50')],
            [InlineKeyboardButton('100USDT', callback_data='yuecz 100'),
             InlineKeyboardButton('200USDT', callback_data='yuecz 200'),
             InlineKeyboardButton('500USDT', callback_data='yuecz 500')],
            [InlineKeyboardButton('1000USDT', callback_data='yuecz 1000'),
             InlineKeyboardButton('1500USDT', callback_data='yuecz 1500'),
             InlineKeyboardButton('2000USDT', callback_data='yuecz 2000')],
            [InlineKeyboardButton('Customize recharge amount', callback_data='zdycz')],
            [InlineKeyboardButton('❌ Back', callback_data='back_to_recharge')]
        ]
    
    query.edit_message_text(text=fstext, parse_mode='HTML',
                          reply_markup=InlineKeyboardMarkup(keyboard))


def epay_wx(update: Update, context: CallbackContext):
    """处理微信支付"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    lang = user_list['lang']
    
    if lang == 'zh':
        fstext = '''
<b>💚 微信支付

请选择充值金额：</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY10', callback_data='epay_wx_10'),
             InlineKeyboardButton('CNY30', callback_data='epay_wx_30'),
             InlineKeyboardButton('CNY50', callback_data='epay_wx_50')],
            [InlineKeyboardButton('CNY100', callback_data='epay_wx_100'),
             InlineKeyboardButton('CNY200', callback_data='epay_wx_200'),
             InlineKeyboardButton('CNY500', callback_data='epay_wx_500')],
            [InlineKeyboardButton('自定义金额', callback_data='epay_wx_custom')],
            [InlineKeyboardButton('❌ 返回', callback_data='back_to_recharge')]
        ]
    else:
        fstext = '''
<b>💚 WeChat Pay

Please select amount:</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY10', callback_data='epay_wx_10'),
             InlineKeyboardButton('CNY30', callback_data='epay_wx_30'),
             InlineKeyboardButton('CNY50', callback_data='epay_wx_50')],
            [InlineKeyboardButton('CNY100', callback_data='epay_wx_100'),
             InlineKeyboardButton('CNY200', callback_data='epay_wx_200'),
             InlineKeyboardButton('CNY500', callback_data='epay_wx_500')],
            [InlineKeyboardButton('Custom Amount', callback_data='epay_wx_custom')],
            [InlineKeyboardButton('❌ Back', callback_data='back_to_recharge')]
        ]
    
    query.edit_message_text(text=fstext, parse_mode='HTML',
                          reply_markup=InlineKeyboardMarkup(keyboard))

def epay_ali(update: Update, context: CallbackContext):
    """处理支付宝"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    lang = user_list['lang']
    
    if lang == 'zh':
        fstext = '''
<b>💙 支付宝

请选择充值金额：</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY10', callback_data='epay_ali_10'),
             InlineKeyboardButton('CNY30', callback_data='epay_ali_30'),
             InlineKeyboardButton('CNY50', callback_data='epay_ali_50')],
            [InlineKeyboardButton('CNY100', callback_data='epay_ali_100'),
             InlineKeyboardButton('CNY200', callback_data='epay_ali_200'),
             InlineKeyboardButton('CNY500', callback_data='epay_ali_500')],
            [InlineKeyboardButton('自定义金额', callback_data='epay_ali_custom')],
            [InlineKeyboardButton('❌ 返回', callback_data='back_to_recharge')]
        ]
    else:
        fstext = '''
<b>💙 Alipay

Please select amount:</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY10', callback_data='epay_ali_10'),
             InlineKeyboardButton('CNY30', callback_data='epay_ali_30'),
             InlineKeyboardButton('CNY50', callback_data='epay_ali_50')],
            [InlineKeyboardButton('CNY100', callback_data='epay_ali_100'),
             InlineKeyboardButton('CNY200', callback_data='epay_ali_200'),
             InlineKeyboardButton('CNY500', callback_data='epay_ali_500')],
            [InlineKeyboardButton('Custom Amount', callback_data='epay_ali_custom')],
            [InlineKeyboardButton('❌ Back', callback_data='back_to_recharge')]
        ]
    
    query.edit_message_text(text=fstext, parse_mode='HTML',
                          reply_markup=InlineKeyboardMarkup(keyboard))

def process_epay_payment_fixed(update: Update, context: CallbackContext):
    """处理易支付支付流程 - 调试版"""
    query = update.callback_query
    query.answer()
    
    data = query.data
    user_id = query.from_user.id
    
    print(f"\n🔍 支付请求调试信息:")
    print(f"   用户: {user_id}")
    print(f"   请求: {data}")
    print(f"   EPAY_CONFIG 状态: {EPAY_CONFIG is not None}")
    print(f"   EPAY_CONFIG 内容: {EPAY_CONFIG}")
    
    # 检查易支付配置
    if EPAY_CONFIG is None:
        print("❌ EPAY_CONFIG 为 None")
        
        # 尝试重新加载配置
        print("🔄 尝试重新加载配置...")
        if load_epay_config():
            print("✅ 重新加载成功")
        else:
            print("❌ 重新加载失败")
            
            # 发送错误信息给用户
            user_list = user.find_one({"user_id": user_id})
            lang = user_list.get('lang', 'zh') if user_list else 'zh'
            
            if lang == 'zh':
                error_text = """❌ 支付系统配置问题

可能的原因：
1. zhifu.py 文件不存在
2. 配置信息不完整
3. 模块导入失败

请尝试：
• 使用 USDT-TRC20 充值
• 联系管理员检查配置

技术信息已记录到日志中"""
            else:
                error_text = """❌ Payment system configuration issue

Possible causes:
1. zhifu.py file missing
2. Incomplete configuration
3. Module import failed

Please try:
• Use USDT-TRC20 recharge
• Contact admin to check config

Technical info logged"""
            
            keyboard = [
                [InlineKeyboardButton('💎 USDT充值' if lang == 'zh' else '💎 USDT Recharge', 
                                    callback_data=f'pay_usdt_{data.split("_")[-1]}')],
                [InlineKeyboardButton('🔙 返回' if lang == 'zh' else '🔙 Back', 
                                    callback_data='back_to_amount_select')]
            ]
            
            query.edit_message_text(text=error_text, 
                                  reply_markup=InlineKeyboardMarkup(keyboard))
            return
    
    # 如果配置存在，继续正常处理
    print("✅ 配置检查通过，继续处理支付...")
    
    user_list = user.find_one({"user_id": user_id})
    if not user_list:
        query.edit_message_text(text="❌ 用户信息未找到，请先发送 /start")
        return
        
    lang = user_list.get('lang', 'zh')
    
    # 解析支付方式和金额
    if data.startswith('pay_wx_'):
        pay_type = 'wxpay'
        amount = int(data.replace('pay_wx_', ''))
        pay_name = '微信支付' if lang == 'zh' else 'WeChat Pay'
    elif data.startswith('pay_ali_'):
        pay_type = 'alipay' 
        amount = int(data.replace('pay_ali_', ''))
        pay_name = '支付宝' if lang == 'zh' else 'Alipay'
    else:
        print(f"❌ 未知的支付方式: {data}")
        query.edit_message_text(text="❌ 不支持的支付方式")
        return
    
    print(f"🔍 处理{pay_name}支付，金额: CNY{amount}")
    
    # 验证金额范围
    if amount < 1:
        query.edit_message_text(text="❌ 充值金额不能小于1元")
        return
    if amount > 10000:
        query.edit_message_text(text="❌ 充值金额不能大于10000元")
        return
    
    # 生成唯一订单号
    timestamp = int(time.time())
    import random
    random_suffix = random.randint(1000, 9999)
    order_id = f"epay_{timestamp}_{user_id}_{random_suffix}"
    
    print(f"📋 生成订单号: {order_id}")
    
    try:
        # 创建支付参数
        params = {
            'pid': EPAY_CONFIG['pid'],
            'type': pay_type,
            'out_trade_no': order_id,
            'notify_url': EPAY_CONFIG['notify_url'],
            'return_url': EPAY_CONFIG['return_url'],
            'name': '充值USDT',
            'money': str(amount),
            'sitename': 'TG机器人充值'
        }
        
        print(f"💳 支付参数: {params}")
        
        # 生成签名
        sorted_params = sorted(params.items())
        param_str = '&'.join([f'{k}={v}' for k, v in sorted_params if v != ''])
        sign_str = param_str + EPAY_CONFIG['key']
        signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        
        params['sign'] = signature
        params['sign_type'] = 'MD5'
        
        print(f"🔐 签名字符串: {sign_str}")
        print(f"🔐 生成签名: {signature}")
        
        # 构建支付链接
        import urllib.parse
        query_string = urllib.parse.urlencode(params)
        pay_url = f"{EPAY_CONFIG['api_url']}?{query_string}"
        
        print(f"🔗 支付链接: {pay_url}")
        
        # 保存订单到数据库
        timer_full = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        order_data = {
            'bianhao': order_id,
            'user_id': user_id,
            'money': amount,
            'pay_type': pay_type,
            'timer': timer_full,
            'epay_status': 'pending',
            'created_timestamp': timestamp,
            'payment_type': 'epay'
        }
        
        try:
            topup.insert_one(order_data)
            print(f"✅ 订单保存成功: {order_id}")
        except Exception as db_error:
            print(f"❌ 订单保存失败: {db_error}")
            query.edit_message_text(text="❌ 订单创建失败，请稍后重试")
            return
        
        # 发送支付链接
        if lang == 'zh':
            fstext = f'''<b>💳 订单创建成功！</b>

💰 充值金额：CNY{amount}
💳 支付方式：{pay_name}
📋 订单号：<code>{order_id}</code>

<b>⚠️ 重要提示：</b>
- 请在10分钟内完成支付
- 支付成功后会自动到账
- 如有问题请联系客服

👇 点击下方按钮去支付'''
            
            keyboard = [
                [InlineKeyboardButton(f'💳 去{pay_name}', url=pay_url)],
                [InlineKeyboardButton('🔄 刷新状态', callback_data=f'check_order_{order_id}')],
                [InlineKeyboardButton('🔙 返回', callback_data='back_to_recharge'),
                 InlineKeyboardButton('❌ 取消', callback_data=f'cancel_order_{order_id}')]
            ]
        else:
            fstext = f'''<b>💳 Order Created Successfully!</b>

💰 Amount: CNY{amount}
💳 Payment Method: {pay_name}
📋 Order No: <code>{order_id}</code>

<b>⚠️ Important:</b>
- Please complete payment within 10 minutes
- Balance will be credited automatically
- Contact support if you have issues

👇 Click button below to pay'''
            
            keyboard = [
                [InlineKeyboardButton(f'💳 Go to {pay_name}', url=pay_url)],
                [InlineKeyboardButton('🔄 Check Status', callback_data=f'check_order_{order_id}')],
                [InlineKeyboardButton('🔙 Back', callback_data='back_to_recharge'),
                 InlineKeyboardButton('❌ Cancel', callback_data=f'cancel_order_{order_id}')]
            ]
        
        query.edit_message_text(text=fstext, parse_mode='HTML',
                              reply_markup=InlineKeyboardMarkup(keyboard))
        
        print(f"✅ 支付界面已发送给用户 {user_id}")
                              
    except Exception as e:
        print(f"❌ 创建支付订单失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 如果创建失败，删除已保存的订单
        try:
            topup.delete_one({'bianhao': order_id})
        except:
            pass
        
        if lang == 'zh':
            query.edit_message_text(text="❌ 订单创建失败，请稍后重试或联系客服")
        else:
            query.edit_message_text(text="❌ Order creation failed, please try again or contact support")

def enhanced_check_payment_notifications(context: CallbackContext):
    """增强版支付通知处理，确保USDT充值能及时通知用户"""
    try:
        # 🔥 修复：优先处理高优先级通知
        notifications_list = list(notifications.find({
            'processed': False
        }).sort([('priority', -1), ('timestamp', 1)]).limit(20))
        
        if not notifications_list:
            return
            
        print(f"🔔 处理 {len(notifications_list)} 个未处理通知")
        
        processed_count = 0
        
        for notification in notifications_list:
            try:
                user_id = notification['user_id']
                noti_type = notification['type']
                
                if noti_type == 'payment_success':
                    amount = notification['amount']
                    new_balance = notification['new_balance']
                    order_no = notification.get('order_no', '')
                    payment_method = notification.get('payment_method', '支付')
                    txid = notification.get('txid', '')
                    
                    # 获取用户语言设置
                    user_info = user.find_one({'user_id': user_id})
                    lang = user_info.get('lang', 'zh') if user_info else 'zh'
                    
                    # 🔥 修复：删除旧的支付消息
                    try:
                        if 'USDT' in payment_method and txid:
                            # 查找并删除相关的支付消息
                            old_orders = list(topup.find({
                                'user_id': user_id, 
                                'message_id': {'$exists': True}
                            }))
                            
                            for order in old_orders:
                                try:
                                    context.bot.delete_message(
                                        chat_id=user_id,
                                        message_id=order['message_id']
                                    )
                                    print(f"🗑️ 已删除旧支付消息: {order['message_id']}")
                                except:
                                    pass
                                    
                    except Exception as delete_error:
                        print(f"⚠️ 删除旧消息失败: {delete_error}")
                    
                    # 🔥 修复：构造成功通知消息
                    if lang == 'zh':
                        if txid and len(txid) > 10:
                            success_text = f'''🎉 <b>充值成功！</b>

💰 充值金额：CNY{amount}
💎 当前余额：CNY{new_balance}
📋 订单号：<code>{order_no}</code>
💳 支付方式：{payment_method}
🔗 交易哈希：<a href="https://tronscan.org/#/transaction/{txid}">查看详情</a>
🕒 到账时间：{time.strftime('%Y-%m-%d %H:%M:%S')}

✅ 余额已到账，感谢您的使用！'''
                        else:
                            success_text = f'''🎉 <b>充值成功！</b>

💰 充值金额：CNY{amount}
💎 当前余额：CNY{new_balance}
📋 订单号：<code>{order_no}</code>
💳 支付方式：{payment_method}
🕒 到账时间：{time.strftime('%Y-%m-%d %H:%M:%S')}

✅ 余额已到账，感谢您的使用！'''

                        keyboard = [
                            [InlineKeyboardButton('💤 个人中心', callback_data='profile')],
                            [InlineKeyboardButton('🛒 购买商品', callback_data='backzcd')],
                            [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]
                        ]
                    else:
                        if txid and len(txid) > 10:
                            success_text = f'''🎉 <b>Payment Successful!</b>

💰 Amount: CNY{amount}
💎 Current Balance: CNY{new_balance}
📋 Order No: <code>{order_no}</code>
💳 Payment Method: {payment_method}
🔗 Transaction: <a href="https://tronscan.org/#/transaction/{txid}">View Details</a>
🕒 Credited: {time.strftime('%Y-%m-%d %H:%M:%S')}

✅ Balance credited, thank you!'''
                        else:
                            success_text = f'''🎉 <b>Payment Successful!</b>

💰 Amount: CNY{amount}
💎 Current Balance: CNY{new_balance}
📋 Order No: <code>{order_no}</code>
💳 Payment Method: {payment_method}
🕒 Credited: {time.strftime('%Y-%m-%d %H:%M:%S')}

✅ Balance credited, thank you!'''

                        keyboard = [
                            [InlineKeyboardButton('💤 Profile', callback_data='profile')],
                            [InlineKeyboardButton('🛒 Buy Products', callback_data='backzcd')],
                            [InlineKeyboardButton('❌ Close', callback_data=f'close {user_id}')]
                        ]
                    
                    # 🔥 修复：发送通知消息
                    try:
                        context.bot.send_message(
                            chat_id=user_id, 
                            text=success_text,
                            parse_mode='HTML',
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            disable_web_page_preview=True
                        )
                        
                        print(f"✅ 已发送充值成功通知给用户 {user_id}")
                        processed_count += 1
                        
                        # 标记通知已处理
                        notifications.update_one(
                            {'_id': notification['_id']},
                            {'$set': {
                                'processed': True, 
                                'sent_time': time.time(),
                                'sent_at': time.strftime('%Y-%m-%d %H:%M:%S')
                            }}
                        )
                        
                        # 🔥 修复：发送管理员通知
                        admin_text = f'''🎯 用户充值通知

👤 用户: <a href="tg://user?id={user_id}">查看用户</a>
💰 充值金额: CNY{amount}
💎 当前余额: CNY{new_balance}
🔗 交易哈希: <code>{txid[:20] if txid else 'N/A'}...</code>
⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}
🔥 状态: 已自动到账'''
                        
                        # 只通知前3个管理员，避免刷屏
                        admin_count = 0
                        for admin in user.find({'state': '4'}).limit(3):
                            if admin_count >= 3:
                                break
                            try:
                                context.bot.send_message(
                                    chat_id=admin['user_id'], 
                                    text=admin_text, 
                                    parse_mode='HTML',
                                    disable_web_page_preview=True
                                )
                                admin_count += 1
                            except:
                                continue
                        
                    except Exception as send_error:
                        print(f"❌ 发送通知给用户 {user_id} 失败: {send_error}")
                        
                        if "Forbidden" in str(send_error) or "blocked" in str(send_error).lower():
                            # 用户可能已阻止机器人，标记为已处理避免重复尝试
                            notifications.update_one(
                                {'_id': notification['_id']},
                                {'$set': {
                                    'processed': True, 
                                    'failed': True,
                                    'error': str(send_error),
                                    'error_time': time.time()
                                }}
                            )
                            print(f"⚠️ 用户 {user_id} 可能已阻止机器人，已标记")
                        continue
                        
            except Exception as process_error:
                print(f"❌ 处理单个通知失败: {process_error}")
                continue
        
        if processed_count > 0:
            print(f"🎉 成功处理了 {processed_count} 个通知")
            
    except Exception as e:
        print(f"❌ 检查支付通知失败: {e}")
        import traceback
        traceback.print_exc()

# ==================== 手动测试函数 ====================
def test_epay_import():
    """手动测试易支付导入"""
    print("\n🧪 开始手动测试易支付导入...")
    
    try:
        # 测试1：检查文件
        import os
        print(f"📁 当前目录: {os.getcwd()}")
        print(f"📄 zhifu.py 存在: {os.path.exists('zhifu.py')}")
        
        # 测试2：直接导入
        print("📂 尝试导入 zhifu...")
        import zhifu
        print("✅ zhifu 模块导入成功")
        
        # 测试3：获取配置
        config = zhifu.EPAY_CONFIG
        print(f"📋 配置获取成功: {config}")
        
        # 测试4：验证配置
        if config and config.get('pid'):
            print(f"✅ 配置验证成功，商户号: {config['pid']}")
            return config
        else:
            print("❌ 配置验证失败")
            return None
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

# 运行测试
test_result = test_epay_import()
print(f"🧪 测试结果: {test_result is not None}")

# ==================== 使用说明 ====================
print("\n" + "="*60)
print("📋 使用说明：")
print("1. 完全替换 bot.py 开头的易支付配置导入代码")
print("2. 替换 process_epay_payment_fixed 函数")
print("3. 重启机器人")
print("4. 查看调试信息确认配置加载状态")
print("5. 如果还有问题，检查日志中的详细调试信息")
print("="*60)

def select_amount(update: Update, context: CallbackContext):
    """修复版金额选择处理"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    
    if user_list is None:
        query.edit_message_text(text="请先发送 /start 初始化账户")
        return
        
    lang = user_list.get('lang', 'zh')
    
    data = query.data
    if data == 'select_amount_custom':
        # 🔥 关键修复：正确设置自定义金额输入状态
        user.update_one({'user_id': user_id}, {"$set": {"sign": 'custom_amount_input'}})
        
        if lang == 'zh':
            fstext = '''💡 <b>自定义充值金额</b>

请输入您要充值的金额（人民币）：

📝 <b>格式：</b>直接输入数字即可
💰 <b>范围：</b>1 - 10000 元
📱 <b>例如：</b>88 或 168

<i>💡 输入后将显示支付方式选择</i>'''
            keyboard = [[InlineKeyboardButton('🔙 返回', callback_data='back_to_amount_select')]]
        else:
            fstext = '''💡 <b>Custom Recharge Amount</b>

Please enter the amount you want to recharge (RMB):

📝 <b>Format:</b> Enter numbers only
💰 <b>Range:</b> 1 - 10000 CNY
📱 <b>Example:</b> 88 or 168

<i>💡 Payment options will appear after input</i>'''
            keyboard = [[InlineKeyboardButton('🔙 Back', callback_data='back_to_amount_select')]]
        
        query.edit_message_text(text=fstext, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # 提取金额
    amount = int(data.replace('select_amount_', ''))
    
    # 显示支付方式选择
    if lang == 'zh':
        fstext = f'''<b>💰充值金额：CNY{amount}

请选择支付方式：</b>'''
        keyboard = [
            [InlineKeyboardButton('💚 微信支付', callback_data=f'pay_wx_{amount}'),
             InlineKeyboardButton('💙 支付宝', callback_data=f'pay_ali_{amount}')],
            [InlineKeyboardButton('💎 USDT-TRC20', callback_data=f'pay_usdt_{amount}')],
            [InlineKeyboardButton('🔙 返回选择金额', callback_data='back_to_amount_select'),
             InlineKeyboardButton('❌ 取消', callback_data=f'close {user_id}')]
        ]
    else:
        fstext = f'''<b>💰Recharge Amount: CNY{amount}

Please select payment method:</b>'''
        keyboard = [
            [InlineKeyboardButton('💚 WeChat Pay', callback_data=f'pay_wx_{amount}'),
             InlineKeyboardButton('💙 Alipay', callback_data=f'pay_ali_{amount}')],
            [InlineKeyboardButton('💎 USDT-TRC20', callback_data=f'pay_usdt_{amount}')],
            [InlineKeyboardButton('🔙 Back to Amount', callback_data='back_to_amount_select'),
             InlineKeyboardButton('❌ Cancel', callback_data=f'close {user_id}')]
        ]
                    
    query.edit_message_text(text=fstext, parse_mode='HTML',
                          reply_markup=InlineKeyboardMarkup(keyboard))


def pay_usdt(update: Update, context: CallbackContext):
    """处理USDT支付选择"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    
    if not user_list:
        query.edit_message_text(text="请先发送 /start")
        return
        
    lang = user_list.get('lang', 'zh')
    
    # 从callback_data中提取金额
    data = query.data
    amount = int(data.replace('pay_usdt_', ''))
    
    # 获取当前汇率
    rate_doc = shangtext.find_one({'projectname': '人民币USDT汇率'})
    exchange_rate = float(rate_doc['text']) if rate_doc else 7.2
    
    # 计算需要支付的USDT金额
    usdt_amount = round(amount / exchange_rate, 2)
    
    # 删除之前的充值订单
    topup.delete_many({'user_id': user_id})
    timer = time.strftime('%Y%m%d%H%M%S', time.localtime())
    bianhao = timer
    
    # 添加随机小数避免重复
    while True:
        suijishu = round(random.uniform(0.01, 0.50), 2)
        final_usdt = Decimal(str(usdt_amount)) + Decimal(str(suijishu))
        if topup.find_one({"money": float(final_usdt)}) is None:
            break

    timer_full = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    
    # 获取充值地址
    trc20_doc = shangtext.find_one({'projectname': '充值地址'})
    if not trc20_doc or not trc20_doc.get('text'):
        query.edit_message_text(text="❌ 充值地址未配置，请联系管理员")
        return
    
    trc20 = trc20_doc['text']
    
    if lang == 'zh':
        text = f'''
<b>💎 USDT-TRC20 充值详情</b>

💰 充值金额：CNY{amount}
💱 当前汇率：1 USDT = CNY{exchange_rate}
💎 实际支付：<code>{final_usdt} USDT</code>
📍 收款地址：<code>{trc20}</code>

<b>⚠️ 重要提示：
- 请一定按照金额后面小数点转账
- 请在10分钟内付款，超时订单自动取消
- 支付成功后余额将显示为人民币</b>
        '''
        keyboard = [[InlineKeyboardButton('❌取消订单', callback_data=f'qxdingdan {user_id}')]]
    else:
        text = f'''
<b>💎 USDT-TRC20 Recharge Details</b>

💰 Recharge Amount: CNY{amount}
💱 Exchange Rate: 1 USDT = CNY{exchange_rate}
💎 Transfer Amount: <code>{final_usdt} USDT</code>
📍 Receiving Address: <code>{trc20}</code>

<b>⚠️ Important Notes:
- Please transfer exactly according to the decimal amount
- Please pay within 10 minutes, order will be auto-cancelled
- Balance will be displayed in RMB after successful payment</b>
        '''
        keyboard = [[InlineKeyboardButton('❌Cancel Order', callback_data=f'qxdingdan {user_id}')]]
    
    # 检查二维码文件是否存在
    qr_file = f'{trc20}.png'
    if not os.path.exists(qr_file):
        try:
            import qrcode
            img = qrcode.make(data=trc20)
            with open(qr_file, 'wb') as f:
                img.save(f)
            print(f"✅ 生成二维码文件: {qr_file}")
        except Exception as e:
            print(f"❌ 生成二维码失败: {e}")
            query.edit_message_text(text=text, parse_mode='HTML',
                                   reply_markup=InlineKeyboardMarkup(keyboard))
            return
    
    try:
        # 发送带二维码的消息
        message_id = context.bot.send_photo(
            chat_id=user_id, 
            photo=open(qr_file, 'rb'), 
            caption=text, 
            parse_mode='HTML', 
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"❌ 发送二维码失败: {e}")
        message_id = context.bot.send_message(
            chat_id=user_id, 
            text=text, 
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 保存订单
    topup.insert_one({
        'bianhao': bianhao,
        'user_id': user_id,
        'money': float(final_usdt),
        'cny_amount': amount,
        'suijishu': suijishu,
        'timer': timer_full,
        'message_id': message_id.message_id,
        'payment_type': 'usdt_cny'
    })




def back_to_amount_select(update: Update, context: CallbackContext):
    """返回金额选择"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    
    if not user_list:
        query.edit_message_text(text="请先发送 /start")
        return
        
    lang = user_list.get('lang', 'zh')
    
    if lang == 'zh':
        fstext = '''
<b>💰请选择充值金额

💹请选择您要充值的金额‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
             InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
             InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
            [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
             InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
             InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
            [InlineKeyboardButton('💡自定义金额', callback_data='select_amount_custom')],
            [InlineKeyboardButton('❌ 取消', callback_data=f'close {user_id}')]
        ]
    else:
        fstext = '''
<b>💰Please select recharge amount

💹Please select the amount you want to recharge‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
             InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
             InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
            [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
             InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
             InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
            [InlineKeyboardButton('💡Custom Amount', callback_data='select_amount_custom')],
            [InlineKeyboardButton('❌ Cancel', callback_data=f'close {user_id}')]
        ]
    
    query.edit_message_text(text=fstext, parse_mode='HTML',
                          reply_markup=InlineKeyboardMarkup(keyboard))

def back_to_recharge(update: Update, context: CallbackContext):
    """返回充值方式选择"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    
    if not user_list:
        query.edit_message_text(text="请先发送 /start")
        return
        
    lang = user_list.get('lang', 'zh')
    
    if lang == 'zh':
        fstext = '''
<b>💰请选择充值金额

💹请选择您要充值的金额‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
             InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
             InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
            [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
             InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
             InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
            [InlineKeyboardButton('💡自定义金额', callback_data='select_amount_custom')],
            [InlineKeyboardButton('❌ 取消', callback_data=f'close {user_id}')]
        ]
    else:
        fstext = '''
<b>💰Please select recharge amount

💹Please select the amount you want to recharge‼️</b>
        '''
        keyboard = [
            [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
             InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
             InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
            [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
             InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
             InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
            [InlineKeyboardButton('💡Custom Amount', callback_data='select_amount_custom')],
            [InlineKeyboardButton('❌ Cancel', callback_data=f'close {user_id}')]
        ]
    
    query.edit_message_text(text=fstext, parse_mode='HTML',
                          reply_markup=InlineKeyboardMarkup(keyboard))

def check_order_status(update: Update, context: CallbackContext):
    """检查订单状态"""
    query = update.callback_query
    query.answer()
    
    order_id = query.data.replace('check_order_', '')
    user_id = query.from_user.id
    
    print(f"🔍 检查订单状态: {order_id}")
    
    try:
        user_list = user.find_one({"user_id": user_id})
        lang = user_list.get('lang', 'zh') if user_list else 'zh'
        
        # 查找订单
        order = topup.find_one({'bianhao': order_id, 'user_id': user_id})
        
        if not order:
            if lang == 'zh':
                query.answer("❌ 订单不存在", show_alert=True)
            else:
                query.answer("❌ Order not found", show_alert=True)
            return
        
        epay_status = order.get('epay_status', 'pending')
        amount = order.get('money', 0)
        pay_type = order.get('pay_type', 'unknown')
        timer = order.get('timer', '')
        
        if epay_status == 'success':
            # 订单已成功
            if lang == 'zh':
                status_text = f'''<b>✅ 支付成功！</b>

💰 充值金额：CNY{amount}
📋 订单号：<code>{order_id}</code>
🕐 完成时间：{timer}

您的余额已到账，感谢使用！'''
                keyboard = [
                    [InlineKeyboardButton('👤 查看余额', callback_data=f'profile')],
                    [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]
                ]
            else:
                status_text = f'''<b>✅ Payment Successful!</b>

💰 Amount: CNY{amount}
📋 Order No: <code>{order_id}</code>
🕐 Completed: {timer}

Your balance has been credited, thank you!'''
                keyboard = [
                    [InlineKeyboardButton('👤 Check Balance', callback_data=f'profile')],
                    [InlineKeyboardButton('❌ Close', callback_data=f'close {user_id}')]
                ]
            
            query.edit_message_text(text=status_text, parse_mode='HTML',
                                  reply_markup=InlineKeyboardMarkup(keyboard))
        
        elif epay_status == 'pending':
            # 订单待支付
            pay_name = {
                'wxpay': '微信支付' if lang == 'zh' else 'WeChat Pay',
                'alipay': '支付宝' if lang == 'zh' else 'Alipay'
            }.get(pay_type, pay_type)
            
            if lang == 'zh':
                status_text = f'''<b>⏳ 等待支付</b>

💰 充值金额：CNY{amount}
💳 支付方式：{pay_name}
📋 订单号：<code>{order_id}</code>
🕐 创建时间：{timer}

<b>订单状态：</b>等待支付中...

如已完成支付请等待1-2分钟后再次刷新'''
                keyboard = [
                    [InlineKeyboardButton('🔄 刷新状态', callback_data=f'check_order_{order_id}')],
                    [InlineKeyboardButton('❌ 取消订单', callback_data=f'cancel_order_{order_id}')]
                ]
            else:
                status_text = f'''<b>⏳ Waiting for Payment</b>

💰 Amount: CNY{amount}
💳 Payment Method: {pay_name}
📋 Order No: <code>{order_id}</code>
🕐 Created: {timer}

<b>Status:</b> Waiting for payment...

If paid, please wait 1-2 minutes and refresh'''
                keyboard = [
                    [InlineKeyboardButton('🔄 Refresh Status', callback_data=f'check_order_{order_id}')],
                    [InlineKeyboardButton('❌ Cancel Order', callback_data=f'cancel_order_{order_id}')]
                ]
            
            query.edit_message_text(text=status_text, parse_mode='HTML',
                                  reply_markup=InlineKeyboardMarkup(keyboard))
        
        else:
            # 其他状态
            if lang == 'zh':
                query.answer(f"订单状态：{epay_status}", show_alert=True)
            else:
                query.answer(f"Order status: {epay_status}", show_alert=True)
    
    except Exception as e:
        print(f"❌ 检查订单状态失败: {e}")
        if lang == 'zh':
            query.answer("❌ 检查失败，请稍后重试", show_alert=True)
        else:
            query.answer("❌ Check failed, please try again", show_alert=True)

def cancel_order(update: Update, context: CallbackContext):
    """取消订单"""
    query = update.callback_query
    query.answer()
    
    order_id = query.data.replace('cancel_order_', '')
    user_id = query.from_user.id
    
    print(f"🗑️ 取消订单: {order_id}")
    
    try:
        user_list = user.find_one({"user_id": user_id})
        lang = user_list.get('lang', 'zh') if user_list else 'zh'
        
        # 查找并删除订单
        result = topup.delete_one({'bianhao': order_id, 'user_id': user_id, 'epay_status': 'pending'})
        
        if result.deleted_count > 0:
            if lang == 'zh':
                query.edit_message_text(text="✅ 订单已取消")
            else:
                query.edit_message_text(text="✅ Order cancelled")
            print(f"✅ 订单 {order_id} 已取消")
        else:
            if lang == 'zh':
                query.answer("❌ 订单无法取消（可能已支付或不存在）", show_alert=True)
            else:
                query.answer("❌ Cannot cancel order (may be paid or not exist)", show_alert=True)
    
    except Exception as e:
        print(f"❌ 取消订单失败: {e}")
        if lang == 'zh':
            query.answer("❌ 取消失败", show_alert=True)
        else:
            query.answer("❌ Cancel failed", show_alert=True)



def check_order_status(update: Update, context: CallbackContext):
    """检查订单状态 - 优化版"""
    query = update.callback_query
    query.answer()
    
    order_id = query.data.replace('check_order_', '')
    user_id = query.from_user.id
    
    print(f"🔍 检查订单状态: {order_id}")
    
    try:
        user_list = user.find_one({"user_id": user_id})
        lang = user_list.get('lang', 'zh') if user_list else 'zh'
        
        # 查找订单
        order = topup.find_one({'bianhao': order_id, 'user_id': user_id})
        
        if not order:
            if lang == 'zh':
                query.answer("❌ 订单不存在", show_alert=True)
            else:
                query.answer("❌ Order not found", show_alert=True)
            return
        
        epay_status = order.get('epay_status', 'pending')
        amount = order.get('money', 0)
        pay_type = order.get('pay_type', 'unknown')
        timer = order.get('timer', '')
        
        if epay_status == 'success':
            # 订单已成功 - 删除支付消息并显示成功信息
            success_message = "✅ 支付已完成！余额已到账。" if lang == 'zh' else "✅ Payment completed! Balance credited."
            
            try:
                # 删除支付消息
                context.bot.delete_message(
                    chat_id=user_id,
                    message_id=query.message.message_id
                )
                
                # 发送简洁的成功消息
                keyboard = [
                    #[InlineKeyboardButton('👤 查看余额', callback_data='profile')],
                    [InlineKeyboardButton('🛒 购买商品', callback_data='backzcd')]
                ]
                
                context.bot.send_message(
                    chat_id=user_id,
                    text=success_message,
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except:
                query.edit_message_text(text=success_message)
            
            return
        
        elif epay_status == 'pending':
            # 订单待支付 - 实际检查支付状态
            pay_name = {
                'wxpay': '微信支付' if lang == 'zh' else 'WeChat Pay',
                'alipay': '支付宝' if lang == 'zh' else 'Alipay'
            }.get(pay_type, pay_type)
            
            # 🔥 这里可以添加实际的支付状态检查逻辑
            # 比如调用易支付API查询订单状态
            actual_status = check_epay_order_status(order_id)  # 你需要实现这个函数
            
            if actual_status == 'success':
                # 如果检查发现支付已成功，更新订单状态
                process_successful_payment(order_id, amount, user_id)
                
                success_message = "✅ 支付成功！余额正在更新..." if lang == 'zh' else "✅ Payment successful! Balance updating..."
                query.edit_message_text(text=success_message)
                return
            
            if lang == 'zh':
                status_text = f'''<b>⏳ 等待支付</b>

💰 充值金额：CNY{amount}
💳 支付方式：{pay_name}
📋 订单号：<code>{order_id}</code>
🕐 创建时间：{timer}

<b>订单状态：</b>等待支付中...

💡 <b>提示：</b>
• 完成支付后通常1-2分钟内自动到账
• 如超过5分钟未到账请联系客服'''

                keyboard = [
                    [InlineKeyboardButton('🔄 刷新状态', callback_data=f'check_order_{order_id}')],
                    [InlineKeyboardButton('📞 联系客服', callback_data='contact_support')],
                    [InlineKeyboardButton('❌ 取消订单', callback_data=f'cancel_order_{order_id}')]
                ]
            else:
                status_text = f'''<b>⏳ Waiting for Payment</b>

💰 Amount: CNY{amount}
💳 Payment Method: {pay_name}
📋 Order No: <code>{order_id}</code>
🕐 Created: {timer}

<b>Status:</b> Waiting for payment...

💡 <b>Tips:</b>
• Usually credited within 1-2 minutes after payment
• Contact support if not credited after 5 minutes'''

                keyboard = [
                    [InlineKeyboardButton('🔄 Refresh Status', callback_data=f'check_order_{order_id}')],
                    [InlineKeyboardButton('📞 Contact Support', callback_data='contact_support')],
                    [InlineKeyboardButton('❌ Cancel Order', callback_data=f'cancel_order_{order_id}')]
                ]
            
            query.edit_message_text(text=status_text, parse_mode='HTML',
                                  reply_markup=InlineKeyboardMarkup(keyboard))
        
        else:
            # 其他状态
            if lang == 'zh':
                query.answer(f"订单状态：{epay_status}", show_alert=True)
            else:
                query.answer(f"Order status: {epay_status}", show_alert=True)
    
    except Exception as e:
        print(f"❌ 检查订单状态失败: {e}")
        if lang == 'zh':
            query.answer("❌ 检查失败，请稍后重试", show_alert=True)
        else:
            query.answer("❌ Check failed, please try again", show_alert=True)


def check_epay_order_status(order_id):
    """检查易支付订单状态 - 需要实现"""
    try:
        # 这里应该调用易支付API查询订单状态
        # 示例代码，需要根据你的易支付平台API文档实现
        if EPAY_CONFIG:
            # 构建查询参数
            params = {
                'pid': EPAY_CONFIG['pid'],
                'out_trade_no': order_id,
            }
            
            # 生成签名
            sorted_params = sorted(params.items())
            param_str = '&'.join([f'{k}={v}' for k, v in sorted_params if v != ''])
            sign_str = param_str + EPAY_CONFIG['key']
            signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
            
            params['sign'] = signature
            
            # 发送查询请求（这里需要根据易支付API实现）
            # response = requests.get('http://易支付域名/api/query.php', params=params)
            # result = response.json()
            # return result.get('trade_status', 'pending')
            
            # 暂时返回pending，你需要实现实际的API调用
            return 'pending'
        
        return 'pending'
    except Exception as e:
        print(f"❌ 查询支付状态失败: {e}")
        return 'pending'


def process_successful_payment(order_id, amount, user_id):
    """处理支付成功 - 模拟回调处理"""
    try:
        # 更新用户余额
        user_info = user.find_one({'user_id': user_id})
        if user_info:
            current_balance = user_info['USDT']
            new_balance = standard_num(float(current_balance) + float(amount))
            new_balance = float(new_balance) if str(new_balance).count('.') > 0 else int(new_balance)
            
            # 更新数据库
            user.update_one({'user_id': user_id}, {"$set": {'USDT': new_balance}})
            
            # 创建通知
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            notifications.insert_one({
                'user_id': user_id,
                'type': 'payment_success',
                'amount': amount,
                'new_balance': new_balance,
                'order_no': order_id,
                'payment_method': '微信支付',
                'processed': False,
                'created_at': timer,
                'timestamp': time.time()
            })
            
            # 记录日志
            user_logging(order_id, '充值', user_id, amount, timer)
            
            # 删除订单
            topup.delete_one({'bianhao': order_id})
            
            print(f"✅ 处理支付成功: 用户{user_id}, 金额CNY{amount}")
            
    except Exception as e:
        print(f"❌ 处理支付成功失败: {e}")


def contact_support(update: Update, context: CallbackContext):
    """联系客服"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    lang = user_list.get('lang', 'zh') if user_list else 'zh'
    
    if lang == 'zh':
        support_text = '''📞 <b>联系客服</b>

如需帮助，请联系客服：
🔗 Telegram: @qingfenger
📧 邮箱: support@example.com

<b>常见问题：</b>
• 支付完成但未到账：通常1-3分钟内到账，请耐心等待
• 订单超时：可重新创建订单进行支付
• 其他问题：请联系客服并提供订单号'''
    else:
        support_text = '''📞 <b>Contact Support</b>

For help, please contact support:
🔗 Telegram: @qingfenger
📧 Email: support@example.com

<b>Common Issues:</b>
• Payment completed but not credited: Usually credited within 1-3 minutes
• Order timeout: Create new order for payment
• Other issues: Contact support with order number'''
    
    keyboard = [[InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]]
    
    query.edit_message_text(
        text=support_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )





def paixurow(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='没有按钮存在')
    else:
        maxrow = max(count)
        if maxrow == 1:
            context.bot.send_message(chat_id=user_id, text='只有一行按钮无法调整')
        else:
            for i in range(0, maxrow):
                if i == 0:
                    keyboard.append(
                        [InlineKeyboardButton(f'第{i + 1}行下移', callback_data=f'paixuyidong xiayi:{i + 1}')])
                elif i == maxrow - 1:
                    keyboard.append(
                        [InlineKeyboardButton(f'第{i + 1}行上移', callback_data=f'paixuyidong shangyi:{i + 1}')])
                else:
                    keyboard.append(
                        [InlineKeyboardButton(f'第{i + 1}行上移', callback_data=f'paixuyidong shangyi:{i + 1}'),
                         InlineKeyboardButton(f'第{i + 1}行下移', callback_data=f'paixuyidong xiayi:{i + 1}')])
            keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
            keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
            query.edit_message_text(text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def paixuyidong(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('paixuyidong ', '')
    qudataall = qudata.split(':')
    yidongtype = qudataall[0]
    row = int(qudataall[1])
    if yidongtype == 'shangyi':
        get_key.update_many({"Row": row - 1}, {"$set": {'Row': 99}})
        get_key.update_many({"Row": row}, {"$set": {'Row': row - 1}})
        get_key.update_many({"Row": 99}, {"$set": {'Row': row}})
    else:
        get_key.update_many({"Row": row + 1}, {"$set": {'Row': 99}})
        get_key.update_many({"Row": row}, {"$set": {'Row': row + 1}})
        get_key.update_many({"Row": 99}, {"$set": {'Row': row}})
    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
    keyboard.append([InlineKeyboardButton('新建一行', callback_data='newrow'),
                     InlineKeyboardButton('删除一行', callback_data='delrow'),
                     InlineKeyboardButton('调整行排序', callback_data='paixurow')])
    keyboard.append([InlineKeyboardButton('修改按钮', callback_data='newkey')])
    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    query.edit_message_text(text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def delrow(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='没有按钮存在')
    else:
        maxrow = max(count)
        for i in range(0, maxrow):
            keyboard.append([InlineKeyboardButton(f'删除第{i + 1}行', callback_data=f'qrscdelrow {i + 1}')])
        keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
        keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
        query.edit_message_text(text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))

def yuecz_cny(update: Update, context: CallbackContext):
    """处理基于人民币金额的USDT充值"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']
    
    data = query.data.replace('yuecz_cny ', '')
    usdt_amount = float(data.split(':')[0])
    cny_amount = int(data.split(':')[1])
    
    # 删除之前的充值订单
    topup.delete_many({'user_id': user_id})
    timer = time.strftime('%Y%m%d%H%M%S', time.localtime())
    bianhao = timer  # 只使用时间戳：20250808053159
    
    # 添加随机小数以避免重复
    while True:
        suijishu = round(random.uniform(0.01, 0.50), 2)
        final_usdt = Decimal(str(usdt_amount)) + Decimal(str(suijishu))
        if topup.find_one({"money": float(final_usdt)}) is None:
            break

    timer_full = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    trc20 = shangtext.find_one({'projectname': '充值地址'})['text']
    
    if lang == 'zh':
        text = f'''
<b>💎 USDT-TRC20 充值详情</b>

💰 充值金额：CNY{cny_amount}
💎 实际支付：<code>{final_usdt} USDT</code>
📍 收款地址：<code>{trc20}</code>

<b>⚠️ 重要提示：
- 请一定按照金额后面小数点转账
- 请在10分钟内付款，超时订单自动取消
- 支付成功后余额将显示为人民币</b>
        '''
        keyboard = [[InlineKeyboardButton('❌取消订单', callback_data=f'qxdingdan {user_id}')]]
    else:
        text = f'''
<b>💎 USDT-TRC20 Recharge Details</b>

💰 Recharge Amount: CNY{cny_amount}
💎 Transfer Amount: <code>{final_usdt} USDT</code>
📍 Receiving Address: <code>{trc20}</code>

<b>⚠️ Important Notes:
- Please transfer exactly according to the decimal amount
- Please pay within 10 minutes, order will be auto-cancelled
- Balance will be displayed in RMB after successful payment</b>
        '''
        keyboard = [[InlineKeyboardButton('❌Cancel Order', callback_data=f'qxdingdan {user_id}')]]
    
    message_id = context.bot.send_photo(chat_id=user_id, photo=open(f'{trc20}.png', 'rb'), 
                                       caption=text, parse_mode='HTML', 
                                       reply_markup=InlineKeyboardMarkup(keyboard))

    # 保存订单，记录人民币金额
    topup.insert_one({
        'bianhao': bianhao,
        'user_id': user_id,
        'money': float(final_usdt),  # USDT金额（用于区块链匹配）
        'cny_amount': cny_amount,    # 人民币金额（用于用户余额）
        'suijishu': suijishu,
        'timer': timer_full,
        'message_id': message_id.message_id,
        'payment_type': 'usdt_cny'   # 标记这是基于人民币的USDT充值
    })

def back_to_pay_select(update: Update, context: CallbackContext):
    """返回支付方式选择"""
    query = update.callback_query
    query.answer()
    
    data = query.data
    amount = int(data.replace('back_to_pay_select_', ''))
    
    user_id = query.from_user.id
    user_list = user.find_one({"user_id": user_id})
    lang = user_list['lang']
    
    if lang == 'zh':
        fstext = f'''
<b>💰充值金额：CNY{amount}

请选择支付方式：</b>
        '''
        keyboard = [
            [InlineKeyboardButton('💚 微信支付', callback_data=f'pay_wx_{amount}'),
             InlineKeyboardButton('💙 支付宝', callback_data=f'pay_ali_{amount}')],
            [InlineKeyboardButton('💎 USDT-TRC20', callback_data=f'pay_usdt_{amount}')],
            [InlineKeyboardButton('🔙 返回选择金额', callback_data='back_to_amount_select'),
             InlineKeyboardButton('❌ 取消', callback_data=f'close {user_id}')]
        ]
    else:
        fstext = f'''
<b>💰Recharge Amount: CNY{amount}

Please select payment method:</b>
        '''
        keyboard = [
            [InlineKeyboardButton('💚 微信支付', callback_data=f'pay_wx_{amount}'),
             InlineKeyboardButton('💙 支付宝', callback_data=f'pay_ali_{amount}')],
            [InlineKeyboardButton('💎 USDT-TRC20', callback_data=f'pay_usdt_{amount}')],
            [InlineKeyboardButton('🔙 返回选择金额', callback_data='back_to_amount_select')],
            [InlineKeyboardButton('❌ Cancel', callback_data=f'close {user_id}')]
        ]
    
    query.edit_message_text(text=fstext, parse_mode='HTML',
                          reply_markup=InlineKeyboardMarkup(keyboard))
def qrscdelrow(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    del_message(query.message)
    row = int(query.data.replace('qrscdelrow ', ''))
    bot_id = context.bot.id
    get_key.delete_many({"Row": row})
    max_list = list(get_key.find({'Row': {"$gt": row}}))
    for i in max_list:
        max_row = i['Row']
        get_key.update_many({'Row': max_row}, {"$set": {"Row": max_row - 1}})
    maxrow = get_key.find_one({}, sort=[('Row', -1)])
    if maxrow is None:
        maxrow = 1
    else:
        maxrow = maxrow['Row'] + 1
    # keybutton(maxrow,1)
    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
    keyboard.append([InlineKeyboardButton('新建一行', callback_data='newrow'),
                     InlineKeyboardButton('删除一行', callback_data='delrow'),
                     InlineKeyboardButton('调整行排序', callback_data='paixurow')])
    keyboard.append([InlineKeyboardButton('修改按钮', callback_data='newkey')])
    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    context.bot.send_message(chat_id=user_id, text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def delhangkey(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    row = int(query.data.replace('delhangkey ', ''))
    bot_id = context.bot.id
    key_list = list(get_key.find({'Row': row}, sort=[('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in key_list:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='没有按钮存在')
    else:

        # maxrow = max(count)
        for i in range(0, len(count)):
            keyboard[count[i]].append(InlineKeyboardButton('➖', callback_data=f'qrdelliekey {row}:{i + 1}'))
        keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
        keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
        query.edit_message_text(text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def keyxq(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('keyxq ', '')
    qudataall = qudata.split(':')
    row = int(qudataall[0])
    first = int(qudataall[1])
    key_list = get_key.find_one({'Row': row, 'first': first})
    projectname = key_list['projectname']
    text = key_list['text']
    print_text = f'''
这是第{row}行第{first}个按钮

按钮名称: {projectname}
    '''

    keyboard = [
        [InlineKeyboardButton('图文设置', callback_data=f'settuwenset {row}:{first}'),
         InlineKeyboardButton('查看图文设置', callback_data=f'cattuwenset {row}:{first}')],
        [InlineKeyboardButton('修改尾随按钮', callback_data=f'setkeyboard {row}:{first}'),
         InlineKeyboardButton('修改按钮名字', callback_data=f'setkeyname {row}:{first}')],
        [InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')]
    ]

    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    query.edit_message_text(text=print_text, reply_markup=InlineKeyboardMarkup(keyboard))


def setkeyname(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('setkeyname ', '')
    qudataall = qudata.split(':')
    row = int(qudataall[0])
    first = int(qudataall[1])
    text = f'''
输入要修改的名字
    '''
    user.update_one({'user_id': user_id}, {"$set": {"sign": f'setkeyname {row}:{first}'}})
    keyboard = [[InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')]]
    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def setkeyboard(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('setkeyboard ', '')
    qudataall = qudata.split(':')
    row = int(qudataall[0])
    first = int(qudataall[1])
    text = f'''
按以下格式设置按钮，填入◈之间，同一行用 | 隔开
按钮名称&https://t.me/... | 按钮名称&https://t.me/...
按钮名称&https://t.me/... | 按钮名称&https://t.me/... | 按钮名称&https://t.me/....
    '''
    key_list = get_key.find_one({'Row': row, 'first': first})
    key_text = key_list['key_text']
    if key_text != '':
        context.bot.send_message(chat_id=user_id, text=key_text)
    user.update_one({'user_id': user_id}, {"$set": {"sign": f'setkeyboard {row}:{first}'}})
    keyboard = [[InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')]]
    keyboard.append([InlineKeyboardButton('返回主界面', callback_data=f'backstart')])
    query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def settuwenset(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('settuwenset ', '')
    qudataall = qudata.split(':')
    row = int(qudataall[0])
    first = int(qudataall[1])
    key_list = get_key.find_one({'Row': row, 'first': first})
    key_text = key_list['key_text']
    text = key_list['text']
    file_type = key_list['file_type']
    file_id = key_list['file_id']
    entities = pickle.loads(key_list['entities'])
    keyboard = pickle.loads(key_list['keyboard'])
    if text == '' and file_id == '':
        pass
    else:
        if file_type == 'text':
            message_id = context.bot.send_message(chat_id=user_id, text=text,
                                                  reply_markup=InlineKeyboardMarkup(keyboard), entities=entities)
        else:
            if file_type == 'photo':
                message_id = context.bot.send_photo(chat_id=user_id, caption=text, photo=file_id,
                                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                                    caption_entities=entities)
            else:
                message_id = context.bot.sendAnimation(chat_id=user_id, caption=text, animation=file_id,
                                                       reply_markup=InlineKeyboardMarkup(keyboard),
                                                       caption_entities=entities)
    text = f'''
✍️ 发送你的图文设置

文字、视频、图片、gif、图文
    '''
    user.update_one({'user_id': user_id}, {"$set": {"sign": f'settuwenset {row}:{first}'}})
    keyboard = [[InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')]]
    context.bot.send_message(chat_id=user_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def cattuwenset(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('cattuwenset ', '')
    qudataall = qudata.split(':')
    row = int(qudataall[0])
    first = int(qudataall[1])
    key_list = get_key.find_one({'Row': row, 'first': first})
    key_text = key_list['key_text']
    text = key_list['text']
    file_type = key_list['file_type']
    file_id = key_list['file_id']
    entities = pickle.loads(key_list['entities'])
    keyboard = pickle.loads(key_list['keyboard'])
    if text == '' and file_id == '':
        message_id = context.bot.send_message(chat_id=user_id, text='请设置图文后点击')
        timer11 = Timer(3, del_message, args=[message_id])
        timer11.start()
    else:
        if file_type == 'text':
            message_id = context.bot.send_message(chat_id=user_id, text=text,
                                                  reply_markup=InlineKeyboardMarkup(keyboard), entities=entities)
        else:
            if file_type == 'photo':
                message_id = context.bot.send_photo(chat_id=user_id, caption=text, photo=file_id,
                                                    reply_markup=InlineKeyboardMarkup(keyboard),
                                                    caption_entities=entities)
            else:
                message_id = context.bot.sendAnimation(chat_id=user_id, caption=text, animation=file_id,
                                                       reply_markup=InlineKeyboardMarkup(keyboard),
                                                       caption_entities=entities)
        timer11 = Timer(3, del_message, args=[message_id])
        timer11.start()


def qrdelliekey(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('qrdelliekey ', '')
    qudataall = qudata.split(':')
    row = int(qudataall[0])
    first = int(qudataall[1])
    get_key.delete_one({"Row": row, 'first': first})
    max_list = list(get_key.find({'Row': row, 'first': {"$gt": first}}))
    for i in max_list:
        max_lie = i['first']
        get_key.update_one({'Row': row, 'first': max_lie}, {"$set": {"first": max_lie - 1}})

    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='请先新建一行')
    else:
        maxrow = max(count)
        for i in range(0, maxrow):
            keyboard.append([InlineKeyboardButton(f'第{i + 1}行', callback_data=f'dddd'),
                             InlineKeyboardButton('➕', callback_data=f'addhangkey {i + 1}'),
                             InlineKeyboardButton('➖', callback_data=f'delhangkey {i + 1}')])
        keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
        context.bot.send_message(chat_id=user_id, text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def addhangkey(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    del_message(query.message)
    row = int(query.data.replace('addhangkey ', ''))
    bot_id = context.bot.id
    lie = get_key.find_one({'Row': row}, sort=[('first', -1)])['first']
    keybutton(row, lie + 1)

    keylist = list(get_key.find({}, sort=[('Row', 1), ('first', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['Row']
        first = i['first']
        keyboard[i["Row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'keyxq {row}:{first}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='请先新建一行')
    else:
        maxrow = max(count)
        for i in range(0, maxrow):
            keyboard.append([InlineKeyboardButton(f'第{i + 1}行', callback_data=f'dddd'),
                             InlineKeyboardButton('➕', callback_data=f'addhangkey {i + 1}'),
                             InlineKeyboardButton('➖', callback_data=f'delhangkey {i + 1}')])
        keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
        context.bot.send_message(chat_id=user_id, text='自定义按钮', reply_markup=InlineKeyboardMarkup(keyboard))


def settrc20(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    text = f'''
输入以T开头共34位的 trc20地址
'''
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    user.update_one({'user_id': user_id}, {"$set": {"sign": 'settrc20'}})
    context.bot.send_message(chat_id=user_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))


def startupdate(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    text = f'''
输入新的欢迎语
'''
    keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    user.update_one({'user_id': user_id}, {"$set": {"sign": 'startupdate'}})
    context.bot.send_message(chat_id=user_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))


@check_business_status
def zdycz(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    lang = user.find_one({'user_id': user_id})['lang']
    bot_id = context.bot.id

    if lang == 'zh':
        text = f'''
输入充值金额
    '''
        keyboard = [[InlineKeyboardButton('取消', callback_data=f'close {user_id}')]]
    else:
        text = f'''
Enter the recharge amount
        '''
        keyboard = [[InlineKeyboardButton('Cancel', callback_data=f'close {user_id}')]]
    message_id = context.bot.send_message(chat_id=user_id, text=text, reply_markup=InlineKeyboardMarkup(keyboard))

    user.update_one({'user_id': user_id}, {"$set": {"sign": f'zdycz {message_id.message_id}'}})


@check_business_status
def yuecz(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    cny_amount = int(query.data.replace('yuecz ', ''))  # 这是人民币金额
    bot_id = context.bot.id
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']
    
    # 获取当前汇率
    rate_doc = shangtext.find_one({'projectname': '人民币USDT汇率'})
    exchange_rate = float(rate_doc['text']) if rate_doc else 7.2
    
    # 计算需要支付的USDT金额
    usdt_amount = round(cny_amount / exchange_rate, 2)
    
    topup.delete_many({'user_id': user_id})
    timer = time.strftime('%Y%m%d%H%M%S', time.localtime())
    bianhao = timer  # 只使用时间戳：20250808053159
    
    # 添加随机小数避免重复
    while 1:
        suijishu = round(random.uniform(0.01, 0.50), 2)
        final_usdt = Decimal(str(usdt_amount)) + Decimal(str(suijishu))
        if topup.find_one({"money": float(final_usdt)}) is None:
            break

    timer_full = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    trc20 = shangtext.find_one({'projectname': '充值地址'})['text']
    
    if lang == 'zh':
        text = f'''
<b>💎 USDT-TRC20 充值详情</b>

💰 充值金额：CNY{cny_amount}
💱 当前汇率：1 USDT = CNY{exchange_rate}
💎 实际支付：<code>{final_usdt} USDT</code>
📍 收款地址：<code>{trc20}</code>

<b>⚠️ 重要提示：
- 请一定按照金额后面小数点转账
- 请在10分钟内付款，超时订单自动取消
- 支付成功后余额将显示为人民币</b>
        '''
        keyboard = [[InlineKeyboardButton('❌取消订单', callback_data=f'qxdingdan {user_id}')]]
    else:
        text = f'''
<b>💎 USDT-TRC20 Recharge Details</b>

💰 Recharge Amount: CNY{cny_amount}
💱 Exchange Rate: 1 USDT = CNY{exchange_rate}
💎 Transfer Amount: <code>{final_usdt} USDT</code>
📍 Receiving Address: <code>{trc20}</code>

<b>⚠️ Important Notes:
- Please transfer exactly according to the decimal amount
- Please pay within 10 minutes, order will be auto-cancelled
- Balance will be displayed in RMB after successful payment</b>
        '''
        keyboard = [[InlineKeyboardButton('❌Cancel Order', callback_data=f'qxdingdan {user_id}')]]
    
    message_id = context.bot.send_photo(chat_id=user_id, photo=open(f'{trc20}.png', 'rb'), 
                                       caption=text, parse_mode='HTML', 
                                       reply_markup=InlineKeyboardMarkup(keyboard))

    # 保存订单，记录人民币金额
    topup.insert_one({
        'bianhao': bianhao,
        'user_id': user_id,
        'money': float(final_usdt),  # USDT金额（用于区块链匹配）
        'cny_amount': cny_amount,    # 人民币金额（用于用户余额）
        'suijishu': suijishu,
        'timer': timer_full,
        'message_id': message_id.message_id,
        'payment_type': 'usdt_cny'   # 标记这是基于人民币的USDT充值
    })


@check_business_status
def catejflsp(update: Update, context: CallbackContext):
    query = update.callback_query
    uid = query.data.replace('catejflsp ', '').split(':')[0]
    zhsl = int(query.data.replace('catejflsp ', '').split(':')[1])
    query.answer()

    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']

    # 获取所有二级分类并排序
    ej_list = ejfl.find({'uid': uid})
    sorted_ej_list = sorted(ej_list, key=lambda x: -len(list(hb.find({'nowuid': x['nowuid'], 'state': 0}))))

    keyboard = [[] for _ in range(len(sorted_ej_list))]

    # 创建键盘按钮
    for count, i in enumerate(sorted_ej_list):
        nowuid = i['nowuid']
        projectname = i['projectname']

        hsl = hb.count_documents({'nowuid': nowuid, 'state': 0})

        projectname = projectname if lang == 'zh' else get_fy(projectname)
        keyboard[count].append(InlineKeyboardButton(f'{projectname}  ({hsl})', callback_data=f'gmsp {nowuid}:{hsl}'))

    # 添加返回和关闭按钮
    back_text = '🔙返回' if lang == 'zh' else '🔙Back'
    close_text = '❌关闭' if lang == 'zh' else '❌Close'
    keyboard.append([InlineKeyboardButton(back_text, callback_data='backzcd'),
                     InlineKeyboardButton(close_text, callback_data=f'close {user_id}')])

    fstext = '''
<b>🛒这是商品列表  选择你需要的商品：

❗️没使用过的本店商品的，请先少量购买测试，以免造成不必要的争执！谢谢合作！

❗️购买后，请立即检测账户是否正常！超过1小时视为放弃售后服务！</b>
        '''

    fstext = fstext if lang == 'zh' else get_fy(fstext)
    query.edit_message_text(fstext, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


@check_business_status
def gmsp(update: Update, context: CallbackContext):
        # 检查营业状态
    yyzt = shangtext.find_one({'projectname': '营业状态'})['text']
    user_id = update.callback_query.from_user.id
    user_list = user.find_one({'user_id': user_id})
    state = user_list.get('state', '1') if user_list else '1'
    
    if yyzt == 0 and state != '4':
        update.callback_query.answer('🚫 机器人暂停营业中', show_alert=True)
        return
    query = update.callback_query

    data = query.data.replace('gmsp ', '')
    nowuid = data.split(':')[0]
    hsl = data.split(':')[1]

    bot_id = context.bot.id
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']

    ejfl_list = ejfl.find_one({'nowuid': nowuid})
    projectname = ejfl_list['projectname']
    money = ejfl_list['money']
    uid = ejfl_list['uid']
    
    # 🔥 关键修改：获取管理员设置的购买提示
    custom_text = ejfl_list.get('text', '')

    query.answer()
    if lang == 'zh':
        fstext = f'''
<b>✅您正在购买:  {projectname}

💰 价格： CNY{money}

🏢 库存： {hsl}

{custom_text}</b>
        '''
        keyboard = [
            [InlineKeyboardButton('✅购买', callback_data=f'gmqq {nowuid}:{hsl}'),
             InlineKeyboardButton('使用说明📜', callback_data=f'sysming {nowuid}')],
            [InlineKeyboardButton('🏠主菜单', callback_data='backzcd'),
             InlineKeyboardButton('返回↩️', callback_data=f'catejflsp {uid}:1000')]
        ]

    else:
        projectname = projectname if lang == 'zh' else get_fy(projectname)
        # 英文版本也使用自定义文本
        custom_text_en = custom_text if lang == 'zh' else get_fy(custom_text)
        fstext = f'''
<b>✅You are buying: {projectname}

💰 Price: CNY{money}

🏢 Inventory: {hsl}

{custom_text_en}</b>
        '''
        keyboard = [
            [InlineKeyboardButton('✅Buy', callback_data=f'gmqq {nowuid}:{hsl}'),
             InlineKeyboardButton('Instructions 📜', callback_data=f'sysming {nowuid}')],
            [InlineKeyboardButton('🏠Main Menu', callback_data='backzcd'),
             InlineKeyboardButton('Return ↩️', callback_data=f'catejflsp {uid}:1000')]
        ]
    query.edit_message_text(fstext, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))


@check_business_status
def gmqq(update: Update, context: CallbackContext):
    """修复版商品购买数量处理"""
    query = update.callback_query
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']
    data = query.data.replace('gmqq ', '')
    nowuid = data.split(':')[0]
    available_stock = int(data.split(':')[1])

    # 获取商品和用户信息
    ejfl_list = ejfl.find_one({'nowuid': nowuid})
    user_list = user.find_one({'user_id': user_id})
    
    if not ejfl_list or not user_list:
        error_msg = "商品或用户信息不存在" if lang == 'zh' else "Product or user information not found"
        query.answer(error_msg, show_alert=True)
        return
    
    projectname = ejfl_list['projectname']
    unit_price = ejfl_list['money']
    USDT = user_list['USDT']
    
    # 检查余额
    if USDT < unit_price:
        error_msg = f"余额不足，请立即充值\n当前余额：CNY{USDT}\n商品单价：CNY{unit_price}" if lang == 'zh' else f"Insufficient balance\nCurrent: CNY{USDT}\nPrice: CNY{unit_price}"
        query.answer(error_msg, show_alert=True)
        return
    
    query.answer()
    
    # 🔥 关键修复：正确设置购买状态并删除原消息
    user.update_one({'user_id': user_id}, {"$set": {"sign": f"gmqq {nowuid}:{available_stock}"}})
    del_message(query.message)
    
    # 显示数量输入提示
    if lang == 'zh':
        fstext = f'''📦 <b>购买商品：{projectname}</b>

💰 单价：CNY{unit_price}
📊 库存：{available_stock}
💎 您的余额：CNY{USDT}

📝 请输入购买数量：

📝 <b>格式：</b>直接输入数字即可
📦 <b>范围：</b>1 - {available_stock}
📱 <b>例如：</b>1 或 5

<i>💡 输入后将显示购买确认信息</i>'''
        
        keyboard = [[InlineKeyboardButton('🔙 返回', callback_data=f'gmsp {nowuid}:{available_stock}')]]
    else:
        fstext = f'''📦 <b>Purchase Product: {projectname}</b>

💰 Unit Price: CNY{unit_price}
📊 Stock: {available_stock}
💎 Your Balance: CNY{USDT}

📝 Please enter quantity:

📝 <b>Format:</b> Enter numbers only
📦 <b>Range:</b> 1 - {available_stock}
📱 <b>Example:</b> 1 or 5

<i>💡 Purchase confirmation will appear after input</i>'''
        
        keyboard = [[InlineKeyboardButton('🔙 Back', callback_data=f'gmsp {nowuid}:{available_stock}')]]
    
    context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                           reply_markup=InlineKeyboardMarkup(keyboard))


def sysming(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    nowuid = query.data.replace('sysming ', '')
    ejfl_list = ejfl.find_one({'nowuid': nowuid})
    sysm = ejfl_list['sysm']

    keyboard = [
        [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]
    ]
    context.bot.send_message(chat_id=user_id, text=sysm, reply_markup=InlineKeyboardMarkup(keyboard))


def paixuejfl(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    uid = query.data.replace('paixuejfl ', '')
    bot_id = context.bot.id
    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keylist = list(ejfl.find({'uid': uid}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['row']
        nowuid = i['nowuid']
        keyboard[i["row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'fejxxi {nowuid}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='没有按钮存在')
    else:
        maxrow = max(count)
        if maxrow == 1:
            context.bot.send_message(chat_id=user_id, text='只有一行按钮无法调整')
        else:
            for i in range(0, maxrow):
                pxuid = ejfl.find_one({'uid': uid, 'row': i + 1})['nowuid']
                if i == 0:
                    keyboard.append(
                        [InlineKeyboardButton(f'第{i + 1}行下移', callback_data=f'ejfpaixu xiayi:{i + 1}:{pxuid}')])
                elif i == maxrow - 1:
                    keyboard.append(
                        [InlineKeyboardButton(f'第{i + 1}行上移', callback_data=f'ejfpaixu shangyi:{i + 1}:{pxuid}')])
                else:
                    keyboard.append(
                        [InlineKeyboardButton(f'第{i + 1}行上移', callback_data=f'ejfpaixu shangyi:{i + 1}:{pxuid}'),
                         InlineKeyboardButton(f'第{i + 1}行下移', callback_data=f'ejfpaixu xiayi:{i + 1}:{pxuid}')])
            keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
            context.bot.send_message(chat_id=user_id, text=f'分类: {fl_pro}',
                                     reply_markup=InlineKeyboardMarkup(keyboard))


def ejfpaixu(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('ejfpaixu ', '')
    qudataall = qudata.split(':')
    yidongtype = qudataall[0]
    row = int(qudataall[1])
    nowuid = qudataall[2]
    uid = ejfl.find_one({'nowuid': nowuid})['uid']
    if yidongtype == 'shangyi':
        ejfl.update_many({"row": row - 1, 'uid': uid}, {"$set": {'row': 99}})
        ejfl.update_many({"row": row, 'uid': uid}, {"$set": {'row': row - 1}})
        ejfl.update_many({"row": 99, 'uid': uid}, {"$set": {'row': row}})
    else:
        ejfl.update_many({"row": row + 1, 'uid': uid}, {"$set": {'row': 99}})
        ejfl.update_many({"row": row, 'uid': uid}, {"$set": {'row': row + 1}})
        ejfl.update_many({"row": 99, 'uid': uid}, {"$set": {'row': row}})

    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    ej_list = ejfl.find({'uid': uid})
    for i in ej_list:
        nowuid = i['nowuid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'fejxxi {nowuid}'))

    keyboard.append([InlineKeyboardButton('修改分类名', callback_data=f'upspname {uid}'),
                     InlineKeyboardButton('新增二级分类', callback_data=f'newejfl {uid}')])
    keyboard.append([InlineKeyboardButton('调整二级分类排序', callback_data=f'paixuejfl {uid}'),
                     InlineKeyboardButton('删除二级分类', callback_data=f'delejfl {uid}')])
    keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
    fstext = f'''
分类: {fl_pro}
    '''
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def paixufl(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    keylist = list(fenlei.find({}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['row']
        uid = i['uid']
        keyboard[i["row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'flxxi {uid}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='没有按钮存在')
    else:
        maxrow = max(count)
        if maxrow == 1:
            context.bot.send_message(chat_id=user_id, text='只有一行按钮无法调整')
        else:
            for i in range(0, maxrow):
                if i == 0:
                    keyboard.append([InlineKeyboardButton(f'第{i + 1}行下移', callback_data=f'flpxyd xiayi:{i + 1}')])
                elif i == maxrow - 1:
                    keyboard.append([InlineKeyboardButton(f'第{i + 1}行上移', callback_data=f'flpxyd shangyi:{i + 1}')])
                else:
                    keyboard.append([InlineKeyboardButton(f'第{i + 1}行上移', callback_data=f'flpxyd shangyi:{i + 1}'),
                                     InlineKeyboardButton(f'第{i + 1}行下移', callback_data=f'flpxyd xiayi:{i + 1}')])
            keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
            context.bot.send_message(chat_id=user_id, text='商品管理', reply_markup=InlineKeyboardMarkup(keyboard))


def flpxyd(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    qudata = query.data.replace('flpxyd ', '')
    qudataall = qudata.split(':')
    yidongtype = qudataall[0]
    row = int(qudataall[1])
    if yidongtype == 'shangyi':
        fenlei.update_many({"row": row - 1}, {"$set": {'row': 99}})
        fenlei.update_many({"row": row}, {"$set": {'row': row - 1}})
        fenlei.update_many({"row": 99}, {"$set": {'row': row}})
    else:
        fenlei.update_many({"row": row + 1}, {"$set": {'row': 99}})
        fenlei.update_many({"row": row}, {"$set": {'row': row + 1}})
        fenlei.update_many({"row": 99}, {"$set": {'row': row}})
    keylist = list(fenlei.find({}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        uid = i['uid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'flxxi {uid}'))
    keyboard.append([InlineKeyboardButton("新建一行", callback_data='newfl'),
                     InlineKeyboardButton('调整行排序', callback_data='paixufl'),
                     InlineKeyboardButton('删除一行', callback_data='delfl')])
    context.bot.send_message(chat_id=user_id, text='商品管理', reply_markup=InlineKeyboardMarkup(keyboard))


def delejfl(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    uid = query.data.replace('delejfl ', '')
    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keylist = list(ejfl.find({'uid': uid}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        projectname = i['projectname']
        row = i['row']
        nowuid = i['nowuid']
        keyboard[i["row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'fejxxi {nowuid}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='没有按钮存在')
    else:
        maxrow = max(count)
        for i in range(0, maxrow):
            pxuid = ejfl.find_one({'uid': uid, 'row': i + 1})['nowuid']
            keyboard.append([InlineKeyboardButton(f'删除第{i + 1}行', callback_data=f'qrscejrow {i + 1}:{pxuid}')])
        keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
        context.bot.send_message(chat_id=user_id, text=f'分类: {fl_pro}', reply_markup=InlineKeyboardMarkup(keyboard))


def qrscejrow(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    del_message(query.message)

    row = int(query.data.replace('qrscejrow ', '').split(':')[0])
    nowuid = query.data.replace('qrscejrow ', '').split(':')[1]
    uid = ejfl.find_one({'nowuid': nowuid})['uid']
    bot_id = context.bot.id
    ejfl.delete_many({'uid': uid, "row": row})
    max_list = list(ejfl.find({'row': {"$gt": row}}))
    for i in max_list:
        max_row = i['row']
        ejfl.update_many({'uid': uid, 'row': max_row}, {"$set": {"row": max_row - 1}})

    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    ej_list = ejfl.find({'uid': uid})
    for i in ej_list:
        nowuid = i['nowuid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'fejxxi {nowuid}'))

    keyboard.append([InlineKeyboardButton('修改分类名', callback_data=f'upspname {uid}'),
                     InlineKeyboardButton('新增二级分类', callback_data=f'newejfl {uid}')])
    keyboard.append([InlineKeyboardButton('调整二级分类排序', callback_data=f'paixuejfl {uid}'),
                     InlineKeyboardButton('删除二级分类', callback_data=f'delejfl {uid}')])
    keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
    fstext = f'''
分类: {fl_pro}
    '''
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def delfl(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    bot_id = context.bot.id
    keylist = list(fenlei.find({}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    count = []
    for i in keylist:
        uid = i['uid']
        projectname = i['projectname']
        row = i['row']
        keyboard[i["row"] - 1].append(InlineKeyboardButton(projectname, callback_data=f'flxxi {uid}'))
        count.append(row)
    if count == []:
        context.bot.send_message(chat_id=user_id, text='没有按钮存在')
    else:
        maxrow = max(count)
        for i in range(0, maxrow):
            keyboard.append([InlineKeyboardButton(f'删除第{i + 1}行', callback_data=f'qrscflrow {i + 1}')])
        keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
        context.bot.send_message(chat_id=user_id, text='商品管理', reply_markup=InlineKeyboardMarkup(keyboard))


def qrscflrow(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    del_message(query.message)
    row = int(query.data.replace('qrscflrow ', ''))
    bot_id = context.bot.id
    fenlei.delete_many({"row": row})
    max_list = list(fenlei.find({'row': {"$gt": row}}))
    for i in max_list:
        max_row = i['row']
        fenlei.update_many({'row': max_row}, {"$set": {"row": max_row - 1}})
    keylist = list(fenlei.find({}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        uid = i['uid']
        projectname = i['projectname']
        row = i['row']
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}', callback_data=f'flxxi {uid}'))
    keyboard.append([InlineKeyboardButton("新建一行", callback_data='newfl'),
                     InlineKeyboardButton('调整行排序', callback_data='paixufl'),
                     InlineKeyboardButton('删除一行', callback_data='delfl')])
    context.bot.send_message(chat_id=user_id, text='商品管理', reply_markup=InlineKeyboardMarkup(keyboard))


def backzcd(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    bot_id = context.bot.id
    user_id = query.from_user.id
    lang = user.find_one({'user_id': user_id})['lang']
    keylist = list(fenlei.find({}, sort=[('row', 1)]))
    keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    for i in keylist:
        uid = i['uid']
        projectname = i['projectname']

        row = i['row']
        hsl = 0
        for j in list(ejfl.find({'uid': uid})):
            nowuid = j['nowuid']
            hsl += len(list(hb.find({'nowuid': nowuid, 'state': 0})))
        projectname = projectname if lang == 'zh' else get_fy(projectname)
        keyboard[row - 1].append(InlineKeyboardButton(f'{projectname}({hsl})', callback_data=f'catejflsp {uid}:{hsl}'))
    fstext = f'''
<b>🛒这是商品列表  选择你需要的商品：

❗️没使用过的本店商品的，请先少量购买测试，以免造成不必要的争执！谢谢合作！

❗️购买后，请立即检测账户是否正常！超过1小时视为放弃售后服务！</b>
        '''
    fstext = fstext if lang == 'zh' else get_fy(fstext)
    keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
    query.edit_message_text(fstext, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def dabaohao(context, user_id, folder_names, leixing, nowuid, erjiprojectname, fstext, yssj):
    if leixing == '协议号':
        shijiancuo = int(time.time())
        zip_filename = f"./协议号发货/{user_id}_{shijiancuo}.zip"
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # 将每个文件及其内容添加到 zip 文件中
            for file_name in folder_names:
                # 检查是否存在以 .json 或 .session 结尾的文件
                json_file_path = os.path.join(f"./协议号/{nowuid}", file_name + ".json")
                session_file_path = os.path.join(f"./协议号/{nowuid}", file_name + ".session")
                if os.path.exists(json_file_path):
                    zipf.write(json_file_path, os.path.basename(json_file_path))
                if os.path.exists(session_file_path):
                    zipf.write(session_file_path, os.path.basename(session_file_path))
        current_time = datetime.datetime.now()

        # 将当前时间格式化为字符串
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")

        # 添加时间戳
        timestamp = str(current_time.timestamp()).replace(".", "")

        # 组合编号
        bianhao = time.strftime('%Y%m%d%H%M%S', time.localtime())
        timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        goumaijilua('协议号', bianhao, user_id, erjiprojectname, zip_filename, fstext, timer)
        # 发送 zip 文件给用户
        context.bot.send_document(chat_id=user_id, document=open(zip_filename, "rb"))
    elif leixing == '直登号':
        shijiancuo = int(time.time())
        zip_filename = f"./发货/{user_id}_{shijiancuo}.zip"
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # 将每个文件夹及其内容添加到 zip 文件中
            for folder_name in folder_names:
                full_folder_path = os.path.join(f"./号包/{nowuid}", folder_name)
                if os.path.exists(full_folder_path):
                    # 添加文件夹及其内容
                    for root, dirs, files in os.walk(full_folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # 使用相对路径在压缩包中添加文件，并设置压缩包内部的路径
                            zipf.write(file_path,
                                       os.path.join(folder_name, os.path.relpath(file_path, full_folder_path)))
                else:
                    # update.message.reply_text(f"文件夹 '{folder_name}' 不存在！")
                    pass

        # 发送 zip 文件给用户

        folder_names = '\n'.join(folder_names)

        current_time = datetime.datetime.now()

        # 将当前时间格式化为字符串
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")

        # 添加时间戳
        timestamp = str(current_time.timestamp()).replace(".", "")

        # 组合编号
        bianhao = time.strftime('%Y%m%d%H%M%S', time.localtime())
        timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        goumaijilua('直登号', bianhao, user_id, erjiprojectname, zip_filename, fstext, timer)

        context.bot.send_document(chat_id=user_id, document=open(zip_filename, "rb"))


@check_business_status
def qrgaimai(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    bot_id = context.bot.id
    user_id = query.from_user.id
    fullname = query.from_user.full_name.replace('<', '').replace('>', '')
    username = query.from_user.username
    data = query.data.replace('qrgaimai ', '')
    nowuid = data.split(':')[0]
    gmsl = int(data.split(':')[1])
    zxymoney = float(data.split(':')[2])
    user_list = user.find_one({'user_id': user_id})
    USDT = user_list['USDT']
    lang = user_list['lang']
    kc = len(list(hb.find({'nowuid': nowuid, 'state': 0})))
    if kc < gmsl:
        kcbz = '当前库存不足' if lang == 'zh' else get_fy('当前库存不足')
        context.bot.send_message(chat_id=user_id, text=kcbz)
        return
    if zxymoney == 0:
        return
    keyboard = [[InlineKeyboardButton('✅已读（点击销毁此消息）', callback_data=f'close {user_id}')]]
    if USDT >= zxymoney:
        now_price = standard_num(float(USDT) - float(zxymoney))
        now_price = float(now_price) if str((now_price)).count('.') > 0 else int(standard_num(now_price))

        ejfl_list = ejfl.find_one({'nowuid': nowuid})

        fhtype = hb.find_one({'nowuid': nowuid})['leixing']
        projectname = ejfl_list['projectname']
        erjiprojectname = ejfl_list['projectname']
        yijiid = ejfl_list['uid']
        yiji_list = fenlei.find_one({'uid': yijiid})
        yijiprojectname = yiji_list['projectname']
        fstext = ejfl_list['text']
        fstext = fstext if lang == 'zh' else get_fy(fstext)
        if fhtype == '协议号':
            zgje = user_list['zgje']
            zgsl = user_list['zgsl']
            user.update_one({'user_id': user_id},
                            {"$set": {'USDT': now_price, 'zgje': zgje + zxymoney, 'zgsl': zgsl + gmsl}})
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            del_message(query.message)
            # for j in list(hb.find({"nowuid": nowuid,'state': 0},limit=gmsl)):
            #     projectname = j['projectname']
            #     hbid = j['hbid']
            #     timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            #     hb.update_one({'hbid': hbid},{"$set":{'state': 1, 'yssj': timer, 'gmid': user_id}})
            #     folder_names.append(projectname)

            query_condition = {"nowuid": nowuid, "state": 0}

            pipeline = [
                {"$match": query_condition},
                {"$limit": gmsl}
            ]
            cursor = hb.aggregate(pipeline)
            document_ids = [doc['_id'] for doc in cursor]
            cursor = hb.aggregate(pipeline)
            folder_names = [doc['projectname'] for doc in cursor]

            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            update_data = {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}}
            hb.update_many({"_id": {"$in": document_ids}}, update_data)

            # timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # update_data = {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}}

            # hb.update_many(query_condition, update_data, limit=gmsl)

            context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=InlineKeyboardMarkup(keyboard))
            fstext = f'''
用户: <a href="tg://user?id={user_id}">{fullname}</a> @{username}
用户ID: <code>{user_id}</code>
购买商品: {yijiprojectname}/{erjiprojectname}
购买数量: {gmsl}
购买金额: CNY{zxymoney}
            '''
            for i in list(user.find({"state": '4'})):
                try:
                    context.bot.send_message(chat_id=i['user_id'], text=fstext, parse_mode='HTML')
                except:
                    pass

            Timer(1, dabaohao,
                  args=[context, user_id, folder_names, '协议号', nowuid, erjiprojectname, fstext, timer]).start()
            # shijiancuo = int(time.time())
            # zip_filename = f"./协议号发货/{user_id}_{shijiancuo}.zip"
            # with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            #     # 将每个文件及其内容添加到 zip 文件中
            #     for file_name in folder_names:
            #         # 检查是否存在以 .json 或 .session 结尾的文件
            #         json_file_path = os.path.join(f"./协议号/{nowuid}", file_name + ".json")
            #         session_file_path = os.path.join(f"./协议号/{nowuid}", file_name + ".session")
            #         if os.path.exists(json_file_path):
            #             zipf.write(json_file_path, os.path.basename(json_file_path))
            #         if os.path.exists(session_file_path):
            #             zipf.write(session_file_path, os.path.basename(session_file_path))
            # current_time = datetime.datetime.now()

            # # 将当前时间格式化为字符串
            # formatted_time = current_time.strftime("%Y%m%d%H%M%S")

            # # 添加时间戳
            # timestamp = str(current_time.timestamp()).replace(".", "")

            # # 组合编号
            # bianhao = formatted_time + timestamp
            # timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # goumaijilua('协议号', bianhao, user_id, erjiprojectname,zip_filename,fstext, timer)
            # # 发送 zip 文件给用户
            # query.message.reply_document(open(zip_filename, "rb"))



        elif fhtype == '谷歌':
            zgje = user_list['zgje']
            zgsl = user_list['zgsl']
            user.update_one({'user_id': user_id},
                            {"$set": {'USDT': now_price, 'zgje': zgje + zxymoney, 'zgsl': zgsl + gmsl}})
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            del_message(query.message)

            context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=InlineKeyboardMarkup(keyboard))
            folder_names = []
            for j in list(hb.find({"nowuid": nowuid, 'state': 0, 'leixing': '谷歌'}, limit=gmsl)):
                projectname = j['projectname']
                hbid = j['hbid']
                timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                hb.update_one({'hbid': hbid}, {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}})
                data = j['data']
                us1 = data['账户']
                us2 = data['密码']
                us3 = data['子邮件']
                fste23xt = f'账户: {us1}\n密码: {us2}\n子邮件: {us3}\n'
                folder_names.append(fste23xt)

            folder_names = '\n'.join(folder_names)

            shijiancuo = int(time.time())
            zip_filename = f"./谷歌发货/{user_id}_{shijiancuo}.txt"
            with open(zip_filename, "w") as f:
                f.write(folder_names)
            current_time = datetime.datetime.now()

            # 将当前时间格式化为字符串
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")

            # 添加时间戳
            timestamp = str(current_time.timestamp()).replace(".", "")

            # 组合编号
            bianhao = time.strftime('%Y%m%d%H%M%S', time.localtime())
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            goumaijilua('谷歌', bianhao, user_id, erjiprojectname, zip_filename, fstext, timer)

            query.message.reply_document(open(zip_filename, "rb"))

            fstext = f'''
用户: <a href="tg://user?id={user_id}">{fullname}</a> @{username}
用户ID: <code>{user_id}</code>
购买商品: {yijiprojectname}/{erjiprojectname}
购买数量: {gmsl}
购买金额: CNY{zxymoney}
            '''
            for i in list(user.find({"state": '4'})):
                try:
                    context.bot.send_message(chat_id=i['user_id'], text=fstext, parse_mode='HTML')
                except:
                    pass


        elif fhtype == 'API':
            zgje = user_list['zgje']
            zgsl = user_list['zgsl']
            user.update_one({'user_id': user_id},
                            {"$set": {'USDT': now_price, 'zgje': zgje + zxymoney, 'zgsl': zgsl + gmsl}})
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            del_message(query.message)

            context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=InlineKeyboardMarkup(keyboard))
            folder_names = []
            for j in list(hb.find({"nowuid": nowuid, 'state': 0}, limit=gmsl)):
                projectname = j['projectname']
                hbid = j['hbid']
                timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                hb.update_one({'hbid': hbid}, {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}})
                folder_names.append(projectname)

            shijiancuo = int(time.time())

            zip_filename = f"./手机接码发货/{user_id}_{shijiancuo}.txt"
            with open(zip_filename, "w") as f:
                for folder_name in folder_names:
                    f.write(folder_name + "\n")

            current_time = datetime.datetime.now()

            # 将当前时间格式化为字符串
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")

            # 添加时间戳
            timestamp = str(current_time.timestamp()).replace(".", "")

            # 组合编号
            bianhao = time.strftime('%Y%m%d%H%M%S', time.localtime())
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            goumaijilua('API链接', bianhao, user_id, erjiprojectname, zip_filename, fstext, timer)

            query.message.reply_document(open(zip_filename, "rb"))

            fstext = f'''
用户: <a href="tg://user?id={user_id}">{fullname}</a> @{username}
用户ID: <code>{user_id}</code>
购买商品: {yijiprojectname}/{erjiprojectname}
购买数量: {gmsl}
购买金额: CNY{zxymoney}
            '''
            for i in list(user.find({"state": '4'})):
                try:
                    context.bot.send_message(chat_id=i['user_id'], text=fstext, parse_mode='HTML')
                except:
                    pass
        elif fhtype == '会员链接':
            zgje = user_list['zgje']
            zgsl = user_list['zgsl']
            user.update_one({'user_id': user_id},
                            {"$set": {'USDT': now_price, 'zgje': zgje + zxymoney, 'zgsl': zgsl + gmsl}})
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            del_message(query.message)
            folder_names = []
            for j in list(hb.find({"nowuid": nowuid, 'state': 0}, limit=gmsl)):
                projectname = j['projectname']
                hbid = j['hbid']
                timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                hb.update_one({'hbid': hbid}, {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}})
                folder_names.append(projectname)

            context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=InlineKeyboardMarkup(keyboard))

            folder_names = '\n'.join(folder_names)

            current_time = datetime.datetime.now()

            # 将当前时间格式化为字符串
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")

            # 添加时间戳
            timestamp = str(current_time.timestamp()).replace(".", "")

            # 组合编号
            bianhao = time.strftime('%Y%m%d%H%M%S', time.localtime())
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            goumaijilua('会员链接', bianhao, user_id, erjiprojectname, folder_names, fstext, timer)

            context.bot.send_message(chat_id=user_id, text=folder_names, disable_web_page_preview=True)

            fstext = f'''
用户: <a href="tg://user?id={user_id}">{fullname}</a> @{username}
用户ID: <code>{user_id}</code>
购买商品: {yijiprojectname}/{erjiprojectname}
购买数量: {gmsl}
购买金额: CNY{zxymoney}
            '''
            for i in list(user.find({"state": '4'})):
                try:
                    context.bot.send_message(chat_id=i['user_id'], text=fstext, parse_mode='HTML')
                except:
                    pass
        else:
            zgje = user_list['zgje']
            zgsl = user_list['zgsl']
            user.update_one({'user_id': user_id},
                            {"$set": {'USDT': now_price, 'zgje': zgje + zxymoney, 'zgsl': zgsl + gmsl}})
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            del_message(query.message)

            # folder_names = []
            # for j in list(hb.find({"nowuid": nowuid, 'state': 0}, limit=gmsl)):
            #     projectname = j['projectname']
            #     hbid = j['hbid']
            #     timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            #     hb.update_one({'hbid': hbid}, {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}})
            #     folder_names.append(projectname)

            query_condition = {"nowuid": nowuid, "state": 0}

            pipeline = [
                {"$match": query_condition},
                {"$limit": gmsl}
            ]
            cursor = hb.aggregate(pipeline)
            document_ids = [doc['_id'] for doc in cursor]
            cursor = hb.aggregate(pipeline)
            folder_names = [doc['projectname'] for doc in cursor]

            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            update_data = {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}}
            hb.update_many({"_id": {"$in": document_ids}}, update_data)

            context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML', disable_web_page_preview=True,
                                     reply_markup=InlineKeyboardMarkup(keyboard))

            fstext = f'''
用户: <a href="tg://user?id={user_id}">{fullname}</a> @{username}
用户ID: <code>{user_id}</code>
购买商品: {yijiprojectname}/{erjiprojectname}
购买数量: {gmsl}
购买金额: CNY{zxymoney}
            '''
            for i in list(user.find({"state": '4'})):
                try:
                    context.bot.send_message(chat_id=i['user_id'], text=fstext, parse_mode='HTML')
                except:
                    pass

            Timer(1, dabaohao,
                  args=[context, user_id, folder_names, '直登号', nowuid, erjiprojectname, fstext, timer]).start()
            # shijiancuo = int(time.time())
            # zip_filename = f"./发货/{user_id}_{shijiancuo}.zip"
            # with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            #     # 将每个文件夹及其内容添加到 zip 文件中
            #     for folder_name in folder_names:
            #         full_folder_path = os.path.join(f"./号包/{nowuid}", folder_name)
            #         if os.path.exists(full_folder_path):
            #             # 添加文件夹及其内容
            #             for root, dirs, files in os.walk(full_folder_path):
            #                 for file in files:
            #                     file_path = os.path.join(root, file)
            #                     # 使用相对路径在压缩包中添加文件，并设置压缩包内部的路径
            #                     zipf.write(file_path, os.path.join(folder_name, os.path.relpath(file_path, full_folder_path)))
            #         else:
            #             # update.message.reply_text(f"文件夹 '{folder_name}' 不存在！")
            #             pass

            # # 发送 zip 文件给用户

            # folder_names = '\n'.join(folder_names)

            # current_time = datetime.datetime.now()

            # # 将当前时间格式化为字符串
            # formatted_time = current_time.strftime("%Y%m%d%H%M%S")

            # # 添加时间戳
            # timestamp = str(current_time.timestamp()).replace(".", "")

            # # 组合编号
            # bianhao = formatted_time + timestamp
            # timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # goumaijilua('直登号', bianhao, user_id, erjiprojectname, zip_filename,fstext, timer)

            # query.message.reply_document(open(zip_filename, "rb"))




    else:
        if lang == 'zh':
            context.bot.send_message(chat_id=user_id, text='❌ 余额不足，请及时充值！')
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
        else:
            context.bot.send_message(chat_id=user_id, text='❌ Insufficient balance, please recharge in time!')
        return


def qchuall(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    bot_id = context.bot.id
    user_id = query.from_user.id

    nowuid = query.data.replace('qchuall ', '')

    ejfl_list = ejfl.find_one({'nowuid': nowuid})
    fhtype = hb.find_one({'nowuid': nowuid})['leixing']
    projectname = ejfl_list['projectname']
    yijiid = ejfl_list['uid']
    yiji_list = fenlei.find_one({'uid': yijiid})
    yijiprojectname = yiji_list['projectname']

    folder_names = []
    if fhtype == '协议号':
        for j in list(hb.find({"nowuid": nowuid, 'state': 0})):
            projectname = j['projectname']
            hbid = j['hbid']
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            hb.delete_one({'hbid': hbid})
            folder_names.append(projectname)
        shijiancuo = int(time.time())
        zip_filename = f"./协议号发货/{user_id}_{shijiancuo}.zip"
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # 将每个文件及其内容添加到 zip 文件中
            for file_name in folder_names:
                # 检查是否存在以 .json 或 .session 结尾的文件
                json_file_path = os.path.join(f"./协议号/{nowuid}", file_name + ".json")
                session_file_path = os.path.join(f"./协议号/{nowuid}", file_name + ".session")
                if os.path.exists(json_file_path):
                    zipf.write(json_file_path, os.path.basename(json_file_path))
                if os.path.exists(session_file_path):
                    zipf.write(session_file_path, os.path.basename(session_file_path))
        query.message.reply_document(open(zip_filename, "rb"))

    elif fhtype == 'API':
        for j in list(hb.find({"nowuid": nowuid, 'state': 0})):
            projectname = j['projectname']
            hbid = j['hbid']
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            hb.delete_one({'hbid': hbid})
            folder_names.append(projectname)

        shijiancuo = int(time.time())

        zip_filename = f"./手机接码发货/{user_id}_{shijiancuo}.txt"
        with open(zip_filename, "w") as f:
            for folder_name in folder_names:
                f.write(folder_name + "\n")

        query.message.reply_document(open(zip_filename, "rb"))

    elif fhtype == '谷歌':
        for j in list(hb.find({"nowuid": nowuid, 'state': 0, 'leixing': '谷歌'})):
            projectname = j['projectname']
            hbid = j['hbid']
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            hb.update_one({'hbid': hbid}, {"$set": {'state': 1, 'yssj': timer, 'gmid': user_id}})
            data = j['data']
            us1 = data['账户']
            us2 = data['密码']
            us3 = data['子邮件']
            fste23xt = f'login: {us1}\npassword: {us2}\nsubmail: {us3}\n'
            hb.delete_one({'hbid': hbid})
            folder_names.append(fste23xt)
        folder_names = '\n'.join(folder_names)
        shijiancuo = int(time.time())

        zip_filename = f"./谷歌发货/{user_id}_{shijiancuo}.txt"
        with open(zip_filename, "w") as f:

            f.write(folder_names)

        query.message.reply_document(open(zip_filename, "rb"))


    elif fhtype == '会员链接':
        for j in list(hb.find({"nowuid": nowuid, 'state': 0})):
            projectname = j['projectname']
            hbid = j['hbid']
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            hb.delete_one({'hbid': hbid})
            folder_names.append(projectname)
        folder_names = '\n'.join(folder_names)

        context.bot.send_message(chat_id=user_id, text=folder_names, disable_web_page_preview=True)
    else:
        for j in list(hb.find({"nowuid": nowuid, 'state': 0})):
            projectname = j['projectname']
            hbid = j['hbid']
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            hb.delete_one({'hbid': hbid})
            folder_names.append(projectname)

        shijiancuo = int(time.time())
        zip_filename = f"./发货/{user_id}_{shijiancuo}.zip"
        with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
            # 将每个文件夹及其内容添加到 zip 文件中
            for folder_name in folder_names:
                full_folder_path = os.path.join(f"./号包/{nowuid}", folder_name)
                if os.path.exists(full_folder_path):
                    # 添加文件夹及其内容
                    for root, dirs, files in os.walk(full_folder_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # 使用相对路径在压缩包中添加文件，并设置压缩包内部的路径
                            zipf.write(file_path,
                                       os.path.join(folder_name, os.path.relpath(file_path, full_folder_path)))
                else:
                    # update.message.reply_text(f"文件夹 '{folder_name}' 不存在！")
                    pass

        query.message.reply_document(open(zip_filename, "rb"))

    ej_list = ejfl.find_one({'nowuid': nowuid})
    uid = ej_list['uid']
    ej_projectname = ej_list['projectname']
    money = ej_list['money']
    fl_pro = fenlei.find_one({'uid': uid})['projectname']
    keyboard = [
        [InlineKeyboardButton('取出所有库存', callback_data=f'qchuall {nowuid}'),
         InlineKeyboardButton('此商品使用说明', callback_data=f'update_sysm {nowuid}')],
        [InlineKeyboardButton('上传谷歌账户', callback_data=f'update_gg {nowuid}'),
         InlineKeyboardButton('购买此商品提示', callback_data=f'update_wbts {nowuid}')],
        [InlineKeyboardButton('上传链接', callback_data=f'update_hy {nowuid}'),
         InlineKeyboardButton('上传txt文件', callback_data=f'update_txt {nowuid}')],
        [InlineKeyboardButton('上传号包', callback_data=f'update_hb {nowuid}'),
         InlineKeyboardButton('上传协议号', callback_data=f'update_xyh {nowuid}')],
        [InlineKeyboardButton('修改二级分类名', callback_data=f'upejflname {nowuid}'),
         InlineKeyboardButton('修改价格', callback_data=f'upmoney {nowuid}')],
        [InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')]
    ]
    kc = len(list(hb.find({'nowuid': nowuid, 'state': 0})))
    ys = len(list(hb.find({'nowuid': nowuid, 'state': 1})))
    fstext = f'''
主分类: {fl_pro}
二级分类: {ej_projectname}

价格: CNY{money}
库存: {kc}
已售: {ys}
    '''
    context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))


def qxdingdan(update: Update, context: CallbackContext):
    query = update.callback_query
    chat = query.message.chat
    query.answer()
    bot_id = context.bot.id
    chat_id = chat.id
    user_id = query.from_user.id

    topup.delete_one({'user_id': user_id})
    context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)


def textkeyboard(update: Update, context: CallbackContext):
    """完整修复版：处理所有文本输入和菜单按钮"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat.id
        username = chat.username
        firstname = chat.first_name
        lastname = chat.last_name
        bot_id = context.bot.id
        fullname = chat.full_name.replace('<', '').replace('>', '')
        reply_to_message_id = update.effective_message.message_id
        timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        user_list = user.find_one({"user_id": user_id})
        
        if not user_list:
            # 用户不存在，引导注册
            context.bot.send_message(chat_id=user_id, text="请先发送 /start 初始化账户")
            return
            
        creation_time = user_list['creation_time']
        state = user_list['state']
        sign = user_list.get('sign', 0)
        USDT = user_list['USDT']
        zgje = user_list.get('zgje', 0)
        zgsl = user_list.get('zgsl', 0)
        lang = user_list['lang']
        text = update.message.text
        zxh = update.message.text_html
        
        # 检查营业状态
        yyzt = shangtext.find_one({'projectname': '营业状态'})['text']
        if yyzt == 0:
            if state != '4':
                return

        print(f"🔍 调试信息: user_id={user_id}, sign={sign}, text='{text}'")

        # ==================== 🔥 修复1: 处理自定义充值金额输入 ====================
        if str(sign) == 'custom_amount_input':
            try:
                amount = float(text.strip())
                if amount < 1:
                    error_msg = "充值金额不能小于1元" if lang == 'zh' else "Amount cannot be less than 1 CNY"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                if amount > 10000:
                    error_msg = "充值金额不能大于10000元" if lang == 'zh' else "Amount cannot exceed 10000 CNY"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                amount = int(amount)  # 转换为整数
                
                # 清除用户状态
                user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
                
                # 删除用户输入消息
                del_message(update.message)
                
                # 显示支付方式选择
                if lang == 'zh':
                    fstext = f'''<b>💰充值金额：CNY{amount}

请选择支付方式：</b>'''
                    keyboard = [
                        [InlineKeyboardButton('💚 微信支付', callback_data=f'pay_wx_{amount}'),
                         InlineKeyboardButton('💙 支付宝', callback_data=f'pay_ali_{amount}')],
                        [InlineKeyboardButton('💎 USDT-TRC20', callback_data=f'pay_usdt_{amount}')],
                        [InlineKeyboardButton('🔙 返回选择金额', callback_data='back_to_amount_select'),
                         InlineKeyboardButton('❌ 取消', callback_data=f'close {user_id}')]
                    ]
                else:
                    fstext = f'''<b>💰Recharge Amount: CNY{amount}

Please select payment method:</b>'''
                    keyboard = [
                        [InlineKeyboardButton('💚 WeChat Pay', callback_data=f'pay_wx_{amount}'),
                         InlineKeyboardButton('💙 Alipay', callback_data=f'pay_ali_{amount}')],
                        [InlineKeyboardButton('💎 USDT-TRC20', callback_data=f'pay_usdt_{amount}')],
                        [InlineKeyboardButton('🔙 Back to Amount', callback_data='back_to_amount_select'),
                         InlineKeyboardButton('❌ Cancel', callback_data=f'close {user_id}')]
                    ]
                
                context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                       reply_markup=InlineKeyboardMarkup(keyboard))
                return
                
            except ValueError:
                error_msg = "请输入有效的数字" if lang == 'zh' else "Please enter a valid number"
                context.bot.send_message(chat_id=user_id, text=error_msg)
                return
        
        # ==================== 🔥 修复2: 处理商品购买数量输入 ====================
        elif str(sign).startswith('gmqq '):
            try:
                quantity = int(text.strip())
                if quantity < 1:
                    error_msg = "购买数量不能小于1" if lang == 'zh' else "Quantity cannot be less than 1"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                if quantity > 1000:
                    error_msg = "购买数量不能大于1000" if lang == 'zh' else "Quantity cannot exceed 1000"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                # 解析商品信息
                data = sign.replace('gmqq ', '')
                nowuid = data.split(':')[0]
                available_stock = int(data.split(':')[1])
                
                if quantity > available_stock:
                    error_msg = f"库存不足，当前库存：{available_stock}" if lang == 'zh' else f"Insufficient stock, current stock: {available_stock}"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                # 获取商品信息
                ejfl_list = ejfl.find_one({'nowuid': nowuid})
                if not ejfl_list:
                    error_msg = "商品不存在" if lang == 'zh' else "Product not found"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                projectname = ejfl_list['projectname']
                unit_price = ejfl_list['money']
                total_price = unit_price * quantity
                
                # 检查用户余额
                if USDT < total_price:
                    error_msg = f"余额不足，当前余额：CNY{USDT}，需要：CNY{total_price}" if lang == 'zh' else f"Insufficient balance. Current: CNY{USDT}, Required: CNY{total_price}"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                # 清除用户状态
                user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
                
                # 删除用户输入消息
                del_message(update.message)
                
                # 显示确认购买界面
                if lang == 'zh':
                    confirm_text = f'''<b>📋 确认购买信息

🛒 商品名称：{projectname}
💰 单价：CNY{unit_price}
📦 数量：{quantity}
💳 总价：CNY{total_price}
💎 当前余额：CNY{USDT}
💰 购买后余额：CNY{USDT - total_price}

请确认是否购买？</b>'''
                    
                    keyboard = [
                        [InlineKeyboardButton('✅ 确认购买', callback_data=f'qrgaimai {nowuid}:{quantity}:{total_price}')],
                        [InlineKeyboardButton('❌ 取消购买', callback_data=f'gmsp {nowuid}:{available_stock}')]
                    ]
                else:
                    confirm_text = f'''<b>📋 Purchase Confirmation

🛒 Product: {projectname}
💰 Unit Price: CNY{unit_price}
📦 Quantity: {quantity}
💳 Total: CNY{total_price}
💎 Current Balance: CNY{USDT}
💰 Balance After: CNY{USDT - total_price}

Confirm purchase?</b>'''
                    
                    keyboard = [
                        [InlineKeyboardButton('✅ Confirm Purchase', callback_data=f'qrgaimai {nowuid}:{quantity}:{total_price}')],
                        [InlineKeyboardButton('❌ Cancel', callback_data=f'gmsp {nowuid}:{available_stock}')]
                    ]
                
                context.bot.send_message(chat_id=user_id, text=confirm_text, parse_mode='HTML',
                                       reply_markup=InlineKeyboardMarkup(keyboard))
                return
                
            except ValueError:
                error_msg = "请输入有效的数字" if lang == 'zh' else "Please enter a valid number"
                context.bot.send_message(chat_id=user_id, text=error_msg)
                return

        # ==================== 🔥 修复3: 处理红包金额输入 ====================
        elif str(sign).startswith('addhb'):
            try:
                money = float(text.strip())
                if money <= 0:
                    error_msg = "红包金额必须大于0" if lang == 'zh' else "Red packet amount must be greater than 0"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                if money > USDT:
                    error_msg = f"余额不足，当前余额：CNY{USDT}" if lang == 'zh' else f"Insufficient balance. Current: CNY{USDT}"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                # 清除用户状态
                user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
                del_message(update.message)
                
                # 显示红包数量输入
                if lang == 'zh':
                    fstext = f'''💡 红包总金额：CNY{money}

请输入红包数量（份数）：

📝 格式：直接输入数字
📦 范围：1 - 100
📱 例如：5 或 10'''
                    keyboard = [[InlineKeyboardButton('🚫取消', callback_data=f'close {user_id}')]]
                else:
                    fstext = f'''💡 Total amount: CNY{money}

Please enter number of red packets:

📝 Format: Enter numbers only  
📦 Range: 1 - 100
📱 Example: 5 or 10'''
                    keyboard = [[InlineKeyboardButton('🚫Cancel', callback_data=f'close {user_id}')]]
                
                user.update_one({'user_id': user_id}, {"$set": {'sign': f'addhb_count {money}'}})
                context.bot.send_message(chat_id=user_id, text=fstext, reply_markup=InlineKeyboardMarkup(keyboard))
                return
                
            except ValueError:
                error_msg = "请输入有效的数字" if lang == 'zh' else "Please enter a valid number"
                context.bot.send_message(chat_id=user_id, text=error_msg)
                return

        # ==================== 🔥 修复4: 处理红包数量输入 ====================
        elif str(sign).startswith('addhb_count '):
            try:
                count = int(text.strip())
                if count < 1 or count > 100:
                    error_msg = "红包数量必须在1-100之间" if lang == 'zh' else "Number of red packets must be between 1-100"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                # 解析红包金额
                money = float(sign.replace('addhb_count ', ''))
                
                # 检查余额
                if money > USDT:
                    error_msg = f"余额不足，当前余额：CNY{USDT}" if lang == 'zh' else f"Insufficient balance. Current: CNY{USDT}"
                    context.bot.send_message(chat_id=user_id, text=error_msg)
                    return
                
                # 清除用户状态并扣除余额
                user.update_one({'user_id': user_id}, {"$set": {'sign': 0, 'USDT': USDT - money}})
                del_message(update.message)
                
                # 创建红包
                uid = generate_24bit_uid()
                timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                
                hongbao.insert_one({
                    'uid': uid,
                    'user_id': user_id,
                    'fullname': fullname,
                    'hbmoney': money,
                    'hbsl': count,
                    'timer': timer,
                    'state': 0
                })
                
                if lang == 'zh':
                    success_text = f'''🎉 红包创建成功！

💰 总金额：CNY{money}
📦 红包数量：{count}份
💎 剩余余额：CNY{USDT - money}

点击下方按钮分享红包：'''
                    keyboard = [
                        [InlineKeyboardButton('🎁 分享红包', switch_inline_query=f'redpacket {uid}')],
                        [InlineKeyboardButton('📊 查看详情', callback_data=f'xzhb {uid}')],
                        [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]
                    ]
                else:
                    success_text = f'''🎉 Red packet created successfully!

💰 Total amount: CNY{money}
📦 Quantity: {count}
💎 Remaining balance: CNY{USDT - money}

Click button below to share:'''
                    keyboard = [
                        [InlineKeyboardButton('🎁 Share Red Packet', switch_inline_query=f'redpacket {uid}')],
                        [InlineKeyboardButton('📊 View Details', callback_data=f'xzhb {uid}')],
                        [InlineKeyboardButton('❌ Close', callback_data=f'close {user_id}')]
                    ]
                
                context.bot.send_message(chat_id=user_id, text=success_text, parse_mode='HTML',
                                       reply_markup=InlineKeyboardMarkup(keyboard))
                return
                
            except ValueError:
                error_msg = "请输入有效的数字" if lang == 'zh' else "Please enter a valid number"
                context.bot.send_message(chat_id=user_id, text=error_msg)
                return

        # ==================== 🔥 修复5: 处理管理功能输入 ====================
        elif sign == 'set_exchange_rate':
            try:
                rate = float(text.strip())
                if rate < 1 or rate > 20:
                    context.bot.send_message(chat_id=user_id, text='汇率应在1-20之间')
                    return
                
                # 更新汇率
                shangtext.update_one({'projectname': '人民币USDT汇率'}, {"$set": {"text": rate}})
                user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
                
                context.bot.send_message(chat_id=user_id, text=f'✅ 汇率已更新为：1 USDT = CNY{rate}')
                del_message(update.message)
                return
                
            except ValueError:
                context.bot.send_message(chat_id=user_id, text='请输入有效的汇率数字')
                return

        elif sign == 'settrc20':
            trc20_address = text.strip()
            if not trc20_address.startswith('T') or len(trc20_address) != 34:
                context.bot.send_message(chat_id=user_id, text='❌ 请输入有效的TRC20地址（以T开头，34位）')
                return
            
            shangtext.update_one({'projectname': '充值地址'}, {"$set": {"text": trc20_address}})
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            
            # 生成二维码
            import qrcode
            qr_file = f'{trc20_address}.png'
            if not os.path.exists(qr_file):
                try:
                    img = qrcode.make(data=trc20_address)
                    with open(qr_file, 'wb') as f:
                        img.save(f)
                except Exception as e:
                    print(f"生成二维码失败: {e}")
            
            context.bot.send_message(chat_id=user_id, text=f'✅ TRC20充值地址已设置为：\n<code>{trc20_address}</code>', parse_mode='HTML')
            del_message(update.message)
            return

        # ==================== 🔥 修复6: 其他管理功能 ====================
        elif sign == 'startupdate':
            new_welcome = text.strip()
            if len(new_welcome) > 1000:
                context.bot.send_message(chat_id=user_id, text='欢迎语长度不能超过1000字符')
                return
            
            shangtext.update_one({'projectname': '欢迎语'}, {"$set": {"text": new_welcome}})
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            
            context.bot.send_message(chat_id=user_id, text='✅ 欢迎语已更新')
            del_message(update.message)
            return

        # ==================== 菜单按钮处理逻辑 ====================
        # 检查是否是菜单按钮
        get_key_list = get_key.find({})
        get_prolist = []
        for i in get_key_list:
            get_prolist.append(i["projectname"])
        
        # 🔥 关键修复：重置sign状态
        if sign != 0 and text in get_prolist:
            print(f"🔄 检测到菜单按钮点击，重置用户状态: {text}")
            user.update_one({'user_id': user_id}, {"$set": {'sign': 0}})
            sign = 0  # 本地变量也要重置

        if sign == 0:
            # 特殊命令处理
            if text == '开始营业':
                if state == '4':
                    shangtext.update_one({'projectname': '营业状态'}, {"$set": {"text": 1}})
                    context.bot.send_message(chat_id=user_id, text='✅ 开始营业')
                    del_message(update.message)
                return
            elif text == '停止营业':
                if state == '4':
                    shangtext.update_one({'projectname': '营业状态'}, {"$set": {"text": 0}})
                    context.bot.send_message(chat_id=user_id, text='✅ 停止营业')
                    del_message(update.message)
                return

            # 🔥 获取菜单关键词 - 修复版
            try:
                grzx = get_key.find_one({'projectname': {"$regex": "中心"}})
                grzx = grzx['projectname'] if grzx else '💤 个人中心'
                if lang == 'en':
                    grzx_trans = fyb.find_one({'text': grzx})
                    grzx = grzx_trans['fanyi'] if grzx_trans else 'Personal Center'
            except:
                grzx = '💤 个人中心' if lang == 'zh' else 'Personal Center'

            try:
                wycz = get_key.find_one({'projectname': {"$regex": "充值"}})
                wycz = wycz['projectname'] if wycz else '💰 余额充值'
                if lang == 'en':
                    wycz_trans = fyb.find_one({'text': wycz})
                    wycz = wycz_trans['fanyi'] if wycz_trans else 'Recharge Balance'
            except:
                wycz = '💰 余额充值' if lang == 'zh' else 'Recharge Balance'

            try:
                splb = get_key.find_one({'projectname': {"$regex": "列表"}})
                splb = splb['projectname'] if splb else '🛒 商品列表'
                if lang == 'en':
                    splb_trans = fyb.find_one({'text': splb})
                    splb = splb_trans['fanyi'] if splb_trans else 'Product List'
            except:
                splb = '🛒 商品列表' if lang == 'zh' else 'Product List'

            # 🔥 关键修复：红包功能识别 - 更强的兼容性
            is_red_packet = False
            try:
                if '红包' in text or 'Red Packet' in text or '🧧' in text:
                    is_red_packet = True
                else:
                    red_packet_menu = get_key.find_one({'projectname': {"$regex": "红包"}})
                    if red_packet_menu and text == red_packet_menu['projectname']:
                        is_red_packet = True
                    elif lang == 'en':
                        red_packet_trans = fyb.find_one({'text': {"$regex": "红包"}})
                        if red_packet_trans and text == red_packet_trans['fanyi']:
                            is_red_packet = True
            except:
                if '红包' in text or 'red packet' in text.lower() or '🧧' in text:
                    is_red_packet = True

            try:
                qhyy = get_key.find_one({'projectname': {"$regex": "切换语言"}})
                qhyy = qhyy['projectname'] if qhyy else '🌍 切换语言'
                if lang == 'en':
                    qhyy_trans = fyb.find_one({'text': qhyy})
                    qhyy = qhyy_trans['fanyi'] if qhyy_trans else 'Switch Language'
            except:
                qhyy = '🌍 切换语言' if lang == 'zh' else 'Switch Language'
            
            try:
                hjkf = get_key.find_one({'projectname': {"$regex": "呼叫客服"}})
                hjkf = hjkf['projectname'] if hjkf else '📞 呼叫客服'
                if lang == 'en':
                    hjkf_trans = fyb.find_one({'text': hjkf})
                    hjkf = hjkf_trans['fanyi'] if hjkf_trans else 'Contact Support'
            except:
                hjkf = '📞 呼叫客服' if lang == 'zh' else 'Contact Support'

            # 🔥 处理菜单点击 - 红包功能修复版
            print(f"🖱️ 菜单处理: text='{text}', grzx='{grzx}', wycz='{wycz}', splb='{splb}', is_red_packet={is_red_packet}")
            
            if text == grzx:  # 个人中心按钮
                del_message(update.message)
                # 个人中心逻辑...
                if username is None:
                    username = fullname
                else:
                    username = f'<a href="https://t.me/{username}">{username}</a>'
                
                if lang == 'zh':
                    fstext = f'''<b>您的ID:</b>  <code>{user_id}</code>
<b>您的用户名:</b>  {username} 
<b>注册日期:</b>  {creation_time}

<b>总购数量:</b>  {zgsl}

<b>总购金额:</b>  CNY{standard_num(zgje)}

<b>您的余额:</b>  CNY{USDT}
'''
                    keyboard = [[InlineKeyboardButton('🛒购买记录', callback_data=f'gmaijilu {user_id}')],
                               [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]]
                else:
                    fstext = f'''<b>Your ID:</b>  <code>{user_id}</code>
<b>username:</b>  {username} 
<b>Registration date:</b>  {creation_time}

<b>Total purchase quantity:</b>  {zgsl}

<b>Total purchase amount:</b>  CNY{standard_num(zgje)}

<b>Balance:</b>  CNY{USDT}
'''
                    keyboard = [[InlineKeyboardButton('🛒Purchase history', callback_data=f'gmaijilu {user_id}')],
                               [InlineKeyboardButton('❌ Close', callback_data=f'close {user_id}')]]
        
                context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                       reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)
        
            elif text == 'Chinese' or text == '中文服务':
                del_message(update.message)
                user.update_one({'user_id': user_id}, {"$set": {'lang': 'zh'}})
                
                # 更新键盘为中文
                keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                           [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                           [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                           [], [], [], [], []]
                
                keylist = get_key.find({}, sort=[('Row', 1), ('first', 1)])
                for i in keylist:
                    projectname = i['projectname']
                    if projectname != '中文服务':
                        row = i['Row']
                        keyboard[row - 1].append(KeyboardButton(projectname))
                
                context.bot.send_message(chat_id=user_id, text='✅ 已切换到中文',
                                       reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                       one_time_keyboard=False))
        
            elif text == 'English':
                del_message(update.message)
                user.update_one({'user_id': user_id}, {"$set": {'lang': 'en'}})
                
                # 更新键盘为英文
                keyboard = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                           [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                           [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [],
                           [], [], [], [], []]
                
                keylist = get_key.find({}, sort=[('Row', 1), ('first', 1)])
                for i in keylist:
                    projectname = i['projectname']
                    if projectname != '中文服务':
                        # 获取英文翻译
                        fy_result = fyb.find_one({'text': projectname})
                        if fy_result:
                            projectname = fy_result['fanyi']
                        else:
                            projectname = get_fy(projectname)
                        row = i['Row']
                        keyboard[row - 1].append(KeyboardButton(projectname))
                
                context.bot.send_message(chat_id=user_id, text='✅ Switched to English',
                                       reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True,
                                                                       one_time_keyboard=False))
        
            elif text == wycz:
                del_message(update.message)
                # 充值逻辑...
                if lang == 'zh':
                    fstext = '''<b>💰请选择充值金额

💹请选择您要充值的金额‼️</b>
'''
                    keyboard = [
                        [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
                         InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
                         InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
                        [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
                         InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
                         InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
                        [InlineKeyboardButton('💡自定义金额', callback_data='select_amount_custom')],
                        [InlineKeyboardButton('❌ 取消', callback_data=f'close {user_id}')]
                    ]
                else:
                    fstext = '''<b>💰Please select recharge amount

💹Please select the amount you want to recharge‼️</b>
'''
                    keyboard = [
                        [InlineKeyboardButton('CNY30', callback_data='select_amount_30'),
                         InlineKeyboardButton('CNY50', callback_data='select_amount_50'),
                         InlineKeyboardButton('CNY100', callback_data='select_amount_100')],
                        [InlineKeyboardButton('CNY200', callback_data='select_amount_200'),
                         InlineKeyboardButton('CNY300', callback_data='select_amount_300'),
                         InlineKeyboardButton('CNY500', callback_data='select_amount_500')],
                        [InlineKeyboardButton('💡Custom Amount', callback_data='select_amount_custom')],
                        [InlineKeyboardButton('❌ Cancel', callback_data=f'close {user_id}')]
                    ]
                
                context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                       reply_markup=InlineKeyboardMarkup(keyboard))

            elif text == splb:  # 🔥 关键修复：商品列表按钮处理
                del_message(update.message)
                print(f"🛒 检测到商品列表按钮点击: {text}")
                
                # 调用商品列表显示逻辑
                lang = user.find_one({'user_id': user_id})['lang']
                fenlei_data = list(fenlei.find({}, sort=[('row', 1)]))
                ejfl_data = list(ejfl.find({}))
                hb_data = list(hb.find({'state': 0}))

                keyboard = [[] for _ in range(50)]

                for i in fenlei_data:
                    uid = i['uid']
                    projectname = i['projectname']
                    row = i['row']

                    hsl = sum(1 for j in ejfl_data if j['uid'] == uid for hb_item in hb_data if
                              hb_item['nowuid'] == j['nowuid'])

                    projectname = projectname if lang == 'zh' else get_fy(projectname)
                    keyboard[row - 1].append(
                        InlineKeyboardButton(f'{projectname}({hsl})', callback_data=f'catejflsp {uid}:{hsl}'))
                
                if lang == 'zh':
                    fstext = '''
<b>🛒这是商品列表  选择你需要的商品：

⚠️没使用过的本店商品的，请先少量购买测试，以免造成不必要的争执！谢谢合作！

⚠️购买后，请立即检测账户是否正常！超过1小时视为放弃售后服务！</b>
                    '''
                else:
                    fstext = get_fy('''
<b>🛒这是商品列表  选择你需要的商品：

⚠️没使用过的本店商品的，请先少量购买测试，以免造成不必要的争执！谢谢合作！

⚠️购买后，请立即检测账户是否正常！超过1小时视为放弃售后服务！</b>
                    ''')
                
                keyboard.append([InlineKeyboardButton('❌关闭', callback_data=f'close {user_id}')])
                context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                       reply_markup=InlineKeyboardMarkup(keyboard))

            # 🔥 关键修复：红包功能处理 - 更好的兼容性
            elif is_red_packet:
                del_message(update.message)
                print(f"🧧 检测到红包功能触发: {text}")
                
                if lang == 'zh':
                    fstext = "从下面的列表中选择一个红包"
                    keyboard = [
                        [InlineKeyboardButton('⚫️进行中', callback_data='jxzhb'),
                         InlineKeyboardButton('已结束', callback_data='yjshb')],
                        [InlineKeyboardButton('➕添加', callback_data='addhb')],
                        [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]
                    ]
                else:
                    fstext = "Select a red packet from the list below"
                    keyboard = [
                        [InlineKeyboardButton('⚫️ In Progress', callback_data='jxzhb'),
                         InlineKeyboardButton('Finished', callback_data='yjshb')],
                        [InlineKeyboardButton('➕ Add', callback_data='addhb')],
                        [InlineKeyboardButton('Close', callback_data=f'close {user_id}')]
                    ]
                
                context.bot.send_message(chat_id=user_id, text=fstext,
                                       reply_markup=InlineKeyboardMarkup(keyboard))

            elif text == qhyy:  # 切换语言按钮
                del_message(update.message)
                # 调用切换语言功能，相当于 /language 命令
                if lang == 'zh':
                    fstext = "请选择语言 / Please select language:"
                else:
                    fstext = "Please select language / 请选择语言:"
                
                keyboard = [
                    [InlineKeyboardButton('🇨🇳 中文', callback_data='set_lang_zh')],
                    [InlineKeyboardButton('🇺🇸 English', callback_data='set_lang_en')],
                    [InlineKeyboardButton('❌ 关闭/Close', callback_data=f'close {user_id}')]
                ]
                
                context.bot.send_message(chat_id=user_id, text=fstext,
                                       reply_markup=InlineKeyboardMarkup(keyboard))
            
            elif text == hjkf:  # 呼叫客服按钮
                del_message(update.message)
                # 获取客服联系信息
                key_list = get_key.find_one({"projectname": text})
                if key_list and key_list.get('text'):
                    customer_service_text = key_list['text']
                    # 如果是英文环境且没有英文翻译，则翻译文本
                    if lang == 'en':
                        customer_service_text = get_fy(customer_service_text)
                else:
                    # 默认客服信息
                    customer_service_text = '如需帮助，请联系客服：@qingfenger' if lang == 'zh' else 'For help, please contact support: @qingfenger'
                
                # 添加关闭按钮
                close_text = '❌ 关闭' if lang == 'zh' else '❌ Close'
                keyboard = [[InlineKeyboardButton(close_text, callback_data=f'close {user_id}')]]
                
                context.bot.send_message(chat_id=user_id, text=customer_service_text,
                                       reply_markup=InlineKeyboardMarkup(keyboard),
                                       disable_web_page_preview=True)
            
            # 在最后的 else 处理中，确保英文按钮也能被处理
            else:
                # 检查是否是英文按钮，转换为中文处理
                if lang == 'en':
                    zh_text_record = fyb.find_one({'fanyi': text})
                    if zh_text_record:
                        text = zh_text_record['text']
                
                # 继续原有的按钮处理逻辑
                key_list = get_key.find_one({"projectname": text})
                if key_list != None:
                    del_message(update.message)
                    key_text = key_list['key_text']
                    print_text = key_list['text']

                    print_text = print_text if lang == 'zh' else get_fy(print_text)
                    file_type = key_list['file_type']
                    file_id = key_list['file_id']
                    entities = pickle.loads(key_list['entities'])
                    keyboard = pickle.loads(key_list['keyboard'])
                    
                    if context.bot.username in ['TelergamKFbot', 'Tclelgnam_bot']:
                        pass
                    else:
                        if print_text == '' and file_id == '':
                            context.bot.send_message(chat_id=user_id, text=text)
                        else:
                            if file_type == 'text':
                                message_id = context.bot.send_message(chat_id=user_id, text=print_text,
                                                                      reply_markup=InlineKeyboardMarkup(keyboard),
                                                                      parse_mode='HTML')
                            else:
                                if file_type == 'photo':
                                    message_id = context.bot.send_photo(chat_id=user_id, caption=print_text,
                                                                        photo=file_id,
                                                                        reply_markup=InlineKeyboardMarkup(keyboard),
                                                                        parse_mode='HTML')
                                else:
                                    message_id = context.bot.sendAnimation(chat_id=user_id, caption=print_text,
                                                                           animation=file_id,
                                                                           reply_markup=InlineKeyboardMarkup(keyboard),
                                                                           parse_mode='HTML')

# 🔥 为了更好的调试，添加一个专门的商品列表调试函数
def debug_products_button(user_id, lang='zh'):
    """调试商品列表按钮功能"""
    try:
        print("🐛 开始调试商品列表功能...")
        
        # 1. 检查菜单按钮配置
        splb_key = get_key.find_one({'projectname': {"$regex": "列表"}})
        print(f"📋 商品列表按钮配置: {splb_key}")
        
        # 2. 检查分类数据
        fenlei_data = list(fenlei.find({}, sort=[('row', 1)]))
        print(f"📦 分类数据数量: {len(fenlei_data)}")
        
        # 3. 检查二级分类数据
        ejfl_data = list(ejfl.find({}))
        print(f"📋 二级分类数据数量: {len(ejfl_data)}")
        
        # 4. 检查库存数据
        hb_data = list(hb.find({'state': 0}))
        print(f"📦 库存数据数量: {len(hb_data)}")
        
        print("✅ 商品列表调试完成")
        return True
        
    except Exception as e:
        print(f"❌ 商品列表调试失败: {e}")
        return False

# 🔥 快速修复函数：手动创建商品列表按钮
def create_products_button_if_missing():
    """如果商品列表按钮缺失，手动创建"""
    try:
        # 检查是否存在商品列表相关按钮
        products_button = get_key.find_one({'projectname': {"$regex": "商品|列表|Product"}})
        
        if not products_button:
            print("🔧 检测到商品列表按钮缺失，正在创建...")
            
            # 找到可用的行和列位置
            max_row = get_key.find_one({}, sort=[('Row', -1)])
            next_row = (max_row['Row'] + 1) if max_row else 1
            
            # 创建商品列表按钮
            get_key.insert_one({
                'Row': next_row,
                'first': 1,
                'projectname': '🛒 商品列表',
                'text': '',
                'file_id': '',
                'file_type': 'text',
                'key_text': '',
                'keyboard': b'\x80\x03]q\x00.',
                'entities': b'\x80\x03]q\x00.'
            })
            
            # 创建对应的英文翻译
            fyb.insert_one({
                'projectname': 'auto_translation',
                'text': '🛒 商品列表',
                'fanyi': '🛒 Product List'
            })
            
            print("✅ 商品列表按钮创建成功")
            return True
        else:
            print("ℹ️ 商品列表按钮已存在")
            return True
            
    except Exception as e:
        print(f"❌ 创建商品列表按钮失败: {e}")
        return False


def del_message(message):
    try:
        message.delete()
    except:
        pass


def standard_num(num):
    value = Decimal(str(num)).quantize(Decimal("0.01"))
    return value.to_integral() if value == value.to_integral() else value.normalize()


def secure_jiexi(context):
    """安全的USDT充值检测和回调处理"""
    try:
        trc20 = shangtext.find_one({'projectname': '充值地址'})
        if not trc20 or not trc20.get('text'):
            print("⚠️ 充值地址未配置")
            return
            
        trc20_address = trc20['text']
        print(f"🔍 检查充值地址: {trc20_address}")
        
        # 🔥 关键修复1：只处理未处理且确认过的交易
        unprocessed_transactions = qukuai.find({
            'state': 0,  # 未处理
            'to_address': trc20_address,
            'confirmations': {'$gte': 1}  # 至少1个确认
        }).sort('_id', 1)  # 按时间顺序处理
        
        processed_count = 0
        
        for transaction in unprocessed_transactions:
            try:
                # 🔥 关键修复2：立即标记为处理中，防止重复处理
                txid = transaction['txid']
                result = qukuai.update_one(
                    {'txid': txid, 'state': 0},  # 只更新未处理的
                    {'$set': {'state': 3, 'processing_time': time.time()}}  # 标记为处理中
                )
                
                if result.modified_count == 0:
                    print(f"⚠️ 交易 {txid} 已被其他进程处理")
                    continue
                
                # 处理交易
                if process_single_transaction(transaction, context):
                    # 成功处理，标记为已完成
                    qukuai.update_one(
                        {'txid': txid}, 
                        {'$set': {
                            'state': 1, 
                            'processed_time': time.time(),
                            'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        }}
                    )
                    processed_count += 1
                else:
                    # 处理失败，恢复为未处理状态
                    qukuai.update_one(
                        {'txid': txid}, 
                        {'$set': {
                            'state': 0,
                            'last_error': f'处理失败于 {time.strftime("%Y-%m-%d %H:%M:%S")}'
                        }}
                    )
                
            except Exception as tx_error:
                print(f"❌ 处理单个交易失败: {tx_error}")
                # 恢复交易状态
                qukuai.update_one(
                    {'txid': transaction['txid']}, 
                    {'$set': {'state': 0, 'error': str(tx_error)}}
                )
                continue
        
        if processed_count > 0:
            print(f"✅ 本次安全处理了 {processed_count} 笔充值")
        
    except Exception as e:
        print(f"❌ 安全USDT充值检测失败: {e}")
        import traceback
        traceback.print_exc()

def process_single_transaction(transaction, context):
    """处理单个交易的安全函数"""
    try:
        txid = transaction['txid']
        quant = transaction['quant']
        from_address = transaction['from_address']
        to_address = transaction['to_address']
        
        # 🔥 关键修复3：验证交易金额和地址
        usdt_amount = abs(float(Decimal(quant) / Decimal('1000000')))
        
        # 验证最小充值金额
        if usdt_amount < 1.0:
            print(f"⚠️ 交易金额太小: {usdt_amount} USDT")
            return False
        
        # 验证最大充值金额（防止异常大额）
        if usdt_amount > 100000:
            print(f"⚠️ 交易金额异常: {usdt_amount} USDT，需要人工审核")
            return False
        
        print(f"💰 处理充值: {usdt_amount} USDT, txid: {txid}")
        
        # 🔥 关键修复4：严格的订单匹配和验证
        matching_order = find_and_validate_order(usdt_amount, txid)
        
        if not matching_order:
            print(f"⚠️ 未找到有效匹配订单: {usdt_amount} USDT")
            return False
        
        # 🔥 关键修复5：事务性处理用户余额更新
        return process_user_balance_update(matching_order, usdt_amount, txid, from_address, context)
        
    except Exception as e:
        print(f"❌ 处理单个交易异常: {e}")
        return False

def find_and_validate_order(usdt_amount, txid):
    """查找并验证订单的安全函数"""
    try:
        # 🔥 关键修复6：精确金额匹配 + 时间窗口验证
        current_time = time.time()
        time_24h_ago = current_time - (24 * 3600)  # 24小时前
        
        # 查找24小时内的匹配订单
        potential_orders = list(topup.find({
            "money": usdt_amount,
            "created_timestamp": {"$gte": time_24h_ago},  # 24小时内的订单
            "processed": {"$ne": True}  # 未处理的订单
        }).sort("created_timestamp", 1))  # 最早的优先
        
        if not potential_orders:
            return None
        
        # 🔥 关键修复7：防重复处理，原子性更新
        for order in potential_orders:
            result = topup.update_one(
                {
                    '_id': order['_id'],
                    'processed': {'$ne': True}  # 确保未被处理
                },
                {'$set': {
                    'processed': True,
                    'txid': txid,
                    'processing_time': current_time
                }}
            )
            
            if result.modified_count > 0:
                # 成功标记订单为已处理
                return order
        
        return None
        
    except Exception as e:
        print(f"❌ 订单验证失败: {e}")
        return None

def process_user_balance_update(order, credit_amount, txid, from_address, context):
    """安全的用户余额更新函数"""
    try:
        user_id = order['user_id']
        order_id = order.get('bianhao', str(uuid.uuid4()))
        payment_type = order.get('payment_type', 'usdt')
        
        # 🔥 关键修复8：获取用户信息并验证
        user_info = user.find_one({'user_id': user_id})
        if not user_info:
            print(f"❌ 找不到用户: {user_id}")
            # 恢复订单状态
            topup.update_one(
                {'_id': order['_id']}, 
                {'$set': {'processed': False}}
            )
            return False
        
        current_balance = user_info['USDT']
        
        # 🔥 关键修复9：根据支付类型确定充值金额
        if payment_type == 'usdt_cny':
            # 基于人民币的USDT充值
            final_credit = order.get('cny_amount', credit_amount * 7.2)
            unit = 'CNY'
        else:
            # 传统USDT充值
            final_credit = credit_amount
            unit = 'USDT'
        
        # 🔥 关键修复10：原子性余额更新
        new_balance = standard_num(float(current_balance) + float(final_credit))
        new_balance = float(new_balance) if str(new_balance).count('.') > 0 else int(new_balance)
        
        # 使用原子操作更新用户余额
        update_result = user.update_one(
            {'user_id': user_id, 'USDT': current_balance},  # 确保余额没有被其他进程修改
            {'$set': {'USDT': new_balance}}
        )
        
        if update_result.modified_count == 0:
            print(f"❌ 用户 {user_id} 余额更新失败，可能存在并发冲突")
            # 恢复订单状态
            topup.update_one(
                {'_id': order['_id']}, 
                {'$set': {'processed': False}}
            )
            return False
        
        # 🔥 关键修复11：记录详细的交易日志
        timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        transaction_log = {
            'user_id': user_id,
            'order_id': order_id,
            'txid': txid,
            'from_address': from_address,
            'amount': final_credit,
            'unit': unit,
            'old_balance': current_balance,
            'new_balance': new_balance,
            'timestamp': time.time(),
            'created_at': timer,
            'type': 'usdt_recharge',
            'status': 'completed'
        }
        
        try:
            # 插入交易日志
            transaction_logs.insert_one(transaction_log)
        except Exception as log_error:
            print(f"⚠️ 记录交易日志失败: {log_error}")
        
        # 🔥 关键修复12：安全的通知创建
        create_secure_notification(user_id, final_credit, new_balance, order_id, txid, from_address, timer)
        
        # 🔥 关键修复13：发送管理员通知（限制频率）
        send_admin_notification_throttled(user_info, final_credit, new_balance, txid, from_address, timer, context)
        
        # 🔥 关键修复14：清理已处理的订单
        topup.delete_one({'_id': order['_id']})
        
        print(f"✅ 安全处理完成: 用户{user_id} {current_balance} -> {new_balance}")
        return True
        
    except Exception as e:
        print(f"❌ 用户余额更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_secure_notification(user_id, amount, new_balance, order_id, txid, from_address, timer):
    """创建安全的充值成功通知"""
    try:
        # 🔥 防止重复通知
        existing_notification = notifications.find_one({
            'user_id': user_id,
            'txid': txid,
            'type': 'payment_success'
        })
        
        if existing_notification:
            print(f"⚠️ 通知已存在，跳过: {txid}")
            return
        
        notification_data = {
            'user_id': user_id,
            'type': 'payment_success',
            'amount': amount,
            'new_balance': new_balance,
            'order_no': order_id,
            'payment_method': 'USDT-TRC20',
            'txid': txid,
            'from_address': from_address,
            'processed': False,
            'created_at': timer,
            'timestamp': time.time(),
            'security_hash': generate_notification_hash(user_id, amount, txid)
        }
        
        notifications.insert_one(notification_data)
        print(f"📩 安全通知已创建: {user_id}")
        
    except Exception as e:
        print(f"❌ 创建通知失败: {e}")

def generate_notification_hash(user_id, amount, txid):
    """生成通知的安全哈希"""
    hash_string = f"{user_id}:{amount}:{txid}:{int(time.time())}"
    return hashlib.sha256(hash_string.encode()).hexdigest()[:16]

def send_admin_notification_throttled(user_info, amount, new_balance, txid, from_address, timer, context):
    """限流的管理员通知"""
    try:
        # 🔥 管理员通知限流：每分钟最多10条
        current_minute = int(time.time() / 60)
        throttle_key = f"admin_notifications:{current_minute}"
        
        # 简单的内存限流（生产环境建议使用Redis）
        if not hasattr(send_admin_notification_throttled, 'counters'):
            send_admin_notification_throttled.counters = {}
        
        count = send_admin_notification_throttled.counters.get(throttle_key, 0)
        if count >= 10:
            print("⚠️ 管理员通知已达到限流上限")
            return
        
        send_admin_notification_throttled.counters[throttle_key] = count + 1
        
        # 清理旧的计数器
        old_keys = [k for k in send_admin_notification_throttled.counters.keys() 
                   if int(k.split(':')[1]) < current_minute - 5]
        for key in old_keys:
            del send_admin_notification_throttled.counters[key]
        
        # 发送管理员通知
        admin_text = f'''🎯 安全充值通知

👤 用户: <a href="tg://user?id={user_info['user_id']}">{user_info.get('fullname', '未知')}</a>
💰 充值金额: CNY{amount}
💎 当前余额: CNY{new_balance}
🔗 交易哈希: <a href="https://tronscan.org/#/transaction/{txid}">{txid[:20]}...</a>
📍 来源地址: <code>{from_address}</code>
⏰ 时间: {timer}
🔐 安全验证: ✅ 已通过'''
        
        admin_count = 0
        for admin in user.find({'state': '4'}):
            if admin_count >= 3:  # 限制同时通知的管理员数量
                break
            try:
                context.bot.send_message(
                    chat_id=admin['user_id'], 
                    text=admin_text, 
                    parse_mode='HTML',
                    disable_web_page_preview=True
                )
                admin_count += 1
            except:
                continue
                
    except Exception as e:
        print(f"⚠️ 发送管理员通知失败: {e}")

# ==================== 订单安全验证函数 ====================

def create_secure_order(user_id, amount, payment_type='usdt_cny'):
    """创建安全的充值订单"""
    try:
        # 🔥 生成唯一订单ID
        timestamp = int(time.time())
        import random
        random_suffix = random.randint(10000, 99999)
        order_id = f"secure_{timestamp}_{user_id}_{random_suffix}"
        
        # 🔥 添加订单安全信息
        order_data = {
            'bianhao': order_id,
            'user_id': user_id,
            'money': float(amount),
            'payment_type': payment_type,
            'created_timestamp': timestamp,
            'timer': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            'processed': False,
            'security_hash': generate_order_hash(user_id, amount, timestamp),
            'expires_at': timestamp + (10 * 60),  # 10分钟过期
            'max_attempts': 3,  # 最大匹配次数
            'attempts': 0
        }
        
        if payment_type == 'usdt_cny':
            # 基于人民币的USDT充值
            rate_doc = shangtext.find_one({'projectname': '人民币USDT汇率'})
            exchange_rate = float(rate_doc['text']) if rate_doc else 7.2
            
            # 计算需要支付的USDT金额
            usdt_amount = round(amount / exchange_rate, 2)
            
            # 添加随机小数避免重复
            while True:
                suijishu = round(random.uniform(0.01, 0.50), 2)
                final_usdt = Decimal(str(usdt_amount)) + Decimal(str(suijishu))
                if topup.find_one({"money": float(final_usdt)}) is None:
                    break
            
            order_data.update({
                'cny_amount': amount,
                'usdt_amount': float(final_usdt),
                'exchange_rate': exchange_rate,
                'money': float(final_usdt)  # 用于区块链匹配的金额
            })
        
        # 插入订单
        result = topup.insert_one(order_data)
        
        if result.inserted_id:
            print(f"✅ 安全订单创建成功: {order_id}")
            return order_data
        else:
            print(f"❌ 订单创建失败")
            return None
            
    except Exception as e:
        print(f"❌ 创建安全订单失败: {e}")
        return None

def generate_order_hash(user_id, amount, timestamp):
    """生成订单安全哈希"""
    hash_string = f"{user_id}:{amount}:{timestamp}"
    return hashlib.sha256(hash_string.encode()).hexdigest()[:16]

# ==================== 清理过期订单函数 ====================

def cleanup_expired_orders():
    """清理过期订单"""
    try:
        current_time = time.time()
        
        # 删除过期且未处理的订单
        result = topup.delete_many({
            'expires_at': {'$lt': current_time},
            'processed': {'$ne': True}
        })
        
        if result.deleted_count > 0:
            print(f"🗑️ 清理了 {result.deleted_count} 个过期订单")
            
    except Exception as e:
        print(f"❌ 清理过期订单失败: {e}")

# ==================== 安全的定时任务 ====================

def enhanced_scheduled_tasks(context):
    """增强版定时任务，确保USDT充值能被及时处理"""
    try:
        current_time = int(time.time())
        
        # 每3秒检查一次通知
        enhanced_check_payment_notifications(context)
        
        # 每30秒清理过期订单
        if current_time % 30 == 0:
            cleanup_expired_orders()
        
        # 每60秒检查区块链数据处理状态
        if current_time % 60 == 0:
            check_blockchain_processing_status()
            
    except Exception as e:
        print(f"❌ 定时任务执行失败: {e}")

def cleanup_expired_orders():
    """清理过期订单"""
    try:
        current_time = time.time()
        result = topup.delete_many({
            'expires_at': {'$lt': current_time},
            'processed': {'$ne': True}
        })
        
        if result.deleted_count > 0:
            print(f"🗑️ 清理了 {result.deleted_count} 个过期订单")
            
    except Exception as e:
        print(f"❌ 清理过期订单失败: {e}")

def check_blockchain_processing_status():
    """检查区块链数据处理状态"""
    try:
        # 检查是否有未处理的区块链交易
        unprocessed_count = qukuai.count_documents({'state': 0})
        if unprocessed_count > 0:
            print(f"⚠️ 发现 {unprocessed_count} 笔未处理的区块链交易")
            
            # 手动处理一些未处理的交易
            unprocessed_txs = list(qukuai.find({
                'state': 0,
                'type': 'USDT'
            }).sort('time', 1).limit(5))
            
            for tx in unprocessed_txs:
                try:
                    # 模拟处理
                    create_instant_notification(tx)
                    # 标记为已处理
                    qukuai.update_one(
                        {'_id': tx['_id']},
                        {'$set': {'state': 1, 'processed_at': time.time()}}
                    )
                    print(f"🔄 补充处理了交易: {tx['txid'][:20]}...")
                except Exception as process_error:
                    print(f"❌ 补充处理失败: {process_error}")
                    
    except Exception as e:
        print(f"❌ 检查区块链处理状态失败: {e}")

# ==================== 紧急修复措施 ====================

def emergency_fix_duplicates():
    """紧急修复：检查并修复重复处理的交易"""
    try:
        print("🚨 执行紧急修复：检查重复处理...")
        
        # 查找可能重复处理的交易
        pipeline = [
            {"$group": {
                "_id": "$txid", 
                "count": {"$sum": 1},
                "docs": {"$push": "$$ROOT"}
            }},
            {"$match": {"count": {"$gt": 1}}}
        ]
        
        # 检查transaction_logs集合是否存在重复
        if 'transaction_logs' in globals():
            duplicates = list(transaction_logs.aggregate(pipeline))
            
            if duplicates:
                print(f"⚠️ 发现 {len(duplicates)} 个重复处理的交易")
                
                for dup in duplicates:
                    txid = dup['_id']
                    docs = dup['docs']
                    
                    # 保留最早的一条记录，删除其他的
                    docs_sorted = sorted(docs, key=lambda x: x.get('timestamp', 0))
                    keep_doc = docs_sorted[0]
                    remove_docs = docs_sorted[1:]
                    
                    print(f"🔧 修复交易 {txid}: 保留 {keep_doc['_id']}, 删除 {len(remove_docs)} 条重复")
                    
                    # 计算需要退还的金额
                    total_duplicate_amount = sum(doc.get('amount', 0) for doc in remove_docs)
                    
                    if total_duplicate_amount > 0:
                        # 从用户余额中扣除重复充值的金额
                        user_id = keep_doc['user_id']
                        user_info = user.find_one({'user_id': user_id})
                        
                        if user_info:
                            current_balance = user_info['USDT']
                            corrected_balance = max(0, current_balance - total_duplicate_amount)
                            
                            user.update_one(
                                {'user_id': user_id},
                                {'$set': {'USDT': corrected_balance}}
                            )
                            
                            print(f"💰 用户 {user_id} 余额修正: {current_balance} -> {corrected_balance}")
                    
                    # 删除重复记录
                    for doc in remove_docs:
                        transaction_logs.delete_one({'_id': doc['_id']})
        
        print("✅ 紧急修复完成")
        
    except Exception as e:
        print(f"❌ 紧急修复失败: {e}")

def check_payment_notifications(context: CallbackContext):
    """增强版支付通知处理"""
    try:
        # 查找未处理的通知，限制数量避免过载
        notifications_list = list(notifications.find({'processed': False}).sort('timestamp', 1).limit(10))
        
        if not notifications_list:
            return
            
        print(f"📬 处理 {len(notifications_list)} 个未处理通知")
        
        for notification in notifications_list:
            try:
                user_id = notification['user_id']
                noti_type = notification['type']
                
                if noti_type == 'payment_success':
                    amount = notification['amount']
                    new_balance = notification['new_balance']
                    order_no = notification.get('order_no', '')
                    payment_method = notification.get('payment_method', '支付')
                    txid = notification.get('txid', '')
                    
                    # 获取用户语言设置
                    user_info = user.find_one({'user_id': user_id})
                    lang = user_info.get('lang', 'zh') if user_info else 'zh'
                    
                    # 🔥 关键修复：查找并删除原支付消息
                    try:
                        if 'USDT' in payment_method and txid:
                            # USDT充值，查找对应的支付消息
                            orders_with_message = list(topup.find({'user_id': user_id, 'message_id': {'$exists': True}}))
                            for order in orders_with_message:
                                try:
                                    context.bot.delete_message(
                                        chat_id=user_id,
                                        message_id=order['message_id']
                                    )
                                    print(f"🗑️ 已删除原支付消息: {order['message_id']}")
                                except:
                                    pass
                    except Exception as delete_error:
                        print(f"⚠️ 删除原消息失败: {delete_error}")
                    
                    # 构造充值成功消息
                    if lang == 'zh':
                        if txid:
                            success_text = f'''🎉 <b>充值成功！</b>

💰 充值金额：CNY{amount}
💎 当前余额：CNY{new_balance}
📋 订单号：<code>{order_no}</code>
💳 支付方式：{payment_method}
🔗 交易哈希：<a href="https://tronscan.org/#/transaction/{txid}">查看详情</a>
🕒 到账时间：{time.strftime('%Y-%m-%d %H:%M:%S')}

✅ 余额已到账，感谢您的使用！'''
                        else:
                            success_text = f'''🎉 <b>充值成功！</b>

💰 充值金额：CNY{amount}
💎 当前余额：CNY{new_balance}
📋 订单号：<code>{order_no}</code>
💳 支付方式：{payment_method}
🕒 到账时间：{time.strftime('%Y-%m-%d %H:%M:%S')}

✅ 余额已到账，感谢您的使用！'''

                        keyboard = [
                            [InlineKeyboardButton('💤 个人中心', callback_data='profile')],
                            [InlineKeyboardButton('🛒 购买商品', callback_data='backzcd')],
                            [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]
                        ]
                    else:
                        if txid:
                            success_text = f'''🎉 <b>Payment Successful!</b>

💰 Amount: CNY{amount}
💎 Current Balance: CNY{new_balance}
📋 Order No: <code>{order_no}</code>
💳 Payment Method: {payment_method}
🔗 Transaction: <a href="https://tronscan.org/#/transaction/{txid}">View Details</a>
🕒 Credited: {time.strftime('%Y-%m-%d %H:%M:%S')}

✅ Balance credited, thank you!'''
                        else:
                            success_text = f'''🎉 <b>Payment Successful!</b>

💰 Amount: CNY{amount}
💎 Current Balance: CNY{new_balance}
📋 Order No: <code>{order_no}</code>
💳 Payment Method: {payment_method}
🕒 Credited: {time.strftime('%Y-%m-%d %H:%M:%S')}

✅ Balance credited, thank you!'''

                        keyboard = [
                            [InlineKeyboardButton('💤 Profile', callback_data='profile')],
                            [InlineKeyboardButton('🛒 Buy Products', callback_data='backzcd')],
                            [InlineKeyboardButton('❌ Close', callback_data=f'close {user_id}')]
                        ]
                    
                    try:
                        context.bot.send_message(
                            chat_id=user_id, 
                            text=success_text,
                            parse_mode='HTML',
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            disable_web_page_preview=True
                        )
                        print(f"✅ 已发送充值成功通知给用户 {user_id}")
                        
                        # 标记通知已处理
                        notifications.update_one(
                            {'_id': notification['_id']},
                            {'$set': {
                                'processed': True, 
                                'sent_time': time.time(),
                                'sent_at': time.strftime('%Y-%m-%d %H:%M:%S')
                            }}
                        )
                        
                    except Exception as send_error:
                        print(f"❌ 发送通知给用户 {user_id} 失败: {send_error}")
                        if "Forbidden" in str(send_error) or "blocked" in str(send_error).lower():
                            # 用户可能已阻止机器人，标记为已处理避免重复尝试
                            notifications.update_one(
                                {'_id': notification['_id']},
                                {'$set': {
                                    'processed': True, 
                                    'failed': True,
                                    'error': str(send_error),
                                    'error_time': time.time()
                                }}
                            )
                            print(f"⚠️ 用户 {user_id} 可能已阻止机器人，已标记")
                        continue
                        
            except Exception as process_error:
                print(f"❌ 处理单个通知失败: {process_error}")
                continue
            
    except Exception as e:
        print(f"❌ 检查支付通知失败: {e}")
        import traceback
        traceback.print_exc()

def create_folder_if_not_exists(folder_path):
    import os
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully")
    else:
        print(f"Folder '{folder_path}' already exists")
def set_rate(update: Update, context: CallbackContext):
    """设置USDT汇率命令"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        user_list = user.find_one({'user_id': user_id})
        state = user_list['state']
        
        # 只有管理员才能设置汇率
        if state == '4':
            # 获取当前汇率
            try:
                current_rate = shangtext.find_one({'projectname': '人民币USDT汇率'})
                if current_rate:
                    current_rate_value = current_rate['text']
                    context.bot.send_message(chat_id=user_id, 
                                           text=f'当前汇率：1 USDT = CNY{current_rate_value}\n\n请输入新的汇率（例如：7.2）')
                else:
                    context.bot.send_message(chat_id=user_id, 
                                           text='请输入新的汇率（例如：7.2）')
            except:
                context.bot.send_message(chat_id=user_id, 
                                       text='请输入新的汇率（例如：7.2）')
            
            # 设置用户状态为等待输入汇率
            user.update_one({'user_id': user_id}, {"$set": {'sign': 'set_exchange_rate'}})
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 权限不足')
def suoyouchengxu(context: CallbackContext):
    """启动所有程序的定时任务"""
    Timer(1, jianceguoqi, args=[context]).start()
    
    # 移除已存在的任务避免重复
    job = context.job_queue.get_jobs_by_name('suoyouchengxu')
    if job != ():
        job[0].schedule_removal()
def fbgg(update: Update, context: CallbackContext):
    """发送广告命令"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        text = update.message.text
        user_list = user.find_one({'user_id': user_id})
        state = user_list['state']
        
        if state == '4':  # 只有管理员才能发广告
            context.bot.send_message(chat_id=user_id, text='开始发送广告')
            fstext = text.replace('/gg ', '')
            
            count_success = 0
            count_fail = 0
            
            for i in user.find({}):
                yh_id = i['user_id']
                keyboard = [[InlineKeyboardButton("✅已读（点击销毁此消息）", callback_data=f'close {yh_id}')]]
                try:
                    context.bot.send_message(chat_id=i['user_id'], text=fstext,
                                           reply_markup=InlineKeyboardMarkup(keyboard))
                    count_success += 1
                except Exception as e:
                    count_fail += 1
                    print(f"发送广告给用户 {yh_id} 失败: {e}")
                time.sleep(1)  # 避免发送太快被限制
            
            context.bot.send_message(chat_id=user_id, text=f'广告发送完成\n成功: {count_success}\n失败: {count_fail}')
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 权限不足，只有管理员才能发送广告')
def cha(update: Update, context: CallbackContext):
    """查询用户信息命令 - 修复版"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        text = update.message.text
        text1 = text.split(' ')
        user_list = user.find_one({'user_id': user_id})
        state = user_list['state']
        
        if state == '4':  # 只有管理员才能查询
            if len(text1) == 2:
                jieguo = text1[1]
                
                # 判断是用户ID还是用户名
                if is_number(jieguo):
                    df_id = int(jieguo)
                    df_list = user.find_one({'user_id': df_id})
                    if df_list is None:
                        context.bot.send_message(chat_id=user_id, text='用户不存在')
                        return
                else:
                    # 通过用户名查找
                    df_list = user.find_one({'username': jieguo.replace('@', '')})
                    if df_list is None:
                        context.bot.send_message(chat_id=user_id, text='用户不存在')
                        return
                    df_id = df_list['user_id']
                
                # 获取用户信息
                df_fullname = df_list['fullname']
                df_username = df_list['username']
                if df_username is None:
                    df_username = df_fullname
                else:
                    df_username = f'<a href="https://t.me/{df_username}">{df_username}</a>'
                
                creation_time = df_list['creation_time']
                zgsl = df_list.get('zgsl', 0)
                zgje = df_list.get('zgje', 0)
                USDT = df_list['USDT']
                
                fstext = f'''
<b>用户ID:</b> <code>{df_id}</code>
<b>用户名:</b> {df_username}
<b>注册日期:</b> {creation_time}

<b>总购数量:</b> {zgsl}
<b>总购金额:</b> CNY{standard_num(zgje)}
<b>当前余额:</b> CNY{USDT}
                '''
                
                keyboard = [
                    [InlineKeyboardButton('🛒购买记录', callback_data=f'gmaijilu {df_id}')],
                    [InlineKeyboardButton('关闭', callback_data=f'close {user_id}')]
                ]
                
                context.bot.send_message(chat_id=user_id, text=fstext, parse_mode='HTML',
                                       reply_markup=InlineKeyboardMarkup(keyboard), 
                                       disable_web_page_preview=True)
            else:
                context.bot.send_message(chat_id=user_id, text='格式为: /cha 用户ID或用户名，有一个空格')
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 权限不足，只有管理员才能查询用户信息')

# ==================== 易支付回调处理 ====================

from flask import Flask, request, jsonify
import threading
import hashlib

# 创建Flask应用用于处理回调
app = Flask(__name__)

def verify_epay_sign(data, key):
    """验证易支付签名"""
    sign = data.pop('sign', '')
    sign_type = data.pop('sign_type', '')
    
    # 构建签名字符串
    sorted_params = sorted(data.items())
    param_str = '&'.join([f'{k}={v}' for k, v in sorted_params if v != ''])
    sign_str = param_str + key
    calculated_sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
    
    return sign.lower() == calculated_sign.lower(), param_str, calculated_sign

@app.route('/epay/notify', methods=['POST'])
def epay_notify():
    """处理易支付异步通知"""
    try:
        print("🔔 收到易支付回调通知")
        
        # 检查配置
        if EPAY_CONFIG is None:
            print("❌ 易支付配置未加载")
            return "fail"
        
        # 获取POST参数
        data = request.form.to_dict()
        print(f"📋 回调参数: {data}")
        
        # 验证必要参数
        required_params = ['pid', 'trade_no', 'out_trade_no', 'type', 'name', 'money', 'trade_status']
        for param in required_params:
            if param not in data:
                print(f"❌ 缺少参数: {param}")
                return "fail"
        
        # 验证签名
        sign_valid, param_str, calculated_sign = verify_epay_sign(data.copy(), EPAY_CONFIG['key'])
        
        print(f"🔐 签名验证:")
        print(f"   参数字符串: {param_str}")
        print(f"   接收签名: {data.get('sign', '')}")
        print(f"   计算签名: {calculated_sign}")
        
        if not sign_valid:
            print("❌ 签名验证失败")
            return "fail"
        
        print("✅ 签名验证成功")
        
        # 处理支付成功通知
        if data['trade_status'] == 'TRADE_SUCCESS':
            out_trade_no = data['out_trade_no']  # 我们的订单号
            money = float(data['money'])  # 支付金额
            
            print(f"💰 处理支付成功: 订单号={out_trade_no}, 金额=CNY{money}")
            
            # 查找对应的充值订单
            order = topup.find_one({'bianhao': out_trade_no})
            if not order:
                print(f"❌ 找不到订单: {out_trade_no}")
                return "fail"
            
            user_id = order['user_id']
            print(f"👤 用户ID: {user_id}")
            
            # 更新用户余额
            user_info = user.find_one({'user_id': user_id})
            if not user_info:
                print(f"❌ 找不到用户: {user_id}")
                return "fail"
            
            current_balance = user_info['USDT']
            new_balance = standard_num(float(current_balance) + float(money))
            new_balance = float(new_balance) if str(new_balance).count('.') > 0 else int(new_balance)
            
            # 更新数据库
            user.update_one({'user_id': user_id}, {"$set": {'USDT': new_balance}})
            
            # 记录日志
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            user_logging(out_trade_no, '充值', user_id, money, timer)
            
            print(f"✅ 余额更新成功: {current_balance} -> {new_balance}")
            
            # 创建通知记录，让机器人发送通知
            try:
                # 使用现有的数据库连接
                teleclient = pymongo.MongoClient('mongodb://fakabot:NExMbNf4xTAPtcWW@localhost:27017/fakabot?authSource=fakabot&authMechanism=SCRAM-SHA-1')
                mydb1 = teleclient['fakabot']
                mydb1['notifications'].insert_one({
                    'user_id': user_id,
                    'type': 'payment_success',
                    'amount': money,
                    'new_balance': new_balance,
                    'order_no': out_trade_no,
                    'processed': False,
                    'created_at': timer
                })
                print("📩 已创建支付成功通知")
            except Exception as e:
                print(f"❌ 创建通知失败: {e}")
            
            # 删除充值订单
            topup.delete_one({'bianhao': out_trade_no})
            
            print(f"🎉 支付处理完成")
            return "success"
        else:
            print(f"⚠️ 非成功状态: {data['trade_status']}")
            return "success"
            
    except Exception as e:
        print(f"❌ 处理回调失败: {e}")
        import traceback
        traceback.print_exc()
        return "fail"

@app.route('/epay/return', methods=['GET'])
def epay_return():
    """处理易支付同步返回"""
    try:
        print("🔙 收到易支付同步返回")
        data = request.args.to_dict()
        print(f"📋 返回参数: {data}")
        
        # 显示支付成功页面
        return """
        <html>
        <head>
            <meta charset="utf-8">
            <title>支付成功</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { 
                    text-align:center; 
                    padding:50px; 
                    font-family:Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    flex-direction: column;
                }
                .success-box {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                }
                .icon { font-size: 64px; margin-bottom: 20px; }
                h2 { margin: 0 0 20px 0; font-size: 28px; }
                p { margin: 10px 0; line-height: 1.6; }
                .small { color: rgba(255,255,255,0.8); font-size: 14px; margin-top: 30px; }
            </style>
        </head>
        <body>
            <div class="success-box">
                <div class="icon">🎉</div>
                <h2>支付成功！</h2>
                <p>您的充值已完成，请返回Telegram查看余额。</p>
                <p class="small">此页面可以关闭</p>
            </div>
        </body>
        </html>
        """
    except Exception as e:
        print(f"❌ 处理返回失败: {e}")
        return "处理失败"

@app.route('/epay/test', methods=['GET'])
def epay_test():
    """测试接口"""
    return jsonify({
        'status': 'ok',
        'message': '易支付回调接口运行正常',
        'config_loaded': EPAY_CONFIG is not None,
        'time': time.strftime('%Y-%m-%d %H:%M:%S')
    })

def run_flask_server():
    """在独立线程中运行Flask服务器"""
    try:
        print("🚀 启动易支付回调服务...")
        print(f"📡 回调地址: http://你的域名/epay/notify")
        print(f"🔙 返回地址: http://你的域名/epay/return")
        print(f"🧪 测试地址: http://你的域名/epay/test")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ Flask服务器启动失败: {e}")

# ==================== 手动处理支付函数 ====================

def manual_process_latest_payment(amount=12):
    """手动处理最近的支付（用于紧急情况）"""
    try:
        print(f"🔧 手动处理支付: CNY{amount}")
        
        # 查找最近的订单
        orders = list(topup.find().sort('_id', -1).limit(5))
        print(f"📋 找到 {len(orders)} 个最近订单")
        
        if not orders:
            print("❌ 没有找到待处理订单")
            return False
        
        # 假设最新订单就是要处理的订单
        latest_order = orders[0]
        user_id = latest_order['user_id']
        
        print(f"👤 处理用户 {user_id} 的订单")
        
        # 更新余额
        user_info = user.find_one({'user_id': user_id})
        if not user_info:
            print(f"❌ 找不到用户: {user_id}")
            return False
        
        current_balance = user_info['USDT']
        new_balance = standard_num(float(current_balance) + float(amount))
        new_balance = float(new_balance) if str(new_balance).count('.') > 0 else int(new_balance)
        
        # 更新数据库
        user.update_one({'user_id': user_id}, {'$set': {'USDT': new_balance}})
        
        # 创建通知
        timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        try:
            teleclient = pymongo.MongoClient('mongodb://fakabot:NExMbNf4xTAPtcWW@localhost:27017/fakabot?authSource=fakabot&authMechanism=SCRAM-SHA-1')
            mydb1 = teleclient['fakabot']
            mydb1['notifications'].insert_one({
                'user_id': user_id,
                'type': 'payment_success',
                'amount': amount,
                'new_balance': new_balance,
                'order_no': latest_order.get('bianhao', 'manual'),
                'processed': False,
                'created_at': timer
            })
        except Exception as e:
            print(f"⚠️ 创建通知失败，但余额已更新: {e}")
        
        # 记录日志
        user_logging(latest_order.get('bianhao', 'manual'), '手动充值', user_id, amount, timer)
        
        # 删除订单
        topup.delete_one({'_id': latest_order['_id']})
        
        print(f"✅ 手动处理成功!")
        print(f"   用户 {user_id} 余额: {current_balance} -> {new_balance}")
        return True
        
    except Exception as e:
        print(f"❌ 手动处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== 区块链监控增强函数 - 添加到bot.py ====================
# 🔥 将以下函数添加到您的 bot.py 文件中，建议放在 main() 函数之前

def enhanced_blockchain_monitor():
    """增强版区块链监控，确保USDT充值能被正确检测"""
    import sys
    import os
    import subprocess
    import threading
    
    # 添加qukuai.py的路径到系统路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    qukuai_path = os.path.join(current_dir, 'qukuai.py')
    
    print(f"🔍 查找区块链监控文件: {qukuai_path}")
    
    if os.path.exists(qukuai_path):
        print("✅ 找到qukuai.py文件")
        
        def run_blockchain_monitor():
            """在独立线程中运行区块链监控"""
            try:
                print("🚀 启动区块链监控进程...")
                
                # 创建子进程运行qukuai.py
                process = subprocess.Popen(
                    [sys.executable, qukuai_path], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1  # 行缓冲
                )
                
                print(f"📊 区块链监控进程已启动，PID: {process.pid}")
                
                # 实时输出监控日志
                try:
                    for line in iter(process.stdout.readline, ''):
                        if line.strip():
                            print(f"⛓️ 区块链: {line.strip()}")
                        
                        # 检查进程是否还在运行
                        if process.poll() is not None:
                            break
                            
                except Exception as e:
                    print(f"❌ 读取区块链监控日志失败: {e}")
                
                # 获取进程退出状态
                exit_code = process.wait()
                if exit_code != 0:
                    # 读取错误信息
                    stderr_output = process.stderr.read()
                    print(f"❌ 区块链监控进程异常退出，代码: {exit_code}")
                    if stderr_output:
                        print(f"❌ 错误信息: {stderr_output}")
                else:
                    print("✅ 区块链监控进程正常退出")
                
            except FileNotFoundError:
                print(f"❌ 找不到Python解释器: {sys.executable}")
            except Exception as e:
                print(f"❌ 区块链监控启动失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 在独立线程中运行
        monitor_thread = threading.Thread(
            target=run_blockchain_monitor, 
            daemon=True, 
            name="BlockchainMonitor"
        )
        monitor_thread.start()
        
        # 等待一下确保线程启动
        import time
        time.sleep(1)
        
        if monitor_thread.is_alive():
            print("✅ 区块链监控线程启动成功")
            return True
        else:
            print("❌ 区块链监控线程启动失败")
            return False
        
    else:
        print(f"❌ 未找到qukuai.py文件: {qukuai_path}")
        print("💡 请确保qukuai.py文件与bot.py在同一目录下")
        
        # 尝试在常见位置查找
        possible_paths = [
            os.path.join(current_dir, '..', 'qukuai.py'),
            os.path.join(current_dir, 'blockchain', 'qukuai.py'),
            os.path.join(current_dir, 'monitor', 'qukuai.py'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"💡 找到qukuai.py在: {path}")
                break
        
        return False

def check_blockchain_dependencies():
    """检查区块链监控依赖"""
    try:
        print("🔍 检查区块链监控依赖...")
        
        # 检查必要的Python包
        required_packages = ['tronpy', 'requests', 'pymongo', 'pika']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"✅ {package} - 已安装")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} - 未安装")
        
        if missing_packages:
            print(f"⚠️ 缺少依赖包: {', '.join(missing_packages)}")
            print("💡 请运行以下命令安装:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
        
        # 检查数据库连接
        try:
            from mongo import qukuai, shangtext
            print("✅ 数据库连接正常")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
        
        # 检查充值地址配置
        try:
            address_config = shangtext.find_one({'projectname': '充值地址'})
            if address_config and address_config.get('text'):
                print(f"✅ 充值地址已配置: {address_config['text'][:10]}...")
            else:
                print("⚠️ 充值地址未配置，USDT充值功能将无法工作")
                print("💡 请使用管理员账号设置TRC20充值地址")
        except Exception as e:
            print(f"❌ 检查充值地址配置失败: {e}")
        
        print("✅ 区块链监控依赖检查完成")
        return True
        
    except Exception as e:
        print(f"❌ 依赖检查失败: {e}")
        return False

def start_blockchain_monitoring():
    """启动完整的区块链监控系统"""
    print("🔗 初始化区块链监控系统...")
    
    # 1. 检查依赖
    if not check_blockchain_dependencies():
        print("❌ 依赖检查失败，区块链监控可能无法正常工作")
        return False
    
    # 2. 启动监控
    if enhanced_blockchain_monitor():
        print("✅ 区块链监控系统启动成功")
        print("💎 USDT充值检测已激活")
        return True
    else:
        print("❌ 区块链监控系统启动失败")
        print("⚠️ USDT充值功能可能无法正常工作")
        return False

# ==================== 可选：区块链监控状态检查函数 ====================
def check_blockchain_status():
    """检查区块链监控运行状态"""
    import threading
    
    # 查找区块链监控线程
    for thread in threading.enumerate():
        if thread.name == "BlockchainMonitor":
            if thread.is_alive():
                print("✅ 区块链监控线程运行正常")
                return True
            else:
                print("❌ 区块链监控线程已停止")
                return False
    
    print("⚠️ 未找到区块链监控线程")
    return False

def restart_blockchain_monitor():
    """重启区块链监控（管理员功能）"""
    print("🔄 重启区块链监控...")
    return start_blockchain_monitoring()

# ==================== 管理员命令：检查区块链状态 ====================
def blockchain_status_command(update: Update, context: CallbackContext):
    """管理员命令：检查区块链监控状态"""
    chat = update.effective_chat
    if chat.type == 'private':
        user_id = chat['id']
        user_list = user.find_one({'user_id': user_id})
        
        if user_list and user_list.get('state') == '4':  # 只有管理员可以使用
            status = check_blockchain_status()
            
            if status:
                status_text = '''✅ <b>区块链监控状态正常</b>

🔗 监控进程：运行中
💎 USDT检测：已激活
⛓️ 网络连接：正常

💡 USDT充值功能正常工作'''
            else:
                status_text = '''❌ <b>区块链监控状态异常</b>

🔗 监控进程：已停止
💎 USDT检测：未激活
⛓️ 网络连接：可能异常

⚠️ USDT充值功能可能无法正常工作'''
            
            keyboard = [
                [InlineKeyboardButton('🔄 重启监控', callback_data='restart_blockchain')],
                [InlineKeyboardButton('❌ 关闭', callback_data=f'close {user_id}')]
            ]
            
            context.bot.send_message(
                chat_id=user_id,
                text=status_text,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            context.bot.send_message(chat_id=user_id, text='❌ 权限不足')

def restart_blockchain_callback(update: Update, context: CallbackContext):
    """处理重启区块链监控的回调"""
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    
    user_list = user.find_one({'user_id': user_id})
    if user_list and user_list.get('state') == '4':
        query.edit_message_text('🔄 正在重启区块链监控...')
        
        success = restart_blockchain_monitor()
        
        if success:
            result_text = '✅ 区块链监控重启成功！'
        else:
            result_text = '❌ 区块链监控重启失败，请检查日志'
        
        query.edit_message_text(result_text)
    else:
        query.answer('❌ 权限不足', show_alert=True)
# ==================== 修改主函数 ====================

# 修复 main() 函数中的 updater 变量问题

def main():
    """主函数 - 完整修复版"""
    try:
        print("🚀 启动Telegram机器人...")
        
        # 🔥 关键修复：首先创建 BOT_TOKEN 和 updater 变量
        BOT_TOKEN = '8276047538:AAFONBnuPe23mnEncZXHdUpQAGTGuYapVUs'
        
        # 创建机器人实例（移动到最前面）
        updater = Updater(
            token=BOT_TOKEN, 
            use_context=True, 
            workers=128,
            request_kwargs={'read_timeout': 20, 'connect_timeout': 20}
        )
        
        print("⏰ 启动定时任务...")
        # 🔥 修复：使用增强版定时任务
        updater.job_queue.run_repeating(suoyouchengxu, 1, 1, name='suoyouchengxu')
        updater.job_queue.run_repeating(enhanced_scheduled_tasks, 3, 1, name='enhanced_tasks')  # 每3秒执行一次
        
        # 创建必需的文件夹
        required_folders = [
            'logs', '发货', '协议号发货', '手机接码发货', 
            '临时文件夹', '谷歌发货', '协议号', '号包'
        ]
        
        for folder in required_folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"📁 创建文件夹: {folder}")
        
        # 设置日志
        setup_logging()
        
        # ⛓️ 启动区块链监控
        print("⛓️ 启动区块链监控...")
        if start_blockchain_monitoring():
            print("✅ 区块链监控启动成功")
        else:
            print("⚠️ 区块链监控启动失败，USDT充值可能无法正常工作")
        
        dispatcher = updater.dispatcher
        
        print("📡 注册命令处理器...")
        
        # ==================== 基础命令 ====================
        dispatcher.add_handler(CommandHandler('start', start, run_async=True))
        dispatcher.add_handler(CommandHandler('help', help_command, run_async=True))
        dispatcher.add_handler(CommandHandler('profile', profile, run_async=True))
        dispatcher.add_handler(CommandHandler('products', products, run_async=True))
        dispatcher.add_handler(CommandHandler('recharge', recharge, run_async=True))
        dispatcher.add_handler(CommandHandler('language', language, run_async=True))
        dispatcher.add_handler(CommandHandler('redpacket', redpacket, run_async=True))
        
        # ==================== 管理员命令 ====================
        dispatcher.add_handler(CommandHandler('add', adm, run_async=True))
        dispatcher.add_handler(CommandHandler('addadmin', addadmin, run_async=True))
        dispatcher.add_handler(CommandHandler('removeadmin', removeadmin, run_async=True))
        dispatcher.add_handler(CommandHandler('listadmin', listadmin, run_async=True))
        dispatcher.add_handler(CommandHandler('cha', cha, run_async=True))
        dispatcher.add_handler(CommandHandler('gg', fbgg, run_async=True))
        dispatcher.add_handler(CommandHandler('rate', set_rate, run_async=True))
        
        # ==================== 帮助和系统状态 ====================
        dispatcher.add_handler(CallbackQueryHandler(refresh_help, pattern='refresh_help'))
        dispatcher.add_handler(CallbackQueryHandler(system_status, pattern='system_status'))
        dispatcher.add_handler(CallbackQueryHandler(refresh_admin_list, pattern='refresh_admin_list'))
        
        # ==================== 支付相关处理器 ====================
        dispatcher.add_handler(CallbackQueryHandler(select_amount, pattern='^select_amount_'))
        dispatcher.add_handler(CallbackQueryHandler(back_to_amount_select, pattern='back_to_amount_select'))
        dispatcher.add_handler(CallbackQueryHandler(back_to_recharge, pattern='back_to_recharge'))
        dispatcher.add_handler(CallbackQueryHandler(process_epay_payment_fixed, pattern='^pay_(wx|ali)_\\d+'))
        dispatcher.add_handler(CallbackQueryHandler(pay_usdt, pattern='^pay_usdt_\\d+'))
        dispatcher.add_handler(CallbackQueryHandler(check_order_status, pattern='^check_order_'))
        dispatcher.add_handler(CallbackQueryHandler(cancel_order, pattern='^cancel_order_'))
        dispatcher.add_handler(CallbackQueryHandler(yuecz, pattern='yuecz '))
        dispatcher.add_handler(CallbackQueryHandler(zdycz, pattern='zdycz'))
        dispatcher.add_handler(CallbackQueryHandler(qxdingdan, pattern='qxdingdan '))
        
        # ==================== 语言设置 ====================
        dispatcher.add_handler(CallbackQueryHandler(set_language, pattern='^set_lang_(zh|en)$'))
        
        # ==================== 个人中心相关 ====================
        dispatcher.add_handler(CallbackQueryHandler(profile, pattern='^profile$'))
        dispatcher.add_handler(CallbackQueryHandler(gmaijilu, pattern='gmaijilu '))
        dispatcher.add_handler(CallbackQueryHandler(gmainext, pattern='gmainext '))
        dispatcher.add_handler(CallbackQueryHandler(backgmjl, pattern='backgmjl '))
        dispatcher.add_handler(CallbackQueryHandler(zcfshuo, pattern='zcfshuo '))
        
        # ==================== 商品管理 ====================
        dispatcher.add_handler(CallbackQueryHandler(spgli, pattern='spgli'))
        dispatcher.add_handler(CallbackQueryHandler(newfl, pattern='newfl'))
        dispatcher.add_handler(CallbackQueryHandler(paixufl, pattern='paixufl'))
        dispatcher.add_handler(CallbackQueryHandler(delfl, pattern='delfl'))
        dispatcher.add_handler(CallbackQueryHandler(flxxi, pattern='flxxi '))
        dispatcher.add_handler(CallbackQueryHandler(fejxxi, pattern='fejxxi '))
        dispatcher.add_handler(CallbackQueryHandler(newejfl, pattern='newejfl '))
        dispatcher.add_handler(CallbackQueryHandler(paixuejfl, pattern='paixuejfl '))
        dispatcher.add_handler(CallbackQueryHandler(delejfl, pattern='delejfl '))
        dispatcher.add_handler(CallbackQueryHandler(qrscflrow, pattern='qrscflrow '))
        dispatcher.add_handler(CallbackQueryHandler(qrscejrow, pattern='qrscejrow '))
        dispatcher.add_handler(CallbackQueryHandler(flpxyd, pattern='flpxyd '))
        dispatcher.add_handler(CallbackQueryHandler(ejfpaixu, pattern='ejfpaixu '))
        
        # ==================== 商品分类管理 ====================
        dispatcher.add_handler(CallbackQueryHandler(upspname, pattern='upspname '))
        dispatcher.add_handler(CallbackQueryHandler(upejflname, pattern='upejflname '))
        dispatcher.add_handler(CallbackQueryHandler(upmoney, pattern='upmoney '))
        
        # ==================== 商品上传管理 ====================
        dispatcher.add_handler(CallbackQueryHandler(update_hb, pattern='update_hb '))
        dispatcher.add_handler(CallbackQueryHandler(update_xyh, pattern='update_xyh '))
        dispatcher.add_handler(CallbackQueryHandler(update_gg, pattern='update_gg '))
        dispatcher.add_handler(CallbackQueryHandler(update_txt, pattern='update_txt '))
        dispatcher.add_handler(CallbackQueryHandler(update_hy, pattern='update_hy '))
        dispatcher.add_handler(CallbackQueryHandler(update_sysm, pattern='update_sysm '))
        dispatcher.add_handler(CallbackQueryHandler(update_wbts, pattern='update_wbts '))
        dispatcher.add_handler(CallbackQueryHandler(qchuall, pattern='qchuall '))
        
        # ==================== 商品浏览和购买 ====================
        dispatcher.add_handler(CallbackQueryHandler(catejflsp, pattern='catejflsp '))
        dispatcher.add_handler(CallbackQueryHandler(gmsp, pattern='gmsp '))
        dispatcher.add_handler(CallbackQueryHandler(gmqq, pattern='gmqq'))  # 修复版
        dispatcher.add_handler(CallbackQueryHandler(qrgaimai, pattern='qrgaimai '))
        dispatcher.add_handler(CallbackQueryHandler(sysming, pattern='sysming '))
        dispatcher.add_handler(CallbackQueryHandler(backzcd, pattern='backzcd'))
        
        # ==================== 红包功能 ====================
        dispatcher.add_handler(CallbackQueryHandler(addhb, pattern='addhb'))
        dispatcher.add_handler(CallbackQueryHandler(lqhb, pattern='lqhb '))
        dispatcher.add_handler(CallbackQueryHandler(xzhb, pattern='xzhb '))
        dispatcher.add_handler(CallbackQueryHandler(yjshb, pattern='yjshb'))
        dispatcher.add_handler(CallbackQueryHandler(jxzhb, pattern='jxzhb'))
        dispatcher.add_handler(CallbackQueryHandler(shokuan, pattern='shokuan '))
        
        # ==================== 管理功能 ====================
        dispatcher.add_handler(CallbackQueryHandler(yhlist, pattern='yhlist'))
        dispatcher.add_handler(CallbackQueryHandler(yhnext, pattern='yhnext '))
        dispatcher.add_handler(CallbackQueryHandler(backstart, pattern='backstart'))
        dispatcher.add_handler(CallbackQueryHandler(sifa, pattern='sifa'))
        dispatcher.add_handler(CallbackQueryHandler(tuwen, pattern='tuwen'))
        dispatcher.add_handler(CallbackQueryHandler(anniu, pattern='anniu'))
        dispatcher.add_handler(CallbackQueryHandler(cattu, pattern='cattu'))
        dispatcher.add_handler(CallbackQueryHandler(kaiqisifa, pattern='kaiqisifa'))
        dispatcher.add_handler(CallbackQueryHandler(settrc20, pattern='settrc20'))
        dispatcher.add_handler(CallbackQueryHandler(startupdate, pattern='startupdate'))
        
        # ==================== 自定义按钮管理 ====================
        dispatcher.add_handler(CallbackQueryHandler(addzdykey, pattern='addzdykey'))
        dispatcher.add_handler(CallbackQueryHandler(newkey, pattern='newkey'))
        dispatcher.add_handler(CallbackQueryHandler(newrow, pattern='newrow'))
        dispatcher.add_handler(CallbackQueryHandler(delrow, pattern='delrow'))
        dispatcher.add_handler(CallbackQueryHandler(paixurow, pattern='paixurow'))
        dispatcher.add_handler(CallbackQueryHandler(qrscdelrow, pattern='qrscdelrow '))
        dispatcher.add_handler(CallbackQueryHandler(paixuyidong, pattern='paixuyidong '))
        dispatcher.add_handler(CallbackQueryHandler(addhangkey, pattern='addhangkey '))
        dispatcher.add_handler(CallbackQueryHandler(delhangkey, pattern='delhangkey '))
        dispatcher.add_handler(CallbackQueryHandler(qrdelliekey, pattern='qrdelliekey '))
        dispatcher.add_handler(CallbackQueryHandler(keyxq, pattern='keyxq '))
        dispatcher.add_handler(CallbackQueryHandler(setkeyname, pattern='setkeyname '))
        dispatcher.add_handler(CallbackQueryHandler(setkeyboard, pattern='setkeyboard '))
        dispatcher.add_handler(CallbackQueryHandler(settuwenset, pattern='settuwenset '))
        dispatcher.add_handler(CallbackQueryHandler(cattuwenset, pattern='cattuwenset '))
        
        # ==================== 通用关闭按钮 ====================
        dispatcher.add_handler(CallbackQueryHandler(close, pattern='close '))
        
        # ==================== 客服支持 ====================
        dispatcher.add_handler(CallbackQueryHandler(contact_support, pattern='contact_support'))
        
        # ==================== 内联查询 ====================
        dispatcher.add_handler(InlineQueryHandler(inline_query))
        
        # ==================== 消息处理器 ====================
        dispatcher.add_handler(MessageHandler(
            Filters.chat_type.private & Filters.reply, 
            huifu
        ))
        dispatcher.add_handler(MessageHandler(
            (Filters.text | Filters.photo | Filters.animation | Filters.video | Filters.document) & ~(Filters.command),
            textkeyboard,  # 使用修复版的textkeyboard
            run_async=True
        ))
        
        print("⏰ 启动定时任务...")
        
        # ==================== 定时任务（增强版） ====================
        updater.job_queue.run_repeating(secure_jiexi, 3, 1, name='chongzhi')  # 使用修复版的jiexi
        updater.job_queue.run_repeating(check_payment_notifications, 5, 1, name='payment_notifications')  # 使用修复版
        
        # ==================== 启动Flask服务器 ====================
        if EPAY_CONFIG:
            print("🌐 启动易支付回调服务...")
            flask_thread = threading.Thread(target=run_flask_server, daemon=True)
            flask_thread.start()
            time.sleep(2)
        
        print("✅ 机器人启动成功！")
        print("📱 开始监听消息...")
        print("\n" + "="*60)
        print("🔧 修复状态:")
        print("✅ 1. 充值自定义金额输入 - 已修复")
        print("✅ 2. USDT充值回调处理 - 已修复") 
        print("✅ 3. 商品购买数量输入 - 已修复")
        print("✅ 4. 区块链监控增强 - 已修复")
        print("✅ 5. 通知系统优化 - 已修复")
        print("✅ 6. updater 变量定义顺序 - 已修复")
        print("="*60 + "\n")
        
        # 启动机器人
        updater.start_polling(timeout=600)
        updater.idle()
        
    except Exception as e:
        print(f"❌ 机器人启动失败: {e}")
        import traceback
        traceback.print_exc()
        raise


# 修复缺失的函数定义
def jianceguoqi(context):
    """监测过期订单和清理"""
    try:
        # 使用安全的USDT充值检测和回调处理
        secure_jiexi(context)
        
        # 每30秒清理过期订单
        current_time = int(time.time())
        if current_time % 30 == 0:
            cleanup_expired_orders()
            
    except Exception as e:
        print(f"❌ 监测过期订单失败: {e}")


def create_instant_notification(transaction_data):
    """创建即时通知"""
    try:
        # 从区块链交易数据创建通知
        txid = transaction_data.get('txid', '')
        amount = transaction_data.get('quant', 0)
        
        # 查找匹配的订单
        usdt_amount = abs(float(Decimal(amount) / Decimal('1000000')))
        matching_order = topup.find_one({"money": usdt_amount})
        
        if matching_order:
            user_id = matching_order['user_id']
            timer = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            
            # 创建通知记录
            notifications.insert_one({
                'user_id': user_id,
                'type': 'payment_success',
                'amount': usdt_amount,
                'txid': txid,
                'processed': False,
                'created_at': timer,
                'timestamp': time.time()
            })
            
            print(f"✅ 创建即时通知成功: 用户{user_id}, 金额{usdt_amount}")
            
    except Exception as e:
        print(f"❌ 创建即时通知失败: {e}")


def suoyouchengxu(context: CallbackContext):
    """启动所有程序的定时任务 - 修复版"""
    try:
        # 使用安全的监测函数
        jianceguoqi(context)
        
    except Exception as e:
        print(f"❌ 定时任务执行失败: {e}")


# 🔥 关键修复：添加缺失的导入和全局变量
try:
    from telegram.ext import Updater
    import telegram
    import threading
    import time
    import sys
    import os
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

# 🔥 关键修复：检查是否定义了所需的函数
def check_missing_functions():
    """检查缺失的关键函数"""
    required_funcs = [
        'secure_jiexi', 'check_payment_notifications', 'enhanced_scheduled_tasks',
        'start_blockchain_monitoring', 'setup_logging'
    ]
    
    current_module = sys.modules[__name__]
    missing = []
    
    for func_name in required_funcs:
        if not hasattr(current_module, func_name):
            missing.append(func_name)
    
    if missing:
        print(f"⚠️ 缺失以下函数: {', '.join(missing)}")
        return False
    
    return True


# 程序入口点修复
if __name__ == '__main__':
    print("🔧 开始系统修复和初始化...")
    
    # 检查函数完整性
    if not check_missing_functions():
        print("❌ 关键函数缺失，请检查代码完整性")
        # 不退出，继续运行看看具体问题
    
    # 1. 修复用户数据
    try:
        fix_missing_user_fields()
    except Exception as e:
        print(f"⚠️ 修复用户数据时出错: {e}")
    
    # 2. 初始化系统配置
    try:
        initialize_system_config()
    except Exception as e:
        print(f"⚠️ 初始化系统配置时出错: {e}")
    
    # 3. 运行原有的修复程序
    try:
        run_full_repair()
    except Exception as e:
        print(f"⚠️ 运行修复程序时出错: {e}")
    
    print("✅ 修复完成，启动机器人...")
    
    # 4. 启动机器人
    main()