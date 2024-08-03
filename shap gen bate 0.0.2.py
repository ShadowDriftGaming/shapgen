import turtle
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, colorchooser
import json
from datetime import datetime, timedelta
import csv
from PIL import ImageGrab
import webbrowser  # For opening GitHub page

# Constants and Global Variables
CREDENTIALS_FILE = 'credentials.json'
FEEDBACK_FILE = 'feedback.txt'
OWNER_ACCOUNT = 'owner'
OWNER_PASSWORD = "shadow"  # Replace with your desired owner password
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
    "star", "hexagon", "octagon", "spiral", "heart"
]

# Initialize the changelog
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
        if username in banned_users:
            messagebox.showerror("Login Failed", "You are banned from this application.")
        elif username in timeout_users and datetime.now() < timeout_users[username]:
            remaining_time = timeout_users[username] - datetime.now()
            messagebox.showerror("Login Failed", f"You are timed out. Try again in {remaining_time.seconds // 60} minutes.")
        else:
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

def load_feedback():
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            feedback_text = f.read()
    except FileNotFoundError:
        feedback_text = "No feedback available."
    return feedback_text

def clear_feedback():
    try:
        if authenticate_admin():
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

    def ban_user():
        if authenticate_admin():
            username = simpledialog.askstring("Ban User", "Enter username to ban:")
            if username in users and username != logged_in_user:
                banned_users.add(username)
                messagebox.showinfo("User Banned", f"User {username} has been banned successfully.")
                changelog.add_entry("1.0.9", "User Banned", f"User {username} banned by {logged_in_user}")
            else:
                messagebox.showerror("Ban Failed", "User not found or you cannot ban yourself.")

    def timeout_user():
        if authenticate_admin():
            username = simpledialog.askstring("Timeout User", "Enter username to timeout:")
            if username in users and username != logged_in_user:
                timeout_duration = simpledialog.askinteger("Timeout Duration", "Enter timeout duration in minutes:")
                if timeout_duration:
                    timeout_users[username] = datetime.now() + timedelta(minutes=timeout_duration)
                    messagebox.showinfo("User Timed Out", f"User {username} has been timed out for {timeout_duration} minutes.")
                    changelog.add_entry("1.0.10", "User Timed Out", f"User {username} timed out by {logged_in_user} for {timeout_duration} minutes")
            else:
                messagebox.showerror("Timeout Failed", "User not found or you cannot timeout yourself.")

    settings_window = tk.Toplevel()
    settings_window.title("Account Settings")

    tk.Button(settings_window, text="Change Password", command=change_password).pack()
    tk.Button(settings_window, text="Change Username", command=change_username).pack()
    tk.Button(settings_window, text="Set Profile Picture", command=set_profile_picture).pack()
    tk.Button(settings_window, text="View Account Details", command=view_account_details).pack()
    tk.Button(settings_window, text="Delete Account", command=delete_account).pack()
    tk.Button(settings_window, text="Ban User", command=ban_user).pack()
    tk.Button(settings_window, text="Timeout User", command=timeout_user).pack()
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
    tk.Button(control_window, text="Change Turtle Color", command=change_turtle_color).pack()
    tk.Button(control_window, text="Change Background Color", command=change_bg_color).pack()
    tk.Button(control_window, text="Clear Drawing", command=clear_drawing).pack()
    tk.Button(control_window, text="Toggle Visibility (V)", command=toggle_visibility).pack()

    speed_frame = tk.LabelFrame(control_window, text="Change Speed")
    speed_frame.pack(pady=5)
    tk.Radiobutton(speed_frame, text="Slow", variable=turtle_speed, value="slow", command=lambda: change_speed("slow")).pack(anchor=tk.W)
    tk.Radiobutton(speed_frame, text="Medium", variable=turtle_speed, value="medium", command=lambda: change_speed("medium")).pack(anchor=tk.W)
    tk.Radiobutton(speed_frame, text="Fast", variable=turtle_speed, value="fast", command=lambda: change_speed("fast")).pack(anchor=tk.W)

    tk.Button(control_window, text="Save Drawing", command=save_drawing).pack()

def check_secret_code(code):
    codes = {
        "god_mode": god_mode_action,
        "bonus_points": bonus_points_action,
        "access_granted": access_granted_action,
        "night_mode": night_mode_action,
        "nexus": nexus_action,
        # Add more secret codes here
    }
    action = codes.get(code.lower())
    if action:
        action()
    else:
        messagebox.showerror("Invalid Code", "The secret code entered is invalid.")

