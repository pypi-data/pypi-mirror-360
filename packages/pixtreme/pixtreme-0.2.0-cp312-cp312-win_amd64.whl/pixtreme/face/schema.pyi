from __future__ import annotations
import builtins as __builtins__
import cupy
import cupy as cp
import inspect
import pydantic._internal._decorators
from pydantic.config import ConfigDict
from pydantic.fields import Field
import pydantic.main
from pydantic.main import BaseModel
import pydantic_core._pydantic_core
import typing
__all__ = ['BaseModel', 'ConfigDict', 'Field', 'PxFace', 'cp']
class PxFace(pydantic.main.BaseModel):
    __abstractmethods__: typing.ClassVar[frozenset]  # value = frozenset()
    __class_vars__: typing.ClassVar[set] = set()
    __private_attributes__: typing.ClassVar[dict] = {}
    __pydantic_complete__: typing.ClassVar[bool] = True
    __pydantic_computed_fields__: typing.ClassVar[dict] = {}
    __pydantic_core_schema__: typing.ClassVar[dict] = {'type': 'model', 'cls': PxFace, 'schema': {'type': 'model-fields', 'fields': {'bbox': {'type': 'model-field', 'schema': {'type': 'is-instance', 'cls': cupy.ndarray}, 'metadata': {'pydantic_js_updates': {'description': 'Bounding box in the format (x1, y1, x2, y2)'}}}, 'score': {'type': 'model-field', 'schema': {'type': 'float'}, 'metadata': {'pydantic_js_updates': {'description': 'Detection score'}}}, 'kps': {'type': 'model-field', 'schema': {'type': 'default', 'schema': {'type': 'nullable', 'schema': {'type': 'is-instance', 'cls': cupy.ndarray}}, 'default': None}, 'metadata': {'pydantic_js_updates': {'description': 'Keypoints in the format (x, y)'}}}, 'matrix': {'type': 'model-field', 'schema': {'type': 'default', 'schema': {'type': 'nullable', 'schema': {'type': 'is-instance', 'cls': cupy.ndarray}}, 'default': None}, 'metadata': {'pydantic_js_updates': {'description': 'Affine transformation matrix'}}}, 'embedding': {'type': 'model-field', 'schema': {'type': 'default', 'schema': {'type': 'nullable', 'schema': {'type': 'is-instance', 'cls': cupy.ndarray}}, 'default': None}, 'metadata': {'pydantic_js_updates': {'description': 'Face embedding'}}}, 'normed_embedding': {'type': 'model-field', 'schema': {'type': 'default', 'schema': {'type': 'nullable', 'schema': {'type': 'is-instance', 'cls': cupy.ndarray}}, 'default': None}, 'metadata': {'pydantic_js_updates': {'description': 'Normalized face embedding'}}}, 'image': {'type': 'model-field', 'schema': {'type': 'default', 'schema': {'type': 'nullable', 'schema': {'type': 'is-instance', 'cls': cupy.ndarray}}, 'default': None}, 'metadata': {'pydantic_js_updates': {'description': 'Face image'}}}}, 'model_name': 'PxFace', 'computed_fields': list()}, 'custom_init': False, 'root_model': False, 'config': {'title': 'PxFace'}, 'ref': 'pixtreme.face.schema.PxFace:2010195390704', 'metadata': {'pydantic_js_functions': [pydantic.main.BaseModel.__get_pydantic_json_schema__]}}
    __pydantic_custom_init__: typing.ClassVar[bool] = False
    __pydantic_decorators__: typing.ClassVar[pydantic._internal._decorators.DecoratorInfos]  # value = DecoratorInfos(validators={}, field_validators={}, root_validators={}, field_serializers={}, model_serializers={}, model_validators={}, computed_fields={})
    __pydantic_fields__: typing.ClassVar[dict]  # value = {'bbox': FieldInfo(annotation=ndarray, required=True, description='Bounding box in the format (x1, y1, x2, y2)'), 'score': FieldInfo(annotation=float, required=True, description='Detection score'), 'kps': FieldInfo(annotation=Union[ndarray, NoneType], required=False, default=None, description='Keypoints in the format (x, y)'), 'matrix': FieldInfo(annotation=Union[ndarray, NoneType], required=False, default=None, description='Affine transformation matrix'), 'embedding': FieldInfo(annotation=Union[ndarray, NoneType], required=False, default=None, description='Face embedding'), 'normed_embedding': FieldInfo(annotation=Union[ndarray, NoneType], required=False, default=None, description='Normalized face embedding'), 'image': FieldInfo(annotation=Union[ndarray, NoneType], required=False, default=None, description='Face image')}
    __pydantic_generic_metadata__: typing.ClassVar[dict] = {'origin': None, 'args': tuple(), 'parameters': tuple()}
    __pydantic_parent_namespace__: typing.ClassVar[dict]  # value = {'f': <pydantic._internal._model_construction._PydanticWeakRef object>, 'args': (pixtreme.face.schema), 'kwds': {}}
    __pydantic_post_init__ = None
    __pydantic_serializer__: typing.ClassVar[pydantic_core._pydantic_core.SchemaSerializer]  # value = SchemaSerializer(serializer=Model(...
    __pydantic_setattr_handlers__: typing.ClassVar[dict] = {}
    __pydantic_validator__: typing.ClassVar[pydantic_core._pydantic_core.SchemaValidator]  # value = SchemaValidator(title="PxFace", validator=Model(...
    __signature__: typing.ClassVar[inspect.Signature]  # value = <Signature (*, bbox: cupy.ndarray, score: float, kps: cupy.ndarray | None = None, matrix: cupy.ndarray | None = None, embedding: cupy.ndarray | None = None, normed_embedding: cupy.ndarray | None = None, image: cupy.ndarray | None = None) -> None>
    _abc_impl: typing.ClassVar[_abc._abc_data]  # value = <_abc._abc_data object>
    model_config: typing.ClassVar[dict] = {'arbitrary_types_allowed': True}
__test__: dict = {}
