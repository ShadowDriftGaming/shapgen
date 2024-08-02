import turtle
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, scrolledtext, ttk
import json
from datetime import datetime, timedelta
import csv
import socket
import threading

# Constants and Global Variables
CREDENTIALS_FILE = 'credentials.json'
FEEDBACK_FILE = 'feedback.txt'
OWNER_ACCOUNT = 'owner'
OWNER_PASSWORD = "owner123"  # Replace with your desired owner password
users = {}
logged_in_user = None
banned_users = set()
timeout_users = {}
multiplayer_mode_active = False
my_turtle = turtle.Turtle()
turtle_speed = "medium"
free_draw_mode_active = False

# Drawing Features
drawing_features = [
    "triangle", "square", "pentagon", "circle", "rectangle",
    "star", "hexagon", "octagon", "spiral", "heart",
    "arrow", "circle_pattern", "flower", "butterfly", "sun",
    "square_spiral", "hexagon_pattern", "octagon_pattern", "polygon", "daisy",
    "spiral_pattern", "wave", "grid", "starburst", "spiral_square",
    "heart_pattern", "kaleidoscope", "whirlwind", "flower_pattern", "lightning"
]

# Games
games = [
    "Number Guessing", "Tic Tac Toe", "Hangman", "Rock Paper Scissors", "Quiz Game"
]

def load_credentials():
    global users
    try:
        with open(CREDENTIALS_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}

