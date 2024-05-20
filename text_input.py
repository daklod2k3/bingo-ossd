from button import Button
import pygame 

class TextInput:
    def __init__(self, img, pos, base_color, active_color, text,  font) -> None:
        self.text = text
        self.user_text = ""
        self.active = False
        self.img = img
        self.pos = pos
        self.base_color = base_color
        self.active_color = active_color
        self.font = font
        self.button = Button(self.img, self.pos, text, self.font, self.base_color, self.base_color)
        

    def update(self, screen):
        if self.active and self.user_text != "":
            self.button.text_input = self.user_text
        else:
            self.button.text_input = self.text

        # self.rect = self.button.rect
        self.button.update(screen)
        
    def set_active(self, bool):
        if bool:
            self.button.current_color = self.active_color
        else:
            self.button.current_color = self.base_color
        self.active = bool

    def active_check(self, pos):
        if self.button.checkForInput(pos):
            self.active = True
            self.button.current_color = self.active_color
        else:
            self.button.current_color = self.base_color
            self.active = False
    
    def check_input(self, event):
        if self.active:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.user_text = self.user_text[:-1]
                else:
                    self.user_text += event.unicode

        return self.user_text

    def clear_user_txt(self):
        self.active = False
        self.button.current_color = self.base_color
        self.user_text = ""
        