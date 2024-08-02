import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, ttk, filedialog
import json
import csv

ADMIN_PASSWORD = "admin123"  # Replace with your desired admin password
FEEDBACK_FILE = 'feedback.txt'  # File to store feedback

def authenticate(password):
    return password == ADMIN_PASSWORD

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

def show_admin_panel():
    password = simpledialog.askstring("Admin Panel", "Enter admin password:", show='*')
    if password and authenticate(password):
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

        # Buttons for additional admin functionalities
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        clear_button = ttk.Button(button_frame, text="Clear Feedback", command=lambda: [clear_feedback(), refresh_feedback()])
        clear_button.pack(fill=tk.X, padx=5, pady=5)

        save_button = ttk.Button(button_frame, text="Save Feedback", command=save_feedback)
        save_button.pack(fill=tk.X, padx=5, pady=5)

        search_button = ttk.Button(button_frame, text="Search Feedback", command=handle_search)
        search_button.pack(fill=tk.X, padx=5, pady=5)

        delete_button = ttk.Button(button_frame, text="Delete Feedback", command=handle_delete)
        delete_button.pack(fill=tk.X, padx=5, pady=5)

        export_csv_button = ttk.Button(button_frame, text="Export as CSV", command=lambda: export_feedback('csv'))
        export_csv_button.pack(fill=tk.X, padx=5, pady=5)

        export_json_button = ttk.Button(button_frame, text="Export as JSON", command=lambda: export_feedback('json'))
        export_json_button.pack(fill=tk.X, padx=5, pady=5)

        root.mainloop()
    else:
        messagebox.showerror("Authentication Failed", "Invalid password.")

if __name__ == "__main__":
    # Directly show the admin panel
    show_admin_panel()
