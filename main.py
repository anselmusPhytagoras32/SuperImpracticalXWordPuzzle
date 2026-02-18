import itertools
import matplotlib.pyplot as plt
import time
import random

GRID_SIZE = 12
FIG_SIZE = (12, 12)
TIMEOUT = 30 

word_list = [
    "MEDIA", "NOISE", "TOUCH", "SPACE", "SOUND", 
    "DATA",  "CODE",  "MODE",  "BODY",  "FACE", 
    "ORAL",  "WORD",  "MASS",  "DYAD",  "SELF", 
    "ACT",   "CUE",   "AIM",   "EYE",   "EAR"
]

class CrosswordSolver:
    def __init__(self, words, size):
        self.size = size
        self.original_words = words
        self.grid = [['' for _ in range(size)] for _ in range(size)]
        self.placed_info = []

    def solve_with_retries(self):
        start_time = time.time()
        attempts = 0
        
        print(f"Attempting to fit {len(self.original_words)} words into {self.size}x{self.size} grid...")

        while time.time() - start_time < TIMEOUT:
            attempts += 1
            
            # Reset
            self.grid = [['' for _ in range(self.size)] for _ in range(self.size)]
            self.placed_info = []
            
            # Shuffle to change the starting conditions
            current_words = list(self.original_words)
            random.shuffle(current_words)
            current_words.sort(key=len, reverse=True)
            
            self.words_to_place = current_words

            if self._backtrack(0):
                print(f"\nSUCCESS! Solved on attempt {attempts} in {time.time() - start_time:.2f}s")
                return self.grid, self.placed_info
            
            if attempts % 100 == 0:
                print(f"Searching... ({attempts} attempts)")

        print("Timeout reached. Returning best partial result (if any).")
        return None, None

    def _backtrack(self, index):
        if index == len(self.words_to_place):
            return True

        word = self.words_to_place[index]

        # Optimization: Force first word to a random spot near the center
        if index == 0:
            return self._extracted_from__backtrack_9(word, index)
        candidates = self._find_candidates(word)
        random.shuffle(candidates)

        for r, c, h in candidates:
            if self._can_place_strict(word, r, c, h):
                self._place(word, r, c, h)
                self.placed_info.append({'word': word, 'row': r, 'col': c, 'is_horiz': h})

                if self._backtrack(index + 1):
                    return True

                self._remove(word, r, c, h)
                self.placed_info.pop()

        return False

    def _extracted_from__backtrack_9(self, word, index):
        r = random.randint(4, 7)

        # Calculate valid column range
        c_min = 3
        c_max = 8 - len(word)
        c_max = max(c_max, c_min) 

        c = random.randint(c_min, c_max) 

        self._place(word, r, c, True)
        self.placed_info.append({'word': word, 'row': r, 'col': c, 'is_horiz': True})

        if self._backtrack(index + 1): return True

        self._remove(word, r, c, True)
        self.placed_info.pop()
        return False

    def _find_candidates(self, word):
        candidates = []
        for r, c in itertools.product(range(self.size), range(self.size)):
            cell = self.grid[r][c]
            if cell != '':
                for i, char in enumerate(word):
                    if char == cell:
                        candidates.extend(((r, c - i, True), (r - i, c, False)))
        return candidates

    def _can_place_strict(self, word, r, c, h):
        length = len(word)
        if r < 0 or c < 0: return False
        if h and c + length > self.size or not h and r + length > self.size: return False
        if h:
            if c > 0 and self.grid[r][c-1] != '': return False
            if c + length < self.size and self.grid[r][c+length] != '': return False
        else:
            if r > 0 and self.grid[r-1][c] != '': return False
            if r + length < self.size and self.grid[r+length][c] != '': return False

        for i, char in enumerate(word):
            rr, cc = (r, c + i) if h else (r + i, c)
            cell = self.grid[rr][cc]
            if cell not in ['', char]: return False
            if cell == '':
                if h:
                    if rr > 0 and self.grid[rr-1][cc] != '': return False
                    if rr < self.size - 1 and self.grid[rr+1][cc] != '': return False
                else:
                    if cc > 0 and self.grid[rr][cc-1] != '': return False
                    if cc < self.size - 1 and self.grid[rr][cc+1] != '': return False
        return True

    def _place(self, word, r, c, h):
        for i, char in enumerate(word):
            rr, cc = (r, c + i) if h else (r + i, c)
            self.grid[rr][cc] = char

    def _remove(self, word, r, c, h):
        for i, char in enumerate(word):
            rr, cc = (r, c + i) if h else (r + i, c)
            needed = False
            for p in self.placed_info:
                if p['word'] == word and p['row'] == r and p['col'] == c and p['is_horiz'] == h: continue
                pr, pc, ph = p['row'], p['col'], p['is_horiz']
                plen = len(p['word'])
                if ph:
                    if rr == pr and pc <= cc < pc + plen: needed = True
                elif cc == pc and pr <= rr < pr + plen: needed = True
            if not needed:
                self.grid[rr][cc] = ''

def render_grid(placed):
    if not placed: return
    _, ax = plt.subplots(figsize=FIG_SIZE)
    # Set limits with 0 at the top to match matrix coordinates
    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(GRID_SIZE, 0) 
    ax.set_aspect('equal')
    plt.axis('off')
    
    # Draw outer border
    #ax.add_patch(plt.Rectangle((0, 0), GRID_SIZE, GRID_SIZE, fill=None, ec='black', lw=4))
    
    placed.sort(key=lambda x: (x['row'], x['col']))
    
    # Map coordinates to numbers
    coord_to_nums = {}
    for i, w in enumerate(placed):
        key = (w['row'], w['col'])
        if key not in coord_to_nums:
            coord_to_nums[key] = []
        coord_to_nums[key].append(str(i + 1))
    
    drawn_labels = set()
    
    for i, w in enumerate(placed):
        key = (w['row'], w['col'])
        
        # Draw Number
        if key not in drawn_labels:
            label = "/".join(coord_to_nums[key]) 
            ax.text(w['col'] + 0.05, w['row'] + 0.05, label, 
                    fontsize=7, fontweight='bold', color='blue',
                    ha='left', va='top') 
            drawn_labels.add(key)
        
        # Draw Box and Letter
        for j, char in enumerate(w['word']):
            r, c = (w['row'], w['col'] + j) if w['is_horiz'] else (w['row'] + j, w['col'])
            ax.add_patch(plt.Rectangle((c, r), 1, 1, color='white', ec='black', lw=1.5))
            ax.text(c+0.5, r+0.5, char, fontsize=14, fontweight='bold', ha='center', va='center')
    
    plt.savefig('crossword_20_organized.png', bbox_inches='tight')
    plt.show()

    print(f"\n--- FINAL CHECK: {len(placed)} WORDS ---")
    for i, w in enumerate(placed):
        d = "ACROSS" if w['is_horiz'] else "DOWN"
        print(f"{i+1}. {w['word']} ({d})")

solver = CrosswordSolver(word_list, GRID_SIZE)
grid, metadata = solver.solve_with_retries()
if metadata:
    render_grid(metadata)
else:
    print("Failed to fit all 20 words. Try running it one more time.")