import asyncio
import hashlib
from threading import Thread, Lock
import time
from typing import Callable
import subprocess
try:
    from pydantic import BaseModel
    from pymilvus import MilvusClient, AsyncMilvusClient
    from sentence_transformers import SentenceTransformer
    from torch import Tensor
except:
    subprocess.check_call(['pip','install', "pydantic", "pymilvus", "sentence-transformer"])
    from pydantic import BaseModel
    from pymilvus import MilvusClient, AsyncMilvusClient
    from sentence_transformers import SentenceTransformer
    from torch import Tensor


def getMD5(bt: bytes)->str:
    md5 = hashlib.md5()
    md5.update(bt)
    return md5.hexdigest()
    
class Milvuser:
    def __init__(self, url:str, model_name_or_path:str, default_col:str, default_vector_key:str, 
                 user: str = "", password: str = "", db_name: str = "", 
                 device:str='cpu'):
        self.client=None
        self.aclient=None
        self._lock = Lock()
        self.url = url
        self._get_model = lambda: SentenceTransformer(model_name_or_path, device=device)
        self.default_col = default_col
        self.default_vector_key=default_vector_key
        self._user = user
        self._pwd = password
        self._db_name = db_name
        self.model:SentenceTransformer = None
        self._func:Callable[[list[dict]], list[str]] = lambda dts: [data[self.default_vector_key] for data in dts]
    
    def init_model(self):
        self.model = self.model or self._get_model()
        
    def set_getText_func(self, func:Callable[[list[dict]], list[str]]):
        self._func = func
        
    def _getAClient(self):
        client = AsyncMilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
    
    def _getClient(self):
        client = MilvusClient(self.url, self._user, self._pwd, self._db_name)
        return client
    
    async def aclient_reset(self):
        if self.aclient: await self.aclient.close()
        self.aclient = self._getAClient()
            
    async def aclient_auto_reset(self, s=600):
        while True:
            await asyncio.sleep(s)
            await self.aclient.close()
            self.aclient = self._getAClient()
            
    def client_auto_reset(self, s=600):
        def temp():
            while True:
                time.sleep(s)
                with self._lock:
                    self.client.close()
                    self.client = self._getClient()
        Thread(target=temp, daemon=True).start()

    async def acreate_collection(self, dimension:int, col:str=None, id_type:str='int', primary_field_name='id', max_length=None, **kwargs):
        self.aclient = self.aclient or self._getAClient()
        return await self.aclient.create_collection(
                                    collection_name=col or self.default_col,
                                    primary_field_name=primary_field_name,
                                    dimension=dimension,  # 维度
                                    id_type = id_type,
                                    max_length=max_length,
                                    **kwargs
                                )
        
    def create_collection(self, dimension:int, col:str=None, id_type:str='int', primary_field_name='id', max_length=None, **kwargs):
        self.client = self.client or self._getClient()
        if self.client.has_collection(col or self.default_col): return None
        return self.client.create_collection(
                                collection_name=col or self.default_col,
                                primary_field_name=primary_field_name,
                                dimension=dimension,  # 维度
                                id_type = id_type,
                                max_length=max_length,
                                **kwargs
                            )
        
    def _getDatas(self, datas)->list[dict]:
        datas=list(datas)
        for i in range(len(datas)):
            if isinstance(datas[i], BaseModel):
                datas[i] = datas[i].model_dump(exclude_none=True)
        texts = self._func(datas)
        self.init_model()
        vcs = self.model.encode(texts)
        return [{**data, 'vector': vector} for data, vector in zip(datas, vcs)]
        
    async def aupdate_insert(self, *datas:dict|BaseModel, col:str=None)->dict:
        rs = self._getDatas(datas)
        self.aclient = self.aclient or self._getAClient()
        return await self.aclient.insert(col or self.default_col, rs)
    
    def update_insert(self, *datas:dict|BaseModel, col:str=None)->dict:
        rs = self._getDatas(datas)
        self.client = self.client or self._getClient()
        return self.client.insert(col or self.default_col, rs)
    
    async def asearch(self, *query:str|Tensor, min_similarity:float=0.5, kn:int=3, filter:str='', col:str=None, output_fields:list[str]=None)->list[dict]|list[list[dict]]:
        """
        向量相似度搜索, 默认余弦选相似度计算, 值与相似度成正比\n
        返回字段包含id、distance、output_fields中的字段
        """
        if isinstance(query[0], str):
            self.init_model()
            vc = self.model.encode(query)
        else:
            vc = list(query)
        self.aclient = self.aclient or self._getAClient()
        res = await self.aclient.search(col or self.default_col, vc, limit=kn, 
                                        output_fields=output_fields,
                                        filter=filter,
                                        # 相似度取值范围
                                        search_params={"params": {
                                                            "radius": min_similarity,
                                                        # "range_filter": 1.0 # =最大值限制, 因为精度问题相同文件的值可能微大于1.0
                                                            }
                                                        })
        datas = [[{**dt.pop('entity'), **dt} for dt in cres] for cres in res]
        return datas if len(query)>1 else datas[0]    
    
    def search(self, *query:str|Tensor, min_similarity:float=0.5, kn:int=3, filter:str='', col:str=None, output_fields:list[str]=None)->list[dict]|list[list[dict]]:
        """
        向量相似度搜索, 默认余弦选相似度计算, 值与相似度成正比\n
        返回字段包含id、distance、output_fields中的字段
        """
        if isinstance(query[0], str):
            self.init_model()
            vc = self.model.encode(query)
        else:
            vc = list(query)
        self.client = self.client or self._getClient()
        res = self.client.search(col or self.default_col, vc, limit=kn, 
                                output_fields=output_fields,
                                filter=filter,
                                # 相似度取值范围
                                search_params={"params": {
                                                    "radius": min_similarity,
                                                # "range_filter": 1.0 # =最大值限制, 因为精度问题相同文件的值可能微大于1.0
                                                    }
                                                })
        datas = [[{**dt.pop('entity'), **dt} for dt in cres] for cres in res]
        return datas if len(query)>1 else datas[0]

    async def aquery(self, filter:str='', limit:int=10, col:str=None, ids:list=None)-> list[dict]:
        self.aclient = self.aclient or self._getAClient()
        res = await self.aclient.query(col or self.default_col, filter=filter, limit=limit, ids=ids)
        return res
    
    def query(self, filter:str='', limit:int=10, col:str=None, ids:list=None)-> list[dict]:
        self.client = self.client or self._getClient()
        res = self.client.query(col or self.default_col, filter=filter, limit=limit, ids=ids)
        return res

    async def adelete(self, filter:str, ids:list=None, col:str = None)-> list[dict]:
        self.aclient = self.aclient or self._getAClient()
        res = await self.aclient.delete(col or self.default_col, filter=filter, ids=ids)
        return res
    
    def delete(self, filter:str, ids:list=None, col:str = None)-> list[dict]:
        self.client = self.client or self._getClient()
        res = self.client.delete(col or self.default_col, filter=filter, ids=ids)
        return res