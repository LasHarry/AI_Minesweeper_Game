import itertools
import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        new_cells = set()
        for item in self.cells:
            if item != cell:
                new_cells.add(item)
            else:
                self.count -= 1
        self.cells = new_cells

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        new_cells = set()
        for item in self.cells:
            if item != cell:
                new_cells.add(item)
        self.cells = new_cells


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # Mark cell as safe and add to moves_made
        self.mark_safe(cell)
        self.moves_made.add(cell)

        # Create and add sentence to knowledge base
        neighbors, count = self.get_enclosed_cells(cell, count)
        sentence = Sentence(neighbors, count)
        self.knowledge.append(sentence)

        # Conclusion
        for s in self.knowledge:
            if s == sentence:
                continue
            elif s.cells.issuperset(sentence.cells):
                set_diff = s.cells - sentence.cells
                # Known safes
                if s.count == sentence.count:
                    for safe_found in set_diff:
                        self.mark_safe(safe_found)
                # Known mines
                elif len(set_diff) == s.count - sentence.count:
                    for mine_found in set_diff:
                        self.mark_mine(mine_found)
            elif sentence.cells.issuperset(s.cells):
                set_diff = sentence.cells - s.cells
                # Known safes
                if s.count == sentence.count:
                    for safe_found in set_diff:
                        self.mark_safe(safe_found)
                # Known mines
                elif len(set_diff) == sentence.count - s.count:
                    for mine_found in set_diff:
                        self.mark_mine(mine_found)
        self.remove_duplicates()
        self.remove_sures()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_cells = self.safes - self.moves_made
        if not safe_cells:
            return None
        move = safe_cells.pop()
        return move

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_moves = set()
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    all_moves.add((i, j))
        # No moves left
        if len(all_moves) == 0:
            return None
        # Return available moves
        move = random.choice(tuple(all_moves))
        return move

    def get_enclosed_cells(self, cell, count):
        """
        Returns all neighbour cells after a cell is selected
        """
        i, j = cell
        enclosed_cells = []

        for row in range(i - 1, i + 2):
            for col in range(j - 1, j + 2):
                if (0 <= row < self.height) \
                        and (0 <= col < self.width) \
                        and (row, col) != cell \
                        and (row, col) not in self.safes \
                        and (row, col) not in self.mines:
                    enclosed_cells.append((row, col))
                if (row, col) in self.mines:
                    count -= 1

        return enclosed_cells, count

    def remove_duplicates(self):
        """
        Removes any duplicate knowledge from the AIs knowledge base
        """
        unique_knowledge = []
        for s in self.knowledge:
            if s not in unique_knowledge:
                unique_knowledge.append(s)
        self.knowledge = unique_knowledge

    def remove_sures(self):
        """
        Removes all known mines and safes from the last update of the knowledge base
        """
        final_knowledge = []
        for s in self.knowledge:
            final_knowledge.append(s)
            if s.known_mines():
                for mine_found in s.known_mines():
                    self.mark_mine(mine_found)
                final_knowledge.pop(-1)
            elif s.known_safes():
                for safe_found in s.known_safes():
                    self.mark_safe(safe_found)
                final_knowledge.pop(-1)
        self.knowledge = final_knowledge
