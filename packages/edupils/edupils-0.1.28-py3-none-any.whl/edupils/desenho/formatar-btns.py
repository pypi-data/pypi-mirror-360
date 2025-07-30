from js import document

def change_icon_color(class_name, color):
    # Assuming 'bi-play-circle' is the class for the icons inside the buttons you want to target
    icons = document.getElementsByClassName(class_name)
    for icon in icons:
        icon.style.color = color

# Example usage: Change the color of icons within buttons to purple
change_icon_color('bi-play-circle', 'purple')

def change_button_background(class_name, color):
    # Get all elements (buttons) with the specified class name
    buttons = document.getElementsByClassName(class_name)
    for button in buttons:
        # Change the background color of each button
        button.style.backgroundColor = color

# Change the background color of buttons with class 'cells-control-button' to purple
change_button_background('py-1', 'white')