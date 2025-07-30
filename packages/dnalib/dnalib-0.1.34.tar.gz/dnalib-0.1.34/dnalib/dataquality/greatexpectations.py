from great_expectations.dataset import SparkDFDataset
from great_expectations.dataset import MetaSparkDFDataset
from great_expectations.core.expectation_suite import ExpectationSuite 
from great_expectations.core.expectation_configuration import ExpectationConfiguration
from dnalib.utils import Utils
from pyspark.sql.functions import col

# Criando uma classe custom de Dataset, é uma implementação com maior 
# liberdade para adicionar expectations novos.
class GreatExpectations(SparkDFDataset):    

    """ 
        Exemplo de classe com expectations customizados para dataframes SQL do PySpark.
    """    
    default_suite_name = "ge_custom_validator"
    def __init__(self, df_or_query, **kwargs):           
        if isinstance(df_or_query, str):
            spark_df = Utils.spark_instance().sql(df_or_query)
        else:
            spark_df = df_or_query  
        SparkDFDataset.__init__(self, spark_df=spark_df, **kwargs)
        self.ge_suite = ExpectationSuite(self.default_suite_name)   
        self.ge_result = None     

    # Método que valida se os valores de uma coluna estão dentro de um conjunto (lista),
    # caso não esteja retorna em partial_unexpected_list (amostras das colunas definidas em keys_to_return)
    @MetaSparkDFDataset.expectation(["column", "value_set", "keys_to_return", "limit_return", "mostly"])
    def expect_column_values_to_be_in_set_given_keys_to_return(self, column, value_set, keys_to_return=[], limit_return=100, mostly=0.99, **kwargs):
        df_verify = self.spark_df.withColumn("__success", col(column).isin(value_set))
        partial_unexpected_list = df_verify.filter(col("__success") == False)      
        number_of_wrong = partial_unexpected_list.count()  
        rows_to_verify = df_verify.count()
        return {
            "success" : (number_of_wrong / rows_to_verify) >= mostly,
            "result" : {
                "partial_unexpected_list": partial_unexpected_list.select(keys_to_return).head(limit_return),
                "unexpected_count": number_of_wrong
            }
        }


    # Método que valida se o campo é um cpf ou cnpj válido (considerando apenas números,cpf de 11 e 6 digitos (miolo do cpf) e cnpj de 14 digitos)
    @MetaSparkDFDataset.expectation(["column", "mostly"])
    def expect_column_to_be_cpf_or_cnpj_number(self, column, mostly=0.99):
        return super().expect_column_values_to_match_regex_list(
            column=column,
            regex_list=['(^[0-9]{14}$)|(^[0-9]{11}$)|(^[0-9]{6}$)'],
            match_on='any',
            mostly=mostly 
        )
    
    # Método que valida se as colunas do dataframe seguem certos padrões de prefixos
    @MetaSparkDFDataset.expectation(["columns", "columns_prefix_patterns"])
    def expect_columns_to_follow_prefix_patterns(self, columns, columns_prefix_patterns):                             
        columns_wrong_prefix = []
        for column_name in columns:
            if not column_name.startswith(tuple(columns_prefix_patterns)):
                columns_wrong_prefix.append(column_name)
        return {
            "success": len(columns_wrong_prefix) == 0,
            "result": {    
                "partial_unexpected_list": columns_wrong_prefix,            
                "unexpected_count": len(columns_wrong_prefix)
            }
        }

    # Método que valida se as colunas do dataframe seguem padrões de nomenclatura
    @MetaSparkDFDataset.expectation(["columns", "columns_valid_types"])
    def expect_columns_to_be_of_valid_types(self, columns, columns_valid_types):       
        invalid_type_fields = []
        for field in self.spark_df.schema:
            field_name = field.name
            field_type = field.dataType.simpleString()    
            if not field_type in columns_valid_types and field_name in columns:
                invalid_type_fields.append(f"Invalid type {field_type} for field {field_name}.") 
        return {
            "success": len(invalid_type_fields) == 0,
            "result": {
                "partial_unexpected_list": invalid_type_fields,
                "unexpected_count": len(invalid_type_fields)
            }
        }

    # Método que valida se as colunas do dataframe seguem tipos validos
    @MetaSparkDFDataset.expectation(["columns"])
    def expect_columns_to_be_commented(self, columns):  
        empty_comment_columns = []
        for field in self.spark_df.schema:
            field_name = field.name
            field_comment = field.metadata.get("comment", "").strip()                    
            if field_comment == "" and field_name in columns:
                empty_comment_columns.append(f"The field {field.name} has no comment")
        return {
            "success": len(empty_comment_columns) == 0,
            "result": {
                "partial_unexpected_list": empty_comment_columns,
                "unexpected_count": len(empty_comment_columns)
            }
        }

    # Método que valida se as colunas do dataframe seguem tipos validos
    @MetaSparkDFDataset.expectation(["columns"])
    def expect_columns_to_be_named_in_lower_case(self, columns):  
        columns_not_in_lower_case = []
        for column_name in columns:
            if not column_name.islower():
                columns_not_in_lower_case.append(column_name)
        return {
            "success": len(columns_not_in_lower_case) == 0,
            "result": {
                "partial_unexpected_list": columns_not_in_lower_case,
                "unexpected_count": len(columns_not_in_lower_case)
            }
        }

    def add_expectation(self, expectation_name, expectations_kwargs):        
        """ """
        self.ge_suite.append_expectation(ExpectationConfiguration(expectation_name, expectations_kwargs))

    def validate(self):
        """ """
        self.ge_result = super().validate(self.ge_suite)
        return self.ge_result
