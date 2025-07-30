class Field:

    def __init__(self, 
                 field_name,                  
                 field_comment=None,                                  
                 field_type=None,
                 field_is_nullable=None, 
                 field_format=None):   

        self.field_name = field_name    
        # dataCarga is not required in yml, cause it is inserted by code            
        if self.field_name == "dataCarga":
            self.field_comment = "Data de carga dos dados"
        # same as dataCarga            
        elif self.field_name == "checksum":
            self.field_comment = "CheckSum/Hash_sql das informações do registro (linha)"
        elif field_comment:
            self.field_comment = field_comment
        else:
            self.field_comment = ""
        if field_type:
            self.field_type = field_type
        else:
            self.field_type = 'string'
        # field is only declared as not nulabble if it is false
        if field_is_nullable != False:
            self.field_is_nullable = True 
        else:
            self.field_is_nullable = False
        # formatation is not aplied only if it is false
        if field_format != False:
            self.field_format = True 
        else:
            self.field_format = False

    def is_valid_comment(self):
        return self.comment != ""

    def hash_sql(self):
        return f"sha2(cast({self.field_name} as string), 256) AS {self.field_name}"

    def to_sql(self):
        sql_representation = "{} {} COMMENT '{}'{}".format(self.field_name, self.field_type, self.field_comment, " NOT NULL" if not self.field_is_nullable else "")  
        return sql_representation
    
    def __repr__(self):
        return self.to_sql()
    
    def __str__(self):
        return f"""Field(field_name={self.field_name}, field_type={self.field_type}, field_comment={self.field_comment}, field_is_nullable={self.field_is_nullable}, field_format={self.field_format})"""
    