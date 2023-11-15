import tkinter as tk
from tkinter import ttk
import requests
import hashlib
import random
import string
import threading

# Function to generate password suggestions based on the user-entered password
def generate_password_suggestions(original_password):
    suggestions = []

    # Suggestion 1: Add random characters at random positions
    added_suggestion = original_password
    for _ in range(random.randint(1, 3)):
        index = random.randint(0, len(added_suggestion))
        new_char = random.choice(string.ascii_letters + string.digits + string.punctuation)
        added_suggestion = added_suggestion[:index] + new_char + added_suggestion[index:]
    suggestions.append(added_suggestion)

    # Suggestion 2: Replace random characters with random characters
    replaced_suggestion = original_password
    for _ in range(random.randint(1, 3)):
        index = random.randint(0, len(replaced_suggestion) - 1)
        new_char = random.choice(string.ascii_letters + string.digits + string.punctuation)
        replaced_suggestion = replaced_suggestion[:index] + new_char + replaced_suggestion[index + 1:]
    suggestions.append(replaced_suggestion)

    # Suggestion 3: Generate a password with some characters replaced
    complex_suggestion = ''.join(
        random.choice(string.ascii_letters + string.digits + string.punctuation) if random.random() < 0.5 else c
        for c in original_password
    )
    suggestions.append(complex_suggestion)

    return suggestions

# Function to check password strength
def check_password_strength():
    # Check if the password check is already in progress
    if check_password_strength.in_progress:
        return

    password = password_entry.get()

    # Check if the password is empty
    if not password:
        result_label.config(text="Please enter a password.")
        return

    # Set the flag to indicate that the password check is in progress
    check_password_strength.in_progress = True

    # Display loading icon
    progress_bar.start()

    def check_password_strength_thread():
        nonlocal password

        sha1_password = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1_password[:5], sha1_password[5:]
        api_url = f"https://api.pwnedpasswords.com/range/{prefix}"

        try:
            response = requests.get(api_url)

            if response.status_code != 200:
                raise Exception("Failed to connect to the API")

            password_occurrences = [line.split(':') for line in response.text.split('\n')]
            for item in password_occurrences:
                if item[0] == suffix:
                    count = int(item[1])
                    if count > 0:
                        result_label.config(text=f"Password is not strong. It has been exposed in {count} data breaches.")
                        suggestions = generate_password_suggestions(password)
                        suggestions_text.config(state=tk.NORMAL)
                        suggestions_text.delete(1.0, tk.END)
                        suggestions_text.insert(tk.END, "Here are some stronger password suggestions:\n")
                        for i, suggestion in enumerate(suggestions, start=1):
                            suggestions_text.insert(tk.END, f"{i}. {suggestion}\n")
                        suggestions_text.config(state=tk.DISABLED)
                        return

            result_label.config(text="Password is strong and has not been exposed in any known data breaches.")

        except requests.exceptions.RequestException:
            result_label.config(text="No internet connection. Please check your connection and try again.")
        finally:
            # Stop the loading icon and hide it
            progress_bar.stop()
            progress_bar.grid_remove()

            # Display suggestions below the password box
            suggestions_text.config(state=tk.NORMAL)
            suggestions_text.delete(1.0, tk.END)
            suggestions_text.insert(tk.END, "Here are some stronger password suggestions:\n")
            suggestions = generate_password_suggestions(password)
            for i, suggestion in enumerate(suggestions, start=1):
                suggestions_text.insert(tk.END, f"{i}. {suggestion}\n")
            suggestions_text.config(state=tk.DISABLED)

            # Center warning messages
            result_label.pack_configure(expand=False)
            suggestions_text.pack_configure(expand=False)

            # Reset the flag after the password check is complete
            check_password_strength.in_progress = False

    # Run the password check in a separate thread
    threading.Thread(target=check_password_strength_thread).start()

# Initialize the flag to indicate that the password check is not in progress
check_password_strength.in_progress = False

# Function to handle right-click context menu
def copy_to_clipboard(event):
    selected_text = suggestions_text.get(tk.SEL_FIRST, tk.SEL_LAST)
    window.clipboard_clear()
    window.clipboard_append(selected_text)

# Function to generate new strong passwords
def generate_new_passwords():
    password_entry.delete(0, tk.END)
    new_password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=random.randint(8, 16)))
    password_entry.insert(tk.END, new_password)
    check_password_strength()

# Create the main window
window = tk.Tk()
window.title("Password Strength Checker")

# Configure the main window to expand with resizing
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Create and place widgets
style = ttk.Style()
style.configure('TLabel', padding=5)

password_label = ttk.Label(window, text="Enter your password:")
password_label.pack(side='top')

password_entry = ttk.Entry(window)
password_entry.pack(side='top', fill='both', expand=True, padx=5, pady=5)
# Bind the <Return> event to the check_password_strength function
password_entry.bind("<Return>", lambda event: check_password_strength())

check_button = ttk.Button(window, text="Check Password Strength", command=check_password_strength)
check_button.pack(side='top', fill='both', expand=True, padx=5, pady=5)

generate_button = ttk.Button(window, text="Generate New Passwords", command=generate_new_passwords)
generate_button.pack(side='top', fill='both', expand=True, padx=5, pady=5)

result_label = ttk.Label(window, text="", justify='center')
result_label.pack(side='top', fill='both', expand=True, padx=5, pady=5)

# Text widget for displaying suggestions
suggestions_text = tk.Text(window, height=5, width=80, wrap=tk.WORD, state=tk.DISABLED)
suggestions_text.pack(side='top', fill='both', expand=True, padx=5, pady=5)
# Right-click context menu for copying
suggestions_text.bind("<Button-3>", copy_to_clipboard)

# Progress bar for loading icon
progress_bar = ttk.Progressbar(window, mode='indeterminate')
progress_bar.pack(side='top', fill='both', expand=True, padx=5, pady=5)

# Instructions label
instructions_label = tk.Label(
    window,
    text="Specify the password you want and press Ctrl-C to copy.",
    font=("Arial", 8),
    fg="gray"
)
instructions_label.pack(side='right', anchor='e', padx=10, pady=10)

# Start the GUI main loop
window.mainloop()
