
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func,text
from sqlalchemy.future import select
from typing import TypeVar,Tuple,List,Dict,Any,Union,Iterator

from sqlalchemy.orm import QueryPropertyDescriptor,joinedload,subqueryload,contains_eager
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.engine.row import  Row

from  sqlalchemy.engine.result import ScalarResult,ChunkedIteratorResult
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql import Select
from .db_filter import absFilterItems,Page_param
from .po import BasePO
from .db_utils import db_tools
 
#from sqlalchemy.orm import selectinload # 紧急装载器 在该表主键又外键的基础上使用 select(UserTable).options(selectinload(UserTable.LoginLog))
 
from co6co.utils import log 


class DbOperations:
	# 实体类存在字段
	"""
	一些用法
	https://www.cnblogs.com/gcxblogs/p/14979274.html#subquery
	"""

	def __init__(self,db_session:AsyncSession) -> None:
		self.db_session = db_session 
		pass
	def _createQuery(self,poType:TypeVar):
		"""
		对没有 query 的 PO 增加 query 对象
		"""
		if not  hasattr(poType,"query") or isinstance(poType.query,Query): 
			query=self.db_session.query_property()  
			poType.query=query  
		 
	
	async def _get_one(self, select:select, selectField:bool=True):
		"""
		获取一行数据
		存在多,返回第一行
		为None 返回None
		存在多列：返回 Row
		""" 
		try: 
			data=await self.db_session.execute(select)
			if selectField:
				#row=data.one_or_none() # 没有返回None， 多行 异常Multiple rows were found when one or none was required
				row=data.fetchone() 	# 没有返回None， 多行，选一行给你
				if row==None:return row 
				return dict(zip(row._fields,row)) 
			else:
				row:Row=data.fetchone()   
				if row==None:return row 
				if len(row)==1:return row[0]
				else:return row # 返回后面这个不好使用 [{row._fields[i]:row[i]} for i in range(0,len(row))]
		except Exception as e:
			log.warn(f"在未找到!\terror:{e}")
			return None  
		
	async def _get_scalar(self ,select:select)->Any:
		data=await self.db_session.execute(select)
		return data.scalar()
	 
	async def _get_tuple(self ,select:select)-> List[dict]:  
		#sqlalchemy.engine.result.ChunkedIteratorResult
		data=await self.db_session.execute(select) 
		return [dict(zip(a._fields,a))  for a in  data]

	async def _get_list(self, select:select,remove_instance_state:bool=True)-> List[dict]|List[TypeVar]:  
		data=await self.db_session.execute(select) 
		if remove_instance_state:
			return db_tools.remove_db_instance_state(data.scalars().fetchall())  
		else:
			return data.scalars().fetchall() 
	
	async def get_one(self,selectColumnOrPo:TypeVar|Tuple[InstrumentedAttribute],*filters:ColumnElement[bool])->Any|None:
		"""
		获取一条数据
		返回 dict 或者 PO 实体
		"""
		'''result = await self.db_session.execute(text('select version()')) #通过conn对象就可对DB进行操作​ 
		data=result.fetchone() '''
		isTule,sml=self.create_select(selectColumnOrPo,*filters)
		return  await self._get_one(sml,isTule) 

	async def get_one_by_pk(self,po:TypeVar,pk:Union[Any, Tuple[Any, ...]]):
		"""
		通过 主键 获取实体
		"""
		try:
			one=await self.db_session.get_one(po,ident=pk)
			return one
		except Exception as e:
			log.warn(f"在{po},查找：pk:{pk} 未找到!\terror:{e}")
			return None
	 
	def create_select(self,selectColumnOrPo:Tuple[InstrumentedAttribute]|TypeVar,*filters:ColumnElement[bool] ) ->  Tuple[bool,Select[Any]]  :
		isTule= type(selectColumnOrPo)==tuple or type(selectColumnOrPo)==list  
		if isTule:
			sml=select(*selectColumnOrPo)  .filter(and_(*filters))
		else:
			# {type(selectColumnOrPo)} == sqlalchemy.orm.decl_api.DeclarativeMeta 
			po:TypeVar=selectColumnOrPo
			sml=select(po).filter(and_(*filters))
		return isTule,sml 
	
	def join(self,select:Select[Any], tarGet:TypeVar ,*filters:ColumnElement[bool] ) ->   Select[Any]:
		"""
		join , 没进行充分测试 谨慎使用
		"""
		sml=select.join(tarGet,and_(*filters)) 
		return sml
	

	async def _create_paged_select(self,filterItem:absFilterItems, selectColumnOrPo:Tuple[InstrumentedAttribute]|TypeVar=None,  allow_paged:bool=True, allow_order:bool=True)-> Tuple[bool,select] :
		"""
		创建 Column select
		"""
		filters=filterItem.filter()  
		#* selectColumn 不会为 None
		if selectColumnOrPo==None:selectColumnOrPo=filterItem.po_type 
		isTule,sml = self.create_select(selectColumnOrPo,*filters)  
		
		sml:Select[Any]=sml 
		if allow_paged:
			limit=filterItem.limit
			offset=filterItem.offset
			sml=sml.offset(offset).limit(limit)
		if allow_order:
			orderBy=filterItem.getOrderBy()
			sml=sml.order_by(*orderBy)
		return isTule,sml
	
	async def text(self,text:text)->dict:
		"""
		执行文本sql,
		返回: dict
		"""
		data=await self.db_session.execute(select(text))  
		return [dict(zip(a._fields,a))  for a in  data] 
	
	async def get_list(self,selectColumnOrPo:Tuple[InstrumentedAttribute]|TypeVar, *filters:ColumnElement[bool],remove_instance_state:bool=True): 
		isTule,sml=self.create_select(selectColumnOrPo,*filters)
		if isTule:return await self._get_tuple(sml)
		return await self._get_list(sml,remove_instance_state)
	
	async def count(self,*filters:ColumnElement[bool],column:InstrumentedAttribute="*" )->int:
		return await self._get_scalar(select(func.count(column)).filter(and_(*filters))) 
	
	async def exist(self,*filters:ColumnElement[bool],column:InstrumentedAttribute="*" )->bool:
		return await self.count(*filters,column=column)>0
	
	def add(self,instance: object, _warn: bool = True):
		self.db_session.add(instance,_warn)
	def add_all(self,instances: Iterator[object]):
		self.db_session.add_all(instances)

	async def delete(self,instance: object):
		await self.db_session.delete(instance)

	async def commit(self):
		await self.db_session.commit()
	async def rollback(self):
		await self.db_session.rollback()
	async def close(self):
		await self.db_session.close()

	
	 

    
	async def query_joined(self,poType:TypeVar, joinArr:Tuple[InstrumentedAttribute], *filters:ColumnElement[bool],param:Page_param=None,orderby: List[InstrumentedAttribute]=None):
		"""
		joinedload ==查询==> LEFT OUTER JOIN 
		不应该使用
		"""  
		self._createQuery(poType) 
		query=poType.query
		if len (joinArr)>0:
			query.options(joinedload(*joinArr)) 
		if  len (filters)>0:			
			query.filter(and_(*filters))
		if param !=None: 
			limit=param.limit
			offset=param.offset
			query.limit(limit).offset(offset)
		return (query.all()) 
	async def query_subquery(self,poType:TypeVar, joinArr:Tuple[InstrumentedAttribute], *filters:ColumnElement[bool],param:Page_param=None,orderby: List[InstrumentedAttribute]=None):
		"""
		先查询 users, 在 select * from (user) u join address on u.u_id == address.user_id
  		不应该使用
		"""  
		self._createQuery(poType) 
		query=poType.query
		if len (joinArr)>0:
			query.options(subqueryload(*joinArr)) 
		if  len (filters)>0:			
			query.filter(and_(*filters))
		if param !=None: 
			limit=param.limit
			offset=param.offset
			query.limit(limit).offset(offset)
		return (query.all()) 
	async def query_eager(self,poType:TypeVar, joinArr:Tuple[InstrumentedAttribute], *filters:ColumnElement[bool],param:Page_param=None,orderby: List[InstrumentedAttribute]=None):
		"""
		数据做笛卡儿积 ，程序为每个元素间应用连接条件进行解析
  		不应该使用
		"""  
		self._createQuery(poType) 
		query=poType.query
		if len (joinArr)>0:
			query.options(contains_eager(*joinArr)) 
		if  len (filters)>0:			
			query.filter(and_(*filters))
		if param !=None: 
			limit=param.limit
			offset=param.offset
			query.limit(limit).offset(offset)
		return (query.all()) 
	async def query_join_eager(self,poType:TypeVar, joinArr:Tuple[InstrumentedAttribute], *filters:ColumnElement[bool],param:Page_param=None,orderby: List[InstrumentedAttribute]=None):
		"""
		内连接，删除空
  		不应该使用
		"""  
		self._createQuery(poType) 
		query=poType.query
		if len (joinArr)>0:
			query.join(*joinArr)
			query.options(contains_eager(*joinArr)) 
		if  len (filters)>0:			
			query.filter(and_(*filters))
		if param !=None: 
			limit=param.limit
			offset=param.offset
			query.limit(limit).offset(offset)
		return (query.all()) 
	
