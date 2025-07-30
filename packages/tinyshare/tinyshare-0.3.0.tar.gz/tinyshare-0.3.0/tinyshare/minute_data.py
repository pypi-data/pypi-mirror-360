#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TinyShare 分钟数据模块
基于baostock实现股票历史分钟数据获取
"""

import baostock as bs
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Optional, Union
import re
import numpy as np
import sys
import os
from contextlib import contextmanager

# 配置日志
logger = logging.getLogger(__name__)

# 禁用baostock的日志输出
@contextmanager
def suppress_baostock_output():
    """上下文管理器，用于禁用baostock的输出"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        # 重定向标准输出到空
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        yield
    finally:
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = old_stdout
        sys.stderr = old_stderr

class MinuteDataFetcher:
    """股票分钟数据获取器"""
    
    def __init__(self):
        self._logged_in = False
    
    def _login_baostock(self):
        """登录baostock系统"""
        if not self._logged_in:
            with suppress_baostock_output():
                lg = bs.login()
            if lg.error_code != '0':
                logger.error(f'登录baostock失败 - error_code: {lg.error_code}, error_msg: {lg.error_msg}')
                raise Exception(f"登录baostock失败: {lg.error_msg}")
            else:
                self._logged_in = True
    
    def _logout_baostock(self):
        """登出baostock系统"""
        if self._logged_in:
            with suppress_baostock_output():
                bs.logout()
            self._logged_in = False
    
    def _convert_ts_code_to_baostock(self, ts_code: str) -> str:
        """
        将tushare格式的股票代码转换为baostock格式
        
        Args:
            ts_code (str): tushare格式代码，如 '600000.SH' 或 '000001.SZ'
            
        Returns:
            str: baostock格式代码，如 'sh.600000' 或 'sz.000001'
        """
        if not ts_code or not isinstance(ts_code, str):
            raise ValueError(f"无效的股票代码格式: {ts_code}，股票代码不能为空且必须是字符串")
        
        if '.' not in ts_code:
            raise ValueError(f"无效的股票代码格式: {ts_code}，正确格式应为：600000.SH 或 000001.SZ")
        
        parts = ts_code.split('.')
        if len(parts) != 2:
            raise ValueError(f"无效的股票代码格式: {ts_code}，正确格式应为：600000.SH 或 000001.SZ")
        
        code, exchange = parts
        
        # 验证股票代码部分（应该是6位数字）
        if not code.isdigit() or len(code) != 6:
            raise ValueError(f"无效的股票代码格式: {ts_code}，股票代码部分应为6位数字")
        
        # 验证交易所代码
        if exchange.upper() == 'SH':
            return f'sh.{code}'
        elif exchange.upper() == 'SZ':
            return f'sz.{code}'
        else:
            raise ValueError(f"不支持的交易所代码: {exchange}，支持的交易所代码: SH, SZ")
    
    def _convert_freq_to_baostock(self, freq: str) -> str:
        """
        将tushare频率转换为baostock频率
        
        Args:
            freq (str): tushare频率，如 '1min', '5min', '15min', '30min', '60min'
            
        Returns:
            str: baostock频率，如 '1', '5', '15', '30', '60'
        """
        freq_map = {
            '1min': '1',
            '5min': '5',
            '15min': '15',
            '30min': '30',
            '60min': '60'
        }
        
        if freq not in freq_map:
            raise ValueError(f"不支持的频率: {freq}，支持的频率: {list(freq_map.keys())}")
        
        # 特别提醒：baostock可能不支持1min数据
        if freq == '1min':
            logger.warning("注意：baostock可能不支持1min数据，建议使用5min或更大的频率")
        
        return freq_map[freq]
    
    def _format_datetime(self, dt_str: Optional[str]) -> Optional[str]:
        """
        格式化日期时间字符串
        
        Args:
            dt_str (str): 日期时间字符串，如 '2023-08-25 09:00:00' 或 '2023-08-25'
            
        Returns:
            str: 格式化后的日期字符串 'YYYY-MM-DD'
        """
        if not dt_str:
            return None
        
        # 如果包含时间，只取日期部分
        if ' ' in dt_str:
            dt_str = dt_str.split(' ')[0]
        
        # 验证日期格式
        try:
            datetime.strptime(dt_str, '%Y-%m-%d')
            return dt_str
        except ValueError:
            raise ValueError(f"无效的日期格式: {dt_str}，应为 'YYYY-MM-DD' 或 'YYYY-MM-DD HH:MM:SS'")
    
    def _convert_to_tushare_format(self, df: pd.DataFrame, ts_code: str) -> pd.DataFrame:
        """
        将baostock数据转换为tushare格式
        
        Args:
            df (pd.DataFrame): baostock原始数据
            ts_code (str): tushare格式的股票代码
            
        Returns:
            pd.DataFrame: tushare格式的数据
        """
        if df is None or df.empty:
            return df
        
        # 创建新的DataFrame
        result = pd.DataFrame()
        
        # 确保ts_code字段正确赋值
        result['ts_code'] = [ts_code] * len(df)
        
        # 处理时间格式：将baostock的date和time字段合并并格式化
        def format_trade_time(date_str, time_str):
            """格式化交易时间"""
            try:
                # baostock的time格式是 'YYYYMMDDHHMMSS000' 或类似格式
                # 从time字段中提取时间部分
                if len(time_str) >= 14:
                    # 格式: YYYYMMDDHHMMSS000
                    time_part = time_str[8:14]  # 提取HHMMSS部分
                    hour = time_part[:2]
                    minute = time_part[2:4]
                    second = time_part[4:6]
                    formatted_time = f"{hour}:{minute}:{second}"
                elif len(time_str) >= 6:
                    # 如果只有时间部分 HHMMSS
                    hour = time_str[:2]
                    minute = time_str[2:4]
                    second = time_str[4:6]
                    formatted_time = f"{hour}:{minute}:{second}"
                else:
                    # 如果时间格式不正确，使用默认时间
                    formatted_time = "00:00:00"
                
                return f"{date_str} {formatted_time}"
            except Exception:
                # 如果格式化失败，返回原始格式
                return f"{date_str} {time_str}"
        
        # 应用时间格式化
        result['trade_time'] = df.apply(lambda row: format_trade_time(row['date'], row['time']), axis=1)
        
        # 调整列顺序：将close放在open之前
        result['close'] = pd.to_numeric(df['close'], errors='coerce')
        result['open'] = pd.to_numeric(df['open'], errors='coerce')
        result['high'] = pd.to_numeric(df['high'], errors='coerce')
        result['low'] = pd.to_numeric(df['low'], errors='coerce')
        
        # 处理成交量，转换为整数类型
        try:
            # 先转换为数值，再处理NaN，最后转换为整数
            vol_series = pd.to_numeric(df['volume'], errors='coerce')
            # 确保是pandas Series类型才调用fillna
            if isinstance(vol_series, pd.Series):
                vol_series = vol_series.fillna(0)
                result['vol'] = vol_series.astype(int)
            else:
                result['vol'] = [0] * len(df)
        except (ValueError, TypeError):
            # 如果转换失败，使用0作为默认值
            result['vol'] = [0] * len(df)
        
        result['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        # 按时间倒序排列（与tushare保持一致）
        result = result.sort_values('trade_time', ascending=False).reset_index(drop=True)
        
        return result
    
    def get_stock_minute_data(self, 
                            ts_code: str, 
                            freq: str, 
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None,
                            origin: bool = False) -> Optional[pd.DataFrame]:
        """
        获取股票分钟数据
        
        Args:
            ts_code (str): 股票代码，如 '600000.SH'
            freq (str): 分钟频度，支持 '1min', '5min', '15min', '30min', '60min'
            start_date (str, optional): 开始日期，格式 '2023-08-25' 或 '2023-08-25 09:00:00'
            end_date (str, optional): 结束日期，格式 '2023-08-25' 或 '2023-08-25 19:00:00'
            origin (bool): 是否返回原始baostock数据，默认False返回tushare格式
            
        Returns:
            pd.DataFrame: 股票分钟数据
        """
        try:
            # 登录baostock
            self._login_baostock()
            
            # 转换参数
            baostock_code = self._convert_ts_code_to_baostock(ts_code)
            baostock_freq = self._convert_freq_to_baostock(freq)
            
            # 格式化日期
            formatted_start_date = self._format_datetime(start_date)
            formatted_end_date = self._format_datetime(end_date)
            
            # 设置默认日期范围
            if formatted_end_date is None:
                formatted_end_date = datetime.now().strftime('%Y-%m-%d')
            if formatted_start_date is None:
                # 默认获取最近30天的数据
                formatted_start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            logger.info(f'开始获取股票 {ts_code} 的{freq}分钟数据，时间范围: {formatted_start_date} 到 {formatted_end_date}')
            
            # baostock分钟线字段
            fields = "date,time,code,open,high,low,close,volume,amount,adjustflag"
            
            # 调用baostock API
            rs = bs.query_history_k_data_plus(
                baostock_code,
                fields,
                start_date=formatted_start_date,
                end_date=formatted_end_date,
                frequency=baostock_freq,
                adjustflag="3"  # 3=不复权
            )
            
            # 检查查询结果
            if rs is None:
                logger.error('baostock查询返回None')
                return None
                
            if rs.error_code != '0':
                logger.error(f'查询失败 - error_code: {rs.error_code}, error_msg: {rs.error_msg}')
                return None
            
            # 获取数据
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                logger.warning(f'未获取到股票 {ts_code} 的数据')
                return None
            
            # 转换为DataFrame
            field_names = ["date", "time", "code", "open", "high", "low", "close", "volume", "amount", "adjustflag"]
            result = pd.DataFrame(data_list, columns=field_names)
            logger.info(f'成功获取 {len(result)} 条数据记录')
            
            # 根据origin参数决定返回格式
            if origin:
                return result
            else:
                return self._convert_to_tushare_format(result, ts_code)
                
        except Exception as e:
            logger.error(f'获取分钟数据时发生错误: {str(e)}')
            raise
        finally:
            # 确保登出
            self._logout_baostock()

# 创建全局实例
_minute_data_fetcher = MinuteDataFetcher()

# 导入权限检查装饰器
from . import permission_required

@permission_required('stk_mins')
def stk_mins_tiny(ts_code: str, 
                 freq: str, 
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None,
                 origin: bool = False) -> Optional[pd.DataFrame]:
    """
    获取A股分钟数据（基于baostock）
    
    这是tinyshare的扩展接口，提供与tushare.stk_mins相似的功能，
    但底层使用baostock数据源，无需tushare积分。
    
    注意：此接口需要权限验证，请先调用 set_token_tiny() 设置权限验证码。
    
    Args:
        ts_code (str): 股票代码，如 '600000.SH'
        freq (str): 分钟频度，支持 '1min', '5min', '15min', '30min', '60min'
        start_date (str, optional): 开始日期，格式 '2023-08-25' 或 '2023-08-25 09:00:00'
        end_date (str, optional): 结束日期，格式 '2023-08-25' 或 '2023-08-25 19:00:00'
        origin (bool): 是否返回原始baostock数据，默认False返回tushare格式
        
    Returns:
        pd.DataFrame: 股票分钟数据
        
    Raises:
        PermissionError: 当权限验证码未设置或权限不足时抛出
        
    Examples:
        >>> import tinyshare as ts
        >>> # 首先设置权限验证码
        >>> ts.set_token_tiny('your_permission_code_here')
        >>> # 获取浦发银行1分钟数据（tushare格式）
        >>> df = ts.stk_mins_tiny('600000.SH', '1min', '2023-08-25', '2023-08-25')
        >>> print(df.head())
        
        >>> # 获取原始baostock格式数据
        >>> df_origin = ts.stk_mins_tiny('600000.SH', '5min', origin=True)
        >>> print(df_origin.head())
    """
    return _minute_data_fetcher.get_stock_minute_data(
        ts_code=ts_code,
        freq=freq,
        start_date=start_date,
        end_date=end_date,
        origin=origin
    ) 