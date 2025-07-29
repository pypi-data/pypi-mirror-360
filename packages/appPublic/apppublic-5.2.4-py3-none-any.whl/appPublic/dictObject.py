import json
from json import JSONEncoder
from inspect import ismethod, isfunction, isbuiltin, isabstract

def multiDict2Dict(md):
	ns = {}
	for k,v in md.items():
		ov = ns.get(k,None)
		if ov is None:
			ns[k] = v
		elif type(ov) == type([]):
			ov.append(v)
			ns[k] = ov
		else:
			ns[k] = [ov,v]
	return ns

class DictObjectEncoder(JSONEncoder):
	def default(self, o):
		return o._addon()

class DictObject(dict):
	def __getattr__(self, attr):
		"""
		实现点操作符访问字典中的键值对
		"""
		try:
			v = self.__DOitem(self[attr])
			self[attr] = v
			return v
		except KeyError:
			return None

	def has(self, key):
		try:
			v = super().__getitem__(key)
			return True
		except KeyError:
			return False

	def get_data_by_keys(self, keys):
		try:
			ks = keys.split('.', 1)
			if '[' not in ks[0]:
				d = getattr(self, ks[0])
				if len(ks) == 1:
					return d
				if isinstance(d, DictObject):
					return d.get_data_by_keys(ks[1])
				return None
			ks1 = ks[0].split('[', 1)
			k = ks1[0]
			idx = int(ks1[1].split(']',1)[0])
			d = getattr(self, k)[idx]
			if len(ks) == 1:
				return d
			if isinstance(d, DictObject):
				return d.get_data_by_keys(ks[1])
			return None
		except:
			return None
			
	def __getitem__(self, key):
		try:
			v = self.__DOitem(super().__getitem__(key))
			self[key] = v
			return v
		except KeyError:
			return None

	def __setattr__(self, attr, value):
		"""
		实现点操作符设置字典中的键值对
		"""
		self[attr] = value

	def get(self, k, defv=None):
		if self.has(k):
			return self[k]
		else:
			return defv

	def copy(self):
		return self.__DOitem(super().copy())

	@classmethod
	def isMe(self,name):
		return name == 'DictObject'

	def to_dict(self):
		return self

	def __DOArray(self,a):
		b = [ self.__DOitem(i) for i in a ]
		return b
	
	def __DOitem(self, i):
		if isinstance(i,DictObject):
			return i
		if isinstance(i,dict):
			i = {k:v for k,v in i.items() if isinstance(k,str)}
			try:
				d = DictObject(**i)
				return d
			except Exception as e:
				raise e
		if type(i) == type([]) or type(i) == type(()) :
			return self.__DOArray(i)
		return i

def dictObjectFactory(_klassName__,**kwargs):
	def findSubclass(_klassName__,klass):
		for k in klass.__subclasses__():
			if k.isMe(_klassName__):
				return k
			k1 = findSubclass(_klassName__,k)
			if k1 is not None:
				return k1
		return None
	try:
		if _klassName__=='DictObject':
			return DictObject(**kwargs)
		k = findSubclass(_klassName__,DictObject)
		if k is None:
			return DictObject(**kwargs)
		return k(**kwargs)
	except Exception as e:
		print("dictObjectFactory()",e,_klassName__)
		raise e

