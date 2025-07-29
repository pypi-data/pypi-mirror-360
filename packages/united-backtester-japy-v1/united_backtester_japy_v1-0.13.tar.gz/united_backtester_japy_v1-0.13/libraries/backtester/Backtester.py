import backtester

from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Union
from typing import Protocol
from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import traceback
from pathlib import Path

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    TRAILING = "trailing"

class OrderPositionSide(Enum):
    LONG = "long"
    SHORT = "short"

class OrderStatus(Enum):
    PENDING = "pending"
    ACTIVATED = "activated"
    FILLED = "filled"
    CANCELED = "canceled"

class CloseType(Enum):
    TAKE_PROFIT = "profit"
    STOP_LOSS = "loss"
    
class DataRow(Protocol):
    Index: datetime
    high: float
    low: float
    close: float
    open: float
    

@dataclass
class Order:
    # 기본 주문 정보
    symbol: str
    position_side: OrderPositionSide
    order_type: OrderType
    entry_price: float
    entry_time: datetime
    margin: float
    interval: str
    activated_time: Optional[datetime] = None
    # 예약 매수 주문시 사용
    activation_price: Optional[float] = None
    
    
    # 청산 관련 정보
    # 실제 청산 가격
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    close_type: Optional[CloseType] = None
    
    # 주문 상태
    status: OrderStatus = OrderStatus.PENDING
    
    # 리밋 주문 익절가격
    limit_price: Optional[float] = None
    
    # 손절 주문 손절 가격
    stop_loss_price: Optional[float] = None
    
    # 트레일링 주문 관련
    trailing_stop_activation_price: Optional[float] = None
    trailing_stop_activated_time: Optional[datetime] = None
    callback_rate: Optional[float] = None
    highest_price: Optional[float] = None  # LONG 포지션용
    lowest_price: Optional[float] = None   # SHORT 포지션용
    
    # 다이나믹 데이터 저장용
    metadata: Optional[dict] = None
    
    def check_activation_price(self, row: DataRow) -> bool:
        """
        매수주문 예약 주문
        """
        if self.activation_price is None:
            raise ValueError("check_activation_price err : Activation price is not set")
        return row.low <= self.activation_price <= row.high
    

    def check_stop_loss_conditions(self, row):
        """손절 조건 체크 로직을 구현해야 합니다
        트레이딩뷰 close 개념"""
        if self.position_side == OrderPositionSide.LONG:
            return row.low <= self.stop_loss_price
        else:
            return row.high >= self.stop_loss_price
        
        
    def check_limit_price(self, row: DataRow) -> bool:
        """
        리밋 주문 체크
        Returns: 주문 실행 필요 여부 (True/False)
        """
            
        if self.order_type != OrderType.LIMIT:
            return False
        if self.position_side == OrderPositionSide.LONG:
            return row.high >= self.limit_price
        elif self.position_side == OrderPositionSide.SHORT:
            return row.low <= self.limit_price
        else:
            raise ValueError("Invalid position side")
    
    
    
    def check_trailing_stop_activation_price(self, row: DataRow) -> bool:
        """
        트레일링 스탑 주문 활성화 체크
        
        Returns: 주문 활성화 필요 여부 (True/False)
        """
        
        if self.position_side == OrderPositionSide.LONG:
            return row.high >= self.trailing_stop_activation_price
        else:
            return row.low <= self.trailing_stop_activation_price
        

        
    def check_trailing_stop(self, row: DataRow, df_5m: pd.DataFrame) -> bool:
        """트레일링 스탑 체크
        Returns: 주문 청산 필요 여부 (True/False)
        """
        if self.order_type != OrderType.TRAILING:
            return False
        
        if self.status != OrderStatus.ACTIVATED:
            return False
        
        is_closed=False
        
        # 한캔들내에서 정리되는 경우
        if row.Index == self.trailing_stop_activated_time:
            if self.position_side == OrderPositionSide.LONG:
                if row.high * (1 - self.callback_rate) < row.close:
                    self.limit_price = row.high * (1 - self.callback_rate)
                    self.highest_price = row.high
                    is_closed=False
                else:
                    self.limit_price = row.high * (1 - self.callback_rate)
                    self.highest_price = row.high
                    is_closed=True
            else:
                if row.low * (1 + self.callback_rate) > row.close:
                    self.limit_price = row.low * (1 + self.callback_rate)
                    self.lowest_price = row.low
                    is_closed=False
                else:
                    self.limit_price = row.low * (1 + self.callback_rate)
                    self.lowest_price = row.low
                    is_closed=True
            
        else:
            highest_or_lowest = self.highest_price if self.position_side == OrderPositionSide.LONG else self.lowest_price 
            _highest_or_lowest, is_closed, new_trailing_stop_price = backtester.check_trailing_stop_exit_cond(
                df = df_5m,
                _index = row.Index,
                _position_size = 1 if self.position_side == OrderPositionSide.LONG else -1,
                _highest_or_lowest = highest_or_lowest,
                _profit_price = self.limit_price,
                _callbackrate = self.callback_rate,
                interval = self.interval
            )
            
            if _highest_or_lowest != highest_or_lowest:
                if self.position_side == OrderPositionSide.LONG:
                    self.highest_price = _highest_or_lowest
                else:
                    self.lowest_price = _highest_or_lowest
            if new_trailing_stop_price != self.limit_price:
                self.limit_price = new_trailing_stop_price
        
        return is_closed
            

    def close_order(self, row: DataRow, close_type: CloseType, close_price=None):
        """주문 청산 여기에서 손절 주문은 order에 해당하는 손절이고 
        전체적인 포지션을 정리하는 로직은 MAIN backtest class에 있음"""
        if close_price is None:
            if close_type == CloseType.TAKE_PROFIT:
                if self.order_type == OrderType.MARKET:
                    close_price = row.close
                elif self.order_type == OrderType.LIMIT:
                    close_price = self.limit_price
                elif self.order_type == OrderType.TRAILING:
                    close_price = self.limit_price
            elif close_type == CloseType.STOP_LOSS:
                if self.stop_loss_price is not None:
                    close_price = self.stop_loss_price
                else:
                    close_price = row.close
        else:
            close_price = close_price
        
        self.exit_price = close_price
        self.exit_time = row.Index
        self.close_type = close_type
        self.status = OrderStatus.FILLED
        

    def to_trade_record(self) -> dict:
        """거래 기록용 딕셔너리 반환"""
        return {
            "symbol": self.symbol,
            "position": self.position_side.value,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "close_type": self.close_type.value if self.close_type else None,
            'profit_pct': ((self.exit_price - self.entry_price) / (self.entry_price))* 100 if self.position_side == OrderPositionSide.LONG
                    else ((self.entry_price - self.exit_price) / (self.entry_price))* 100,
            "margin": self.margin if self.margin is not None else 0,
            "entry_time": self.entry_time,
            "activated_time": self.activated_time,
            "exit_time": self.exit_time
        }
        
    def to_dict(self) -> dict:
        """Order 객체의 모든 속성을 딕셔너리로 반환"""
        return {
            "symbol": self.symbol,
            "position_side": self.position_side.value,
            "order_type": self.order_type.value,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time,
            "interval": self.interval,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time,
            "close_type": self.close_type.value if self.close_type else None,
            "status": self.status.value,
            "margin": self.margin if self.margin is not None else 0,
            "limit_price": self.limit_price,
            "activation_price": self.activation_price,
            "trailing_stop_activation_price": self.trailing_stop_activation_price,
            "callback_rate": self.callback_rate,
            "highest_price": self.highest_price,
            "lowest_price": self.lowest_price,
            "activated_time": self.activated_time
        }


