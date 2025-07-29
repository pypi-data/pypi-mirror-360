import json

from django.db import models
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework import serializers

from .interface import BaseTypeModel
from .logger import logger


class PydanticModelFieldEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump(mode="json")
        elif isinstance(obj, list) and isinstance(obj[0], BaseModel):
            data: list[BaseModel] = obj
            return [model.model_dump(mode="json") for model in data]
        else:
            return super().default(obj)


class PydanticModelField(models.JSONField):
    """Usage

    data = PydanticModelField(pydantic_model=AnswerModel) \n
    data = PydanticModelField(pydantic_model=[AnswerModel]) \n
    data = PydanticModelField(pydantic_model={"word_play":AnswerModel,"essay":EssayAnswer})
    """

    def __init__(
        self,
        pydantic_model: BaseModel
        | tuple[type[BaseModel]]
        | dict[str, type[BaseModel]] = None,
        null: bool = True,
        blank: bool = True,
        validate_default: bool = False,
        base_type_model: type[BaseTypeModel] | None = BaseTypeModel,
        *args,
        **kwargs,
    ):
        """
        Initialize a PydanticModelField for Django models.

        Args:
            pydantic_model (BaseModel | tuple[type[BaseModel]] | dict[str, type[BaseModel]], optional):
                The Pydantic model(s) to use for validation and serialization.
                Can be a single model, a tuple/list of models, or a dict mapping type names to models.
            null (bool, optional): Whether the field allows NULL values. Defaults to True.
            blank (bool, optional): Whether the field allows blank values. Defaults to True.
            validate_default (bool, optional): Whether to validate the default value against the model.
                Defaults to False.
            base_type_model (type[BaseTypeModel] | None, optional): The base type for
                polymorphic models. Defaults to BaseTypeModel.
            *args: Additional positional arguments for the parent class.
            **kwargs: Additional keyword arguments for the parent class.

        Raises:
            ValueError: If the provided pydantic_model or default value is invalid.
        """
        self.base_type_model = base_type_model or BaseTypeModel
        self.default_value = None

        # Validate and set the default value if provided
        if default_value := kwargs.get("default"):
            if validate_default:
                if isinstance(default_value, type):
                    if not (
                        default_value
                        and isinstance(pydantic_model, (list, tuple))
                        and issubclass(default_value, (list, tuple))
                    ) and not issubclass(
                        default_value, (BaseModel, self.base_type_model)
                    ):
                        raise ValueError(
                            f"Invalid default value: {default_value}. "
                            f"Expected a subclass of BaseModel or BaseTypeModel, "
                            f"or a tuple/list of such classes matching the pydantic_model. "
                            f"Check that your default value matches the type and structure of your pydantic_model."
                        )
                else:
                    if not (
                        default_value
                        and isinstance(pydantic_model, (list, tuple))
                        and isinstance(default_value, (list, tuple))
                    ) and not isinstance(
                        default_value, (BaseModel, self.base_type_model)
                    ):
                        raise ValueError(
                            f"Invalid default value instance: {default_value}. "
                            f"Expected an instance of BaseModel or BaseTypeModel, "
                            f"or a tuple/list of such instances matching the pydantic_model. "
                            f"Check that your default value matches the type and structure of your pydantic_model."
                        )
            self.default_value = default_value

        # Validate the pydantic_model argument
        if pydantic_model:
            if isinstance(pydantic_model, (list, tuple)):
                if not pydantic_model:
                    raise ValueError(
                        "pydantic_model list/tuple cannot be empty. "
                        "Provide at least one Pydantic model class."
                    )
                for model_class in pydantic_model:
                    if not issubclass(model_class, (BaseModel, self.base_type_model)):
                        raise ValueError(
                            f"Invalid model class in pydantic_model list/tuple: {model_class}. "
                            "All elements must be subclasses of BaseModel or BaseTypeModel."
                        )
            elif isinstance(pydantic_model, dict):
                for key, model_class in pydantic_model.items():
                    if not issubclass(model_class, self.base_type_model):
                        raise ValueError(
                            f"Invalid model class for key '{key}' in pydantic_model dict: {model_class}. "
                            "All values must be subclasses of BaseTypeModel."
                        )
            elif not issubclass(pydantic_model, (BaseModel, self.base_type_model)):
                raise ValueError(
                    f"Invalid pydantic_model: {pydantic_model}. "
                    "Must be a subclass of BaseModel or BaseTypeModel, "
                    "a tuple/list of such classes, or a dict mapping to such classes."
                )

        self.pydantic_model: (
            type[BaseModel]
            | type[BaseTypeModel]
            | None
            | tuple[type[BaseModel] | type[BaseTypeModel]]
            | dict[str, type[BaseModel] | type[BaseTypeModel]]
        ) = pydantic_model

        # Use the custom encoder for JSON serialization
        kwargs["encoder"] = kwargs.get("encoder", PydanticModelFieldEncoder)
        super().__init__(null=null, blank=blank, *args, **kwargs)

    def to_python(
        self, value
    ) -> BaseModel | BaseTypeModel | list[BaseModel] | dict | None:
        """
        Convert the input value from the database or deserialization into a Pydantic model instance,
        a list of model instances, or a dictionary, depending on the configuration of the field.

        Args:
            value (str | dict | list | None): The value to convert, typically from the database.

        Returns:
            BaseModel | BaseTypeModel | list[BaseModel] | dict | None:
                The deserialized Pydantic model(s) or default value.

        Raises:
            ValueError: If the value cannot be deserialized into the expected Pydantic model(s).
        """

        # If the value is a JSON string, attempt to parse it
        if isinstance(value, str):
            try:
                value = json.loads(value)
                if isinstance(value, str):
                    value = json.loads(value)
            except (TypeError, ValueError) as e:
                logger.error(f"Failed to decode JSON string in to_python: {e}")
                raise ValueError(
                    f"Failed to decode JSON string for field '{self.name}': {e}. "
                    "Ensure the value is valid JSON."
                ) from e

        # If a pydantic_model is set and value is not empty, attempt to instantiate the model(s)
        if value and self.pydantic_model:
            try:
                if isinstance(self.pydantic_model, (list, tuple)):
                    # Expecting a list of model instances
                    if not isinstance(value, (list, tuple)):
                        raise ValueError(
                            f"Expected a list/tuple for field '{self.name}', got {type(value).__name__}. "
                            "Check that the stored data matches the expected structure."
                        )
                    data = []
                    ModelClass = self.pydantic_model[0]
                    for idx, x in enumerate(value):
                        try:
                            data.append(ModelClass(**x))
                        except Exception as e:
                            raise ValueError(
                                f"Failed to instantiate {ModelClass.__name__} at index "
                                f"{idx} for field '{self.name}': {e}. "
                                "Check that each item matches the model schema."
                            ) from e
                    return data
                elif isinstance(self.pydantic_model, dict):
                    # Expecting a dict with a "type" key and "data" payload
                    if not isinstance(value, dict):
                        try:
                            value = dict(value)
                        except (TypeError, ValueError):
                            raise ValueError(
                                f"Expected a dict for field '{self.name}', got {type(value).__name__}. "
                                "Check that the stored data matches the expected structure."
                            )
                    model_type = value.get("type")
                    ModelClass = self.pydantic_model.get(model_type)
                    if not ModelClass:
                        raise ValueError(
                            f"Invalid or missing 'type' key '{model_type}' for field '{self.name}'. "
                            f"Valid types: {list(self.pydantic_model.keys())}. "
                            "Check that the 'type' field is present and correct."
                        )
                    data_payload = value.get("data", {})
                    try:
                        return ModelClass(**data_payload)
                    except Exception as e:
                        raise ValueError(
                            f"Failed to instantiate {ModelClass.__name__} "
                            f"for type '{model_type}' in field '{self.name}': {e}. "
                            "Check that the 'data' payload matches the model schema."
                        ) from e
                elif issubclass(self.pydantic_model, (BaseModel, self.base_type_model)):
                    # Expecting a single model instance
                    if not isinstance(value, dict):
                        try:
                            value = dict(value)
                        except (TypeError, ValueError):
                            raise ValueError(
                                f"Expected a dict for field '{self.name}', got {type(value).__name__}. "
                                "Check that the stored data matches the expected structure."
                            )

                    try:
                        return self.pydantic_model(**value)
                    except Exception as e:
                        raise ValueError(
                            f"Failed to instantiate {self.pydantic_model.__name__} for field '{self.name}': {e}. "
                            "Check that the value matches the model schema."
                        ) from e
                else:
                    raise ValueError(
                        f"Invalid pydantic_model configuration for field '{self.name}'. "
                        "Check that the field is configured with a valid Pydantic model, list, or dict."
                    )
            except Exception as exc:
                logger.exception(f"Invalid data for field '{self.name}': {exc}")
                if self.default_value:
                    return self.__get_default_instance()
                raise exc
        elif self.default_value:
            return self.__get_default_instance()

        # Return the value as-is if no model is set or value is empty
        return value

    def __get_default_value(self) -> str:
        """
        Returns the default value for the field, serialized as a JSON string.

        Returns:
            str: The JSON-encoded default value, which matches the structure expected by the field's pydantic_model.

        Raises:
            ValueError: If the default value cannot be serialized due to a type mismatch or invalid structure.
        """
        # Determine the base value structure based on the pydantic_model type
        value: list | dict = (
            [] if isinstance(self.pydantic_model, (list, tuple)) else {}
        )

        if self.default_value:
            # If the default value is callable (e.g., a function or lambda), call it to get the value
            if callable(self.default_value):
                default_value: BaseModel | BaseTypeModel | list | tuple = (
                    self.default_value()
                )
            else:
                default_value: BaseModel | BaseTypeModel | list | tuple = (
                    self.default_value
                )

            try:
                # For list/tuple pydantic_model, wrap the default value in a list if it's not already a list/tuple
                if isinstance(self.pydantic_model, (list, tuple)):
                    if isinstance(default_value, (list, tuple)):
                        value = [item.model_dump(mode="json") for item in default_value]
                    else:
                        value = [default_value.model_dump(mode="json")]
                else:
                    # For single model, just dump the default value
                    value = default_value.model_dump(mode="json")
            except AttributeError as e:
                raise ValueError(
                    f"Failed to serialize default value for field '{self.name}': {e}. "
                    f"Ensure the default value is an instance of the expected Pydantic model(s) "
                    f"({self.pydantic_model}) and implements 'model_dump(mode=\"json\")'."
                ) from e
            except Exception as e:
                raise ValueError(
                    f"Unexpected error while serializing default value for field '{self.name}': {e}. "
                    f"Check that the default value matches the structure and type of the pydantic_model."
                ) from e

        try:
            return json.dumps(value)
        except Exception as e:
            raise ValueError(
                f"Failed to encode default value to JSON for field '{self.name}': {e}. "
                f"Check that the value is serializable and matches the expected structure."
            ) from e

    def __get_default_instance(
        self,
    ) -> BaseModel | BaseTypeModel | list[BaseModel] | dict | None:
        """
        Returns the default instance for the field, matching the structure expected by the field's pydantic_model.

        Returns:
            BaseModel | BaseTypeModel | list[BaseModel] | dict | None: The default instance(s) for the field.

        Raises:
            ValueError: If the default value is not compatible with the pydantic_model configuration.
        """
        if self.default_value:
            # If the default value is callable (e.g., a function or lambda), call it to get the value
            if callable(self.default_value):
                default_value: BaseModel | BaseTypeModel | list | tuple = (
                    self.default_value()
                )
            else:
                default_value: BaseModel | BaseTypeModel | list | tuple = (
                    self.default_value
                )

            # For list/tuple pydantic_model, wrap the default value in a list if it's not already a list/tuple
            if isinstance(self.pydantic_model, (list, tuple)):
                if not isinstance(default_value, (list, tuple)):
                    return [default_value]
                return default_value
            else:
                return default_value

        # If no default value is set, return an empty list or dict based on the pydantic_model type
        if isinstance(self.pydantic_model, (list, tuple)):
            return []
        elif isinstance(self.pydantic_model, dict):
            return {}
        elif self.pydantic_model is None:
            return None
        else:
            raise ValueError(
                f"Unable to determine a default instance for field '{self.name}'. "
                f"Check that the field's pydantic_model is configured correctly and a valid default value is provided. "
                f"pydantic_model: {self.pydantic_model}, default_value: {self.default_value}"
            )

    def from_db_value(
        self, value: str | dict | list | None, expression, connection
    ) -> BaseModel | BaseTypeModel | list[BaseModel] | dict | None:
        """
        Converts a value as returned by the database to a Python object.

        Args:
            value (str | dict | list | None): The value from the database.
            expression: The expression used in the query (unused).
            connection: The database connection (unused).

        Returns:
            BaseModel | BaseTypeModel | list[BaseModel] | dict | None:
                The deserialized Pydantic model(s) or default value.

        Raises:
            ValueError: If the value cannot be deserialized into the expected Pydantic model(s).
        """
        try:
            return self.to_python(value)
        except Exception as exc:
            logger.exception(
                f"Error in from_db_value for field '{self.name}': {exc}. "
                f"Value from DB: {value!r}. "
                f"Expected pydantic_model: {self.pydantic_model!r}. "
                "Check that the stored data matches the expected structure and type."
            )
            raise ValueError(
                f"Failed to convert database value for field '{self.name}': {exc}. "
                f"Value: {value!r}. "
                f"Expected model: {self.pydantic_model!r}. "
                "Ensure the database value is valid and matches the expected schema."
            ) from exc

    def get_prep_value(
        self, value: BaseModel | BaseTypeModel | list[BaseModel] | None
    ) -> str:
        """
        Prepare the value for storage in the database by serializing it to a JSON string.
        Handles single Pydantic models, lists/tuples of models, and polymorphic dict-based models.

        Args:
            value (BaseModel | BaseTypeModel | list[BaseModel] | None): The value to serialize.

        Returns:
            str: The JSON-encoded value suitable for database storage.

        Raises:
            ValueError: If the value does not match the expected structure or type for the configured pydantic_model.
        """
        if value is None or not self.pydantic_model:
            return self.__get_default_value()

        data = {}

        if isinstance(self.pydantic_model, (list, tuple)):
            # Expecting a list/tuple of model instances
            if not isinstance(value, (list, tuple)):
                raise ValueError(
                    f"Invalid value for field '{self.name}': Expected a list or tuple "
                    "because pydantic_model is a list/tuple, "
                    f"but got {type(value).__name__}. Value: {value!r}. "
                    "Ensure you are passing a list/tuple of model instances matching the pydantic_model."
                )
            data = []
            ModelClass = self.pydantic_model[0]
            for idx, model_instance in enumerate(value):
                if not isinstance(model_instance, ModelClass):
                    raise ValueError(
                        f"Invalid item at index {idx} for field '{self.name}': "
                        f"Expected instance of {ModelClass.__name__}, "
                        f"but got {type(model_instance).__name__}. Value: {model_instance!r}. "
                        "Check that all items in the list/tuple are instances of the correct Pydantic model."
                    )
                data.append(model_instance.model_dump(mode="json"))
        elif isinstance(self.pydantic_model, dict):
            # Expecting a polymorphic model (dict with "type" and "data")
            if not isinstance(value, self.base_type_model):
                raise ValueError(
                    f"Invalid value for field '{self.name}': Expected an instance of {self.base_type_model.__name__} "
                    f"because pydantic_model is a dict, but got {type(value).__name__}. Value: {value!r}. "
                    "Ensure you are passing a valid polymorphic model instance."
                )
            _type = getattr(value, "type", None)
            if not _type:
                raise ValueError(
                    f"Missing 'type' attribute in value for field '{self.name}': {value!r}. "
                    "Polymorphic models must have a 'type' attribute to determine the correct model class."
                )
            model_type = _type
            ModelClass = self.pydantic_model.get(model_type)
            if ModelClass is None:
                raise ValueError(
                    f"Invalid model type '{model_type}' for field '{self.name}'. "
                    f"Allowed types: {list(self.pydantic_model.keys())}. Value: {value!r}. "
                    "Check that the 'type' attribute matches one of the configured model types."
                )
            if not isinstance(value, ModelClass):
                raise ValueError(
                    f"Type mismatch for field '{self.name}': Value is of type {type(value).__name__}, "
                    f"but expected {ModelClass.__name__} for model type '{model_type}'. Value: {value!r}. "
                    "Ensure the value matches the expected model class for its type."
                )
            data = {"type": model_type, "data": value.model_dump(mode="json")}
        elif issubclass(self.pydantic_model, (BaseModel, self.base_type_model)):
            # Expecting a single Pydantic model instance
            if not isinstance(value, BaseModel):
                if not value:
                    return value
                raise ValueError(
                    f"Invalid value for field '{self.name}': Expected an instance of BaseModel or BaseTypeModel "
                    f"({self.pydantic_model.__name__}), but got {type(value).__name__}. Value: {value!r}. "
                    "Check that you are passing a valid Pydantic model instance."
                )
            return value.model_dump_json()
        else:
            raise ValueError(
                f"Invalid pydantic_model configuration for field '{self.name}': {self.pydantic_model!r}. "
                "Check that the field is configured with a valid Pydantic model, list, or dict."
            )
        try:
            return json.dumps(data)
        except Exception as e:
            raise ValueError(
                f"Failed to encode value to JSON for field '{self.name}': {e}. Data: {data!r}. "
                "Ensure the value is serializable and matches the expected structure."
            ) from e

    def value_to_string(self, obj) -> str:
        """
        Serializes the field's value from the given model instance to a JSON
        string for use in fixtures or serialization.

        Args:
            obj: The model instance from which to retrieve the field value.

        Returns:
            str: The JSON-encoded string representation of the field's value.

        Raises:
            ValueError: If the value cannot be serialized due to a type mismatch or invalid structure.
        """
        try:
            value = self.value_from_object(obj)
            return self.get_prep_value(value)
        except Exception as exc:
            raise ValueError(
                f"Failed to serialize value for field '{self.name}' in value_to_string: {exc}. "
                f"Object: {obj!r}. "
                "Ensure the value is compatible with the configured pydantic_model and is serializable to JSON."
            ) from exc


