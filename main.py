import pygame
from button import Button
from text_input import TextInput
import random
import socket
import threading
from main_menu import MainMenu
import pickle

# tkinter().wm_withdraw() #to hide the main window
# import turtle

# timmy = turtle.Turtle()


pygame.init()

host = ''
port = 8000




clock = pygame.time.Clock()

screen_width = 1300
screen_height = 844
player_money = 100000

def get_font(size):
    return pygame.font.Font(size=size)

running = True


def init_screen():
    global screen 
    screen = pygame.display.set_mode([screen_width, screen_height])
    screen.fill((0, 0, 0))
    

init_screen()

def get_dec_from_float(float):
    tmp = str(float).split('.')
    return int(tmp[0])

class Room():
    def __init__(self, host, room_name, player_name, client = None) -> None:
        self.listBtn = []
        self.diceHistory = []
        self.ready = 0
        self.playerCount = 1
        self.txtTitleStr = "Waiting all ready"
        self.readyCountTime = 5
        self.gameEndCountTime = 15
        self.diceRollCountTime = 3
        self.animationTime = 1000
        self.time = 0
        self.user_txt = ""
        self.state = 0
        self.close = False


        self.diceRollTime = self.diceRollCountTime * 1000
        

        self.messHistory = []





        self.playerReady = False

        self.host = host
        self.client = client

        # current bet curformed
        self.currentConfirm = []
        # self.currentConfirm.append([3, 1000])

        self.roomBet = []
        for i in range(18 - 3 + 1):
            self.roomBet.append(0)            
                


        imgBtnNumber = pygame.image.load("./assets/btnNumber.png")
        self.imgBtnNumber = pygame.transform.smoothscale(imgBtnNumber, (90, 90))
        imgBtnNumberDisable = pygame.image.load('./assets/btnNumberDisable.png')
        self.imgBtnNumberDisable = pygame.transform.smoothscale(imgBtnNumberDisable, (90, 90))

        chatboxImg = pygame.image.load('./assets/chatbox.png')
        chatboxImg = pygame.transform.smoothscale(chatboxImg, (screen_width / 3 - 40, 30))

        readyImg = pygame.image.load('./assets/button2.png')
        self.readyImg = pygame.transform.smoothscale(readyImg, (200,60))

        self.inputMess = TextInput(chatboxImg, (screen_width * 2 / 3 + screen_width / 6, screen_height - 40), "white", "yellow", "Click to chat", get_font(30))

        backImg = pygame.image.load('./assets/back.png')
        backImg = pygame.transform.smoothscale(backImg, (100, 50))
        self.btnBack = Button(image=backImg, pos=(screen_width - 60, 35), text_input="Back", font=get_font(30), base_color="black", hovering_color="white")

        dice_disable_rect = pygame.image.load('./assets/diceDisable.png')
        dice_rect = pygame.image.load('./assets/dice.png')
        self.imgDiceDisable = pygame.transform.smoothscale(dice_disable_rect, (80, 80))
        self.imgDice = pygame.transform.smoothscale(dice_rect, (80, 80))

                
        self.dice1 = Button(self.imgDiceDisable, (300 - 100, 190), "?", get_font(40), "white", "white")
        self.dice2 = Button(self.imgDiceDisable, (300, 190), "?", get_font(40), "white", "white")
        self.dice3 = Button(self.imgDiceDisable, (300 + 100, 190), "?", get_font(40), "white", "white")


        bg = pygame.image.load('./assets/room_background.png')
        self.bg = pygame.transform.smoothscale(bg, (screen_width / 3 * 2 - 10, screen_height - 20))
        
        self.imgBg = bg

        mess_bg = pygame.image.load('./assets/room_background.png')
        self.mess_bg = pygame.transform.smoothscale(mess_bg, (screen_width / 3 - 20, screen_height - 80))

        self.btnReady = Button(image=self.readyImg, pos=((screen_width * 2 / 3 - 40) / 2 + 25, screen_height - 50), text_input="Ready", font=get_font(40), base_color="black", hovering_color="white")

        imgBet = pygame.transform.smoothscale(readyImg, (300, 60))

        self.btnBet = Button(image=imgBet, pos=((screen_width * 2 / 3 - 40) / 2 + 25, screen_height - 50), text_input="Bet number 18", font=get_font(40), base_color="black", hovering_color="white")


        self.current_number = -1


        self.currentBet = []
        self.listPrice = []
        for i in range(18 - 3 + 1):
            self.currentBet.append(10000)
            btn = self.init_btn_number(i)
            self.listPrice.append(self.init_txt_price(i))
            self.listBtn.append(btn)



        self.inputBet = TextInput(chatboxImg, ((screen_width * 2/ 3 - 40) / 2 + 25,screen_height - 130), "white", "yellow", "10.000", get_font(25))

        txtBetTitle = get_font(20).render("Your bet", True, "white")
        screen.blit(txtBetTitle, (200, 100))

        self.imgCoinIcon = pygame.transform.smoothscale(imgBtnNumber, (30, 30))

        imgChip = pygame.image.load("./assets/poker-chips.png")   
        self.imgChip = pygame.transform.smoothscale(imgChip, (30,30)) 


        if self.host:
            self.server_init()
        else:
            threading.Thread(target=self.client_rev, daemon=True).start()
        
        self.txtPlayerName = get_font(30).render("Room owner: " + room_name, True, "white")
        self.room_name = room_name
        self.player_name = player_name

        
    def price_scale(self, number):
        array = [
            120,
            40,
            20,
            12,
            8,
            5.5,
            4.7,
            4.4,
        ]
        if (number > 10):
            number = 18 - number + 3
        print(number)
        return array[number - 3]
            



    def server_init(self):
        # create a socket object
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global host, port
        try:
            server.bind((host, port))
            server.listen(10)
            print('listen on port: ' + str(port))
            self.server = server
            self.clients = []
            global t1
            t1 = threading.Thread(target=self.server_add_connect, daemon=True)
            t1.daemon = True
            t1.start()
            self.openPort = True
            self.thread = threading.Thread(target=self.start_broadcast_server, daemon=True)
            self.thread.start()
            return
        except:
            self.openPort = False
        self.openPort = False




    
        

    def update(self, delta, screen):
        screen.fill("black")
        if self.host and not self.openPort:
            global room, screen_id
            room = MainMenu(screen_width, screen_height)
            screen_id = 1
            
            return
        
        if self.host:
            # self.server_rev()
            pass
        else:
            pass
        self.time += delta
        screen.blit(self.bg, (10, 10))
        screen.blit(self.mess_bg, (screen_width * 2 /3 + 10, 10 + 60))


        for idx, mess in enumerate(self.messHistory):
            txt = get_font(25).render(str(mess), True, "white")
            screen.blit(txt, (screen_width * 2 /3 + 20, 20 + 60 + 30 * idx))


        txtBetTitle = get_font(30).render("Current bet", True, "white")
        screen.blit(txtBetTitle, (screen_width * 2 / 3 - 200, 180))
        bgBetTitle = pygame.image.load('./assets/chatbox.png')
        bgBetTitle = pygame.transform.smoothscale(bgBetTitle, (200, 300))
        screen.blit(bgBetTitle, (screen_width * 2 / 3 - 200 - 47, 180 + 30))
        txtTotalBet = get_font(25).render("Total bet " + str(len(self.currentConfirm)) + "/4", True, "white")
        screen.blit(txtTotalBet, txtTotalBet.get_rect(center=(screen_width * 2 / 3 - 200 + 50, 180 + 30 + 320)))


        screen.blit(self.imgChip, self.imgChip.get_rect(center=(screen_width * 2 / 3 - 200, 35)))

        txtTotalChip = get_font(30).render(str(player_money), True, "white")
        screen.blit(txtTotalChip, (screen_width * 2 / 3 - 180, 30))

        for idx, bet in enumerate(self.currentConfirm):
            rect = (screen_width * 2 / 3 - 200 - 10, screen_height / 3 - 40 + 40 * idx)
            img_rect = self.imgCoinIcon.get_rect(center=rect)
            txtNumber = get_font(25).render(str(bet[0]), True, "black")
            txt_rect = txtNumber.get_rect(center=rect)

            txtBetNumber = get_font(30).render(str(bet[1]), True, "white")
            txtBetNumberRect = txtBetNumber.get_rect(center=(rect[0] + 60, rect[1]))
            screen.blit(self.imgCoinIcon, img_rect)
            screen.blit(txtNumber, txt_rect)
            screen.blit(txtBetNumber, txtBetNumberRect)
            


        # global second
        # print(second)
        match self.state:
            case 0:
                if (self.time > self.animationTime):
                    self.animationTime += 1000

                    # self.time = 
                    if (self.txtTitleStr == "Waiting all ready..."):
                        self.txtTitleStr = "Waiting all ready" 
                    else:
                        self.txtTitleStr += "."

                    
                if self.ready == self.playerCount and self.host:
                    self.init_state(1)
                    return
                    
                if not self.playerReady:
                    self.btnReady.update(screen)


            case 1:
                if (self.playerCount < self.ready) and self.host:
                    self.state = 0
                    return

                self.txtTitleStr = "Start after " + str(get_dec_from_float(self.readyTime / 1000)) + "s"

                self.readyTime -= delta

                if self.readyTime < 0:
                    self.init_state(2)

                
            case 2:
                self.gameEndTime -= delta
                self.txtTitleStr = "Dice roll after: " + str(get_dec_from_float(self.gameEndTime / 1000))


                if self.gameEndTime < 0 and self.host:
                    self.init_state(3)
                    return


                if self.current_number != -1:

                    self.inputBet.user_text = str(self.currentBet[self.current_number - 3])

                    self.btnBet.text_input = "Bet number " + str(self.current_number)

                    
                    self.inputBet.update(screen)
                    self.btnBet.update(screen)
            case 3:
                self.diceRollTime -= delta

                if self.diceRollTime < 0 and self.host:
                    self.init_state(4)
                    return
                try:
                    self.listBtn[int(self.txtTitleStr)].image = self.imgBtnNumberDisable
                except:
                    pass
                dice1 = random.choice(range(5)) + 1
                dice2 = random.choice(range(5)) + 1
                dice3 = random.choice(range(5)) + 1
                self.dice1.text_input = str(dice1)
                self.dice2.text_input = str(dice2)
                self.dice3.text_input = str(dice3)
                result = (dice1 + dice2 + dice3)
                self.txtTitleStr = str(result)
                self.listBtn[result].image = self.imgBtnNumber
                



                
             

            case 4:
                if self.host:
                # print(4)
                    self.state_time -= delta
                    if self.state_time < 0:
                        self.init_state(0)
                pass


        screen.blit(get_font(30).render("Total players: " + str(self.playerCount), True, "white"), (20,20))
        screen.blit(get_font(30).render("Ready players: " + str(self.ready), True, "white"), (20,40))
        if not self.host:
            screen.blit(self.txtPlayerName, (20, 60))

        


        self.btnBack.update(screen)

        self.dice1.update(screen)
        self.dice2.update(screen)
        self.dice3.update(screen)

        # 
        screen.blit(get_font(30).render("+", True, "white"), (self.dice2.rect.x - 16, self.dice2.rect.y + 26))
        screen.blit(get_font(30).render("+", True, "white"), (self.dice2.rect.x + 84, self.dice2.rect.y + 26))





        title_pos_x = (screen_width * 2 / 3 + 20) / 2
        title_pos_y = 100
        self.txtTitle = get_font(40).render(self.txtTitleStr, True, "white")
        screen.blit(self.txtTitle, (title_pos_x - self.txtTitle.get_rect().width / 2, title_pos_y))

        # for btn in self.listBtn:
        #     if btn.checkForInput(pos):

        for btn in self.listBtn:
            if self.state == 2:
                btn.image = self.imgBtnNumber
            btn.update(screen)
        for price in self.listPrice:
            price.update(screen)

        self.inputMess.update(screen)

    def key_down(self, event):
        if event.key == pygame.K_RETURN:
            txt = self.player_name + ": " + self.inputMess.user_text
            if self.host:
                self.messHistory.append(txt)
                self.server_send("mess", txt)
            else:
                self.client_send("mess", txt)
            self.inputMess.clear_user_txt()
        self.inputMess.check_input(event)

        try:
            int(event.unicode)
            number = self.inputBet.check_input(event)
            self.currentBet[self.current_number - 3] = number
        except:
            if event.key == pygame.K_BACKSPACE:
                number = (self.inputBet.check_input(event))
                if number == "":
                    number = 0
                else:
                    number = int(number)
                self.currentBet[self.current_number - 3] = number

        # if event.unicode
        # if int(numberBet):
    
    def init_state(self, state):
        match state:
            case 0:
                for btn in self.listBtn:
                    btn.image = self.imgBtnNumberDisable
                
                self.txtTitleStr = "Waiting all ready" 
                self.currentConfirm = []
                    
                self.dice1.image = self.imgDiceDisable
                self.dice2.image = self.imgDiceDisable
                self.dice3.image = self.imgDiceDisable

                self.dice1.text_input = "?"
                self.dice2.text_input = "?"
                self.dice3.text_input = "?"

                self.playerReady = False
                self.ready = 0
                if self.host:
                    self.server_send("state", 0)
            case 1:
                self.readyTime = self.readyCountTime * 1000
                pass

            case 2:
                self.gameEndTime = self.gameEndCountTime * 1000

                pass
            case 3:
                self.diceRollTime = self.diceRollCountTime * 1000
                self.dice1.image = self.imgDice
                self.dice2.image = self.imgDice
                self.dice3.image = self.imgDice
                for btn in self.listBtn:
                    btn.image = self.imgBtnNumberDisable
                pass
            case 4:
                
                for btn in self.listBtn:
                    btn.image = self.imgBtnNumberDisable
                

                if self.host:
                    result = (self.dice1.text_input, self.dice2.text_input, self.dice3.text_input)
                    self.server_send("result", ','.join(result))
                self.state_time = 5000

                self.listBtn[int(self.txtTitleStr) - 3].image = self.imgBtnNumber

                for bet in self.currentConfirm:
                    print(bet)
                    global player_money
                    if (bet[0] == int(self.txtTitleStr)):
                        price = int(bet[1]) * self.price_scale(bet[0])
                        player_money+= price
                        print(price)

                pass
                
            case 5:
                pass

        self.state = state
        if self.host and self.state != 4:
            self.server_send("state", state)



    def init_btn_number(self, number):
        padding = 10
        scale_x = 90
        scale_y = 90

        init_x = 150
        init_y = 300

        pos_x = init_x + (((number) % 4) * (scale_x + padding))
        pos_y = init_y + (get_dec_from_float((number)/ 4)) * (scale_y + padding)

        if (self.state == 2):
            btnImg = self.imgBtnNumber
        else:
            btnImg = self.imgBtnNumberDisable

        btnImg = pygame.transform.smoothscale(btnImg, (scale_x, scale_y))

        tmp = Button(image=btnImg, pos=(pos_x,pos_y), text_input=str(number + 3), font=get_font(40), base_color="black", hovering_color="yellow")
        tmp.update(screen)
        return tmp

    def init_txt_price(self, number):
        padding = 10
        scale_x = 90
        scale_y = 90

        init_x = 150
        init_y = 350

        pos_x = init_x + (((number) % 4) * (scale_x + padding))
        pos_y = init_y + (get_dec_from_float((number)/ 4)) * (scale_y + padding)

        if (self.state == 2):
            btnImg = self.imgBtnNumber
        else:
            btnImg = self.imgBtnNumberDisable

        btnImg = pygame.transform.smoothscale(btnImg, (scale_x, scale_y))

        tmp = Button(image=None, pos=(pos_x,pos_y), text_input="x" + str(self.price_scale(number + 3)), font=get_font(20), base_color="white", hovering_color="yellow")
        tmp.update(screen)
        return tmp
    
    def mouse_down(self, pos):
        self.inputMess.active_check(pos)
        self.inputBet.active_check(pos)

        if self.btnBack.checkForInput(pos):
            global room, screen_id
            room.close = True
            room.server.close()
            room = MainMenu(screen_width, screen_height)
            screen_id = 1

        match self.state:
            case 0:
                if (self.btnReady.checkForInput(pos)):
                    self.playerReady = True
                    if not self.host:
                        self.client_send("ready")
                    else:
                        self.ready += 1
                        self.server_send("ready", self.ready)
                if self.ready == self.playerCount:
                    self.readyTime = 1000 * self.playerCount
            case 1:
                pass
            case 2: 
                for btn in self.listBtn:
                    if btn.checkForInput(pos):
                        self.current_number = int(btn.text_input)
                        self.current_button = btn

                global player_money
                if self.btnBet.checkForInput(pos) and player_money > int(self.inputBet.user_text) and len(self.currentConfirm) < 4:
                        player_money -= int(self.inputBet.user_text)
                        self.currentConfirm.append([self.current_number, self.inputBet.user_text])
                        # self.listBtn.remove(self.current_button)
                        self.current_number = -1
                        # if self.host:
                        #     self.server_send("bet", self.roomBet)
    


    def server_rev(self, client):
        while True:
            try:
                request = client.recv(1024)
                if request is None:
                    self.clients.remove(client)
                    self.playerCount -=1
                    self.ready = 0
                    self.server_send("player_count", self.playerCount)
                    self.server_send("ready", 0)
                request = request.decode("utf-8")

                print("Server rev: " + request)
                # if request == "#close":
                #     self.client.close()
                #     self.clients.remove(client)
                request = request.split("/")
                match request[0]:
                    case "#mess":
                        self.server_send("mess", request[1])
                        self.messHistory.append(request[1])

                    case "#getname":
                        client.send(self.room_name.encode())
                        self.clients.remove(client)
                    
                    case "#join":
                        print(request[1] + "joining")
                        self.messHistory.append(request[1] + " joined room")
                        time = self.diceRollTime
                        client.send(pickle.dumps(SeverData(self.state, time, self.ready, self.playerCount, self.roomBet)))
                        self.server_send("mess", request[1] + " joined room")
                    case "#ready":
                        self.ready += 1
                        self.server_send("ready", self.ready)

                    case "#bet":
                        pass
                        # except:
                        #     # self.clients.remove(client)
                        #     print("error")
                        #     pass



                        # print("rev " + request)
            except:
                print("client connect error")
                self.clients.remove(client)
                self.messHistory.append("player out")
                self.playerCount -= 1
                self.server_send("player_count", self.playerCount)
    
    def client_rev(self):
        while True:
            try:
                print("client listen")
                # self.client.settimeout(1)
                request = self.client.recv(1024)
                print(request)

                if request is None:
                    global screen_id, room
                    screen_id = 1
                    room = MainMenu(screen_width, screen_height)

                request = request.decode().split("/")
                match request[0]:
                    case "#mess":
                        self.messHistory.append(request[1])
                    case "#player_count":
                        self.playerCount = int(request[1])
                    case "#state":
                        self.init_state(int(request[1]))
                    case "#ready":
                        self.ready = int(request[1])
                    case "#result":
                        result = request[1].split(',')
                        self.dice1.text_input = result[0]
                        self.dice2.text_input = result[1]
                        self.dice3.text_input = result[2]
                        self.txtTitleStr = str(int(result[0]) + int(result[1]) + int(result[2]))
                        self.init_state(4)
                        
                    case "bet":
                        self.roomBet = pickle.loads(request[1])
            except:
                return
                pass

    def client_send(self, type, value = None):
        print("client send", type)
        match type:
            case "mess":
                self.client.send(("#mess/" + value).encode())
            case "bet":
                self.client.send("#bet/".encode() + pickle.dumps(self.roomBet))
            case "ready":
                self.client.send("#ready".encode())
            case "joinned":
                # self.client_send("#joinned")
                pass
            case "close":
                self.client.send("#close".encode())
        pass

    def server_send(self, type, value = None):
        value = str(value)
        match type:
            case "player_count":
                self.server_broadcast("#player_count/" + value)
            case "state":
                self.server_broadcast("#state/" + value)
            case "ready":
                self.server_broadcast("#ready/" + value)
            case "join":
                self.server_broadcast("#join/" + value)
            case "mess":
                self.server_broadcast("#mess/" + value)
            case "result":
                self.server_broadcast("#result/" + value)
            case "bet":
                self.server_broadcast("#bet/" + pickle.dumps(value))

    def server_broadcast(self, string):
        for client in self.clients:
            try:
                client.send(string.encode())
            except:
                continue

    # def server_room_bet(self, room_bet):
    def mouse_motion(self, pos):
        self.btnReady.changeColor(pos)
        self.btnBet.changeColor(pos)
        self.btnBack.changeColor(pos)


    def start_broadcast_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
            server_socket.bind(('', 65432))
            while True:
                if self.close:
                    server_socket.close()
                    return
                try:
                    server_socket.settimeout(1)
                    message, address = server_socket.recvfrom(1024)
                    print(f"Received message from {address}: {message}")
                    if message == b'discover' and self.state == 0:
                        server_socket.sendto(self.player_name.encode(), address)
                except:
                    pass

        pass

            
            
    
    def server_add_connect(self):
        while True:
            try:
                client_socket, client_address = self.server.accept()
                print(str(client_address) + "connected")
                self.clients.append(client_socket)
                self.playerCount += 1
                self.server_send("player_count", self.playerCount)
                threading.Thread(target=self.server_rev, daemon=True, args=(client_socket,)).start()

                # client_socket.send(pickle.dumps(SeverData(room.state, room.time, room.playerCount, room.roomBet)))
            except:
                print("server add connect error")
                return
        