class BacktesterABS(ABC):
    def __init__(self, test_id, symbol, test_start_date='2023-01-01', test_end_date='2024-06-30', 
                 interval='60m', data_type='futures', params=None ,pyramiding=1, leverage=1, slippage=0.0005, ptc=0.0005,initial_balance=10000,save_trades=True,plot_results=True):
        self.test_id = test_id
        self.symbol = symbol
        self.interval = interval
        self.leverage = leverage
        self.slippage = slippage
        self.ptc = ptc
        self.initial_balance = initial_balance
        self.test_start_date = test_start_date
        self.test_end_date = test_end_date
        self.trade_history = []
        self.active_orders = []
        self.data = None
        self.data_5m = None
        self.data_type = data_type
        self.result = None
        self.params = None
        self.pyramiding = pyramiding
        self.save_trades = save_trades
        self.plot_results = plot_results
        
        # balance 관련
        self.wallet_balance=initial_balance
        self.wallet_balance_with_slippage=initial_balance
        self.margin_balance=initial_balance
        
        self.wallet_balance_list = []
        self.wallet_balance_with_slippage_list = []
        self.margin_balance_list = []
        
        # 포지션 괸련
        self.long_avg_entry_price = 0
        self.long_position_size=0
        self.short_avg_entry_price = 0
        self.short_position_size=0
        
        self.set_params(params)
        
    def set_test_id(self, test_id):
        """테스트 ID 설정"""
        self.test_id = test_id
        
    def fetch_test_data(self):
        """테스트 데이터 가져오기"""
        self.data = backtester.get_data(self.symbol, self.interval, data_type=self.data_type)
        # 트레일링 스탑 용도
        try:
            self.data_5m = backtester.get_data(self.symbol, '5m', data_type=self.data_type)
        except:
            self.data_5m = None
        
    def check_take_profit_conditions(self, row, order: Order):
        """조건으로 인한 익절시 사용 
        EX 마켓주문에서 골든 크로스 일 때 익절인 경우 -> 청산가는 ROW의 CLOSE가 된다."""
        pass

    def check_loss_conditions(self, row, order: Order):
        """조건으로 인한 손절시 사용
        EX 데드 크로스 일 때 손절인 경우 -> 청산가는 ROW의 CLOSE가 된다."""
        pass
    
    def check_cancel_conditions(self, row, order: Order):
        """조건으로 인한 취소시 사용
        """
        pass
    
    def add_trade_record(self, trade):
        """거래 기록 추가"""
        self.trade_history.append(trade)

    def save_results(self):
        """결과 저장"""
        results_df = pd.DataFrame(self.result)
        result_path = f'{self.test_id}_results.csv'
        results_df.to_csv(result_path,index=False)
        backtester.merge_csv_to_excel(self.test_id,result_path)
        
    def prepare_for_backtest(self):
        """백테스트 실행 전 준비"""
        self.trade_history = []
        self.fetch_test_data()
        self.set_indicators()
        self.set_entry_signal()
        if self.test_start_date:
            self.data = self.data.loc[self.test_start_date:]
            if self.data_5m is not None:
                self.data_5m = self.data_5m.loc[self.test_start_date:]
        if self.test_end_date:
            self.data = self.data.loc[:self.test_end_date]
            if self.data_5m is not None:
                self.data_5m = self.data_5m.loc[:self.test_end_date]
                
    def update_avg_entry_price(self, position_size, avg_entry_price, position_side):
        if position_side == OrderPositionSide.LONG:
            self.long_avg_entry_price = (self.long_avg_entry_price * self.long_position_size + avg_entry_price * position_size) / (self.long_position_size + position_size)
            self.long_position_size += position_size
        elif position_side == OrderPositionSide.SHORT:
            self.short_avg_entry_price = (self.short_avg_entry_price * self.short_position_size + avg_entry_price * position_size) / (self.short_position_size + position_size)
            self.short_position_size += position_size
        else:
            raise ValueError("update_avg_entry_price err : Invalid position side")
        
    def update_wallet_balance(self,order):
        order_dict = order.to_trade_record()
        profit = (order_dict['profit_pct'] - 200*self.ptc)/100 * order_dict['margin']
        self.wallet_balance += profit
        
    def update_wallet_balance_with_slippage(self,order):
        
        if self.wallet_balance_with_slippage < 0:
            return
        order_dict = order.to_trade_record()
        profit = (order_dict['profit_pct'] - (200*self.ptc + 100*self.slippage))/100 * order_dict['margin']
        self.wallet_balance_with_slippage += profit
        
    def change_position_size(self,position_size, position_side):
        if position_side == OrderPositionSide.LONG:
            self.long_position_size -= position_size
        else:
            self.short_position_size -= position_size
            
    def update_unrealized_profit(self,row):
        """포지션 청산 후 자산 업데이트"""
        long_profit=0
        short_profit=0
        if self.long_position_size != 0:
            long_profit = (row.close - self.long_avg_entry_price)/ self.long_avg_entry_price * self.long_position_size
        if self.short_position_size != 0:
            short_profit = (self.short_avg_entry_price - row.close)/ self.short_avg_entry_price * self.short_position_size
            
        self.unrealized_profit = long_profit + short_profit
        
    def close_order(self,order:Order,row:DataRow, close_type:CloseType, close_price):
        order.close_order(row, close_type, close_price)
        self.add_trade_record(order)
        self.update_wallet_balance(order)
        self.update_wallet_balance_with_slippage(order)
        self.change_position_size(order.margin,order.position_side)
        self.update_unrealized_profit(row)
    
    def create_order(self, order:Order):
        self.active_orders.append(order)
        if order.status == OrderStatus.ACTIVATED:
            self.update_avg_entry_price(order.margin, order.entry_price,order.position_side)
            
    def process_order(self, row: DataRow):
        """주문 처리 로직"""
        remove_orders = []
        close_position=False
        for order in self.active_orders:
            if row.Index != order.entry_time:
                
                if order.status == OrderStatus.PENDING:
                    if order.check_activation_price(row):
                        order.status = OrderStatus.ACTIVATED
                        order.activated_time = row.Index
                        self.update_avg_entry_price(order.margin, order.entry_price,order.position_side)
                    else:
                        if self.check_cancel_conditions(row, order):
                            order.status = OrderStatus.CANCELED
                            self.active_orders.remove(order)
                            self.cancel_orders.append(order)
                    continue
                            
                if order.status == OrderStatus.ACTIVATED:
                    if order.order_type != OrderType.TRAILING:
                        if order.limit_price is not None:
                            if order.check_limit_price(row):
                                self.close_order(order,row,CloseType.TAKE_PROFIT,order.limit_price)
                                remove_orders.append(order)
                                continue
                        
                        if order.stop_loss_price is not None:
                            if order.check_stop_loss_conditions(row):
                                self.close_order(order,row,CloseType.STOP_LOSS,order.stop_loss_price)
                                remove_orders.append(order)
                                continue
                            
                        if self.check_loss_conditions(row,order):
                            self.close_order(order,row,CloseType.STOP_LOSS,row.close)
                            remove_orders.append(order)
                            continue
                        
                        if order.order_type == OrderType.MARKET and self.check_take_profit_conditions(row,order):
                            self.close_order(order,row,CloseType.TAKE_PROFIT,row.close)
                            remove_orders.append(order)
                            continue
                        continue
                        
                    
                    # 트레일링스탑
                    else:
                        if order.trailing_stop_activated_time is None:
                            if order.check_trailing_stop_activation_price(row):
                                order.trailing_stop_activated_time = row.Index
                            else:
                                if order.stop_loss_price is not None:
                                    if order.check_stop_loss_conditions(row):
                                        self.close_order(order,row,CloseType.STOP_LOSS,order.stop_loss_price)
                                        remove_orders.append(order)
                                        continue
                                if self.check_loss_conditions(row,order):
                                    self.close_order(order,row,CloseType.STOP_LOSS,row.close)
                                    remove_orders.append(order)
                                    continue
                                
                        # elif 사용 금지
                        if order.trailing_stop_activated_time is not None:
                            if order.check_trailing_stop(row, self.data_5m):
                                self.close_order(order,row,CloseType.TAKE_PROFIT,order.limit_price)
                                remove_orders.append(order)
                                continue
                

        for order in remove_orders:
            self.active_orders.remove(order)
        
        position_clear_cond = True
        for order in self.active_orders:
            if order.status == OrderStatus.ACTIVATED:
                position_clear_cond = False
                break
            
        if position_clear_cond:
            self.long_avg_entry_price = 0
            self.short_avg_entry_price = 0
            self.long_position_size = 0
            self.short_position_size = 0
            
        
    def get_order_num_by_position_side(self):
        long_order_num = 0
        short_order_num = 0
        for order in self.active_orders:
            if order.position_side == OrderPositionSide.LONG:
                long_order_num += 1
            elif order.position_side == OrderPositionSide.SHORT:
                short_order_num += 1
        return long_order_num, short_order_num
        
    def run_backtest(self):
        """백테스트 실행 메인 로직"""
        self.prepare_for_backtest()
        # 백테스트 실행 로직 구현
        for row in self.data.itertuples():

            if len(self.active_orders) > 0:
                self.process_order(row)
            
            long_signal, short_signal = self.check_entry_signals(row)
            long_order_num, short_order_num = self.get_order_num_by_position_side()
            
            if long_signal and long_order_num < self.pyramiding:
                self.open_position(row, OrderPositionSide.LONG)
            elif short_signal and short_order_num < self.pyramiding:
                self.open_position(row, OrderPositionSide.SHORT)

                
            self.wallet_balance_list.append(self.wallet_balance)
            self.wallet_balance_with_slippage_list.append(self.wallet_balance_with_slippage)
            self.update_unrealized_profit(row)
            self.margin_balance = self.wallet_balance + self.unrealized_profit
            self.margin_balance_list.append(self.margin_balance)
        try:
            self.data['wallet_balance'] = self.wallet_balance_list
            self.data['wallet_balance_with_slippage'] = self.wallet_balance_with_slippage_list
            self.data['margin_balance'] = self.margin_balance_list
            self.analyze_trade_history()
        except Exception as e:
            traceback.print_exc()
            print(f'wallet update error: {e}')
    
    def set_params(self, params):
        """
        전략 파라미터 설정
        self.params = params
        if params:
            self.signal_var = params[0]
            self.blackflag_atr_period, self.blackflag_atr_factor, self.blackflag_interval = params[1]
            self.supertrend_atr_period, self.supertrend_multiplier, self.supertrend_interval = params[2]
            self.time_loss_var = params[3]
        이런식으로 필요한 파라미터 설정
        """
        pass

    def set_indicators(self, params):
        """
        지표 설정 로직을 구현해야 합니다.
        예: RSI, MACD, 볼린저밴드 등의 기술적 지표
        self.data['indicator'] 컬럼에 지표 값 저장 1 or 0 or -1
        """
        pass

    def set_entry_signal(self, params):
        """
        진입 조건 설정 로직을 구현해야 합니다.
        예: 크로스오버, 돌파, 반전, UT시그널, SUPERTREND V 등
        self.data['signal'] 컬럼에 시그널 값 저장 1 or 0 or -1
        """
        pass

    def check_entry_signals(self, row):
        """진입 시그널 체크 로직을 구현해야 합니다"""
        long_signal = False
        short_signal = False
        return long_signal, short_signal
    
    @abstractmethod
    def open_position(self, row, position_side: OrderPositionSide):
        """포지션 진입 로직을 구현해야 합니다"""
        pass

    def analyze_trade_history(self):
        """거래 기록 분석 """
        trade_history = [i.to_trade_record() for i in self.trade_history]
        result = backtester.analyze_trade_history(
            trade_history, self.data, self.symbol,
            save_trades=self.save_trades,
            leverage=self.leverage,
            pyramiding=self.pyramiding,
            params=self.params if self.params is not None else {}
        )
        if self.plot_results:
            self.plot_results_and_save()
        self.result=result
        
    def plot_results_and_save(self):
        """결과 그래프 그리기"""
        margin_data = self.data[['margin_balance','wallet_balance',
                                'wallet_balance_with_slippage','close']].copy()
        
                # 2) 인덱스가 DatetimeIndex 인지 확인 (필수!)
        margin_data.index = pd.to_datetime(margin_data.index)

        # 3) ‘일’ 단위로 리샘플해 평균값 계산
        daily_data = margin_data.resample('D').last()


        # 5) 시각화 ── 깔끔한 스타일 적용
        plt.style.use('ggplot')
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 첫 번째 y축 (좌측) → wallet 관련
        ax1.plot(daily_data.index,
                daily_data['wallet_balance'],
                label='Wallet Balance',
                linewidth=2)

        ax1.plot(daily_data.index,
                daily_data['wallet_balance_with_slippage'],
                label='Wallet Balance (Slippage)',
                linewidth=2)
        
        ax1.plot(daily_data.index,
                daily_data['margin_balance'],
                label='Margin Balance',
                linewidth=2)

        ax1.set_ylabel('Wallet Balance (USDT)', fontsize=12)
        ax1.set_xlabel('Date', fontsize=12)
        ax1.tick_params(axis='y')
        ax1.grid(alpha=0.3)

        # 두 번째 y축 (우측) → close
        ax2 = ax1.twinx()
        ax2.plot(daily_data.index,
                daily_data['close'],
                label='Close Price',
                color='blue', linestyle='--', linewidth=2)
        ax2.set_ylabel('Close Price (USDT)', fontsize=12)
        ax2.tick_params(axis='y')

        # 제목 및 범례
        fig.suptitle(f'{self.symbol} {self.interval} – Daily Wallet Balance & Price', fontsize=14)

        # 범례 합치기 (두 축의 라벨을 같이 표시)
        lines, labels = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines + lines2, labels + labels2, loc='upper left')

        plt.tight_layout()

        # 6) 파일 저장 (폴더 자동 생성)
        out_path = Path('result_plot') / f'{self.symbol}_test_id_{self.test_id}.png'
        out_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_path, dpi=300)
        plt.close()
        