class PydanticModelSerializerField(serializers.JSONField):
    """
    Example:
        class TestModelRetrieve(serializers.ModelSerializer):
            data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.data.field.pydantic_model
            )\n
            list_data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.list_data.field.pydantic_model
            )\n
            type_data = PydanticModelSerializerField(
                pydantic_model=modelsv2.TestModel.type_data.field.pydantic_model
            )\n

            class Meta:
                model = modelsv2.TestModel\n
                fields = [
                    "data",
                    "list_data",
                    "type_data",
                ]


        data with different type will be

        {
            "type":"WORD_PLAY",
            "data":{
                "key1":"value1",
            }
        }

    Args:
        serializers (_type_): _description_
    """

    def __init__(
        self,
        pydantic_model: type[BaseModel]
        | tuple[type[BaseModel]]
        | dict[str, type[BaseModel]]
        | None = None,
        *args,
        **kwargs,
    ):
        """
        Initialize a PydanticModelSerializerField for DRF serializers.

        Args:
            pydantic_model (type[BaseModel] | tuple[type[BaseModel]] | dict[str, type[BaseModel]] | None, optional):
                The Pydantic model(s) to use for validation and serialization.
                Can be a single model, a tuple/list of models, or a dict mapping type names to models.
            *args: Additional positional arguments for the parent class.
            **kwargs: Additional keyword arguments for the parent class.

        Raises:
            ValueError: If the provided pydantic_model is invalid.
        """
        self.pydantic_model = pydantic_model
        try:
            super().__init__(*args, **kwargs)
        except Exception as exc:
            raise ValueError(
                f"Failed to initialize PydanticModelSerializerField with pydantic_model={pydantic_model!r}: {exc}. "
                "Check that the pydantic_model argument is a valid Pydantic model class, a tuple/list of such "
                "classes, or a dict mapping to such classes. "
                "Also ensure that any additional arguments are compatible with DRF's JSONField."
            ) from exc

    def to_internal_value(self, data: dict):
        try:
            if self.pydantic_model:
                if isinstance(self.pydantic_model, (list, tuple)):
                    deserialized_data = []
                    ModelClass = self.pydantic_model[0]
                    for item in data:
                        deserialized_data.append(ModelClass(**item))
                    return deserialized_data
                elif isinstance(self.pydantic_model, dict):
                    ModelClass = self.pydantic_model.get(data.get("type"))
                    if not ModelClass:
                        raise serializers.ValidationError(
                            f"Invalid type; {data.get('type')}"
                        )
                    return ModelClass(**data)
                elif issubclass(self.pydantic_model, (BaseModel, BaseTypeModel)):

                    return self.pydantic_model(**data)
                else:
                    raise serializers.ValidationError("Invalid data")
            return data
        except PydanticValidationError as e:
            raise serializers.ValidationError(e.json())

    def to_representation(self, value) -> str | dict | list | None:
        """
        Serializes the internal value (Pydantic model instance(s)) to a JSON-compatible Python object
        for use in API responses.

        Args:
            value: The internal value to serialize, which may be a Pydantic model instance, a list of instances,
                   or a dict, depending on the field configuration.

        Returns:
            str | dict | list | None: The serialized representation suitable for JSON encoding.

        Raises:
            serializers.ValidationError: If serialization fails due to a type mismatch or invalid structure,
                with a comprehensive error message indicating the root cause.
        """
        try:
            # Use the PydanticModelField logic to serialize the value to a JSON string
            data = PydanticModelField(self.pydantic_model).get_prep_value(value)
            if isinstance(data, str):
                data = json.loads(data)
            # If the data is a dict with "type" and "data" keys, and the type matches the nested data's type,
            # flatten the structure for cleaner API output
            if (
                data
                and isinstance(data, dict)
                and sorted(list(data.keys())) == sorted(["data", "type"])
                and data.get("type")
                and data.get("type") == data.get("data", {}).get("type")
            ):
                data = data.get("data")
            return data
        except Exception as exc:
            raise serializers.ValidationError(
                f"Failed to serialize value for field "
                f"'{self.field_name if hasattr(self, 'field_name') else ''}' in to_representation: {exc}. "
                f"Value: {value!r}. "
                f"pydantic_model: {self.pydantic_model!r}. "
                "Ensure the value is compatible with the configured pydantic_model and is serializable to JSON. "
                "Check for type mismatches, missing required fields, or invalid model structure."
            ) from exc

    def _format_validation_error(self, error: Exception) -> list[dict[str, str]] | str:
        """
        Formats a PydanticValidationError or any other exception into a comprehensive error message
        that helps developers understand the root cause of the error.

        Args:
            error (Exception): The exception to format, typically a PydanticValidationError.

        Returns:
            list[dict[str, str]] | str: A list of error details (field and message) if available,
            or a string with the error message.
        """
        if isinstance(error, PydanticValidationError):
            error_messages = []
            for err in error.errors():
                # Each err is a dict with keys like 'loc', 'msg', 'type'
                field_path = ".".join(str(loc) for loc in err.get("loc", []))
                message = (
                    f"{err.get('msg', '')} (type: {err.get('type', '')})"
                    if "type" in err
                    else err.get("msg", "")
                )
                error_messages.append(
                    {
                        "field": field_path,
                        "message": (
                            f"Validation error on field '{field_path}': {message}. "
                            f"Input value: {err.get('input', 'N/A')}. "
                            "Check that the value matches the expected type and constraints."
                        ),
                    }
                )
            return error_messages
        # For non-Pydantic errors, return a detailed string
        return (
            f"Unexpected error: {str(error)}. "
            "Check the stack trace and ensure the input data and model configuration are correct."
        )
