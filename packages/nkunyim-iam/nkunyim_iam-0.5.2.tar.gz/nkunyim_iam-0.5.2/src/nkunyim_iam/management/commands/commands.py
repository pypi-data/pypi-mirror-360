
from abc import ABC, abstractmethod
from datetime import datetime
import importlib.util
import os
from pathlib import Path
import re
import shutil
from typing import Union


from django.conf import settings


PYTHON_FILE_NAME_EXT = ".py"

DATAX_NAME_PREFIX = "Datax_"

DATAX_INPUT_ERROR = "DATAX_INPUT_ERROR"
DATAX_FILE_ERROR = "DATAX_FILE_ERROR"

DATAX_MIGRATE_EXCEPTION = "DATAX_MIGRATE_EXCEPTION"
DATAX_REVERSE_EXCEPTION = "DATAX_REVERSE_EXCEPTION"

DATAX_CLASS_NAME = "DataxMigration"
DATAX_METHOD_MIGRATE = "migrate"
DATAX_METHOD_REVERSE = "reverse"


class DataxBaseCommand(ABC):
    
    def __init__(self, file_name: str) -> None:

        self.base_path = os.path.join(settings.BASE_DIR, 'nkunyim_data/datax')
        
        self.python_file_name = f"{file_name}{PYTHON_FILE_NAME_EXT}"
        
        self.pyhton_file_path = os.path.join(self.base_path, self.python_file_name)
        
        # Create Datax root directory if not exist.
        os.makedirs(self.base_path, exist_ok=True)

        template_dir = Path(__file__).parent.resolve()
        self.template_path =  os.path.join(template_dir, "template.py")


    @abstractmethod
    def go(self) -> Union[str, None]:
        pass

        
    def run(self, method_name: str) -> Union[str, None]:
        try:

            if not os.path.isfile(self.pyhton_file_path):
                return f"{self.python_file_name} is not a valid Datax Migration file."
            
            # Load module spec from file path
            module_name = os.path.splitext(os.path.basename(self.pyhton_file_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, self.pyhton_file_path)

            if spec is None or spec.loader is None:
                return f"Could not load module from {self.python_file_name}"

            # Create a module and execute it
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Get the class from the module
            klass = getattr(module, DATAX_CLASS_NAME)
            instance = klass()

            # Get the method and call it
            method = getattr(instance, method_name)
            result = method()

            return result
            
        except Exception as e:
            return f"{DATAX_FILE_ERROR}: {e}."
        


class DataxNewCommand(DataxBaseCommand):
    
    def __init__(self, input_name: str) -> None:
        name = re.sub(r'[^a-zA-Z]', ' ', input_name)
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        pins = name.split()
        cmd_name = ''.join(pin.capitalize() for pin in pins)
        date_str = datetime.now().strftime("%Y%m%d%H%M%S")
        file_name = f"{DATAX_NAME_PREFIX}{date_str}_{cmd_name}"
        
        super().__init__(file_name=file_name)

    
    def go(self) -> Union[str, None]:
        try:
            # Copy template to implementing project and rename to user input_text 
            shutil.copy2(self.template_path, self.pyhton_file_path)
            
            return None
        except FileNotFoundError:
            return f"{DATAX_FILE_ERROR}: Source file '{self.template_path}' not found."
        except Exception as e:
            return f"{DATAX_FILE_ERROR}: Exception {e}."
        
        
        
class DataxRunCommand(DataxBaseCommand):
    
    def __init__(self, input_name: str) -> None:
        
        if not input_name.startswith(DATAX_NAME_PREFIX):
            input_name = f"{DATAX_NAME_PREFIX}{input_name}"
    
        if input_name.endswith(PYTHON_FILE_NAME_EXT):
            input_name = input_name.split(".")[0]

        super().__init__(file_name=input_name)

            
  
    def go(self) -> Union[str, None]:
        return self.run(method_name=DATAX_METHOD_MIGRATE)

        
        
class DataxRevCommand(DataxBaseCommand):
    
    def __init__(self, input_name: str) -> None:
        
        if not input_name.startswith(DATAX_NAME_PREFIX):
            input_name = f"{DATAX_NAME_PREFIX}{input_name}"
    
        if not input_name.endswith(PYTHON_FILE_NAME_EXT):
            input_name = f"{input_name}{PYTHON_FILE_NAME_EXT}"

        super().__init__(file_name=input_name)

            
  
    def go(self) -> Union[str, None]:
        return self.run(method_name=DATAX_METHOD_REVERSE)

