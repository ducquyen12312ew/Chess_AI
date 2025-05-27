import pygame
import chess
import math
from Square import Square

columns = 'abcdefgh'

def get_pos_from_coord(coord:str):
    for i in range(8):
        if columns[i] == coord[0]:
            res = (i, 8 - int(coord[1]))
            break
    return res

def get_coord_from_pos(x, y):
    return columns[x] + str(8-y)

class GUI_Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tile_width = width // 8
        self.tile_height = height // 8
        self.selected_piece = None
        self.turn = chess.WHITE
        self.config = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['','','','','','','',''],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.chess_board = chess.Board()
        self.squares = self.generate_squares()
        self.setup_board()
        
        # Animation variables
        self.animating_piece = None
        self.animating_piece_img = None
        self.animation_start_pos = None
        self.animation_target_pos = None
        self.animation_progress = 0.0
        self.animation_speed = 0.12  # Slightly slower for smoother animation
        self.is_animating = False

    def generate_squares(self):
        output = set()
        for y in range(8):
            for x in range(8):
                output.add(Square(x, y, self.tile_width, self.tile_height))
        return output

    def get_square_from_pos(self, pos):
        for square in self.squares:
            if (square.x, square.y) == (pos[0], pos[1]):
                return square

    def get_piece_from_pos(self, pos):
        return self.get_square_from_pos(pos).occupying_piece
    
    def setup_board(self):
        for y, row in enumerate(self.config):
            for x, piece in enumerate(row):
                if piece != '':
                    square = self.get_square_from_pos((x, y))
                    # Set occupying piece in square based on config
                    if piece[1] == 'R':
                        square.occupying_piece = Piece((x,y), chess.ROOK, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'N':
                        square.occupying_piece = Piece((x,y), chess.KNIGHT, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'B':
                        square.occupying_piece = Piece((x,y), chess.BISHOP, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'Q':
                        square.occupying_piece = Piece((x,y), chess.QUEEN, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'K':
                        square.occupying_piece = Piece((x,y), chess.KING, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
                    elif piece[1] == 'P':
                        square.occupying_piece = Piece((x,y), chess.PAWN, chess.WHITE if piece[0] == 'w' else chess.BLACK, self)
    
    def get_possible_moves(self):
        res = set()
        for square in self.squares:
            if square.occupying_piece is not None:
                for valid_move in square.occupying_piece.get_moves():
                    res.add(valid_move)
        return res
    
    def is_checkmate(self):
        return self.chess_board.is_checkmate()
    def is_draw(self):
        return self.chess_board.is_stalemate() or self.chess_board.is_seventyfive_moves() or self.chess_board.is_fivefold_repetition() or self.chess_board.is_insufficient_material()
    
    def is_end_game(self):
        res = ''
        if self.is_checkmate():
            side = 'White' if self.turn == chess.BLACK else 'Black'
            res = side + ' wins!'
        elif self.is_draw():
            res = 'Draw!'
        if res != '':
            return res
        return False
    
    def start_animation(self, piece, start_pos, target_pos):
        """Start animation for piece movement"""
        # Create a copy of the piece image to avoid reference issues
        self.animating_piece = piece
        self.animating_piece_img = piece.img.copy()  # Store a copy of the image
        self.animation_start_pos = start_pos
        self.animation_target_pos = target_pos
        self.animation_progress = 0.0
        self.is_animating = True
    
    def update_animation(self):
        """Update animation progress"""
        if self.is_animating:
            self.animation_progress += self.animation_speed
            if self.animation_progress >= 1.0:
                self.animation_progress = 1.0
                self.is_animating = False
                self.animating_piece = None
                self.animating_piece_img = None
    
    def get_animated_position(self):
        """Get current animated position using smooth easing"""
        if not self.is_animating or self.animating_piece is None:
            return None
        
        # Enhanced smooth easing function
        t = self.animation_progress
        # Cubic easing for more natural movement
        t = t * t * (3.0 - 2.0 * t)  # Smoothstep
        
        start_x = self.animation_start_pos[0] * self.tile_width + self.tile_width // 2
        start_y = self.animation_start_pos[1] * self.tile_height + self.tile_height // 2
        target_x = self.animation_target_pos[0] * self.tile_width + self.tile_width // 2
        target_y = self.animation_target_pos[1] * self.tile_height + self.tile_height // 2
        
        current_x = start_x + (target_x - start_x) * t
        current_y = start_y + (target_y - start_y) * t
        
        return (current_x, current_y)
    
    def handle_click(self, mx, my):
        if self.is_animating:
            return None
            
        x = mx // self.tile_width
        y = my // self.tile_height
        clicked_square = self.get_square_from_pos((x, y))
        try:
            move_made = self.selected_piece.move(clicked_square)
        except AttributeError:
            move_made = None

        if move_made is not None:
            return move_made

        elif self.selected_piece is None:
            # Select a piece
            if clicked_square.occupying_piece is not None:
                if clicked_square.occupying_piece.color == self.turn:
                    # 1. Currently not selecting any piece; 2. Clicking on a piece; 3. Clicking on self's side's piece
                    self.selected_piece = clicked_square.occupying_piece

        elif clicked_square.occupying_piece is not None:
            if clicked_square.occupying_piece.color == self.turn:
                # Change selected piece
                self.selected_piece = clicked_square.occupying_piece
    
    def draw_luxury_border(self, display):
        """Draw an enhanced luxury wooden border"""
        border_width = 30
        
        # Create border surface
        border_surface = pygame.Surface((self.width + 2*border_width, self.height + 2*border_width))
        
        # Gradient background for border
        for y in range(border_surface.get_height()):
            ratio = y / border_surface.get_height()
            r = int(139 + (101 - 139) * ratio)
            g = int(116 + (67 - 116) * ratio)
            b = int(78 + (33 - 78) * ratio)
            pygame.draw.line(border_surface, (r, g, b), (0, y), (border_surface.get_width(), y))
        
        # Multiple border layers for depth
        colors = [(101, 67, 33), (139, 116, 78), (160, 140, 100)]
        widths = [6, 3, 1]
        for color, width in zip(colors, widths):
            pygame.draw.rect(border_surface, color, 
                           (border_width - width*3, border_width - width*3, 
                            self.width + width*6, self.height + width*6), width)
        
        return border_surface
    
    def draw_coordinates(self, surface, font, border_width):
        """Draw elegant coordinate labels"""
        text_color = (101, 67, 33)
        
        # Files (a-h) - bottom
        for i, letter in enumerate('abcdefgh'):
            text = font.render(letter, True, text_color)
            x = border_width + i * self.tile_width + self.tile_width // 2 - text.get_width() // 2
            y = self.height + border_width + 5
            surface.blit(text, (x, y))
        
        # Ranks (1-8) - left side
        for i in range(8):
            number = str(8 - i)
            text = font.render(number, True, text_color)
            x = border_width - 20
            y = border_width + i * self.tile_height + self.tile_height // 2 - text.get_height() // 2
            surface.blit(text, (x, y))
    
    def draw(self, display):
        # Create enhanced border surface
        border_width = 30
        board_surface = self.draw_luxury_border(display)
        
        # Create the main board surface
        main_surface = pygame.Surface((self.width, self.height))
        
        cur_turn = self.turn
        
        # Clear all highlights first
        for square in self.squares:
            square.highlight = False
            if hasattr(square, 'is_move_indicator'):
                delattr(square, 'is_move_indicator')
        
        # Set highlights for selected piece and valid moves
        if self.selected_piece is not None:
            self.get_square_from_pos(self.selected_piece.pos).highlight = True
            for square in self.selected_piece.get_valid_moves():
                square.highlight = True
                square.is_move_indicator = True  # Mark as move indicator
        
        # Draw squares with enhanced effects
        for square in self.squares:
            # Check status for kings
            if square.occupying_piece is not None:
                if square.occupying_piece.piece_type == chess.KING and square.occupying_piece.color == cur_turn:
                    if self.is_checkmate():
                        square.checkmate = True
                    elif self.chess_board.is_check():
                        square.check = True
                    else:
                        square.check = False
                        square.checkmate = False
                else:
                    square.check = square.checkmate = False
            else:
                square.check = square.checkmate = False
            
            # Determine if piece should be drawn
            draw_piece = True
            if (self.is_animating and self.animating_piece and 
                square.occupying_piece == self.animating_piece):
                draw_piece = False
            
            square.draw(main_surface, draw_piece)
        
        # Draw animated piece with enhanced effects
        if self.is_animating and self.animating_piece and self.animating_piece_img:
            animated_pos = self.get_animated_position()
            if animated_pos:
                # Enhanced shadow for animated piece
                piece_rect = self.animating_piece_img.get_rect()
                piece_rect.center = animated_pos
                
                # Multiple shadow layers for depth
                shadow_offsets = [(4, 4), (3, 3), (2, 2)]
                shadow_alphas = [20, 30, 40]
                for offset, alpha in zip(shadow_offsets, shadow_alphas):
                    shadow_surface = pygame.Surface((piece_rect.width, piece_rect.height), pygame.SRCALPHA)
                    shadow_surface.fill((0, 0, 0, alpha))
                    main_surface.blit(shadow_surface, (piece_rect.topleft[0] + offset[0], piece_rect.topleft[1] + offset[1]))
                
                # Draw the animated piece
                main_surface.blit(self.animating_piece_img, piece_rect.topleft)
        
        # Update animation
        self.update_animation()
        
        # Blit main surface to board surface
        board_surface.blit(main_surface, (border_width, border_width))
        
        # Draw coordinates
        try:
            font = pygame.font.Font(None, 24)
            self.draw_coordinates(board_surface, font, border_width)
        except:
            pass  # Skip if font fails
        
        # Blit to main display
        display.blit(board_surface, (0, 0))


class Piece(chess.Piece):
    def __init__(self, pos, type:chess.PieceType, color:chess.Color, board:GUI_Board):
        super().__init__(type, color)
        self.pos = pos # position on 8x8 board with indices from 0 to 7
        self.coord = get_coord_from_pos(*self.pos) # coordinate by chess rule
        self.x = self.pos[0]
        self.y = self.pos[1]
        self.gui_board = board
        self.img = self.get_img()
    
    def get_img(self):
        img_path = 'data/imgs/'
        pieces = ['_pawn.png', '_knight.png', '_bishop.png', '_rook.png', '_queen.png', '_king.png']
        if self.color == chess.WHITE:
            img_path += 'w'
        else:
            img_path += 'b'
        img_path += pieces[self.piece_type - 1]
        res = pygame.image.load(img_path)
        res = pygame.transform.scale(res, (self.gui_board.tile_width - 35, self.gui_board.tile_height - 35))
        return res
    
    def get_moves(self):
        output = set()
        available_moves = {move.uci() for move in self.gui_board.chess_board.generate_legal_moves()}
        
        for move in available_moves:
            if move[0:2] == self.coord:
                output.add(move)
        return output
    
    def get_valid_moves(self):
        output = set()
        for move in self.get_moves():
            sq_pos = get_pos_from_coord(move[2:4])
            square = self.gui_board.get_square_from_pos(sq_pos)
            output.add(square)
        return output

    def move(self, square, force=False):
        for i in self.gui_board.squares:
            i.highlight = False
        
        mark_castling = False
        mark_en_passant = False
        if self.piece_type == chess.KING and abs(square.x - self.x) == 2 and self.gui_board.chess_board.has_castling_rights(self.gui_board.turn):
            mark_castling = True
            side = 'KING_SIDE' if square.x > self.x else 'QUEEN_SIDE'
        if self.piece_type == chess.PAWN and abs(self.x - square.x) == 1 and abs(self.y - square.y) == 1 and square.occupying_piece == None:
            mark_en_passant = True
        
        if square in self.get_valid_moves() or force:           
            prev_square = self.gui_board.get_square_from_pos(self.pos)
            move_cur = self.coord
            
            # Start animation if not forced move
            if not force:
                self.gui_board.start_animation(self, self.pos, square.pos)
            
            self.pos, self.x, self.y = square.pos, square.x, square.y
            self.coord = get_coord_from_pos(*self.pos)
            prev_square.occupying_piece = None
            square.occupying_piece = self
            self.gui_board.selected_piece = None
            move_new = self.coord
            
            if self.piece_type == chess.PAWN:
                if (self.color == chess.WHITE and move_new[1] == '8') or (self.color == chess.BLACK and move_new[1] == '1'):
                    move_new += 'q'
                    self.piece_type = chess.QUEEN
                    self.img = self.get_img()
            if not force:
                self.gui_board.chess_board.push_san(move_cur + move_new)
            
            if mark_en_passant:
                captured_pawn_at = self.gui_board.get_square_from_pos((square.x, prev_square.y))
                captured_pawn_at.occupying_piece = None
            
            if mark_castling:
                if self.gui_board.turn == chess.WHITE:
                    rook_cur_pos = (7, 7) if side == 'KING_SIDE' else (0, 7)
                    rook_new_pos = (5, 7) if side == 'KING_SIDE' else (3, 7)
                elif self.gui_board.turn == chess.BLACK:
                    rook_cur_pos = (7, 0) if side == 'KING_SIDE' else (0, 0)
                    rook_new_pos = (5, 0) if side == 'KING_SIDE' else (3, 0)
                rook = self.gui_board.get_piece_from_pos(rook_cur_pos)
                rook.move(self.gui_board.get_square_from_pos(rook_new_pos), force=True)
            if not force:
                self.gui_board.turn = chess.WHITE if self.gui_board.turn == chess.BLACK else chess.BLACK
            return move_cur + move_new
        
        else:
            self.gui_board.selected_piece = None
            return None