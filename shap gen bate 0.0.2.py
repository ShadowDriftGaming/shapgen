import turtle
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, scrolledtext, ttk, colorchooser
import json
from datetime import datetime, timedelta
import csv
import socket
import threading
from PIL import ImageGrab

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

class Changelog:
    def __init__(self, file_path='changelog.json'):
        self.file_path = file_path
        self.changes = self.load_changes()

    def load_changes(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_changes(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.changes, file, indent=4)

    def add_entry(self, version, change_type, description):
        entry = {
            "version": version,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": change_type,
            "description": description
        }
        self.changes.append(entry)
        self.save_changes()

# Initialize the changelog
changelog = Changelog()

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
        changelog.add_entry("1.0.0", "Account Creation", f"New account created: {username}")
    else:
        messagebox.showerror("Signup", "Username and password cannot be empty.")

def authenticate_admin():
    if not logged_in_user:
        messagebox.showerror("Authentication Failed", "You must be logged in as admin to perform this action.")
        return False
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
            changelog.add_entry("1.0.1", "Password Change", f"Password changed for user: {logged_in_user}")

    def change_username():
        new_username = simpledialog.askstring("Change Username", "Enter new username:")
        if new_username:
            if new_username in users:
                messagebox.showerror("Change Username", "Username already exists.")
            else:
                users[new_username] = users.pop(logged_in_user)
                logged_in_user = new_username
                save_credentials()
                messagebox.showinfo("Username Changed", "Username has been changed successfully.")
                changelog.add_entry("1.0.7", "Username Change", f"Username changed from {logged_in_user} to {new_username}")

    def set_profile_picture():
        file_path = filedialog.askopenfilename(title="Select Profile Picture", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            users[logged_in_user + "_profile_pic"] = file_path
            save_credentials()
            messagebox.showinfo("Profile Picture Set", "Profile picture has been set successfully.")
            changelog.add_entry("1.0.8", "Profile Picture Set", f"Profile picture set for user: {logged_in_user}")

    def view_account_details():
        details = f"Username: {logged_in_user}\nPassword: {users[logged_in_user]}"
        profile_pic = users.get(logged_in_user + "_profile_pic", "Not set")
        details += f"\nProfile Picture: {profile_pic}"
        messagebox.showinfo("Account Details", details)

    def delete_account():
        if messagebox.askyesno("Delete Account", "Are you sure you want to delete your account?"):
            del users[logged_in_user]
            save_credentials()
            messagebox.showinfo("Account Deleted", "Your account has been deleted successfully.")
            

    settings_window = tk.Toplevel()
    settings_window.title("Account Settings")

    tk.Button(settings_window, text="Change Password", command=change_password).pack()
    tk.Button(settings_window, text="Change Username", command=change_username).pack()
    tk.Button(settings_window, text="Set Profile Picture", command=set_profile_picture).pack()
    tk.Button(settings_window, text="View Account Details", command=view_account_details).pack()
    tk.Button(settings_window, text="Delete Account", command=delete_account).pack()
    tk.Button(settings_window, text="Close", command=settings_window.destroy).pack()

def turtle_control():
    def move_forward():
        my_turtle.forward(10)

    def move_backward():
        my_turtle.backward(10)

    def turn_left():
        my_turtle.left(15)

    def turn_right():
        my_turtle.right(15)

    def change_turtle_color():
        color = colorchooser.askcolor()[1]
        if color:
            my_turtle.color(color)

    def clear_drawing():
        my_turtle.clear()

    def change_speed(speed):
        global turtle_speed
        turtle_speed = speed
        speeds = {
            "slow": 1,
            "medium": 5,
            "fast": 10
        }
        my_turtle.speed(speeds[speed])

    def toggle_visibility():
        if my_turtle.isvisible():
            my_turtle.hideturtle()
        else:
            my_turtle.showturtle()

    def change_bg_color():
        color = colorchooser.askcolor()[1]
        if color:
            turtle.bgcolor(color)

    def save_drawing():
        canvas = turtle.getcanvas()
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            x = canvas.winfo_rootx()
            y = canvas.winfo_rooty()
            x1 = x + canvas.winfo_width()
            y1 = y + canvas.winfo_height()
            ImageGrab.grab().crop((x, y, x1, y1)).save(file_path)
            messagebox.showinfo("Drawing Saved", "Drawing has been saved successfully.")

    control_window = tk.Toplevel()
    control_window.title("Turtle Control")

    tk.Button(control_window, text="Move Forward (W)", command=move_forward).pack()
    tk.Button(control_window, text="Move Backward (S)", command=move_backward).pack()
    tk.Button(control_window, text="Turn Left (A)", command=turn_left).pack()
    tk.Button(control_window, text="Turn Right (D)", command=turn_right).pack()
    tk.Button(control_window, text="Change Color", command=change_turtle_color).pack()
    tk.Button(control_window, text="Clear", command=clear_drawing).pack()

    speed_frame = tk.Frame(control_window)
    tk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
    speed_var = tk.StringVar(value=turtle_speed)
    tk.OptionMenu(speed_frame, speed_var, "slow", "medium", "fast", command=change_speed).pack(side=tk.LEFT)
    speed_frame.pack()

    tk.Button(control_window, text="Toggle Visibility", command=toggle_visibility).pack()
    tk.Button(control_window, text="Change Background Color", command=change_bg_color).pack()
    tk.Button(control_window, text="Save Drawing", command=save_drawing).pack()
    tk.Button(control_window, text="Close", command=control_window.destroy).pack()

def secret_codes():
    code = simpledialog.askstring("Secret Code", "Enter secret code:")
    if code == "404":
        messagebox.showerror("Error Code", "An error has occurred.")
    elif code == "nexus":
        color = colorchooser.askcolor()[1]
        if color:
            my_turtle.color(color)
            messagebox.showinfo("Nexus", "Turtle color changed successfully.")
    else:
        messagebox.showerror("Invalid Code", "The code you entered is invalid.")

def handle_multiplayer_mode():
    global multiplayer_mode_active
    if authenticate_admin():
        multiplayer_mode_active = not multiplayer_mode_active
        status = "activated" if multiplayer_mode_active else "deactivated"
        messagebox.showinfo("Multiplayer Mode", f"Multiplayer mode has been {status}.")
        changelog.add_entry("1.0.4", "Multiplayer Mode", f"Multiplayer mode {status}")

def free_draw_mode():
    global free_draw_mode_active
    free_draw_mode_active = not free_draw_mode_active
    status = "activated" if free_draw_mode_active else "deactivated"
    messagebox.showinfo("Free Draw Mode", f"Free draw mode has been {status}.")
    changelog.add_entry("1.0.5", "Free Draw Mode", f"Free draw mode {status}")

def view_changelog():
    changelog_window = tk.Toplevel()
    changelog_window.title("Changelog")

    changelog_text = scrolledtext.ScrolledText(changelog_window, wrap=tk.WORD)
    changelog_text.pack(expand=True, fill=tk.BOTH)

    for entry in changelog.changes:
        changelog_text.insert(tk.END, f"Version: {entry['version']}\n")
        changelog_text.insert(tk.END, f"Date: {entry['date']}\n")
        changelog_text.insert(tk.END, f"Type: {entry['type']}\n")
        changelog_text.insert(tk.END, f"Description: {entry['description']}\n\n")

    changelog_text.config(state=tk.DISABLED)

    tk.Button(changelog_window, text="Close", command=changelog_window.destroy).pack()

def handle_draw_shape():
    shape = simpledialog.askstring("Draw Shape", "Enter shape to draw (triangle, square, etc.):")
    if shape and shape.lower() in drawing_features:
        draw_shape(shape.lower())
        changelog.add_entry("1.0.6", "Draw Shape", f"{shape} drawn")

def draw_shape(shape):
    shapes = {
        "triangle": [(0, -50), (50, 50), (-50, 50)],
        "square": [(0, 0), (0, 50), (50, 50), (50, 0)],
        "pentagon": [(0, 50), (47, 15), (29, -40), (-29, -40), (-47, 15)],
        "circle": [(i, 50 * turtle.sin(i * turtle.pi / 180)) for i in range(360)],
        "rectangle": [(0, 0), (0, 50), (100, 50), (100, 0)],
        "star": [(0, 50), (14, 20), (47, 15), (23, -7), (29, -40), (0, -25), (-29, -40), (-23, -7), (-47, 15), (-14, 20)],
        "hexagon": [(0, 50), (43, 25), (43, -25), (0, -50), (-43, -25), (-43, 25)],
        "octagon": [(0, 50), (35, 35), (50, 0), (35, -35), (0, -50), (-35, -35), (-50, 0), (-35, 35)],
        "spiral": [(i, i * 0.5) for i in range(360)],
        "heart": [(i, 50 * turtle.sin(i * turtle.pi / 180)) for i in range(-45, 225)]
        # Add more shapes as needed
    }

    my_turtle.penup()
    my_turtle.goto(shapes[shape][0])
    my_turtle.pendown()
    for point in shapes[shape][1:]:
        my_turtle.goto(point)
    my_turtle.penup()

def setup_turtle_controls():
    turtle.listen()
    turtle.onkey(lambda: my_turtle.forward(10), "w")
    turtle.onkey(lambda: my_turtle.backward(10), "s")
    turtle.onkey(lambda: my_turtle.left(15), "a")
    turtle.onkey(lambda: my_turtle.right(15), "d")

def create_gui():
    root = tk.Tk()
    root.title("Main Menu")

    tk.Button(root, text="Login", command=login).pack()
    tk.Button(root, text="Signup", command=signup).pack()
    tk.Button(root, text="Account Settings", command=handle_account_settings).pack()
    tk.Button(root, text="Turtle Control", command=turtle_control).pack()
    tk.Button(root, text="Draw Shape", command=handle_draw_shape).pack()
    tk.Button(root, text="Free Draw Mode", command=free_draw_mode).pack()
    tk.Button(root, text="Multiplayer Mode", command=handle_multiplayer_mode).pack()
    tk.Button(root, text="Secret Codes", command=secret_codes).pack()
    tk.Button(root, text="View Changelog", command=view_changelog).pack()
    tk.Button(root, text="Exit", command=root.destroy).pack()

    load_credentials()
    setup_turtle_controls()

    root.mainloop()

if __name__ == "__main__":
    create_gui()
