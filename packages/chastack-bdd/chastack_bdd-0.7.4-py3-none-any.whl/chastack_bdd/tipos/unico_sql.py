from chastack_bdd.tipos import TypeVar, Generic
from chastack_bdd.utiles import tieneAtributoPrivado

T = TypeVar('T')

class MetaUnico(type):
    def __instancecheck__(cls, instancia):
        if hasattr(cls, '__tipo__'):
            return isinstance(getattr(instancia, '__valor__', instancia), cls.__tipo__)
        return super().__instancecheck__(instancia)

    def __subclasscheck__(cls, subclase):
        if hasattr(cls, '__tipo__'):
            return issubclass(getattr(subclase, '__tipo__', subclase), cls.__tipo__)
        return super().__subclasscheck__(subclase)

class Unico(Generic[T], metaclass=MetaUnico):
    __slots__ = ('__valor__',)

    def __init__(self, valor: T):
        self.__valor__ = valor

    def __getattr__(self, attr):
        return getattr(self.__valor__, attr)

    def __str__(self):
        return str(self.__valor__)

    def __repr__(self):
        return f"Unico({repr(self.__valor__)})"

    def __eq__(self, otro):
        if tieneAtributo(otro, '__valor__'):
            return self.__valor__ == otro.valor 
        return self.__valor__ == otro

    @property
    def valor(self) -> T:
        return self.__valor__

    def __class_getitem__(cls, tipo):
        class SubUnico(cls):
            __tipo__ = tipo

        SubUnico.__name__ = f"Unico[{tipo.__name__}]"
        SubUnico.__qualname__ = f"Unico[{tipo.__name__}]"
        return SubUnico
