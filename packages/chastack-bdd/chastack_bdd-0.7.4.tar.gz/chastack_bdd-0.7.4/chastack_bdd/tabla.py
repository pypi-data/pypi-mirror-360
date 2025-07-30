from chastack_bdd.tipos import *
from chastack_bdd.utiles import *
from chastack_bdd.bdd import ProtocoloBaseDeDatos
from chastack_bdd.registro import Registro, RegistroIntermedio

class Tabla(type):
    def __new__(mcs, nombre, bases, atributos):
    
        bases_ext = bases
        if not any(issubclass(base, Registro) for base in bases) and nombre != 'Registro':
            bases_ext = (Registro,) + bases
        
        cls = super().__new__(mcs, nombre, bases_ext, atributos)
        
        asignarAtributoPrivado(cls,'__tabla',nombre)
        setattr(cls, "tabla", property(lambda cls : cls.__tabla))

        
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = {}
        
        return cls

    def __init__(cls, nombre, ancestros, diccionario):
        cls.__INICIALIZADA = False
        cls.__DEBUG = lambda msj : None

    def __call__(cls, bdd: ProtocoloBaseDeDatos, *posicionales, **nominales): 
        if nominales and nominales.get("debug", False):
            cls.__DEBUG = lambda msj: print(f"[DEBUG] {msj.rstrip()}")
        cls.__DEBUG(f"Se llamó a la clase {cls.__qualname__}. Instanciando objeto.")
        cls.__inicializar(bdd)

        instancia = super().__call__(bdd, *posicionales, **nominales)
        asignarAtributoPrivado(instancia,"__bdd",bdd)
        cls.__DEBUG(f"---------\n{instancia}\n---------\n")
        return instancia
    
    def __str__(cls):
        if not cls.__INICIALIZADA: 
            return f"<Tabla {cls.__name__}>"
        filas = {atributoPublico(ll) : v for ll,v in cls.__annotations__.items()}      
        ll_max, v_max = max(len(str(ll)) for ll, _ in filas.items() ), max(len(str(v)) for _, v in filas.items() )
        tabla_str = f"┌{'─' * (ll_max + 2)}┐\n" \
                    + f"│ {cls.__name__:<{ll_max}} │\n" \
                    + f"├{'─' * (ll_max + 2)}┼{'─' * (v_max + 2)}┬{'─' * (v_max + 2)}┐\n" \
                    + "\n".join(f"│ {str(ll):<{ll_max}} │ {str(v):<{v_max}} │ {str(cls.__tipoSQLDesdePython(v)):<{v_max}} │" for ll, v in filas.items()) \
                    + f"\n└{'─' * (ll_max + 2)}┴{'─' * (v_max + 2)}┴{'─' * (v_max + 2)}┘\n" 
        return tabla_str
    def __inicializar(cls,bdd):
            cls.__DEBUG(f"{cls.__qualname__} {'ya' if cls.__INICIALIZADA else 'no'} estaba inicializada.")
            if cls.__INICIALIZADA: return
            
            cls.__DEBUG(f"Inicializando modelo para: {cls.__tabla}.")
            slots :list[str] = []        
            anotaciones : dict[str,type] = {}
            with bdd as bdd:
                resultados = bdd.DESCRIBE(cls.__tabla).ejecutar().devolverResultados()
            
                for columna in resultados:
                    nombre_campo = columna.get('Field')
                    es_clave = columna.get('Key') == "PRI"
                    es_auto = "auto_increment" in columna.get("Extra", "").lower() or "default_generated" in columna.get("Extra", "").lower() or "auto_generated" in columna.get("Extra", "").lower()
                    
                    nombre_attr = f"__{nombre_campo}" if es_clave or es_auto else nombre_campo
                    
                    tipo = cls.__resolverTipo(columna.get('Type'), nombre_campo)
                    
                    if nombre_attr not in cls.__slots__:
                        slots.append(nombre_attr)
                    anotaciones.update({
                        nombre_attr : tipo
                    })
                    
                    if es_clave or es_auto:
                        setattr(cls, nombre_campo, property(lambda self, nombre_=nombre_campo: devolverAtributoPrivado(self,nombre_)))
                    cls.__bdd = bdd
            cls.__slots__ = cls.__slots__ + tuple(slots)
            cls.__annotations__.update(anotaciones)
            cls.__INICIALIZADA = True
            cls.__DEBUG(f"---------\n{cls}\n---------\n")
            

    @classmethod
    def __resolverTipo(cls, tipo_sql: str, nombre_columna: Optional[str]) -> type:
        """
        Deduce y devuelve un tipo de Python en base al tipo declarado en MySQL para la columna.
        Si encuentra un ENUM, crea un enum de Python y lo guarda como una constante de la clase.
        
        Parámetros:
            :arg tipo_sql str: El tipo definido en MySQL
            :arg nombre_columna Optional[str]: El nombre de la columna (útil para enums)
        
        Devuelve:
            :arg tipo `type`: el tipo python correspondiente (o `Any`)
        """
        tipo_declarado: Optional[Match[AnyStr]] = match(r'([a-z]+)(\(.*\))?', tipo_sql.lower())
        if not tipo_declarado:
            return Any

        tipo_base: str = tipo_declarado.group(1)
        parametros: str = tipo_declarado.group(2) if tipo_declarado.group(2) else ""
        tipo_completo: str = tipo_base + parametros

        tipos: dict[str, type] = {
            'tinyint': int,
            'smallint': int,
            'mediumint': int,
            'int': int,
            'bigint': int,
            'float': float,
            'double': float,
            'decimal': Decimal,
            'datetime': datetime,
            'timestamp': datetime,
            'date': date,
            'time': time,
            'char': str,
            'varchar': str,
            'text': str,
            'mediumtext': str,
            'longtext': str,
            'tinytext': str,
            'boolean': bool,
            'bool': bool,
            'tinyint(1)': bool,
            'blob': bytearray,
            'mediumblob': bytearray,
            'longblob': bytearray,
            'tinyblob': bytearray,
            'binary': bytes,
            'varbinary': bytes,
            'json': dict,
        }

        
        if tipo_base == 'enum':
            valores_enum: list[Any] = findall(r"'([^']*)'", tipo_sql)
            dicc_enum: dict[str, int] = {'_invalido': 0}
            for i, val in enumerate(valores_enum, 1):   
                dicc_enum[val] = i
            
            nombre_enum: str = f"Tipo{nombre_columna.capitalize()}" if nombre_columna else f"__ENUM_{token_urlsafe(4)}"
            clase_enum: type = type(
                nombre_enum,
                (EnumSQL, Enum),
                dicc_enum
            )
            
            setattr(cls,nombre_enum,clase_enum)
            return clase_enum

        
        if tipo_completo in tipos:
            return tipos[tipo_completo]
        return tipos.get(tipo_base, Any)

    @classmethod
    def __tipoSQLDesdePython(cls, tipo_python: type) -> str:
        """
        Devuelve el tipo SQL correspondiente a un tipo de Python.
        Si el tipo es un Enum generado por __resolverTipo, intenta reconstruir el ENUM SQL.
        
        Parámetros:
            :arg tipo_python type: el tipo de Python (p. ej., int, str, Enum, etc.)

        Devuelve:
            :arg str: el tipo SQL correspondiente
        """
        # Mapeo inverso de tipos básicos
        tipos_inversos: dict[type, str] = {
            int: 'int',
            float: 'double',
            Decimal: 'decimal(10,2)',
            datetime: 'timestamp',
            date: 'date',
            time: 'time',
            str: 'varchar(255)',
            bool: 'tinyint(1)',
            bytes: 'varbinary(255)',
            bytearray: 'blob',
            dict: 'json',
        }

        # Enums definidos dinámicamente por __resolverTipo
        if isinstance(tipo_python, type) and issubclass(tipo_python, EnumSQL):
            valores = [f"'{e.name}'" for e in tipo_python if e.name != '_invalido']
            return f"enum({','.join(valores)})"

        return tipos_inversos.get(tipo_python, 'text').upper()


    
