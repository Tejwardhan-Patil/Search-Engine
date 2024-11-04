import hashlib
from typing import Dict, List, Optional


class Permission:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Permission(name={self.name})"


class Role:
    def __init__(self, name: str):
        self.name = name
        self.permissions: List[Permission] = []

    def add_permission(self, permission: Permission):
        if permission not in self.permissions:
            self.permissions.append(permission)

    def remove_permission(self, permission: Permission):
        if permission in self.permissions:
            self.permissions.remove(permission)

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

    def __repr__(self):
        return f"Role(name={self.name}, permissions={self.permissions})"


class User:
    def __init__(self, username: str):
        self.username = username
        self.roles: List[Role] = []

    def add_role(self, role: Role):
        if role not in self.roles:
            self.roles.append(role)

    def remove_role(self, role: Role):
        if role in self.roles:
            self.roles.remove(role)

    def has_permission(self, permission: Permission) -> bool:
        for role in self.roles:
            if role.has_permission(permission):
                return True
        return False

    def __repr__(self):
        return f"User(username={self.username}, roles={self.roles})"


class AccessControlList:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}

    def create_user(self, username: str) -> User:
        if username in self.users:
            raise ValueError(f"User {username} already exists.")
        user = User(username)
        self.users[username] = user
        return user

    def create_role(self, role_name: str) -> Role:
        if role_name in self.roles:
            raise ValueError(f"Role {role_name} already exists.")
        role = Role(role_name)
        self.roles[role_name] = role
        return role

    def create_permission(self, permission_name: str) -> Permission:
        if permission_name in self.permissions:
            raise ValueError(f"Permission {permission_name} already exists.")
        permission = Permission(permission_name)
        self.permissions[permission_name] = permission
        return permission

    def assign_role_to_user(self, username: str, role_name: str):
        user = self.users.get(username)
        role = self.roles.get(role_name)
        if not user or not role:
            raise ValueError(f"User or Role not found.")
        user.add_role(role)

    def assign_permission_to_role(self, role_name: str, permission_name: str):
        role = self.roles.get(role_name)
        permission = self.permissions.get(permission_name)
        if not role or not permission:
            raise ValueError(f"Role or Permission not found.")
        role.add_permission(permission)

    def check_user_permission(self, username: str, permission_name: str) -> bool:
        user = self.users.get(username)
        permission = self.permissions.get(permission_name)
        if not user or not permission:
            raise ValueError(f"User or Permission not found.")
        return user.has_permission(permission)

    def revoke_role_from_user(self, username: str, role_name: str):
        user = self.users.get(username)
        role = self.roles.get(role_name)
        if not user or not role:
            raise ValueError(f"User or Role not found.")
        user.remove_role(role)

    def revoke_permission_from_role(self, role_name: str, permission_name: str):
        role = self.roles.get(role_name)
        permission = self.permissions.get(permission_name)
        if not role or not permission:
            raise ValueError(f"Role or Permission not found.")
        role.remove_permission(permission)

    def list_user_roles(self, username: str) -> List[Role]:
        user = self.users.get(username)
        if not user:
            raise ValueError(f"User {username} not found.")
        return user.roles

    def list_role_permissions(self, role_name: str) -> List[Permission]:
        role = self.roles.get(role_name)
        if not role:
            raise ValueError(f"Role {role_name} not found.")
        return role.permissions

    def __repr__(self):
        return f"AccessControlList(users={self.users}, roles={self.roles}, permissions={self.permissions})"


# Usage
def main():
    acl = AccessControlList()

    # Create users
    user1 = acl.create_user("Person1")
    user2 = acl.create_user("Person2")

    # Create roles
    admin_role = acl.create_role("admin")
    editor_role = acl.create_role("editor")

    # Create permissions
    read_permission = acl.create_permission("read")
    write_permission = acl.create_permission("write")
    delete_permission = acl.create_permission("delete")

    # Assign roles to users
    acl.assign_role_to_user("Person1", "admin")
    acl.assign_role_to_user("Person2", "editor")

    # Assign permissions to roles
    acl.assign_permission_to_role("admin", "read")
    acl.assign_permission_to_role("admin", "write")
    acl.assign_permission_to_role("admin", "delete")
    acl.assign_permission_to_role("editor", "read")
    acl.assign_permission_to_role("editor", "write")

    # Check permissions for users
    print(f"Person1 has 'write' permission: {acl.check_user_permission('Person1', 'write')}")
    print(f"Person2 has 'delete' permission: {acl.check_user_permission('Person2', 'delete')}")

    # List roles and permissions
    print(f"Person1 roles: {acl.list_user_roles('Person1')}")
    print(f"Admin role permissions: {acl.list_role_permissions('admin')}")

    # Revoke permissions
    acl.revoke_permission_from_role("editor", "write")
    print(f"Editor role permissions after revoke: {acl.list_role_permissions('editor')}")

    # Revoke role from user
    acl.revoke_role_from_user("Person2", "editor")
    print(f"Person2 roles after revoke: {acl.list_user_roles('Person2')}")


if __name__ == "__main__":
    main()