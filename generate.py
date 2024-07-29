import sys
import copy
from crossword import *


class CrosswordCreator:
    def __init__(self, crossword):
        """
        Create new CSP crossword generator.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy() for var in self.crossword.variables
        }


    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters


    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()


    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size, self.crossword.height * cell_size),
            "black",
        )
        try:
            font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        except IOError:
            font = ImageFont.load_default()  # Use default font if the specified font is not found
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border, i * cell_size + cell_border),
                    (
                        (j + 1) * cell_size - cell_border,
                        (i + 1) * cell_size - cell_border,
                    ),
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        bbox = draw.textbbox((0, 0), letters[i][j], font=font)
                        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                        draw.text(
                            (
                                rect[0][0] + ((interior_size - w) / 2),
                                rect[0][1] + ((interior_size - h) / 2) - 10,
                            ),
                            letters[i][j],
                            fill="black",
                            font=font,
                        )

        img.save(filename)


    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()

        return self.backtrack(dict())


    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        self_domains = copy.deepcopy(self.domains)

        # Eliminate words that have different lengths than the variables
        for variable in self_domains:
            for word in self_domains[variable]:
                if len(word) != variable.length:
                    self.domains[variable].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        x_overlap, y_overlap = self.crossword.overlaps[x, y]

        # Variable to keep track if a revision was made to the domain of x
        revised = False

        # Create a deepcopy of self.domains to avoid modifying the original domain while iterating over it
        self_domains = copy.deepcopy(self.domains)

        if x_overlap is not None:
            for x_word in self_domains[x]:
                words_match = False
                for y_word in self_domains[y]:
                    if x_word[x_overlap] == y_word[y_overlap]:
                        words_match = True
                        break
                if not words_match:
                    self.domains[x].remove(x_word)
                    revised = True

        return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            queue = []
            for variable in self.domains:
                for overlap_variable in self.crossword.neighbors(variable):
                    if self.crossword.overlaps[variable, overlap_variable] is not None:
                        queue.append((variable, overlap_variable))

        while len(queue) > 0:
            x, y = queue.pop(0)

            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        queue.append((neighbor, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        words = [*assignment.values()]
        if len(words) != len(set(words)):
            return False

        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False

        for variable in assignment:
            for neighbor in self.crossword.neighbors(variable):
                if neighbor in assignment:
                    x, y = self.crossword.overlaps[variable, neighbor]
                    if assignment[variable][x] != assignment[neighbor][y]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        words = {}
        neighbors = self.crossword.neighbors(var)

        for word in self.domains[var]:
            eliminated_words = 0
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                else:
                    x_overlap, y_overlap = self.crossword.overlaps[var, neighbor]
                    for neighbor_word in self.domains[neighbor]:
                        if word[x_overlap] != neighbor_word[y_overlap]:
                            eliminated_words += 1
            words[word] = eliminated_words

        sorted_dict = {k: v for k, v in sorted(words.items(), key=lambda item: item[1])}
        return [*sorted_dict]


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        choice_dict = {}

        for variable in self.domains:
            if variable not in assignment:
                choice_dict[variable] = self.domains[variable]

        sorted_list = [
            val for val, k in sorted(choice_dict.items(), key=lambda item: len(item[1]))
        ]

        return sorted_list[0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if len(assignment) == len(self.domains):
            return assignment

        variable = self.select_unassigned_variable(assignment)

        for value in self.domains[variable]:
            assignment_copy = assignment.copy()
            assignment_copy[variable] = value

            if self.consistent(assignment_copy):
                result = self.backtrack(assignment_copy)

                if result is not None:
                    return result

        return None



def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()



# Usage and Output Examples:
# ----------------------------

# (.conda) razvansavin@AEGIS:~/ProiecteVechi/CS50AI/crossword$ python generate.py data/structure0.txt data/words0.txt
# █SIX█
# █E██F
# █V██I
# █E██V
# █NINE

# (.conda) razvansavin@AEGIS:~/ProiecteVechi/CS50AI/crossword$ python generate.py data/structure1.txt data/words1.txt
# ██████████████
# ███████M████R█
# █INTELLIGENCE█
# █N█████N████S█
# █F██LOGIC███O█
# █E█████M████L█
# █R███SEARCH█V█
# ███████X████E█
# ██████████████

# (.conda) razvansavin@AEGIS:~/ProiecteVechi/CS50AI/crossword$ python generate.py data/structure2.txt data/words2.txt
# ██████B
# INTO██R
# D██FREE
# E██F██A
# A██E██T
# █BAR██H

# ----------------------
# Output as file:
