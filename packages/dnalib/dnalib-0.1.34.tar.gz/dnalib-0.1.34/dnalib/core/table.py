from dnalib.writer import BatchTableWriter
from dnalib.utils import TableUtils, Utils
from dnalib.log import *
from .ddl import TableDDL
from .field import Field

class Table(TableDDL):

    keywords = {
        'descricao': '- **Descrição**:',
        'sistema_origem': '- **Sistema Origem**:',
        'calendario': '- **Calendário de Disponibilização**:',
        'tecnologia': '- **Tecnologia Sistema Origem**:',
        'camada': '- **Camada de Dados**:',
        'peridiocidade': '- **Periodicidade de Atualização**:',
        'retencao': '- **Período de Retenção**:',
        'vertical': '- **Vertical**:',
        'dominio': '- **Domínio**:',
        'squad': '- **Squad Responsável**:',
        'categoria_portosdm': '- **Categoria e Grupo PortoSDM**:',
        'confidencialidade': '- **Classificação da Confidencialidade**:',
        'classificacao': '- **Classificação**:',
        'campos_anonimizados': '- **Campos Anonimizados**:',
        'deprecated': '- **Deprecated**:'
    }

    squad_keywords = {
        'gi': '- **GI - Gestor da Informação**:',
        'gdn': '- **GDN - Gestor de Negócio**:',
        'curador': '- **Curador**:',
        'custodiante': '- **Custodiante**:'
    }

    atlan_keywords =  {
        'descricao': '- **Descrição**:',
        'sistema_origem': '- **Sistema Origem**:',
        'calendario': '- **Calendário de Disponibilização**:',
        'tecnologia': '- **Tecnologia Sistema Origem**:',
        'camada': '- **Camada de Dados**:',
        'peridiocidade': '- **Periodicidade de Atualização**:',
        'retencao': '- **Período de Retenção**:',
        'vertical': '- **Vertical**:',
        'dominio': '- **Domínio**:',
        'gi': '- **GI - Gestor da Informação**:',
        'gdn': '- **GDN - Gestor de Negócio**:',
        'curador': '- **Curador**:',
        'custodiante': '- **Custodiante**:',
        'squad': '- **Squad Responsável**:',
        'categoria_portosdm': '- **Categoria e Grupo PortoSDM**:',
        'confidencialidade': '- **Classificação da Confidencialidade**:',
        'classificacao': '- **Classificação**:',
        'campos_anonimizados': '- **Campos Anonimizados**:',
        'deprecated': '- **Deprecated**:'
    }

    atlan_non_required_keywords = ['campos_anonimizados', 'deprecated']

    def __init__(self, 
                 layer, 
                 table_name, 
                 schema=None,
                 yml={}, 
                 partition_fields=[],    
                 anonimized_fields=[],                 
                 tbl_properties={},
                 comment={}, 
                 comment_squad={},          
                 fields={},                 
                 replace=False):
        TableDDL.__init__(self, layer, table_name)                            
        self.schema = schema
        self.yml = yml
        if isinstance(self.yml, str):
            self.yml = Utils.safe_load_and_parse_yml(yml)
        self.partition_fields = self.yml.get("partition_fields", partition_fields)  
        self.anonimized_fields = self.yml.get("anonimized_fields", anonimized_fields)    
        self.tbl_properties = self.yml.get("tbl_properties", tbl_properties)  
        self.comment = self.yml.get("comment", comment)    
        self.comment_squad = self.yml.get("comment_squad", comment_squad)    
        self.fields = self.yml.get("fields", fields)                  
        self.fields_metadata = []
        self.fields_catalog_information = None    
        self.replace = replace     
        self.comment_complete = {}
        self.parsed_table = ""
        self.parsed_view = ""
        self.sql_parsed_comment = ""
        self.sql_fields_metadata = "" 
        self.sql_tbl_properties = "" 
        self.sql_partition_fields = ""    
        self.sql_parsed_comment = "" 
        self.last_operation_metrics = {}

    # validation methods (for advanced tables purpores)
    def validate_comment_complete(self):
        """ 
            Método que valida se os comentários estão seguindo o padrão exigido pelo Atlan, o conteúdo não é validado, apenas a estrutura.
        """
        # parse comment complete structure
        self.parse_comment_complete()
        # validate if it has all atlan keywords
        diff_atlan_keywords = set(self.atlan_keywords.keys()) - set(self.comment_complete.keys())
        # if there is some difference, then some keywords were not informed
        if len(diff_atlan_keywords) > 0:
            log(__name__).error(f"You must inform all comment keywords: {diff_atlan_keywords}")
            raise Exception(f"You must inform all comment keywords: {diff_atlan_keywords}")
        # now we validate all values except anonimized fields and deprecated (they are not required)        
        required_comments = {key:value for key, value in self.comment_complete.items() if key not in Table.atlan_non_required_keywords}        
        # if some comment is empty we do not accept it
        if not all(required_comments.values()):
            empty_keys = [key for key, value in required_comments.items() if len(value) == 0]
            log(__name__).error(f"Those keys are empty and must be informed: {empty_keys}")
            raise Exception(f"Those keys are empty and must be informed: {empty_keys}")

    # parse methods
    def parse_last_operation_metrics(self):
        df_desc_history = TableUtils.describe_history(self.layer, self.table_name, limit=1)
        last_operation_metrics = df_desc_history.select("operationMetrics").collect()[0].asDict()
        self.last_operation_metrics = last_operation_metrics.get("operationMetrics")
        return self.last_operation_metrics

    def parse_parameters_from_table_comment(self):
        parsed_str_comment = TableUtils.table_comment(self.layer, self.table_name)
        list_comment_pattern_clean = []

        # in this solution we consider that each keyword is separated by '\n'
        for table_content in parsed_str_comment.split("\n"):
            # remove empty string
            comment_pattern_clean = table_content.strip()
            if comment_pattern_clean != '':
                list_comment_pattern_clean.append(comment_pattern_clean)

        comment = dict.fromkeys(self.keywords.keys(), "")
        comment_squad = dict.fromkeys(self.squad_keywords.keys(), "")

        # for each keyword we try to find its definition in the list of the table comment
        for table_comment_key in self.atlan_keywords:
            table_keyword = self.atlan_keywords[table_comment_key]    
            for comment_pattern_clean in list_comment_pattern_clean:                
                comment_idx = comment_pattern_clean.find(":")+1        
                if table_keyword.upper() in comment_pattern_clean.upper() and comment_idx < len(comment_pattern_clean):    
                    if table_comment_key in comment:        
                        comment[table_comment_key] = comment_pattern_clean[comment_idx:].strip()
                    else:
                        comment_squad[table_comment_key] = comment_pattern_clean[comment_idx:].strip()  

        # try to load anonimized fields from the table comment
        str_anonimized_fields = comment["campos_anonimizados"]       
        list_anonimized_fields = str_anonimized_fields.replace(".", "").replace(" e ", ",").split(",")  
        anonimized_fields = [] 
        for anonimized_field in list_anonimized_fields:
            anonimized_field_clean = anonimized_field.strip()
            if anonimized_field_clean != '':
                anonimized_fields.append(anonimized_field_clean.lower())

        return comment, comment_squad, anonimized_fields

    def parse_comment_complete(self):
        """ """
        if len(self.comment_complete) == 0:
            if len(self.yml) == 0 and self.exists():
                (comment, comment_squad, anonimized_fields) = self.parse_parameters_from_table_comment()
                if len(self.comment) == 0:  
                    self.comment = comment              
                if len(self.comment_squad) == 0:
                    self.comment_squad = comment_squad
                if len(self.anonimized_fields) == 0:
                    self.anonimized_fields = anonimized_fields
    
            # merge both dicts
            self.comment_complete = {**self.comment, **self.comment_squad}       

            # adjust non required parameters     
            self.comment_complete["campos_anonimizados"] = ", ".join(self.anonimized_fields)
            self.comment_complete.setdefault("deprecated", "")            
        return self.comment_complete

    def parse_fields_catalog_information(self):
        """ """
        if self.fields_catalog_information is None and self.exists():
            self.fields_catalog_information = self.spark.catalog.listColumns(f"{self.layer}.{self.table_name}")
        return self.fields_catalog_information    

    def parse_tbl_properties(self): 
        """ """                 
        if len(self.tbl_properties) == 0 and self.exists():
            df_tbl_properties = self.show_tbl_properties()
            self.tbl_properties = {tbl_property[0]:tbl_property[1] for tbl_property in df_tbl_properties.collect()}            
        return self.tbl_properties        

    def parse_partition_fields(self):
        """ """
        if len(self.partition_fields) == 0 and self.exists():            
            self.parse_fields_catalog_information()
            for field in self.fields_catalog_information:
                if field.isPartition:
                    self.partition_fields.append(field.name)
        return self.partition_fields

    def parse_fields_metadata(self):
        """ """                
        if len(self.fields_metadata) == 0:
            if len(self.fields) == 0 and self.exists():                                                    
                self.parse_fields_catalog_information()
                for field in self.fields_catalog_information:
                    self.fields_metadata.append(Field(field.name, field.description, field.dataType, field.nullable))
            else:                
                if self.schema != None:                                    
                    for field in self.schema:     
                        field_params = self.fields.get(field.name, [])
                        # comment can only comes for yml (currently)
                        field_comment = (field_params[0:1] or [field.metadata.get("comment", None)])[0]                                                  
                        # if field comes from yml, we ignore datatype of schema, because it can be a parameter to cast data
                        field_type = (field_params[1:2] or [None])[0] or field.dataType.simpleString()
                        # we only consider nullable from yml if it is True, otherwise the value is keep from schema
                        field_is_nullable = (field_params[2:3] or [None])[0] or field.nullable
                        # format can only comes from yml
                        field_format = (field_params[3:4] or [None])[0]
                        self.fields_metadata.append(Field(field.name, field_comment, field_type, field_is_nullable, field_format))        
                else:
                    for field_name, field_params in self.fields.items():                             
                        self.fields_metadata.append(Field(field_name, *field_params))        
        return self.fields_metadata
    
    def table_comment_to_sql(self):
        """ """
        self.parse_comment_complete()
        # parameters "campos_anonimizados" and "deprecated" are not required
        if len(self.comment_complete) > 2:
            list_of_comments = [f"{self.atlan_keywords[key]} {TableUtils.format_comment_content(self.comment_complete[key])}" for key in self.comment_complete]
            self.sql_parsed_comment = "\n".join(list_of_comments)                        
        return self.sql_parsed_comment

    def fields_metadata_to_sql(self):
        """ """
        self.parse_fields_metadata()
        if len(self.fields_metadata) > 0:            
            self.sql_fields_metadata = str(self.fields_metadata)[1:-1]
        return self.sql_fields_metadata

    def tbl_properties_to_sql(self):
        """ """
        self.parse_tbl_properties()
        if len(self.tbl_properties) > 0:
            tbl_properties_content = ", ".join([f"{key}='{value}'" for key, value in self.tbl_properties.items()])            
            self.sql_tbl_properties = f"TBLPROPERTIES ({tbl_properties_content})"
        return self.sql_tbl_properties
    
    def partition_fields_to_sql(self):
        """ """
        self.parse_partition_fields()
        if len(self.partition_fields) > 0:            
            partition_fields_content = str(self.partition_fields)[1:-1]
            self.sql_partition_fields = f"PARTITIONED BY ({partition_fields_content})"
        return self.sql_partition_fields

    def describe(self):        
        return TableUtils.describe_table(self.layer, self.table_name).display()

    def drop(self):
        return TableUtils.drop_table(self.layer, self.table_name)
    
    def exists(self):
        return TableUtils.table_exists(self.layer, self.table_name)
    
    def view_exists(self):
        return TableUtils.view_exists(self.layer, f"{self.table_name}_vw")
    
    def show_tbl_properties(self):
        if self.exists():
            return self.spark.sql(f"SHOW TBLPROPERTIES {self.layer}.{self.table_name}")
    
    def truncate(self):
        if self.exists():
            log(__name__).info(f"Truncating table {self.layer}.{self.table_name}.")
            return self.spark.sql(f"TRUNCATE TABLE {self.layer}.{self.table_name}")

    def parse(self):
        # generate template for create table
        self.parsed_table = """
            CREATE OR REPLACE TABLE {}.{} (
                {}
            )
            USING delta
            {}
            COMMENT "{}"
            {}
            LOCATION '{}'
        """.format(self.layer, self.table_name, self.fields_metadata_to_sql(), self.tbl_properties_to_sql(), self.table_comment_to_sql() , self.partition_fields_to_sql(), self.table_path)
        return self.parsed_table    
    
    def parse_view(self):        
        self.parse_fields_metadata()
        list_of_fields = []
        for field in self.fields_metadata:
            list_of_fields.append(field.hash_sql() if field.field_name in self.anonimized_fields else field.field_name)
        # generate template for create view
        self.parsed_view = """
            CREATE OR REPLACE VIEW {}.{}_vw (
                {}
            ) 
            COMMENT "{}"
            AS
            SELECT {} FROM {}.{}
        """.format(self.layer, self.table_name, self.fields_metadata_to_sql(), self.table_comment_to_sql(), ", ".join(list_of_fields), self.layer, self.table_name)
        return self.parsed_view
    
    def create(self):
        if not self.exists() or self.replace:                 
            ## generate final create table template            
            self.spark.sql(self.parse())                                            
            # mark table has been created or replaced by class
            self.has_created_table = True    
        else:
            log(__name__).warning(f"The table already exists, so nothing will be done.")
        return self
    
    def create_view(self):
        if not self.view_exists() or self.replace or self.has_created_table:
            ## generate final create view template            
            self.spark.sql(self.parse_view())                                            
            # mark table has been created or replaced by class            
        else:
            log(__name__).warning(f"The view already exists, so nothing will be done.")
        return self

    # alter methods
    def add_tbl_properties(self, tbl_properties):
        # armazenando o tbl_properties caso ele exista
        current_tbl_properties = self.tbl_properties 
        # setando temporariamente para usar o método interno de conversão
        self.tbl_properties = tbl_properties
        # rodando o alter table
        self.spark.sql("""
            ALTER TABLE {}.{} SET {}
        """.format(self.layer, self.table_name, self.tbl_properties_to_sql()))        
        # retornando as propriedades anteriores (se houvessem)
        self.tbl_properties = current_tbl_properties

    # remove tbl properties
    def remove_tbl_properties(self, list_of_tbl_properties_keys):        
        # rodando o alter table
        self.spark.sql("""
            ALTER TABLE {}.{} UNSET TBLPROPERTIES({})
        """.format(self.layer, self.table_name, str(list_of_tbl_properties_keys)[1:-1]))                
    
