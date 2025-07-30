import collections as _col
import functools as _func
import pathlib as _pth
import typing as _typ
import warnings as _warn

from . import extension as _ext

path: str = "~/.tidy3d/pf_cache"


def _cache_path(name: str) -> _pth.Path:
    return _pth.Path(path).expanduser() / name[:3]


class _Cache:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.data = _col.OrderedDict()

    def __getitem__(self, key: _typ.Any) -> _typ.Any:
        value = self.data.get(key, None)
        if value is not None:
            self.data.move_to_end(key)
        return value

    def __setitem__(self, key: _typ.Any, value: _typ.Any) -> None:
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = value
        if self.capacity > 0:
            while len(self.data) >= self.capacity:
                self.data.popitem(False)

    def clear(self) -> None:
        self.data = _col.OrderedDict()


_s_matrix_cache = _Cache(64)
_tidy3d_model_cache = _Cache(64)
_mode_solver_cache = _Cache(64)
_mode_overlap_cache = _Cache(64)
_all_caches = [_s_matrix_cache, _tidy3d_model_cache, _mode_solver_cache, _mode_overlap_cache]


def cache_s_matrix(start: _typ.Callable):
    """Decorator that can be used in :func:`Model.start` to cache results."""

    @_func.wraps(start)
    def _start(model, component, frequencies, *args, **kwargs):
        # Global config must be part of the key
        cache_target = _ext.Component("", _ext.config.default_technology)
        cache_target.add_reference(component)
        cache_target.add_model(model, "")
        kwargs[""] = (
            tuple(frequencies),
            _ext.config.default_mesh_refinement,
            _ext.config.default_kwargs,
            *args,
        )
        cache_target.parametric_kwargs = kwargs

        try:
            key = cache_target.as_bytes
        except Exception:
            _warn.warn(
                f"Unable to cache results for component '{component.name}'.", RuntimeWarning, 2
            )
            return start(model, component, frequencies, *args, **kwargs)

        result = _s_matrix_cache[key]
        if result is None:
            result = start(model, component, frequencies, *args, **kwargs)
            _s_matrix_cache[key] = result
        elif kwargs.get("verbose", False):
            print(f"Using cached result for {component}/{model}.")
        return result

    return _start


def clear_cache() -> None:
    """Clear the runtime caches, but not the file cache.

    The file cache is stored in :data:`photonforge.cache.path`. It can be
    cleared by simply deleting the contents in that directory.
    """
    for c in _all_caches:
        c.clear()


def cache_capacity(capacity: int) -> None:
    """Set the runtime cache capacity.

    Args:
        capacity: Set a new cache capacity. A negative value removes the
          capacity limit.
    """
    for c in _all_caches:
        c.capacity = capacity
