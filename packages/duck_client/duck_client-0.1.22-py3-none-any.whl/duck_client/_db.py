import duckdb
import fireducks.pandas as pd
from typing import Literal
from urllib.parse import urljoin
from pathlib import Path
from tqdm import tqdm
import datetime
import numpy as np


class DataBase:
    FREQ_MAP = {
        "1m": 1,
        "3m": 3,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "6h": 360,
        "12h": 720,
        "1d": 1440,
    }

    ASSET_CLASS_MAP = {
        "spot": "spot",
        "um": "futures/um",
        "cm": "futures/cm",
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
        cache_base_path: str = "/usr/local/share/binance_data/cache/",
        db_path: str | None = None,
        read_only: bool = True,
    ):
        """
        Initialize the query class

        Args:
            cache_base_path: The base path of the cache data
        """
        self._db_path = db_path
        self.cache_base_path = cache_base_path

        if db_path:
            self.conn = duckdb.connect(database=db_path, read_only=read_only)
        else:
            self.conn = duckdb.connect()
            
        self._read_only = read_only

    def _check_table_exists(self, table_name: str):
        check_sql = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_name = '{table_name}'"
        table_exists = self.conn.query(check_sql).fetchone()[0] > 0
        return table_exists

    def klines_2_db(
        self,
        symbol: str,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
    ):
        if freq not in self.FREQ_MAP:
            raise ValueError(
                f"Invalid frequency: {freq}. Must be one of: {', '.join(self.FREQ_MAP.keys())}"
            )

        table_name = f"binance_{asset_class}_klines_{freq}_{symbol}"
        table_exists = self._check_table_exists(table_name)

        monthly_path = urljoin(
            self.cache_base_path,
            f"{self.ASSET_CLASS_MAP[asset_class]}/monthly/klines/{symbol}/1m/*.parquet",
        )
        daily_path = urljoin(
            self.cache_base_path,
            f"{self.ASSET_CLASS_MAP[asset_class]}/daily/klines/{symbol}/1m/*.parquet",
        )

        def get_create_table_sql(paths: str) -> str:
            if freq == "1m":
                return f"""
                    CREATE TABLE IF NOT EXISTS {table_name} AS
                    SELECT DISTINCT
                        to_timestamp(timestamp / 1000) as timestamp,
                        open, high, low, close,
                        volume, quote_volume,
                        taker_buy_volume, taker_buy_quote_volume
                    FROM read_parquet({paths})
                    ORDER BY timestamp
                """
            else:
                return f"""
                    CREATE TABLE IF NOT EXISTS {table_name} AS
                    SELECT DISTINCT
                        time_bucket(INTERVAL '{self.FREQ_MAP[freq]} minutes', to_timestamp(timestamp / 1000)) as timestamp,
                        FIRST(open) as open,
                        MAX(high) as high,
                        MIN(low) as low,
                        LAST(close) as close,
                        SUM(volume) as volume,
                        SUM(quote_volume) as quote_volume,
                        SUM(taker_buy_volume) as taker_buy_volume,
                        SUM(taker_buy_quote_volume) as taker_buy_quote_volume
                    FROM read_parquet({paths})
                    GROUP BY time_bucket(INTERVAL '{self.FREQ_MAP[freq]} minutes', to_timestamp(timestamp / 1000))
                    ORDER BY timestamp
                """

        def get_insert_table_sql(paths: str, last_ts: datetime.datetime) -> str:
            last_ts = datetime.datetime(
                last_ts.year, last_ts.month, last_ts.day, 0, 0, 0
            ) + datetime.timedelta(days=1)

            last_ts_ms = int(last_ts.timestamp() * 1000)
            if freq == "1m":
                return f"""
                    WITH filtered_data AS (
                        SELECT *
                        FROM read_parquet({paths})
                        WHERE timestamp >= {last_ts_ms}
                    )
                    INSERT INTO {table_name}
                    SELECT DISTINCT
                        to_timestamp(timestamp / 1000) as timestamp,
                        open, high, low, close,
                        volume, quote_volume,
                        taker_buy_volume, taker_buy_quote_volume
                    FROM filtered_data
                    ORDER BY timestamp
                """
            else:
                return f"""
                    WITH filtered_data AS (
                        SELECT *
                        FROM read_parquet({paths})
                        WHERE timestamp >= {last_ts_ms}
                    )
                    INSERT INTO {table_name}
                    SELECT DISTINCT
                        time_bucket(INTERVAL '{self.FREQ_MAP[freq]} minutes', to_timestamp(timestamp / 1000)) as timestamp,
                        FIRST(open) as open,
                        MAX(high) as high,
                        MIN(low) as low,
                        LAST(close) as close,
                        SUM(volume) as volume,
                        SUM(quote_volume) as quote_volume,
                        SUM(taker_buy_volume) as taker_buy_volume,
                        SUM(taker_buy_quote_volume) as taker_buy_quote_volume
                    FROM filtered_data
                    GROUP BY time_bucket(INTERVAL '{self.FREQ_MAP[freq]} minutes', to_timestamp(timestamp / 1000))
                    ORDER BY timestamp
                """

        path_options = [
            f"['{monthly_path}', '{daily_path}']",
            f"['{daily_path}']",
            f"['{monthly_path}']",
        ]

        for paths in path_options:
            try:
                if not table_exists:
                    self.conn.execute(get_create_table_sql(paths))
                else:
                    last_ts = self.conn.query(
                        f"SELECT MAX(timestamp) FROM {table_name}"
                    ).fetchone()[0]
                    self.conn.execute(get_insert_table_sql(paths, last_ts))
                break
            except duckdb.duckdb.IOException:
                continue

    def _list_klines_symbols(self, asset_class: Literal["spot", "um", "cm"] = "um"):
        monthly_path = urljoin(
            self.cache_base_path, f"{self.ASSET_CLASS_MAP[asset_class]}/monthly/klines/"
        )
        daily_path = urljoin(
            self.cache_base_path, f"{self.ASSET_CLASS_MAP[asset_class]}/daily/klines/"
        )

        monthly_symbols = [x.name for x in Path(monthly_path).iterdir() if x.is_dir()]
        daily_symbols = [x.name for x in Path(daily_path).iterdir() if x.is_dir()]

        return list(set(monthly_symbols + daily_symbols))

    def _list_metrics_symbols(self, asset_class: Literal["um"] = "um"):
        daily_path = urljoin(
            self.cache_base_path, f"{self.ASSET_CLASS_MAP[asset_class]}/daily/metrics/"
        )
        daily_symbols = [x.name for x in Path(daily_path).iterdir() if x.is_dir()]
        return daily_symbols

    def list_all_symbols(
        self,
        asset_class: Literal["spot", "um", "cm"] = "um",
        data_type: Literal["klines", "metrics"] = "klines",
    ):
        if data_type == "klines":
            return self._list_klines_symbols(asset_class)
        elif data_type == "metrics":
            if asset_class != "um":
                raise ValueError("`metrics` only support `um`")
            return self._list_metrics_symbols(asset_class)

    def klines(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
    ):
        if freq not in self.FREQ_MAP:
            raise ValueError(
                f"Invalid frequency: {freq}. Must be one of: {', '.join(self.FREQ_MAP.keys())}"
            )

        table_klines = f"binance_{asset_class}_klines_{freq}_{symbol}"
        table_factors = f"binance_{asset_class}_factors_{freq}_{symbol}"
        sql = f"""
            WITH klines AS (
                SELECT * FROM {table_klines}
            ),
            factors AS (
                SELECT * FROM {table_factors}
            )
            SELECT klines.*, factors.return, factors.momentum, factors.volatility, factors.beta
            FROM klines
            LEFT JOIN factors ON klines.timestamp = factors.timestamp
        """

        if start_date:
            start_date = pd.to_datetime(start_date).timestamp() 
            sql += f" WHERE klines.timestamp >= TO_TIMESTAMP('{start_date}')"
        if end_date:
            end_date = pd.to_datetime(end_date).timestamp()
            sql += f" AND klines.timestamp < TO_TIMESTAMP('{end_date}')"

        df = self.conn.query(sql).to_df()
        
        df.loc[:self.MOMENTUM_WINDOW_MAP[freq], 'momentum'] = np.nan
        df.loc[:self.VOLATILITY_WINDOW_MAP[freq], 'volatility'] = np.nan
        df.loc[:self.BETA_WINDOW_MAP[freq], 'beta'] = np.nan
        return df

    def query_data(
        self,
        symbol: str,
        freq: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        fields: list[str] | None = None,
        asset_class: Literal["spot", "futures/um", "futures/cm"] = "futures/um",
        data_type: Literal["klines", "metrics"] = "klines",
    ):
        if data_type == "metrics" and asset_class != "futures/um":
            raise ValueError("`metrics` only support `futures/um`")

        # 检查 klines 数据类型是否提供了 freq 参数
        if data_type == "klines" and not freq:
            raise ValueError("`klines` data type must provide `freq` parameter")

        if start_date:
            start_date = pd.to_datetime(start_date).timestamp() * 1000
        if end_date:
            end_date = pd.to_datetime(end_date).timestamp() * 1000

        # 构建 SELECT 语句的列部分
        columns = "*" if not fields else ", ".join(fields)

        if data_type == "klines":
            try:
                monthly_path = urljoin(
                    self.cache_base_path,
                    f"{asset_class}/monthly/klines/{symbol}/{freq}/*.parquet",
                )
                daily_path = urljoin(
                    self.cache_base_path,
                    f"{asset_class}/daily/klines/{symbol}/{freq}/*.parquet",
                )

                if start_date and end_date:
                    df = self.conn.query(
                        f"SELECT {columns} FROM read_parquet(['{monthly_path}', '{daily_path}']) "
                        f"WHERE open_time >= {start_date} AND open_time < {end_date}"
                    ).to_df()
                else:
                    df = self.conn.query(
                        f"SELECT {columns} FROM read_parquet(['{monthly_path}', '{daily_path}'])"
                    ).to_df()
            except duckdb.duckdb.IOException:
                if start_date and end_date:
                    df = self.conn.query(
                        f"SELECT {columns} FROM read_parquet(['{daily_path}']) "
                        f"WHERE open_time >= {start_date} AND open_time < {end_date}"
                    ).to_df()
                else:
                    df = self.conn.query(
                        f"SELECT {columns} FROM read_parquet(['{daily_path}'])"
                    ).to_df()
        elif data_type == "metrics":
            daily_path = urljoin(
                self.cache_base_path, f"{asset_class}/daily/metrics/{symbol}/*.parquet"
            )

            if start_date and end_date:
                df = self.conn.query(
                    f"SELECT {columns} FROM read_parquet(['{daily_path}']) "
                    f"WHERE open_time >= {start_date} AND open_time < {end_date}"
                ).to_df()
            else:
                df = self.conn.query(
                    f"SELECT {columns} FROM read_parquet(['{daily_path}'])"
                ).to_df()

        return df

    def factors_2_db(
        self, symbol: str, freq: str, asset_class: Literal["spot", "um", "cm"] = "um"
    ):


        if freq not in self.MOMENTUM_WINDOW_MAP:
            raise ValueError(f"Not support freq: {freq}")

        m_window = self.MOMENTUM_WINDOW_MAP[freq]
        v_window = self.VOLATILITY_WINDOW_MAP[freq]
        b_window = self.BETA_WINDOW_MAP[freq]

        table_name = f"binance_{asset_class}_klines_{freq}_{symbol}"
        btc_table = f"binance_{asset_class}_klines_{freq}_BTCUSDT"

        factors_table_name = f"binance_{asset_class}_factors_{freq}_{symbol}"

        sql = f"""
        CREATE OR REPLACE TABLE {factors_table_name} AS
        WITH base_returns AS (
            SELECT DISTINCT
                t1.timestamp,
                (t1.close/LAG(t1.close) OVER (ORDER BY t1.timestamp) - 1) AS return,
                (t2.close/LAG(t2.close) OVER (ORDER BY t2.timestamp) - 1) AS btc_return
            FROM {table_name} t1
            LEFT JOIN {btc_table} t2 ON t1.timestamp = t2.timestamp
        ),
        momentum AS (
            SELECT 
                *,
                PRODUCT(1 + return) OVER (
                    ORDER BY timestamp 
                    ROWS BETWEEN {m_window - 1} PRECEDING AND CURRENT ROW
                ) - 1 AS momentum
            FROM base_returns
        ),
        volatility AS (
            SELECT 
                *,
                STDDEV(return) OVER (
                    ORDER BY timestamp 
                    ROWS BETWEEN {v_window - 1} PRECEDING AND CURRENT ROW
                ) AS volatility
            FROM momentum
        ),
        beta AS (
            SELECT 
                *,
                REGR_SLOPE(btc_return, return) OVER (
                    ORDER BY timestamp
                    ROWS BETWEEN {b_window - 1} PRECEDING AND CURRENT ROW
                ) AS beta
            FROM volatility
        )
        SELECT 
            timestamp,
            return,
            momentum,
            volatility,
            beta
        FROM beta
        ORDER BY timestamp
        """
        self.conn.execute(sql)
        
    def update_klines(
        self,
        asset_class: Literal["spot", "um", "cm"] = "um",
        symbols: list[str] | None = None,
    ):
        if self._read_only:
            raise ValueError("`update_klines` is not allowed in read-only mode, please set `read_only=False`")
        
        if not symbols:
            symbols = self.list_all_symbols(asset_class=asset_class, data_type="klines")
        freqs = ["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"]
        for symbol in tqdm(symbols):
            try:
                for freq in tqdm(freqs, leave=False):
                    self.klines_2_db(symbol=symbol, freq=freq, asset_class=asset_class)
            except Exception as e:
                print(f"Error: {e} {symbol} {freq}")

    def update_factors(
        self, asset_class: Literal["um"] = "um", symbols: list[str] | None = None
    ):
        if self._read_only:
            raise ValueError("`update_factors` is not allowed in read-only mode, please set `read_only=False`")
        
        if not symbols:
            symbols = self.list_all_symbols(asset_class=asset_class, data_type="klines")
        freqs = ["1m", "3m", "15m", "30m", "1h", "4h", "12h", "1d"]
        for symbol in tqdm(symbols):
            for freq in tqdm(freqs, leave=False):
                try:
                    self.factors_2_db(symbol=symbol, freq=freq, asset_class=asset_class)
                except Exception as e:
                    print(f"Error: {e} {symbol} {freq}")
                    

    def return_matrix(
        self,
        symbols: list[str],
        start_date: str | None = None,
        end_date: str | None = None,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
    ) -> pd.DataFrame:
        # 构建基础SQL查询 - 使用UNION ALL获取所有唯一时间戳
        base_sql = """
        WITH all_timestamps AS (
            SELECT DISTINCT timestamp
            FROM (
        """
        
        # 为每个交易对添加时间戳
        for i, symbol in enumerate(symbols):
            base_sql += f"""
                SELECT timestamp
                FROM binance_{asset_class}_factors_{freq}_{symbol}
                {f"WHERE timestamp >= TIMESTAMP '{start_date}' AND timestamp < TIMESTAMP '{end_date}'" if start_date and end_date else ""}
                {'UNION ALL' if i < len(symbols)-1 else ''}
            """
            
        base_sql += """
            )
            ORDER BY timestamp
        )
        SELECT at.timestamp"""
        
        # 为每个交易对添加return列
        for symbol in symbols:
            base_sql += f"""
            , f_{symbol}.return as '{symbol}'
            """
            
        base_sql += "\nFROM all_timestamps at\n"
        
        # 添加所有FULL OUTER JOIN语句
        for symbol in symbols:
            base_sql += f"""
            FULL OUTER JOIN binance_{asset_class}_factors_{freq}_{symbol} f_{symbol}
            ON at.timestamp = f_{symbol}.timestamp
            """
            
        base_sql += "\nORDER BY at.timestamp"
            
        # 执行查询并返回DataFrame
        return self.conn.query(base_sql).to_df()
    
    def return_matrix_v2(
        self,
        symbols: list[str],
        start_date: str | None = None,
        end_date: str | None = None,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
    ) -> pd.DataFrame:
        
        dfs = []
        for symbol in tqdm(symbols):
            sql = f"""
            SELECT timestamp, return as '{symbol}'
            FROM binance_{asset_class}_factors_{freq}_{symbol}
            """
            
            if start_date and end_date:
                sql += f" WHERE timestamp >= TIMESTAMP '{start_date}' AND timestamp < TIMESTAMP '{end_date}'"
                
            df = self.conn.query(sql).to_df()
            df.set_index("timestamp", inplace=True)
            dfs.append(df)
            
        return pd.concat(dfs, axis=1)
    
    def create_merged_klines(
        self,
        symbols: list[str],
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
    ):
        if self._read_only:
            raise ValueError("`create_merged_klines` is not allowed in read-only mode, please set `read_only=False`")

        merged_table = f"binance_{asset_class}_klines_{freq}"
        
        # 使用UNION ALL一次性合并所有数据
        create_sql = f"""
        CREATE OR REPLACE TABLE {merged_table} AS
        SELECT * FROM (
        """
        
        for i, symbol in enumerate(symbols):
            source_table = f"binance_{asset_class}_klines_{freq}_{symbol}"
            create_sql += f"""
            SELECT 
                timestamp,
                '{symbol}' as symbol,
                open,
                high,
                low,
                close,
                volume,
                quote_volume,
                taker_buy_volume,
                taker_buy_quote_volume
            FROM {source_table}
            {'UNION ALL' if i < len(symbols)-1 else ''}
            """
        
        create_sql += ")"
        
        try:
            self.conn.execute(create_sql)
        except Exception as e:
            print(f"Error creating merged table: {e}")
    
    def create_merged_factors(
        self,
        symbols: list[str],
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
    ):
        if self._read_only:
            raise ValueError("`create_merged_klines` is not allowed in read-only mode, please set `read_only=False`")

        merged_table = f"binance_{asset_class}_factors_{freq}"
        
        # 使用UNION ALL一次性合并所有数据
        create_sql = f"""
        CREATE OR REPLACE TABLE {merged_table} AS
        SELECT * FROM (
        """

        for i, symbol in enumerate(symbols):
            source_table = f"binance_{asset_class}_factors_{freq}_{symbol}"
            create_sql += f"""
            SELECT 
                timestamp,
                '{symbol}' as symbol,
                return,
                momentum,
                volatility,
                beta
            FROM {source_table}
            {'UNION ALL' if i < len(symbols)-1 else ''}
            """
        
        create_sql += ")"
        
        try:
            self.conn.execute(create_sql)
        except Exception as e:
            print(f"Error creating merged table: {e}")
    
    def klines_matrix(
        self,
        symbols: list[str] | None = None,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
        value_col: Literal["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_volume", "taker_buy_quote_volume"] = "close",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        table_name = f"binance_{asset_class}_klines_{freq}"
        
        sql = f"""
        WITH filtered_klines AS (
            SELECT timestamp, symbol, {value_col}
            FROM {table_name}
            WHERE 1=1
            {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ''}
            {f"AND timestamp >= TIMESTAMP '{start_date}'" if start_date else ''}
            {f"AND timestamp < TIMESTAMP '{end_date}'" if end_date else ''}
        )
        PIVOT filtered_klines ON symbol USING min({value_col})
        ORDER BY timestamp
        """
        
        return self.conn.query(sql).to_df()
    
    def factors_matrix(
        self,
        symbols: list[str] | None = None,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
        value_col: Literal["return", "momentum", "volatility", "beta"] = "return",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        table_name = f"binance_{asset_class}_factors_{freq}"
        
        sql = f"""
        WITH filtered_factors AS (
            SELECT timestamp, symbol, {value_col}
            FROM {table_name}
            WHERE 1=1
            {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ''}
            {f"AND timestamp >= TIMESTAMP '{start_date}'" if start_date else ''}
            {f"AND timestamp < TIMESTAMP '{end_date}'" if end_date else ''}
        )
        PIVOT filtered_factors ON symbol USING min({value_col})
        ORDER BY timestamp
        """
        
        return self.conn.query(sql).to_df()
    
    def klines_table(
        self,
        symbols: list[str] | None = None,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
        start_date: str | None = None,
        end_date: str | None = None,
    ):
        sql = f"""
        SELECT * FROM binance_{asset_class}_klines_{freq}
        WHERE 1=1
        {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ''}
        {f"AND timestamp >= TIMESTAMP '{start_date}'" if start_date else ''}
        {f"AND timestamp < TIMESTAMP '{end_date}'" if end_date else ''}
        """
        return self.conn.query(sql).to_df()
    
    def factors_table(
        self,
        symbols: list[str] | None = None,
        freq: str = "1m",
        asset_class: Literal["spot", "um", "cm"] = "um",
        start_date: str | None = None,
        end_date: str | None = None,
    ):
        sql = f"""
        SELECT * FROM binance_{asset_class}_factors_{freq}
        WHERE 1=1
        {f"AND symbol IN ({','.join([f''''{s}' ''' for s in symbols])})" if symbols else ''}
        {f"AND timestamp >= TIMESTAMP '{start_date}'" if start_date else ''}
        {f"AND timestamp < TIMESTAMP '{end_date}'" if end_date else ''}
        """
        return self.conn.query(sql).to_df()
        
    

if __name__ == "__main__":    
    path = "/usr/local/share/binance_data/cache/"
    db_path = "/usr/local/share/binance_data/data.db"
    db = DataBase(path, db_path, read_only=True)

    # db.update_klines(asset_class="spot", symbols=["BIOUSDT"])
    # db.update_factors(asset_class="spot", symbols=["BIOUSDT"])
    
    df = db.klines_table(symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"], freq="1m", asset_class="spot", start_date="2023-12-31 23:59:00")
    print(df)

    df = db.factors_table(symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"], freq="1m", asset_class="spot", start_date="2023-12-31 23:59:00")
    print(df)
