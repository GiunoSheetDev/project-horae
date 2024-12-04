import pygame

class InputManager:
    def __init__(self):
        self.key_map = {
            #"spawn_animal" : pygame.K_f,
            "escape": pygame.K_ESCAPE,
            "f" : pygame.K_f,
            "space": pygame.K_SPACE,
        }
        
        self.mouse_buttons = {
            'left': pygame.BUTTON_LEFT,
            'right': pygame.BUTTON_RIGHT,
            
        }

        self.keys_pressed = set()
        self.mouse_buttons_pressed = set()

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons_pressed.add(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons_pressed.discard(event.button)

    def getKeyState(self, action):
        return self.key_map[action] in self.keys_pressed

    def getMouseButtonState(self, button):
        return self.mouse_buttons[button] in self.mouse_buttons_pressed

    def isActionPressed(self, action):
        return self.getKeyState(action)

    def isMouseButtonPressed(self, button):
        return self.getMouseButtonState(button)

# Usage in your main loop
input_manager = InputManager()

if __name__ == "__main__":
    while True:
        input_manager.handleEvents()
        
        if input_manager.isActionPressed('move_left'):
            print("Moving left")
        
        if input_manager.isMouseButtonPressed('left_click'):
            print("Left mouse button clicked")