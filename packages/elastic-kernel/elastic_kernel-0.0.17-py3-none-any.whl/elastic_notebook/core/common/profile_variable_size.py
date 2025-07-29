import sys
import types


def get_total_size(data):
    """
    Compute the estimated total size of a variable.
    """

    def get_memory_size(obj, is_initialize, visited):
        # same memory space should be calculated only once
        obj_id = id(obj)
        if obj_id in visited:
            return 0
        visited.add(obj_id)

        try:
            total_size = sys.getsizeof(obj)
        except Exception:
            total_size = float("inf")

        obj_type = type(obj)
        if obj_type in [int, float, str, bool, type(None)]:
            # if the original obj is not primitive, then the size is already included
            if not is_initialize:
                return 0
        else:
            if obj_type in [list, tuple, set]:
                for e in obj:
                    total_size = total_size + get_memory_size(e, False, visited)
            elif obj_type is dict:
                for k, v in obj.items():
                    total_size = total_size + get_memory_size(k, False, visited)
                    total_size = total_size + get_memory_size(v, False, visited)
            # function, method, class
            elif obj_type in [
                types.FunctionType,
                types.MethodType,
                types.BuiltinFunctionType,
                types.ModuleType,
            ] or isinstance(
                obj, type
            ):  # True if obj is a class
                pass
            # custom class instance
            elif isinstance(type(obj), type):
                # if obj has no builtin size and has additional pointers
                # if obj has builtin size, all the additional memory space is already added
                if not hasattr(obj, "__sizeof__") and hasattr(obj, "__dict__"):
                    for k, v in getattr(obj, "__dict__").items():
                        total_size = total_size + get_memory_size(k, False, visited)
                        total_size = total_size + get_memory_size(v, False, visited)
            else:
                raise NotImplementedError("Not handled", obj)
        return total_size

    return get_memory_size(data, True, set())


def profile_variable_size(x) -> int:
    """
    Profiles the size of variable x. Notably, this should recursively find the size of lists, sets and dictionaries.
    Args:
        x: The variable to profile.
    """
    return get_total_size(x)
