from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import scoped_session, sessionmaker

# from model.pos.DbModelPo import User, Process

from sqlalchemy import select, create_engine, Engine
from sqlalchemy.orm import selectinload

import asyncio
import time
import typing
from typing import TypeVar
from co6co.utils import log
from co6co_db_ext.po import BasePO
from sqlalchemy.pool import NullPool


class db_service:
    default_settings: dict = {
        'DB_HOST': 'localhost',
        'DB_NAME': '',
        'DB_USER': 'root',
        'DB_PASSWORD': '',
        'echo': True,
        'pool_size': 20,
        'max_overflow': 10,
        'pool_pre_ping': True,  # 执行sql语句前悲观地检查db是否可用
        # 'pool_recycle':1800 #超时时间 单位s

    }
    settings = {}
    session: scoped_session  # 同步连接

    async_session_factory: sessionmaker  # 异步连接
    """
    AsyncSession 工厂函数
    sessionmaker 是个生成器类

    """
    useAsync: bool
    poolSize: int = None
    poolSize: int = None

    def createEngine(self, url, **kwargs) -> Engine:
        setting = {
            "ping": self.settings.get("pool_pre_ping"),
            "echo": True if type(self.settings.get("echo")) != bool else self.settings.get("echo"),
            "pool_size": self.settings.get("pool_size"),
            "max_overflow": self.settings.get("max_overflow"),
            "poolclass": NullPool
        }
        setting.update(kwargs)
        return create_engine(url, **setting)

    def createAsyncEngine(self, url, **kwargs) -> AsyncEngine:
        setting = {
            "pool_pre_ping": self.settings.get("pool_pre_ping"),
            "echo": True if type(self.settings.get("echo")) != bool else self.settings.get("echo"),
            "pool_size": self.settings.get("pool_size"),
            "max_overflow": self.settings.get("max_overflow")
        }
        setting.update(kwargs)
        return create_async_engine(url, **setting)

    def _session_factory(self, engine: Engine = None, **kv) -> AsyncSession:
        if engine == None:
            engine = self.createEngine(self.url)
        default = {
            "autoflush": False,
            "autocommit": False,
        }
        default.update(kv)
        factory = sessionmaker(bind=self.engine,  **default)
        return factory

    def _async_session_factory(self, engine: AsyncEngine = None, **kv) -> AsyncSession:
        if engine == None:
            engine = self.createAsyncEngine(self.url)
        default = {
            "expire_on_commit": False,
            "class_": AsyncSession,
        }
        default.update(kv)
        factory = sessionmaker(engine, **default)
        return factory

    def createSession(self, engine: AsyncEngine = None, **kv) -> scoped_session:
        factory = self._session_factory(engine, **kv)
        return scoped_session(factory)

    def createAsyncSession(self, engine: AsyncEngine = None, **kv) -> AsyncSession:
        factory = self._async_session_factory(engine, **kv)
        return factory()

    def _createEngine(self, url: str):
        self.useAsync = True
        if "sqlite" in url:
            self.useAsync = False
            self.engine = self.createEngine(url)
            self.session = self.createSession(self.engine)
            BasePO.query = self.session.query_property()
        else:  # AsyncSession
            self.engine = self.createAsyncEngine(url)
            self.async_session_factory = self._async_session_factory(self.engine)

        self.base_model_session_ctx = ContextVar("session")
        pass

    def __init__(self, config: dict, engineUrl: str = None) -> None:
        self.settings = self.default_settings.copy()
        if engineUrl == None:
            self.settings .update(config)
            engineUrl = "mysql+aiomysql://{}:{}@{}/{}".format(self.settings['DB_USER'], self.settings['DB_PASSWORD'], self.settings['DB_HOST'], self.settings['DB_NAME'])
        self.url = engineUrl
        self._createEngine(engineUrl)
        pass

    async def init_tables(self):
        if self.useAsync:
            async with self.engine.begin() as conn:
                # await conn.run_sync(BasePO.metadata.drop_a顶顶顶顶ll)
                await conn.run_sync(BasePO.metadata.create_all)
                await conn.commit()
            await self.engine.dispose()
        else:
            BasePO.metadata.create_all(bind=self.engine)

    def sync_init_tables(self):
        retryTime = 0
        while (True):
            try:
                if retryTime < 8:
                    retryTime += 1
                asyncio.run(self.init_tables())
                break
            except Exception as e:
                log.warn(f"同步数据表失败{e}!")
                log.info(f"{retryTime*5}s后重试...")
                time.sleep(retryTime*5)
