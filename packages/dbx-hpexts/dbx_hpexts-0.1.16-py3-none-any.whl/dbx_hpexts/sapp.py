from dbx_hpexts.dbutilslike import DBUtils
from pyspark.sql import SparkSession

dbutils:DBUtils = DBUtils()


def get_spark_conf(conf_key, default:str = None)->str:
    spark:SparkSession = SparkSession.builder.getOrCreate()
    _value:str = None
    try:
        _value = spark.conf.get(conf_key)
    except Exception as e:
        _value = default
    return _value