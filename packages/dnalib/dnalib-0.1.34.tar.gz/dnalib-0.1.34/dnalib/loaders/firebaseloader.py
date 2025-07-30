from pyspark.sql.functions import col, to_json
from dnalib.utils import Utils
from .loader import Loader
from dnalib.log import *
from firebase_admin import credentials, firestore, initialize_app
from google.api_core.retry import Retry
from tempfile import NamedTemporaryFile
import json

class FireBaseApp: 
    """
        A classe FireBaseApp implementa um singleton para manter uma instancia única de execução do cliente do Firestore.
    """
    _instance = None

    def __init__(self, service_account_data, db_name=None):
        self.service_account_data = service_account_data
        self.db_name = db_name
        self.db = self.authenticate_db()
        
    def authenticate_db(self):
        with NamedTemporaryFile('w+') as fp:
            fp.write(self.service_account_data)
            fp.seek(0)
            cred = credentials.Certificate(fp.name)
            initialize_app(cred)
            return firestore.client(database_id=self.db_name)
        return None
    
    @classmethod
    def instance(cls, service_account_data, db_name=None):
        if cls._instance is None:
            cls._instance = cls(service_account_data, db_name)
        return cls._instance

class FireBaseLoader(Loader):
    """
       A classe FireBaseLoader encapsula o processo de carregamento de dados do Firestore para um dataframe Spark. 
    """
    def __init__(self, 
                 source_path,       
                 loader_type,           
                 collection_name, 
                 order_by='__name__', 
                 page_size=1000,
                 init_load=None,
                 end_load=None,
                 flat_json=True,
                 db_name=None,
                 spark_num_partitions=None):
        super().__init__(source_path, loader_type)
        self.collection_name = collection_name
        self.order_by = order_by
        self.page_size = page_size
        self.init_load = init_load
        self.end_load = end_load
        self.flat_json = flat_json
        self.db_name = db_name
        self.spark_num_partitions = spark_num_partitions
        self.service_account_data = Utils.key_vault_value(source_path)   
        self.db = FireBaseApp.instance(self.service_account_data, self.db_name).db
        self.collection = self.load_collection()
        self.docs = []
        self.count = 0
        self.df_raw = None            

    def load_collection(self):
        """  """
        collection = self.db.collection(self.collection_name)
        if self.init_load:
            filter_init = firestore.FieldFilter(self.order_by, ">=", self.init_load)
            collection = collection.where(filter=filter_init)
        if self.end_load:
            filter_end = firestore.FieldFilter(self.order_by, "<=", self.end_load)
            collection = collection.where(filter=filter_end)
        return collection

    def iterate_documents(self):
        """  """
        cursor = None
        self.count = 0
        while True:
            docs = []  
            if cursor:
                docs = [snapshot for snapshot in self.collection.limit(self.page_size).order_by(self.order_by).start_after(cursor).stream(retry=Retry())]
            else:
                docs = [snapshot for snapshot in self.collection.limit(self.page_size).order_by(self.order_by).stream(retry=Retry())]
            self.count = self.count + len(docs)
            for doc in docs:
                # return doc to iterate  
                yield doc                
            print(f"Firebase loaded {self.count} documents.", end="\r")            
            if len(docs) == self.page_size:
                cursor = docs[self.page_size-1]
                continue
            break
    
    def load_incremental(self):
        """  """       
        for doc in self.iterate_documents():            
            self.docs.append(json.dumps(doc.to_dict(), default=str))
        log(__name__).info(f"Firebase loaded {self.count} documents.")
        # converts all documents to json string, make primitives string to avoid break schema
        if self.flat_json:
            par = Utils.spark_instance().sparkContext.parallelize(self.docs, self.spark_num_partitions)
            self.df_raw = Utils.spark_instance().read.json(par, primitivesAsString=True) 
            for field in self.df_raw.schema:
                if field.dataType.simpleString() != "string":
                    self.df_raw = self.df_raw.withColumn(field.name, to_json(col(field.name)))   
        else:            
            par = Utils.spark_instance().sparkContext.parallelize([[doc] for doc in self.docs], self.spark_num_partitions)
            self.df_raw = Utils.spark_instance().createDataFrame(par, "json_document: string")             
        return self.df_raw
    
    def load_full(self):
        """  """
        return self.load_incremental()
    