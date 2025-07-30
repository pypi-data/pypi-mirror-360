from datetime import datetime, date, time
from typing import Union
from uuid import UUID

VAL = Union[int, bool, str, float, UUID, datetime, date, time]
NVAL = Union[VAL, None]


def is_uuid(val: str, ver: int = 4) -> bool:
    try:
        return str(UUID(val, version=ver)) == val
    except ValueError:
        return False


class SchemaField:
    def __init__(self, name: str, schema: dict):
        self.name = name
        self.typ = schema.get('typ')
        self.req = schema.get('req', True)
        self.min = schema.get('min', 0)
        self.max = schema.get('max', 0)
        self.len = schema.get('len', 0)
        self.iss = schema.get('iss', f"Field '{name}' is either missing or invalid.")
        self.prop: Union[dict[str, dict[str, VAL]], None] = schema.get('prop')
        self.enum = schema.get('enum')

        if not self.typ or self.typ not in {'int', 'bool', 'str', 'uuid', 'float', 'list', 'dict'}:
            self.error = f"Schema field '{name}' has missing/invalid 'type' attribute."
        else:
            self.error = None


class Validation:
    def __init__(self) -> None:
        self.errors = []
        self.is_valid = True

    def validate(self, field: SchemaField, key: str, value: NVAL) -> None:
        hints = []
        val_str = str(value) if value is not None else ""

        if field.req and (value is None or val_str == ''):
            hints.append(f"Field '{key}' is required.")

        if field.min > 0 and len(val_str) < field.min:
            hints.append(f"Field '{key}' must have a minimum length of {field.min}.")

        if 0 < field.max < len(val_str):
            hints.append(f"Field '{key}' must have a maximum length of {field.max}.")

        if field.len > 0 and len(val_str) != field.len:
            hints.append(f"Field '{key}' must be of length {field.len}.")

        if field.typ == 'uuid':
            if not is_uuid(val_str):
                hints.append(f"Field '{key}' is not a valid UUID.")
        elif value is not None and type(value).__name__ != field.typ:
            hints.append(f"Field '{key}' must be of type {field.typ}, {type(value).__name__} provided.")

        if field.enum and value not in field.enum:
            enum_str = ", ".join(map(str, field.enum))
            hints.append(f"Field '{key}' must be one of [{enum_str}].")

        if hints:
            self.errors.append({
                'type': "VALIDATION ERROR",
                'field': key,
                'error': field.iss,
                'hints': hints
            })

    def check(self, schema: dict[str, dict], data: dict) -> None:
        for key, field_schema in schema.items():
            field = SchemaField(name=key, schema=field_schema)

            if field.error:
                self.errors.append({
                    'type': "SCHEMA ERROR",
                    'field': key,
                    'error': field.error
                })
                continue

            value: NVAL = data.get(key)

            if field.typ == 'dict' and isinstance(value, dict) and field.prop:
                self.check(schema=field.prop, data=value)

            self.validate(field=field, key=key, value=value)

        if self.errors:
            self.is_valid = False
