from __future__ import annotations

from collections.abc import Hashable, Mapping
from typing import Any

import pyproj
import xarray as xr
from pyproj.exceptions import CRSError

# TODO: import from xarray.errors when available
# (https://github.com/pydata/xarray/pull/10285)
from xarray import AlignmentError
from xarray.indexes import Index


def _format_crs(crs: pyproj.CRS, max_width: int = 20) -> str:
    srs = crs.to_string()
    return srs if len(srs) <= max_width else " ".join([srs[:max_width], "..."])


class CRSIndex(Index):
    """A basic :py:class:`xarray.Index` that has a :py:class:`pyproj.crs.CRS`
    attached.

    This index must be associated with a scalar coordinate variable.

    Best way to create a CRSIndex is via either
    :py:meth:`xarray.Dataset.proj.assign_crs` or
    :py:meth:`xarray.Dataset.set_xindex` (or the DataArray equivalent methods).

    This index is used for propagation of the CRS information through Xarray
    operations and for CRS-aware alignment of Xarray objects (only checking
    strict equality, automatic re-indexing / re-projection is not supported). It
    doesn't support CRS-aware data selection.

    """

    _crs: pyproj.CRS

    def __init__(self, crs: pyproj.CRS | Any):
        """
        Parameters
        ----------
        crs : Any
            The coordinate reference system to attach to the index in any format
            that can be passed to :py:meth:`pyproj.crs.CRS.from_user_input`.

        """
        self._crs = pyproj.CRS.from_user_input(crs)

    @property
    def crs(self) -> pyproj.CRS:
        """Returns the :py:class:`pyproj.crs.CRS` object attached to this index."""
        return self._crs

    @classmethod
    def from_variables(
        cls,
        variables: Mapping[Any, xr.Variable],
        *,
        options: Mapping[str, Any],
    ) -> CRSIndex:
        if len(variables) != 1:
            raise ValueError("can only create a CRSIndex from one scalar variable")

        varname = next(iter(variables.keys()))
        var = next(iter(variables.values()))

        if var.ndim != 0:
            raise ValueError("can only create a CRSIndex from one scalar variable")

        try:
            if "crs" in options:
                crs = pyproj.CRS.from_user_input(options["crs"])
            else:
                crs = pyproj.CRS.from_cf(var.attrs)
        except CRSError:
            raise ValueError(
                f"CRS could not be constructed from attrs on provided variable {varname!r}"
                f"Either add appropriate attributes to {varname!r} or pass a `crs` kwarg."
            )

        return cls(crs)

    def equals(self, other: Index, *, exclude: frozenset[Hashable] | None = None) -> bool:
        if not isinstance(other, CRSIndex):
            return False
        if not self.crs == other.crs:
            return False
        return True

    def join(self, other: CRSIndex, how: str = "inner") -> CRSIndex:
        # If this method is called during Xarray alignment, it means that the
        # equality check failed. Instead of a NotImplementedError we raise a
        # ValueError with a nice error message.
        raise AlignmentError(
            "Objects to align do not have the same CRS\n"
            f"first index:\n{self!r}\n\nsecond index:\n{other!r}"
        )

    def _repr_inline_(self, max_width: int) -> str:
        if max_width is None:
            max_width = xr.get_options()["display_width"]

        srs = _format_crs(self.crs, max_width=max_width)
        return f"{self.__class__.__name__} (crs={srs})"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}" + "\n" + repr(self.crs)
