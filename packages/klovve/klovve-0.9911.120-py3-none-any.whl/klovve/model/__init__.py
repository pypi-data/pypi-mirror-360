#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
import json
import pathlib
import typing as t

import klovve.data
import klovve.timer
from klovve.object import (property, list_property, computed_property, computed_list_property,
                           transformed_list_property, concatenated_list_property, ListTransformer, Object as _Object,
                           WithPublicBind as _WithPublicBind)


@t.dataclass_transform(kw_only_default=True)
class Model(klovve.timer._TimingObject, _Object, _WithPublicBind):

    def __init__(self, **kwargs):
        super().__init__()
        self._initialize_timing()
        self._set_data_by_kwargs(kwargs)


def configuration_model[TModel](model_type: type[TModel], model_args=None, model_kwargs=None, *,
                                app_name: str, config_name: str = "main") -> TModel:
    model = model_type(*(model_args or ()), **(model_kwargs or {}))

    config_dir = pathlib.Path("~").expanduser() / f".config/{app_name}/{config_name}"
    config_dir.mkdir(parents=True, exist_ok=True)

    for property_name, config_property in model._introspect.all_properties.items():
        if config_property.is_settable:
            property_file = config_dir / property_name
            if property_file.exists():
                setattr(model, property_name, json.loads(property_file.read_text()))

            klovve.effect.activate_effect(__ConfigurationModel_WriteValueToDiskEffect,
                                          (model, property_name, property_file), owner=model)

    return model


class __ConfigurationModel_WriteValueToDiskEffect(klovve.effect.Effect):

    def __init__(self, model: Model, property_name: str, property_file: pathlib.Path):
        super().__init__()
        self.__model = model
        self.__property_name = property_name
        self.__property_file = property_file
        self.__is_first_time = True

    def run(self):
        value = getattr(self.__model, self.__property_name)
        if not self.__is_first_time:
            if isinstance(value, klovve.data.list.List):
                value = list(value)
            self.__property_file.write_text(json.dumps(value))
        self.__is_first_time = False
