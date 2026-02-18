import matplotlib.pyplot as plt
import random

GRID_SIZE = 50
MAX_WORDS = 20
FIG_SIZE = (15, 15)

def generate_crossword_layout(words):
    # Randomize then sort by length to vary the "centerpiece" word
    words = [w.upper() for w in words]
    random.shuffle(words)
    sorted_words = sorted(words, key=len, reverse=True)[:MAX_WORDS]

    grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    # Place first word in center
    first = sorted_words[0]
    row = GRID_SIZE // 2
    col = (GRID_SIZE - len(first)) // 2

    _place_word(grid, first, row, col, True)
    placed_words = [{'word': first, 'row': row, 'col': col, 'is_horiz': True}]
    # Place remaining words randomly
    for word in sorted_words[1:]:
        if placement := _find_random_position(grid, word, placed_words):
            r, c, h = placement
            _place_word(grid, word, r, c, h)
            placed_words.append({'word': word, 'row': r, 'col': c, 'is_horiz': h})

    return grid, placed_words

def _find_random_position(grid, word, placed_words):
    valid_spots = []
    
    for spot in _iter_possible_intersections(word, placed_words):
        r, c, h = spot
        if _is_valid_placement(grid, word, r, c, h):
            valid_spots.append(spot)
            
    return random.choice(valid_spots) if valid_spots else None

def _iter_possible_intersections(word, placed_words):
    for placed in placed_words:
        for i_p, char_p in enumerate(placed['word']):
            for i_w, char_w in enumerate(word):
                if char_p == char_w:
                    # Perpendicular placement logic
                    if placed['is_horiz']:
                        yield (placed['row'] - i_w, placed['col'] + i_p, False)
                    else:
                        yield (placed['row'] + i_p, placed['col'] - i_w, True)

def _is_valid_placement(grid, word, row, col, is_horiz):
    length = len(word)

    # 1. Bounds Check
    if row < 0 or col < 0: return False
    if is_horiz and col + length >= GRID_SIZE: return False
    if not is_horiz and row + length >= GRID_SIZE: return False

    # Endpoint Check (prevent merging)
    if not _are_endpoints_clear(grid, row, col, length, is_horiz):
        return False

    # Cell Conflict Check
    for i, char in enumerate(word):
        r = row + (0 if is_horiz else i)
        c = col + (i if is_horiz else 0)
        cell = grid[r][c]

        if cell not in ['', char]:
            return False # Mismatch

        if cell == '' and _has_illegal_neighbors(grid, r, c, is_horiz):
            return False # Side-by-side touching

    return True

def _are_endpoints_clear(grid, row, col, length, is_horiz):
    if is_horiz:
        pre = (col > 0 and grid[row][col-1] != '')
        post = (col + length < GRID_SIZE and grid[row][col+length] != '')
    else:
        pre = (row > 0 and grid[row-1][col] != '')
        post = (row + length < GRID_SIZE and grid[row+length][col] != '')
    return not (pre or post)

def _has_illegal_neighbors(grid, r, c, is_horiz):
    # If placing Horizontal, check Vertical neighbors (Top/Bottom)
    if is_horiz:
        if r > 0 and grid[r-1][c] != '': return True
        if r < GRID_SIZE - 1 and grid[r+1][c] != '': return True
    # If placing Vertical, check Horizontal neighbors (Left/Right)
    else:
        if c > 0 and grid[r][c-1] != '': return True
        if c < GRID_SIZE - 1 and grid[r][c+1] != '': return True
    return False

def _place_word(grid, word, row, col, is_horiz):
    for i, char in enumerate(word):
        r = row + (0 if is_horiz else i)
        c = col + (i if is_horiz else 0)
        grid[r][c] = char

def render_crossword(placed_words):
    if not placed_words: return

    # Calculate crop bounds
    rows = [p['row'] for p in placed_words]
    cols = [p['col'] for p in placed_words]
    max_r = max(p['row'] + (len(p['word']) if not p['is_horiz'] else 1) for p in placed_words)
    max_c = max(p['col'] + (len(p['word']) if p['is_horiz'] else 1) for p in placed_words)
    
    # Plot setup
    _, ax = plt.subplots(figsize=FIG_SIZE)
    ax.set_xlim(min(cols) - 1, max_c + 1)
    ax.set_ylim(max_r + 1, min(rows) - 1)
    ax.set_aspect('equal')
    plt.axis('off')

    # Numbering
    placed_words.sort(key=lambda x: (x['row'], x['col']))
    coords_to_num = {}
    counter = 1
    for w in placed_words:
        key = (w['row'], w['col'])
        if key not in coords_to_num:
            coords_to_num[key] = counter
            counter += 1

    # Drawing
    for w in placed_words:
        num = coords_to_num[(w['row'], w['col'])]
        ax.text(w['col'], w['row'], str(num), fontsize=8, ha='left', va='bottom', fontweight='bold', color='blue')

        for i, char in enumerate(w['word']):
            r = w['row'] + (i if not w['is_horiz'] else 0)
            c = w['col'] + (i if w['is_horiz'] else 0)
            
            ax.add_patch(plt.Rectangle((c, r), 1, 1, color='white', ec='black', lw=1.5))
            ax.text(c + 0.5, r + 0.5, char, fontsize=16, ha='center', va='center', color='black')

    plt.savefig('crossword_random.png', bbox_inches='tight', dpi=150)
    plt.show()

word_list = [
    "TRANSPARENCY", "ACCOUNTABILITY", "TRANSACTIONAL", "INTERACTIVE", "NONVERBAL",
    "ARISTOTLE", "LASSWELL", "INTEGRITY", "FEEDBACK", "DECODING", "ENCODING",
    "RECEIVER", "MESSAGE", "CHANNEL", "WRITTEN", "VISUAL", "VERBAL", "SENDER",
    "CLARITY", "NOISE", "ECONOMY", "LINEAR"
]

grid, metadata = generate_crossword_layout(word_list)
render_crossword(metadata)