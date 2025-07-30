

from typing import TypeVar, Tuple, List, Dict, Any, Union, Iterator, Callable
from sqlalchemy.engine.row import Row, RowMapping
from .po import BasePO
from co6co.utils import log

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, Update, Insert, Delete
from sqlalchemy.future import select
from sqlalchemy import and_
from sqlalchemy import func, text
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.engine.result import ChunkedIteratorResult
from sqlalchemy.engine.cursor import CursorResult

from .db_filter import absFilterItems


class db_tools:
    """
    数据转换工具
    1. 
    data=  exec.mappings().all() 
    result=[dict(zip( a.keys(),a._to_tuple_instance())) for a in  data] 

    2.
    [dict(zip(a._fields,a))  for a in  executeResult]
    """
    __po_has_field__: str = "_sa_instance_state"

    @staticmethod
    def remove_db_instance_state(poInstance_or_poList: Iterator | Any) -> List[Dict] | Dict:
        if hasattr(poInstance_or_poList, "__iter__"):
            result = [dict(filter(lambda k: k[0] != db_tools.__po_has_field__,
                           a1.__dict__.items())) for a1 in poInstance_or_poList]
            for r in result:
                for r1 in r:
                    value = r.get(r1)
                    if (isinstance(value, BasePO)):
                        dic = db_tools.remove_db_instance_state(value)
                        r.update({r1: dic})
            return result
        # and hasattr (poInstance_or_poList,"__dict__")
        elif hasattr(poInstance_or_poList, "__dict__"):
            return dict(filter(lambda k: k[0] != db_tools.__po_has_field__, poInstance_or_poList.__dict__.items()))
        else:
            return poInstance_or_poList

    @staticmethod
    def row2dict(row: Row) -> Dict:
        """
        xxxxPO.id.label("xxx_id") 为数据取别名
        出现重名覆盖
        """
        d: dict = {}
        for i in range(0, len(row)):
            c = row[i]
            if hasattr(c, db_tools.__po_has_field__):
                dc = db_tools.remove_db_instance_state(c)
                d.update(dc)
            else:
                key = row._fields[i]
                '''
                j=1 
                while key in d.keys():
                    key=f"{ row._fields[i]}_{str(j )}"
                    j+=1
                '''
                d.update({key: c})
        return d

    @staticmethod
    def one2Dict(fetchone: Row | RowMapping) -> Dict:
        """
        Row:        execute.fetchmany() | execute.fetchone()
        RowMapping: execute.mappings().fetchall()|execute.mappings().fetchone()  
        """
        if type(fetchone) == Row:
            return dict(zip(fetchone._fields, fetchone))
        elif type(fetchone) == RowMapping:
            return dict(fetchone)
        elif type(fetchone) == dict:
            return fetchone
        log.warn(f"未知类型：‘{type(fetchone)}’,直接返回")
        return fetchone

    @staticmethod
    def list2Dict(list: List[Row | RowMapping]) -> List[dict]:
        return [db_tools.one2Dict(a) for a in list]

    def mapping(executeResult: any) -> List[dict]:
        """
        不在使用
        """
        # sqlalchemy.engine.result.ChunkedIteratorResult
        return [dict(zip(a._fields, a)) for a in executeResult]

    async def execSelect(session: AsyncSession, select: Select, params: Dict | List | Tuple = None) -> int | None:
        """
        执行查询语句
        @return: int | None
        """
        exec = await session.execute(select, params)
        return exec.scalar()

    async def count(session: AsyncSession, *filters: ColumnElement[bool], column: InstrumentedAttribute = "*") -> int:
        """
        count
        """
        sql = select(func.count(column)).filter(and_(*filters))
        return await db_tools.execSelect(session, sql)

    async def exist(session: AsyncSession, *filters: ColumnElement[bool], column: InstrumentedAttribute = "*") -> bool:
        """
        exist
        """
        count = await db_tools.count(session, *filters, column=column)
        if count > 0:
            return True
        else:
            return False

    async def execForMappings(session: AsyncSession, select: Select, queryOne: bool = False, params: Dict | Tuple | List = None):
        """
        session: AsyncSession
        select:Select 

        return list
        """

        executer = await session.execute(select, params)
        if queryOne:
            result = executer.mappings().fetchone()
            return db_tools.one2Dict(result)
        else:
            result = executer.mappings().all()
            return db_tools.list2Dict(result)

    async def execForPos(session: AsyncSession, select: Select, remove_db_instance_state: bool = True, params: Dict | List | Tuple = None):
        """
        session: AsyncSession
        select:Select
        remove_db_instance_state: bool

        return list
        """

        exec: ChunkedIteratorResult = await session.execute(select, params)
        if remove_db_instance_state:
            return db_tools.remove_db_instance_state(exec.scalars().fetchall())
        else:
            return exec.scalars().fetchall()

    async def execForPo(session: AsyncSession, select: Select, remove_db_instance_state: bool = True, params: Dict | List | Tuple = None):
        """
        session: AsyncSession
        select:Select
        remove_db_instance_state: bool

        return PO|None
        """
        exec: ChunkedIteratorResult = await session.execute(select, params)
        # user: UserPO = result.scalar()
        data = exec.fetchone()
        # 返回的是元组
        one = None
        if data != None:
            one = data[0]
            if remove_db_instance_state:
                return db_tools.remove_db_instance_state(one)
            else:
                return one
        else:
            return None

    async def execSQL(session: AsyncSession, sql: Update | Insert | Delete, sqlParam: Dict | List | Tuple = None) -> int:
        """
        执行简单SQL语句
        """
        data: CursorResult = await session.execute(sql, sqlParam)
        return data.rowcount


