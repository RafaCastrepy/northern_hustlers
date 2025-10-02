import pygame
import sys
import sqlite3
import random
# Initialize Pygame
pygame.init()

# Constants for the window
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

w_con = WIDTH


BACKGROUND_COLOR = (150, 150, 150)
FONT = pygame.font.SysFont("verdana", 24)


class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("The Northern Hustle")
        self.background2 = pygame.image.load("bg2.png")
        self.background2 = pygame.transform.scale(self.background2, (self.width, self.height))

    def update(self):
        self.screen.blit(self.background2, (0, 0))


class MessageBox:
    def __init__(self, game_window, start_cords, width, height, font):
        self.game_window = game_window
        self.width = width
        self.height = height
        self.font = font
        self.text = ""
        self.box_color = (220, 220, 220)
        self.text_color = (0, 0, 0)
        self.position = start_cords

    def set_text(self, new_text):
        self.text = new_text

    def draw(self):
        pygame.draw.rect(self.game_window.screen, self.box_color, 
                         (self.position[0], self.position[1], self.width, self.height))
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            self.game_window.screen.blit(text_surface, (self.position[0]+50, self.position[1]+10))

class Info_Box(MessageBox):
    def __init__(self, game_window, start_cords, width, height, font, player):
        super().__init__(game_window, start_cords, width, height, font)
        self.player = player

    def balance_display(self):
        if self.player.bankrupt == True:
            self.set_text("HUSTLED")
        else:
            self.set_text(f"Player {self.player.name}: £{self.player.balance}")

    def draw(self):
        pygame.draw.rect(self.game_window.screen, self.box_color, 
                         (self.position[0], self.position[1], self.width, self.height))
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            self.game_window.screen.blit(text_surface, (self.position[0]+10, self.position[1]+10))


class Sign(MessageBox):
    def __init__(self, game_window, start_cords, width, height, font):
        super().__init__(game_window, start_cords, width, height, font)
    
    def draw(self):
        pygame.draw.rect(self.game_window.screen, self.box_color, 
                         (self.position[0], self.position[1], self.width, self.height))
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            self.game_window.screen.blit(text_surface, (self.position[0]+10, self.position[1]+10))



class Player:
    def __init__(self, name, position, balance, in_jail, color, board, game_window, sprite_path):
        self.name = name
        self.position = position
        self.balance = balance
        self.in_jail = in_jail
        self.board = board
        self.game_window = game_window
        self.size = 50
        self.color = color
        
        self.bankrupt = False
        self.remaining_turns_in_jail = 0

        self.sprite = pygame.image.load(sprite_path).convert_alpha()
        
        self.sprite = pygame.transform.scale(self.sprite, (self.size, self.size))
        self.flipped_sprite = pygame.transform.flip(self.sprite, flip_x=True, flip_y=False)

        if self.name == 1:
            self.hor_offset = 10
            self.ver_offset = 0
        elif self.name == 2:
            self.hor_offset = 30
            self.ver_offset = 0
        elif self.name == 3:
            self.hor_offset = 10
            self.ver_offset = 20
        else:
            self.hor_offset = 30
            self.ver_offset = 20

        self.cords = [40 + self.hor_offset,60 + self.ver_offset]
    
    def take_turn(self):
        if self.bankrupt == True:
            state.skip()
            return
        roll = random.randint(1,6)
        self.position += roll
        if self.position >= 24:
            self.position -= 24
            self.balance += 20
        
        if self.position == 18:
            self.position = 6
            state.jailed.append(self.name)
            self.remaining_turns_in_jail = 3
            message_box.set_text(f"Player {self.name}, has been caught for tax evasion and will spend 3 turns in Strange Ways Prison")
            



        board_cords = board.tiles[self.position].start_cords
        self.cords[0] = board_cords[0] + self.hor_offset
        self.cords[1] = board_cords[1] + self.ver_offset

        if self.position not in [0,6,12,18]:
            state.current_property = self.board.tiles[self.position].property
            if state.current_property.owner_id == 0:
                self.offer_purchase(state.current_property)
            else:
                self.pay_rent(state.current_property)
        else:
            state.next_player()
                
       
    def turn_in_jail(self):
        self.remaining_turns_in_jail -= 1
        if self.remaining_turns_in_jail == 0:
            state.jailed.remove(self.name)
                


    
    def offer_purchase(self, property):
        if self.balance >= property.cost:
            message_box.set_text(f"Player {self.name}, Do you want to buy {property.name} for £{property.cost}?   Current Funds: £{self.balance}")
            state.set_state("offer_purchase")
                
        else:
            message_box.set_text(f"Player {self.name}, you cannot afford {property.name} for £{property.cost}.   Current Funds: £{self.balance}")
            state.next_player()
           


    def pay_rent(self, property):
        if property.cost > self.balance:
            players[property.owner_id].balance += self.balance
            self.balance = 0
            self.bankruptcy()
        else:
            self.balance -= property.cost
            players[property.owner_id].balance += property.cost
            message_box.set_text(f"Player {self.name} ({self.balance}) has paid {property.cost} to Player {players[property.owner_id].name} ({players[property.owner_id].balance})")
        state.next_player()
    
    def bankruptcy(self):
        #state.max_players -= 1
        self.bankrupt = True
        for item in property_list:
            if item.owner_id == self.name:
                item.owner_id = 0
        counter = 0
        has_money = []
        for person in range(1,5):
            if players[person].bankrupt == True:
                counter += 1
            else:
                has_money.append(players[person])
        if counter == 3:
            print(f"Winner is Player {has_money[0].name}")
            state.winner = has_money[0].name
        
            
        
        

    def draw(self):
        if self.bankrupt == True:
            return
        
        if self.position >= 6 and self.position <= 17:
            self.game_window.screen.blit(self.flipped_sprite, self.cords)
        else:
            self.game_window.screen.blit(self.sprite, self.cords)

        

