from enum import StrEnum

from app.modules.role.domain.enumerators.permissions.analytic_permissions import (
    AnalyticsPermission,
)
from app.modules.role.domain.enumerators.permissions.audit_permissions import (
    AuditPermission,
)
from app.modules.role.domain.enumerators.permissions.content_permissions import (
    ContentPermission,
)
from app.modules.role.domain.enumerators.permissions.menu_permissions import (
    MenuPermission,
)
from app.modules.role.domain.enumerators.permissions.owner_permissions import (
    OwnerPermission,
)
from app.modules.role.domain.enumerators.permissions.poi_permissions import (
    POIPermission,
)
from app.modules.role.domain.enumerators.permissions.role_permissions import (
    RolePermission,
)
from app.modules.role.domain.enumerators.permissions.system_permission import (
    SystemPermission,
)
from app.modules.role.domain.enumerators.permissions.user_permissions import (
    UserPermission,
)

PERMISSION_DOMAINS: tuple[type[StrEnum], ...] = (
    POIPermission,
    MenuPermission,
    UserPermission,
    RolePermission,
    AnalyticsPermission,
    AuditPermission,
    SystemPermission,
    OwnerPermission,
    ContentPermission,
)

ALL_PERMISSIONS = frozenset(
    permission.value for domain in PERMISSION_DOMAINS for permission in domain
)
