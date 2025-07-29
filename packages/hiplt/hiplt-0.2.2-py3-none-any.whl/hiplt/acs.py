# hiplt/acs.py

import json
from functools import wraps
from typing import Dict, Set, Callable, Optional


class AccessDenied(Exception):
    """Исключение при отказе в доступе."""
    pass


class Role:
    def __init__(self, name: str, permissions: Optional[Set[str]] = None, inherits: Optional[Set[str]] = None, priority: int = 0):
        self.name = name
        self.permissions = permissions or set()
        self.inherits = inherits or set()
        self.priority = priority

    def add_permission(self, perm: str):
        self.permissions.add(perm)

    def remove_permission(self, perm: str):
        self.permissions.discard(perm)

    def has_permission(self, perm: str, roles_map: Dict[str, "Role"], checked=None) -> bool:
        if checked is None:
            checked = set()
        if perm in self.permissions:
            return True
        checked.add(self.name)
        for parent_name in self.inherits:
            if parent_name in checked:
                continue
            parent_role = roles_map.get(parent_name)
            if parent_role and parent_role.has_permission(perm, roles_map, checked):
                return True
        return False


class AccessControlSystem:
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_roles: Dict[str, Set[str]] = {}
        self.groups: Dict[str, Set[str]] = {}
        self.group_roles: Dict[str, Set[str]] = {}
        self._cache = {}

    def log(self, msg: str):
        print(f"[ACS LOG] {msg}")

    def add_role(self, role_name: str, permissions: Optional[Set[str]] = None, inherits: Optional[Set[str]] = None, priority: int = 0):
        self.roles[role_name] = Role(role_name, permissions, inherits, priority)
        self.log(f"Role '{role_name}' added with priority {priority}")

    def remove_role(self, role_name: str):
        self.roles.pop(role_name, None)
        for user, roles in self.user_roles.items():
            roles.discard(role_name)
        for group, roles in self.group_roles.items():
            roles.discard(role_name)
        self.log(f"Role '{role_name}' removed")

    def assign_role(self, user_id: str, role_name: str):
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist")
        self.user_roles.setdefault(user_id, set()).add(role_name)
        self._cache_clear(user_id)
        self.log(f"Role '{role_name}' assigned to user '{user_id}'")

    def revoke_role(self, user_id: str, role_name: str):
        if user_id in self.user_roles:
            self.user_roles[user_id].discard(role_name)
            self._cache_clear(user_id)
            self.log(f"Role '{role_name}' revoked from user '{user_id}'")

    def add_group(self, group_name: str):
        self.groups.setdefault(group_name, set())
        self.group_roles.setdefault(group_name, set())
        self.log(f"Group '{group_name}' created")

    def remove_group(self, group_name: str):
        self.groups.pop(group_name, None)
        self.group_roles.pop(group_name, None)
        self.log(f"Group '{group_name}' removed")

    def add_user_to_group(self, user_id: str, group_name: str):
        if group_name not in self.groups:
            raise ValueError(f"Group '{group_name}' does not exist")
        self.groups[group_name].add(user_id)
        self._cache_clear(user_id)
        self.log(f"User '{user_id}' added to group '{group_name}'")

    def remove_user_from_group(self, user_id: str, group_name: str):
        if group_name in self.groups:
            self.groups[group_name].discard(user_id)
            self._cache_clear(user_id)
            self.log(f"User '{user_id}' removed from group '{group_name}'")

    def assign_role_to_group(self, group_name: str, role_name: str):
        if group_name not in self.groups:
            raise ValueError(f"Group '{group_name}' does not exist")
        if role_name not in self.roles:
            raise ValueError(f"Role '{role_name}' does not exist")
        self.group_roles[group_name].add(role_name)
        for user_id in self.groups[group_name]:
            self._cache_clear(user_id)
        self.log(f"Role '{role_name}' assigned to group '{group_name}'")

    def revoke_role_from_group(self, group_name: str, role_name: str):
        if group_name in self.group_roles:
            self.group_roles[group_name].discard(role_name)
            for user_id in self.groups.get(group_name, []):
                self._cache_clear(user_id)
            self.log(f"Role '{role_name}' revoked from group '{group_name}'")

    def _get_user_all_roles(self, user_id: str) -> Set[str]:
        roles = set(self.user_roles.get(user_id, set()))
        for group_name, users in self.groups.items():
            if user_id in users:
                roles.update(self.group_roles.get(group_name, set()))
        return roles

    def user_has_permission(self, user_id: str, perm: str) -> bool:
        cache_key = (user_id, perm)
        if cache_key in self._cache:
            return self._cache[cache_key]

        roles = self._get_user_all_roles(user_id)
        roles_objs = [self.roles[r] for r in roles if r in self.roles]
        roles_objs.sort(key=lambda r: r.priority, reverse=True)

        for role in roles_objs:
            if role.has_permission(perm, self.roles):
                self._cache[cache_key] = True
                return True

        self._cache[cache_key] = False
        return False

    def _cache_clear(self, user_id: str):
        keys_to_delete = [k for k in self._cache if k[0] == user_id]
        for k in keys_to_delete:
            del self._cache[k]

    def require_permission(self, perm: str):
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(user_id: str, *args, **kwargs):
                if not self.user_has_permission(user_id, perm):
                    raise AccessDenied(f"User '{user_id}' does not have permission '{perm}'")
                return func(user_id, *args, **kwargs)
            return wrapper
        return decorator

    def load_from_file(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.roles.clear()
        for role_name, info in data.get("roles", {}).items():
            perms = set(info.get("permissions", []))
            inherits = set(info.get("inherits", []))
            priority = info.get("priority", 0)
            self.add_role(role_name, perms, inherits, priority)

        self.user_roles = {user: set(roles) for user, roles in data.get("user_roles", {}).items()}
        self.groups = {g: set(users) for g, users in data.get("groups", {}).items()}
        self.group_roles = {g: set(roles) for g, roles in data.get("group_roles", {}).items()}
        self._cache.clear()
        self.log(f"Data loaded from {path}")

    def save_to_file(self, path: str):
        data = {
            "roles": {
                role_name: {
                    "permissions": list(role.permissions),
                    "inherits": list(role.inherits),
                    "priority": role.priority
                } for role_name, role in self.roles.items()
            },
            "user_roles": {user: list(roles) for user, roles in self.user_roles.items()},
            "groups": {g: list(users) for g, users in self.groups.items()},
            "group_roles": {g: list(roles) for g, roles in self.group_roles.items()},
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        self.log(f"Data saved to {path}")


# Пример использования
if __name__ == "__main__":
    acs = AccessControlSystem()

    acs.add_role("admin", {"manage_users", "ban_users"}, priority=10)
    acs.add_role("moderator", {"delete_messages"}, inherits={"user"}, priority=5)
    acs.add_role("user", {"read_messages", "write_messages"}, priority=1)

    acs.add_group("vip")
    acs.assign_role_to_group("vip", "user")
    acs.assign_role_to_group("vip", "moderator")

    acs.add_user_to_group("user_10", "vip")

    acs.assign_role("user_1", "admin")

    print(acs.user_has_permission("user_1", "ban_users"))       # True
    print(acs.user_has_permission("user_10", "delete_messages"))  # True (через группу)
    print(acs.user_has_permission("user_10", "ban_users"))        # False

    @acs.require_permission("ban_users")
    def ban_user(caller_id: str, target_id: str):
        print(f"User {caller_id} banned {target_id}")

    try:
        ban_user("user_1", "user_10")
        ban_user("user_10", "user_1")
    except AccessDenied as e:
        print(e)