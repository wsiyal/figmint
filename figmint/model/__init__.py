"""Model layer: selection state and artist reference resolution."""

from figmint.model.artref import artist_ref, describe_artist
from figmint.model.selection import SelectionModel

__all__ = ["SelectionModel", "artist_ref", "describe_artist"]
