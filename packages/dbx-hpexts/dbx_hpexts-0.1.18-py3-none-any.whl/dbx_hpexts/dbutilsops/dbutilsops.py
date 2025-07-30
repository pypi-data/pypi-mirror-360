import dbx_hpexts

def get_dbutils_widget(widget_key)->str:
    widget_value:str = None
    if dbx_hpexts.dbutils is not None:
        try:
            widget_value = dbx_hpexts.dbutils.widgets.get(widget_key)
        except:
            widget_value = None
    return widget_value


def get_dbutils_secret(scope, key)->str:
    secret_value:str = None
    if dbx_hpexts.dbutils is not None:
        try:
            secret_value = dbx_hpexts.dbutils.secrets.get(scope=scope, key=key)
        except:
            secret_value = None
    return secret_value