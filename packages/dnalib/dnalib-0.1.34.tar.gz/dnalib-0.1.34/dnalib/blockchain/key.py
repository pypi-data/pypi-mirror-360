from pyspark.sql.functions import col, get_json_object
import pickle
import re

class Key:	
    """ 
        A classe Key é um wrapper para o método col do Pyspark, com a adição que ela armazena as fields em listas internas, para consulta.

        Args:
            field (str): string que representa o nome de uma coluna do pyspark, internamente é repassado para o col.

        Attributes:
            field (str): string que representa o nome de uma coluna do pyspark, internamente é repassado para o col.
            field_rep (col): resultado de várias operações booleanas feitas internamente com a função col.
            fields (list): lista com todas as fields resultantes das operações com as Keys.
            lfieds (list): lista com todas as fields a esquerda resultantes das operações com as Keys.
            lfieds (list): lista com todas as fields a direita resultantes das operações com as Keys.

    """ 
    
    def __init__(self, field):
        self.field = field        
        self.field_rep = None
        self.fields = [field]        
        self.lfields = []
        self.rfields = []
        self.key_field_rep = f'Key("{field}")'

    @staticmethod
    def from_serialized(serialized_key):   
        return eval(serialized_key)        
    
    def serialize(self):        
        return self.key_field_rep

    def right_fields(self):
        """
            Método getter que retorna a lista de fields a direita.

            Returns: 
                list: lista com todas as fields a direita.
        """
        return list(dict.fromkeys(self.rfields).keys())

    def left_fields(self):
        """
            Método getter que retorna a lista de fields a esquerda.

            Returns: 
                list: lista com todas as fields a esquerda.
        """
        return list(dict.fromkeys(self.lfields).keys())

    def chain_key(self, df_alias, key_name):
        return get_json_object(col(f"{df_alias}.payload"), f"$.{key_name}")
    
    def propagate_fields(self, other, op):
        # na primeira vez, precisa preencher as fields a esquerda da operação
        if len(self.lfields) == 0:
            self.lfields.append(self.field)

        # na primeira vez, precisa preencher as fields a direita da operação
        if len(self.rfields) == 0:
            self.rfields.append(other.field)        

        # propaga as fields da esquerda
        self.lfields = self.lfields + other.lfields
        # propaga as fields da direita
        self.rfields = self.rfields + other.rfields
        # propaga todos os valores de fields
        self.fields = self.fields + other.fields  

        # criando uma string para representar as operações
        self.key_field_rep = f"({self.key_field_rep} {op} {other.key_field_rep})"        

    def init_fields(self, other):        
        if self.field_rep is None:
            self.field_rep = self.chain_key("block", self.field)        
        if other.field_rep is None:
            other.field_rep = self.chain_key("block_prev", other.field)

    def __repr__(self):
        return str(self.key_field_rep)

    def __str__(self):
        return str(self.key_field_rep)

    def __or__(self, other):                
        self.init_fields(other)
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep | other.field_rep   
        # propaga as fields
        self.propagate_fields(other, "|")       
        return self

    def __and__(self, other):                
        self.init_fields(other)
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep & other.field_rep    
        # propaga as fields
        self.propagate_fields(other, "&")       
        return self
    
    def __lt__(self, other):   
        self.init_fields(other)     
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep < other.field_rep
        # propaga as fields
        self.propagate_fields(other, "<")
        return self
    
    def __le__(self, other):   
        self.init_fields(other)     
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep <= other.field_rep
        # propaga as fields
        self.propagate_fields(other, ">=")
        return self
    
    def __eq__(self, other):   
        self.init_fields(other)     
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep == other.field_rep
        # propaga as fields
        self.propagate_fields(other, "==")
        return self
    
    def __ne__(self, other):   
        self.init_fields(other)     
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep != other.field_rep
        # propaga as fields
        self.propagate_fields(other, "!=")
        return self
    
    def __gt__(self, other):   
        self.init_fields(other)     
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep > other.field_rep
        # propaga as fields
        self.propagate_fields(other, ">")
        return self
    
    def __ge__(self, other):   
        self.init_fields(other)     
        # popula a estrutura de fields usando o col do spark
        self.field_rep = self.field_rep >= other.field_rep
        # propaga as fields
        self.propagate_fields(other, ">=")
        return self