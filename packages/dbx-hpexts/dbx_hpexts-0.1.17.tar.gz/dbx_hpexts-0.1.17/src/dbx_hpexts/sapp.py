from dbx_hpexts.dbutilslike import DBUtils
from pyspark.sql import SparkSession

dbutils:DBUtils = DBUtils()


def get_dbutils_widget(widget_key)->str:
    widget_value:str = None
    if dbutils is not None:
        try:
            widget_value = dbutils.widgets.get(widget_key)
        except:
            widget_value = None
    return widget_value


def get_dbutils_secret(scope, key)->str:
    secret_value:str = None
    if dbutils is not None:
        try:
            secret_value = dbutils.secrets.get(scope=scope, key=key)
        except:
            secret_value = None
    return secret_value
#


def get_spark_conf(conf_key, default:str = None)->str:
    spark:SparkSession = SparkSession.builder.getOrCreate()
    _value:str = None
    try:
        _value = spark.conf.get(conf_key)
    except Exception as e:
        _value = default
    return _value