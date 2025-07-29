class FinalMeta(type):
    """Metaclass to ensure classes are final."""

    def __new__(cls, name, bases, namespace):
        for base in bases:
            assert not isinstance(base, FinalMeta), (
                f"class {base.__qualname__} is final and cannot be subclassed"
            )
        return super().__new__(cls, name, bases, namespace)
