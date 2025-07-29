#-------------------- Imports --------------------

from typing import Type, Callable

from .classes import create_slots_cls
from .cache import get_global_cache_manager
from .utils import create_cache_key

#-------------------- Stash Decorator --------------------

def Stash(
        freeze: bool = False
    ) -> Callable[[Type], Type]:

    """
    A Python class-decorator designed for memory optimization by dynamically generating a __slots__-based class.

    Decorator reduces general memory overhead by eliminating __dict__,
    and automatically generating __init__, __repr__, __eq__ methods.

    Args:
        Freeze (bool): If True, prevents attribute mutation after instantiation.
        Preserve (list[str]): List of individual methods preserved from teh original class.

    Returns:
        Callable[[Type], Type]Dynamically creates a new class-object instead of initial class.

    Exceptions:
        TypeErrors: Raised if individual params are not of the correct Type. 
    """

    if not isinstance(freeze, bool):
        raise TypeError(f"Paramater 'Freeze' must be of Type: Boolean, not {type(freeze).__name__}")
    
    cache_manager = get_global_cache_manager()

    def wrapper(cls: Type) -> Type:

        key = create_cache_key(cls, freeze)

        cached = cache_manager.get(key)
        if cached is not None:
            return cached
        
        new_cls = create_slots_cls(cls, freeze)
        cache_manager.add(key, new_cls)

        return new_cls

    return wrapper


#-------------------- Conserve Decorator --------------------

def conserve(method: Callable) -> Callable:
    """
    Method-decorator used to define class-functions that @Stash is required to preserve.

    Used in conjuction with @Stash class-decorator in order to explicitly mark which functions
    require preservation.

    Args:
        No arguments required.

    Returns:
        Callable: The decorator-method, marked for preservation in the new __slots__-based class.

    Exceptions:
        None. 
    """

    if isinstance(method, (staticmethod, classmethod)):
        func = method.__func__
        setattr(func, "_conserve", True)
    else:
        setattr(method, "_conserve", True)
    return method
    
    