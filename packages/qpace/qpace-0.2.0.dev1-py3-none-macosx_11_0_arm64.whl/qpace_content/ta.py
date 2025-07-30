
  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from qpace_content import _lib
  
  


def accdist(ctx: Ctx, ) -> List[float]:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    return _lib.Incr_fn_accdist_8f6067(ctx=ctx, ).collect()

class AccdistLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Accdist:
    """
Total money flowing in and out (Accumulation/Distribution)

`accdist() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_accdist_8f6067(ctx, )
        self.locals = AccdistLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def cum(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    return _lib.Incr_fn_cum_a00134(ctx=ctx, ).collect(_29947_src=src)

class CumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cum:
    """
Adds up the values so far (running total)

`cum(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cum_a00134(ctx, )
        self.locals = CumLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_29947_src=src)
    



def change(ctx: Ctx, src: List[float], ) -> List[float]:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    return _lib.Incr_fn_change_ab6c9c(ctx=ctx, ).collect(_29949_src=src)

class ChangeLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Change:
    """
How much it moved from the previous bar

`change(series<float> src) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_change_ab6c9c(ctx, )
        self.locals = ChangeLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_29949_src=src)
    



def barssince(ctx: Ctx, condition: List[bool], ) -> List[int]:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    return _lib.Incr_fn_barssince_28f975(ctx=ctx, ).collect(_29951_condition=condition)

class BarssinceLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Barssince:
    """
Number of bars since something happened

`barssince(series<bool> condition) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_barssince_28f975(ctx, )
        self.locals = BarssinceLocals(self.inner)

    def next(self, condition: bool) -> Optional[int]:
        return self.inner.next(_29951_condition=condition)
    



def roc(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_roc_7a84d5(ctx=ctx, ).collect(_29953_src=src, _29954_length=length)

class RocLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Roc:
    """
Speed of change over given bars

`roc(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_roc_7a84d5(ctx, )
        self.locals = RocLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29953_src=src, _29954_length=length)
    



def crossover(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossover_079468(ctx=ctx, ).collect(_29956_source1=source1, _29957_source2=source2)

class CrossoverLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossover:
    """
When line1 moves above line2

`crossover(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossover_079468(ctx, )
        self.locals = CrossoverLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_29956_source1=source1, _29957_source2=source2)
    



