import os
import glob
from pathlib import Path

CURRENT_DIR = Path(__file__).parent.resolve()

def resolve_path(path):
    return str(CURRENT_DIR / path)

def clear_folder(folder_path):
    try:
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f'{file_name} deleted')
    except Exception as e:
        print(e)


def clear_specific_files(folder_path, file_pattern):
    try:
        for file_name in glob.glob(os.path.join(folder_path, file_pattern)):
            os.remove(file_name)
            print(f'{file_name} deleted')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    folders_1 = [
        '../data/output',
        'modules/m02_mention_extraction_typing/logs',
        'modules/m03_entity_resolution_disambiguation/logs',
        'modules/m04_local_relation_extraction/logs',
        'modules/m05_global_relation_extraction/logs',
        'modules/m06_schema_generation/logs',
    ]

    
    for folder in folders_1:
        clear_folder(resolve_path(folder))

    folders_2 = [
        'modules/m01_kg_preprocessing',
        'modules/m02_mention_extraction_typing',
        'modules/m03_entity_resolution_disambiguation',
        'modules/m04_local_relation_extraction',
        'modules/m05_global_relation_extraction',
        'modules/m06_schema_generation',
        'modules/m07_kg_postprocessing',
    ]

    for folder in folders_2:
        clear_specific_files(resolve_path(folder), 'kg_*.json')

    