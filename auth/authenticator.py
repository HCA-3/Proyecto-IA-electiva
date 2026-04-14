"""
auth/authenticator.py
---------------------
Gestión de usuarios, roles y autenticación de Justicia IA.
Usa SHA-256 para almacenar contraseñas. Los usuarios se persisten
en auth/users.json y se crean automáticamente en el primer arranque.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------------------------
# Enumerados y modelos de datos
# ---------------------------------------------------------------------------

class Role(str, Enum):
    SUPERADMIN = "superadmin"
    USER = "user"


@dataclass
class User:
    username: str
    password_hash: str
    role: Role
    display_name: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["role"] = self.role.value
        return d

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(
            username=data["username"],
            password_hash=data["password_hash"],
            role=Role(data["role"]),
            display_name=data["display_name"],
        )


# ---------------------------------------------------------------------------
# AuthManager
# ---------------------------------------------------------------------------

class AuthManager:
    """
    Gestiona la autenticación y el ciclo de vida de usuarios.

    Persiste los usuarios en un archivo JSON. Si el archivo no existe,
    crea un conjunto de usuarios por defecto en el primer arranque.

    Credenciales por defecto:
        - superadmin / Admin123!
        - usuario    / User123!
    """

    _USERS_FILE = Path(__file__).parent / "users.json"

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._load_or_initialize()

    # ------------------------------------------------------------------
    # Público
    # ------------------------------------------------------------------

    def authenticate(self, username: str, password: str) -> User | None:
        """
        Verifica credenciales y retorna el User si son correctas, None si no.

        Args:
            username: Nombre de usuario (case-insensitive).
            password: Contraseña en texto plano.

        Returns:
            User autenticado o None.
        """
        user = self._users.get(username.lower().strip())
        if user and user.password_hash == self._hash(password):
            return user
        return None

    def change_password(self, username: str, new_password: str) -> None:
        """Cambia la contraseña de un usuario y persiste el cambio."""
        if username not in self._users:
            raise ValueError(f"Usuario '{username}' no encontrado.")
        self._users[username].password_hash = self._hash(new_password)
        self._save()

    def list_users(self) -> list[User]:
        """Retorna todos los usuarios registrados."""
        return list(self._users.values())

    def add_user(self, username: str, password: str, role: Role, display_name: str) -> None:
        """Agrega un nuevo usuario y lo persiste."""
        key = username.lower().strip()
        if key in self._users:
            raise ValueError(f"El usuario '{username}' ya existe.")
        self._users[key] = User(
            username=key,
            password_hash=self._hash(password),
            role=role,
            display_name=display_name,
        )
        self._save()

    def delete_user(self, username: str) -> None:
        """Elimina un usuario. No permite eliminar al último superadmin."""
        key = username.lower().strip()
        if key not in self._users:
            raise ValueError(f"Usuario '{username}' no encontrado.")
        admins = [u for u in self._users.values() if u.role == Role.SUPERADMIN]
        if self._users[key].role == Role.SUPERADMIN and len(admins) <= 1:
            raise ValueError("No se puede eliminar el único superadministrador.")
        del self._users[key]
        self._save()

    # ------------------------------------------------------------------
    # Privado
    # ------------------------------------------------------------------

    def _load_or_initialize(self) -> None:
        """Carga usuarios desde JSON o crea los usuarios por defecto."""
        if self._USERS_FILE.exists():
            self._load()
        else:
            self._create_defaults()
            self._save()

    def _load(self) -> None:
        with open(self._USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._users = {u["username"]: User.from_dict(u) for u in data.get("users", [])}

    def _save(self) -> None:
        self._USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self._USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"users": [u.to_dict() for u in self._users.values()]},
                f,
                indent=2,
                ensure_ascii=False,
            )

    def _create_defaults(self) -> None:
        self._users = {
            "admin": User(
                username="admin",
                password_hash=self._hash("Admin123!"),
                role=Role.SUPERADMIN,
                display_name="Administrador",
            ),
            "usuario": User(
                username="usuario",
                password_hash=self._hash("User123!"),
                role=Role.USER,
                display_name="Usuario",
            ),
        }

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()
