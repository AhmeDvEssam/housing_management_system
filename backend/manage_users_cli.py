import os
import sys
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "housing.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("===========================================")
    print("      Housing System User Manager          ")
    print("===========================================")

def create_admin():
    print("\n--- Create New Superuser ---")
    username = input("Username: ")
    email = input("Email: ")
    password = input("Password: ")
    
    if User.objects.filter(username=username).exists():
        print(f"Error: Username '{username}' already exists!")
        return
    
    try:
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created successfully!")
    except Exception as e:
        print(f"Error: {e}")

def create_staff():
    print("\n--- Create New Staff User ---")
    username = input("Username: ")
    password = input("Password: ")
    
    if User.objects.filter(username=username).exists():
        print(f"Error: Username '{username}' already exists!")
        return
    
    try:
        user = User.objects.create_user(username=username, password=password)
        user.is_staff = True
        user.save()
        print(f"Staff user '{username}' created successfully! They can now login to admin.")
    except Exception as e:
        print(f"Error: {e}")

def change_password():
    print("\n--- Change Password ---")
    username = input("Username: ")
    try:
        user = User.objects.get(username=username)
        new_password = input("New Password: ")
        user.set_password(new_password)
        user.save()
        print(f"Password for user '{username}' changed successfully!")
    except User.DoesNotExist:
        print(f"Error: User '{username}' not found!")
    except Exception as e:
        print(f"Error: {e}")

def promote_to_staff():
    print("\n--- Enable Admin Access (Staff Status) ---")
    username = input("Username: ")
    try:
        user = User.objects.get(username=username)
        user.is_staff = True
        user.is_active = True
        user.save()
        print(f"User '{username}' is now a Staff member and can login to Admin.")
    except User.DoesNotExist:
        print(f"Error: User '{username}' not found!")
    except Exception as e:
        print(f"Error: {e}")

def list_users():
    print("\n--- User List ---")
    users = User.objects.all()
    print(f"{'Username':<20} | {'Staff?':<10} | {'Super?':<10} | {'Active?':<10}")
    print("-" * 60)
    for u in users:
        print(f"{u.username:<20} | {str(u.is_staff):<10} | {str(u.is_superuser):<10} | {str(u.is_active):<10}")

def main_menu():
    while True:
        clear_screen()
        print_header()
        print("1. Create New Superuser (Full Admin)")
        print("2. Create New Staff User (Limited Access)")
        print("3. Change User Password")
        print("4. Enable Admin Access for existing user (Make Staff)")
        print("5. List All Users")
        print("6. Exit")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            create_admin()
            input("\nPress Enter to return...")
        elif choice == '2':
            create_staff()
            input("\nPress Enter to return...")
        elif choice == '3':
            change_password()
            input("\nPress Enter to return...")
        elif choice == '4':
            promote_to_staff()
            input("\nPress Enter to return...")
        elif choice == '5':
            list_users()
            input("\nPress Enter to return...")
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid choice!")
            input("\nPress Enter to try again...")

if __name__ == "__main__":
    main_menu()