class BronzeTable(Table):

    layer = "bronze"

    def __init__(self,                  
                 table_name,
                 schema=None, 
                 yml={},    
                 partition_fields=[],       
                 anonimized_fields=[],  
                 tbl_properties={},                                                                      
                 comment={}, 
                 comment_squad={},  
                 fields={}):
        Table.__init__(self, self.layer, table_name, schema, yml, partition_fields, anonimized_fields, tbl_properties, comment, comment_squad, fields)          

class SilverTable(Table):

    layer = "silver"

    def __init__(self,                  
                 table_name, 
                 schema=None,
                 yml={}, 
                 partition_fields=[],   
                 anonimized_fields=[], 
                 tbl_properties={},
                 comment={}, 
                 comment_squad={},                                          
                 fields={}):
        Table.__init__(self, self.layer, table_name, schema, yml, partition_fields, anonimized_fields, tbl_properties, comment, comment_squad, fields)          

class GoldTable(Table,
                BatchTableWriter):

    layer = "gold"

    def __init__(self,                  
                 table_name, 
                 schema=None,
                 yml={}, 
                 partition_fields=[],    
                 anonimized_fields=[],                 
                 tbl_properties={},
                 comment={}, 
                 comment_squad={},          
                 fields={}):
        Table.__init__(self, self.layer, table_name, schema, yml, partition_fields, anonimized_fields, tbl_properties, comment, comment_squad, fields)          
        BatchTableWriter.__init__(self, self.layer, table_name)
            
