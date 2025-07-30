class MedusaError(Exception):
    pass


class RangeError(MedusaError):
    pass


class HardwareError(MedusaError):
    pass


class GraphLayoutError(MedusaError):
    pass


class PathError(MedusaError):
    pass