def crossunder(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_crossunder_45c2a1(ctx=ctx, ).collect(_29959_source1=source1, _29960_source2=source2)

class CrossunderLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Crossunder:
    """
When line1 drops below line2

`crossunder(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_crossunder_45c2a1(ctx, )
        self.locals = CrossunderLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_29959_source1=source1, _29960_source2=source2)
    



def cross(ctx: Ctx, source1: List[float], source2: List[float], ) -> List[bool]:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    return _lib.Incr_fn_cross_754bd2(ctx=ctx, ).collect(_29962_source1=source1, _29963_source2=source2)

class CrossLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Cross:
    """
When two lines meet

`cross(series<float> source1, series<float> source2) -> bool`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cross_754bd2(ctx, )
        self.locals = CrossLocals(self.inner)

    def next(self, source1: float, source2: float) -> Optional[bool]:
        return self.inner.next(_29962_source1=source1, _29963_source2=source2)
    



def highestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_highestbars_96bbd2(ctx=ctx, ).collect(_29965_src=src, _29966_length=length)

class HighestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highestbars:
    """
Bar index with highest value in period

`highestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highestbars_96bbd2(ctx, )
        self.locals = HighestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_29965_src=src, _29966_length=length)
    



def lowestbars(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[int]:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    return _lib.Incr_fn_lowestbars_4969cb(ctx=ctx, ).collect(_29968_src=src, _29969_length=length)

class LowestbarsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowestbars:
    """
Bar index with lowest value in period

`lowestbars(series<float> src, int length = 14) -> int`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowestbars_4969cb(ctx, )
        self.locals = LowestbarsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[int]:
        return self.inner.next(_29968_src=src, _29969_length=length)
    



def highest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_highest_27dfe4(ctx=ctx, ).collect(_29971_src=src, _29972_length=length)

class HighestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Highest:
    """
Highest value in period

`highest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_highest_27dfe4(ctx, )
        self.locals = HighestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29971_src=src, _29972_length=length)
    



def lowest(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lowest_16452f(ctx=ctx, ).collect(_29974_src=src, _29975_length=length)

class LowestLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Lowest:
    """
Lowest value in period

`lowest(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lowest_16452f(ctx, )
        self.locals = LowestLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29974_src=src, _29975_length=length)
    



def swma(ctx: Ctx, src: List[float], ) -> List[float]:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    return _lib.Incr_fn_swma_0b8d30(ctx=ctx, ).collect(_29977_src=src)

class SwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Swma:
    """
Smoothed weighted moving average line

`swma(series<float> src) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_swma_0b8d30(ctx, )
        self.locals = SwmaLocals(self.inner)

    def next(self, src: float) -> Optional[float]:
        return self.inner.next(_29977_src=src)
    



def sma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_sma_b24bc5(ctx=ctx, ).collect(_29979_src=src, _29980_length=length)

class SmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Sma:
    """
Simple moving average (plain average)

`sma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_sma_b24bc5(ctx, )
        self.locals = SmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29979_src=src, _29980_length=length)
    



def ema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_ema_f27391(ctx=ctx, ).collect(_29982_src=src, _29983_length=length)

class EmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Ema:
    """
Exponential moving average (reacts faster)

`ema(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ema_f27391(ctx, )
        self.locals = EmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29982_src=src, _29983_length=length)
    



def rma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rma_96c11d(ctx=ctx, ).collect(_29985_src=src, _29986_length=length)

class RmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rma:
    """
RMA used inside RSI

`rma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rma_96c11d(ctx, )
        self.locals = RmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29985_src=src, _29986_length=length)
    



def wma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_wma_bf4d1c(ctx=ctx, ).collect(_29988_src=src, _29989_length=length)

class WmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Wma:
    """
Weighted moving average (recent bars matter more)

`wma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_wma_bf4d1c(ctx, )
        self.locals = WmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29988_src=src, _29989_length=length)
    



def lwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_lwma_99bf78(ctx=ctx, ).collect(_29991_src=src, _29992_length=length)

class LwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Lwma:
    """
Linear weighted moving average

`lwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_lwma_99bf78(ctx, )
        self.locals = LwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29991_src=src, _29992_length=length)
    



def hma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_hma_0b63f6(ctx=ctx, ).collect(_29994_src=src, _29995_length=length)

class HmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Hma:
    """
Hull moving average (smooth and fast)

`hma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_hma_0b63f6(ctx, )
        self.locals = HmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29994_src=src, _29995_length=length)
    



def vwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_vwma_2786e8(ctx=ctx, ).collect(_29997_src=src, _29998_length=length)

class VwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Vwma:
    """
Volume‑weighted moving average

`vwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vwma_2786e8(ctx, )
        self.locals = VwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_29997_src=src, _29998_length=length)
    



def dev(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_dev_bed781(ctx=ctx, ).collect(_30000_src=src, _30001_length=length)

class DevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dev:
    """
Standard deviation (how much it varies)

`dev(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dev_bed781(ctx, )
        self.locals = DevLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30000_src=src, _30001_length=length)
    



def tr(ctx: Ctx, handle_na: Optional[bool] = None, ) -> List[float]:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    return _lib.Incr_fn_tr_68789c(ctx=ctx, ).collect(_30003_handle_na=handle_na)

class TrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Tr:
    """
True range (how much price moved in bar)

`tr(bool handle_na = true) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tr_68789c(ctx, )
        self.locals = TrLocals(self.inner)

    def next(self, handle_na: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_30003_handle_na=handle_na)
    



