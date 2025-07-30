from chastack_bdd.tipos import *
from chastack_bdd.utiles import *
from chastack_bdd.usuario.errores import *
from chastack_bdd import Tabla, Registro
from chastack_bdd import ProtocoloBaseDeDatos, TipoCondicion, ErrorMalaSolicitud
from typing import Optional
import os
from secrets import token_bytes, token_urlsafe
from hashlib import sha256

class Usuario(Registro):
    """
    Clase base con funcionalidad común a usuarios.
    Maneja autenticación, encriptado de contraseñas,
    y gestión de sesiones y códigos de acceso únicos.
    """
    __slots__ = (
        "nombre_usuario",
        "correo",
        "contrasena",
        "id_sesion",
        "codigo_unico",
        "sal",
        "__fecha_ultimo_ingreso",
    )

    nombre_usuario : str
    correo : str
    contrasena : bytes
    __fecha_ultimo_ingreso : datetime
    id_sesion : str
    codigo_unico : Optional[str]
    sal : bytes

    @sobrecargar
    def __init__(
        self, 
        bdd : ProtocoloBaseDeDatos, 
        correo : str,
        contrasena : str,
        nombre_usuario : str = None
        ,*,debug : bool = False,
    ):
        correo = correo
        nombre_usuario = nombre_usuario if nombre_usuario is not None else correo
        contrasena, sal = self.encriptarContraseña(contrasena)
        id_sesion = self.__generarIdSesion()
        codigo_unico = None
        fecha_ultimo_ingreso = datetime.now()
        super().__init__(
            bdd=bdd,
            valores = dict(
                correo = correo,
                nombre_usuario = nombre_usuario,
                contrasena = contrasena,
                sal = sal,
                id_sesion = id_sesion,
                codigo_unico = codigo_unico,
                fecha_ultimo_ingreso = fecha_ultimo_ingreso,
            )
        )

    @classmethod
    def registrar(
        cls, 
        bdd : ProtocoloBaseDeDatos, 
        correo : str,
        contrasena : str,
        nombre_usuario : str = None,
        **nominales,
    ):
        este_usuario = cls(bdd, correo, contrasena, nombre_usuario)
        este_usuario.__init__(bdd, valores=dict(**nominales))
        return este_usuario

    @classmethod
    @sobrecargar
    def ingresar(
        cls,
        bdd: ProtocoloBaseDeDatos,
        nombre_usuario: str,
        contrasena: str
    ) -> 'Usuario':
        """Autentica un usuario usando nombre de usuario/correo y contraseña.  
        **Parametros:**  
            :param ProtocoloBaseDeDatos bdd: Conexión a la base de datos.  
            :param str nombre_usuario: Nombre de usuario o correo electrónico.  
            :param str contrasena: Contraseña en texto plano.    
        
        **Levanta:**  
            :param ErrorAccesoIncorrecto: Si las credenciales son incorrectas  
        
        **Retorna:**  
            :param Usuario: Instancia del usuario autenticado    
        ---  
        """
        datos : Optional[Resultado]
        columnas : tuple[str] = cls.__devolverColumnas()
        with bdd as bdd:
            bdd.SELECT(cls.__name__,columnas)
            if '@' in nombre_usuario:                
                bdd.WHERE(TipoCondicion.IGUAL,correo=nombre_usuario)
            else:
                bdd.WHERE(TipoCondicion.IGUAL,nombre_usuario=nombre_usuario)
            datos = bdd.ejecutar().devolverUnResultado()

        if datos is not None and cls.__verificarContraseña(datos.get('contrasena'), contrasena, datos.get('sal')):
            este_usuario = cls(bdd,valores = datos)
            este_usuario.id_sesion = cls.__generarIdSesion()
            este_usuario._actualizarFechaIngreso()
            este_usuario.guardar()
            return este_usuario
        else:
            raise ErrorAccesoIncorrecto("Usuario, correo o contraseña incorrectos.")
    
    @classmethod
    @sobrecargar
    def ingresar(
        cls,
        bdd : ProtocoloBaseDeDatos,
        id_sesion : str
    ) -> 'Usuario':
        datos : Optional[Resultado]
        columnas : tuple[str] = self.__devolverColumnas()
        with self.__bdd:
            datos = bdd.SELECT(cls.__name__,columnas)\
                    .WHERE(TipoCondicion.IGUAL,id_sesion=id_sesion)\
                    .ejecutar().devolverUnResultado()

        if datos is not None:
            este_usuario = cls(bdd,valores = datos)
            este_usuario._actualizarFechaIngreso()
            este_usuario.guardar()
            return este_usuario
        else:
            raise ErrorMalaSolicitud("No existe usuario con el id_sesion provisto.")
        
    def cerrarSesion(self) -> None:
        """
        Cierra la sesión del usuario eliminando su ID de sesión.
        """
        self.id_sesion = None
        self.guardar()
    
    def cambiarContraseña(self, contrasena_nueva: str) -> Self:
        """
        Cambia la contraseña del usuario.
        
        Args:
            contrasena_nueva: Nueva contraseña en texto plano
        """
        contrasena_encriptada, sal = self.encriptarContraseña(contrasena_nueva)
        self.contrasena = contrasena_encriptada
        self.sal = sal
        self.guardar()
        return self
    
    @staticmethod
    def encriptarContraseña(contrasena: str, sal: bytes = None) -> tuple[bytes, bytes]:
        """Encripta una contraseña usando SHA-256 con sal y pimienta.  
        **Precondición:**  
            Debe existir la variable de entrono PIMIENTA, que contenga la cadena única 
            y persistente utilizada para el encriptado.  
        **Parametros:**  
            :param str contrasena: Contraseña en texto plano.  
            :param bytes sal: al para la encriptación. Si es `None`, se genera. Por defecto: None.  
        
        **Retorna:**  
            :param tuple[bytes, bytes]: Tupla con (contraseña_encriptada, sal)    
        
        ---  
        """
        if sal is None:
            sal = token_bytes(32) 
            
        pimienta = os.environ.get('PIMIENTA', '').encode('utf-8')
        contrasena_base = contrasena.encode('utf-8')
        
        contrasena_encriptada = sha256(contrasena_base + sal + pimienta).digest()
        return contrasena_encriptada, sal
    
    @staticmethod
    def __verificarContraseña(
        contrasena_encriptada: bytes, 
        contrasena: str, 
        sal: bytes
    ) -> bool:
        """Verifica si una contraseña coincide con su versión encriptada.    
        **Precondición:**  
            Debe existir la variable de entrono PIMIENTA, que contenga la cadena única 
            y persistente utilizada para el encriptado.  
        **Parametros:**  
            :param bytes contrasena_encriptada: Contraseña encriptada almacenada.  
            :param str contrasena: Contraseña en texto plano a verificar.  
            :param bytes sal: Sal utilizada en el encriptado.  
        
        **Retorna:**  
            :param bool: `True` si la contraseña es correcta, `False` en caso contrario.    
        
        ---  
        """
        return contrasena_encriptada == Usuario.encriptarContraseña(contrasena, sal)[0]

    @staticmethod 
    def __generarIdSesion() -> str:
        return token_urlsafe(64)
        
    @classmethod
    def __devolverColumnas(cls) -> tuple[str]:
        """Devuelve los `__slots__` de `Usuario` como columnas para operar con SQL.  
        
        **Retorna:**  
            :param tuple[str]: columnas SQL.    
        ---  
        """
        return (atributoPublico(atr) for atr in cls.__slots__ if atr not in ('__bdd','__tabla'))
    
    def _actualizarFechaIngreso(self, fecha_ultimo_ingreso : datetime = datetime.now()):
        self.__fecha_ultimo_ingreso = fecha_ultimo_ingreso