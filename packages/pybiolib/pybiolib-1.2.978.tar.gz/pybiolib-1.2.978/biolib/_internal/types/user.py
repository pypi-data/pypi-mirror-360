from .account import AccountDict
from .typing import Optional, TypedDict


class EnterpriseSettingsDict(TypedDict):
    account_uuid: str
    dashboard_message: Optional[str]
    docs_message: Optional[str]
    featured_dashboard_app_version_uuid: Optional[str]


class UserDict(TypedDict):
    uuid: str
    email: str
    account: AccountDict


class UserDetailedDict(UserDict):
    enterprise_settings: Optional[EnterpriseSettingsDict]
