import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import random

# Function to move the window randomly
def move_window():
    x = random.randint(0, root.winfo_screenwidth() - 100)  # Adjust Axie's window width
    y = random.randint(0, root.winfo_screenheight() - 100)  # Adjust Axie's window height
    root.geometry(f"+{x}+{y}")
    root.after(1000, move_window)  # Move every second

# Function to fetch and display the Axie image
def display_axie_image(axie_id):
    image_url = fetch_axie_image(axie_id)
    
    # Fetch image from URL
    response = requests.get(image_url)
    img_data = response.content
    img = Image.open(BytesIO(img_data))
    
    # Resize image if necessary
    img = img.resize((100, 100), Image.ANTIALIAS)
    axie_image = ImageTk.PhotoImage(img)
    
    # Create a label to display the Axie image
    label = tk.Label(root, image=axie_image, bg='black')
    label.image = axie_image  # Keep a reference to prevent garbage collection
    label.pack()

# Create the tkinter root window
root = tk.Tk()

# Set window properties
root.overrideredirect(True)  # Remove window decorations
root.attributes('-topmost', True)  # Always on top
root.attributes('-transparentcolor', 'black')  # Make the black background transparent

# Fetch and display the Axie
axie_id = "123456"  # Replace with the actual Axie ID
display_axie_image(axie_id)

# Move window randomly
move_window()

# Run the Tkinter main loop
root.mainloop()
