#-------------------- Imports --------------------

#-------------------- Custom Exceptions --------------------

class FreezeAttributeException(AttributeError):
    def __init__(self, message=None, *, name=None, obj=None):
        if message is None:
            message = f"Cannot modify frozen attribute {name} on {obj!r}"
        super().__init__(message)
        self.name = name
        self.obj = obj