def save_credentials():
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def login():
    global logged_in_user
    username = simpledialog.askstring("Login", "Enter username:")
    password = simpledialog.askstring("Login", "Enter password:", show='*')
    if username in users and users[username] == password:
        logged_in_user = username
        messagebox.showinfo("Login", f"Welcome back, {username}!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def signup():
    global logged_in_user
    username = simpledialog.askstring("Signup", "Enter new username:")
    if username in users:
        messagebox.showerror("Signup Failed", "Username already exists.")
        return
    password = simpledialog.askstring("Signup", "Enter new password:", show='*')
    if username and password:
        users[username] = password
        save_credentials()
        logged_in_user = username
        messagebox.showinfo("Signup", f"Account created successfully! Welcome, {username}!")
    else:
        messagebox.showerror("Signup", "Username and password cannot be empty.")

def authenticate_admin():
    password = simpledialog.askstring("Admin Authentication", "Enter admin password:", show='*')
    return password == OWNER_PASSWORD

def authenticate_user(password):
    return password == users.get(logged_in_user, "")

def load_feedback():
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            feedback_text = f.read()
    except FileNotFoundError:
        feedback_text = "No feedback available."
    return feedback_text

def clear_feedback():
    try:
        open(FEEDBACK_FILE, 'w').close()
        messagebox.showinfo("Feedback Cleared", "All feedback has been cleared.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to clear feedback: {e}")

def save_feedback():
    try:
        feedback_data = load_feedback()
        save_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if save_file_path:
            with open(save_file_path, 'w') as f:
                f.write(feedback_data)
            messagebox.showinfo("Feedback Saved", "Feedback has been saved.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save feedback: {e}")

def search_feedback(search_term):
    feedback_data = load_feedback()
    search_results = "\n".join([line for line in feedback_data.split('\n') if search_term.lower() in line.lower()])
    return search_results or "No matching feedback found."

def delete_feedback(feedback_to_delete):
    feedback_data = load_feedback().split('\n')
    if feedback_to_delete in feedback_data:
        feedback_data.remove(feedback_to_delete)
        with open(FEEDBACK_FILE, 'w') as f:
            f.write("\n".join(feedback_data) + "\n")
        messagebox.showinfo("Feedback Deleted", "Feedback has been deleted.")
    else:
        messagebox.showerror("Error", "Feedback not found.")

def export_feedback(format):
    feedback_data = load_feedback().split('\n')
    save_file_path = filedialog.asksaveasfilename(defaultextension=f".{format}", filetypes=[(f"{format.upper()} files", f"*.{format}")])
    if save_file_path:
        try:
            if format == 'csv':
                with open(save_file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    for line in feedback_data:
                        writer.writerow([line])
            elif format == 'json':
                with open(save_file_path, 'w') as f:
                    json.dump(feedback_data, f, indent=4)
            messagebox.showinfo("Feedback Exported", f"Feedback has been exported as {format.upper()}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export feedback: {e}")

def handle_account_settings():
    if not logged_in_user:
        messagebox.showerror("Authentication Failed", "You must be logged in to access account settings.")
        return

    def change_password():
        new_password = simpledialog.askstring("Change Password", "Enter new password:", show='*')
        if new_password:
            users[logged_in_user] = new_password
            save_credentials()
            messagebox.showinfo("Password Changed", "Password has been changed successfully.")

    def view_account_details():
        details = f"Username: {logged_in_user}\nPassword: {users[logged_in_user]}"
        messagebox.showinfo("Account Details", details)

   

    settings_window = tk.Toplevel()
    settings_window.title("Account Settings")

    ttk.Button(settings_window, text="Change Password", command=change_password).pack(padx=10, pady=5)
    ttk.Button(settings_window, text="View Account Details", command=view_account_details).pack(padx=10, pady=5)
    ttk.Button(settings_window, text="Delete Account", command=delete_account).pack(padx=10, pady=5)

def handle_kick():
    if not authenticate_admin():
        messagebox.showerror("Authentication Failed", "Invalid admin password.")
        return
    username = simpledialog.askstring("Kick User", "Enter username to kick:")
    if username in users:
        # Simulate kicking user (in a real scenario, you'd disconnect their session)
        messagebox.showinfo("User Kicked", f"User {username} has been kicked out.")
    else:
        messagebox.showerror("Error", "User not found.")

def handle_ban():
    if not authenticate_admin():
        messagebox.showerror("Authentication Failed", "Invalid admin password.")
        return
    username = simpledialog.askstring("Ban User", "Enter username to ban:")
    if username in users:
        banned_users.add(username)
        messagebox.showinfo("User Banned", f"User {username} has been banned.")
    else:
        messagebox.showerror("Error", "User not found.")

def handle_timeout():
    if not authenticate_admin():
        messagebox.showerror("Authentication Failed", "Invalid admin password.")
        return
    username = simpledialog.askstring("Timeout User", "Enter username to timeout:")
    timeout_duration = simpledialog.askinteger("Timeout Duration", "Enter timeout duration in minutes:")
    if username in users and timeout_duration:
        timeout_users[username] = datetime.now() + timedelta(minutes=timeout_duration)
        messagebox.showinfo("User Timed Out", f"User {username} has been timed out for {timeout_duration} minutes.")
    else:
        messagebox.showerror("Error", "User not found or invalid duration.")

def show_admin_panel():
    if not logged_in_user:
        messagebox.showerror("Authentication Failed", "You must be logged in to access the admin panel.")
        return
    if logged_in_user != OWNER_ACCOUNT and not authenticate_admin():
        messagebox.showerror("Authentication Failed", "Invalid admin password.")
        return

    root = tk.Tk()
    root.title("Admin Panel")

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    feedback_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=40, height=20)
    feedback_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    feedback_data = load_feedback()
    feedback_display.insert(tk.END, feedback_data)

    def refresh_feedback():
        feedback_display.delete(1.0, tk.END)
        feedback_display.insert(tk.END, load_feedback())

    def handle_search():
        search_term = simpledialog.askstring("Search Feedback", "Enter search term:")
        if search_term:
            search_results = search_feedback(search_term)
            feedback_display.delete(1.0, tk.END)
            feedback_display.insert(tk.END, search_results)

    def handle_delete():
        feedback_to_delete = simpledialog.askstring("Delete Feedback", "Enter exact feedback to delete:")
        if feedback_to_delete:
            delete_feedback(feedback_to_delete)
            refresh_feedback()

    def handle_export_csv():
        export_feedback('csv')

    def handle_export_json():
        export_feedback('json')

    button_frame = ttk.Frame(frame)
    button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

    ttk.Button(button_frame, text="Clear Feedback", command=lambda: [clear_feedback(), refresh_feedback()]).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Save Feedback", command=save_feedback).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Search Feedback", command=handle_search).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Delete Feedback", command=handle_delete).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Export as CSV", command=handle_export_csv).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Export as JSON", command=handle_export_json).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Kick User", command=handle_kick).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Ban User", command=handle_ban).pack(fill=tk.X, padx=5, pady=5)
    ttk.Button(button_frame, text="Timeout User", command=handle_timeout).pack(fill=tk.X, padx=5, pady=5)

    root.mainloop()

# Drawing Functions
def draw_star():
    my_turtle.shape("turtle")
    my_turtle.color("cyan")
    set_turtle_speed()
    for _ in range(5):
        my_turtle.forward(100)
        my_turtle.right(144)

def draw_hexagon():
    my_turtle.shape("turtle")
    my_turtle.color("magenta")
    set_turtle_speed()
    for _ in range(6):
        my_turtle.forward(100)
        my_turtle.left(60)

