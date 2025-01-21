import random
import string
import datetime
import os
import time
import sys
from colorama import init, Fore, Style, Back
from termcolor import colored
import requests
import hashlib
from tqdm import tqdm

# Initialize colorama for cross-platform color support
init()

class PasswordDatabase:
    def __init__(self):
        self.main_file = "main.txt"
        self.private_file = "mypasswds.txt"
        self.passwords = set()
        self.load_database()

    def load_database(self):
        """Load passwords from main database file"""
        try:
            with open(self.main_file, 'r', encoding='utf-8', errors='ignore') as f:
                self.passwords = set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            # If file doesn't exist, create an empty one
            with open(self.main_file, 'w', encoding='utf-8') as f:
                pass
            self.passwords = set()
        except Exception as e:
            print(f"Error loading database: {e}")
            self.passwords = set()
            
    def save_database(self):
        """Save passwords to main database file"""
        try:
            current_passwords = set()
            if os.path.exists(self.main_file):
                with open(self.main_file, 'r', encoding='utf-8', errors='ignore') as f:
                    current_passwords = set(line.strip() for line in f if line.strip())
            
            # Merge existing passwords with new ones
            all_passwords = current_passwords.union(self.passwords)
            
            with open(self.main_file, 'w', encoding='utf-8') as f:
                for password in sorted(all_passwords):
                    f.write(f"{password}\n")
        except Exception as e:
            print(f"Error saving database: {e}")

