import json
import os
from typing import Union

from django.conf import settings
from nkunyim_iam.management.commands.commands import DATAX_MIGRATE_EXCEPTION, DATAX_REVERSE_EXCEPTION
from nkunyim_iam.management.commands.migrations import BaseDataxMigration



class DataxMigration(BaseDataxMigration):
    
    def migrate(self) -> Union[str, None]:
        super().migrate()
        
        try:
            # Write your data migration.migrate functions here.
              
            data = {
                "id": "29eb115f-aab8-406b-b6f6-f9050c0bec56",
                "code": "GH",
                "name": "Ghana",
                "phone": "233",
                "capital": "Accra",
                "languages": "en-GH,ak,ee,tw",
                "north": 11.173301,
                "south": 4.736723,
                "east": 1.191781,
                "west": -3.25542,
                "is_active": True,
            }
            
            base_path = os.path.join(settings.BASE_DIR, 'nkunyim_data/json')
            file_path = os.path.join(base_path, "nations.json")
                
            # Create Datax root directory if not exist.
            os.makedirs(base_path, exist_ok=True)
        
            with open(file_path, "w") as json_file:
                json.dump(data, json_file, indent=4, sort_keys=True)
                
            # Return None if successfull
            return None
        except IOError as ex:
            return f"{DATAX_MIGRATE_EXCEPTION}: {ex}"
        except Exception as ex:
            return f"{DATAX_MIGRATE_EXCEPTION}: {ex}"
        
    
    def reverse(self) -> Union[str, None]:
        super().reverse()
        
        try:
            # Write your data migration.reverse functions here
        
        
            # Return None if successfull
            return None
        except Exception as ex:
            return f"{DATAX_REVERSE_EXCEPTION}: {ex}"
    
    