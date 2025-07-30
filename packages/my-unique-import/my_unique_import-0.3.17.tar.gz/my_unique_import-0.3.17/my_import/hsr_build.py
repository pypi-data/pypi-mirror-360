import os


def create_character_file(character_name, location=None):
    filename = character_name + '.py' if location is None else os.path.join(location, character_name + '.py')
    if os.path.exists(filename):
        print("File already exists")
        return
    with open(filename, "w") as file:
        file.write(f"""from CharacterMeta import Character
        
        
class {character_name}(Character):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)""")

    print(f"Created {filename}")
    dirtory = os.path.dirname(filename)
    init_file = os.path.join(dirtory, '__init__.py')
    if os.path.exists(init_file):
        with open(init_file, 'r') as file:
            lines = file.readlines()

        with open(init_file, 'w') as file:
            for line in lines:
                if line.strip().startswith('from .'):
                    file.write(line)
                elif line.strip() == '__all__ = [':
                    file.write(line)
                    file.write(f"    '{character_name}',\n")
                else:
                    file.write(line)
            file.write(f"\nfrom .{character_name} import {character_name}\n")
            file.write(f"\n__all__.append('{character_name}')\n")

    else:
        with open(init_file, 'w') as file:
            file.write(f"from .{character_name} import {character_name}\n")
            file.write(f"__all__ = ['{character_name}']\n")


