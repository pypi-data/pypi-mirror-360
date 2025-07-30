import duckdb
from typing import Literal
import os
import numpy as np
from tqdm import tqdm
from duck_client.error import DBReadOnlyError, DBError
import pandas as pd
import datetime
from typing import Union


class DataBase:
    FREQ_MAP = {
        "1m": 1,
        "3m": 3,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "12h": 720,
        "1d": 1440,
    }

    BINANCE_ASSET_CLASS_MAP = {
        "spot": "spot",
        "um": "futures/um",
        # "cm": "/futures/cm", #NOTE: not supported yet
    }

    OKX_ASSET_CLASS_MAP = {
        "swap": "swap",
        # "spot": "spot",
    }

    MOMENTUM_WINDOW_MAP = {
        "1d": 7,
        "12h": 6,
        "4h": 6,
        "1h": 4,
        "30m": 4,
        "15m": 4,
        "3m": 5,
        "1m": 5,
    }

    VOLATILITY_WINDOW_MAP = {
        "1d": 14,
        "12h": 14,
        "4h": 18,
        "1h": 24,
        "30m": 12,
        "15m": 16,
        "3m": 20,
        "1m": 30,
    }

    BETA_WINDOW_MAP = {
        "1d": 90,
        "12h": 180,
        "4h": 180,
        "1h": 720,
        "30m": 1440,
        "15m": 2880,
        "3m": 7 * 24 * 20,
        "1m": 7 * 24 * 60,
    }

    def __init__(
        self,
        share_folder_path: str | None = None,
        db_path: str | None = None,
        read_only: bool = True,
    ):
        self._db_path = db_path
        self._share_folder_path = share_folder_path
        self._read_only = read_only
        if db_path:
            self.conn = duckdb.connect(database=db_path, read_only=read_only)
        else:
            self.conn = duckdb.connect()

    def _list_klines_symbols(
        self,
        asset_class: Literal["spot", "um", "swap"] = "um",
        exchange: Literal["binance", "okx"] = "binance",
    ):
        # query all symbols from klines table
        self._asset_class_check(asset_class, exchange)
        sql = f"""
        SELECT DISTINCT symbol FROM {exchange}_{asset_class}_klines_1m
        """
        return sorted(self.conn.query(sql).to_df()["symbol"].tolist())

    def list_all_symbols(
        self,
        asset_class: Literal["spot", "um", "swap"] = "um",
        data_type: Literal["klines"] = "klines",
        exchange: Literal["binance", "okx"] = "binance",
    ):
        if data_type == "klines":
            return self._list_klines_symbols(asset_class, exchange)

    def _read_only_check(self):
        if self._read_only:
            raise DBReadOnlyError(
                "Cannot create table in `read-only` mode, please set `read_only=False`"
            )

    def _exchange_asset_class_map(
        self, exchange: Literal["binance", "okx"] = "binance"
    ):
        match exchange:
            case "binance":
                return self.BINANCE_ASSET_CLASS_MAP
            case "okx":
                return self.OKX_ASSET_CLASS_MAP
            case _:
                raise DBError(
                    f"Invalid exchange: {exchange}. Must be one of: binance, okx"
                )

    def _asset_class_check(
        self,
        asset_class: Literal["spot", "um", "swap"],
        exchange: Literal["binance", "okx"] = "binance",
    ):
        asset_class_map = self._exchange_asset_class_map(exchange)

        if asset_class not in asset_class_map:
            raise DBError(
                f"Invalid asset class: {asset_class}. Must be one of: {', '.join(asset_class_map.keys())}"
            )

    def _freq_check(
        self, freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"]
    ):
        if freq not in self.FREQ_MAP:
            raise DBError(
                f"Invalid frequency: {freq}. Must be one of: {', '.join(self.FREQ_MAP.keys())}"
            )

    def _inclusive_check(self, inclusive: Literal["right", "left", "both", "neither"]):
        if inclusive not in ["right", "left", "both", "neither"]:
            raise DBError(
                f"Invalid inclusive value: {inclusive}. Must be one of: right, left, both, neither"
            )
        if inclusive == "right":
            right, left = ">=", "<"
        elif inclusive == "left":
            right, left = ">", "<="
        elif inclusive == "both":
            right, left = ">=", "<="
        else:
            right, left = ">", "<"
        return right, left

    def _create_binance_klines_table(
        self,
        asset_class: Literal["spot", "um"],
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"],
    ):
        self._read_only_check()
        self._asset_class_check(asset_class, exchange="binance")
        self._freq_check(freq)
        path = os.path.join(
            self._share_folder_path,
            "binance_data",
            self.BINANCE_ASSET_CLASS_MAP[asset_class],
        )
        if freq == "1m":
            sql = f"""
            CREATE OR REPLACE TABLE binance_{asset_class}_klines_{freq} AS
            SELECT DISTINCT
                SPLIT_PART(filename, '/', -3) as symbol,
                to_timestamp(timestamp / 1000) as timestamp,
                open,
                high,
                low,
                close,
                volume,
                quote_volume,
                taker_buy_volume,
                taker_buy_quote_volume
            FROM read_parquet(
                '{path}/*/klines/*/1m/*.parquet',
                FILENAME = true
            )
            """
        else:
            sql = f"""
            CREATE OR REPLACE TABLE binance_{asset_class}_klines_{freq} AS
            SELECT DISTINCT
                SPLIT_PART(filename, '/', -3) as symbol,
                time_bucket(INTERVAL {self.FREQ_MAP[freq]} minutes, to_timestamp(timestamp / 1000)) as timestamp,
                FIRST(open) as open,
                MAX(high) as high,
                MIN(low) as low,
                LAST(close) as close,
                SUM(volume) as volume,
                SUM(quote_volume) as quote_volume,
                SUM(taker_buy_volume) as taker_buy_volume,
                SUM(taker_buy_quote_volume) as taker_buy_quote_volume
            FROM read_parquet(
                '{path}/*/klines/*/1m/*.parquet',
                FILENAME = true
            )
            GROUP BY symbol, time_bucket(INTERVAL {self.FREQ_MAP[freq]} minutes, to_timestamp(timestamp / 1000))
            """
        self.conn.execute(sql)

    def _create_binance_factors_table(
        self,
        asset_class: Literal["spot", "um"],
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"],
    ):
        self._read_only_check()
        self._asset_class_check(asset_class, exchange="binance")
        self._freq_check(freq)

        m_window = self.MOMENTUM_WINDOW_MAP[freq]
        v_window = self.VOLATILITY_WINDOW_MAP[freq]
        b_window = self.BETA_WINDOW_MAP[freq]

        sql = f"""
        CREATE OR REPLACE TABLE binance_{asset_class}_factors_{freq} AS
        WITH base AS (
            SELECT 
                k.symbol,
                k.timestamp,
                k.close,
                k.close / LAG(k.close) OVER w_symbol - 1 AS return,
                btc.return AS btc_return
            FROM binance_{asset_class}_klines_{freq} k
            LEFT JOIN (
                SELECT 
                    timestamp,
                    close / LAG(close) OVER (ORDER BY timestamp) - 1 AS return
                FROM binance_{asset_class}_klines_{freq}
                WHERE symbol = 'BTCUSDT'
            ) btc USING (timestamp)
            WINDOW w_symbol AS (PARTITION BY k.symbol ORDER BY k.timestamp)
        ),
        factors AS (
            SELECT
                *,
                -- 合并窗口计算
                CASE WHEN ROW_NUMBER() OVER w_symbol >= {m_window} 
                    THEN PRODUCT(1 + return) OVER (w_symbol ROWS BETWEEN {m_window - 1} PRECEDING AND CURRENT ROW) - 1 
                    ELSE NULL END AS momentum,
                    
                CASE WHEN ROW_NUMBER() OVER w_symbol >= {v_window} 
                    THEN STDDEV(return) OVER (w_symbol ROWS BETWEEN {v_window - 1} PRECEDING AND CURRENT ROW) 
                    ELSE NULL END AS volatility,
                    
                CASE WHEN ROW_NUMBER() OVER w_symbol >= {b_window} 
                    THEN REGR_SLOPE(btc_return, return) OVER (w_symbol ROWS BETWEEN {b_window - 1} PRECEDING AND CURRENT ROW) 
                    ELSE NULL END AS beta
            FROM base
            WINDOW w_symbol AS (PARTITION BY symbol ORDER BY timestamp)
        )

        SELECT
            timestamp,
            symbol,
            close,
            return,
            momentum,
            volatility,
            beta
            FROM factors;
        """

        self.conn.execute(sql)

    def update_klines(self, exchange: Literal["binance", "okx"] = "binance"):
        klines_funcs = {
            "binance": self._create_binance_klines_table,
            "okx": self._create_okx_klines_table,
        }

        asset_class_map = self._exchange_asset_class_map(exchange)
        for asset_class in tqdm(asset_class_map):
            for freq in tqdm(self.FREQ_MAP, leave=False):
                try:
                    klines_funcs[exchange](asset_class, freq)
                except Exception as e:
                    print(f"Error creating klines table for {asset_class} {freq}: {e}")

    def update_factors(self, exchange: Literal["binance", "okx"] = "binance"):
        factors_funcs = {
            "binance": self._create_binance_factors_table,
            "okx": self._create_okx_factors_table,
        }

        asset_class_map = self._exchange_asset_class_map(exchange)
        for asset_class in tqdm(asset_class_map):
            for freq in tqdm(self.FREQ_MAP, leave=False):
                try:
                    factors_funcs[exchange](asset_class, freq)
                except Exception as e:
                    print(f"Error creating factors table for {asset_class} {freq}: {e}")

    def df_factors(
        self,
        symbols: list[str] | None = None,
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"] = "1m",
        asset_class: Literal["spot", "um"] = "um",
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        order_by_timestamp: bool = False,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
        exchange: Literal["binance", "okx"] = "binance",
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")   
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")   

        self._asset_class_check(asset_class, exchange=exchange)
        self._freq_check(freq)
        right, left = self._inclusive_check(inclusive)

        sql = f"""
        SELECT * FROM {exchange}_{asset_class}_factors_{freq}
        WHERE 1=1
        {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ""}
        {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        """
        if order_by_timestamp:
            sql += "ORDER BY timestamp"
        return self.conn.query(sql).to_df()

    def df_klines(
        self,
        symbols: list[str] | None = None,
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"] = "1m",
        asset_class: Literal["spot", "um"] = "um",
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        order_by_timestamp: bool = False,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
        exchange: Literal["binance", "okx"] = "binance",
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")   
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")   

        self._asset_class_check(asset_class, exchange=exchange)
        self._freq_check(freq)
        right, left = self._inclusive_check(inclusive)
        sql = f"""
        SELECT * FROM {exchange}_{asset_class}_klines_{freq}
        WHERE 1=1
        {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ""}
        {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        """
        if order_by_timestamp:
            sql += "ORDER BY timestamp"
        return self.conn.query(sql).to_df()

    def klines_matrix(
        self,
        symbols: list[str] | None = None,
        field: Literal[
            "open",
            "high",
            "low",
            "close",
            "volume",
            "quote_volume",
            "taker_buy_volume",
            "taker_buy_quote_volume",
        ] = "close",
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"] = "1m",
        asset_class: Literal["spot", "um"] = "um",
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
        exchange: Literal["binance", "okx"] = "binance",
    ):
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S")
        self._asset_class_check(asset_class, exchange=exchange)
        self._freq_check(freq)
        right, left = self._inclusive_check(inclusive)

        sql = f"""
        WITH filtered_klines AS (
            SELECT timestamp, symbol, {field}
            FROM {exchange}_{asset_class}_klines_{freq}
            WHERE 1=1
            {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ""}
            {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
            {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        )
        PIVOT filtered_klines ON symbol USING min({field})
        ORDER BY timestamp
        """
        return self.conn.query(sql).to_df()

    def factors_matrix(
        self,
        symbols: list[str] | None = None,
        factor: Literal["return", "momentum", "volatility", "beta"] = "return",
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"] = "1m",
        asset_class: Literal["spot", "um", "swap"] = "um",
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
        exchange: Literal["binance", "okx"] = "binance",
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")   
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")   
        self._asset_class_check(asset_class, exchange=exchange)
        self._freq_check(freq)
        right, left = self._inclusive_check(inclusive)

        sql = f"""
        WITH filtered_factors AS (
            SELECT timestamp, symbol, {factor}
            FROM {exchange}_{asset_class}_factors_{freq}
            WHERE 1=1
            {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ""}
            {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
            {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        )
        PIVOT filtered_factors ON symbol USING min({factor})
        ORDER BY timestamp
        """
        df = self.conn.query(sql).to_df()

        if symbols:
            expected_columns = set(symbols)
            existing_columns = set(df.columns) - {"timestamp"}
            df_nan = pd.DataFrame(
                np.nan,
                index=df.index,
                columns=list(expected_columns - existing_columns),
            )
            column_order = ["timestamp"] + symbols
            df = pd.concat([df, df_nan], axis=1)
            df = df.reindex(columns=column_order)
        df.set_index("timestamp", inplace=True)
        return df

    def _news_source_check(self, source: str):
        if source not in [
            "BWEnews",
            "ChainCatcher",
            "ChainNews",
            "FCNews",
            "ForeSight",
            "ODaily",
            "PANews",
            "TechFlow",
            "WuBlock",
        ]:
            raise DBError(
                f"Invalid news source: {source}. Must be one of: BWEnews, ChainCatcher, ChainNews, FCNews, ForeSight, ODaily, PANews, TechFlow, WuBlock"
            )

    def news(
        self,
        source: Literal[
            "BWEnews",
            "ChainCatcher",
            "ChainNews",
            "FCNews",
            "ForeSight",
            "ODaily",
            "PANews",
            "TechFlow",
            "WuBlock",
        ] = "BWEnews",
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
    ):
        self._news_source_check(source)
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")   
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")   
        right, left = self._inclusive_check(inclusive)

        path = os.path.join(self._share_folder_path, "news_data", source, "*.parquet")
        sql = f"""
        SELECT * FROM read_parquet('{path}')
        WHERE 1=1
        {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        ORDER BY timestamp
        """
        return self.conn.query(sql).to_df()
    
    def alpaca_klines(
        self,
        symbol: str | None = None,
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")   
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")      
        right, left = self._inclusive_check(inclusive)
        path = os.path.join(self._share_folder_path, "alpaca", "kline","*.parquet")
        sql = f"""
        SELECT * FROM read_parquet('{path}')
        WHERE 1=1
        {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        {f"AND symbol = '{symbol}'" if symbol else ""}
        ORDER BY timestamp
        """
        return self.conn.query(sql).to_df()
    
    def alpaca_auctions(
        self,
        symbol: str | None = None,
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")   
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")      
        right, left = self._inclusive_check(inclusive)
        path = os.path.join(self._share_folder_path, "alpaca", "auction","*.parquet")
        sql = f"""
        SELECT * FROM read_parquet('{path}')
        WHERE 1=1
        {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        {f"AND symbol = '{symbol}'" if symbol else ""}
        ORDER BY timestamp
        """
        return self.conn.query(sql).to_df()

    def cmc_snapshot(
        self,
        symbol: str | None = None,
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")   
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")   
        right, left = self._inclusive_check(inclusive)
        path = os.path.join(self._share_folder_path, "cmc_snapshot", "*.parquet")
        sql = f"""
        SELECT * FROM read_parquet('{path}')
        WHERE 1=1
        {f"AND date {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND date {left} TIMESTAMP '{end_date}'" if end_date else ""}
        {f"AND symbol = '{symbol}'" if symbol else ""}
        ORDER BY date
        """
        df = self.conn.query(sql).to_df()
        df['date'] = pd.to_datetime(df['date']).dt.floor('D')  # Ensure date is in date format
        return df

    def _create_okx_klines_table(
        self,
        asset_class: Literal["swap", "spot"],
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"],
    ):
        self._read_only_check()
        self._freq_check(freq)
        self._asset_class_check(asset_class, exchange="okx")
        base_path = os.path.join(
            self._share_folder_path, "okx_data", asset_class, "klines"
        )

        if freq == "1m":
            sql = f"""
            CREATE OR REPLACE TABLE okx_{asset_class}_klines_{freq} AS
            SELECT DISTINCT
                SPLIT_PART(SPLIT_PART(filename, '-klines-', 1), '/', -1) as symbol,
                timestamp,
                open,
                high,
                low,
                close,
                volume
            FROM read_parquet(
                '{base_path}/*/*.parquet',
                FILENAME = true
            )
            """
        else:
            sql = f"""
            CREATE OR REPLACE TABLE okx_{asset_class}_klines_{freq} AS
            SELECT
                SPLIT_PART(SPLIT_PART(filename, '-klines-', 1), '/', -1) as symbol,
                time_bucket(INTERVAL {self.FREQ_MAP[freq]} minutes, timestamp) as timestamp,
                FIRST(open) as open,
                MAX(high) as high,
                MIN(low) as low,
                LAST(close) as close,
                SUM(volume) as volume
            FROM read_parquet(
                '{base_path}/*/*.parquet',
                FILENAME = true
            )
            GROUP BY symbol, time_bucket(INTERVAL {self.FREQ_MAP[freq]} minutes, timestamp)
            """
        self.conn.execute(sql)

    def _create_okx_factors_table(
        self,
        asset_class: Literal["swap", "spot"],
        freq: Literal["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"],
    ):
        if asset_class == "swap":
            btc_symbol = "BTC-USDT-SWAP"
        else:
            btc_symbol = "BTC-USDT"

        self._read_only_check()
        self._freq_check(freq)
        self._asset_class_check(asset_class, exchange="okx")

        m_window = self.MOMENTUM_WINDOW_MAP[freq]
        v_window = self.VOLATILITY_WINDOW_MAP[freq]
        b_window = self.BETA_WINDOW_MAP[freq]

        sql = f"""
        CREATE OR REPLACE TABLE okx_{asset_class}_factors_{freq} AS
        WITH base AS (
            SELECT 
                k.symbol,
                k.timestamp,
                k.close,
                k.close / LAG(k.close) OVER w_symbol - 1 AS return,
                btc.return AS btc_return
            FROM okx_{asset_class}_klines_{freq} k
            LEFT JOIN (
                SELECT 
                    timestamp,
                    close / LAG(close) OVER (ORDER BY timestamp) - 1 AS return
                FROM okx_{asset_class}_klines_{freq}
                WHERE symbol = '{btc_symbol}'
            ) btc USING (timestamp)
            WINDOW w_symbol AS (PARTITION BY k.symbol ORDER BY k.timestamp)
        ),
        factors AS (
            SELECT
                *,
                -- 合并窗口计算
                CASE WHEN ROW_NUMBER() OVER w_symbol >= {m_window} 
                    THEN PRODUCT(1 + return) OVER (w_symbol ROWS BETWEEN {m_window - 1} PRECEDING AND CURRENT ROW) - 1 
                    ELSE NULL END AS momentum,
                    
                CASE WHEN ROW_NUMBER() OVER w_symbol >= {v_window} 
                    THEN STDDEV(return) OVER (w_symbol ROWS BETWEEN {v_window - 1} PRECEDING AND CURRENT ROW) 
                    ELSE NULL END AS volatility,
                    
                CASE WHEN ROW_NUMBER() OVER w_symbol >= {b_window} 
                    THEN REGR_SLOPE(btc_return, return) OVER (w_symbol ROWS BETWEEN {b_window - 1} PRECEDING AND CURRENT ROW) 
                    ELSE NULL END AS beta
            FROM base
            WINDOW w_symbol AS (PARTITION BY symbol ORDER BY timestamp)
        )

        SELECT
            timestamp,
            symbol,
            close,
            return,
            momentum,
            volatility,
            beta
            FROM factors;
        """

        self.conn.execute(sql)
    
    def df_binance_um_matrix(self, 
        symbols: list[str] | None = None,
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
        order_by_timestamp: bool = False,
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.join(self._share_folder_path, "binance_data/futures/um/daily/metrics")
        right, left = self._inclusive_check(inclusive)

        sql = f"""
        SELECT 
            to_timestamp(timestamp / 1000) as timestamp,
            symbol,
            sum_open_interest_value,
            count_toptrader_long_short_ratio,  
            sum_toptrader_long_short_ratio, 
            count_long_short_ratio, 
            sum_taker_long_short_vol_ratio
        FROM read_parquet('{path}/*/*.parquet')
        WHERE 1=1
        {f"AND to_timestamp(timestamp / 1000) {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND to_timestamp(timestamp / 1000) {left} TIMESTAMP '{end_date}'" if end_date else ""}
        {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ""}
        """
        if order_by_timestamp:
            sql += " ORDER BY timestamp"
        
        return self.conn.query(sql).to_df()
    
    def df_funding_rate(
        self,
        symbols: list[str] | None = None,
        start_date: Union[str, datetime.datetime] | None = None,
        end_date: Union[str, datetime.datetime] | None = None,
        inclusive: Literal["right", "left", "both", "neither"] = "right",
        exchange: Literal["binance", "okx"] = "binance",
        order_by_timestamp: bool = False,
    ):
        if start_date:
            if isinstance(start_date, datetime.datetime):
                start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        if end_date:
            if isinstance(end_date, datetime.datetime):
                end_date = end_date.strftime("%Y-%m-%d %H:%M:%S")
                
        if exchange == "binance":
            path = os.path.join(self._share_folder_path, "binance_data/futures/um/daily/funding_rate/*.parquet")
        elif exchange == "okx":
            path = os.path.join(self._share_folder_path, "okx_data/swap/swaprate-all/*/*.parquet")
        
        right, left = self._inclusive_check(inclusive)
        
        sql = f"""
        SELECT 
            *
        FROM read_parquet('{path}')
        WHERE 1=1
        {f"AND timestamp {right} TIMESTAMP '{start_date}'" if start_date else ""}
        {f"AND timestamp {left} TIMESTAMP '{end_date}'" if end_date else ""}
        {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ""}
        {"ORDER BY timestamp" if order_by_timestamp else ""}
        """
        df = self.conn.query(sql).to_df()
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.floor('h')  # Ensure timestamp is in date format

        if exchange == "okx":
            df['timestamp'] = df['timestamp'] - pd.Timedelta(hours=8)

        return df
        
        
        
