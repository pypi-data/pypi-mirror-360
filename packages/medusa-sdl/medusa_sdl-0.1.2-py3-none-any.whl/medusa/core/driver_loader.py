from importlib.metadata import entry_points
from typing import Dict, Tuple, Type

_EP_GROUP = "medusa.devices"

def discover() -> dict[str, type]:
    """Return {'TecanXCPump': <class ...>, ...} for *all* installed plugins."""
    return {ep.name: ep.load() for ep in entry_points(group=_EP_GROUP)}

# global, evaluated once at import-time
DEVICE_REGISTRY: dict[str, type] = discover()

def get_driver(name: str):
    """Return the concrete driver class, or raise a clear error."""
    try:
        return DEVICE_REGISTRY[name]
    except KeyError as e:
        raise ValueError(
            f"No driver named '{name}'. Install the plugin, e.g.  pip install medusa-devices-{name.lower()}"
        ) from e
    
def get_classes_by_category(category: str) -> Tuple[Type, ...]:
    """All drivers whose class attribute  `category == category` ."""
    return tuple(
        cls for cls in DEVICE_REGISTRY.values()
        if getattr(cls, "category", None) == category
    )

def get_classes_by_category_or_name(category: str) -> Tuple[Type, ...]:
    cat_lower = category.lower()
    out = []
    for cls in DEVICE_REGISTRY.values():
        cls_cat = getattr(cls, "category", "").lower()
        name   = cls.__name__.lower()
        # match exact category OR substring match on class name
        if cls_cat == cat_lower or cat_lower in name:
            out.append(cls)
    return tuple(out)

def get_category_map() -> Dict[Type, str]:
    """{DriverClass: 'Pump' | 'Valve' | ...} for every installed class."""
    return {
        cls: getattr(cls, "category", cls.__name__)
        for cls in DEVICE_REGISTRY.values()
    }