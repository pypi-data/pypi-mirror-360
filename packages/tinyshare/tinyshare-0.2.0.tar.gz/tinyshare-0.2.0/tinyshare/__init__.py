#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyShare - A lightweight wrapper for tushare financial data API

This package provides a drop-in replacement for tushare with additional
features and optimizations while maintaining 100% API compatibility.
"""

import tushare as _tushare
import functools
import logging
import re
import requests
import json
from typing import Any, Optional, List, Dict
from pathlib import Path

__version__ = "0.2.0"
__author__ = "Your Name"

# Set up logging
logger = logging.getLogger(__name__)

# Global token storage and status
_token = None
_token_set_success = False

# Global tiny token storage and status for permission checking
_tiny_token = None
_tiny_token_set_success = False


class PermissionManager:
    """权限管理器，用于处理权限验证码和权限检查"""
    
    def __init__(self):
        self.auth_api_url = "http://localhost:1337/api/auth/validate"
        self.cache_dir_name = ".tinyshare"
        self.permission_cache = {}  # 权限缓存
    
    def get_cache_file_path(self):
        """获取缓存文件路径"""
        cache_dir = Path.home() / self.cache_dir_name
        cache_dir.mkdir(exist_ok=True)
        return cache_dir / "permission_cache.json"
    
    def save_permission_to_cache(self, token, permissions):
        """将权限信息保存到本地缓存"""
        cache_file = self.get_cache_file_path()
        cache_data = {
            'token': token,
            'permissions': permissions,
            'timestamp': json.dumps(None, default=str)  # 可以后续添加时间戳
        }
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"权限信息已缓存到本地: {cache_file}")
        except IOError as e:
            logger.error(f"保存权限缓存文件失败: {e}")
    
    def validate_permission(self, token, required_permission):
        """
        验证权限
        
        Args:
            token (str): 权限验证码
            required_permission (str): 需要的权限，如 'stk_mins'
            
        Returns:
            bool: 是否有权限
        """
        if not token:
            logger.error("权限验证码不能为空")
            return False
        
        headers = {"Content-Type": "application/json"}
        data = {"code": token}
        
        try:
            logger.info(f"正在验证权限: {required_permission}")
            response = requests.post(self.auth_api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success') and result.get('valid'):
                logger.info("权限验证成功")
                
                # 从响应中获取权限信息
                # 目前接口返回的是 tooltype，我们将其作为默认权限
                # 后续可以扩展为 authArr 字段
                auth_arr = result.get('authArr', [])
                if not auth_arr:
                    # 如果没有 authArr，使用 tooltype 作为默认权限
                    tooltype = result.get('tooltype', result.get('data', {}).get('tooltype', ''))
                    if tooltype:
                        auth_arr = [tooltype]
                
                # 检查是否包含所需权限
                if required_permission in auth_arr:
                    logger.info(f"权限检查通过: {required_permission}")
                    # 缓存权限信息
                    self.permission_cache[token] = auth_arr
                    self.save_permission_to_cache(token, auth_arr)
                    return True
                else:
                    logger.warning(f"权限不足: 需要 {required_permission}，当前权限: {auth_arr}")
                    return False
            else:
                logger.error(f"权限验证失败: {result.get('message', '未知错误')}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"权限验证请求失败: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"权限验证响应解析失败: {e}")
            return False
        except Exception as e:
            logger.error(f"权限验证时发生未知错误: {e}")
            return False


class TokenManager:
    """Token管理器，用于处理提取码和token转换"""
    
    def __init__(self):
        self.api_url = "https://extract.swiftiny.com/api/extract/getLatestKey"
        self.cache_dir_name = ".tushare"
    
    def get_cache_file_path(self):
        """获取缓存文件路径"""
        cache_dir = Path.home() / self.cache_dir_name
        cache_dir.mkdir(exist_ok=True)
        return cache_dir / "token_cache.json"
    
    def save_token_to_cache(self, token, key_name=None, call_count=None, max_count=None):
        """将token保存到本地缓存"""
        cache_file = self.get_cache_file_path()
        cache_data = {
            'token': token,
            'key_name': key_name,
            'call_count': call_count,
            'max_count': max_count
        }
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Token已缓存到本地: {cache_file}")
        except IOError as e:
            logger.error(f"保存缓存文件失败: {e}")
    
    def get_token_from_extract_code(self, extract_code):
        """通过提取码获取真实token"""
        headers = {"Content-Type": "application/json"}
        data = {"code": extract_code}
        
        try:
            logger.info("正在通过提取码获取token...")
            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success') and result.get('status') == 200:
                token = result.get('apiKey')
                key_name = result.get('keyName')
                call_count = result.get('callCount')
                max_count = result.get('maxCount')
                
                logger.info(f"获取新token成功: {key_name}")
                logger.info(f"调用次数: {call_count}/{max_count}")
                
                # 保存到缓存
                self.save_token_to_cache(token, key_name, call_count, max_count)
                return token
            else:
                logger.error(f"获取token失败: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析响应失败: {e}")
            return None


# 创建管理器实例
_token_manager = TokenManager()
_permission_manager = PermissionManager()


def permission_required(required_permission: str):
    """
    权限检查装饰器
    
    Args:
        required_permission (str): 需要的权限，如 'stk_mins'
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            global _tiny_token
            
            if not _tiny_token:
                raise PermissionError(f"未设置权限验证码，请先调用 set_token_tiny() 设置权限验证码")
            
            # 检查权限
            if not _permission_manager.validate_permission(_tiny_token, required_permission):
                raise PermissionError(f"权限不足，需要 '{required_permission}' 权限")
            
            # 权限检查通过，执行原函数
            return func(*args, **kwargs)
        return wrapper
    return decorator


