import os

from enum import Enum

from tsst_sino_backtest import __version__

# ============================================================================= #
# 系統相關
# ============================================================================= #
class BASIC_INFO(str, Enum):
    """
        回測模組基本資訊
    """
    name = 'Sino Backtest Module'
    version = __version__

    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_path = os.path.abspath(os.path.join(current_dir, '../..'))
    data_dir = os.path.join(root_path, 'data')

    fee_settings_name = 'fee_settings.json'

class FLAG(str, Enum):
    """
        回測模組 Flag
    """
    exit_send_tick = 'exit_send_tick'
    exit_receive_response = 'exit_receive_response'
    exit_receive_positions = 'exit_receive_positions'

    finish_backfilling = 'finish_backfilling'

# ============================================================================= #
# 交易相關
# ============================================================================= #
class BaseConstant(str, Enum):
    def __str__(self):
        return self.value  # 返回字串值

    def __format__(self, format_spec):
        return self.value  # 返回字串值
    
    @classmethod
    def from_value(cls, value):
        """允許根據 value 找到對應的 Enum 成員"""
        for member in cls:
            if member.value == value:
                return member.value
        raise ValueError(f"Invalid value: {value}")

class OperationType(BaseConstant):
    """操作類型
    """
    NEW = "New"
    CANCEL = "Cancel"
    UPDATE_PRICE = "UpdatePrice"
    UPDATE_QTY = "UpdateQty"
    DEAL = "Deal"
    UPDATE_PRICE_QTY = "UpdatePriceQty"
    DYNAMIC_CANCEL = "DynamicCancel"

class Action(BaseConstant):
    """買賣類型
    """
    BUY = "Buy"
    SELL = "Sell"

class PriceType(BaseConstant):
    """價格類型
    """
    LMT = "LMT"
    MKT = "MKT"
    MKP = "MKP"

class OrderType(BaseConstant):
    """委託類型
    """
    ROD = "ROD"
    IOC = "IOC"
    FOK = "FOK"

class OrderCond(BaseConstant):
    """委託條件
    """
    CASH = "Cash"
    MARGIN_T = "MarginTrading" # 融資
    SHORT_S = "ShortSelling" # 融券

class OrderLot(BaseConstant):
    """委託方式
    """
    COMMON = "Common" # 整股
    FIXING = "Fixing" # 盤後定盤
    ODD = "Odd" # 盤後零股
    INTRADAY_ODD = "IntradayOdd" # 盤中零股

class OCType(BaseConstant):
    """開倉或平倉類型
    """
    AUTO = "Auto"
    NEW = "New"
    COVER = "Cover"
    DAY_TRADE = "DayTrade"

class BaseCode(Enum):
    @property
    def code(self):
        return self.value["code"]

    @property
    def message(self):
        return self.value["message"]

class SuccessCode(BaseCode):
    # 縮寫說明
    # BT: 回測模組相關相關
    # AUTH: 身分驗證相關
    CreateOrder = { "code": "BT-00000", "message": "建立訂單成功" }
    OrderBeCancel = { "code": "BT-00001", "message": "剩餘委託單已取消" }
    ModifyOrder = { "code": "BT-00002", "message": "修改訂單成功" }
    CancelOrder = { "code": "BT-00003", "message": "取消訂單成功" }

class ErrorCode(BaseCode):
    # 縮寫說明
    # BT: 回測模組相關相關
    # AUTH: 身分驗證相關
    ArgumentNotMatchException = { "code": "BT-10000", "message": "參數不符合預期" }
    NotSupportMarketException = { "code": "BT-10001", "message": "不支援的市場類型" }
    TradeNotFoundException = { "code": "BT-10002", "message": "找不到交易紀錄" }

class FutureIndexContractValue(BaseConstant):
    """期指合約價值(單位: 口)
    """
    TX : float = 200    # 台指期
    MTX: float = 50     # 小台指期
    TMF: float = 10     # 微台指期
    M1F: float = 10     # 台灣中型 100
    E4F: float = 100    # 台灣永續期貨
    TE : float = 4000   # 電子期貨
    ZEF: float = 500    # 小型電子期貨
    TF : float = 1000   # 金融期貨
    ZFF: float = 250    # 小型金融期貨
    XIF: float = 100    # 非金電期貨
    SHF: float = 1000   # 航運期貨
    SOF: float = 50     # 半導體 30
    BTF: float = 50     # 台灣生技
    GTF: float = 4000   # 櫃買
    G2F: float = 50     # 富櫃 200
    TJF: float = 200    # 東證期貨
    UDF: float = 20     # 美國道瓊
    SPF: float = 200    # 標普 500
    UNF: float = 50     # 那斯達克 100
    SXF: float = 80     # 費半
    F1F: float = 50     # 英國富時 100
