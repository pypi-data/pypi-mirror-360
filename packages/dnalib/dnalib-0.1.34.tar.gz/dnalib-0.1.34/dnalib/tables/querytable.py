from dnalib.utils import Utils

def compile_query(query_string, *args, **kwargs):
    """
        Uma função python para compilar as queries usando o método format.
        
        args = [arg_0, arg_1, ..., arg_n]
        kwargs_flatten = [key_0, value_0, key_1, value_1 ..., key_n, value_n]
        kwargs = {key_0:value_0, key_1:value_1 ..., key_n:value_n}
        kwargs_keys = {id_key_0:key_0, id_key_1:key_1 ..., id_key_n:key_n}

        format(arg_0, arg_1, ..., arg_n, key_0, value_0, 
               key_1, value_1 ..., key_n, value_n, 
               {key_0:value_0, key_1:value_1 ..., key_n:value_n,
               id_key_0:key_0, id_key_1:key_1 ..., id_key_n:key_n})

        Usando args:                    
            compile_query("select * from {0}.{1}", "bronze", "pln_ge_pessoa")
                "select * from bronze.pln_ge_pessoa"
        
        Usando kwargs:
            compile_query("select * from {layer}.{table_name}", layer="bronze", table_name="pln_ge_pessoa")
                "select * from bronze.pln_ge_pessoa"

        Usando kwargs sem especificar uma das chaves (usando a posição como em args):
            compile_query("select * from {layer}.{table_name} where {4} = '{5}'", layer="bronze", table_name="pln_ge_pessoa", cpf="12345")
                "select * from bronze.pln_ge_pessoa where cpf = '12345'"

        Usando kwargs acessando a chave e valor dentro da query (a key sempre fica com id_ na frente)
            compile_query("select * from {layer}.{table_name} where {id_cota} = '{cota}'", layer="bronze", table_name="pln_ge_pessoa", cota="134567")
    """              
    # we flat the kwargs to a list with consecutive [key, value, ...]
    kwargs_flatten = [kv_flat for kv in zip(kwargs.keys(), kwargs.values()) for kv_flat in kv]   
    # we create a dictionary with the id_key as key and the key as value
    kwargs_keys = {f"id_{key}" : key for key in kwargs.keys()}
    # merge both dictionaries
    kwargs_full = {**kwargs, **kwargs_keys}
    # finally we compile the query according to a simple logic
    compiled_query = query_string.format(*args, *kwargs_flatten, **kwargs_full)                                               
    return compiled_query

def query(query_string, *args, **kwargs):
    """
        Um decorator para compilar queries em classes ou métodos no formato do spark sql e retornar um dataframe com o resultado.
    """
    def inner(func):          
        def wrapper(*args, **kwargs):                 
            args_idx = 0
            # test if the first parameter is the "self"
            if len(args) > 0 and hasattr(args[0], '__dict__'):                                
                args_idx = 1            
            compiled_query = compile_query(query_string, *args[args_idx:], **kwargs)                                                                
            return func(*args[:args_idx], Utils.spark_instance().sql(compiled_query))
        return wrapper
    return inner

class QueryTable:   

    def __init__(self, query_view_name="view_query_table"):
        self.query_view_name = query_view_name
        self.result_df = None
    
    @query(""" 
        select {fields}
        from {source_table} where {field}::string="{0}" 
    """)
    def _find_by_single_parameter(self, result_df):
        self.result_df = result_df
        self.result_df.createOrReplaceTempView(self.query_view_name)
        return self

    @query(""" 
        select {fields} 
        from {source_table} where {first_field}::string="{0}" and {second_field}::string="{1}" 
    """)    
    def _find_by_first_and_second_parameter(self, result_df):
        self.result_df = result_df
        self.result_df.createOrReplaceTempView(self.query_view_name)
        return self 

    @query(""" 
        select {fields} 
        from {source_table} where {first_field}::string="{0}" or {second_field}::string="{1}" 
    """)
    def _find_by_first_or_second_parameter(self, result_df):
        self.result_df = result_df
        self.result_df.createOrReplaceTempView(self.query_view_name)
        return self 

    @query(""" 
        select {fields}
        from {source_table} where {json_field}:{6}::string="{7}" 
    """)
    def _find_by_json_parameter(self, result_df):
        self.result_df = result_df
        self.result_df.createOrReplaceTempView(self.query_view_name)
        return self

    @query(""" 
        select {fields} from {source_table} 
        where {in_field} in (		    
            select {in_field} from {source_table}	
            where {json_field}:{11}::string="{12}" 
        )
    """)
    def _find_by_json_parameter_in_field(self, result_df):
        self.result_df = result_df
        self.result_df.createOrReplaceTempView(self.query_view_name)
        return self
    