from dataclasses import asdict, dataclass, field, fields
from orionis.container.enums.lifetimes import Lifetime
from orionis.container.exceptions import OrionisContainerTypeError

@dataclass(unsafe_hash=True, kw_only=True)
class Binding:

    contract: type = field(
        default=None,
        metadata={
            "description": "Contrato de la clase concreta a inyectar.",
            "default": None
        }
    )

    concrete: type = field(
        default=None,
        metadata={
            "description": "Clase concreta que implementa el contrato.",
            "default": None
        }
    )

    instance: object = field(
        default=None,
        metadata={
            "description": "Instancia concreta de la clase, si se proporciona.",
            "default": None
        }
    )

    function: callable = field(
        default=None,
        metadata={
            "description": "Función que se invoca para crear la instancia.",
            "default": None
        }
    )

    lifetime: Lifetime = field(
        default=Lifetime.TRANSIENT,
        metadata={
            "description": "Tiempo de vida de la instancia.",
            "default": Lifetime.TRANSIENT
        }
    )

    enforce_decoupling: bool = field(
        default=False,
        metadata={
            "description": "Indica si se debe forzar el desacoplamiento entre contrato y concreta.",
            "default": False
        }
    )

    alias: str = field(
        default=None,
        metadata={
            "description": "Alias para resolver la dependencia desde el contenedor.",
            "default": None
        }
    )

    def __post_init__(self):
        """
        Performs type validation of instance attributes after initialization.

        Parameters
        ----------
        None

        Raises
        ------
        OrionisContainerTypeError
            If 'lifetime' is not an instance of `Lifetime` (when not None).
        OrionisContainerTypeError
            If 'enforce_decoupling' is not of type `bool`.
        OrionisContainerTypeError
            If 'alias' is not of type `str` or `None`.
        """
        if self.lifetime is not None and not isinstance(self.lifetime, Lifetime):
            raise OrionisContainerTypeError(
                f"The 'lifetime' attribute must be an instance of 'Lifetime', but received type '{type(self.lifetime).__name__}'."
            )

        if not isinstance(self.enforce_decoupling, bool):
            raise OrionisContainerTypeError(
                f"The 'enforce_decoupling' attribute must be of type 'bool', but received type '{type(self.enforce_decoupling).__name__}'."
            )

        if self.alias is not None and not isinstance(self.alias, str):
            raise OrionisContainerTypeError(
                f"The 'alias' attribute must be of type 'str' or 'None', but received type '{type(self.alias).__name__}'."
            )

    def toDict(self) -> dict:
        """
        Convert the object to a dictionary representation.
        Returns:
            dict: A dictionary representation of the Dataclass object.
        """
        return asdict(self)

    def getFields(self):
        """
        Retrieves a list of field information for the current dataclass instance.

        Returns:
            list: A list of dictionaries, each containing details about a field:
                - name (str): The name of the field.
                - type (type): The type of the field.
                - default: The default value of the field, if specified; otherwise, the value from metadata or None.
                - metadata (mapping): The metadata associated with the field.
        """
        __fields = []
        for field in fields(self):
            __metadata = dict(field.metadata) or {}
            __fields.append({
                "name": field.name,
                "type": field.type.__name__ if hasattr(field.type, '__name__') else str(field.type),
                "default": field.default if (field.default is not None and '_MISSING_TYPE' not in str(field.default)) else __metadata.get('default', None),
                "metadata": __metadata
            })
        return __fields