'''
exec.fetchone() //None| (data,)
exec.mappings().fetchone()  // {'id': 1, 'userName': 'admin'} | {"userPO":PO}
exec..fetchone()    //(1, 'admin') || po
'''


class DbCallable:
    session: AsyncSession = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __call__(self, func: Callable[[AsyncSession], Any]):
        async with self.session, self.session.begin():
            if func != None:
                return await func(self.session)


class QueryOneCallable(DbCallable):
    async def __call__(self, select: Select, isPO: bool = True, param: Dict | List | Tuple = None):
        async def exec(session: AsyncSession):
            exec = await session.execute(select, param)
            if isPO:
                data = exec.fetchone()
                # 返回的是元组
                if data != None:
                    return data[0]
                else:
                    return None
            else:
                data = exec.mappings().fetchone()
                if data == None:
                    return None
                result = db_tools.one2Dict(data)
                return result
        return await super().__call__(exec)


class InsertCallable(DbCallable):
    async def __call__(self, *po: BasePO):
        async def exec(session: AsyncSession):
            try:
                session.add_all(po)
            except Exception as e:
                await session.rollback()
                log.warn("执行'InsertOneCallable'异常", e)
                raise
        return await super().__call__(exec)


class UpdateOneCallable(DbCallable):
    async def __call__(self, queryOneSelect: Select, editFn: Callable[[AsyncSession, Any], None | Any] = None, param: Dict | List | Tuple = None):
        """
        queryOneSelect: 查询语句
        editFn: (session,po)->Any|None   返回:None  ->回滚,
                                            :Any   -> 函数返回值
        """
        async def exec(session: AsyncSession):
            try:
                exec = await session.execute(queryOneSelect, param)
                data = exec.fetchone()
                # 返回的是元组
                one = None
                if data != None:
                    one = data[0]
                else:
                    one = None
                if editFn != None:
                    result = await editFn(session, one)
                    if result == None:
                        await session.rollback()
                    return result
            except Exception as e:
                await session.rollback()
                log.warn("执行'UpdateOneCallable'异常", e)
                raise

        return await super().__call__(exec)


class QueryListCallable(DbCallable):
    async def __call__(self, select: Select, isPO: bool = True, remove_db_instance=True, param: Dict | List | Tuple = None):
        async def exec(session: AsyncSession):
            if isPO:
                result = await db_tools.execForPos(session, select, remove_db_instance, params=param)
            else:
                result = await db_tools.execForMappings(session, select, params=param)
            return result
        # return await super(QueryListCallable,self).__call__(exec) #// 2.x 写法
        return await super().__call__(exec)


class QueryPagedCallable(DbCallable):
    async def __call__(self, countSelect: Select, select: Select, isPO: bool = True, remove_db_instance=True, param: Dict | List | Tuple = None) -> Tuple[int, List[dict]]:
        async def exec(session: AsyncSession):
            total = await db_tools.execSelect(session, countSelect, param)
            if isPO:
                result = await db_tools.execForPos(session, select, remove_db_instance, param)
            else:
                result = await db_tools.execForMappings(session, select, param)

            return total, result
        return await super().__call__(exec)


class QueryPagedByFilterCallable(QueryPagedCallable):
    async def __call__(self, filter: absFilterItems, isPO: bool = True, remove_db_instance=True, param: Dict | List | Tuple = None) -> Tuple[int, List[dict]]:
        return await super().__call__(filter.count_select, filter.list_select, isPO, remove_db_instance, param)