def atr(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    return _lib.Incr_fn_atr_5c0d75(ctx=ctx, ).collect(_30005_length=length)

class AtrLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Atr:
    """
Average true range (typical move size)

`atr(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_atr_5c0d75(ctx, )
        self.locals = AtrLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30005_length=length)
    



def rsi(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_rsi_ecc5c2(ctx=ctx, ).collect(_30007_src=src, _30008_length=length)

class RsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Rsi:
    """
Relative Strength Index (momentum strength)

`rsi(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_rsi_ecc5c2(ctx, )
        self.locals = RsiLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30007_src=src, _30008_length=length)
    



def cci(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_cci_27ef02(ctx=ctx, ).collect(_30010_src=src, _30011_length=length)

class CciLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Cci:
    """
Commodity Channel Index (price vs average)

`cci(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_cci_27ef02(ctx, )
        self.locals = CciLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30010_src=src, _30011_length=length)
    



def stdev(ctx: Ctx, src: List[float], length: int, biased: Optional[bool] = None, ) -> List[float]:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    return _lib.Incr_fn_stdev_401a66(ctx=ctx, ).collect(_30013_src=src, _30014_length=length, _30015_biased=biased)

class StdevLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Stdev:
    """
Standard deviation over period

`stdev(series<float> src, int length, bool biased = true) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stdev_401a66(ctx, )
        self.locals = StdevLocals(self.inner)

    def next(self, src: float, length: int, biased: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_30013_src=src, _30014_length=length, _30015_biased=biased)
    



def aroon(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_aroon_50c15d(ctx=ctx, ).collect(_30017_length=length)

class AroonLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Aroon:
    """
Aroon indicator (time since highs/lows)

`aroon(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_aroon_50c15d(ctx, )
        self.locals = AroonLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_30017_length=length)
    



def supertrend(ctx: Ctx, src: List[float], factor: float, atr_period: int, ) -> Tuple[float, int]:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    return _lib.Incr_fn_supertrend_db8d7e(ctx=ctx, ).collect(_30019_src=src, _30020_factor=factor, _30021_atr_period=atr_period)

class SupertrendLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Supertrend:
    """
Supertrend line for direction

`supertrend(series<float> src, float factor, int atr_period) -> [float, int]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_supertrend_db8d7e(ctx, )
        self.locals = SupertrendLocals(self.inner)

    def next(self, src: float, factor: float, atr_period: int) -> Optional[Tuple[float, int]]:
        return self.inner.next(_30019_src=src, _30020_factor=factor, _30021_atr_period=atr_period)
    



def awesome_oscillator(ctx: Ctx, src: List[float], slow_length: Optional[int] = None, fast_length: Optional[int] = None, ) -> List[float]:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    return _lib.Incr_fn_awesome_oscillator_29200a(ctx=ctx, ).collect(_30023_src=src, _30024_slow_length=slow_length, _30025_fast_length=fast_length)

class AwesomeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AwesomeOscillator:
    """
Awesome Oscillator (momentum)

`awesome_oscillator(series<float> src, int slow_length = 5, int fast_length = 34) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_awesome_oscillator_29200a(ctx, )
        self.locals = AwesomeOscillatorLocals(self.inner)

    def next(self, src: float, slow_length: Optional[int] = None, fast_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30023_src=src, _30024_slow_length=slow_length, _30025_fast_length=fast_length)
    



def balance_of_power(ctx: Ctx, ) -> List[float]:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    return _lib.Incr_fn_balance_of_power_a4bea2(ctx=ctx, ).collect()

class BalanceOfPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class BalanceOfPower:
    """
Balance of power between buyers and sellers

`balance_of_power() -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_balance_of_power_a4bea2(ctx, )
        self.locals = BalanceOfPowerLocals(self.inner)

    def next(self, ) -> Optional[float]:
        return self.inner.next()
    



def bollinger_bands_pct_b(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_pct_b_e737a5(ctx=ctx, ).collect(_30030_src=src, _30031_length=length, _30032_mult=mult)

class BollingerBandsPctBLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsPctB:
    """
%B – where price is inside Bollinger Bands (0‑1)

`bollinger_bands_pct_b(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_pct_b_e737a5(ctx, )
        self.locals = BollingerBandsPctBLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_30030_src=src, _30031_length=length, _30032_mult=mult)
    



def bollinger_bands_width(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> List[float]:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    return _lib.Incr_fn_bollinger_bands_width_2b304d(ctx=ctx, ).collect(_30039_src=src, _30040_length=length, _30041_mult=mult)

class BollingerBandsWidthLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBandsWidth:
    """
Band width – how wide Bollinger Bands are

`bollinger_bands_width(series<float> src, int length = 20, float mult = 2.0) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_width_2b304d(ctx, )
        self.locals = BollingerBandsWidthLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[float]:
        return self.inner.next(_30039_src=src, _30040_length=length, _30041_mult=mult)
    



def bollinger_bands(ctx: Ctx, src: List[float], length: Optional[int] = None, mult: Optional[float] = None, ) -> Tuple[float, float]:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    return _lib.Incr_fn_bollinger_bands_c2f493(ctx=ctx, ).collect(_30048_src=src, _30049_length=length, _30050_mult=mult)

class BollingerBandsLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BollingerBands:
    """
Gives upper and lower Bollinger Bands

`bollinger_bands(series<float> src, int length = 20, float mult = 2.0) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bollinger_bands_c2f493(ctx, )
        self.locals = BollingerBandsLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None, mult: Optional[float] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_30048_src=src, _30049_length=length, _30050_mult=mult)
    



def chaikin_money_flow(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    return _lib.Incr_fn_chaikin_money_flow_1f6cb4(ctx=ctx, ).collect(_30056_length=length)

class ChaikinMoneyFlowLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def cumVol(self) -> float:
        return self.__inner._30057_cumVol()
  
      

class ChaikinMoneyFlow:
    """
Chaikin Money Flow – volume weighted flow

`chaikin_money_flow(int length = 20) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chaikin_money_flow_1f6cb4(ctx, )
        self.locals = ChaikinMoneyFlowLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30056_length=length)
    



def chande_kroll_stop(ctx: Ctx, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_chande_kroll_stop_55d31f(ctx=ctx, ).collect(_30061_atr_length=atr_length, _30062_atr_coeff=atr_coeff, _30063_stop_length=stop_length)

class ChandeKrollStopLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChandeKrollStop:
    """
Chande‑Kroll stop lines

`chande_kroll_stop(int atr_length = 10, float atr_coeff = 1.0, int stop_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_chande_kroll_stop_55d31f(ctx, )
        self.locals = ChandeKrollStopLocals(self.inner)

    def next(self, atr_length: Optional[int] = None, atr_coeff: Optional[float] = None, stop_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_30061_atr_length=atr_length, _30062_atr_coeff=atr_coeff, _30063_stop_length=stop_length)
    



def choppiness_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_choppiness_index_28e6a8(ctx=ctx, ).collect(_30072_length=length)

class ChoppinessIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ChoppinessIndex:
    """
Choppiness Index – tells if market is sideways or trending

`choppiness_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_choppiness_index_28e6a8(ctx, )
        self.locals = ChoppinessIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30072_length=length)
    



def connors_rsi(ctx: Ctx, src: List[float], rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None, ) -> List[float]:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    return _lib.Incr_fn_connors_rsi_4e7137(ctx=ctx, ).collect(_30079_src=src, _30080_rsi_length=rsi_length, _30081_up_down_length=up_down_length, _30082_roc_length=roc_length)

class ConnorsRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ConnorsRsi:
    """
`connors_rsi(series<float> src, int rsi_length = 3, int up_down_length = 2, int roc_length = 100) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_connors_rsi_4e7137(ctx, )
        self.locals = ConnorsRsiLocals(self.inner)

    def next(self, src: float, rsi_length: Optional[int] = None, up_down_length: Optional[int] = None, roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30079_src=src, _30080_rsi_length=rsi_length, _30081_up_down_length=up_down_length, _30082_roc_length=roc_length)
    



def coppock_curve(ctx: Ctx, src: List[float], wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None, ) -> List[float]:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    return _lib.Incr_fn_coppock_curve_d20214(ctx=ctx, ).collect(_30088_src=src, _30089_wma_length=wma_length, _30090_long_roc_length=long_roc_length, _30091_short_roc_length=short_roc_length)

class CoppockCurveLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class CoppockCurve:
    """
Coppock Curve – long‑term momentum

`coppock_curve(series<float> src, int wma_length = 10, int long_roc_length = 14, int short_roc_length = 11) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_coppock_curve_d20214(ctx, )
        self.locals = CoppockCurveLocals(self.inner)

    def next(self, src: float, wma_length: Optional[int] = None, long_roc_length: Optional[int] = None, short_roc_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30088_src=src, _30089_wma_length=wma_length, _30090_long_roc_length=long_roc_length, _30091_short_roc_length=short_roc_length)
    



def donchian_channel(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> Tuple[float, float, float]:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    return _lib.Incr_fn_donchian_channel_2863c8(ctx=ctx, ).collect(_30093_src=src, _30094_length=length)

class DonchianChannelLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DonchianChannel:
    """
Donchian Channel highs/lows

`donchian_channel(series<float> src, int length = 20) -> [float, float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_donchian_channel_2863c8(ctx, )
        self.locals = DonchianChannelLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[Tuple[float, float, float]]:
        return self.inner.next(_30093_src=src, _30094_length=length)
    



def macd(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_macd_c4fc5c(ctx=ctx, ).collect(_30099_src=src, _30100_short_length=short_length, _30101_long_length=long_length)

class MacdLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Macd:
    """
MACD line (fast trend vs slow)

`macd(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_macd_c4fc5c(ctx, )
        self.locals = MacdLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30099_src=src, _30100_short_length=short_length, _30101_long_length=long_length)
    



def price_oscillator(ctx: Ctx, src: List[float], short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    return _lib.Incr_fn_price_oscillator_4911a5(ctx=ctx, ).collect(_30104_src=src, _30105_short_length=short_length, _30106_long_length=long_length)

class PriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class PriceOscillator:
    """
Price oscillator in percent

`price_oscillator(series<float> src, int short_length = 12, int long_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_price_oscillator_4911a5(ctx, )
        self.locals = PriceOscillatorLocals(self.inner)

    def next(self, src: float, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30104_src=src, _30105_short_length=short_length, _30106_long_length=long_length)
    



def relative_vigor_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_vigor_index_bc336f(ctx=ctx, ).collect(_30111_length=length)

class RelativeVigorIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVigorIndex:
    """
Relative Vigor Index – strength of close vs range

`relative_vigor_index(int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_vigor_index_bc336f(ctx, )
        self.locals = RelativeVigorIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30111_length=length)
    



def relative_volatility_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_relative_volatility_index_6692f2(ctx=ctx, ).collect(_30113_src=src, _30114_length=length)

class RelativeVolatilityIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class RelativeVolatilityIndex:
    """
Relative Volatility Index – like RSI but for volatility

`relative_volatility_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_relative_volatility_index_6692f2(ctx, )
        self.locals = RelativeVolatilityIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30113_src=src, _30114_length=length)
    



def stochastic_rsi(ctx: Ctx, src: List[float], stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None, ) -> Tuple[float, float]:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    return _lib.Incr_fn_stochastic_rsi_7b3d90(ctx=ctx, ).collect(_30120_src=src, _30121_stoch_length=stoch_length, _30122_rsi_length=rsi_length, _30123_k=k, _30124_d=d)

class StochasticRsiLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class StochasticRsi:
    """
Stochastic RSI

`stochastic_rsi(series<float> src, int stoch_length = 14, int rsi_length = 14, int k = 3, int d = 3) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_stochastic_rsi_7b3d90(ctx, )
        self.locals = StochasticRsiLocals(self.inner)

    def next(self, src: float, stoch_length: Optional[int] = None, rsi_length: Optional[int] = None, k: Optional[int] = None, d: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_30120_src=src, _30121_stoch_length=stoch_length, _30122_rsi_length=rsi_length, _30123_k=k, _30124_d=d)
    



def ultimate_oscillator(ctx: Ctx, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    return _lib.Incr_fn_ultimate_oscillator_23f2f1(ctx=ctx, ).collect(_30133_fast_length=fast_length, _30134_medium_length=medium_length, _30135_slow_length=slow_length)

class UltimateOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class UltimateOscillator:
    """
Ultimate Oscillator – combines 3 speeds

`ultimate_oscillator(int fast_length = 7, int medium_length = 14, int slow_length = 28) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ultimate_oscillator_23f2f1(ctx, )
        self.locals = UltimateOscillatorLocals(self.inner)

    def next(self, fast_length: Optional[int] = None, medium_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30133_fast_length=fast_length, _30134_medium_length=medium_length, _30135_slow_length=slow_length)
    



def volume_oscillator(ctx: Ctx, short_length: Optional[int] = None, long_length: Optional[int] = None, ) -> List[float]:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    return _lib.Incr_fn_volume_oscillator_45fb33(ctx=ctx, ).collect(_30145_short_length=short_length, _30146_long_length=long_length)

class VolumeOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VolumeOscillator:
    """
Volume Oscillator – volume momentum

`volume_oscillator(int short_length = 5, int long_length = 10) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_volume_oscillator_45fb33(ctx, )
        self.locals = VolumeOscillatorLocals(self.inner)

    def next(self, short_length: Optional[int] = None, long_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30145_short_length=short_length, _30146_long_length=long_length)
    



def vortex_indicator(ctx: Ctx, length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    return _lib.Incr_fn_vortex_indicator_f8f98c(ctx=ctx, ).collect(_30151_length=length)

class VortexIndicatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class VortexIndicator:
    """
Vortex Indicator – shows trend direction

`vortex_indicator(int length = 14) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_vortex_indicator_f8f98c(ctx, )
        self.locals = VortexIndicatorLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_30151_length=length)
    



def williams_pct_r(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_williams_pct_r_123677(ctx=ctx, ).collect(_30158_src=src, _30159_length=length)

class WilliamsPctRLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class WilliamsPctR:
    """
Williams %R – overbought/oversold

`williams_pct_r(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_williams_pct_r_123677(ctx, )
        self.locals = WilliamsPctRLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30158_src=src, _30159_length=length)
    



def advance_decline_ratio(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    return _lib.Incr_fn_advance_decline_ratio_f5ac2e(ctx=ctx, ).collect(_30164_length=length)

class AdvanceDeclineRatioLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AdvanceDeclineRatio:
    """
Advance/Decline Ratio (Bars)

`advance_decline_ratio(int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_advance_decline_ratio_f5ac2e(ctx, )
        self.locals = AdvanceDeclineRatioLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30164_length=length)
    



def detrended_price_oscillator(ctx: Ctx, length: Optional[int] = None, centered: Optional[bool] = None, ) -> List[float]:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    return _lib.Incr_fn_detrended_price_oscillator_53d64c(ctx=ctx, ).collect(_30170_length=length, _30171_centered=centered)

class DetrendedPriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class DetrendedPriceOscillator:
    """
Detrended Price Oscillator (DPO)

`detrended_price_oscillator(int length = 21, bool centered = false) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_detrended_price_oscillator_53d64c(ctx, )
        self.locals = DetrendedPriceOscillatorLocals(self.inner)

    def next(self, length: Optional[int] = None, centered: Optional[bool] = None) -> Optional[float]:
        return self.inner.next(_30170_length=length, _30171_centered=centered)
    



def bull_bear_power(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    return _lib.Incr_fn_bull_bear_power_0290d7(ctx=ctx, ).collect(_30176_length=length)

class BullBearPowerLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class BullBearPower:
    """
Bull Bear Power (BBP)

`bull_bear_power(int length = 13) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_bull_bear_power_0290d7(ctx, )
        self.locals = BullBearPowerLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30176_length=length)
    



def absolute_price_oscillator(ctx: Ctx, src: List[float], fast_length: Optional[int] = None, slow_length: Optional[int] = None, ) -> List[float]:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    return _lib.Incr_fn_absolute_price_oscillator_32a84e(ctx=ctx, ).collect(_30182_src=src, _30183_fast_length=fast_length, _30184_slow_length=slow_length)

class AbsolutePriceOscillatorLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class AbsolutePriceOscillator:
    """
Absolute Price Oscillator (APO)

`absolute_price_oscillator(series<float> src, int fast_length = 12, int slow_length = 26) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_absolute_price_oscillator_32a84e(ctx, )
        self.locals = AbsolutePriceOscillatorLocals(self.inner)

    def next(self, src: float, fast_length: Optional[int] = None, slow_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30182_src=src, _30183_fast_length=fast_length, _30184_slow_length=slow_length)
    



def know_sure_thing(ctx: Ctx, src: List[float], roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None, ) -> Tuple[float, float]:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    return _lib.Incr_fn_know_sure_thing_7400e2(ctx=ctx, ).collect(_30188_src=src, _30189_roc_length1=roc_length1, _30190_roc_length2=roc_length2, _30191_roc_length3=roc_length3, _30192_roc_length4=roc_length4, _30193_sma_length1=sma_length1, _30194_sma_length2=sma_length2, _30195_sma_length3=sma_length3, _30196_sma_length4=sma_length4, _30197_sig_length=sig_length)

class KnowSureThingLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class KnowSureThing:
    """
Know Sure Thing (KST)

`know_sure_thing(series<float> src, int roc_length1 = 10, int roc_length2 = 15, int roc_length3 = 20, int roc_length4 = 30, int sma_length1 = 10, int sma_length2 = 10, int sma_length3 = 10, int sma_length4 = 15, int sig_length = 9) -> [float, float]`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_know_sure_thing_7400e2(ctx, )
        self.locals = KnowSureThingLocals(self.inner)

    def next(self, src: float, roc_length1: Optional[int] = None, roc_length2: Optional[int] = None, roc_length3: Optional[int] = None, roc_length4: Optional[int] = None, sma_length1: Optional[int] = None, sma_length2: Optional[int] = None, sma_length3: Optional[int] = None, sma_length4: Optional[int] = None, sig_length: Optional[int] = None) -> Optional[Tuple[float, float]]:
        return self.inner.next(_30188_src=src, _30189_roc_length1=roc_length1, _30190_roc_length2=roc_length2, _30191_roc_length3=roc_length3, _30192_roc_length4=roc_length4, _30193_sma_length1=sma_length1, _30194_sma_length2=sma_length2, _30195_sma_length3=sma_length3, _30196_sma_length4=sma_length4, _30197_sig_length=sig_length)
    



def momentum(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    return _lib.Incr_fn_momentum_9367af(ctx=ctx, ).collect(_30205_src=src, _30206_length=length)

class MomentumLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Momentum:
    """
Momentum (MOM)

`momentum(series<float> src, int length = 10) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_momentum_9367af(ctx, )
        self.locals = MomentumLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30205_src=src, _30206_length=length)
    



def trix(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    return _lib.Incr_fn_trix_d5eee1(ctx=ctx, ).collect(_30208_src=src, _30209_length=length)

class TrixLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Trix:
    """
Trix

`trix(series<float> src, int length = 18) -> series<float>`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_trix_d5eee1(ctx, )
        self.locals = TrixLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30208_src=src, _30209_length=length)
    



def true_strength_index(ctx: Ctx, src: List[float], long_length: Optional[int] = None, short_length: Optional[int] = None, ) -> List[float]:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    return _lib.Incr_fn_true_strength_index_cb650b(ctx=ctx, ).collect(_30211_src=src, _30212_long_length=long_length, _30213_short_length=short_length)

class TrueStrengthIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class TrueStrengthIndex:
    """
True Strength Index (TSI)

`true_strength_index(series<float> src, int long_length = 25, int short_length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_true_strength_index_cb650b(ctx, )
        self.locals = TrueStrengthIndexLocals(self.inner)

    def next(self, src: float, long_length: Optional[int] = None, short_length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30211_src=src, _30212_long_length=long_length, _30213_short_length=short_length)
    



def dema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_dema_21bb2c(ctx=ctx, ).collect(_30219_src=src, _30220_length=length)

class DemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Dema:
    """
Double Exponential Moving Average (DEMA)

`dema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_dema_21bb2c(ctx, )
        self.locals = DemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30219_src=src, _30220_length=length)
    



def fwma(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_fwma_893a68(ctx=ctx, ).collect(_30229_src=src, _30230_length=length)

class FwmaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

class Fwma:
    """
Fibonacci Weighted Moving Average (FWMA)

`fwma(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_fwma_893a68(ctx, )
        self.locals = FwmaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30229_src=src, _30230_length=length)
    



def money_flow_index(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    return _lib.Incr_fn_money_flow_index_d445f8(ctx=ctx, ).collect(_30236_src=src, _30237_length=length)

class MoneyFlowIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class MoneyFlowIndex:
    """
Money Flow Index (MFI)

`money_flow_index(series<float> src, int length = 14) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_money_flow_index_d445f8(ctx, )
        self.locals = MoneyFlowIndexLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30236_src=src, _30237_length=length)
    



def ease_of_movement(ctx: Ctx, length: Optional[int] = None, divisor: Optional[int] = None, ) -> List[float]:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    return _lib.Incr_fn_ease_of_movement_ef7bc9(ctx=ctx, ).collect(_30239_length=length, _30240_divisor=divisor)

class EaseOfMovementLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class EaseOfMovement:
    """
Ease of Movement (EOM)

`ease_of_movement(int length = 14, int divisor = 10000) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_ease_of_movement_ef7bc9(ctx, )
        self.locals = EaseOfMovementLocals(self.inner)

    def next(self, length: Optional[int] = None, divisor: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30239_length=length, _30240_divisor=divisor)
    



def elder_force_index(ctx: Ctx, length: Optional[int] = None, ) -> List[float]:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    return _lib.Incr_fn_elder_force_index_76e796(ctx=ctx, ).collect(_30242_length=length)

class ElderForceIndexLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class ElderForceIndex:
    """
Elder Force Index (EFI)

`elder_force_index(int length = 13) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_elder_force_index_76e796(ctx, )
        self.locals = ElderForceIndexLocals(self.inner)

    def next(self, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30242_length=length)
    



def tema(ctx: Ctx, src: List[float], length: Optional[int] = None, ) -> List[float]:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    return _lib.Incr_fn_tema_f0a88c(ctx=ctx, ).collect(_30244_src=src, _30245_length=length)

class TemaLocals:
    def __init__(self, inner):
        self.__inner = inner

    

      

class Tema:
    """
Tripple Exponential Moving Average (TEMA)

`tema(series<float> src, int length = 9) -> float`
    """
    
    def __init__(self, ctx: Ctx, ):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_tema_f0a88c(ctx, )
        self.locals = TemaLocals(self.inner)

    def next(self, src: float, length: Optional[int] = None) -> Optional[float]:
        return self.inner.next(_30244_src=src, _30245_length=length)
    
          