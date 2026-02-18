import matplotlib.pyplot as plt
import random
import time
import sys

GRID_SIZE = 12
FIG_SIZE = (12, 12)

word_list = [
    "DATA", "CODE", "MODE", "ICON", "IDEA", 
    "BIAS", "TONE", "BODY", "FACE", "SIGN", 
    "ORAL", "MASS", "YES",  "ACT",  "AIM", 
    "CUE",  "LINK", "VIEW", "TRUE", "SELF"
]

def generate_strict_grid(words):
    start_time = time.time()
    attempts = 0

    # We define this OUTSIDE the loop so it remembers the best run forever.
    best_grid = None
    best_placed = [] 

    print("Tracking highest words in the 12x12 grid")

    while True:
        attempts += 1

        current_grid = [['' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        random.shuffle(words)

        # Place First Word Center
        first = words[0]
        r, c = 5, 4
        _place_word(current_grid, first, r, c, True)
        current_placed = [{'word': first, 'row': r, 'col': c, 'is_horiz': True}]
        # This tries to place the rest
        for word in words[1:]:
            valid_spots = []

            # Find every possible intersection with existing words
            for p in current_placed:
                for i_p, char_p in enumerate(p['word']):
                    for i_w, char_w in enumerate(word):
                        if char_p == char_w:
                            # Calculate start position for perpendicular placement
                            if p['is_horiz']:
                                r_new, c_new, h_new = p['row'] - i_w, p['col'] + i_p, False
                            else:
                                r_new, c_new, h_new = p['row'] + i_p, p['col'] - i_w, True

                            if _is_safe(current_grid, word, r_new, c_new, h_new):
                                valid_spots.append((r_new, c_new, h_new))

            # Pick a random valid spot if any exist
            if valid_spots:
                r, c, h = random.choice(valid_spots)
                _place_word(current_grid, word, r, c, h)
                current_placed.append({'word': word, 'row': r, 'col': c, 'is_horiz': h})

        # If this attempt placed more words than our previous record, SAVE IT.
        if len(current_placed) > len(best_placed):
            best_placed = list(current_placed) # Save copy of list
            best_grid = [row[:] for row in current_grid] # Save copy of grid

            # Print update immediately so you know it's working
            print(f"\n>> NEW RECORD! Found {len(best_placed)} words in {time.time() - start_time:.1f}s")

        if attempts % 2000 == 0:
            sys.stdout.write(f"\rAttempts: {attempts} | Current Best: {len(best_placed)}/20")
            sys.stdout.flush()

        if len(best_placed) == 20:
            print(f"\n\nSUCCESS! Found clean 20-word grid in {time.time() - start_time:.2f}s!")
            return best_grid, best_placed

def _is_safe(grid, word, r, c, h):
    length = len(word)

    # BOUNDARY CHECK
    if r < 0 or c < 0: return False
    if h and c + length > GRID_SIZE or not h and r + length > GRID_SIZE: return False
    # ENDPOINT CHECK
    # cell before the word must be empty
    if h:
        if c > 0 and grid[r][c-1] != '': return False
        if c + length < GRID_SIZE and grid[r][c+length] != '': return False
    else:
        if r > 0 and grid[r-1][c] != '': return False
        if r + length < GRID_SIZE and grid[r+length][c] != '': return False

    # BODY & PARALLEL CHECK
    for i, char in enumerate(word):
        rr, cc = (r, c + i) if h else (r + i, c)
        cell = grid[rr][cc]

        # Collision Check
        if cell not in ['', char]: return False

        # If the cell is empty, this avoids creating a parallel adjacency
        if cell == '':
            if h:
                if rr > 0 and grid[rr-1][cc] != '': 
                    return False 
                if rr < GRID_SIZE - 1 and grid[rr+1][cc] != '': 
                    return False
            else:
                if cc > 0 and grid[rr][cc-1] != '': 
                    return False
                if cc < GRID_SIZE - 1 and grid[rr][cc+1] != '': 
                    return False

    return True

def _place_word(grid, word, r, c, h):
    for i, char in enumerate(word):
        rr, cc = (r, c + i) if h else (r + i, c)
        grid[rr][cc] = char

def render(placed):
    if not placed: return
    _, ax = plt.subplots(figsize=FIG_SIZE)
    ax.set_xlim(0, GRID_SIZE); ax.set_ylim(GRID_SIZE, 0); ax.set_aspect('equal'); plt.axis('off')
    ax.add_patch(plt.Rectangle((0, 0), GRID_SIZE, GRID_SIZE, fill=None, ec='black', lw=4))
    
    placed.sort(key=lambda x: (x['row'], x['col']))
    coords_to_num = {}
    cnt = 1
    for w in placed:
        if (w['row'], w['col']) not in coords_to_num:
            coords_to_num[(w['row'], w['col'])] = cnt
            cnt += 1
            
    for w in placed:
        num = coords_to_num[(w['row'], w['col'])]
        ax.text(w['col']+0.1, w['row']+0.1, str(num), fontsize=10, fontweight='bold', color='blue')
        for i, char in enumerate(w['word']):
            r, c = (w['row'], w['col'] + i) if w['is_horiz'] else (w['row'] + i, w['col'])
            ax.add_patch(plt.Rectangle((c, r), 1, 1, color='white', ec='black', lw=1.5))
            ax.text(c+0.5, r+0.5, char, fontsize=14, fontweight='bold', ha='center', va='center')
    
    plt.savefig('crossword_20_best_record.png', bbox_inches='tight')
    plt.show()

    # Verify Output
    print("\nGENERATED LIST (20 Words)")
    for i, w in enumerate(placed):
        d = "ACROSS" if w['is_horiz'] else "DOWN"
        print(f"{i+1}. {w['word']} ({d})")

grid, metadata = generate_strict_grid(word_list)
render(metadata)