from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MovieInfo:
    """Data class holding metadata for a single movie."""

    title: Optional[str] = None
    original_title: Optional[str] = None
    year: Optional[str] = None
    plot: Optional[str] = None
    outline: Optional[str] = None
    director: Optional[str] = None
    runtime: Optional[str] = None
    rating: Optional[float] = None
    votes: Optional[int] = None
    genre: list[str] = field(default_factory=list)
    actor: list[str] = field(default_factory=list)
    country: list[str] = field(default_factory=list)
    language: list[str] = field(default_factory=list)
    studio: Optional[str] = None
    cover: Optional[str] = None
    backdrop: Optional[str] = None
    trailer: Optional[str] = None
    publish_date: Optional[str] = None
    tmdb_id: Optional[str] = None
    imdb_id: Optional[str] = None
    douban_id: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None

    # Local file info (populated by scanner)
    file_path: Optional[str] = None
    file_size: Optional[int] = None

    def merge(self, other: 'MovieInfo'):
        """Merge non-None fields from another MovieInfo, without overwriting existing values."""
        for f in self.__dataclass_fields__:
            other_val = getattr(other, f)
            self_val = getattr(self, f)
            if other_val is None:
                continue
            if isinstance(other_val, list) and not other_val:
                continue
            if self_val is None or (isinstance(self_val, list) and not self_val):
                setattr(self, f, other_val)

    def has_required_keys(self, keys: list[str]) -> bool:
        """Check if specified fields are non-empty."""
        for key in keys:
            val = getattr(self, key, None)
            if val is None:
                return False
            if isinstance(val, (list, str)) and not val:
                return False
        return True

    def __str__(self) -> str:
        lines = []
        for f in self.__dataclass_fields__:
            val = getattr(self, f)
            if val is not None and val != [] and val != '':
                lines.append(f"  {f}: {val}")
        header = self.title or 'Unknown'
        return f"MovieInfo: {header}\n" + "\n".join(lines)
