import hashlib
from datetime import datetime, timedelta

import duckdb


class DuckDBCache:
    def __init__(self):
        self.con = duckdb.connect()
        self.query_schedule = {}
        self._init_cache_metadata()

    def connect_database(self, database_con: str, database_type: str) -> None:
        self.con.sql(f"ATTACH '{database_con}' AS db (TYPE {database_type}, READ_ONLY);")
    
    def connect_query(self, query) -> None:
        query = self._query_clean(query)
        self.con.sql(query)

    def set_schedule_reset(
            self, query: str,
            hour: int = None,
            minute: int = None,
            second: int = None,
            interval: int = None) -> None:
        query = self._query_clean(query)
        query_hash = self._query_hash(query)
        self.query_schedule[query_hash] = {
            'hour':hour,
            'minute':minute,
            'second':second,
            'interval':interval
        }
    
    def get_data(self, query: str) -> duckdb.DuckDBPyRelation:
        query = self._query_clean(query)
        query_hash = self._query_hash(query)
        dt_now = datetime.now()
        
        if self._is_cache_reset(query_hash, dt_now):
            self._cache_reset(query_hash, query, dt_now)

        return self.con.sql(f"SELECT * FROM '{query_hash}'")
    
    def close(self) -> None:
        self.con.close()

    def _init_cache_metadata(self) -> None:
        self.con.sql("""
            CREATE TABLE IF NOT EXISTS cache_metadata (
                query_hash VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP);
        """)

    def _is_cache_reset(self, query_hash: str, dt_now: datetime) -> bool:
        query_metadata = self.con.sql(
            f"SELECT query_hash, timestamp FROM cache_metadata WHERE query_hash = '{query_hash}';").fetchone()

        if not query_metadata:
            return True
                
        schedule = self.query_schedule.get(query_hash)
                
        if not schedule:
            return False
        
        last_updated = query_metadata[1]
        interval = timedelta(seconds=schedule['interval'] if schedule['interval'] else 0)

        if interval > timedelta(seconds=0) and dt_now - last_updated >= interval:
            return True
            
        schedule_cache_reset = datetime(
            year=last_updated.year, 
            month=last_updated.month, 
            day=last_updated.day,
            hour=schedule['hour'] if schedule['hour'] else last_updated.hour,
            minute=schedule['minute'] if schedule['minute'] else last_updated.minute,
            second=schedule['second'] if schedule['second'] else last_updated.second)
        
        if schedule_cache_reset < last_updated and last_updated < dt_now:
            schedule_cache_reset += interval
        
        return last_updated < schedule_cache_reset and schedule_cache_reset < dt_now

    def _cache_reset(self, query_hash: str, query: str, dt_now: datetime) -> None:
        self.con.sql(f"INSERT OR REPLACE INTO cache_metadata VALUES ('{query_hash}', '{dt_now}');")
        self.con.sql(f"CREATE OR REPLACE TABLE '{query_hash}' AS {query}")

    @staticmethod
    def _query_hash(query: str) -> str:
        return hashlib.shake_128(query.encode()).hexdigest(10)

    @staticmethod
    def _query_clean(query: str) -> str:
        return ' '.join(query.split())
