# backtester/__init__.py

"""
Backtester
~~~~~~~~~~

암호화폐 거래 전략을 백테스트하기 위한 프레임워크입니다.

:copyright: (c) 2024
:license: MIT
"""

from .data_utils import (
    get_data,
    generate_data_for_backtest,
    make_unofficial_interval,
)

from .indicators import (
    # Outer functions
    calculate_supertrend,
    get_supertrend,
    calculate_ut_signal,
    get_ut_signal,
    calculate_blackflag,
    get_blackflag,
    calculate_ichimoku_senkou_a,
    get_ichimoku_senkou_a,
)

from .trade_analysis import (
    analyze_trade_history,
    analyze_trade_history_for_vector,
    merge_csv_to_excel
)

from .trade_execution import (
    record_trade,
    check_trailing_stop_exit_cond
)

from .Backtester import (
    BacktesterABS,
    OrderType,
    OrderPositionSide,
    OrderStatus,
    CloseType,
    DataRow,
    Order,
)

from .symbols import get_binance_symbols_for_backtest

__all__ = [
    # Data Utils
    'get_data',
    'generate_data_for_backtest',
    'make_unofficial_interval',
    
    # Indicators
    'get_candle_signal',
    'calculate_goya_line',
    'calculate_supertrend',
    'get_supertrend',
    'calculate_ut_signal',
    'get_ut_signal',
    'calculate_supertrend_v',
    'get_supertrend_v',
    'calculate_blackflag',
    'get_blackflag',
    'calculate_divergence_signal',
    'get_divergence_signal',
    'calculate_ichimoku_senkou_a',
    'get_ichimoku_senkou_a',
    'calculate_support_resistance_line',
    'get_support_resistance_line',
    
    # Trade Analysis
    'analyze_trade_history',
    'analyze_trade_history_with_drawdown',
    'analyze_trade_history_for_vector',
    'merge_csv_to_excel',
    
    # Trade Execution
    'record_trade',
    'record_trade_with_drawdown',
    'check_trailing_stop_exit_cond',
    
    # Backtester Classes
    'BacktesterABS',
    'FilteredTrailingStopBacktester',
    'FilteredTrailingStopBacktesterWithTimeLoss',
    'OrderType',
    'OrderPositionSide',
    'OrderStatus',
    'CloseType',
    'DataRow',
    'Order',
    'FilteredBacktester',
    

    # Symbols
    'get_binance_symbols_for_backtest'
]

# 버전 정보
__version__ = '1.0.0'
VERSION_INFO = tuple(map(int, __version__.split('.')))