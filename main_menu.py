import pygame
from button import Button
import socket
import threading
from text_input import TextInput
import pickle


def get_font(size):
    return pygame.font.Font(size=size)

class MainMenu:
    def __init__(self, screen_width, screen_height) -> None:

        self.screen_width = screen_width
        self.screen_height = screen_height
        
        imgBackground = pygame.image.load('./assets/room_background.png')
        self.imgBackground = pygame.transform.smoothscale(imgBackground, (screen_width - 20, screen_height - 20))
        
        imgButton = pygame.image.load('./assets/button2.png')
        imgButton = pygame.transform.smoothscale(imgButton, (350, 90))

        self.host = Button(imgButton, (screen_width / 2, 300), "Host Room", get_font(30), "white", "black")
        self.join = Button(imgButton, (screen_width / 2, 450), "Join Room", get_font(30), "white", "black")
        self.exit = Button(imgButton, (screen_width / 2, 600), "Exit", get_font(30), "white", "black")
        backImg = pygame.image.load('./assets/back.png')
        backImg = pygame.transform.smoothscale(backImg, (100, 50))
        self.btnBack = Button(image=backImg, pos=(screen_width - 60, 35), text_input="Back", font=get_font(30), base_color="black", hovering_color="white")

        # self.imgBorder = pygame.image.load
        self.state = 0
        self.playerName = None

        imgBorder = pygame.image.load('./assets/chatbox.png')
        imgInput = pygame.transform.smoothscale(imgBorder, (300, 50))
        self.imgRoomSelect = pygame.transform.smoothscale(imgBorder, (200, 30))
    

        self.inputName = TextInput(imgInput, (screen_width / 2, screen_height / 2), "white", "yellow", "Enter your name", get_font(30))
        # self.inputName.set_active(True)
        self.txtEnterToPlay = get_font(30).render("Enter to play", True, "white")  
            
    def update(self, delta, screen):
        screen.fill("black")

        screen.blit(self.imgBackground, (10,10))

        if self.playerName is None:
            if self.inputName.user_text != "":
                screen.blit(self.txtEnterToPlay, self.txtEnterToPlay.get_rect(center = (self.screen_width/ 2, self.screen_height / 2 + 100)))
            self.inputName.update(screen)
            return


        if self.state == 1:       
            self.btnBack.update(screen)

            if len(self.listBtn) == 0:
                txtNotFound = get_font(30).render("No room found", True, "white")
                screen.blit(txtNotFound, (100,100))
            for btn in self.listBtn:
                btn[0].update(screen)
        else:   
            self.host.update(screen)
            self.join.update(screen)
            self.exit.update(screen)
        
    

    def mouse_down(self, pos):

        if self.playerName is None:
            self.inputName.active_check(pos)
            return
                

        match self.state:
            case 0:
                if self.host.checkForInput(pos):
                    return 1
                if self.join.checkForInput(pos):
                    self.serverList = []
                    self.listBtn = []
                    threading.Thread(target=self.discover_server).start()
                    return 2
                if self.exit.checkForInput(pos):
                    return 3
            

            case 1:
                if self.btnBack.checkForInput(pos):
                    self.state -= 1
                    return -1
                
                for btn in self.listBtn:
                    if btn[0].checkForInput(pos):
                        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client.connect((btn[1][0], 8000))
                        self.client.send(("#join/" + str(self.playerName)).encode())
                        self.room_name = btn[0].text_input
                        while True:
                            try:
                                self.room_data = pickle.loads(self.client.recv(1024))
                                print(self.room_data.total_bet)
                                return -2
                            except:
                                pass
                        return -2
        

    def mouse_motion(self, pos):

        self.btnBack.changeColor(pos)

        self.host.changeColor(pos)
        self.join.changeColor(pos)
        self.exit.changeColor(pos)

    def key_down(self, event):
        if self.playerName is None:
            if event.key == pygame.K_RETURN and self.inputName.user_text !=  "":
                self.playerName = self.inputName.user_text
            else: 
                self.inputName.check_input(event)
    
    def join_init(self):
        self.state = 1

    def room_search(self):
        for i in range(10):
            try:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client.connect((socket.gethostname(), 8000 + i))
                # print(8000 + i)
                self.serverList.append(8000 + i)
                self.client.send("#getname".encode())
                name = str(self.client.recv(1024).decode())
                self.listBtn.append((Button(self.imgRoomSelect, (self.screen_width / 2, 200 + 40 * len(self.serverList) - 1), name, get_font(25), "white", "black"), 8000 + i))
                self.client.close()
            except socket.error:
                print('error ' + str(i))
                continue


    def discover_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as client_socket:
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            client_socket.settimeout(5)
            client_socket.sendto(b'discover', ('<broadcast>', 65432))
            try:
                data, server = client_socket.recvfrom(1024)
                print(f"Server discovered at {server}: {data}")
                self.listBtn.append((Button(self.imgRoomSelect, (self.screen_width / 2, 200 + 40 * len(self.serverList) - 1), data.decode(), get_font(25), "white", "black"), server))
            except socket.timeout:
                print("No server response")
