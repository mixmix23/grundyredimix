import os

# Open a new notepad window
os.system("start notepad.exe")

# Wait for the notepad window to open
input("Press Enter to continue...")

# Get the window handle of the notepad process
notepad_handle = None
while not notepad_handle:
    for hwnd in windows:
        if "notepad" in str(hwnd.GetWindowText()):
            notepad_handle = hwnd
            break

# Send some text to the notepad window
os.system(f'echo "Hello, World!" > /dev/{notepad_handle}')
