from dnalib.utils import TableUtils, Utils
from dnalib.log import *

class DDL:    
    """ """    
    def __init__(self, layer):
        self.layer = layer.strip().lower()   
        self.spark = Utils.spark_instance() 
        self.dbutils = Utils.dbutils()

class TableDDL(DDL):
    """ """
    def __init__(self, layer, table_name):
        DDL.__init__(self, layer)          
        self.table_name = table_name.strip().lower()
        self.table_path = Utils.lakehouse_path(self.layer, self.table_name)
        self.table_catalog_path = f"{self.layer}.{self.table_name}"

    def describe(self):
        raise NotImplementedError("Method describe() must be implemented.")    

    def create(self):
        raise NotImplementedError("Method create() must be implemented.")    

    def create_view(self):
        raise NotImplementedError("Method create_view() must be implemented.")    
        
    def drop(self):
        raise NotImplementedError("Method drop() must be implemented.")        

    def drop_view(self):
        raise NotImplementedError("Method drop_view() must be implemented.")      

    def exists(self):
        raise NotImplementedError("Method exists() must be implemented.")        

    def view_exists(self):
        raise NotImplementedError("Method view_exists() must be implemented.")        
