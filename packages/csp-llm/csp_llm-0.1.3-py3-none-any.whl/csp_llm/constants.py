ANTHROPIC_PREFIX = "anthropic"
CHATGPT_PREFIX = "openai"
CRIL_PREFIX = "cril"
GOOGLE_PREFIX = "google"

BASE_CRIL_URL = "http://172.17.141.34/api"
BASE_GOOGLE_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


MODELS = [
    f"{CRIL_PREFIX}  [phi4:14b]",
    f"{CRIL_PREFIX}  [llama3.2:latest]",
    f"{CRIL_PREFIX} [qwen3:14b]",
    f"{CRIL_PREFIX}  [deepseek-r1:14b]",
    f"{ANTHROPIC_PREFIX} [claude-sonnet-4-20250514]",
    f"{ANTHROPIC_PREFIX} [claude-3-7-sonnet-20250219]",
    f"{ANTHROPIC_PREFIX} [claude-3-5-sonnet-20241022]",
    f"{CHATGPT_PREFIX}  [gpt-3.5]",
    f"{CHATGPT_PREFIX}  [gpt-4.1]",
    f"{GOOGLE_PREFIX}  [gemini-2.0-flash]",
]


# Example problems
EXAMPLE_PROBLEMS = {
    "Custom": "Enter your own problem description",
    "N-Queens": "Solve the 8-Queens problem: place 8 queens on a chessboard so no two queens attack each other",
    "Sudoku": "Create a 4x4 Sudoku solver with variables for each cell and constraints for rows, columns, and blocks",
    "Graph Coloring": "Color a graph with 4 nodes and edges [(0,1), (1,2), (2,3), (3,0)] using minimum colors",
    "Knapsack": "Knapsack problem with items having weights [2,3,4,5] and values [3,4,5,6], capacity 5",
}

QUICK_EXAMPLE_PROBLEMS = {
    "3x3 magic square": "Create a 3x3 magic square where all rows, columns, and diagonals sum to 15",
    "Simple graph coloring": "Color a triangle graph (3 nodes, all connected) with minimum colors",
    "Coin change problem": "Find ways to make change for 10 cents using coins [1,5,10]",
    "Assignment problem": "Assign 3 tasks to 3 workers with cost matrix [[1,2,3],[2,1,3],[3,2,1]]",
}
