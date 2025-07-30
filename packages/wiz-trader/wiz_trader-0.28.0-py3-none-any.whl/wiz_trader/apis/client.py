import os
import json
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

import requests

# Setup module-level logger with a default handler if none exists.
logger = logging.getLogger(__name__)
if not logger.handlers:
  handler = logging.StreamHandler()
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  handler.setFormatter(formatter)
  logger.addHandler(handler)

class WizzerClient:
  """
  A Python SDK for connecting to the Wizzer's REST API.

  Attributes:
    base_url (str): Base URL of the Wizzer's API server.
    token (str): JWT token for authentication.
    log_level (str): Logging level. Options: "error", "info", "debug".
    strategy_id (str): Default strategy ID to use if not provided in methods.
  """
  
  # Constants
  # Transaction types
  TRANSACTION_TYPE_BUY = "BUY"
  TRANSACTION_TYPE_SELL = "SELL"

  # Product types
  PRODUCT_CNC = "CNC"         # Cash and Carry
  PRODUCT_MIS = "MIS"         # Margin Intraday Square-off
  PRODUCT_NRML = "NRML"       # Normal / Overnight Futures and Options

  # Order types
  ORDER_TYPE_MARKET = "MARKET"
  ORDER_TYPE_LIMIT = "LIMIT"
  ORDER_TYPE_SL = "STOPLIMIT"        # Stop Loss
  ORDER_TYPE_SLM = "STOPMARKET"      # Stop Loss Market

  # Validity types
  VALIDITY_DAY = "DAY"
  VALIDITY_IOC = "IOC"        # Immediate or Cancel
  VALIDITY_GTT = "GTT"        # Good Till Triggered

  # Variety types
  VARIETY_REGULAR = "REGULAR"
  VARIETY_AMO = "AMO"         # After Market Order
  VARIETY_BO = "BO"           # Bracket Order
  VARIETY_CO = "CO"           # Cover Order

  # Exchanges
  EXCHANGE_NSE = "NSE"        # National Stock Exchange
  EXCHANGE_BSE = "BSE"        # Bombay Stock Exchange
  EXCHANGE_WZR = "WZR"        # Wizzer Exchange (for baskets)

  # Segments
  SEGMENT_NSE_CM = "NSECM"    # NSE Cash Market
  SEGMENT_BSE_CM = "BSECM"    # BSE Cash Market
  SEGMENT_NSE_FO = "NSEFO"    # NSE Futures and Options
  SEGMENT_WZREQ = "WZREQ"     # Wizzer Basket Segment
  
  # Order status constants
  ORDER_STATUS_OPEN = "OPEN"
  ORDER_STATUS_CANCELLED = "CANCELLED" 
  ORDER_STATUS_REJECTED = "REJECTED"
  ORDER_STATUS_PENDING = "PENDING"
  ORDER_STATUS_COMPLETED = "COMPLETED"

  # Trading mode constants
  TRADING_MODE_PAPER = "paper_trading"
  TRADING_MODE_ADVICES = "advices"
  TRADING_MODE_TRADING_AND_ADVICES = "trading_and_advices"
  
  # Rebalance execution policies
  REBALANCE_FULL = "full_rebalance"
  REBALANCE_ENTRY_ONLY = "entry_only"
  REBALANCE_EXIT_ONLY = "exit_only"
  
  # Add constants for option types and moneyness
  OPTION_TYPE_CE = "CE"
  OPTION_TYPE_PE = "PE"

  MONEYNESS_ATM = "ATM"
  MONEYNESS_ITM = "ITM" 
  MONEYNESS_OTM = "OTM"
  
  # Expiry preference constants
  EXPIRY_CURRENT_WEEKLY = "current_weekly"
  EXPIRY_NEAR_MONTH = "near_month"
  EXPIRY_MID_MONTH = "mid_month"
  EXPIRY_FAR_MONTH = "far_month"
  EXPIRY_FIRST_WEEKLY = "first_weekly"
  EXPIRY_SECOND_WEEKLY = "second_weekly"
  EXPIRY_THIRD_WEEKLY = "third_weekly"
  EXPIRY_FOURTH_WEEKLY = "fourth_weekly"
  EXPIRY_FIFTH_WEEKLY = "fifth_weekly"
  EXPIRY_FIRST_WEEKLY_MID_MONTH = "first_weekly_mid_month"
  EXPIRY_SECOND_WEEKLY_MID_MONTH = "second_weekly_mid_month"
  EXPIRY_THIRD_WEEKLY_MID_MONTH = "third_weekly_mid_month"
  EXPIRY_FOURTH_WEEKLY_MID_MONTH = "fourth_weekly_mid_month"
  EXPIRY_FIFTH_WEEKLY_MID_MONTH = "fifth_weekly_mid_month"
  EXPIRY_FIRST_WEEKLY_FAR_MONTH = "first_weekly_far_month"
  EXPIRY_SECOND_WEEKLY_FAR_MONTH = "second_weekly_far_month"
  EXPIRY_THIRD_WEEKLY_FAR_MONTH = "third_weekly_far_month"
  EXPIRY_FOURTH_WEEKLY_FAR_MONTH = "fourth_weekly_far_month"
  EXPIRY_FIFTH_WEEKLY_FAR_MONTH = "fifth_weekly_far_month"
  EXPIRY_FIRST_QUARTER = "first_quarter"
  EXPIRY_SECOND_QUARTER = "second_quarter"
  EXPIRY_THIRD_QUARTER = "third_quarter"
  EXPIRY_FOURTH_QUARTER = "fourth_quarter"
  EXPIRY_FIRST_HALF = "first_half_yearly"
  EXPIRY_SECOND_HALF = "second_half_yearly"
  EXPIRY_FIRST_QUARTER_PLUS_1 = "first_quarter_plus_1"
  EXPIRY_SECOND_QUARTER_PLUS_1 = "second_quarter_plus_1"
  EXPIRY_THIRD_QUARTER_PLUS_1 = "third_quarter_plus_1"
  EXPIRY_FOURTH_QUARTER_PLUS_1 = "fourth_quarter_plus_1"
  EXPIRY_FIRST_HALF_PLUS_1 = "first_half_yearly_plus_1"
  EXPIRY_SECOND_HALF_PLUS_1 = "second_half_yearly_plus_1"
  EXPIRY_FIRST_QUARTER_PLUS_2 = "first_quarter_plus_2"
  EXPIRY_SECOND_QUARTER_PLUS_2 = "second_quarter_plus_2"
  EXPIRY_THIRD_QUARTER_PLUS_2 = "third_quarter_plus_2"
  EXPIRY_FOURTH_QUARTER_PLUS_2 = "fourth_quarter_plus_2"
  EXPIRY_FIRST_HALF_PLUS_2 = "first_half_yearly_plus_2"
  EXPIRY_SECOND_HALF_PLUS_2 = "second_half_yearly_plus_2"
  EXPIRY_FIRST_QUARTER_PLUS_3 = "first_quarter_plus_3"
  EXPIRY_SECOND_QUARTER_PLUS_3 = "second_quarter_plus_3"
  EXPIRY_THIRD_QUARTER_PLUS_3 = "third_quarter_plus_3"
  EXPIRY_FOURTH_QUARTER_PLUS_3 = "fourth_quarter_plus_3"
  EXPIRY_FIRST_HALF_PLUS_3 = "first_half_yearly_plus_3"
  EXPIRY_SECOND_HALF_PLUS_3 = "second_half_yearly_plus_3"
  EXPIRY_FIRST_QUARTER_PLUS_4 = "first_quarter_plus_4"
  EXPIRY_SECOND_QUARTER_PLUS_4 = "second_quarter_plus_4"
  EXPIRY_THIRD_QUARTER_PLUS_4 = "third_quarter_plus_4"
  EXPIRY_FOURTH_QUARTER_PLUS_4 = "fourth_quarter_plus_4"
  EXPIRY_FIRST_HALF_PLUS_4 = "first_half_yearly_plus_4"
  EXPIRY_SECOND_HALF_PLUS_4 = "second_half_yearly_plus_4"
  
  # Historical data interval constants
  INTERVAL_1_MINUTE = "1m"
  INTERVAL_2_MINUTES = "2m"
  INTERVAL_3_MINUTES = "3m"
  INTERVAL_5_MINUTES = "5m"
  INTERVAL_10_MINUTES = "10m"
  INTERVAL_15_MINUTES = "15m"
  INTERVAL_30_MINUTES = "30m"
  INTERVAL_45_MINUTES = "45m"
  INTERVAL_1_HOUR = "1h"
  INTERVAL_1_DAY = "1d"
  INTERVAL_1_MONTH = "1M"
  
  # Constants for weightage schemes
  WEIGHTAGE_SCHEME_EQUI_WEIGHTED = "equi_weighted"
  WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED = "quantity_weighted"
  WEIGHTAGE_SCHEME_PRICE_WEIGHTED = "price_weighted"
  WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED = "market_cap_weighted"
  WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED = "float_adjusted_market_cap_weighted"
  WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED = "fundamental_weighted"
  WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED = "custom_weighted"

  # URIs to various API endpoints
  _routes = {
    # Order related endpoints
    "order.place": "/orders",
    "order.get": "/orders",
    "order.modify": "/orders/{order_id}",
    "order.cancel": "/orders/{order_id}",
    "order.info": "/orders/{order_id}",
    
    # Basket order endpoints
    "basket.order.place": "/orders/basket",
    "basket.order.exit": "/orders/basket/exit",
    "basket.order.modify": "/orders/basket/{order_id}",
    
    # Portfolio and position management
    "portfolio.positions": "/portfolios/positions",
    "portfolio.positions.exit.all": "/portfolios/positions/exit/all",
    "portfolio.positions.exit.strategy": "/portfolios/positions/exit/strategies/{strategy_id}",
    "portfolio.holdings": "/portfolios/holdings",
    
    # Basket management
    "basket.create": "/baskets",
    "basket.list": "/baskets",
    "basket.info": "/baskets/{basket_id}",
    "basket.instruments": "/baskets/{basket_id}/instruments",
    "basket.rebalance": "/baskets/rebalance",
    
    # Data hub endpoints
    "datahub.indices": "/datahub/indices",
    "datahub.index.components": "/datahub/index/components",
    "datahub.historical.ohlcv": "/datahub/historical/ohlcv",
    
    # Instrument & asset class endpoints
    "instrument.metrics": "/instruments/metrics",
    "instrument.option_chain": "/instruments/options/chain",
    "instrument.expiry_list": "/instruments/options/chain/expirylist",
    "instrument.future_list": "/instruments/futures/list",

    # Classification API endpoints
    "classification.types": "/datahub/classifications/types",
    "classification.values": "/datahub/classifications/{type}",
    "indices.filter": "/datahub/indices/filter",
    "instruments.filter": "/datahub/instruments/filter",
    "instruments.filter_with_index": "/datahub/indices/{id}/instruments"
  }
  
  def __init__(
    self,
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    strategy_id: Optional[str] = None,
    log_level: str = "error"  # default only errors
  ):
    # Configure logger based on log_level.
    valid_levels = {"error": logging.ERROR, "info": logging.INFO, "debug": logging.DEBUG}
    if log_level not in valid_levels:
      raise ValueError(f"log_level must be one of {list(valid_levels.keys())}")
    logger.setLevel(valid_levels[log_level])

    self.log_level = log_level
    # System env vars take precedence over .env
    self.base_url = base_url or os.environ.get("WZ__API_BASE_URL")
    self.token = token or os.environ.get("WZ__TOKEN")
    self.strategy_id = strategy_id or os.environ.get("WZ__STRATEGY_ID")
    
    if not self.token:
      raise ValueError("JWT token must be provided as an argument or in .env (WZ__TOKEN)")
    if not self.base_url:
      raise ValueError("Base URL must be provided as an argument or in .env (WZ__API_BASE_URL)")

    # Prepare the authorization header
    self.headers = {
      "Authorization": f"Bearer {self.token}",
      "Content-Type": "application/json"
    }

    logger.debug("Initialized WizzerClient with URL: %s", self.base_url)

  def _get_strategy(self, strategy: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Get strategy information, either from the provided parameter or from the default.
    
    Args:
      strategy (Optional[Dict[str, str]]): Strategy object with id, identifier, and name.
    
    Returns:
      Dict[str, str]: A strategy object with at least the id field.
        
    Raises:
      ValueError: If no strategy is provided and no default is set.
    """
    if strategy and "id" in strategy:
      return strategy
    
    if not self.strategy_id:
      raise ValueError("Strategy ID must be provided either as a parameter or set in .env (WZ__STRATEGY_ID)")
    
    return {"id": self.strategy_id}

  def _validate_datetime_format(self, datetime_str: str, interval: str) -> bool:
    """
    Validate datetime format based on interval type.
    
    Args:
      datetime_str (str): The datetime string to validate
      interval (str): The interval type
    
    Returns:
      bool: True if format is valid for the interval
    """
    # For daily and monthly intervals, only date is required
    if interval in [self.INTERVAL_1_DAY, self.INTERVAL_1_MONTH]:
      try:
        datetime.strptime(datetime_str, "%Y-%m-%d")
        return True
      except ValueError:
        return False
    
    # For intraday intervals, datetime is required
    else:
      try:
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return True
      except ValueError:
        return False
  
  # ===== DATA HUB METHODS =====

  def get_indices(self, trading_symbol: Optional[str] = None, exchange: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of indices available on the exchange.

    Args:
      trading_symbol (Optional[str]): Filter by specific index symbol.
      exchange (Optional[str]): Filter by specific exchange (NSE, BSE).

    Returns:
      List[Dict[str, Any]]: List of index information.
    """
    params = {}
    
    if trading_symbol:
      params["tradingSymbol"] = trading_symbol
    if exchange:
      params["exchange"] = exchange

    logger.debug("Fetching indices with params: %s", params)
    response = self._make_request("GET", self._routes["datahub.indices"], params=params)
    return response

  def get_index_components(self, trading_symbol: str, exchange: str) -> List[Dict[str, Any]]:
    """
    Get list of components (stocks) for a specific index.

    Args:
      trading_symbol (str): Index symbol (e.g., "NIFTY 50").
      exchange (str): Exchange name (NSE, BSE).

    Returns:
       List[Dict[str, Any]]: List of component stocks in the index.
    """
    params = {
      "tradingSymbol": trading_symbol,
      "exchange": exchange
    }

    logger.debug("Fetching index components with params: %s", params)
    response = self._make_request("GET", self._routes["datahub.index.components"], params=params)
    return response
  
  def get_historical_ohlcv(
    self, 
    instruments: List[str], 
    start_date: str, 
    end_date: str, 
    ohlcv: List[str],
    interval: str = "1d",
    continuous: bool = False
  ) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data for specified instruments.

    Args:
      instruments (List[str]): List of instrument identifiers (e.g., ["NSE:SBIN:3045"]).
      start_date (str): Start date. For daily/monthly intervals: YYYY-MM-DD format.
                       For intraday intervals: YYYY-MM-DD HH:MM:SS format.
      end_date (str): End date. For daily/monthly intervals: YYYY-MM-DD format.
                     For intraday intervals: YYYY-MM-DD HH:MM:SS format.
      ohlcv (List[str]): List of OHLCV fields to retrieve. 
        Valid values: "open", "high", "low", "close", "volume", "oi" (open interest - F&O only).
      interval (str, optional): Data interval. Options:
        - Intraday: "1m", "2m", "3m", "5m", "10m", "15m", "30m", "45m", "1h"
        - Daily: "1d" (default)
        - Monthly: "1M" (last trading day of month)
        
        Use constants like client.INTERVAL_5_MINUTES, client.INTERVAL_1_DAY, etc.
      continuous (bool, optional): Only relevant for futures. If True, returns continuous data across 
        multiple contract months to form a seamless data stream. Defaults to False.

    Returns:
      List[Dict[str, Any]]: Historical data for requested instruments.
      
      Note:
      - For daily/monthly intervals, the 'date' field contains YYYY-MM-DD.
      - For intraday intervals, the 'date' field contains YYYY-MM-DD HH:MM:SS.
      - The "oi" (open interest) field is only applicable for F&O instruments
      - The "continuous" parameter is only relevant for futures instruments and allows you to get
        backdated data across multiple contract months for a seamless time series

    Raises:
      ValueError: If datetime format doesn't match the interval requirements.
    """
    # Validate datetime formats
    if not self._validate_datetime_format(start_date, interval):
      if interval in [self.INTERVAL_1_DAY, self.INTERVAL_1_MONTH]:
        raise ValueError(f"For interval '{interval}', start_date must be in YYYY-MM-DD format")
      else:
        raise ValueError(f"For interval '{interval}', start_date must be in YYYY-MM-DD HH:MM:SS format")
    
    if not self._validate_datetime_format(end_date, interval):
      if interval in [self.INTERVAL_1_DAY, self.INTERVAL_1_MONTH]:
        raise ValueError(f"For interval '{interval}', end_date must be in YYYY-MM-DD format")
      else:
        raise ValueError(f"For interval '{interval}', end_date must be in YYYY-MM-DD HH:MM:SS format")

    endpoint = self._routes["datahub.historical.ohlcv"]
    data = {
      "instruments": instruments,
      "startDate": start_date,
      "endDate": end_date,
      "ohlcv": ohlcv,
      "interval": interval
    }
    
    # Add continuous parameter if specified
    if continuous:
      data["continuous"] = continuous

    logger.debug("Fetching historical OHLCV with data: %s", data)
    response = self._make_request("POST", endpoint, json=data)
    return response

  # ===== ORDER MANAGEMENT METHODS =====

  def place_order(
    self,
    exchange: str,
    trading_symbol: str,
    transaction_type: str,
    quantity: int,
    order_type: str = None,
    product: str = None,
    price: float = 0,
    trigger_price: float = 0,
    disclosed_qty: int = 0,
    validity: str = None,
    variety: str = None,
    stoploss: float = 0,
    target: float = 0,
    exchange_token: Optional[int] = None,
    broker: str = None,
    strategy: Optional[Dict[str, str]] = None
  ) -> Dict[str, Any]:
    """
    Place a regular order.
    
    Args:
      exchange (str): Exchange code (e.g., "NSE", "BSE").
      trading_symbol (str): Symbol of the instrument.
      transaction_type (str): "BUY" or "SELL".
      quantity (int): Number of shares to trade.
      order_type (str, optional): Order type (e.g., "MARKET", "LIMIT"). Defaults to MARKET.
      product (str, optional): Product code (e.g., "CNC" for delivery). Defaults to CNC.
      price (float, optional): Price for limit orders. Defaults to 0.
      trigger_price (float, optional): Trigger price for stop orders. Defaults to 0.
      disclosed_qty (int, optional): Disclosed quantity. Defaults to 0.
      validity (str, optional): Order validity (e.g., "DAY", "IOC"). Defaults to DAY.
      variety (str, optional): Order variety. Defaults to REGULAR.
      stoploss (float, optional): Stop loss price. Defaults to 0.
      target (float, optional): Target price. Defaults to 0.
      segment (Optional[str], optional): Market segment. If None, determined from exchange.
      exchange_token (Optional[int], optional): Exchange token for the instrument.
      broker (str, optional): Broker code.
      strategy (Optional[Dict[str, str]], optional): Strategy information. If None, uses default.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["order.place"]
    
    # Set default values from constants if not provided
    if order_type is None:
      order_type = self.ORDER_TYPE_MARKET
    if product is None:
      product = self.PRODUCT_CNC
    if validity is None:
      validity = self.VALIDITY_DAY
    if variety is None:
      variety = self.VARIETY_REGULAR
    
    # Get strategy information
    strategy_info = self._get_strategy(strategy)
    
    data = {
      "exchange": exchange,
      "tradingSymbol": trading_symbol,
      "transactionType": transaction_type,
      "qty": quantity,
      "orderType": order_type,
      "product": product,
      "price": price,
      "triggerPrice": trigger_price,
      "disclosedQty": disclosed_qty,
      "validity": validity,
      "variety": variety,
      "stoploss": stoploss,
      "target": target,
      "strategy": strategy_info
    }
    
    # Add exchange token if provided
    if exchange_token:
      data["exchangeToken"] = exchange_token
        
    logger.debug("Placing order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def modify_order(
    self,
    order_id: str,
    **params
  ) -> Dict[str, Any]:
    """
    Modify an existing order.
    
    Args:
      order_id (str): Order ID to modify.
      **params: Parameters to update in the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["order.modify"].format(order_id=order_id)
    
    logger.debug("Modifying order %s with params: %s", order_id, params)
    return self._make_request("PATCH", endpoint, json=params)
    
  def cancel_order(self, order_id: str) -> Dict[str, Any]:
    """
    Cancel an existing order.
    
    Args:
      order_id (str): Order ID to cancel.
        
    Returns:
      Dict[str, Any]: Response with the cancelled order ID.
    """
    endpoint = self._routes["order.cancel"].format(order_id=order_id)
    
    logger.debug("Cancelling order: %s", order_id)
    return self._make_request("DELETE", endpoint)

  def get_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      page_no: int = 1,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
              Valid values: "paper_trading", "advices", "trading_and_advices".
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
              Valid values: "OPEN", "CANCELLED", "REJECTED", "PENDING", "COMPLETED".
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format. Defaults to today.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format. Defaults to today.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          page_no (int, optional): Page number for pagination. Defaults to 1.
          paginate (bool, optional): Whether to automatically fetch all pages. Defaults to False.
              
      Returns:
          List[Dict[str, Any]]: List of orders matching the filter criteria.
      """
      endpoint = self._routes["order.get"]
      
      # Build the base parameters without list items
      params = {}
      
      # Handle single parameters
      if from_date:
          params["fromDateRange"] = from_date
      
      if to_date:
          params["toDateRange"] = to_date
      
      if not paginate:
          params["pageNo"] = page_no
      
      # Validate trading modes
      if trading_modes:
          for mode in trading_modes:
              if mode not in [self.TRADING_MODE_PAPER, self.TRADING_MODE_ADVICES, self.TRADING_MODE_TRADING_AND_ADVICES]:
                  raise ValueError(f"Invalid trading mode: {mode}")
      
      # Validate order statuses
      if order_statuses:
          for status in order_statuses:
              if status not in [self.ORDER_STATUS_OPEN, self.ORDER_STATUS_CANCELLED, 
                              self.ORDER_STATUS_REJECTED, self.ORDER_STATUS_PENDING, 
                              self.ORDER_STATUS_COMPLETED]:
                  raise ValueError(f"Invalid order status: {status}")
      
      # Handle pagination with properly formatted parameters
      if paginate:
          return self._paginate_orders(endpoint, params, trading_modes, order_statuses, trading_symbols)
      else:
          logger.debug("Fetching orders with params: %s", params)
          return self._make_request_with_multi_params(
              "GET", 
              endpoint, 
              params=params,
              trading_modes=trading_modes,
              order_statuses=order_statuses, 
              trading_symbols=trading_symbols
          )

  def _make_request_with_multi_params(
      self, 
      method: str, 
      endpoint: str, 
      params: Dict[str, Any],
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      trading_symbols: Optional[List[str]] = None
  ) -> Any:
      """
      Make an HTTP request with multiple parameters having the same name.
      
      Args:
          method (str): HTTP method (GET, POST, etc.)
          endpoint (str): API endpoint path.
          params (Dict[str, Any]): Base query parameters.
          trading_modes (Optional[List[str]]): List of trading modes.
          order_statuses (Optional[List[str]]): List of order statuses.
          trading_symbols (Optional[List[str]]): List of trading symbols.
          
      Returns:
          Any: Parsed JSON response.
      """
      url = f"{self.base_url}{endpoint}"
      
      # Start with the base parameters
      all_params = params.copy()
      
      # Create a session to manually handle parameter encoding
      session = requests.Session()
      req = requests.Request(method, url, headers=self.headers, params=all_params)
      prepped = req.prepare()
      
      # Build the URL with additional repeated parameters
      query_parts = []
      if prepped.url.find('?') >= 0:
          query_parts.append(prepped.url.split('?', 1)[1])
      
      # Add repeated parameters
      if trading_modes:
          for mode in trading_modes:
              query_parts.append(f"tradingMode={mode}")
      
      if order_statuses:
          for status in order_statuses:
              query_parts.append(f"orderStatus={status}")
      
      if trading_symbols:
          for symbol in trading_symbols:
              query_parts.append(f"tradingSymbols={symbol}")
      
      # Build the final URL
      final_url = prepped.url.split('?')[0]
      if query_parts:
          final_url += '?' + '&'.join(query_parts)
      
      try:
          logger.debug("%s request to %s", method, final_url)
          response = session.send(prepped)
          response.url = final_url
          response.raise_for_status()
          return response.json()
      except requests.RequestException as e:
          logger.error("API request failed: %s", e, exc_info=True)
          if hasattr(e.response, 'text'):
              logger.error("Response content: %s", e.response.text)
          raise

  def _paginate_orders(
      self, 
      endpoint: str, 
      params: Dict[str, Any],
      trading_modes: Optional[List[str]] = None,
      order_statuses: Optional[List[str]] = None,
      trading_symbols: Optional[List[str]] = None
  ) -> List[Dict[str, Any]]:
      """
      Internal method to handle pagination for orders API with multi-value parameters.
      
      Args:
          endpoint (str): API endpoint.
          params (Dict[str, Any]): Base query parameters.
          trading_modes (Optional[List[str]]): List of trading modes.
          order_statuses (Optional[List[str]]): List of order statuses.
          trading_symbols (Optional[List[str]]): List of trading symbols.
          
      Returns:
          List[Dict[str, Any]]: Combined results from all pages.
      """
      all_orders = []
      page_no = 1
      total_count = None
      page_size = 50  # API returns 50 orders per page
      
      while True:
          current_params = params.copy()
          current_params["pageNo"] = page_no
          logger.debug("Fetching orders page %d", page_no)
          
          # Build the URL with the session to get the properly formatted parameters
          session = requests.Session()
          req = requests.Request("GET", f"{self.base_url}{endpoint}", headers=self.headers, params=current_params)
          prepped = req.prepare()
          
          # Build the URL with additional repeated parameters
          query_parts = []
          if prepped.url.find('?') >= 0:
              query_parts.append(prepped.url.split('?', 1)[1])
          
          # Add repeated parameters
          if trading_modes:
              for mode in trading_modes:
                  query_parts.append(f"tradingMode={mode}")
          
          if order_statuses:
              for status in order_statuses:
                  query_parts.append(f"orderStatus={status}")
          
          if trading_symbols:
              for symbol in trading_symbols:
                  query_parts.append(f"tradingSymbols={symbol}")
          
          # Build the final URL
          final_url = prepped.url.split('?')[0]
          if query_parts:
              final_url += '?' + '&'.join(query_parts)
          
          # Make the request
          try:
              logger.debug("GET request to %s", final_url)
              prepped.url = final_url
              response = session.send(prepped)
              response.raise_for_status()
              
              # Get orders from the current page
              orders = response.json()
              all_orders.extend(orders)
              
              # Check if we need to fetch more pages
              if total_count is None and "X-Total-Count" in response.headers:
                  try:
                      total_count = int(response.headers["X-Total-Count"])
                      logger.debug("Total orders count: %d", total_count)
                  except (ValueError, TypeError):
                      logger.warning("Could not parse X-Total-Count header")
                      break
              
              # If we've fetched all orders or there are no more pages, stop
              if not orders or len(all_orders) >= total_count or total_count is None:
                  break
              
              # Move to the next page
              page_no += 1
              
          except requests.RequestException as e:
              logger.error("API request failed during pagination: %s", e, exc_info=True)
              if hasattr(e.response, 'text'):
                  logger.error("Response content: %s", e.response.text)
              raise
      
      logger.info("Fetched %d orders in total", len(all_orders))
      return all_orders

  def get_open_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get open orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of open orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_OPEN],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_completed_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get completed orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of completed orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_COMPLETED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_pending_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get pending orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of pending orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_PENDING],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_cancelled_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get cancelled orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of cancelled orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_CANCELLED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_rejected_orders(
      self,
      trading_modes: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get rejected orders with optional filtering.
      
      Args:
          trading_modes (Optional[List[str]], optional): Filter by trading modes.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of rejected orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=trading_modes,
          order_statuses=[self.ORDER_STATUS_REJECTED],
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_paper_traded_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get paper traded orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of paper traded orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_PAPER],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_advised_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get advised orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of advised orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_ADVICES],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )

  def get_live_traded_orders(
      self,
      order_statuses: Optional[List[str]] = None,
      from_date: Optional[str] = None,
      to_date: Optional[str] = None,
      trading_symbols: Optional[List[str]] = None,
      paginate: bool = False
  ) -> List[Dict[str, Any]]:
      """
      Get live traded orders with optional filtering.
      
      Args:
          order_statuses (Optional[List[str]], optional): Filter by order statuses.
          from_date (Optional[str], optional): Start date in YYYY-MM-DD format.
          to_date (Optional[str], optional): End date in YYYY-MM-DD format.
          trading_symbols (Optional[List[str]], optional): Filter by trading symbols.
          paginate (bool, optional): Whether to automatically fetch all pages.
              
      Returns:
          List[Dict[str, Any]]: List of live traded orders matching the filter criteria.
      """
      return self.get_orders(
          trading_modes=[self.TRADING_MODE_TRADING_AND_ADVICES],
          order_statuses=order_statuses,
          from_date=from_date,
          to_date=to_date,
          trading_symbols=trading_symbols,
          paginate=paginate
      )
  
  def get_order(self, order_id: str) -> Dict[str, Any]:
    """
    Get details of a specific order by ID.
    
    Args:
      order_id (str): ID of the order to retrieve.
        
    Returns:
      Dict[str, Any]: Order details.
    """
    endpoint = self._routes["order.info"].format(order_id=order_id)
    
    logger.debug("Fetching order: %s", order_id)
    return self._make_request("GET", endpoint)
    
  def get_positions(self, position_status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get portfolio positions with optional filtering by status.
    
    Args:
      position_status (Optional[str], optional): Filter positions by status.
        Valid values: "open", "closed". If None, returns all positions.
        
    Returns:
      List[Dict[str, Any]]: List of positions matching the filter criteria.
    """
    endpoint = self._routes["portfolio.positions"]
    params = {}
    
    if position_status:
      if position_status not in ["open", "closed"]:
        raise ValueError("position_status must be either 'open', 'closed', or None")
      params["positionStatus"] = position_status
    
    logger.debug("Fetching positions with status: %s", position_status or "all")
    return self._make_request("GET", endpoint, params=params)
    
  def get_open_positions(self) -> List[Dict[str, Any]]:
    """
    Get all open positions in the portfolio.
    
    Returns:
      List[Dict[str, Any]]: List of open positions.
    """
    return self.get_positions(position_status="open")
    
  def get_closed_positions(self) -> List[Dict[str, Any]]:
    """
    Get all closed positions in the portfolio.
    
    Returns:
      List[Dict[str, Any]]: List of closed positions.
    """
    return self.get_positions(position_status="closed")
  
  def get_holdings(self, portfolios: Optional[str] = "default") -> List[Dict[str, Any]]:
    """
    Get current holdings.
    
    Args:
      portfolios (str, optional): Portfolio name. Defaults to "default".
        
    Returns:
      List[Dict[str, Any]]: List of holdings.
    """
    endpoint = self._routes["portfolio.holdings"]
    params = {"portfolios": portfolios}
    
    logger.debug("Fetching holdings for portfolio: %s", portfolios)
    return self._make_request("GET", endpoint, params=params)
    
  # ===== BASKET MANAGEMENT METHODS =====

  def create_basket(
    self,
    name: str,
    instruments: List[Dict[str, Any]],
    weightage_scheme: str = "equi_weighted",
    capital: Optional[Dict[str, float]] = None,
    instrument_types: Optional[List[str]] = None,
    trading_symbol: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Create a new basket.
    
    Args:
      name (str): Name of the basket.
      instruments (List[Dict[str, Any]]): List of instruments with weightage and shares.
      weightage_scheme (str, optional): Weightage scheme. Defaults to "equi_weighted".
      capital (Optional[Dict[str, float]], optional): Capital allocation. Defaults to {"minValue": 0, "actualValue": 0}.
      instrument_types (Optional[List[str]], optional): Types of instruments. Defaults to ["EQLC"].
        
    Returns:
      Dict[str, Any]: Basket information.
    """
    endpoint = self._routes["basket.create"]
    
    # Set defaults
    if capital is None:
      capital = {"minValue": 0, "actualValue": 0}
        
    data = {
      "name": name,
      "weightageScheme": weightage_scheme,
      "instruments": instruments,
      "capital": capital,
      "instrumentTypes": instrument_types
    }
    
    logger.debug("Creating basket: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def get_baskets(self) -> List[Dict[str, Any]]:
    """
    Get all baskets.
    
    Returns:
      List[Dict[str, Any]]: List of baskets.
    """
    endpoint = self._routes["basket.list"]
    
    logger.debug("Fetching baskets")
    return self._make_request("GET", endpoint)
    
  def get_basket(self, basket_id: str) -> Dict[str, Any]:
    """
    Get a specific basket by ID.
    
    Args:
      basket_id (str): Basket ID.
        
    Returns:
      Dict[str, Any]: Basket information.
    """
    endpoint = self._routes["basket.info"].format(basket_id=basket_id)
    
    logger.debug("Fetching basket: %s", basket_id)
    return self._make_request("GET", endpoint)
    
  def get_basket_instruments(self, basket_id: str) -> List[Dict[str, Any]]:
    """
    Get instruments in a basket.
    
    Args:
      basket_id (str): Basket ID.
        
    Returns:
      List[Dict[str, Any]]: List of instruments in the basket.
    """
    endpoint = self._routes["basket.instruments"].format(basket_id=basket_id)
    
    logger.debug("Fetching instruments for basket: %s", basket_id)
    return self._make_request("GET", endpoint)
    
  def place_basket_order(
    self,
    trading_symbol: str,
    transaction_type: str,
    quantity: float,
    price: float = 0,
    order_type: str = None,
    product: str = None,
    validity: str = None,
    exchange_token: Optional[int] = None,
    trigger_price: float = 0,
    stoploss: float = 0,
    target: float = 0,
    broker: str = "wizzer",
    variety: str = None,
    strategy: Optional[Dict[str, str]] = None,
    disclosed_qty: int = 0,
    sl_applied_level: Optional[str] = None
  ) -> Dict[str, Any]:
    """
    Place a basket order.
    
    Args:
      trading_symbol (str): Basket trading symbol (e.g., "/BASKET_NAME").
      transaction_type (str): "BUY" or "SELL".
      quantity (float): Quantity/units of the basket.
      price (float, optional): Price for limit orders. Defaults to 0.
      order_type (str, optional): Order type. Defaults to MARKET.
      product (str, optional): Product code. Defaults to CNC.
      validity (str, optional): Order validity. Defaults to DAY.
      exchange_token (Optional[int], optional): Exchange token for the basket.
      trigger_price (float, optional): Trigger price. Defaults to 0.
      stoploss (float, optional): Stop loss price. Defaults to 0.
      target (float, optional): Target price. Defaults to 0.
      broker (str, optional): Broker code. Defaults to "wizzer".
      variety (str, optional): Order variety. Defaults to REGULAR.
      strategy (Optional[Dict[str, str]], optional): Strategy information. If None, uses default.
      disclosed_qty (int, optional): Disclosed quantity. Defaults to 0.
      sl_applied_level (Optional[str], optional): Stop loss applied level (e.g., "basket").
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.place"]
    
    # Set default values from constants if not provided
    if order_type is None:
      order_type = self.ORDER_TYPE_MARKET
    if product is None:
      product = self.PRODUCT_CNC
    if validity is None:
      validity = self.VALIDITY_DAY
    if variety is None:
      variety = self.VARIETY_REGULAR
    
    # Get strategy information
    strategy_info = self._get_strategy(strategy)
    
    data = {
      "tradingSymbol": trading_symbol,
      "exchange": self.EXCHANGE_WZR,
      "transactionType": transaction_type,
      "qty": quantity,
      "price": price,
      "orderType": order_type,
      "product": product,
      "validity": validity,
      "triggerPrice": trigger_price,
      "stoploss": stoploss,
      "target": target,
      "broker": broker,
      "variety": variety,
      "strategy": strategy_info,
      "segment": self.SEGMENT_WZREQ,
      "disclosedQty": disclosed_qty
    }
    
    # Add exchange token if provided
    if exchange_token:
      data["exchangeToken"] = exchange_token
        
    # Add stop loss level if provided
    if sl_applied_level:
      data["slAppliedLevel"] = sl_applied_level
        
    logger.debug("Placing basket order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def place_basket_exit_order(
    self,
    trading_symbol: str,
    exchange: str,
    transaction_type: str,
    quantity: float,
    exchange_token: int,
    **kwargs
  ) -> Dict[str, Any]:
    """
    Place a basket exit order.
    
    Args:
      trading_symbol (str): Basket trading symbol.
      exchange (str): Exchange code (usually "WZR" for baskets).
      transaction_type (str): "BUY" or "SELL" (usually "SELL" for exit).
      quantity (float): Quantity/units of the basket.
      exchange_token (int): Exchange token for the basket.
      **kwargs: Additional parameters for the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.exit"]
    
    # Build base data
    data = {
      "tradingSymbol": trading_symbol,
      "exchange": exchange,
      "transactionType": transaction_type,
      "qty": quantity,
      "exchangeToken": exchange_token,
      **kwargs
    }
    
    # Set strategy if not in kwargs
    if "strategy" not in kwargs:
      data["strategy"] = self._get_strategy(None)
        
    # Set defaults if not in kwargs
    defaults = {
      "orderType": self.ORDER_TYPE_MARKET,
      "product": self.PRODUCT_CNC, 
      "validity": self.VALIDITY_DAY,
      "disclosedQty": 0,
      "price": 0,
      "variety": self.VARIETY_REGULAR,
      "stoploss": 0,
      "broker": "wizzer",
      "triggerPrice": 0,
      "target": 0,
      "segment": self.SEGMENT_WZREQ
    }
    
    for key, value in defaults.items():
      if key not in data:
        data[key] = value
    
    logger.debug("Placing basket exit order: %s", data)
    return self._make_request("POST", endpoint, json=data)
    
  def modify_basket_order(
    self,
    order_id: str,
    **params
  ) -> Dict[str, Any]:
    """
    Modify an existing basket order.
    
    Args:
      order_id (str): Order ID to modify.
      **params: Parameters to update in the order.
        
    Returns:
      Dict[str, Any]: Order response containing orderId.
    """
    endpoint = self._routes["basket.order.modify"].format(order_id=order_id)
    
    logger.debug("Modifying basket order %s with params: %s", order_id, params)
    return self._make_request("PATCH", endpoint, json=params)
    
  def rebalance_basket(
        self,
        trading_symbol: str,
        instruments: List[str],
        execution_policy: str,
        order_type: str = None,
        product: str = None,
        weightage_scheme: str = None
    ) -> Dict[str, Any]:
        """
        Rebalance a basket with new instruments.
        
        Args:
          trading_symbol (str): Basket trading symbol.
          instruments (List[str]): List of instrument identifiers for the new basket composition.
          execution_policy (str): Rebalance execution policy.
              Options: REBALANCE_FULL, REBALANCE_ENTRY_ONLY, REBALANCE_EXIT_ONLY.
          order_type (str, optional): Order type to use for rebalance orders.
              Options: ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT
          product (str, optional): Product type to use for rebalance orders.
              Options: PRODUCT_CNC, PRODUCT_MIS
          weightage_scheme (str, optional): Weightage scheme for rebalancing. Options:
              WEIGHTAGE_SCHEME_EQUI_WEIGHTED, WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED, 
              WEIGHTAGE_SCHEME_PRICE_WEIGHTED, WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED,
              WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED, 
              WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED, WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED
            
        Returns:
          Dict[str, Any]: Rebalance response.
        """
        endpoint = self._routes["basket.rebalance"]
        
        # Validate execution policy
        valid_execution_policies = [self.REBALANCE_FULL, self.REBALANCE_ENTRY_ONLY, self.REBALANCE_EXIT_ONLY]
        if execution_policy not in valid_execution_policies:
            raise ValueError(f"execution_policy must be one of {valid_execution_policies}")
          
        # Validate weightage scheme if provided
        if weightage_scheme:
            valid_weightage_schemes = [
                self.WEIGHTAGE_SCHEME_EQUI_WEIGHTED, 
                self.WEIGHTAGE_SCHEME_QUANTITY_WEIGHTED,
                self.WEIGHTAGE_SCHEME_PRICE_WEIGHTED, 
                self.WEIGHTAGE_SCHEME_MARKET_CAP_WEIGHTED,
                self.WEIGHTAGE_SCHEME_FLOAT_ADJUSTED_MARKET_CAP_WEIGHTED,
                self.WEIGHTAGE_SCHEME_FUNDAMENTAL_WEIGHTED, 
                self.WEIGHTAGE_SCHEME_CUSTOM_WEIGHTED
            ]
            if weightage_scheme not in valid_weightage_schemes:
                raise ValueError(f"weightage_scheme must be one of {valid_weightage_schemes}")
        
        # Build the basic request payload
        data = {
            "tradingSymbol": trading_symbol,
            "instruments": instruments,
            "policies": {
                "execution": execution_policy
            }
        }
        
        # Add order policies if specified
        if order_type or product:
            order_policies = {}
            
            if order_type:
                valid_order_types = [self.ORDER_TYPE_MARKET, self.ORDER_TYPE_LIMIT]
                if order_type not in valid_order_types:
                    raise ValueError(f"order_type must be one of {valid_order_types}")
                order_policies["orderType"] = order_type
                
            if product:
                valid_products = [self.PRODUCT_CNC, self.PRODUCT_MIS, self.PRODUCT_NRML]
                if product not in valid_products:
                    raise ValueError(f"product must be one of {valid_products}")
                order_policies["product"] = product
            
            if order_policies:
                data["policies"]["orders"] = order_policies
                
        # Add weightage scheme if specified
        if weightage_scheme:
            data["policies"]["weightageScheme"] = weightage_scheme
        
        logger.debug("Rebalancing basket %s with instruments: %s, policy: %s, order settings: %s", 
                    trading_symbol, instruments, execution_policy, 
                    {"order_type": order_type, "product": product, "weightage_scheme": weightage_scheme})
        
        return self._make_request("POST", endpoint, json=data)
    
  def exit_all_positions(self) -> Dict[str, Any]:
    """
    Exit all positions across all strategies.
    
    This method sends a request to close all open positions for the user.
    
    Returns:
      Dict[str, Any]: Response with summary of success and failure counts.
    """
    endpoint = self._routes["portfolio.positions.exit.all"]
    
    data = {}
    
    logger.debug("Exiting all positions")
    return self._make_request("POST", endpoint, json=data)
    
  def exit_strategy_positions(self, strategy_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Exit all positions for a specific strategy.
    
    Args:
      strategy_id (Optional[str]): ID of the strategy to exit positions for.
        If None, uses the default strategy ID.
        
    Returns:
      Dict[str, Any]: Response with summary of success and failure counts.
      
    Raises:
      ValueError: If no strategy_id is provided and no default is set.
    """
    # Get strategy ID (either from parameter or default)
    if not strategy_id:
      if not self.strategy_id:
        raise ValueError("Strategy ID must be provided either as a parameter or set in .env (WZ__STRATEGY_ID)")
      strategy_id = self.strategy_id
      
    endpoint = self._routes["portfolio.positions.exit.strategy"].format(strategy_id=strategy_id)
    
    data = {}
    
    logger.debug("Exiting all positions for strategy: %s", strategy_id)
    return self._make_request("POST", endpoint, json=data)

  # =====INSTRUMENT & ASSET CLASS METHODS =====
  
  def get_instrument_metrics(self, identifiers: List[str]) -> List[Dict[str, Any]]:
    """
    Get detailed metrics for instruments by their identifiers.
    
    Args:
        identifiers (List[str]): List of instrument identifiers in the format
                                "EXCHANGE:SYMBOL:TOKEN" (e.g., "NSE:SBIN:3045").
        
    Returns:
        List[Dict[str, Any]]: List of instrument metrics.
    
    Example:
        >>> client.get_instrument_metrics([
        ...     "NSE:SBIN:3045", 
        ...     "NSE:RELIANCE:2885",
        ...     "NSE:NIFTY26DEC11000CE:61009"
        ... ])
    """
    endpoint = self._routes["instrument.metrics"]
    data = {
        "identifiers": identifiers
    }
    
    logger.debug("Fetching instrument metrics for identifiers: %s", identifiers)
    response = self._make_request("POST", endpoint, json=data)
    return response

  def get_option_chain(
      self,
      identifier: str,
      expiry_date: Optional[str] = None,
      expiry_preference: Optional[str] = None,
      option_type: List[str] = None,
      moneyness: List[str] = None
  ) -> Dict[str, Any]:
      """
      Get option chain for a specified instrument.
      
      Args:
          identifier (str): Instrument identifier (e.g., "NSE:SBIN:3045").
          expiry_date (str): Expiry date in YYYY-MM-DD format.
          expiry_preference (Optional[str]): Expiry category preference instead of exact date.
              Use the EXPIRY_* constants provided by the class.
          option_type (List[str]): List of option types to include. 
              Values from [OPTION_TYPE_CE, OPTION_TYPE_PE].
          moneyness (List[str]): List of moneyness types to include. 
              Values from [MONEYNESS_ATM, MONEYNESS_ITM, MONEYNESS_OTM].
      
      Returns:
          Dict[str, Any]: Option chain data including strikes.
          
      Raises:
          ValueError: If option_type or moneyness lists are empty.
      """
      endpoint = self._routes["instrument.option_chain"]
      
      # Validate option_type and moneyness parameters
      if not option_type:
          raise ValueError("At least one option type must be specified")
      if not moneyness:
          raise ValueError("At least one moneyness type must be specified")
      if not expiry_date and not expiry_preference:
        raise ValueError("Either expiry_date or expiry_preference must be provided")
      
      # Validate option_type values
      valid_option_types = [self.OPTION_TYPE_CE, self.OPTION_TYPE_PE]
      for opt_type in option_type:
          if opt_type not in valid_option_types:
              raise ValueError(f"Invalid option type: {opt_type}. Must be one of {valid_option_types}")
      
      # Validate moneyness values
      valid_moneyness = [self.MONEYNESS_ATM, self.MONEYNESS_ITM, self.MONEYNESS_OTM]
      for money in moneyness:
          if money not in valid_moneyness:
              raise ValueError(f"Invalid moneyness: {money}. Must be one of {valid_moneyness}")
      
      data = {
          "identifier": identifier,
          "optionType": option_type,
          "moneyness": moneyness
      }
      
      # Add either expiryDate or expiryPreference
      if expiry_date:
          data["expiryDate"] = expiry_date
      elif expiry_preference:
          data["expiryPreference"] = expiry_preference
      
      logger.debug("Fetching option chain with data: %s", data)
      return self._make_request("POST", endpoint, json=data)

  def get_option_expiry_list(
      self,
      identifier: str
  ) -> Dict[str, Any]:
      """
      Get a list of available expiry dates for an instrument's options.
      
      Args:
        identifier (str): Instrument identifier in the format "EXCHANGE:SYMBOL:TOKEN"
          (e.g., "NSE:SBIN:3045" or "NSE:NIFTY 50:26000").
          
      Returns:
        Dict[str, Any]: Response containing the list of available expiry dates with contract types.
        
      Example:
        ```python
        # Get expiry dates for a stock
        expiry_list = client.get_option_expiry_list("NSE:SBIN:3045")
        
        # Get expiry dates for an index
        nifty_expiry = client.get_option_expiry_list("NSE:NIFTY 50:26000")
        
        # Access the expiry dates
        for expiry in expiry_list.get('expiryList', []):
            print(f"{expiry['date']} - {expiry['contract']}")
        ```
      """
      endpoint = self._routes["instrument.expiry_list"]
      
      data = {
        "identifier": identifier
      }

      logger.debug("Fetching option expiry list for %s", identifier)
      return self._make_request("POST", endpoint, json=data)
    
  def get_futures_list(self, identifier: str) -> List[Dict[str, Any]]:
    """
    Get available futures contracts for an instrument.
    
    Args:
      identifier (str): Instrument identifier (e.g., "NSE:SBIN:3045" or "NSE:NIFTY 50:26000").
        
    Returns:
      List[Dict[str, Any]]: List of available futures contracts with expiry dates and contract types.
      
    Example:
      # Get futures for a stock
      sbin_futures = client.get_futures_list("NSE:SBIN:3045")
      for future in sbin_futures:
          print(f"{future['tradingSymbol']} - {future['expiry']} ({future['contract']})")
          
      # Get futures for an index
      nifty_futures = client.get_futures_list("NSE:NIFTY 50:26000")
    """
    endpoint = self._routes["instrument.future_list"]
    data = {"identifier": identifier}
    
    logger.debug("Fetching futures list for: %s", identifier)
    return self._make_request("POST", endpoint, json=data)


  def get_classification_types(self) -> list:
    """
    Retrieve all available classification types.
    
    Returns:
      list: A list of classification types.
    """
    endpoint = self._routes["classification.types"]
    logger.debug("Fetching classification types.")
    return self._make_request("GET", endpoint)

  def get_classifications(self, classification_type: str) -> list:
    """
    Retrieve all values for a specific classification type.
    
    Args:
      classification_type (str): The type of classification to retrieve values for.
      
    Returns:
      list: A list of classification values.
    """
    endpoint = self._routes["classification.values"].format(type=classification_type)
    logger.debug(f"Fetching classification values for type: {classification_type}")
    return self._make_request("GET", endpoint)

  def filter_indices(self, filters: Dict[str, List[str]], match_all: bool = True) -> list:
    """
    Filter indices based on multiple classification criteria.
    
    Args:
      filters (Dict[str, List[str]]): A dictionary of filters where keys are classification
                                      types and values are lists of classification values.
      match_all (bool): If True, performs an AND logic search. If False, performs an OR logic search.
      
    Returns:
      list: A list of indices that match the filter criteria.
    """
    endpoint = self._routes["indices.filter"]
    data = {
      "filters": filters,
      "matchAll": match_all
    }
    logger.debug(f"Filtering indices with filters: {filters} and match_all: {match_all}")
    return self._make_request("POST", endpoint, json=data)

  def filter_instruments(
    self,
    filters: Optional[Dict[str, List[str]]] = None,
    match_all: bool = True,
    index_identifier: Optional[str] = None
  ) -> list:
    """
    Filter instruments based on classification criteria, with an option to filter within an index.
    
    Args:
      filters (Optional[Dict[str, List[str]]]): A dictionary of filters where keys are classification
                                      types and values are lists of classification values. Can be None.
      match_all (bool): If True, performs an AND logic search. If False, performs an OR logic search.
      index_identifier (Optional[str]): If provided, filters instruments within a specific index.
      
    Returns:
      list: A list of instruments that match the filter criteria.
    """
    data = {
        "filters": filters or {},
        "matchAll": match_all
    }

    if index_identifier:
        endpoint = self._routes["instruments.filter_with_index"].format(id=index_identifier)
        logger.debug(f"Filtering instruments for index: {index_identifier} with filters: {filters} and match_all: {match_all}")
    else:
        endpoint = self._routes["instruments.filter"]
        logger.debug(f"Filtering instruments with filters: {filters} and match_all: {match_all}")
        
    return self._make_request("POST", endpoint, json=data)

  def _make_request(
    self, 
    method: str, 
    endpoint: str, 
    params: Optional[Dict[str, str]] = None, 
    json: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
  ) -> Any:
    """
    Make an HTTP request to the API.

    Args:
      method (str): HTTP method (GET, POST, etc.)
      endpoint (str): API endpoint path.
      params (Optional[Dict[str, str]]): Query parameters for GET requests.
      json (Optional[Dict[str, Any]]): JSON payload for POST requests.
      headers (Optional[Dict[str, str]]): Custom headers to override the defaults.

    Returns:
      Any: Parsed JSON response.

    Raises:
      requests.RequestException: If the request fails.
    """
    url = f"{self.base_url}{endpoint}"
    request_headers = headers if headers else self.headers
    
    try:
      logger.debug("%s request to %s", method, url)
      response = requests.request(
        method=method,
        url=url,
        headers=request_headers,
        params=params,
        json=json
      )
      response.raise_for_status()
      return response.json()
    except requests.RequestException as e:
      logger.error("API request failed: %s", e, exc_info=True)
      if hasattr(e.response, 'text'):
        logger.error("Response content: %s", e.response.text)
      raise
