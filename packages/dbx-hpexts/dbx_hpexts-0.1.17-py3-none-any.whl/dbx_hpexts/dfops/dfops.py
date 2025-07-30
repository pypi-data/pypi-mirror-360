from typing import Any
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, when, trim, rand
from dbx_hpexts import get_spark_conf
import dbx_hpexts
import string
import secrets

class DataFrameOP:
    
    sample_percentage_key = 'sample_percentage'
    
    
    @classmethod
    def cols_numeric_to_timestamp(cls, df:DataFrame, column_names:dict|list, divisor:int = 1_000_000)->DataFrame:
        """
        Transforms columns with numeric values to timestamp type\n
        df: the dataframe U need to modify\n
        column_names: list of columns to update, or a mapping dict e.g. { col_name: new_col_name} in case U need to rename columns\n
        divisor: In case u need to divide the colum values by something else than 1000000 to make it a standard epoch timestamp
        """
        columns_map = {}
        if isinstance(column_names, list):
            columns_map = { value: value for value in column_names }
        elif isinstance(column_names, dict):
            columns_map = column_names
        else:
            raise Exception(f'columns names must be of type list or dict, type {type(column_names)} not supported.')
            
        for col_name, new_col_name in columns_map.items():
            df = df.withColumn(col_name, when((col(col_name).isNotNull()) & (trim(col(col_name)) != ""),
                        (col(col_name).cast("bigint") / divisor).cast("timestamp")).otherwise(None) )
            if new_col_name != col_name:
                df = df.withColumnRenamed(col_name, new_col_name)
        return df


    @classmethod
    def cols_to_datatype(cls, df:DataFrame, column_names:dict|list, datatype:Any)->DataFrame:
        """
        Transforms column types\n
        df: the dataframe U need to modify\n
        column_names: list of columns to convert, or a mapping dict e.g. { col_name: new_col_name} in case U need to rename columns\n
        datatype: the pyspark datatype U want on the columns
        """
        columns_map = {}
        if isinstance(column_names, list):
            columns_map = { value: value for value in column_names }
        elif isinstance(column_names, dict):
            columns_map = column_names
        else:
            raise Exception(f'columns names must be of type list or dict, type {type(column_names)} not supported.')
        
        for col_name, new_col_name in columns_map.items():
            df = df.withColumn(col_name, col(col_name).cast(datatype))
            if col_name != new_col_name:
                df = df.withColumnRenamed(col_name, new_col_name)
        return df
    
    
    @classmethod
    def to_sample(cls, df:DataFrame, percentage:int=None, randomize:bool|int=True)->DataFrame:
        """
        Extracts a subset of data inside dataframe only if pencentage is provided and it is minor than 100\n
        df: the dataframe to operate with\n
        percentage: percentage from 0 to 100 of data to be extracted from df\n
                    if U set sample_percentage from base_parameters or configuration in your bundle yaml that value will overwrite the one provided here.\n
        randomize: In case U want the extracted dataframe to always be the same for the exact input dataframe set it to False\n
                   give an integer value if U want to especify a seed, it provides similar behaviour to False but U can control somehow what data
        """
        bare_percentage:float = cls.__resolve_sample_percentage(percentage)
        if bare_percentage is not None:  
            rand_colname:str = '_name'
            while rand_colname in df.columns or rand_colname[0].isdigit():
                rand_colname = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
            seed:int = 999999
            provideseed:bool = False
            if isinstance(randomize, bool):
                provideseed = not randomize
            elif isinstance(randomize, int):
                provideseed = True
                seed = randomize
            elif randomize is not None:
                raise Exception(f'type {type(randomize)} not supported for randomize parameter.')
            
            seed = seed if provideseed else None
            return df.withColumn(rand_colname, rand(seed)).filter(f"{rand_colname} < {bare_percentage}").drop(rand_colname)
        else:
            return df
        
    
    @classmethod
    def __resolve_sample_percentage(cls, percentage:int=None)->float:
        _sample_percentage = get_spark_conf(cls.sample_percentage_key)
        if _sample_percentage is None:
            _sample_percentage = dbx_hpexts.get_dbutils_widget(cls.sample_percentage_key)
        percentage = percentage if _sample_percentage is None else int(_sample_percentage)
        if percentage is None or percentage >= 100 or percentage <= 0:
            return None
        else:
            return (percentage / 100)