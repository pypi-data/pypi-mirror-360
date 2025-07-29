#! /usr/bin/python3

import os
import sqlite3

import numpy as np
import pandas as pd

from .holidays import Holidays
from .utils import get_tencent_client


class Instrument:
    """
    Handy wrapper of instrument.db files
    """

    tencent_addr = "https://market-data-1330004739.cos.ap-shanghai.myqcloud.com/"
    public_addr = "public/promisedland/"

    def __init__(self, dt:str, suffix:str='8am', bucket='market-data-1330004739', sct_id="", sct_key=""):
        """
        Returns an instance of Instrument class for instrument.db

        Parameters
        ----------
        dt: date string for an instrument
        suffix: use instrument_%Y-%m-%d_{suffix}.db

        Raises
        ----------
        FileNotFoundError
            * If the specified instrument is not on COS

        Examples
        --------
        >>> ins = Instrument("20210908", suffix='csi')
        >>> ins = Instrument("20210908")
        """
        self.dt = Holidays.to_datetime(dt)
        self.suffix = suffix
        self.coscli = get_tencent_client(sct_id=sct_id, sct_key=sct_key)
        # self.bucket = 'market-data-1302861777'
        self.bucket = bucket
        # Instrument.tencent_addr = f"https://{self.bucket}.cos.ap-shanghai.myqcloud.com/"

        self._cache_instrument_db()

    def __del__(self):
        try:
            self.coscli._session.close()
            os.remove(self.cache)
        except FileNotFoundError:
            pass
        except OSError:
            pass

    def _cache_instrument_db(self) -> int:
        dt_str = self.dt.strftime("%Y-%m-%d") if Holidays.tradingday(self.dt) else Holidays.prev_tradingday(self.dt).strftime("%Y-%m-%d")
        remote_db_name = f"instrument_{dt_str}_{self.suffix}.db"
        local_db_name = f"tmp_{remote_db_name}"
        if not os.path.exists(local_db_name):
            response = self.coscli.get_object(Bucket=self.bucket, Key=self.dt.strftime(f"trade-data/dbs/%Y/%m/instrument_{dt_str}_{self.suffix}.db"))
            response['Body'].get_stream_to_file(local_db_name)
        self.cache = local_db_name
        return 0

    def get_contract_mapping(self,
                            col=['code', 'type', 'strike', 'expiration', 'unit'],
                            colnames=['code', 'type', 'strike', 'expiration', 'unit']) -> pd.DataFrame:

        """
        Return the contract mapping of an Instrument instance

        Parameters
        ----------
        col: columns that select from , default is '['code', 'type', 'strike', 'expiration', 'unit']'
        colnames: column names of the returned Pandas DataFrame

        Examples
        --------
        >>> ins = Instrument("20210908")
        >>> ins.get_contract_mapping()
        >>> 	code	type	strike	expiration	unit
            0	IO2009-C-3100	1.0	3100.0	2020-09-18	100
            1	IO2009-C-3200	1.0	3200.0	2020-09-18	100
            2	IO2009-C-3300	1.0	3300.0	2020-09-18	100
            3	IO2009-C-3400	1.0	3400.0	2020-09-18	100
            4	IO2009-C-3500	1.0	3500.0	2020-09-18	100
            ...	...	...	...	...	...
            11	IF2112	0.0	NaN	2021-12-17	300
            12	IF2107	0.0	NaN	2021-07-16	300
            13	IF2108	0.0	NaN	2021-08-20	300
            14	IF2203	0.0	NaN	2022-03-18	300
            15	IF2110	0.0	NaN	2021-10-15	300
            948 rows x 5 columns
        """
        conn = sqlite3.connect(self.cache)
        cur = conn.cursor()
        columns = ', '.join(col)
        cur.execute(f"SELECT {columns} FROM Options;")
        opt_df = pd.DataFrame.from_records(cur.fetchall(), columns=col)
        cur.execute(f"SELECT code, type, expiration, unit FROM Futures;")
        fut_df = pd.DataFrame.from_records(cur.fetchall(), columns=['code', 'type', 'expiration', 'unit'])
        fut_df['strike'] = np.nan
        ret = pd.concat([opt_df, fut_df])
        ret['expiration'] = pd.to_datetime(ret['expiration'], format='%Y%m%d')
        ret['expiration'] = ret['expiration'].astype(str)
        ret.columns = colnames
        conn.close()
        return ret

    def get_tradable_contracts(self, prefix='IF') -> pd.DataFrame:
        """
        Return 4 tradable Futures codes of an Instrument instance

        Examples
        --------
        >>> ins = Instrument("20220722")
        >>> ins.get_tradable_contracts()
        >>> code
            0   IF2303
            1   IF2212
            2   IF2209
            3   IF2208
            4   IF2207
            5   IF2206
        >>> ins.get_tradable_contracts(prefix='IM')
        >>> code
            0  IM2303
            1  IM2212
            2  IM2209
            3  IM2208
        """
        conn = sqlite3.connect(self.cache)
        cur = conn.cursor()
        cur.execute(f"SELECT code FROM Futures WHERE (Code LIKE '%{prefix}%') ORDER BY code DESC;")
        ret = cur.fetchall()
        ret = pd.DataFrame(ret, columns=['code'])
        return ret
