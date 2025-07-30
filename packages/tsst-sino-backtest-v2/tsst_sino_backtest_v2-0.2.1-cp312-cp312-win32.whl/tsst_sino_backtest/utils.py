import logging
import os

from rich.console import Console
from datetime import datetime, date
from typing import Any

console = Console()

# 設置日誌輸出目錄
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # 確保目錄存在

# 設置日誌格式
log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# 設置日誌記錄器
logging.basicConfig(
    level=logging.DEBUG,  # 設置最低日誌級別
    format=log_format,
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "backtest.log"), encoding="utf-8"),  # 檔案輸出
    ],
)

logger = logging.getLogger("app")

def format_to_dt(value: Any) -> datetime:
    """格式化時間資料

    Args:
        value (datetime|date|str): 時間資料, 字串或者日期物件

    Returns:
        datetime: 格式化後的時間物件
    """
    if isinstance(value, str):
        if '.' in value:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        elif ':' in value:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.strptime(value, '%Y-%m-%d')
    
    if type(value) is date:
        return datetime.combine(value, datetime.min.time())

    return value

def format_nano_ts_to_second_ts(value: int, truncate_gmt_sec: int = 0) -> float:
    """將奈秒時間戳轉換為秒時間戳
    
    Args:
        value (int): 奈秒時間戳
        truncate_gmt_sec (int): 減去 GMT + n 的秒數
    
    Returns:
        float: 秒時間戳
    """
    # @TODO 看有沒有更好的做法
    # 永豐歷史 Tick 的時區是 GMT + 0, 為了讓本地電腦也可以正常顯示, 所以減掉 8 小時的秒數
    return value / 1e9 - (truncate_gmt_sec * 3600) # 歷史 Tick 的時間戳記單位是 ns, 而即時的 tick 是 ms, 而客戶端目前是使用 fromtimestamp 轉換, 

def make_dir(path: str):
    """建立目錄

    Args:
        path (str): 目錄路徑
    """
    if not os.path.exists(path):
        console.print(f"建立 {path} 資料夾...", style="bold green")
        os.makedirs(path)
