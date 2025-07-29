# dbutils.py - Stub for VS Code
"""
If running inside Databricks, the runtime provides a global `dbutils` object.
Outside Databricks (e.g. in VS Code), this stub allows syntax highlighting and linting.
Save this file as `dbutils.py` in your project root.
"""
import builtins
from typing import List, Dict, Any, Optional

# -- Credentials utility (dbutils.credentials)
class DBUtilsCredentials:
    def assumeRole(self, role: str) -> bool:
        """Set the IAM role ARN for credentials passthrough."""
        raise NotImplementedError("dbutils.credentials.assumeRole is not available outside Databricks.")

    def getServiceCredentialsProvider(self, credentialName: str) -> Any:
        """Get a service credentials provider object."""
        raise NotImplementedError("dbutils.credentials.getServiceCredentialsProvider is not available outside Databricks.")

    def showCurrentRole(self) -> List[str]:
        """List the currently assumed IAM role(s)."""
        raise NotImplementedError("dbutils.credentials.showCurrentRole is not available outside Databricks.")

    def showRoles(self) -> List[str]:
        """List possible IAM roles to assume."""
        raise NotImplementedError("dbutils.credentials.showRoles is not available outside Databricks.")

# -- Data utility (dbutils.data)
class DBUtilsData:
    def summarize(self, df: Any, precise: bool = False) -> None:
        """Summarize a Spark or pandas DataFrame."""
        raise NotImplementedError("dbutils.data.summarize is not available outside Databricks.")

# -- File system utility (dbutils.fs)
class DBUtilsFS:
    def ls(self, path: str) -> List[Dict[str, Any]]:
        """List files and dirs under a path."""
        raise NotImplementedError("dbutils.fs.ls is not available outside Databricks.")

    def cp(self, source: str, dest: str, recurse: bool = False) -> None:
        """Copy files or directories."""
        raise NotImplementedError("dbutils.fs.cp is not available outside Databricks.")

    def rm(self, path: str, recurse: bool = False) -> None:
        """Remove a file or directory."""
        raise NotImplementedError("dbutils.fs.rm is not available outside Databricks.")

    def mkdirs(self, path: str) -> None:
        """Create directories."""
        raise NotImplementedError("dbutils.fs.mkdirs is not available outside Databricks.")

    def mount(self, source: str, mount_point: str, extra_configs: Dict[str, str] = None) -> None:
        """Mount storage."""
        raise NotImplementedError("dbutils.fs.mount is not available outside Databricks.")

    def unmount(self, mount_point: str) -> None:
        """Unmount storage."""
        raise NotImplementedError("dbutils.fs.unmount is not available outside Databricks.")

# -- Jobs utility (dbutils.jobs.taskValues)
class DBUtilsJobsTaskValues:
    def get(self, taskKey: str, key: str, default: Any = None, debugValue: Any = None) -> Any:
        """Get a job task value."""
        raise NotImplementedError("dbutils.jobs.taskValues.get is not available outside Databricks.")

    def set(self, key: str, value: Any) -> bool:
        """Set a job task value."""
        raise NotImplementedError("dbutils.jobs.taskValues.set is not available outside Databricks.")

class DBUtilsJobs:
    def __init__(self):
        self.taskValues = DBUtilsJobsTaskValues()

# -- Library utility (dbutils.library)
class DBUtilsLibrary:
    def install(self, libraries: List[Dict[str, Any]]) -> None:
        """Install session-scoped libraries."""
        raise NotImplementedError("dbutils.library.install is not available outside Databricks.")

    def uninstall(self, name: str) -> None:
        """Uninstall a library."""
        raise NotImplementedError("dbutils.library.uninstall is not available outside Databricks.")

# -- Meta utility (dbutils.meta)
class DBUtilsMeta:
    def debug(self, msg: str) -> None:
        """Emit compiler hook debug info."""
        raise NotImplementedError("dbutils.meta.debug is not available outside Databricks.")

# -- Notebook utility (dbutils.notebook)
class DBUtilsNotebook:
    def run(self, path: str, timeout_seconds: int = 0, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Run another notebook."""
        raise NotImplementedError("dbutils.notebook.run is not available outside Databricks.")

    def exit(self, return_value: Any = None) -> None:
        """Exit the current notebook with a return value."""
        raise NotImplementedError("dbutils.notebook.exit is not available outside Databricks.")

    def getContext(self) -> Any:
        """Get the notebook context."""
        raise NotImplementedError("dbutils.notebook.getContext is not available outside Databricks.")

# -- Preview utility (dbutils.preview)
class DBUtilsPreview:
    def listPreviews(self) -> List[str]:
        """List preview features or data."""
        raise NotImplementedError("dbutils.preview.listPreviews is not available outside Databricks.")

# -- Secrets utility (dbutils.secrets)
class DBUtilsSecrets:
    def get(self, scope: str, key: str) -> str:
        """Get a secret string."""
        raise NotImplementedError("dbutils.secrets.get is not available outside Databricks.")

    def getBytes(self, scope: str, key: str) -> bytes:
        """Get a secret as bytes."""
        raise NotImplementedError("dbutils.secrets.getBytes is not available outside Databricks.")

    def list(self, scope: str) -> List[Dict[str, Any]]:
        """List all secrets in a scope."""
        raise NotImplementedError("dbutils.secrets.list is not available outside Databricks.")

    def listScopes(self) -> List[Dict[str, Any]]:
        """List all secret scopes."""
        raise NotImplementedError("dbutils.secrets.listScopes is not available outside Databricks.")

# -- Widgets utility (dbutils.widgets)
class DBUtilsWidgets:
    def text(self, name: str, defaultValue: str = "", label: str = "") -> None:
        """Create a text widget."""
        raise NotImplementedError("dbutils.widgets.text is not available outside Databricks.")

    def dropdown(self, name: str, defaultValue: str, choices: List[str], label: str = "") -> None:
        """Create a dropdown widget."""
        raise NotImplementedError("dbutils.widgets.dropdown is not available outside Databricks.")

    def get(self, name: str) -> str:
        """Get the value of a widget."""
        raise NotImplementedError("dbutils.widgets.get is not available outside Databricks.")

    def removeAll(self) -> None:
        """Remove all widgets."""
        raise NotImplementedError("dbutils.widgets.removeAll is not available outside Databricks.")

# -- API utility (dbutils.api)
class DBUtilsAPI:
    def build(self, **kwargs) -> Any:
        """Manage application builds."""
        raise NotImplementedError("dbutils.api.build is not available outside Databricks.")

# -- Composite dbutils
class DBUtils:
    def __init__(self):
        self.credentials = DBUtilsCredentials()
        self.data        = DBUtilsData()
        self.fs          = DBUtilsFS()
        self.jobs        = DBUtilsJobs()
        self.library     = DBUtilsLibrary()
        self.meta        = DBUtilsMeta()
        self.notebook    = DBUtilsNotebook()
        self.preview     = DBUtilsPreview()
        self.secrets     = DBUtilsSecrets()
        self.widgets     = DBUtilsWidgets()
        self.api         = DBUtilsAPI()

# Use Databricks-provided dbutils if available
if hasattr(builtins, 'dbutils'):
    dbutils = builtins.dbutils
else:
    dbutils = DBUtils()
