import pygame
import chess
from time import sleep
from Board import GUI_Board
import Bot

def draw_gradient_background(display, width, height):
    """Draw a beautiful gradient background"""
    for y in range(height):
        color_ratio = y / height
        # Elegant dark to light brown gradient
        r = int(101 + (139 - 101) * color_ratio)
        g = int(67 + (116 - 67) * color_ratio)
        b = int(33 + (78 - 33) * color_ratio)
        pygame.draw.line(display, (r, g, b), (0, y), (width, y))

def draw_move_history_panel(display, move_history, font, panel_rect):
    """Draw the elegant move history panel"""
    # Panel background with gradient
    panel_surface = pygame.Surface((panel_rect.width, panel_rect.height))
    for y in range(panel_rect.height):
        ratio = y / panel_rect.height
        r = int(240 + (220 - 240) * ratio)
        g = int(230 + (210 - 230) * ratio)
        b = int(200 + (180 - 200) * ratio)
        pygame.draw.line(panel_surface, (r, g, b), (0, y), (panel_rect.width, y))
    
    # Panel border
    pygame.draw.rect(panel_surface, (101, 67, 33), (0, 0, panel_rect.width, panel_rect.height), 3)
    pygame.draw.rect(panel_surface, (139, 116, 78), (2, 2, panel_rect.width - 4, panel_rect.height - 4), 1)
    
    # Title
    title = font.render("History of Move", True, (101, 67, 33))
    title_rect = title.get_rect(centerx=panel_rect.width // 2, y=10)
    panel_surface.blit(title, title_rect)
    
    # Divider line
    pygame.draw.line(panel_surface, (101, 67, 33), 
                    (10, 40), (panel_rect.width - 10, 40), 2)
    
    # Move history
    y_offset = 50
    moves_per_line = 2
    line_height = 25
    
    if move_history:
        for i in range(0, len(move_history), moves_per_line):
            move_text = ""
            move_number = (i // 2) + 1
            
            if i < len(move_history):
                white_move = move_history[i]
                move_text = f"{move_number}. {white_move}"
                
                if i + 1 < len(move_history):
                    black_move = move_history[i + 1]
                    move_text += f" {black_move}"
            
            if move_text and y_offset < panel_rect.height - 30:
                # Highlight the latest move
                text_color = (200, 0, 0) if i >= len(move_history) - 2 else (101, 67, 33)
                move_surface = font.render(move_text, True, text_color)
                panel_surface.blit(move_surface, (15, y_offset))
                y_offset += line_height
    
    display.blit(panel_surface, panel_rect.topleft)

def draw(display, board, move_history, font):
    # Create a beautiful gradient background
    draw_gradient_background(display, TOTAL_WIDTH, TOTAL_HEIGHT)
    
    # Draw the chess board (offset by border)
    board.draw(display)
    
    # Draw move history panel
    panel_rect = pygame.Rect(BOARD_WIDTH + BORDER_WIDTH + 10, BORDER_WIDTH, 
                           PANEL_WIDTH - 20, BOARD_HEIGHT)
    draw_move_history_panel(display, move_history, font, panel_rect)
    
    pygame.display.update()

# Enhanced window dimensions
BOARD_SIZE = (600, 600)
BORDER_WIDTH = 30
PANEL_WIDTH = 250
BOARD_WIDTH, BOARD_HEIGHT = BOARD_SIZE
TOTAL_WIDTH = BOARD_WIDTH + BORDER_WIDTH * 2 + PANEL_WIDTH
TOTAL_HEIGHT = BOARD_HEIGHT + BORDER_WIDTH * 2

if __name__ == '__main__':
    Bot.initialize_openings()
    pygame.init()
    
    # Initialize font
    pygame.font.init()
    font = pygame.font.Font(None, 20)
    
    # Create enhanced screen with side panel
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("Enhanced Luxury Chess Game")
    
    # Set up the game clock for smooth animation
    clock = pygame.time.Clock()
    
    board = GUI_Board(*BOARD_SIZE)
    sequence = []
    move_history = []  # Track move history for display
    opening = True

    running = True
    while running:
        # Handle bot moves
        if board.turn == chess.BLACK and not board.is_animating:
            print("Board value after player has moved:", Bot.get_board_val(board.chess_board))
            move_made = None
            if opening and len(sequence) < 6:
                move_made = Bot.opening_search(board, sequence)
            
            if move_made is None:
                move_made = Bot.minimax_search(board, 4, board.turn == chess.WHITE)
                opening = False

            status = (move_made is not None)
            if opening:
                sequence.append(move_made)
            
            # Add bot move to history
            if move_made:
                move_history.append(move_made)
                
            print("Board value after bot has moved:", Bot.get_board_val(board.chess_board))
            print("--------------------------------------")

            if not status:
                print(board.is_end_game())
                sleep(5)
                break
        
        # Check for game end
        if board.is_end_game() is not False:
            print(board.is_end_game())
            sleep(5)
            break
        
        # Handle events
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not board.is_animating:  # Only handle clicks when not animating
                    # Check if click is within board area
                    board_rect = pygame.Rect(BORDER_WIDTH, BORDER_WIDTH, BOARD_WIDTH, BOARD_HEIGHT)
                    if board_rect.collidepoint(mx, my):
                        # Adjust mouse coordinates for border offset
                        adjusted_mx = mx - BORDER_WIDTH
                        adjusted_my = my - BORDER_WIDTH
                        move_made = board.handle_click(adjusted_mx, adjusted_my)
                        if move_made is not None:
                            if opening: 
                                sequence.append(move_made)
                            # Add player move to history
                            move_history.append(move_made)
        
        # Draw everything
        draw(screen, board, move_history, font)
        
        # Control frame rate for smooth animation
        clock.tick(60)  # 60 FPS for smooth animation