def draw_octagon():
    my_turtle.shape("turtle")
    my_turtle.color("teal")
    set_turtle_speed()
    for _ in range(8):
        my_turtle.forward(100)
        my_turtle.left(45)

def draw_spiral():
    my_turtle.shape("turtle")
    my_turtle.color("brown")
    set_turtle_speed()
    for i in range(100):
        my_turtle.forward(i)
        my_turtle.left(59)

def draw_heart():
    my_turtle.shape("turtle")
    my_turtle.color("pink")
    set_turtle_speed()
    my_turtle.begin_fill()
    my_turtle.left(140)
    my_turtle.forward(113)
    for _ in range(200):
        my_turtle.right(1)
        my_turtle.forward(1)
    my_turtle.left(120)
    for _ in range(200):
        my_turtle.right(1)
        my_turtle.forward(1)
    my_turtle.forward(112)
    my_turtle.end_fill()

# Additional Drawing Functions
def draw_arrow():
    my_turtle.shape("turtle")
    my_turtle.color("gold")
    set_turtle_speed()
    my_turtle.forward(100)
    my_turtle.left(135)
    my_turtle.forward(50)
    my_turtle.backward(50)
    my_turtle.right(270)
    my_turtle.forward(50)
    my_turtle.backward(50)
    my_turtle.left(135)
    my_turtle.backward(50)

def draw_circle_pattern():
    my_turtle.shape("turtle")
    my_turtle.color("violet")
    set_turtle_speed()
    for _ in range(36):
        my_turtle.circle(100)
        my_turtle.left(10)

def draw_flower():
    my_turtle.shape("turtle")
    my_turtle.color("red")
    set_turtle_speed()
    for _ in range(36):
        my_turtle.circle(100, 60)
        my_turtle.left(120)
        my_turtle.circle(100, 60)
        my_turtle.left(120)

def draw_butterfly():
    my_turtle.shape("turtle")
    my_turtle.color("blue")
    set_turtle_speed()
    my_turtle.begin_fill()
    for _ in range(2):
        my_turtle.circle(100, 60)
        my_turtle.circle(100, -60)
    my_turtle.end_fill()

def draw_sun():
    my_turtle.shape("turtle")
    my_turtle.color("yellow")
    set_turtle_speed()
    my_turtle.begin_fill()
    my_turtle.circle(100)
    my_turtle.end_fill()
    my_turtle.penup()
    my_turtle.goto(0, 0)
    my_turtle.pendown()
    for _ in range(12):
        my_turtle.forward(150)
        my_turtle.backward(150)
        my_turtle.right(30)

def draw_square_spiral():
    my_turtle.shape("turtle")
    my_turtle.color("grey")
    set_turtle_speed()
    for i in range(100):
        my_turtle.forward(i)
        my_turtle.right(90)

def draw_hexagon_pattern():
    my_turtle.shape("turtle")
    my_turtle.color("cyan")
    set_turtle_speed()
    for _ in range(6):
        for _ in range(6):
            my_turtle.forward(100)
            my_turtle.left(60)
        my_turtle.left(60)

def draw_octagon_pattern():
    my_turtle.shape("turtle")
    my_turtle.color("purple")
    set_turtle_speed()
    for _ in range(8):
        for _ in range(8):
            my_turtle.forward(50)
            my_turtle.left(45)
        my_turtle.left(45)

def draw_polygon(sides):
    my_turtle.shape("turtle")
    my_turtle.color("orange")
    set_turtle_speed()
    angle = 360 / sides
    for _ in range(sides):
        my_turtle.forward(100)
        my_turtle.left(angle)

def draw_daisy():
    my_turtle.shape("turtle")
    my_turtle.color("yellow")
    set_turtle_speed()
    for _ in range(36):
        my_turtle.forward(100)
        my_turtle.left(170)

def draw_spiral_pattern():
    my_turtle.shape("turtle")
    my_turtle.color("green")
    set_turtle_speed()
    for i in range(100):
        my_turtle.forward(i)
        my_turtle.left(59)

def draw_wave():
    my_turtle.shape("turtle")
    my_turtle.color("blue")
    set_turtle_speed()
    for _ in range(20):
        my_turtle.forward(100)
        my_turtle.left(30)
        my_turtle.forward(100)
        my_turtle.right(30)

def draw_grid():
    my_turtle.shape("turtle")
    my_turtle.color("black")
    set_turtle_speed()
    for i in range(10):
        my_turtle.forward(100)
        my_turtle.backward(100)
        my_turtle.right(90)
        my_turtle.forward(100)
        my_turtle.left(90)