class DbPagedOperations(DbOperations): 
	def __init__(self, db_session:AsyncSession,filter_items:absFilterItems):
		super().__init__(db_session)
		self.filter_items=filter_items  
	
	async def get_count(self,field:InstrumentedAttribute="*" )->int:
		"""
		根据 absFilterItems 获取符合条件的条数
		"""
		filters=self.filter_items.filter()
		return await self.count(*filters,field)
		#return await self._get_scalar(select(func.count(field)).filter(and_(*filters)))
		'''
		execute =await self.db_session.execute(select(func.count(field)).filter(and_(*filters)))  
		total= execute.scalar()   '''
		
		'''from co6co.utils import log
		#当选取整个对象的时候，都要用 scalars 方法，否则返回的是一个包含一个对象的 tuple 
		bts=await self.db_session.execute(select(ProcessPO.id,ProcessPO.boatName,ProcessPO.flowStatus).filter(and_(*filters)).limit(3))
	 
		log.succ(f"-----{type(bts)}\n{dir(bts)}") 
		for b in bts.fetchall():
			print(b)  

		filters=self.filter_items.filter( )
		orderBy=self.filter_items.getOrderBy() 
		data=await self.db_session.execute(select(ProcessPO).filter(and_(*filters)).offset(self.filter_items. get_db_page_index()).limit(3).order_by(*orderBy))
		log.succ(f"-----{type(data)}\n{dir(data)}")
		for b in data:
			print(b.tuple)  

		one=await self.db_session.get_one(ProcessPO,ident=2884) 
		print(one) ''' 
		return total
	
	async def get_paged (self ,selectColumnOrPo:Tuple[InstrumentedAttribute]|TypeVar=None,remove_instance_state:bool=True)-> List[dict]:
		"""
		selectColumn:  实体对象或者 filed
		返回列表
		"""
		isTule,sml=await self._create_paged_select(self.filter_items,selectColumnOrPo)
		if isTule:return await  self._get_tuple(sml)
		return await self._get_list(sml,remove_instance_state)