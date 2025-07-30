from . import display_sh1106, display_ssd1306

def main():
    print("Choose display type:")
    print("1. SH1106")
    print("2. SSD1306")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        display_sh1106.run()
    elif choice == "2":
        display_ssd1306.run()
    else:
        print("Invalid choice.")