def draw_starburst():
    my_turtle.shape("turtle")
    my_turtle.color("red")
    set_turtle_speed()
    for _ in range(12):
        my_turtle.forward(100)
        my_turtle.backward(100)
        my_turtle.right(30)

def draw_spiral_square():
    my_turtle.shape("turtle")
    my_turtle.color("brown")
    set_turtle_speed()
    for i in range(100):
        my_turtle.forward(i)
        my_turtle.right(90)

def draw_heart_pattern():
    my_turtle.shape("turtle")
    my_turtle.color("pink")
    set_turtle_speed()
    for _ in range(36):
        my_turtle.forward(100)
        my_turtle.right(170)
        my_turtle.forward(100)
        my_turtle.left(10)

def draw_kaleidoscope():
    my_turtle.shape("turtle")
    my_turtle.color("yellow")
    set_turtle_speed()
    for _ in range(36):
        draw_star()
        my_turtle.right(10)

def draw_whirlwind():
    my_turtle.shape("turtle")
    my_turtle.color("blue")
    set_turtle_speed()
    for i in range(100):
        my_turtle.forward(i)
        my_turtle.right(30)

def draw_flower_pattern():
    my_turtle.shape("turtle")
    my_turtle.color("red")
    set_turtle_speed()
    for _ in range(36):
        draw_flower()
        my_turtle.right(10)

def draw_lightning():
    my_turtle.shape("turtle")
    my_turtle.color("yellow")
    set_turtle_speed()
    for _ in range(3):
        my_turtle.forward(100)
        my_turtle.right(120)
        my_turtle.forward(100)
        my_turtle.left(120)
        my_turtle.forward(100)
        my_turtle.right(120)
        my_turtle.forward(100)

def set_turtle_speed():
    speeds = {"slow": 1, "medium": 6, "fast": 10}
    my_turtle.speed(speeds.get(turtle_speed, 6))

def start_drawing():
    global free_draw_mode_active
    free_draw_mode_active = True
    my_turtle.showturtle()
    turtle.mainloop()

def stop_drawing():
    global free_draw_mode_active
    free_draw_mode_active = False
    my_turtle.hideturtle()
    turtle.bye()

def start_multiplayer_mode():
    global multiplayer_mode_active
    multiplayer_mode_active = True
    # Setup multiplayer mode (e.g., network setup, additional features)
    messagebox.showinfo("Multiplayer Mode", "Multiplayer mode activated!")

def stop_multiplayer_mode():
    global multiplayer_mode_active
    multiplayer_mode_active = False
    # Teardown multiplayer mode (e.g., network cleanup)
    messagebox.showinfo("Multiplayer Mode", "Multiplayer mode deactivated!")

def show_game_selection():
    game = simpledialog.askstring("Game Selection", f"Choose a game:\n{', '.join(games)}")
    if game in games:
        messagebox.showinfo("Game Selected", f"You selected: {game}")
        # Launch the chosen game (implementation of each game is needed here)
    else:
        messagebox.showerror("Invalid Game", "Game not found.")

def show_secret_features():
    secret_code = simpledialog.askstring("Secret Access", "Enter secret code:")
    secrets = [
        "Unlock Hidden Feature 1",
        "Unlock Hidden Feature 2",
        "Unlock Hidden Feature 3",
        "Unlock Hidden Feature 4",
        "Unlock Hidden Feature 5",
        "Unlock Hidden Feature 6",
        "Unlock Hidden Feature 7",
        "Unlock Hidden Feature 8",
        "Unlock Hidden Feature 9",
        "Unlock Hidden Feature 10"
    ]
    if secret_code in secrets:
        messagebox.showinfo("Secret Unlocked", f"Secret Feature: {secret_code} has been unlocked!")
    else:
        messagebox.showerror("Invalid Secret Code", "Secret code not found.")

def main_menu():
    root = tk.Tk()
    root.title("Main Menu")

    menu_frame = ttk.Frame(root)
    menu_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    ttk.Button(menu_frame, text="Login", command=login).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Signup", command=signup).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Admin Panel", command=show_admin_panel).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Start Drawing", command=start_drawing).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Stop Drawing", command=stop_drawing).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Start Multiplayer Mode", command=start_multiplayer_mode).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Stop Multiplayer Mode", command=stop_multiplayer_mode).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Game Selection", command=show_game_selection).pack(padx=10, pady=5)
    ttk.Button(menu_frame, text="Secret Features", command=show_secret_features).pack(padx=10, pady=5)

    root.mainloop()

if __name__ == "__main__":
    load_credentials()
    main_menu()
