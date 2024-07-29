# Crossword Puzzle Solver

## Overview
This project is a constraint satisfaction problem (CSP) solver for generating and solving crossword puzzles. It leverages AI techniques to ensure that the words fit correctly in the puzzle structure without any conflicts. The solver enforces node and arc consistency to find valid word placements efficiently.

## Features
- **Variable Representation**: Each variable represents a potential word placement in the crossword grid, characterized by its start position, direction (across or down), and length.
- **Crossword Structure**: The structure of the crossword is defined by a grid where each cell can either be a part of a word slot or a blocked cell.
- **Domain of Words**: The domain consists of a set of possible words that can fill the slots, which are filtered based on length and consistency constraints.
- **Arc Consistency**: The solver ensures that each variable is arc consistent, meaning any assignment of words to slots does not violate the constraints of neighboring slots.
- **Backtracking Search**: Uses backtracking to explore possible assignments and find a solution that fits all the constraints.

## Files
### `crossword.py`
Defines the structure and variables of the crossword puzzle.
- **Class `Variable`**: Represents a word slot with its start position, direction, length, and occupied cells.
- **Class `Crossword`**: Reads the crossword structure and words from files, identifies slots for words, and computes overlaps between slots.

### `generate.py`
Implements the CSP solver to generate the crossword puzzle solution.
- **Class `CrosswordCreator`**: Contains methods to enforce node and arc consistency, backtracking search, and utility functions for printing and saving the crossword.
  - **`solve`**: Main method to solve the crossword by enforcing consistency and using backtracking.
  - **`enforce_node_consistency`**: Ensures each slot can only take words of matching length.
  - **`revise`**: Ensures arc consistency between two variables.
  - **`ac3`**: Arc Consistency 3 algorithm to enforce arc consistency for the entire puzzle.
  - **`assignment_complete`**: Checks if the current assignment is complete.
  - **`consistent`**: Checks if the current assignment is consistent.
  - **`order_domain_values`**: Orders the domain values to prioritize those that eliminate the fewest options for neighbors.
  - **`select_unassigned_variable`**: Selects the next variable to assign based on the Minimum Remaining Values heuristic.
  - **`backtrack`**: Backtracking search to find a valid assignment.

## Usage
To run the crossword puzzle solver, use the following command:
```
python generate.py <structure_file> <words_file> [output_file]
```
- `<structure_file>`: Path to the file containing the crossword structure.
- `<words_file>`: Path to the file containing the list of words.
- `[output_file]`: Optional path to save the solved crossword as an image.

### Example Commands

- Command to solve the crossword puzzle and print the solution to the terminal:
  ```
  python generate.py data/structure0.txt data/words0.txt
  ```

- Command to solve the crossword puzzle and save the output as an image in the `output` folder:
  ```
  python generate.py data/structure0.txt data/words0.txt output/output0.png
  ```

  ```
  python generate.py data/structure1.txt data/words1.txt output/output1.png
  ```

  ```
  python generate.py data/structure2.txt data/words2.txt output/output2.png
  ```

## Example Solutions
Running the solver on different structures and word lists produces various valid crossword solutions, demonstrating the solver's flexibility and effectiveness.

- **Example 1**:
  ```
  █SIX█
  █E██F
  █V██I
  █E██V
  █NINE
  ```

- **Example 2**:
  ```
  ██████████████
  ███████M████R█
  █INTELLIGENCE█
  █N█████N████S█
  █F██LOGIC███O█
  █E█████M████L█
  █R███SEARCH█V█
  ███████X████E█
  ██████████████
  ```

- **Example 3**:
  ```
  ██████B
  INTO██R
  D██FREE
  E██F██A
  A██E██T
  █BAR██H
  ```

## Dependencies
- Python 3
- `PIL` (Python Imaging Library) for saving the crossword as an image.

## Installation
Install the required dependencies using pip:
```
pip install pillow
```

## Conclusion
This project demonstrates the application of AI techniques in solving constraint satisfaction problems like crossword puzzles. The solver effectively manages word placements using node and arc consistency, along with a backtracking search to find valid solutions.