def god_mode_action():
    messagebox.showinfo("God Mode", "God mode activated!")

def bonus_points_action():
    messagebox.showinfo("Bonus Points", "You've received 100 bonus points!")

def access_granted_action():
    messagebox.showinfo("Access Granted", "Special access granted!")

def night_mode_action():
    root.configure(bg="black")
    for widget in root.winfo_children():
        if isinstance(widget, tk.Menu):
            widget.configure(bg="black", fg="white")
        elif isinstance(widget, tk.Widget):
            widget.configure(bg="black", fg="white")

def nexus_action():
    troll_menu()

def troll_menu():
    troll_window = tk.Toplevel()
    troll_window.title("Troll Menu")

    def fake_error():
        messagebox.showerror("Error", "Something went wrong!")

    def fake_warning():
        messagebox.showwarning("Warning", "This is a warning!")

    def fake_info():
        messagebox.showinfo("Info", "you should sub to my channle shadowdrift_gameing not nexus.")

    def fake_question():
        response = messagebox.askquestion("Question", "Do you like this troll menu?")
        messagebox.showinfo("Response", f"You responded: {response}")

    tk.Button(troll_window, text="Fake Error", command=fake_error).pack()
    tk.Button(troll_window, text="Fake Warning", command=fake_warning).pack()
    tk.Button(troll_window, text="Fake Info", command=fake_info).pack()
    tk.Button(troll_window, text="Fake Question", command=fake_question).pack()

def multiplayer_menu():
    def host_session():
        global multiplayer_mode_active
        multiplayer_mode_active = True
        messagebox.showinfo("Host Session", "You are now hosting a session.")

    def join_session():
        global multiplayer_mode_active
        multiplayer_mode_active = True
        session_code = simpledialog.askstring("Join Session", "Enter session code:")
        if session_code:
            messagebox.showinfo("Join Session", f"You have joined session: {session_code}")

    multiplayer_window = tk.Toplevel()
    multiplayer_window.title("Multiplayer Menu")

    tk.Button(multiplayer_window, text="Host Session", command=host_session).pack()
    tk.Button(multiplayer_window, text="Join Session", command=join_session).pack()

# Initialize the main application
root = tk.Tk()
root.title("Enhanced Application")

# Create Menu Bar
menu_bar = tk.Menu(root)

# Account Menu
account_menu = tk.Menu(menu_bar, tearoff=0)
account_menu.add_command(label="Login", command=login)
account_menu.add_command(label="Signup", command=signup)
account_menu.add_separator()
account_menu.add_command(label="Account Settings", command=handle_account_settings)
account_menu.add_command(label="Logout", command=lambda: globals().update(logged_in_user=None))
menu_bar.add_cascade(label="Account", menu=account_menu)

# Admin Menu
admin_menu = tk.Menu(menu_bar, tearoff=0)
admin_menu.add_command(label="View Feedback", command=lambda: messagebox.showinfo("Feedback", load_feedback()))
admin_menu.add_command(label="Clear Feedback", command=clear_feedback)
admin_menu.add_command(label="Save Feedback", command=save_feedback)
menu_bar.add_cascade(label="Admin", menu=admin_menu)

# Turtle Control Menu
turtle_menu = tk.Menu(menu_bar, tearoff=0)
turtle_menu.add_command(label="Control Turtle", command=turtle_control)
menu_bar.add_cascade(label="Turtle Control", menu=turtle_menu)

# Secret Codes Menu
secret_code_menu = tk.Menu(menu_bar, tearoff=0)
secret_code_menu.add_command(label="Enter Secret Code", command=lambda: check_secret_code(simpledialog.askstring("Secret Code", "Enter secret code:")))
menu_bar.add_cascade(label="Secret Codes", menu=secret_code_menu)

# Multiplayer Menu
multiplayer_menu_bar = tk.Menu(menu_bar, tearoff=0)
multiplayer_menu_bar.add_command(label="Multiplayer", command=multiplayer_menu)
menu_bar.add_cascade(label="Multiplayer", menu=multiplayer_menu_bar)

# Changelog Menu
changelog_menu = tk.Menu(menu_bar, tearoff=0)
changelog_menu.add_command(label="View Changelog", command=lambda: messagebox.showinfo("Changelog", json.dumps(changelog.changes, indent=4)))
menu_bar.add_cascade(label="Changelog", menu=changelog_menu)

def open_github():
    webbrowser.open("https://github.com/ShadowDriftGaming")

tk.Button(root, text="Open GitHub", command=open_github).pack()
root.config(menu=menu_bar)

load_credentials()

root.mainloop()