def is_extract_code(token_str: str) -> bool:
    """
    判断输入的字符串是否为提取码（包含大写字母）
    
    Args:
        token_str (str): 输入的token字符串
        
    Returns:
        bool: 如果包含大写字母则认为是提取码，返回True；否则返回False
    """
    return bool(re.search(r'[A-Z]', token_str))


def is_normal_token(token_str: str) -> bool:
    """
    判断输入的字符串是否为正常token（全是小写字母+数字）
    
    Args:
        token_str (str): 输入的token字符串
        
    Returns:
        bool: 如果全是小写字母和数字则返回True；否则返回False
    """
    return bool(re.match(r'^[a-z0-9]+$', token_str))


def set_token_tiny(token: str) -> None:
    """
    设置权限验证码，用于控制自定义接口的权限
    
    Args:
        token (str): 权限验证码
    """
    global _tiny_token, _tiny_token_set_success
    
    if not token or not isinstance(token, str):
        logger.error("权限验证码不能为空且必须是字符串")
        _tiny_token_set_success = False
        return
    
    token = token.strip()

    _tiny_token = token
    _tiny_token_set_success = True
    logger.info("权限验证码设置成功")


def get_token_tiny() -> Optional[str]:
    """
    获取当前设置的权限验证码
    
    Returns:
        str or None: 当前权限验证码，如果未设置则返回 None
    """
    return _tiny_token


def is_token_tiny_set_success() -> bool:
    """
    检查权限验证码是否设置成功
    
    Returns:
        bool: 权限验证码设置成功状态
    """
    return _tiny_token_set_success


def set_token(token: str) -> None:
    """
    Set the tushare API token.
    支持普通token和提取码两种方式。
    
    Args:
        token (str): Your tushare API token or extract code
    """
    global _token, _token_set_success
    
    if not token or not isinstance(token, str):
        logger.error("Token不能为空且必须是字符串")
        _token_set_success = False
        return
    
    token = token.strip()
    
    try:
        # 情况1：如果token全是小写字母+数字，则默认走tushare的set_token方法
        if is_normal_token(token):
            logger.info("检测到普通token格式，直接设置")
            _token = token
            _tushare.set_token(token)
            _token_set_success = True
            logger.info("Token设置成功")
            
        # 情况2：如果token包含大写字母，则认为是提取码，需要调用接口获取真实token
        elif is_extract_code(token):
            logger.info("检测到提取码格式，正在获取真实token")
            
            # 通过提取码获取真实token
            real_token = _token_manager.get_token_from_extract_code(token)
            
            if real_token:
                logger.info("成功获取真实token，正在设置")
                # 获取到真实token后，继续走tushare的set_token方法
                _token = real_token
                _tushare.set_token(real_token)
                _token_set_success = True
                logger.info("Token设置成功")
            else:
                logger.error("无法通过提取码获取真实token")
                _token_set_success = False
                
        else:
            # 其他格式，尝试直接设置
            logger.info("未识别的token格式，尝试直接设置")
            _token = token
            _tushare.set_token(token)
            _token_set_success = True
            logger.info("Token设置成功")
            
    except Exception as e:
        logger.error(f"设置token时发生错误: {e}")
        _token_set_success = False
        raise


def get_token() -> Optional[str]:
    """
    Get the current tushare API token.
    
    Returns:
        str or None: Current token if set, None otherwise
    """
    return _token


def is_token_set_success() -> bool:
    """
    检查token是否设置成功
    
    Returns:
        bool: token设置成功状态
    """
    return _token_set_success


def pro_api(token: Optional[str] = None, timeout: int = 30) -> Any:
    """
    Initialize tushare pro API client.
    
    Args:
        token (str, optional): API token. If not provided, uses globally set token.
        timeout (int): Request timeout in seconds. Defaults to 30.
    
    Returns:
        TuShare Pro API client instance
    """
    if token:
        set_token(token)
        actual_token = token
    elif _token:
        actual_token = _token
    else:
        raise ValueError("Token not set. Please call set_token() first or provide token parameter.")
    
    try:
        client = _tushare.pro_api(token=actual_token, timeout=timeout)
        logger.info("Pro API client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize pro API client: {e}")
        raise


# Proxy all other tushare functions and attributes
def __getattr__(name: str) -> Any:
    """
    Proxy all tushare attributes and functions.
    
    This allows tinyshare to act as a complete drop-in replacement for tushare
    while maintaining the ability to add custom functionality.
    """
    if hasattr(_tushare, name):
        attr = getattr(_tushare, name)
        
        # If it's a callable, wrap it with logging
        if callable(attr):
            @functools.wraps(attr)
            def wrapper(*args, **kwargs):
                logger.debug(f"Calling tushare.{name} with args={args}, kwargs={kwargs}")
                try:
                    result = attr(*args, **kwargs)
                    logger.debug(f"tushare.{name} completed successfully")
                    return result
                except Exception as e:
                    logger.error(f"Error in tushare.{name}: {e}")
                    raise
            return wrapper
        else:
            return attr
    else:
        raise AttributeError(f"module 'tinyshare' has no attribute '{name}'")


# Export commonly used functions directly
from tushare import get_hist_data, get_tick_data, get_today_all, get_realtime_quotes

# Import our custom minute data function
from .minute_data import stk_mins_tiny

# Make sure we export the main functions
__all__ = [
    'set_token',
    'get_token', 
    'is_token_set_success',
    'is_normal_token',
    'is_extract_code',
    'set_token_tiny',
    'get_token_tiny',
    'is_token_tiny_set_success',
    'pro_api',
    'get_hist_data',
    'get_tick_data',
    'get_today_all',
    'get_realtime_quotes',
    'stk_mins_tiny',
    '__version__'
] 