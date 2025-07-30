import json, os
"Bulbasaur, grass, posion, ivysaur"
"Charmander, fire, charmeleon"
class Pokémon:
    def __init__(self, name: str, id: int, types: list[str], evolution: str):
        self.name = name
        self.id = id
        self.types = types
        self.evolution = evolution

    def to_dict(self): # Convert the Pokémon object to a dictionary for easy JSON reading/writing
        return {
            "name": self.name,
            "id": self.id,
            "types": self.types,
            "evolution": self.evolution
        }
    
pokédex = [] # collections of Pokémon objects

DATA_PATH = "pokemons.json"

def load_pokédex():
    global pokédex
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, 'r') as file:
            try:
                data = json.load(file)
                pokédex = [Pokémon(**item) for item in data] # for each item in the JSON data, create a Pokémon object
            except (json.JSONDecodeError, TypeError):
                pokédex = []
    else:
        pokédex = []

def save_pokédex():
    TEMP_DATA_PATH = DATA_PATH + ".tmp"
    with open(TEMP_DATA_PATH, 'w') as file:
        json.dump([pokemon.to_dict() for pokemon in pokédex], file, indent=4)
    os.replace(TEMP_DATA_PATH, DATA_PATH) # replace the old file with the new one

def add_pokemon():
    name = input("Enter Pokémon name: ")
    if not name.strip(): # Check if the name is empty or just whitespace
        print('Please give your Pokémon a name.')
        return
    try:
        id_str = input("Enter Pokémon ID: ")
        id = int(id_str)
        if id <= 0:
            print('ID must be a positive number.')
            return
    except ValueError:
        print('Invalid ID. Please enter a number.')
        return

    types_input = input("Enter Pokémon types (comma separated): ")
    types = [t.strip() for t in types_input.split(',') if t.strip()]
    if not types:
        print('Please provide at least one type for your Pokémon.')
        return
    evolution = input("Enter Pokémon evolution: ")
    if not evolution.strip():
        print('Please provide an evolution for your Pokémon.')
        return
    
    print()

    for pokemon in pokédex:
        if pokemon.name.lower() == name.lower() or pokemon.id == id:
            print(f"\033[1mA Pokémon with that name or ID already exists in your Pokédex!\033[0m")
            return  # Exit the function to prevent adding a duplicate
    new_pokemon = Pokémon(name.strip(), id, types, evolution.strip()) # Create a new Pokémon object with the provided details and append it to the pokédex
    pokédex.append(new_pokemon)
    save_pokédex()
    print(f"\033[1mA {name} has been added to the Pokédex.\033[0m")

def _find_pokemon(search_term, by='name'): #Helper function to find a Pokémon by name or ID
    if by == 'name':
        search_term = search_term.lower()
        for pokemon in pokédex:
            if pokemon.name.lower() == search_term:
                return pokemon
    elif by == 'id':
        try:
            search_id = int(search_term)
            for pokemon in pokédex:
                if pokemon.id == search_id:
                    return pokemon
        except (ValueError, TypeError):
            return None
    return None

def search_pokemon():
    try:
        choice1 = int(input('Would you like to search by name (1) or id (2)? Enter 1 or 2 for your choice: '))
        print()
    except ValueError:
        print("Invalid choice. Please enter a number.")
        return

    if choice1 == 1:
        name = input('Enter Pokémon name to search: ')
        print()
        print(f'Searching for {name} in the Pokédex...')
        pokemon = _find_pokemon(name, by='name')
        if pokemon:
            print(f"\033[1mFound Pokémon: Name: {pokemon.name}, ID: {pokemon.id}, Types: {', '.join(pokemon.types)}, Evolution: {pokemon.evolution}\033[0m")
            return
        print(f"\033[1mPokémon with name: {name} not found.\033[0m")
    elif choice1 == 2:
        id_search = input('Enter Pokémon ID to search: ')
        print()
        print(f'Searching for {id_search} in the Pokédex...')
        pokemon = _find_pokemon(id_search, by='id')
        if pokemon:
            print(f"\033[1mFound Pokémon: Name: {pokemon.name}, ID: {pokemon.id}, Types: {', '.join(pokemon.types)}, Evolution: {pokemon.evolution}\033[0m")
            return
        print("\033[1mPokémon not found.\033[0m")
    else:
        print('Invalid choice, please try again.')


def remove_pokemon():
    """Removes a Pokémon from the Pokédex by name or ID."""
    try:
        choice_str = input('Remove by name (1) or ID (2)? Enter 1 or 2: ')
        print()
        choice = int(choice_str)
    except ValueError:
        print("Invalid input. Please enter 1 or 2.")
        return

    pokemon_to_remove = None
    if choice == 1:
        name = input('Enter Pokémon name to remove: ')
        pokemon_to_remove = _find_pokemon(name, by='name')
    elif choice == 2:
        id_remove = input('Enter Pokémon ID to remove: ')
        pokemon_to_remove = _find_pokemon(id_remove, by='id')
    else:
        print("Invalid choice. Please try again.")
        return

    if pokemon_to_remove:
        confirm = input(f"Are you sure you want to remove {pokemon_to_remove.name}? (y/n): ").lower()
        print()
        if confirm == 'y':
            pokédex.remove(pokemon_to_remove)
            save_pokédex()
            print(f"\033[1mA {pokemon_to_remove.name} has been removed from the Pokédex.\033[0m")
        else:
            print("Removal cancelled.")
    else:
        print("Pokémon not found.")

def view_all():
    if not pokédex:
        print("The Pokédex is empty.")
        return

    # Sort the pokédex list in-place by the name attribute of each Pokémon object
    sorted_pokédex = sorted(pokédex, key=lambda p: p.name.lower())

    print("\033[1m--- All Pokémon in Pokédex ---\033[0m")
    for pokemon in sorted_pokédex:
        print(f"Name: {pokemon.name}, ID: {pokemon.id}, Types: {', '.join(pokemon.types)}, Evolution: {pokemon.evolution}")
    print("\033[1m----------------------------\033[0m")

def main():
    load_pokédex()
    while True:
        print("\n Pokédex Menu:")
        print("1. Add Pokémon")
        print("2. Search Pokémon")
        print("3. Remove Pokémon")
        print("4. View All Pokémon")
        print("5. Exit")
        try:
            choice_str = input("Enter your choice: ")
            print()
            choice = int(choice_str)
        except ValueError:
            print("Invalid choice. Please enter a number.")
            continue
        if choice == 1:
            add_pokemon()
        elif choice == 2:
            search_pokemon()
        elif choice == 3:
            remove_pokemon()
        elif choice == 4:
            view_all()
        elif choice == 5:
            save_pokédex()
            print('Pokédex saved successfully.')
            print("Exiting Pokédex.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()


"""Now, Some lines may look confusing to new people so let me explain them, eli15:

Line 28: `pokédex = [Pokémon(**item) for item in data]` 
- This line takes each item in the list called 'data' (which is loaded from the JSON file) and turns it into a Pokémon object. It uses each key-value pair in the dictionary as arguments for the Pokémon class.

Line 36: `json.dump([pokemon.to_dict() for pokemon in pokédex], file, indent=4)` 
- This line converts each Pokémon object back into a dictionary using the `to_dict` method and writes it to the JSON file.

Line 47: `new_pokemon = Pokémon(name.strip(), int(id), [t.strip() for t in types], evolution.strip())`
- This line creates a new Pokémon object with the provided details and appends it to the pokédex. Strips whitespaces from the input.
"""
