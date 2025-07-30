
from hcp import HCPVaultClient
import dbx_hpexts
from dbx_hpexts import get_spark_conf

class HCPSecretsMngr:
    
    client_id_key = 'client_id'
    client_secret_key = 'client_secret'
    org_id_key = 'org_id'
    project_id_key = 'project_id'
    app_id_key = 'app_id'
    clear_refresh_key = 'clear_refresh'
    secret_uri_key = 'secret_uri'
    refresh_timeout_min_key = 'refresh_timeout_min'
    
    required_keys:list = [client_id_key, client_secret_key, org_id_key, project_id_key, app_id_key]
    secrets_scope_key:str = 'secrets_scope'
    secrets_map_key = 'hpc_secrets_map'
    
    @classmethod
    def get(cls, client_id:str, client_secret:str, org_id:str, project_id:str, app_id:str, secret_uri:str=None, refresh_timeout_min:int=None, clear_refresh:bool=False)->dict:
        """This is just a wrapper for HCPVaultClient."""
        params = {cls.client_id_key: client_id, cls.client_secret_key: client_secret, cls.org_id_key: org_id, cls.project_id_key: project_id, cls.app_id_key: app_id, cls.clear_refresh_key: clear_refresh}
        if secret_uri is not None:
            params[cls.secret_uri_key] = secret_uri
        if refresh_timeout_min is not None:
            params[cls.refresh_timeout_min_key] = refresh_timeout_min
        secrets_mgr = HCPVaultClient(**params)
        return secrets_mgr.fetch_secrets()
    
    
    @classmethod
    def __resolve_scope_name(cls, scope_name:str= None)->str:
        _scope_name = get_spark_conf(cls.secrets_scope_key)
        if _scope_name is None:
            _scope_name = dbx_hpexts.get_dbutils_widget(cls.secrets_scope_key)
        scope_name = scope_name if _scope_name is None else _scope_name
        return scope_name
    
    
    @classmethod
    def __resolve_secrets_map(cls, secrets_map:str|dict=None)->dict:
        f_secrets_map:dict = None
        _secrets_map = get_spark_conf(cls.secrets_map_key)
        if _secrets_map is None:
            _secrets_map = dbx_hpexts.get_dbutils_widget(cls.secrets_map_key)
        secrets_map = secrets_map if _secrets_map is None else _secrets_map
        
        if isinstance(secrets_map, str):
            secrets_map_list = secrets_map.split(';')
            secrets_map = { }
            
            for current_map in secrets_map_list:
               current_map_list = str(current_map).split(':')
               if len(current_map_list) == 2:
                secrets_map[current_map_list[0].strip()] = current_map_list[1].strip()
                
        if isinstance(secrets_map, dict):
            found_keys:list = [str(key).lower() for key in secrets_map.keys()]
            if not set(cls.required_keys).issubset(set(found_keys)):
                raise Exception(f"U are not providing all the required keys for {cls.secrets_map_key}. required_keys: {set(cls.required_keys)} ,found_keys {set(found_keys)}")
            f_secrets_map = { value: str(key).lower() for key, value in secrets_map.items() if str(key).lower() in cls.required_keys }
        return f_secrets_map
    
    
    @classmethod
    def get_from_secrets(cls, scope_name:str=None, secrets_map:str|dict=None, secret_uri:str=None, refresh_timeout_min:int=None, clear_refresh:bool=False)->dict:
        """
        scope_name: what secrets scope contains the secrets where U have hcp configuration keys
                    if U set secrets_scope from base_parameters or configuration in your bundle yaml that value will overwrite the one provided here.
        secrets_map: mapping for hcp conf, e.g. CLIENT_ID:HCP_CLIENT_ID;CLIENT_SECRET:HCP_CLIENT_SECRET;APP_ID:HCP_APP_ID;ORG_ID:HCP_ORG_ID;PROJECT_ID:HCP_PROJECT_ID
                    if U set hpc_secrets_map from base_parameters or configuration in your bundle yaml that value will overwrite the one provided here.
        """
        scope_name = cls.__resolve_scope_name(scope_name)
        if scope_name is None:
            raise Exception(f"{cls.secrets_scope_key} can't be resolved, please provide secrets scope.")
        secrets_map = cls.__resolve_secrets_map(secrets_map)
        if secrets_map is None:
            raise Exception(f"{cls.secrets_map_key} can't be resolved, please provide hcp secrets map.")

        params = {}
        for secret_key, hcp_key in secrets_map.items():
            params[hcp_key] = dbx_hpexts.get_dbutils_secret(scope=scope_name, key=secret_key)
            if params[hcp_key] is None:
                raise Exception(f"secret {secret_key} not found under scope {scope_name}.")
        
        _params = {}
        for required_key in cls.required_keys:
            _params[required_key] = params[required_key]
        _params = {**_params, **{cls.clear_refresh_key: clear_refresh, cls.secret_uri_key: secret_uri, cls.refresh_timeout_min_key: refresh_timeout_min}}

        return cls.get(**_params)

        
    