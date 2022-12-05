"""
Main file responsible for handling user input and displaying the current game state object.
"""

import pygame, engine


width = height = 512
dimension = 8 # dimension of the board
square_size = height // dimension
max_fps = 15 # for animation
images = {}

# Load images

def load_images():

    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']

    for piece in pieces:
        images[piece] = pygame.transform.scale(pygame.image.load("images/"+ piece + ".png"), (square_size, square_size))

# Handling user input and displaying graphics

def main():

    pygame.init()

    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    gs = engine.GameState() # GameState object
    valid_moves = gs.get_valid_moves()
    move_made = False
    
    load_images()

    running = True

    square_selected = () # keep track of the last user click, tuple: (row, col)
    player_clicks = [] # keep track of the user clicks, two tuples [(row, col), (row, col)]


    while running:

        for e in pygame.event.get():

            if e.type == pygame.QUIT:
                running = False
            
            elif e.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos() # (x, y) getting the location of the mouse
                col = location[0] // square_size
                row = location[1] // square_size

                if square_selected == (row, col): # selected the same square twice
                    square_selected = () # deselect the square
                    player_clicks = [] # clear player clicks

                else:
                    square_selected = (row, col)
                    player_clicks.append(square_selected)

                if len(player_clicks) == 2: # after 2nd click
                    move = engine.Move(player_clicks[0], player_clicks[1], gs.board)

                    print(move.get_chess_notation())

                    for i in range(len(valid_moves)):

                        if move == valid_moves[i]:
                            gs.make_move(valid_moves[i])
                            move_made = True
                            square_selected = () # reset the user clicks
                            player_clicks = []

                    if not move_made:
                        player_clicks = [square_selected] 
            
            elif e.type == pygame.KEYDOWN:

                if e.key == pygame.K_z:
                    gs.undo_move() 
                    move_made = True                   
                
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(max_fps)
        pygame.display.flip()


# Draw the graphics in the current game state
def draw_game_state(screen, gs):
    
    draw_board(screen)
    draw_pieces(screen, gs.board)


def draw_board(screen):
    
    colors = [pygame.Color("white"), pygame.Color("gray")]

    for r in range(dimension):

        for c in range(dimension):

            color = colors[((r + c) % 2)]

            pygame.draw.rect(screen, color, pygame.Rect(c * square_size, r * square_size, square_size, square_size))


def draw_pieces(screen, board):
    
    for r in range(dimension):

        for c in range(dimension):

            piece = board[r][c]

            if piece != "--": # Not empty square
                screen.blit(images[piece], pygame.Rect(c * square_size, r * square_size, square_size, square_size))



if __name__ == '__main__':
    main()