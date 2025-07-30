
from abc import ABC, abstractmethod 
from .page_param import Page_param
from typing import TypeVar,Tuple,List,Dict,Any,Union,Iterator
from sqlalchemy .orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy import func,or_,and_,Select  

class absFilterItems(ABC, Page_param): 
	"""
	抽象过滤器
	配合 DbOperations 使用
	"""
	listSelectFields: List[InstrumentedAttribute]=None# 使用该数据 dictor
	po_type:TypeVar=None
	def __init__(self,po:TypeVar) -> None:
		super().__init__() 

		self.po_type=po # 与排序相关
		 
		pass

	@property
	def offset(self):
		return self.get_db_page_index()*self.pageSize
	@property
	def limit(self):
		return self.pageSize
	

	#@abstractclassmethod 
	@abstractmethod
	def filter(self)->List[ColumnElement[bool]]:
		raise NotADirectoryError("Can't instantiate abstract clas") 
	
	def _getOrderby(self)->List[Dict[str,str]]:
		"""
		orderBy:id,name
		order: asc,desc
		从字符串转 [{"id":"asc"},{"name","desc"}]
		"""
		if self.orderBy and  self.order:
			by=self.orderBy.split(",")
			order=self.order.split(",")
			if len(by)==len(order):
				return [{b:o} for b in by for o in order if b and o]
			else:
				return [{b:order[0]} for b in by if b ]
		elif self.orderBy:
			by=self.orderBy.split(",")
			return [{b:"asc"} for b in by if b ]
		return [] 
	 
	@abstractmethod
	def getDefaultOrderBy(self)->Tuple[InstrumentedAttribute]:
		raise NotADirectoryError("Can't instantiate abstract clas") 
	 
	def getOrderBy(self)->List[InstrumentedAttribute]:
		""" 
		获取排序规则
		
		"""
		orderList= self._getOrderby()
		if len(orderList)==0: return self.getDefaultOrderBy()
		# () 获取的结果不能重复 取*
        # []  获取的结果能重复 取* 
		else: return [ self. po_type.__dict__[key].desc() if it[key] and it[key].lower()=="desc" else  self. po_type.__dict__[key].asc() for it in orderList for key in it.keys() if key in self.po_type.__dict__]
	def getOrderBy_Fields(self)->List[InstrumentedAttribute]:
		""" 
		获取排序规则 2 由 select 字段 排序
		//todo 功能未实现
		"""
		orderList= self._getOrderby()
		if len(orderList)==0: return self.getDefaultOrderBy() 
		else: return [ self. po_type.__dict__[key].desc() if it[key] and it[key].lower()=="desc" else  self. po_type.__dict__[key].asc() for it in orderList for key in it.keys() if key in self.po_type.__dict__]
	
	def checkFieldValue(self,fielValue:Any)->bool:
		if type(fielValue) == str and fielValue:return True
		if type(fielValue) == int :return True
		if type(fielValue) == bool :return True
		return False
	 
	def create_List_select(self):
		if self.listSelectFields !=None and len(self.listSelectFields)>0: 
			select=(
				Select(*self.listSelectFields)#.join(device.deviceCategoryPO,isouter=True)
				.filter(and_(*self.filter()))  
			)
		else :
			select=(
				Select(self.po_type)#.join(device.deviceCategoryPO,isouter=True)
				.filter(and_(*self.filter()))  
			) 
		return select
	
	@property
	def list_select(self,useListFiled=False):
		if useListFiled:
			return self.create_List_select().limit(self.limit).offset(self.offset).order_by(*self.getOrderBy_Fields())
		return self.create_List_select().limit(self.limit).offset(self.offset).order_by(*self.getOrderBy())
	@property
	def count_select(self): 
		return Select( func.count( )).select_from(self.create_List_select())