class Button:
    def __init__(self, x, y, width, height, text, font, bg_colour, text_colour, hover_colour, border_colour, screen, border_thickness=3):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_colour = bg_colour
        self.text_colour = text_colour
        self.hover_colour = hover_colour
        self.border_colour = border_colour
        self.border_thickness = border_thickness
        self.screen = screen
        self.visible = True

    def set_text(self, new_text):
        self.text = new_text

    def draw(self):
        if not self.visible:
            return

        mouse_pos = pygame.mouse.get_pos()
        colour = self.hover_colour if self.rect.collidepoint(mouse_pos) else self.bg_colour

        # Draw border
        pygame.draw.rect(self.screen, self.border_colour, self.rect.inflate(self.border_thickness * 2, self.border_thickness * 2), border_radius=12)

        # Draw button rectangle
        pygame.draw.rect(self.screen, colour, self.rect, border_radius=10)

        # Draw text
        text_surface = self.font.render(self.text, True, self.text_colour)
        text_rect = text_surface.get_rect(center=self.rect.center)
        self.screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def hide(self):
        self.visible = False

    def show(self):
        self.visible = True

    def toggle(self):
        self.visible = not self.visible

class Property:
    property_count = 0

    def __init__(self, name, cost, message_box, owner_id, mortgaged):
        self.name = name 
        self.cost = cost
        self.houses_built = 0
        self.hotel_built = False
        self.morgaged = False
        self.message_box = message_box
        self.owner_id = 0

    def purchase(self, owner):
        self.owner_id = owner

    def display_info(self):
        if state.current_state == "neutral":
            ids = {0:"Un-purchased", 1:"Player 1", 2:"Player 2", 3:"Player 3", 4:"Player 4"}
            self.message_box.set_text(f"Name: {self.name},   Cost: £{self.cost},   Owner: {ids[self.owner_id]}")


