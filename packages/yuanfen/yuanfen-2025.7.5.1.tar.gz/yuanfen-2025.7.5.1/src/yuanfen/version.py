from typing import Dict, SupportsInt, Tuple, Union

Comparable = Union["Version", Dict[str, int], Union[int], str]


class Version:
    def __init__(self, major: SupportsInt, minor: SupportsInt = 0, patch: SupportsInt = 0):
        version_parts = {"major": int(major), "minor": int(minor), "patch": int(patch)}
        self._major = version_parts["major"]
        self._minor = version_parts["minor"]
        self._patch = version_parts["patch"]

    @property
    def major(self) -> int:
        """The major part of a version (read-only)."""
        return self._major

    @major.setter
    def major(self, value):
        raise AttributeError("attribute 'major' is readonly")

    @property
    def minor(self) -> int:
        """The minor part of a version (read-only)."""
        return self._minor

    @minor.setter
    def minor(self, value):
        raise AttributeError("attribute 'minor' is readonly")

    @property
    def patch(self) -> int:
        """The patch part of a version (read-only)."""
        return self._patch

    @patch.setter
    def patch(self, value):
        raise AttributeError("attribute 'patch' is readonly")

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)

    def to_dict(self) -> Dict[str, int]:
        return {"major": self.major, "minor": self.minor, "patch": self.patch}

    def __str__(self) -> str:
        return f"{self._major}.{self._minor}.{self._patch}"

    def __repr__(self) -> str:
        s = ", ".join("%s=%r" % (key, val) for key, val in self.to_dict().items())
        return "%s(%s)" % (type(self).__name__, s)

    @classmethod
    def parse(cls, version: str) -> "Version":
        version_parts = version.split(".")
        if len(version_parts) < 1:
            raise ValueError("Invalid version format")

        major = int(version_parts[0])
        if len(version_parts) < 2:
            return cls(major)

        minor = int(version_parts[1])
        if len(version_parts) < 3:
            return cls(major, minor)

        patch = int(version_parts[2])
        return cls(major, minor, patch)

    def compare(self, other: Comparable) -> int:
        cls = type(self)

        if isinstance(other, dict):
            other = Version(**other)
        elif isinstance(other, (tuple, list)):
            other = Version(*other)
        elif isinstance(other, str):
            other = Version.parse(other)
        elif not isinstance(other, cls):
            raise ValueError(f"Unsupported type: {type(other)}")

        v1 = self.to_tuple()
        v2 = other.to_tuple()
        return (v1 > v2) - (v1 < v2)
