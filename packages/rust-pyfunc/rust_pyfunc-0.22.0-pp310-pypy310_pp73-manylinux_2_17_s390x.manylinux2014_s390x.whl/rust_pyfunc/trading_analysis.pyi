"""交易分析函数类型声明"""
from typing import List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray

def find_follow_volume_sum_same_price(times: NDArray[np.float64], prices: NDArray[np.float64], volumes: NDArray[np.float64], time_window: float = 0.1, check_price: bool = True, filter_ratio: float = 0.0, timeout_seconds: Optional[float] = None) -> NDArray[np.float64]:
    """计算每一行在其后time_window秒内具有相同volume（及可选相同price）的行的volume总和。

    参数说明：
    ----------
    times : numpy.ndarray
        时间戳数组（单位：秒）
    prices : numpy.ndarray
        价格数组
    volumes : numpy.ndarray
        成交量数组
    time_window : float, optional
        时间窗口大小（单位：秒），默认为0.1
    check_price : bool, optional
        是否检查价格是否相同，默认为True。设为False时只检查volume是否相同。
    filter_ratio : float, optional, default=0.0
        要过滤的volume数值比例，默认为0（不过滤）。如果大于0，则过滤出现频率最高的前 filter_ratio 比例的volume种类，对应的行会被设为NaN。
    timeout_seconds : float, optional, default=None
        计算超时时间（秒）。如果计算时间超过该值，函数将返回全NaN的数组。默认为None，表示不设置超时限制。

    返回值：
    -------
    numpy.ndarray
        每一行在其后time_window秒内（包括当前行）具有相同条件的行的volume总和。
        如果filter_ratio>0，则出现频率最高的前filter_ratio比例的volume值对应的行会被设为NaN。
    """
    ...

def find_follow_volume_sum_same_price_and_flag(times: NDArray[np.float64], prices: NDArray[np.float64], volumes: NDArray[np.float64], flags: NDArray[np.int32], time_window: float = 0.1) -> NDArray[np.float64]:
    """计算每一行在其后0.1秒内具有相同flag、price和volume的行的volume总和。

    参数说明：
    ----------
    times : array_like
        时间戳数组（单位：秒）
    prices : array_like
        价格数组
    volumes : array_like
        成交量数组
    flags : array_like
        主买卖标志数组
    time_window : float, optional
        时间窗口大小（单位：秒），默认为0.1

    返回值：
    -------
    numpy.ndarray
        每一行在其后time_window秒内具有相同price和volume的行的volume总和
    """
    ...

def mark_follow_groups(times: NDArray[np.float64], prices: NDArray[np.float64], volumes: NDArray[np.float64], time_window: float = 0.1) -> NDArray[np.int32]:
    """标记每一行在其后0.1秒内具有相同price和volume的行组。
    对于同一个时间窗口内的相同交易组，标记相同的组号。
    组号从1开始递增，每遇到一个新的交易组就分配一个新的组号。

    参数说明：
    ----------
    times : numpy.ndarray
        时间戳数组（单位：秒）
    prices : numpy.ndarray
        价格数组
    volumes : numpy.ndarray
        成交量数组
    time_window : float, optional
        时间窗口大小（单位：秒），默认为0.1

    返回值：
    -------
    numpy.ndarray
        整数数组，表示每行所属的组号。0表示不属于任何组。
    """
    ...

def mark_follow_groups_with_flag(times: NDArray[np.float64], prices: NDArray[np.float64], volumes: NDArray[np.float64], flags: NDArray[np.int64], time_window: float = 0.1) -> NDArray[np.int32]:
    """标记每一行在其后time_window秒内具有相同flag、price和volume的行组。
    对于同一个时间窗口内的相同交易组，标记相同的组号。
    组号从1开始递增，每遇到一个新的交易组就分配一个新的组号。

    参数说明：
    ----------
    times : numpy.ndarray
        时间戳数组（单位：秒）
    prices : numpy.ndarray
        价格数组
    volumes : numpy.ndarray
        成交量数组
    flags : numpy.ndarray
        主买卖标志数组
    time_window : float, optional
        时间窗口大小（单位：秒），默认为0.1

    返回值：
    -------
    numpy.ndarray
        整数数组，表示每行所属的组号。0表示不属于任何组。
    """
    ...

