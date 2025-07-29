import builtins
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import datetime
from dill.source import getsource
from functools import partial, wraps
import json
from inspect import isclass
import logging
from typing import Annotated, Callable, ClassVar, Dict, List, Optional, Union

from fastapi_utils.cbv import cbv as controller
from fastapi.encoders import jsonable_encoder
from pydantic_core._pydantic_core import ValidationError
from pydantic import BaseModel, Field, parse_obj_as, PrivateAttr, field_validator, PlainSerializer, BeforeValidator
from pydantic._internal._model_construction import ModelMetaclass
from pytz import UTC
from redis import Redis

from chaiverse.chaiverse_secrets import scrub_secrets
from chaiverse.database import _FirebaseDatabase
from chaiverse.lib.dict_tools import deep_get
from chaiverse.lib.func import deserialize_function
from chaiverse.lib.func import is_base_64


class class_property(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class InfernoLogEntry(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    entry: str
    level: str
    line_number: int
    path: str

    @staticmethod
    def from_logging_record(record: logging.LogRecord):
        entry = str(scrub_secrets(record.msg))
        log_entry = InfernoLogEntry(
            timestamp=datetime.utcfromtimestamp(record.created).replace(tzinfo=UTC),
            entry=entry,
            level=record.levelname,
            line_number=record.lineno,
            path=record.pathname
        )
        return log_entry


class RecordNotFoundError(Exception):
    pass


class InfernoModel(BaseModel):
    """
    Inferno is a light-weight object relational-mapper (ORM/ODM)
    for Firebase. It maps records in the database to python
    objects to ensure type-safety, validation and encourage
    cleaner coding standards when interfacing with the database.
    """
    database: ClassVar[_FirebaseDatabase]
    path: ClassVar[str]
    # Must set execlude as otherwise pydantic tries to
    # serialize it
    cache: ClassVar[Optional[Redis]] = Field(exclude=True)

    logs: Optional[List[InfernoLogEntry]] = None

    class Config:
        arbitrary_types_allowed = True

    @class_property
    def lazy(cls):
        # Mixin lazy behaviour into base class
        lazy_class = type(f"Lazy{cls.__name__}", (LazyInfernoModelMixin, cls), {})
        return lazy_class

    @classmethod
    def create(cls, **kwargs):
        data = cls(**kwargs)
        msg = f'entry with id "{data.id}" already exists in database! Please use a different id'
        assert not cls.is_in_database(**{cls._id: data.id}), msg
        return data

    @classmethod
    def from_id(cls, default=None, **kwargs):
        instance_id = cls._get_instance_id(kwargs)
        data = cls.database.get(path=f'{cls.path}/{instance_id}') or default
        if data is None:
            raise RecordNotFoundError(f'no entry with id "{instance_id}" found on database!')
        if cls._id not in data:
            data[cls._id] = instance_id
        return cls(**data)

    @classmethod
    def from_records(cls, records):
        instances = []
        for record in records:
            try:
                instance = cls(**record)
                instances.append(instance)
            except ValidationError as ex:
                logging.error(str(ex))
        return instances

    @classmethod
    def where(cls, **kwargs):
        records = cls.database.where(path=cls.path, **kwargs)
        return cls.from_records(records)

    @classmethod
    def all(cls, **kwargs):
        all_entries = cls.database.get(path=cls.path)
        all_records = all_entries.values() if all_entries else []
        return cls.from_records(all_records)

    @classmethod
    def paginate(cls, index, limit, order_by=None):
        # Paginate (in reverse order) an Inferno model with a sortable id
        if order_by == None:
            order_by = cls._id
        entries = cls.database.query_by_child_value_range(
            cls.path, order_by, end_at=index, limit_to_last=limit
        )
        entries = cls.from_records(entries.values()) if entries else []
        entries.sort(key=lambda x: deep_get(x.to_dict(), order_by), reverse=True)
        return entries

    @classmethod
    def is_in_database(cls, **kwargs):
        instance_id = cls._get_instance_id(kwargs)
        is_in = cls.database.is_in_database(path=f'{cls.path}/{instance_id}')
        return is_in

    def to_dict(self, exclude_none=True, **kwargs):
        serialised_record = jsonable_encoder(
            self, exclude_none=exclude_none, **kwargs
        )
        # Logs are often written in a separate thread, so we drop them if
        # they're none to avoid overwriting
        if "logs" in serialised_record and serialised_record["logs"] == None:
            serialised_record.pop("logs")
        return serialised_record

    def to_lazy(self):
        kwargs = {self.__class__._id: self.id}
        lazy_model = self.lazy.from_id(**kwargs)
        return lazy_model

    @contextmanager
    def register_logger(self, lazy=True):
        handler = InfernoLoggerHandler(inferno_model=self, level=logging.DEBUG, lazy=lazy)
        try:
            root_logger = logging.getLogger()
            root_logger.addHandler(handler)
            yield
        finally:
            root_logger.removeHandler(handler)

    def save(self):
        record = self._build_save_record()
        self.database.multi_update(path="/", record=record)

    def delete(self):
        path = f"{self.path}/{self.id}"
        self.database.remove(path)

    def refresh(self):
        instance_id = getattr(self, self._id)
        data = self.database.get(path=f'{self.path}/{instance_id}')
        new_instance = self.__class__(**data)
        for field in self.__fields__:
            new_value = getattr(new_instance, field)
            self._set_field(field, new_value)

    @property
    def id(self):
        id_field = self.__class__._id
        instance_id = getattr(self, id_field)
        return instance_id

    @classmethod
    def _get_denormalised_fields(cls):
        # Cannot set this as a Pydantic ClassVar as it gets shared across all
        # InfernoModel instances
        denormalised_fields = getattr(cls, "_denormalised_fields", {})
        return denormalised_fields

    @classmethod
    def _get_instance_id(cls, kwargs):
        assert cls._id in kwargs, f'invalid keyword id, please use keyword "{cls._id}"'
        instance_id = kwargs[cls._id]
        return instance_id

    def _build_save_record(self):
        record = {self.path: {self.id: self.to_dict(exclude_none=True)}}
        # TODO: This ensures that if a dictionary field is not set, then it is
        # deleted. This really should be in the Firebase adapter.
        record = _empty_dict_to_none(record)
        for field, path in self._get_denormalised_fields().items():
            denormalised_record = {path: {self.id: self.to_dict(include=[self._id, field])}}
            record.update(denormalised_record)
        return record

    def _set_field(self, field, value):
        new_data = {field: value}
        data = self.to_dict()
        data.update(new_data)
        try:
            self.__class__.model_validate(data)
        except Exception as ex:
            errors = [error for error in ex.errors() if error["loc"][0] in data.keys()]
            if errors:
                new_ex = ValidationError.from_exception_data(
                    title=ex.title,
                    line_errors=errors,
                )
                raise new_ex
        setattr(self, field, value)



class LazyInfernoModelMixin():

    @classmethod
    def construct(cls, **kwargs):
        # Having defaults interferes with how LazyInferno lazy loads an
        # attribute from the db, so we just disable them.
        for name, field in cls.__fields__.items():
            field.default = None
        return cls.model_construct(**kwargs)

    @classmethod
    def from_id(cls, **kwargs):
        assert cls._id in kwargs, f'invalid keyword id, please use keyword "{cls._id}"'
        instance = cls.construct()
        instance_id = kwargs[cls._id]
        instance._set_field(cls._id, instance_id)
        return instance

    @classmethod
    def where(cls, **kwargs):
        assert len(kwargs) == 1, "Cannot perform a lazy where on more than one field!"
        field = list(kwargs.keys())[0]
        assert field in cls._get_denormalised_fields(), f"Cannot perform a lazy where on the field `{field}` as it has not been denormalised!"
        denormalised_path = cls._denormalised_fields[field]
        records = cls.database.where(path=denormalised_path, **kwargs)
        return [cls.construct(**data) for data in records]

    def __getattribute__(self, field):
        value = super().__getattribute__(field)
        # Have to redirect to database if None as optional fields are
        # instantiated with None (and therefore have a value)
        if value is None and field in self.__fields__:
            value = self.__getattr__(field)
        return value

    def __getattr__(self, field):
        if field in self.__fields__:
            value = self.database.get(f"{self.path}/{self.id}/{field}")
            self._set_field(field, value)
        else:
            value = super().__getattribute__(field)
        return value


def get_source(function):
    source = getattr(function, "__source__", None) or _get_source(function)
    return source


def _get_source(function):
    source = getsource(function)
    source = source.lstrip()
    # Check if we need to add an import to facilitate subclasses
    if isclass(function) and len(function.__bases__) > 0:
        source = _get_subclass_source(function, source)
    return source


def _get_subclass_source(function, source):
    assert len(function.__bases__) == 1, "Multi-inheritance not supported!"
    base = function.__bases__[0]
    # If this is a builtin python superclass, there is nothing to do
    if base.__name__ in dir(builtins):
        return source
    module = base.__module__
    package = module.split(".")[1]
    import_source = f"import importlib\n{package} = importlib.import_module('{module}')\n"
    source = import_source + source
    # If the subclass is directly imported, we need to modify the class
    # definition to append the package name
    name = base.__name__
    source = source.replace(f"({name})", f"({package}.{name})")
    return source


def process_callable(func):
    if type(func) == list:
        func = [process_callable(f) for f in func]
    elif type(func) == str and is_base_64(func):
        # Deprecated unsafe base64 functions are rejected
        pass
    elif type(func) == str:
        func = load_function(func)
    elif type(func) == partial:
        func = InfernoPartial.from_orm(func)
    elif isinstance(func, dict):
        func = InfernoPartial(**func)
    elif getattr(func, "__name__", None) == "<lambda>":
        # Seems difficult to get source code of inline lambdas
        raise NotImplementedError("Cannot use lambda callables in Inferno!")
    return func


def load_function(source):
    # Remove any unwanted indentation
    source = source.lstrip()
    locals = {}
    # Execute the python code, with no access to globals, and empty
    # locals for later inspection
    exec(source, None, locals)
    func = list(locals.values())[-1]
    assert callable(func), f"{func} is not callable"
    # Not possible to get source code for function defined by exec
    # so we store it for future reference
    func.__source__ = source
    return func


InfernoCallable = Annotated[
    Callable, PlainSerializer(get_source),
    BeforeValidator(process_callable)
]


class InfernoPartial(BaseModel):
    func: Optional[InfernoCallable] = None
    args: Optional[tuple] = ()
    keywords: Optional[dict] = {}

    @field_validator("args", mode="before")
    def validate_args(cls, args):
        if args == None:
            args = ()
        return args

    @field_validator("keywords", mode="before")
    def validate_kwargs(cls, kwargs):
        if kwargs == None:
            kwargs = {}
        return kwargs

    class Config():
        # Set ORM mode so that we can easily create an InfernoPartial from a
        # partial via pydantic type-hinting
        orm_mode = True
        from_attributes = True

    def __call__(self, *args, **kwargs):
        loaded_partial = partial(self.func, *self.args, **self.keywords)
        return loaded_partial(*args, **kwargs)

    @property
    def __name__(self):
        return self.func.__name__

    @property
    def __wrapped__(self):
        return self.func


class InfernoLoggerHandler(logging.Handler):
    def __init__(self, inferno_model, level, lazy=True):
        super().__init__(level)
        # Convert to lazy to ensure we are not overwriting data in other
        # threads while logging
        self.inferno_model = inferno_model.to_lazy() if lazy else inferno_model

    def emit(self, record):
        log_entry = InfernoLogEntry.from_logging_record(record)
        if not self.inferno_model.logs:
            self.inferno_model.logs = []
        self.inferno_model.logs.append(log_entry)
        self.inferno_model.save()


def _get_pydantic_errors_for_field(validation_error, field):
    errors = [
        err_wrapper for err_wrapper in validation_error.raw_errors
        if err_wrapper.loc_tuple()[0] == field
    ]
    validation_error.raw_errors = errors
    return validation_error


def set_id(field: str):
    def wrapped(cls):
        cls._id = field
        return cls
    return wrapped


class cache():
    def __init__(self, ttl: float):
        self.ttl = ttl
        self.cache_instance = None
        self.function_path = None
        self.function_return_type = None

    def __call__(self, function):
        self.function_path = f"{function.__module__}.{function.__qualname__}"
        self.function_return_type = function.__annotations__.get("return", None)

        @wraps(function)
        def wrapper(*args, **kwargs):
            # To be able to access the cache instance
            nonlocal self
            # Grab the redis cache instance from the InfernoModel's schema
            self.cache_instance = args[0].cache
            value = self.get(*args, **kwargs)
            # Cache miss, so we fallback to the underlying database
            # and then store the value in the cache
            if value is None:
                value = function(*args, **kwargs)
                self.set(value, *args, **kwargs)
            return value
        return wrapper

    def get(self, *args, **kwargs):
        prefix = self.get_prefix(*args, **kwargs)
        value = self.cache_instance.get(prefix)
        if value is not None:
            value = json.loads(value)
            value = self._deserialise_value(args[0], value)
        return value

    def set(self, value, *args, **kwargs):
        prefix = self.get_prefix(*args, **kwargs)
        serialised_record = self._serialise_value(value)
        json_record = json.dumps(serialised_record)
        self.cache_instance.set(prefix, json_record)
        self.cache_instance.expire(prefix, self.ttl)

    def get_prefix(self, *args, **kwargs):
        args = self._get_args_prefix(*args)
        kwargs = self._get_kwargs_prefix(**kwargs)
        if args and kwargs:
            kwargs = ", {kwargs}"
        prefix = f"{self.function_path}({args}{kwargs})"
        return prefix

    def _get_args_prefix(self, *args):
        # The first argument is either the class object
        # or instance object itself, we don't need this in the prefix
        args = list(args)
        args.pop(0)
        args = ", ".join(args)
        return args

    def _get_kwargs_prefix(self, **kwargs):
        kwargs = [f"{key}={value}" for key, value in kwargs.items()]
        kwargs = ", ".join(kwargs)
        return kwargs

    def _deserialise_value(self, cls, value):
        if type(value) == list:
            value = [self._deserialise_value(cls, v) for v in value]
        elif self.function_return_type and issubclass(self.function_return_type, BaseModel):
            value = self.function_return_type(**value)
        elif self.function_return_type:
            assert isinstance(value, self.function_return_type), "Value not of expected return type, custom deserialisation logic needed!"
            pass
        elif isinstance(value, dict):
            # No return type is specified, so we just fallback to trying to
            # deserialise into the InfernoModel this cache is declared within
            value = cls(**value)
        else:
            raise NotImplementedError("Failed to deserialize data from cache!")
        return value

    def _serialise_value(self, value):
        if type(value) == list:
            serialised_record = [self._serialise_value(v) for v in value]
        elif isinstance(value, InfernoModel):
            serialised_record = value.to_dict()
        elif isinstance(value, BaseModel):
            serialised_record = value.dict()
        else:
            serialised_record = value
        return serialised_record


def denormalise_field(field: str, path_format: str = "{path}_{field}_denormalisation"):
    # Used to duplicate information in an Inferno model to improve read
    # performance, as is usually suggested when dealing with NoSQL databases
    # (especially Firebase)
    # See https://firebase.blog/posts/2013/04/denormalizing-your-data-is-normal
    def wrapped(cls):
        denormalisation_path = path_format.format(path=cls.path, field=field)
        cls._denormalised_fields = getattr(cls, "_denormalised_fields", {})
        cls._denormalised_fields[field] = denormalisation_path
        return cls
    return wrapped


class InfernoUnionMetaClass(ModelMetaclass):
    def __setattr__(self, name, value):
        # We do this so we can set database patches at the Union level, and
        # ensure they propogate to the polymorphisms
        # This has to be in a metaclass, because the Inferno database field is
        # a class attribute
        if getattr(self, "database", None) and name == "database":
            for cls in self._polymorphisms:
                cls.database = value
        super().__setattr__(name, value)


class InfernoUnion(InfernoModel, metaclass=InfernoUnionMetaClass):
    """
    Helper class to do polymorphism with InfernoModel.
    Example:
            class BaseSubmission(InfernoModel):
                platform = Literal["base"]

            class RewardSubmission(InfernoModel):
                platform = Literal["reward"]

            Submission = InfernoUnion[BaseSubmission, RewardSubmission]
    This relies on Pydantic's valdiation behaviour to resolve the correct class,
    so each polymorphism must implement a discriminator in a similar fashion to 'platform'
    in the above example.
    """
    @class_property
    def greatest_common_superclass(cls):
        return get_greatest_common_superclass(cls._polymorphisms)

    @class_property
    def lazy(cls):
        lazy_cls = cls.greatest_common_superclass.lazy
        lazy_cls.database = cls.database
        return lazy_cls

    def __new__(cls, *args, **kwargs):
        instance = parse_obj_as(Union[cls._polymorphisms], kwargs)
        return instance

    def __class_getitem__(cls, classes):
        cls._validate_union(classes)
        greatest_common_superclass = get_greatest_common_superclass(classes)
        new_class = type("InfernoUnion", (greatest_common_superclass, InfernoUnion), {})
        new_class._polymorphisms = classes
        new_class.database = classes[0].database
        new_class.path = classes[0].path
        new_class._id = classes[0]._id
        return new_class

    @classmethod
    def _validate_union(cls, item):
        item = item if isinstance(item, Iterable) else [item]
        assert all([isclass(i) for i in item]), "Can only create an InfernoUnion from classes!"
        assert all([issubclass(i, InfernoModel) for i in item]), "Can only create an InfernoUnion from InfernoModels!"
        assert len(set([i.database for i in item])) == 1, "Cannot create an InfernoUnion from InfernoModels with different databases!"
        assert len(set([i.path for i in item])) == 1, "Cannot create an InfernoUnion from InfernoModels with different paths!"


def get_greatest_common_superclass(classes):
    classes = [cls.mro() for cls in classes]
    for x in classes[0]:
        if all(x in mro for mro in classes):
            return x


def crud_controller(inferno_model, router):
    def wrapper(cls):
        # TODO: To ensure we don't override any similar routes that are set in
        # the actual controller that this is applied to, we check this. It's
        # quite mad. Ideally this should just work via inheritance, but that seems broken.
        existing_routes = [(route.path, route.methods) for route in router.routes]
        class InfernoCRUDController():
            if (f"/{inferno_model.path}", {"POST"}) not in existing_routes:
                @router.post(f"/{inferno_model.path}")
                def create(self, model: inferno_model):
                    model.save()
                    model_id = getattr(model, model._id)
                    return {model._id: model_id}

            if (f"/{inferno_model.path}/{{model_id}}", {"GET"}) not in existing_routes:
                @router.get(f"/{inferno_model.path}/{{model_id}}")
                def get(self, model_id: str):
                    model = inferno_model.from_id(**{inferno_model._id: model_id})
                    return model

            if (f"/{inferno_model.path}/{{model_id}}", {"PATCH"}) not in existing_routes:
                @router.patch(f"/{inferno_model.path}/{{model_id}}")
                def patch(self, model_id: str, model: inferno_model):
                    model.save()
                    return model

            if (f"/{inferno_model.path}/{{model_id}}", {"DELETE"}) not in existing_routes:
                @router.delete(f"/{inferno_model.path}/{{model_id}}")
                def delete(self, model_id: str):
                    model = inferno_model.lazy.from_id(**{inferno_model._id: model_id})
                    model.delete()
                    return model

            if (f"/{inferno_model.path}", {"GET"}) not in existing_routes:
                @router.get(f"/{inferno_model.path}")
                def all(self):
                    return inferno_model.all()

        # Mixin the InfernoCRUDController behaviour
        controller_class = type(cls.__name__, (cls, InfernoCRUDController), {})
        # Mixin FastAPI controller behaviour
        controller(router)(controller_class)
        # Install create route
        return controller_class
    return wrapper


def _empty_dict_to_none(mapping):
    for key, value in mapping.items():
        if isinstance(value, dict) and len(value) > 0:
            mapping[key] = _empty_dict_to_none(value)
        elif value == {}:
            mapping[key] = None
    return mapping
