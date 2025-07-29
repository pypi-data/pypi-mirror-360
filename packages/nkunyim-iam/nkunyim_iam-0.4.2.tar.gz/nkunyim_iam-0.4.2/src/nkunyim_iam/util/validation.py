from datetime import datetime, date, time
from typing import Union
from uuid import UUID


VAL = Union[int, bool, str, float, UUID, datetime, date, time]
NVAL = Union[VAL, None]


def is_uuid(val:str, ver:int=4) -> bool:
    try:
        uuid_obj = UUID(val, version=ver)
        return str(uuid_obj) == val
    except ValueError:
        return False


class SchemaField:
    
    def __init__(self, name:str, schema:dict):
    
        self.error = None
        self.name = name
        self.typ = str(schema['typ']) if 'typ' in schema else None
        self.req = bool(schema['req']) if 'req' in schema else True
        self.min = int(schema['min']) if 'min' in schema else 0
        self.max = int(schema['max']) if 'max' in schema else 0
        self.len = int(schema['len']) if 'len' in schema else 0
        self.iss = str(schema['iss']) if 'iss' in schema else f"Field '{name}' is either missing or invalid."
        self.prop: Union[dict[str, dict[str, VAL]], None] = dict(schema['prop']) if 'prop' in schema else None
        
        if not (self.typ and self.typ in ['int', 'bool', 'str', 'uuid', 'float', 'list', 'dict']) :
            self.error = f"Schema field '{name}' has missing/invalid 'type' attribute."



class Validation:
    
    def __init__(self) -> None:
        self.errors = []
        self.is_valid = True


    def validate(self, field: SchemaField, key: str, value: NVAL) -> None:
        hints = []
        
        if field.req == True and bool(value is None or value == ''):
            hints.append(f"Field '{key}' is required.")
            
        if field.min > 0 and len(str(value)) < field.min:
            hints.append(f"Field '{key}' must have a minimum lenght of {str(field.min)}.")
            
        if 0 < field.max < len(str(value)):
            hints.append(f"Field '{key}' must have a maximum lenght of {str(field.max)}.")
            
        if field.len > 0 and not (len(str(value)) == field.len):
            hints.append(f"Field '{key}' must be of lenght {str(field.len)}.")
            
        if field.typ == 'uuid':
            if not is_uuid(val=str(value)):
                hints.append(f"Field '{key}' is not a valid UUID.")
        elif type(value).__name__ != field.typ:
            hints.append(f"Field '{key}' must be of type {field.typ}, {type(value).__name__} provided.")
            
        if len(hints) > 0:
            self.errors.append({
                'type': "VALIDATION ERROR",
                'field': key,
                'error': field.iss,
                'hints': hints
            })

        
    def check(self, schema: dict[str, dict], data: dict) -> None:
        for key in list(schema.keys()):
            field = SchemaField(name=key, schema=schema[key])
            if field.error:
                self.errors.append({
                    'type': "SCHEMA ERROR",
                    'field': key,
                    'error': field.error
                })
            
            value: NVAL = data[key] if key in  data else None
            
            if field.typ == 'dict' and field.prop and value:
                self.check(schema=field.prop, data=dict(value))
            
            self.validate(field=field, key=key, value=value)
            
        if len(self.errors) > 0:
            self.is_valid = False