class Base:
    def __init__(self, game_window, start_cords, width, height):
        self.fill_colour = (255, 255, 255)
        self.rim_colour = (0, 0, 0)
        self.start_cords = start_cords
        self.margin_width = 2
        self.width = width
        self.WIDTH = width
        self.height = height
        self.HEIGHT = height
        self.game_window = game_window

        self.growth_factor = 1.3

    def sub_box(self, rel_width, rel_height, sub_fill_colour, rel_x_cord, rel_y_cord):
        real_width = self.width * rel_width
        real_height = self.height * rel_height
        real_cords = (
            ((self.width - real_width) * rel_x_cord) + self.start_cords[0], 
            ((self.height - real_height) * rel_y_cord) + self.start_cords[1]
        )

        pygame.draw.rect(self.game_window.screen, self.rim_colour, 
                         (real_cords[0], real_cords[1], real_width, real_height))
        
        pygame.draw.rect(self.game_window.screen, sub_fill_colour, 
                         (real_cords[0] + self.margin_width, real_cords[1] + self.margin_width, 
                          real_width - 2 * self.margin_width, real_height - 2 * self.margin_width))

    def draw(self):
        self.sub_box(1, 1, self.fill_colour, 0, 0)  # Draw the main box

    def is_hovered(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        x, y = self.start_cords
        return x <= mouse_x <= x + self.width and y <= mouse_y <= y + self.height

    def enlarge(self):
        if self.is_hovered():
            self.width = self.WIDTH * self.growth_factor
            self.height = self.HEIGHT * self.growth_factor
        else:
            self.width = self.WIDTH
            self.height = self.HEIGHT



class Corner(Base):
    def __init__(self, game_window, start_cords, width, height):
        super().__init__(game_window, start_cords, width, height)
        self.margin_width = 5

    def draw(self):
        super().draw()  # Call the base class draw function
        

class Property_Tile(Base):
    def __init__(self, game_window, start_cords, width, height, orientation, the_property):
        super().__init__(game_window, start_cords, width, height)
        self.orientation = orientation
        if self.orientation == "n" or self.orientation == "s":
            self.width = width 
            self.WIDTH = width
            self.height = height
            self.HEIGHT = height
        else:
            self.width = height  # More balanced width
            self.WIDTH = height
            self.height = width
            self.HEIGHT = width
        self.margin_width = 5

        self.property = the_property

    def draw(self):
        super().draw()  # Call the base class draw function
        if self.orientation == "n":
            self.sub_box(1, 0.3, (255, 0, 0), 0, 0)  # Additional design
        elif self.orientation == "s":
            self.sub_box(1, 0.3, (255, 255, 0), 0, 1)  # Additional design
        elif self.orientation == "w":
            self.sub_box(0.3, 1, (0, 255, 0), 0, 0)  # Additional design
        elif self.orientation == "e":
            self.sub_box(0.3, 1, (0, 0, 255), 1, 0)  # Additional design


    def info_dump(self):
        if self.is_hovered():
            self.property.display_info()


class Board:
    def __init__(self, game_window, property_list, start_cords, prop_width, prop_height):
        self.game_window = game_window
        self.prop_width = prop_width
        self.prop_height = prop_height
        self.start_cords = start_cords
        self.property_list = property_list
        self.tiles = []  # Store created properties

        self.create_properties()  # Create properties at initialization

    def create_properties(self):
        spawn_cords = self.start_cords
        x_change = self.prop_width
        y_change = 0

        for row in range(4):  # This only creates one row for now
            for space in range(6):
                if row == 0:
                    if space == 0:
                        self.tiles.append(Corner(self.game_window, spawn_cords, self.prop_height, self.prop_height))
                        spawn_cords = (spawn_cords[0] + self.prop_height, spawn_cords[1])
                    else:
                        self.tiles.append(Property_Tile(self.game_window, spawn_cords, self.prop_width, self.prop_height, "n", self.property_list[Property.property_count]))
                        Property.property_count += 1
                        spawn_cords = (spawn_cords[0] + self.prop_width, spawn_cords[1])
                elif row == 1:
                    if space == 0:
                        spawn_cords = (spawn_cords[0], spawn_cords[1])
                        self.tiles.append(Corner(self.game_window, spawn_cords, self.prop_height, self.prop_height))
                        spawn_cords = (spawn_cords[0], spawn_cords[1] + self.prop_height)
                    else:
                        self.tiles.append(Property_Tile(self.game_window, spawn_cords, self.prop_width, self.prop_height, "e", self.property_list[Property.property_count]))
                        Property.property_count += 1
                        spawn_cords = (spawn_cords[0], spawn_cords[1] + self.prop_width)
                elif row == 2:
                    if space == 0:
                        #spawn_cords = (spawn_cords[0], spawn_cords[1] - self.prop_width)
                        self.tiles.append(Corner(self.game_window, spawn_cords, self.prop_height, self.prop_height))
                        spawn_cords = (spawn_cords[0] - self.prop_width, spawn_cords[1])
                    else:
                        self.tiles.append(Property_Tile(self.game_window, spawn_cords, self.prop_width, self.prop_height, "s", self.property_list[Property.property_count]))
                        Property.property_count += 1
                        spawn_cords = (spawn_cords[0] - self.prop_width, spawn_cords[1])
                elif row == 3:
                    if space == 0:
                        spawn_cords = (spawn_cords[0] - self.prop_height + self.prop_width, spawn_cords[1])
                        self.tiles.append(Corner(self.game_window, spawn_cords, self.prop_height, self.prop_height))
                        spawn_cords = (spawn_cords[0], spawn_cords[1] - self.prop_width)
                    else:
                        self.tiles.append(Property_Tile(self.game_window, spawn_cords, self.prop_width, self.prop_height, "w", self.property_list[Property.property_count]))
                        Property.property_count += 1
                        spawn_cords = (spawn_cords[0], spawn_cords[1] - self.prop_width)

    def draw(self):
        for space in self.tiles:
            #space.enlarge()
            space.draw()

    def info_dump(self):
        for i in range(24):
            if i not in [0,6,12,18]:
                self.tiles[i].info_dump()



def fetch_properties_from_db():
    conn = sqlite3.connect("monopoly_game.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, price FROM Property")
    properties = cursor.fetchall()
    conn.close()
    return properties

class Game_State:
    def __init__(self):
        self.current_player = 1
        self.current_state = "neutral"
        self.current_property = "null"
        self.winner = 0
        self.max_players = 4
        self.jailed = []
        

    
    def advance(self):
        players[self.current_player].take_turn()
        
        
    def skip(self):
        self.next_player()
        players[self.current_player].take_turn()
        
    
    def next_player(self):
        self.current_player += 1
        #print(f"max players = {self.max_players}")
        if self.current_player > (self.max_players):
            self.current_player = 1
        advance_button.set_text(f"Player {state.current_player}'s Roll")
        if self.current_player in self.jailed:
            players[self.current_player].turn_in_jail()
            self.next_player()
        if players[self.current_player].bankrupt:
            self.next_player()
        
    def set_state(self, new_state):
        self.current_state = new_state
        if new_state == "neutral":
            advance_button.show()
            yes_button.hide()
            no_button.hide()
            

        elif new_state == "offer_purchase":
            advance_button.hide()
            yes_button.show()
            no_button.show()



def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if advance_button.is_clicked(event):
                state.advance()
            if state.current_state == "offer_purchase":
                if yes_button.is_clicked(event):
                    state.current_property.purchase(players[state.current_player].name)
                    players[state.current_player].balance -= state.current_property.cost
                    state.set_state("neutral")
                    state.next_player()
                elif no_button.is_clicked(event):
                    state.set_state("neutral")
                    state.next_player()
                
                    

        game_window.update()
        board.draw()


        # Call info_dump during each frame to check for hover
        board.info_dump()

        message_box.draw()
        for box in info_boxs:
            box.draw()
            box.balance_display()
     
        go_sign.draw()
        jail_sign.draw()
        go_to_jail_sign.draw()

        for i in range(1,5):
            players[i].draw()

        
        
        
        advance_button.draw()
        yes_button.draw()
        no_button.draw()

        if state.winner != 0:
            return state.winner

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def player_selection():
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Check if any of the buttons are clicked
            if button1.is_clicked(event):
                print("2 Players Selected")
                return 2
            if button2.is_clicked(event):
                print("3 Players Selected")
                return 3
            if button3.is_clicked(event):
                print("4 Players Selected")
                return 4

        # Fill the screen with a color (white for now)
        game_window.screen.fill((255, 255, 255))
        game_window.screen.blit(background, (0, 0))

        # Draw the buttons
        button1.draw()
        button2.draw()
        button3.draw()

        # Blit the images onto the screen
        game_window.screen.blit(image1, image1_rect)
        game_window.screen.blit(image2, image2_rect)
        game_window.screen.blit(image3, image3_rect)

        # Update the display
        pygame.display.flip()


        

        pygame.display.flip()
        pygame.time.Clock().tick(60)

def win_screen():
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


        # Fill the screen with a color (white for now)
        game_window.screen.fill((255, 255, 255))
        game_window.screen.blit(background, (0, 0))


        # Update the display
        pygame.display.flip()
        pygame.time.Clock().tick(60)

if __name__ == "__main__":

    game_window = Window(WIDTH, HEIGHT)
    background2 = pygame.image.load("bg2.png")
    background2 = pygame.transform.scale(background2, (WIDTH, HEIGHT))


    # Load the images (replace '2Players.png', '3Players.png', '4Players.png' with your image paths)
    image1 = pygame.image.load('2Players.png')
    image2 = pygame.image.load('3Players.png')
    image3 = pygame.image.load('4Players.png')

    # Scale the images to double their size
    image1 = pygame.transform.scale(image1, (image1.get_width() * 2, image1.get_height() * 2))
    image2 = pygame.transform.scale(image2, (image2.get_width() * 2, image2.get_height() * 2))
    image3 = pygame.transform.scale(image3, (image3.get_width() * 2, image3.get_height() * 2))

    # Get the new image sizes
    image1_rect = image1.get_rect()
    image2_rect = image2.get_rect()
    image3_rect = image3.get_rect()

    # Load the background image (replace 'CHARbg.png' with your image path)
    background = pygame.image.load('CHARbg.png')

    # Scale the background to fit the screen (in case the image size is different)
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Set the Y position to be along the "equator" (middle of the screen)
    equator_y = HEIGHT // 2

    # Calculate the X positions so they're equally spaced
    space = (WIDTH // 4) - 310  # Space between images
    x1 = space
    x2 = 2 * space + image2_rect.width
    x3 = 3 * space + 2 * image3_rect.width

    # Set the rect positions
    image1_rect.topleft = (x1, equator_y - image1_rect.height // 2)
    image2_rect.topleft = (x2, equator_y - image2_rect.height // 2)
    image3_rect.topleft = (x3, equator_y - image3_rect.height // 2)

    button1 = Button(x1+130, equator_y + 180, 150, 50, "2 Players", FONT, 
                 (0, 128, 0), (255, 255, 255), (0, 255, 0), (0, 0, 0), game_window.screen)

    button2 = Button(x2+130, equator_y + 180, 150, 50, "3 Players", FONT, 
                 (0, 128, 0), (255, 255, 255), (0, 255, 0), (0, 0, 0), game_window.screen)

    button3 = Button(x3+130, equator_y + 180, 150, 50, "4 Players", FONT, 
                 (0, 128, 0), (255, 255, 255), (0, 255, 0), (0, 0, 0), game_window.screen)


    num_of_players = player_selection()

    print("worker bee")

    
    message_box = MessageBox(game_window, [0,0], WIDTH, 50, FONT)

    go_sign = Sign(game_window, [50,95], 70, 50, FONT)
    go_sign.set_text("GO!")
    jail_sign = Sign(game_window, [550,95], 70, 50, FONT)
    jail_sign.set_text("JAIL")
    go_to_jail_sign = Sign(game_window, [50,585], 70, 50, FONT)
    go_to_jail_sign.set_text("Feds")

    # Fetch properties from the database
    property_data = fetch_properties_from_db()
    
    # Pass the message_box correctly to each Property instance
    property_list = [Property(name, cost, message_box, False, False) for name, cost in property_data]
    
    board = Board(game_window, property_list, (30, 60), 75, 118)

    advance_button = Button(700, 150, 175, 70, "Roll!", FONT, "#3075FF", "black", "#003192", "black", game_window.screen)

    yes_button = Button(700, 350, 150, 60, "Yes", FONT, "#52CD1E", "black", "#226803", "black", game_window.screen)

    no_button = Button(700, 500, 150, 60, "No", FONT, "#52CD1E", "black", "#226803", "black", game_window.screen)

    print(f"num of players {num_of_players}")
    state = Game_State()

    state.set_state("neutral")

    players = {1:Player(1, 0, 500, False, "red", board, game_window, "Red man.png"), 2:Player(2, 0, 500, False, "blue", board, game_window, "Blue man.png"),
               3:Player(3, 0, 500, False, "yellow", board, game_window, "Purple man.png"), 4:Player(4, 0, 500, False, "green", board, game_window, "Green man.png")}
    
    info_boxs = [Info_Box(game_window, [1000, 100], 200, 50, FONT, players[1]), Info_Box(game_window, [1000, 250], 200, 50, FONT, players[2]),
        Info_Box(game_window, [1000, 400], 200, 50, FONT, players[3]), Info_Box(game_window, [1000, 550], 200, 50, FONT, players[4])]

    if num_of_players == 2:
        players[3].bankruptcy()
        players[4].bankruptcy()
    elif num_of_players == 3:
        players[4].bankruptcy()

    winner = game_loop()

    # Load the background image (replace 'CHARbg.png' with your image path)
    win_screens = {1:pygame.image.load('HUSTLED1.png'), 2:pygame.image.load('HUSTLED2.png'), 
                   3:pygame.image.load('HUSTLED3.png'), 4:pygame.image.load('HUSTLED4.png')}

    # Scale the background to fit the screen (in case the image size is different)
    background = pygame.transform.scale(win_screens[winner], (WIDTH, HEIGHT))

    win_screen()