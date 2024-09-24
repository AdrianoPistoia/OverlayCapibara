import requests
import json
import tkinter as tk
from tkinter import simpledialog, Menu
from PIL import Image, ImageTk
from io import BytesIO
import random

_scale = 2  # Default scale
axie_windows = []  # List to keep track of all Axie windows

# Function to fetch Axie details using GraphQL
def get_axie_detail(axie_id):
    url = "https://graphql-gateway.axieinfinity.com/graphql"
    payload = {
        "operation": "GetAxieDetail",
        "variables": {
            "axieId": str(axie_id)
        },
        "query": """
        query GetAxieDetail($axieId: ID!) {
            axie(axieId: $axieId) {
                id
                image
            }
        }"""
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        data = response.json()
        return data['data']['axie']
    else:
        raise Exception(f"Failed to fetch Axie details. Status code: {response.status_code}, Response: {response.text}")

# Function to move each Axie smoothly to a random location
def move_smoothly(axie_window, steps=100):
    if hasattr(axie_window, 'is_dragged') and axie_window.is_dragged:
        return  # Stop moving if the Axie was dragged

    if hasattr(axie_window, 'movement_stopped') and axie_window.movement_stopped:
        return  # Stop if movement is paused

    current_x = axie_window.winfo_x()
    current_y = axie_window.winfo_y()

    target_x = random.randint(0, root.winfo_screenwidth() - 100)
    target_y = random.randint(0, root.winfo_screenheight() - 100)

    step_x = (target_x - current_x) / steps
    step_y = (target_y - current_y) / steps

    def move_step(step=0):
        if step < steps and not axie_window.is_dragged:
            new_x = int(current_x + step_x * step)
            new_y = int(current_y + step_y * step)
            axie_window.geometry(f"+{new_x}+{new_y}")
            axie_window.after(10, move_step, step + 1)
        else:
            delay = random.randint(4000, 10000)
            if not axie_window.is_dragged:
                axie_window.after(delay, lambda: move_smoothly(axie_window))

    move_step()

# Function to create a wobble effect for each Axie
def wobble(axie_window):
    if hasattr(axie_window, 'wobble_stopped') and axie_window.wobble_stopped:
        return  # Stop wobbling if it's paused

    wobble_offset = 0
    wobble_direction = 1

    def wobble_step():
        nonlocal wobble_offset, wobble_direction
        if axie_window.wobble_stopped:
            return  # Stop wobbling if paused
        wobble_offset += wobble_direction
        if wobble_offset > 2 or wobble_offset < -2:  # Set the wobble range
            wobble_direction *= -1  # Reverse the direction
        axie_window.geometry(f"+{axie_window.winfo_x()}+{axie_window.winfo_y() + wobble_offset}")
        axie_window.after(50, wobble_step)

    wobble_step()

# Function to fetch and display the Axie image in a new window, keeping the original aspect ratio
def display_axie_image(axie_id):
    try:
        # Fetch the Axie details (including image URL)
        axie_data = get_axie_detail(axie_id)
        image_url = axie_data['image']

        # Fetch image from URL
        response = requests.get(image_url)
        img_data = response.content
        img = Image.open(BytesIO(img_data))

        # Preserve aspect ratio
        max_size = 100  # Define the maximum size for width or height
        width, height = img.size

        if width > height:
            new_width = max_size
            new_height = int((height / width) * max_size)
        else:
            new_height = max_size
            new_width = int((width / height) * max_size)

        img = img.resize((new_width * _scale, new_height * _scale), Image.LANCZOS)
        axie_image = ImageTk.PhotoImage(img)

        # Create a new window for each Axie
        axie_window = tk.Toplevel(root)
        axie_window.overrideredirect(True)
        axie_window.attributes('-topmost', True)
        axie_window.attributes('-transparentcolor', 'black')

        # Add the new axie window to the list
        axie_windows.append(axie_window)

        # Create a label to display the Axie image
        label = tk.Label(axie_window, image=axie_image, bg='black')
        label.image = axie_image  # Keep a reference to prevent garbage collection
        label.pack()

        # Start movement and wobble for this Axie
        axie_window.is_dragged = False
        axie_window.movement_stopped = False
        axie_window.wobble_stopped = False

        move_smoothly(axie_window)
        wobble(axie_window)

        # Enable drag functionality
        enable_drag(axie_window)

        # Bind right-click context menu
        axie_window.bind('<Button-3>', lambda event: show_context_menu(axie_window, event))

    except Exception as e:
        print(f"Error fetching Axie image: {e}")

# Function to enable dragging of the Axie window
def enable_drag(axie_window):
    def on_click(event):
        axie_window.start_x = event.x
        axie_window.start_y = event.y
        stop_movement_on_drag(axie_window)

    def on_drag(event):
        delta_x = event.x - axie_window.start_x
        delta_y = event.y - axie_window.start_y
        new_x = axie_window.winfo_x() + delta_x
        new_y = axie_window.winfo_y() + delta_y
        axie_window.geometry(f"+{new_x}+{new_y}")

    def on_release(event):
        resume_movement_after_drag(axie_window)

    # Bind mouse events for dragging
    axie_window.bind('<Button-1>', on_click)
    axie_window.bind('<B1-Motion>', on_drag)
    axie_window.bind('<ButtonRelease-1>', on_release)

# Function to stop movement when dragged
def stop_movement_on_drag(axie_window):
    axie_window.is_dragged = True

# Function to resume movement after dragging
def resume_movement_after_drag(axie_window):
    axie_window.is_dragged = False
    # move_smoothly(axie_window)

# Function to show the context menu on right-click
def show_context_menu(axie_window, event):
    menu = Menu(root, tearoff=0)
    menu.add_command(label="Add Another Axie", command=ask_for_axie_id)
    menu.add_command(label="Switch Selected Axie")  # Placeholder for actual switching logic
    menu.add_command(label="Stop/Resume Random Movement", command=lambda: toggle_movement(axie_window))
    menu.add_command(label="Stop/Resume Wobble", command=lambda: toggle_wobble(axie_window))
    menu.add_command(label="Change Scale", command=lambda: change_scale(axie_window))
    menu.add_command(label="Remove Selected Axie", command=lambda: remove_axie(axie_window))
    menu.post(event.x_root, event.y_root)

# Function to toggle movement on/off
def toggle_movement(axie_window):
    axie_window.movement_stopped = not axie_window.movement_stopped
    if not axie_window.movement_stopped:
        move_smoothly(axie_window)

# Function to toggle wobble on/off
def toggle_wobble(axie_window):
    axie_window.wobble_stopped = not axie_window.wobble_stopped
    if not axie_window.wobble_stopped:
        wobble(axie_window)

# Function to change the scale of the Axie
def change_scale(axie_window):
    global _scale
    new_scale = simpledialog.askfloat("Change Scale", "Enter new scale factor (e.g., 1.5 for 150%):")
    if new_scale:
        _scale = new_scale
        # Get the current Axie ID and redisplay with the new scale
        axie_window.destroy()
        ask_for_axie_id()

# Function to remove an Axie and quit if it's the last one
def remove_axie(axie_window):
    axie_windows.remove(axie_window)
    axie_window.destroy()

    # If no more axies are left, quit the app
    if not axie_windows:
        root.quit()

# Function to ask for a new Axie ID and display it
def ask_for_axie_id():
    axie_id = simpledialog.askstring("Input", "Please enter the Axie ID:")
    if axie_id:
        display_axie_image(axie_id)

# Keybind function for Alt+Q to quit
def quit_app(event=None):
    root.quit()

# Keybind function for Alt+S to add another Axie
def add_new_axie(event=None):
    ask_for_axie_id()

# Create the tkinter root window (invisible base window)
root = tk.Tk()
root.withdraw()  # Hide the root window, as we'll be using Toplevel windows for Axies

# Key bindings for adding new Axies and quitting the app
root.bind_all('<Alt-q>', quit_app)
root.bind_all('<Alt-s>', add_new_axie)

# Ask for the initial Axie ID at startup
ask_for_axie_id()

# Run the Tkinter main loop
root.mainloop()
