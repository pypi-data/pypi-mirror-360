from typing import Dict, Literal, Any, List, Union, Optional
from tsst.base import Base

class Account:
    """交易帳號類別
    """
    def __init__(self, account: str, type: Literal["Stock", "Future", "Option"], source: Any = None):
        self.account = account
        self.type = type
        self.source = source

class BaseLogin(Base):
    """
        登入模組的基底類別
    """
    def __init__(self, is_simulation: bool = True):
        """初始化登入模組

        Args:
            is_simulation (bool, optional): 是否為模擬環境. 預設為 True.
        """
        self.is_simulation = is_simulation
        self.accounts = {
            "Stock": {},
            "Future": {},
            "Option": {},
        }

        self._main_stock_account = None
        self._main_future_account = None
        self._main_option_account = None

    @property
    def main_stock_account(self) -> Account:
        """取得主要股票帳號

        Returns:
            Account: 股票帳號
        """
        if not self._main_stock_account:
            self._main_stock_account = list(self.accounts["Stock"].values())[0]
        
        return self._main_stock_account

    @property
    def main_future_account(self) -> Account:
        """取得主要期貨帳號

        Returns:
            Account: 期貨帳號
        """
        if not self._main_future_account:
            self._main_future_account = list(self.accounts["Future"].values())[0]
        
        return self._main_future_account

    @property
    def main_option_account(self) -> Account:
        """取得主要選擇權帳號

        Returns:
            Account: 選擇權帳號
        """
        if not self._main_option_account:
            self._main_option_account = list(self.accounts["Option"].values())[0]
        
        return self._main_option_account

    def set_main_account(self, account: str, type: Literal["Stock", "Future", "Option"]):
        """設定主要帳號

        Args:
            account (str): 帳號
            type (Literal["Stock", "Future", "Option"]): 帳號類型
        """
        if type == "Stock":
            self._main_stock_account = self.accounts["Stock"][account]
        elif type == "Future":
            self._main_future_account = self.accounts["Future"][account]
        elif type == "Option":
            self._main_option_account = self.accounts["Option"][account]
        else:
            raise ValueError("Account type not found")

    def run(self, params: dict) -> Dict[str, str]:
        """登入 API

        Args:
            params (dict): 參數

        Returns:
            Dict[str, str]: 回傳結果
        """
        raise NotImplementedError("Please implement this method")
    
    def set_account(self, key: str, account: str, type: Literal["Stock", "Future", "Option"], source: Any = None):
        """設定交易帳號

        Args:
            key (str): 交易帳號的 key
            account (str): 交易帳號
            type (str): 交易帳號類型
            source (Any, optional): 交易帳號來源，例如永豐或者群益等券商的帳戶資料. 預設為 None.
        """
        assert type in ["Stock", "Future", "Option"]

        if key in self.accounts[type]:
            return

        self.accounts[type][key] = Account(account, type, source)