def display_banner():
    banner = """
    ███████╗██╗   ██╗██████╗ ██████╗  █████╗ ███████╗███████╗████████╗ ██████╗  ██████╗ ██╗     
    ██╔════╝██║   ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔═══██╗██║     
    ███████╗██║   ██║██████╔╝██████╔╝███████║███████╗███████╗   ██║   ██║   ██║██║   ██║██║     
    ╚════██║██║   ██║██╔══██╗██╔═══╝ ██╔══██║╚════██║╚════██║   ██║   ██║   ██║██║   ██║██║     
    ███████║╚██████╔╝██║  ██║██║     ██║  ██║███████║███████║   ██║   ╚██████╔╝╚██████╔╝███████╗
    ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
                                                                                    
                                   SurPassTool Version 2
                                   ---------------------
                             The Swiss Army Knife For Passwords
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)

def loading_animation(duration=2):
    """Display a loading animation"""
    chars = "|/-\\"
    for _ in range(duration * 10):
        for char in chars:
            sys.stdout.write('\r' + 'Processing ' + char)
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 20 + '\r')

def add_to_database(db):
    """Add passwords to database manually or via file"""
    choice = input("Would you like to add manually (m) or upload a list (l)? ").lower()
    
    if choice == 'm':
        print("Enter passwords (separate multiple passwords with commas):")
        passwords = input().split(',')
        passwords = [p.strip() for p in passwords]
        db.passwords.update(passwords)
        
    elif choice == 'l':
        file_path = input("Enter file path or drag and drop password list: ").strip('"')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f]
                db.passwords.update(passwords)
        except FileNotFoundError:
            print(Fore.RED + "File not found!" + Style.RESET_ALL)
            return

    db.save_database()
    print(Fore.GREEN + "Passwords added successfully!" + Style.RESET_ALL)

def remove_from_database(db):
    """Remove passwords from database manually or via file"""
    choice = input("Would you like to remove manually (m) or via list (l)? ").lower()
    
    if choice == 'm':
        passwords = input("Enter passwords to remove (separate by commas): ").split(',')
        passwords = [p.strip() for p in passwords]
    elif choice == 'l':
        file_path = input("Enter file path or drag and drop password list: ").strip('"')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f]
        except FileNotFoundError:
            print(Fore.RED + "File not found!" + Style.RESET_ALL)
            return
    else:
        print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
        return

    confirm = input(Fore.YELLOW + "Are you sure you want to remove these passwords? (y/n): " + Style.RESET_ALL).lower()
    if confirm == 'y':
        db.passwords.difference_update(passwords)
        db.save_database()
        print(Fore.GREEN + "Passwords removed successfully!" + Style.RESET_ALL)

def check_duplicates(db):
    """Check for and optionally remove duplicate passwords"""
    duplicates = []
    seen = set()
    
    for password in db.passwords:
        if password in seen:
            duplicates.append(password)
        seen.add(password)
    
    if duplicates:
        print(Fore.YELLOW + "Duplicates found:" + Style.RESET_ALL)
        for dup in duplicates:
            print(dup)
        
        if input("Would you like to remove these duplicates? (y/n): ").lower() == 'y':
            db.passwords = seen
            db.save_database()
            print(Fore.GREEN + "Duplicates removed!" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "No duplicates found!" + Style.RESET_ALL)

def generate_random_password():
    """Generate random password with specified strength"""
    print("\nPassword Strength Levels:")
    print("0 - Basic (e.g., qwerty, password123)")
    print("1 - Medium (alphanumeric)")
    print("2 - Strong (alphanumeric + special chars)")
    print("3 - Very Strong (complex combination)")
    
    try:
        strength = int(input("\nEnter strength level (0-3): "))
        if strength not in range(4):
            raise ValueError
    except ValueError:
        print(Fore.RED + "Invalid strength level!" + Style.RESET_ALL)
        return

    loading_animation()
    
    if strength == 0:
        passwords = ['password123', 'qwerty', 'admin123', '123456789']
        password = random.choice(passwords)
    elif strength == 1:
        length = random.randint(8, 12)
        chars = string.ascii_letters + string.digits
        password = ''.join(random.choice(chars) for _ in range(length))
    elif strength == 2:
        length = random.randint(12, 16)
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
    else:
        length = random.randint(16, 20)
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
    
    print(f"\nGenerated password: {Fore.GREEN}{password}{Style.RESET_ALL}")
    
    choice = input("\n1. Save to main database\n2. Save to private file\n3. Morph password\n4. Return to menu\nChoice: ")
    
    if choice == '1':
        db.passwords.add(password)
        db.save_database()
    elif choice == '2':
        with open(db.private_file, 'a') as f:
            f.write(f"{password}\n")
    elif choice == '3':
        return password_morph(password, db)

def check_password_strength(password):
    """Check password strength and return rating"""
    score = 0.0
    
    # Length check
    if len(password) >= 12:
        score += 1.0
    elif len(password) >= 8:
        score += 0.5
        
    # Character variety
    if any(c.isupper() for c in password):
        score += 0.5
    if any(c.islower() for c in password):
        score += 0.5
    if any(c.isdigit() for c in password):
        score += 0.5
    if any(c in string.punctuation for c in password):
        score += 0.5
        
    # Common patterns check
    common = ['password', '123456', 'qwerty', 'admin']
    if any(pattern in password.lower() for pattern in common):
        score -= 1.0
        
    return round(min(max(score, 0), 3), 2)

def password_morph(password, db):
    """Create variations of a password"""
    variations = []
    leet_map = {'a': '@', 'e': '3', 'i': '1', 'o': '0', 's': '$', 't': '7'}
    
    num_variations = int(input("How many variations would you like (max 100)? "))
    num_variations = min(num_variations, 100)
    
    loading_animation()
    
    # Base variations
    variations.append(password)
    variations.append(password.capitalize())
    variations.append(password.upper())
    variations.append(password.lower())
    
    # Leet speak variations
    leet = password
    for char, replacement in leet_map.items():
        leet = leet.replace(char, replacement)
        variations.append(leet)
    
    # Add numbers and special chars
    for i in range(num_variations):
        var = password
        if random.random() > 0.5:
            var += str(random.randint(0, 999))
        if random.random() > 0.7:
            var += random.choice(string.punctuation)
        variations.append(var)
    
    variations = list(set(variations))[:num_variations]  # Remove duplicates and limit
    
    print("\nMorphed variations:")
    for var in variations:
        print(var)
    
    if input("\nWould you like to save these variations? (y/n): ").lower() == 'y':
        save_choice = input("Save to: 1. Main database 2. Separate file: ")
        if save_choice == '1':
            db.passwords.update(variations)
            db.save_database()
        elif save_choice == '2':
            filename = f"morphed_{int(time.time())}.txt"
            with open(filename, 'w') as f:
                for var in variations:
                    f.write(f"{var}\n")
            print(f"Saved to {filename}")

def password_search(db):
    """Search for passwords and check exposure"""
    password = input("Enter password to search: ")
    
    loading_animation()
    
    # Local search
    found = [p for p in db.passwords if password in p]
    if found:
        print(Fore.YELLOW + "\nFound in local database:" + Style.RESET_ALL)
        for p in found:
            print(p)
    
    # Check strength
    strength = check_password_strength(password)
    print(f"\nPassword strength: {strength:.2f}/3.0")
    
    if strength < 2.0:
        print(Fore.RED + "Warning: This password is likely exposed!" + Style.RESET_ALL)
    elif strength < 3.0:
        print(Fore.YELLOW + "Warning: This password might be exposed" + Style.RESET_ALL)
    
    return_to_menu = input("\nPress Enter to return to menu...")

def show_manual():
    """Display program manual"""
    manual = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                    SurPassTool Manual                            ║
    ╚══════════════════════════════════════════════════════════════════╝
    
    1. Add to Database:
       - Add passwords manually or via file
       - Supports comma-separated input
       
    2. Remove from Database:
       - Remove specific passwords
       - Supports both manual input and file upload
       
    3. Check for Duplicates:
       - Scan database for duplicate entries
       - Option to remove duplicates
       
    4. Generate Random Password:
       - Create passwords of varying strength
       - Option to save or morph generated passwords
       
    5. Check Password Strength:
       - Analyze password security
       - Get detailed strength assessment
       
    6. Password Morph:
       - Create variations of passwords
       - Apply common substitution patterns
       
    7. Password Search:
       - Search local database
       - Check password exposure risk
       
    DISCLAIMER:
    This tool is for educational and research purposes only.
    Do not use for unauthorized access or malicious purposes.

    For any questions, comments or concerns 
    Contact: asmcwhite243@gmail.com
    
        =======
       ||     ||
       ||     ||
       ||=====||
              ||
              ||
        =======     
    """
    print(manual)
    input("\nPress Enter to return to menu...")

