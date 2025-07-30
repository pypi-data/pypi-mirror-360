from .list_of_practical import practical_list
import os
import shutil

def start():
    print("Hello, please select which practical you want:")

    for item in practical_list:
        print(list(item.keys())[0])

    while True:
        try:
            practical_index = int(input("Enter practical number: "))
            if 1 <= practical_index <= len(practical_list):
                selected = practical_list[practical_index - 1]
                title = list(selected.keys())[0]
                relative_path = selected[title]

                # Absolute path to the file
                base_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(base_dir, relative_path)

                print(f"\nYou selected: {title}")

                print("\nPlease select the action you want to perform:")
                print("1. Print the practical text")
                print("2. Get the practical file path")
                print("3. Download the practical file (copy to current directory)")

                try:
                    action = int(input("Enter action number: "))

                    if action == 1:
                        if os.path.exists(file_path):
                            with open(file_path, 'r') as file:
                                print("\n--- Practical Content ---")
                                print(file.read())
                        else:
                            print(f"❌ File not found: {file_path}")

                    elif action == 2:
                        print(f"📁 Full File Path: {file_path}")

                    elif action == 3:
                        if os.path.exists(file_path):
                            file_name = os.path.basename(file_path)
                            destination = os.path.join(os.getcwd(), file_name)
                            shutil.copy(file_path, destination)
                            print(f"✅ File copied to current folder: {destination}")
                        else:
                            print(f"❌ File not found: {file_path}")

                    else:
                        print("❌ Invalid action number.")

                except ValueError:
                    print("❌ Please enter a valid number.")
                break
            else:
                print("❌ Please enter a number within range.")
        except ValueError:
            print("❌ Please enter a valid number.")