class SeverData():
    def __init__(self, state, time, ready, player_count, total_bet) -> None:
        self.state = state
        self.time = time
        self.ready = ready
        self.player_count = player_count
        self.total_bet = total_bet



room = MainMenu(screen_width, screen_height)
delta = None

screen_id = 1

while running:

    delta = clock.get_time()
    mouse_pos = pygame.mouse.get_pos()


    match screen_id:
        case 1:
            for event in pygame.event.get():
                
                if event.type == pygame.MOUSEMOTION:
                    room.mouse_motion(mouse_pos)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    match room.mouse_down(mouse_pos):
                        case 1:
                            print(room.playerName)
                            player_name = room.playerName
                            room = Room(True, player_name, room.playerName)
                            screen_id = 2
                        case 2:
                            room.join_init()
                            continue
                        
                        case 3:
                            room.client.send("close".encode())
                            room.client.close()
                            running = False
                            
                        case -2:
                            tmp = Room(False, room.room_name, room.playerName, room.client)
                            tmp.state = room.room_data.state
                            tmp.playerCount = room.room_data.player_count
                            tmp.ready = room.room_data.ready
                            tmp.diceRollTime = room.room_data.time
                            tmp.roomBet = room.room_data.total_bet
                            tmp.init_state(tmp.state)
                            del room
                            room = tmp
                            screen_id = 2
                            # tmp.client_send("joinned")
                            

                if event.type == pygame.KEYDOWN:
                    room.key_down(event)
                    
                if event.type == pygame.QUIT:
                    room.client.send("close".encode())
                    room.client.close()
                    running = False

            room.update(delta, screen)

        case 2:
            for event in pygame.event.get():
                
                if event.type == pygame.MOUSEMOTION:
                    room.mouse_motion(mouse_pos)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    room.mouse_down(mouse_pos)

                if event.type == pygame.KEYDOWN:
                    room.key_down(event)
                    

                if event.type == pygame.QUIT:
                    if room.host:
                        room.server.close()
                    else:
                        room.client_send("close")
                    running = False


            room.update(delta, screen)
    pygame.display.update()

    clock.tick(60)


pygame.quit()

    