def main():
    db = PasswordDatabase()
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        display_banner()
        
        print(f"\n{Fore.RED}{Style.BRIGHT}MENU:{Style.RESET_ALL}")
        print("1. Add to Database")
        print("2. Remove from Database")
        print("3. Check for Duplicates")
        print("4. Generate Random Password")
        print("5. Check Password Strength")
        print("6. Password Morph")
        print("7. Password Search")
        print("8. Manual")
        print("9. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            add_to_database(db)
        elif choice == '2':
            remove_from_database(db)
        elif choice == '3':
            check_duplicates(db)
        elif choice == '4':
            generate_random_password()
        elif choice == '5':
            password = input("Enter password to check: ")
            strength = check_password_strength(password)
            print(f"\nStrength rating: {strength:.2f}/3.0")
            if strength < 2.0:
                print(Fore.RED + "This password is weak. Consider strengthening it." + Style.RESET_ALL)
                if input("Would you like to morph this password? (y/n): ").lower() == 'y':
                    password_morph(password, db)
        elif choice == '6':
            password = input("Enter password to morph: ")
            password_morph(password, db)
        elif choice == '7':
            password_search(db)
        elif choice == '8':
            show_manual()
        elif choice == '9':
            print(Fore.GREEN + "Thank you for using SurPassTool!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()        
   