class TablaIntermedia(type):
    def __new__(mcs, nombre, bases, atributos, esIntermedia: bool =True):
        
        bases_ext = bases
        if not any(issubclass(base, RegistroIntermedio) for base in bases) and nombre != 'RegistroIntermedio':
            bases_ext = (RegistroIntermedio,) + bases
        
        cls = super().__new__(mcs, nombre, bases_ext, atributos)
        
        asignarAtributoPrivado(cls,'__tabla',nombre)
        setattr(cls, "tabla", property(lambda cls : cls.__tabla))

        
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = {}
        
        return cls

    def __init__(cls, nombre, ancestros, diccionario):
        cls.__INICIALIZADA = False
        cls.__DEBUG = lambda msj : None

    def __call__(cls, bdd: ProtocoloBaseDeDatos, *posicionales, **nominales): 
        if nominales and nominales.get("debug", False):
            cls.__DEBUG = lambda msj: print(f"[DEBUG] {msj.rstrip()}")
        cls.__DEBUG(f"Se llamó a la clase {cls.__qualname__}. Instanciando objeto.")
        cls.__inicializar(bdd)

        instancia = super().__call__(bdd, *posicionales, **nominales)
        asignarAtributoPrivado(instancia,"__bdd",bdd)
        cls.__DEBUG(f"---------\n{instancia}\n---------\n")
        return instancia
    
    def __str__(cls):
        if not cls.__INICIALIZADA: 
            return f"<TablaIntermedia {cls.__name__}>"
        filas = {atributoPublico(ll) : v for ll,v in cls.__annotations__.items()}      
        ll_max, v_max = max(len(str(ll)) for ll, _ in filas.items() ), max(len(str(v)) for _, v in filas.items() )
        tabla_str = f"┌{'─' * (ll_max + 2)}┐\n" \
                    + f"│ {cls.__name__:<{ll_max}} │\n" \
                    + f"├{'─' * (ll_max + 2)}┼{'─' * (v_max + 2)}┬{'─' * (v_max + 2)}┐\n" \
                    + "\n".join(f"│ {str(ll):<{ll_max}} │ {str(v):<{v_max}} │ {str(cls.__tipoSQLDesdePython(v)):<{v_max}} │" for ll, v in filas.items()) \
                    + f"\n└{'─' * (ll_max + 2)}┴{'─' * (v_max + 2)}┴{'─' * (v_max + 2)}┘\n" 
        return tabla_str
    def __inicializar(cls,bdd):
            cls.__DEBUG(f"{cls.__qualname__} {'ya' if cls.__INICIALIZADA else 'no'} estaba inicializada.")
            if cls.__INICIALIZADA: return
            
            cls.__DEBUG(f"Inicializando modelo para: {cls.__tabla}.")
            slots :list[str] = []        
            anotaciones : dict[str,type] = {}
            with bdd as bdd:
                resultados = bdd.DESCRIBE(cls.__tabla).ejecutar().devolverResultados()
            
                for columna in resultados:
                    nombre_campo = columna.get('Field')
                    es_clave = columna.get('Key') == "PRI"
                    es_auto = "auto_increment" in columna.get("Extra", "").lower() or "default_generated" in columna.get("Extra", "").lower() or "auto_generated" in columna.get("Extra", "").lower()
                    
                    nombre_attr = f"__{nombre_campo}" if es_clave or es_auto else nombre_campo
                    
                    tipo = cls.__resolverTipo(columna.get('Type'), nombre_campo)
                    
                    if nombre_attr not in cls.__slots__:
                        slots.append(nombre_attr)
                    anotaciones.update({
                        nombre_attr : tipo
                    })
                    
                    if es_clave or es_auto:
                        setattr(cls, nombre_campo, property(lambda self, nombre_=nombre_campo: devolverAtributoPrivado(self,nombre_)))
                    cls.__bdd = bdd
            cls.__slots__ = cls.__slots__ + tuple(slots)
            cls.__annotations__.update(anotaciones)
            cls.__INICIALIZADA = True
            cls.__DEBUG(f"---------\n{cls}\n---------\n")
            

    @classmethod
    def __resolverTipo(cls, tipo_sql: str, nombre_columna: Optional[str]) -> type:
        """
        Deduce y devuelve un tipo de Python en base al tipo declarado en MySQL para la columna.
        Si encuentra un ENUM, crea un enum de Python y lo guarda como una constante de la clase.
        
        Parámetros:
            :arg tipo_sql str: El tipo definido en MySQL
            :arg nombre_columna Optional[str]: El nombre de la columna (útil para enums)
        
        Devuelve:
            :arg tipo `type`: el tipo python correspondiente (o `Any`)
        """
        tipo_declarado: Optional[Match[AnyStr]] = match(r'([a-z]+)(\(.*\))?', tipo_sql.lower())
        if not tipo_declarado:
            return Any

        tipo_base: str = tipo_declarado.group(1)
        parametros: str = tipo_declarado.group(2) if tipo_declarado.group(2) else ""
        tipo_completo: str = tipo_base + parametros

        tipos: dict[str, type] = {
            'tinyint': int,
            'smallint': int,
            'mediumint': int,
            'int': int,
            'bigint': int,
            'float': float,
            'double': float,
            'decimal': Decimal,
            'datetime': datetime,
            'timestamp': datetime,
            'date': date,
            'time': time,
            'char': str,
            'varchar': str,
            'text': str,
            'mediumtext': str,
            'longtext': str,
            'tinytext': str,
            'boolean': bool,
            'bool': bool,
            'tinyint(1)': bool,
            'blob': bytearray,
            'mediumblob': bytearray,
            'longblob': bytearray,
            'tinyblob': bytearray,
            'binary': bytes,
            'varbinary': bytes,
            'json': dict,
        }

        
        if tipo_base == 'enum':
            valores_enum: list[Any] = findall(r"'([^']*)'", tipo_sql)
            dicc_enum: dict[str, int] = {'_invalido': 0}
            for i, val in enumerate(valores_enum, 1):   
                dicc_enum[val] = i
            
            nombre_enum: str = f"Tipo{nombre_columna.capitalize()}" if nombre_columna else f"__ENUM_{token_urlsafe(4)}"
            clase_enum: type = type(
                nombre_enum,
                (EnumSQL, Enum),
                dicc_enum
            )
            
            setattr(cls,nombre_enum,clase_enum)
            return clase_enum

        
        if tipo_completo in tipos:
            return tipos[tipo_completo]
        return tipos.get(tipo_base, Any)

    @classmethod
    def __tipoSQLDesdePython(cls, tipo_python: type) -> str:
        """
        Devuelve el tipo SQL correspondiente a un tipo de Python.
        Si el tipo es un Enum generado por __resolverTipo, intenta reconstruir el ENUM SQL.
        
        Parámetros:
            :arg tipo_python type: el tipo de Python (p. ej., int, str, Enum, etc.)

        Devuelve:
            :arg str: el tipo SQL correspondiente
        """
        # Mapeo inverso de tipos básicos
        tipos_inversos: dict[type, str] = {
            int: 'int',
            float: 'double',
            Decimal: 'decimal(10,2)',
            datetime: 'timestamp',
            date: 'date',
            time: 'time',
            str: 'varchar(255)',
            bool: 'tinyint(1)',
            bytes: 'varbinary(255)',
            bytearray: 'blob',
            dict: 'json',
        }

        # Enums definidos dinámicamente por __resolverTipo
        if isinstance(tipo_python, type) and issubclass(tipo_python, EnumSQL):
            valores = [f"'{e.name}'" for e in tipo_python if e.name != '_invalido']
            return f"enum({','.join(valores)})"

        return tipos_inversos.get(tipo_python, 'text').upper()

        