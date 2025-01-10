from modules.bytes_formatter    import bytes_formatter
from modules.db_manager         import database
from unicodedata                import category
from pathlib                    import Path
from shutil                     import get_terminal_size
from json                       import dumps
from modules                    import settings


def show_table(entries: list) -> None:
    """Show the entries in the terminal."""
    if not entries:
        print('No links found. Use "add links" to store new ones.')
        return

    terminal_width = get_terminal_size()[0]
    num_columns = 4
    fixed_cells_total_width = 2 * 12 + 5
    mutable_width = max((terminal_width - fixed_cells_total_width - (num_columns + 1)) // 2, 5)

    header = f"| {'KEY':^5} | {'TITLE':^{mutable_width}} | {'LINK':^{mutable_width}} | {'SIZE':^10} |"
    separator = "-" * len(header)

    rows = ""
    for key, title, link, size, _ in entries:
        sanitized_title = ''.join(char if category(char) not in ["Cs", "So", "Cn"] else '¬' for char in title)
        rows += f"| {key:^5} | {sanitized_title[:mutable_width]:<{mutable_width}} | {link[:mutable_width]:<{mutable_width}} | {bytes_formatter(size):>10} |\n"

    print(f"{header}\n{separator}\n{rows}{separator}")

def add_links(db: database) -> None:
    """Add links into the database."""
    print('How do you want to proceed?')
    print('"one": To add only one through the terminal\n"several": To add from a file named "links.txt"')

    choice = input('> ').lower()
    if choice == "one":
        link = input('Type the link: ')
        db.add_link(link)
        print("Success!")
        
    elif choice == "several":
        file = Path('links.txt')
        if file.exists() and file.stat().st_size > 0:
            for line in file.read_text().splitlines():
                if line.strip():
                    db.add_link(line.strip())
            print("Success!")
        else:
            print('The file "links.txt" doesn\'t exist or it\'s empty.')

    else:
        print("Invalid!")
    db.save_db()

def delete_links(db: database, entries: list) -> None:
    """Remove links from the database."""
    print('Type the KEYs of the links you want to remove separated by commas.')
    print('Ot type "all" to remove every link or "back" to go back.')
    choice = input('> ').lower()

    if choice == "all":
        confirmation = input('Are you sure? [y/n]: ').lower()
        if confirmation.startswith('y'):
            for entry in entries:
                db.rm_link(entry[2])
            db.save_db()
            print("The database is empty now.")
    elif choice == "back":
        return
    else:
        try:
            keys = [int(number.strip()) for number in choice.split(',')]
            for key in keys:
                for entry in entries:
                    if entry[0] == key:
                        db.rm_link(entry[2])
            print("Links removed!")
        except ValueError:
            print("Invalid. Make sure to type numbers separated by commas.")

def save_json(entries: list):
    if not(entries):
        print('No links found. Use "add links" to store new ones.')
        return
    
    file = Path('links to download.json')
    file.write_text(dumps(entries, indent= 4))
    print(f'Saved in "{file.resolve()}".')

def links_page(db: database) -> None:
    """This function is used to manage the database."""
    while True:
        entries = db.read_db()
        show_table(entries)

        print('"Add links"  "Delete links"  "Save to JSON"  "Back"')
        choice = input('> ').lower()

        if choice.startswith("add"):
            add_links(db)
        elif choice.startswith("del"):
            delete_links(db, entries)
        elif choice.startswith('save'):
            save_json(entries)
        elif choice.startswith("back"):
            break
        else:
            print("Invalid!")

def settings_page():
    '''Get the user settings.'''
    sets = settings.read_sets()
    text = f'Settings:\n{''.join(f"{key}: {value}\n" for key, value in sets.items())}'
    print(text)
    print('Modify the "settings.json" file to desired values.')

def cli_interface(db: database) -> None:
    print('\n', '  Videos Downloader  '.center(get_terminal_size()[0], '-'), sep='')
    while True:
        num_links = len(db) + (1 if settings.read_sets()['default playlist'] else 0)
        print(f"\nThere {'is' if num_links == 1 else 'are'} {num_links} {'link' if num_links == 1 else 'links'} registered. What you want to do next?")
        print('"start"  "show links"  "settings"  "quit"')

        choice = input('> ').lower()
        if choice.startswith('start'):
            db.save_db()
            return
        elif choice.startswith('show'):
            links_page(db)
        elif choice.startswith('set'):
            settings_page()
        elif choice.startswith('quit'):
            db.save_db()
            raise KeyboardInterrupt
        else:
            print("Opção inválida!")

