"""Version module for pyminideprecator."""

from datetime import date, datetime


class Version:
    """
    Represents a version for deprecation lifecycle management.

    Supports both semantic versioning (1.2.3) and date-based versioning (2023.12.31).
    Provides comparison operations for version lifecycle decisions.

    Args:
        version_str: Version string to parse

    Raises:
        ValueError: For invalid version formats

    Attributes:
        raw: Original version string
        is_date: True if version is date-based
        parts: Tuple of integers for semantic versions
        date: Date object for date-based versions

    """

    def __init__(self, version_str: str) -> None:
        """
        Initialize a version class.

        Args:
            version_str (str): version as string.

        Raises:
            ValueError: invalid version format.

        """
        self.raw: str = version_str
        self.hash = hash(self.raw)
        self.is_date: bool = False
        self.parts: tuple[int, ...] = ()
        self.date: date = date(1970, 1, 1)

        try:
            self.date = datetime.strptime(  # noqa: DTZ007
                version_str, "%Y.%m.%d"
            ).date()

            self.is_date = True
        except ValueError:
            pass

        if not self.is_date:
            try:
                self.parts = tuple(int(part) for part in version_str.split("."))
            except ValueError as ex:
                raise ValueError(
                    f"Invalid version format: {version_str} ({ex})"
                ) from ex

    def __lt__(self, other: "Version") -> bool:
        """
        Implements less-than comparison between versions.

        Args:
            other: Version object to compare against

        Returns:
            True if this version is less than other version

        Raises:
            TypeError: When comparing different version types

        """
        if self.is_date != other.is_date:
            raise TypeError("Cannot compare different version types")

        if self.is_date:
            return self.date < other.date
        return self.parts < other.parts

    def __ge__(self, other: "Version") -> bool:
        """
        Implements greater-than-or-equal comparison between versions.

        Args:
            other: Version object to compare against

        Returns:
            True if this version is greater than or equal to other version

        Raises:
            TypeError: When comparing different version types

        """
        return not self < other

    def __hash__(self) -> int:
        """
        Get hash version (raw).

        Returns:
            raw

        """
        return self.hash

    def __eq__(self, other: object) -> bool:
        """
        Implements equals comparison between versions.

        Args:
            other: Version object to compare against

        Returns:
            True if this version is equals than other version

        """
        return hash(self) == hash(other)

    def __repr__(self) -> str:
        """
        Official string representation of the Version object.

        Returns:
            String representation that can be used to recreate the object

        """
        return f"Version('{self.raw}')"
