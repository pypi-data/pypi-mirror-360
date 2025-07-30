from pathlib import PurePosixPath
from typing import Union, Type


class SupportsPermission:
    @property
    def path(self) -> str:
        raise NotImplementedError

    @classmethod
    def get_class_path(cls) -> str:
        raise NotImplementedError

    @staticmethod
    def as_path_string(obj: Union["SupportsPermission", str]) -> str:
        # Get the raw path
        if isinstance(obj, SupportsPermission):
            path = obj.path
        elif isinstance(obj, str):
            path = obj
        else:
            raise TypeError("Invalid type for SupportsPermission.")

        # Validate the path
        try:
            # Convert to PurePosixPath to normalize and validate
            normalized = str(PurePosixPath(path))

            # Additional security checks
            if not normalized or normalized.isspace():
                raise ValueError("Empty or whitespace-only path")
            if ".." in normalized:
                raise ValueError("Path traversal not allowed")

            return normalized

        except Exception as e:
            raise ValueError(f"Invalid path format: {path}. Error: {str(e)}")

    @staticmethod
    def get_parent_path(path: str) -> str:
        return str(PurePosixPath(path).parent)

    @property
    def parent_path(self):
        return self.get_parent_path(self.path)


class PermissionEnabledSQLModelMixin(SupportsPermission):
    @classmethod
    def get_class_path(cls) -> str:
        return cls.__tablename__  # noqa


class ResourceType(SupportsPermission):
    def __init__(
        self,
        cls: Type[SupportsPermission] | str,
        path_prefix: str | None = None,
        path_postfix: str | None = None,
    ):
        if isinstance(cls, type) and not issubclass(cls, SupportsPermission):
            raise TypeError(
                f"Class {cls.__name__} must inherit from SupportsPermission"
            )
        self._class_path = cls.get_class_path() if isinstance(cls, type) else cls
        self._path_prefix = path_prefix
        self._path_postfix = path_postfix

    def __truediv__(self, other: str) -> "ResourceType":
        """Allow using / operator to append to the path postfix.

        Example:
            resource_type / "some_id"
        """
        new_postfix = (
            other if self._path_postfix is None else f"{self._path_postfix}/{other}"
        )
        return ResourceType(
            cls=self._class_path,  # Pass the string path directly
            path_prefix=self._path_prefix,
            path_postfix=new_postfix,
        )

    @property
    def path(self) -> str:
        # Build path components, filtering out None values
        components = [
            comp
            for comp in [self._path_prefix, self._class_path, self._path_postfix]
            if comp is not None
        ]
        # Join and normalize using the existing validation method
        return self.as_path_string("/".join(components))

    def in_account(self, account: SupportsPermission) -> "ResourceType":
        self._path_prefix = account.path
        return self