def analyze_retreat_advance(
    trade_times: NDArray[np.float64],
    trade_prices: NDArray[np.float64], 
    trade_volumes: NDArray[np.float64],
    trade_flags: NDArray[np.float64],
    orderbook_times: NDArray[np.float64],
    orderbook_prices: NDArray[np.float64],
    orderbook_volumes: NDArray[np.float64],
    volume_percentile: Optional[float] = 99.0,
    time_window_minutes: Optional[float] = 1.0
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """分析股票交易中的"以退为进"现象
    
    该函数分析当价格触及某个局部高点后回落，然后在该价格的异常大挂单量消失后
    成功突破该价格的现象。
    
    参数说明：
    ----------
    trade_times : NDArray[np.float64]
        逐笔成交数据的时间戳序列（纳秒时间戳）
    trade_prices : NDArray[np.float64]
        逐笔成交数据的价格序列
    trade_volumes : NDArray[np.float64]
        逐笔成交数据的成交量序列
    trade_flags : NDArray[np.float64]
        逐笔成交数据的标志序列（买卖方向，正数表示买入，负数表示卖出）
    orderbook_times : NDArray[np.float64]
        盘口快照数据的时间戳序列（纳秒时间戳）
    orderbook_prices : NDArray[np.float64]
        盘口快照数据的价格序列
    orderbook_volumes : NDArray[np.float64]
        盘口快照数据的挂单量序列
    volume_percentile : Optional[float], default=99.0
        异常大挂单量的百分位数阈值，默认为99.0（即前1%）
    time_window_minutes : Optional[float], default=1.0
        检查异常大挂单量的时间窗口（分钟），默认为1.0分钟
    
    返回值：
    -------
    Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]
        包含6个数组的元组：
        - 过程期间的成交量
        - 过程期间首次观察到的价格x在盘口上的异常大挂单量
        - 过程开始后指定时间窗口内的成交量
        - 过程期间的主动买入成交量占比
        - 过程期间的价格种类数
        - 过程期间价格相对局部高点的最大下降比例
    """
    ...

def analyze_retreat_advance_v2(
    trade_times: List[float],
    trade_prices: List[float], 
    trade_volumes: List[float],
    trade_flags: List[float],
    orderbook_times: List[float],
    orderbook_prices: List[float],
    orderbook_volumes: List[float],
    volume_percentile: Optional[float] = 99.0,
    time_window_minutes: Optional[float] = 1.0,
    breakthrough_threshold: Optional[float] = 0.0,
    dedup_time_seconds: Optional[float] = 30.0,
    find_local_lows: Optional[bool] = False
) -> Tuple[List[float], List[float], List[float], List[float], List[float], List[float], List[float], List[float], List[float]]:
    """分析股票交易中的"以退为进"或"以进为退"现象（纳秒版本）
    
    该函数分析两种现象：
    1. "以退为进"（find_local_lows=False）：价格触及局部高点后回落，然后在该价格的异常大卖单量消失后成功突破该价格
    2. "以进为退"（find_local_lows=True）：价格跌至局部低点后反弹，然后在该价格的异常大买单量消失后成功跌破该价格
    
    这是analyze_retreat_advance函数的改进版本，专门为处理纳秒级时间戳而优化，并包含局部极值点去重功能。
    
    参数说明：
    ----------
    trade_times : List[float]
        逐笔成交数据的时间戳序列（纳秒时间戳）
    trade_prices : List[float]
        逐笔成交数据的价格序列
    trade_volumes : List[float]
        逐笔成交数据的成交量序列
    trade_flags : List[float]
        逐笔成交数据的标志序列（买卖方向），66表示主动买入，83表示主动卖出
    orderbook_times : List[float]
        盘口快照数据的时间戳序列（纳秒时间戳）
    orderbook_prices : List[float]
        盘口快照数据的价格序列
    orderbook_volumes : List[float]
        盘口快照数据的挂单量序列
    volume_percentile : Optional[float], default=99.0
        异常大挂单量的百分位数阈值，默认为99.0（即前1%）
    time_window_minutes : Optional[float], default=1.0
        检查异常大挂单量的时间窗口（分钟），默认为1.0分钟
    breakthrough_threshold : Optional[float], default=0.0
        突破阈值（百分比），默认为0.0（即只要高于局部高点任何幅度都算突破）
        例如：0.1表示需要高出局部高点0.1%才算突破
    dedup_time_seconds : Optional[float], default=30.0
        去重时间阈值（秒），默认为30.0。相同价格且时间间隔小于此值的局部极值点将被视为重复
    find_local_lows : Optional[bool], default=False
        是否查找局部低点，默认为False（查找局部高点）。
        当为True时，分析"以进为退"现象：价格跌至局部低点后反弹，在该价格的异常大买单量消失后成功跌破该价格
    
    返回值：
    -------
    Tuple[List[float], List[float], List[float], List[float], List[float], List[float], List[float], List[float], List[float]]
        包含9个列表的元组：
        - 过程期间的成交量
        - 局部极值价格在盘口上时间最近的挂单量
        - 过程开始后指定时间窗口内的成交量
        - 过程期间的主动买入成交量占比
        - 过程期间的价格种类数
        - 过程期间价格相对局部极值的最大变化比例（高点模式为最大下降比例，低点模式为最大上升比例）
        - 过程持续时间（秒）
        - 过程开始时间（纳秒时间戳）
        - 局部极值的价格
    
    特点：
    ------
    1. 纳秒级时间戳处理 - 专门优化处理纳秒级别的高精度时间戳
    2. 双模式分析 - 支持局部高点（以退为进）和局部低点（以进为退）两种分析模式
    3. 改进的局部极值识别 - 使用更准确的算法识别价格局部高点或低点
    4. 可配置的局部极值去重功能 - 对相同价格且时间接近的局部极值进行去重，时间阈值可自定义
    5. 智能挂单量检测 - 根据模式自动检测卖单（高点模式）或买单（低点模式）的异常大挂单量
    6. 可配置的突破条件 - 通过breakthrough_threshold参数自定义突破阈值
    7. 时间窗口控制 - 设置4小时最大搜索窗口，避免无限搜索
    """
    ...

def calculate_large_order_nearby_small_order_time_gap(
    volumes: NDArray[np.float64],
    exchtimes: NDArray[np.float64],
    large_quantile: float,
    small_quantile: float,
    near_number: int,
    exclude_same_time: bool = False,
    order_type: str = "small",
    flags: Optional[NDArray[np.int32]] = None,
    flag_filter: str = "ignore"
) -> NDArray[np.float64]:
    """计算每个大单与其临近订单之间的时间间隔均值。

    参数说明：
    ----------
    volumes : numpy.ndarray
        交易量数组
    exchtimes : numpy.ndarray
        交易时间数组（单位：纳秒）
    large_quantile : float
        大单的分位点阈值
    small_quantile : float
        小单的分位点阈值
    near_number : int
        每个大单要考虑的临近订单数量
    exclude_same_time : bool, default=False
        是否排除与大单时间戳相同的订单
    order_type : str, default="small"
        指定与大单计算时间间隔的订单类型：
        - "small"：计算大单与小于small_quantile分位点的订单的时间间隔
        - "mid"：计算大单与位于small_quantile和large_quantile分位点之间的订单的时间间隔
        - "full"：计算大单与小于large_quantile分位点的所有订单的时间间隔
    flags : Optional[NDArray[np.int32]], default=None
        交易标志数组，通常66表示主动买入，83表示主动卖出
    flag_filter : str, default="ignore"
        指定如何根据交易标志筛选计算对象：
        - "same"：只计算与大单交易标志相同的订单的时间间隔
        - "diff"：只计算与大单交易标志不同的订单的时间间隔
        - "ignore"：忽略交易标志，计算所有符合条件的订单的时间间隔

    返回值：
    -------
    numpy.ndarray
        浮点数数组，与输入volumes等长。对于大单，返回其与临近目标订单的时间间隔均值（秒）；
        对于非大单，返回NaN。
    """
    ...

def order_contamination(
    exchtime: NDArray[np.int64],
    order: NDArray[np.int64],
    volume: NDArray[np.int64],
    top_percentile: float = 10.0,
    time_window_seconds: float = 1.0
) -> NDArray[np.int64]:
    """订单浸染函数（高性能优化版本）
    
    根据订单成交量找到前top_percentile%的大单，然后将这些大单附近时间窗口内的非大单
    订单编号改为最近大单的订单编号，模拟大单浸染附近小单的效果。
    
    该版本经过大幅性能优化，使用时间索引排序和二分查找算法，
    处理速度相比原版本提升数十倍。
    
    参数说明：
    ----------
    exchtime : NDArray[np.int64]
        成交时间数组（纳秒）
    order : NDArray[np.int64]
        订单编号数组
    volume : NDArray[np.int64]
        成交量数组
    top_percentile : float, default=10.0
        大单百分比阈值（1-100），默认10.0表示前10%
    time_window_seconds : float, default=1.0
        时间窗口（秒），默认1秒
        
    返回值：
    -------
    NDArray[np.int64]
        浸染后的订单编号数组
        
    性能特点：
    ----------
    - 时间复杂度：O(n log n + m * log n)，其中n为总记录数，m为大单数
    - 空间复杂度：O(n)
    - 处理速度：约700万条/秒（实际股票数据）
    """
    ...

def order_contamination_parallel(
    exchtime: NDArray[np.int64],
    order: NDArray[np.int64],
    volume: NDArray[np.int64],
    top_percentile: float = 10.0,
    time_window_seconds: float = 1.0
) -> NDArray[np.int64]:
    """订单浸染函数（5核心并行版本）
    
    根据订单成交量找到前top_percentile%的大单，然后将这些大单附近时间窗口内的非大单
    订单编号改为最近大单的订单编号，模拟大单浸染附近小单的效果。
    
    此版本使用5个CPU核心进行并行计算，适用于大规模数据处理。
    
    参数说明：
    ----------
    exchtime : NDArray[np.int64]
        成交时间数组（纳秒）
    order : NDArray[np.int64]
        订单编号数组
    volume : NDArray[np.int64]
        成交量数组
    top_percentile : float, default=10.0
        大单百分比阈值（1-100），默认10.0表示前10%
    time_window_seconds : float, default=1.0
        时间窗口（秒），默认1秒
        
    返回值：
    -------
    NDArray[np.int64]
        浸染后的订单编号数组
        
    注意：
    -----
    该函数固定使用5个CPU核心进行并行计算。对于小规模数据，
    串行版本order_contamination可能更快。
    """
    ...

def trade_peak_analysis(
    exchtime: NDArray[np.int64],
    volume: NDArray[np.float64],
    flag: NDArray[np.int32],
    top_tier1: float,
    top_tier2: float,
    time_window: float,
    flag_different: bool,
    with_forth: bool
) -> Tuple[NDArray[np.float64], List[str]]:
    """交易高峰模式分析函数
    
    该函数用于分析交易数据中的高峰模式，包括：
    1. 识别成交量的局部高峰(根据top_tier1百分比)
    2. 在每个高峰的时间窗口内识别小峰(根据top_tier2百分比)
    3. 计算16个统计指标来描述高峰-小峰的模式特征
    
    参数说明：
    ----------
    exchtime : NDArray[np.int64]
        交易时间数组(纳秒时间戳)
    volume : NDArray[np.float64]
        成交量数组
    flag : NDArray[np.int32]
        交易标志数组(主动买入/卖出标志)
    top_tier1 : float
        高峰识别的百分比阈值(例如0.01表示前1%的大成交量)
    top_tier2 : float
        小峰识别的百分比阈值(例如0.10表示前10%的大成交量)
    time_window : float
        时间窗口大小(秒)
    flag_different : bool
        是否只考虑与高峰flag不同的小峰
    with_forth : bool
        是否同时考虑高峰前后的时间窗口
        
    返回值：
    -------
    Tuple[NDArray[np.float64], List[str]]
        第一个元素：N行16列的数组，每行对应一个局部高峰的16个统计指标
        第二个元素：包含16个特征名称的字符串列表
        
        16个特征列分别为：
        列0: 小峰成交量总和比值
        列1: 小峰平均成交量比值  
        列2: 小峰个数
        列3: 时间间隔均值秒
        列4: 成交量时间相关系数
        列5: DTW距离
        列6: 成交量变异系数
        列7: 成交量偏度
        列8: 成交量峰度
        列9: 成交量趋势
        列10: 成交量自相关
        列11: 时间变异系数
        列12: 时间偏度
        列13: 时间峰度
        列14: 时间趋势
        列15: 时间自相关
        
    使用示例：
    ---------
    >>> result_matrix, feature_names = trade_peak_analysis(...)
    >>> import pandas as pd
    >>> df = pd.DataFrame(result_matrix, columns=feature_names)
    """
    ...