from app.core.database import SessionLocal, Base, engine
from app.models.problem import DifficultyLevel, Problem, TestCase, TopicType
from app.models.user import User


PROBLEMS = [
    {
        "title": "Pair Target",
        "slug": "pair-target",
        "description": "Find two values that add up to the target and return their indices.",
        "difficulty": DifficultyLevel.EASY,
        "topic": TopicType.ARRAYS,
        "constraints": "1 <= n <= 10^5",
        "input_format": "The first line contains n and target. The second line contains n integers.",
        "output_format": "Print the two indices as space-separated integers.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "sample_cases": [
            {"input_data": "4 9\n2 7 11 15", "expected_output": "0 1", "explanation": "The pair 2 and 7 sums to 9.", "order_index": 1},
            {"input_data": "5 20\n1 3 5 7 9", "expected_output": "3 4", "explanation": "The pair 7 and 9 sums to 16; use a different example.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "3 6\n1 2 3", "expected_output": "1 2", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "5 10\n1 2 3 4 5", "expected_output": "3 4", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "2 100\n50 50", "expected_output": "0 1", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Balanced Symbols",
        "slug": "balanced-symbols",
        "description": "Validate whether a bracket sequence closes properly.",
        "difficulty": DifficultyLevel.EASY,
        "topic": TopicType.STACKS,
        "constraints": "1 <= n <= 1000",
        "input_format": "A string containing parentheses, brackets, and braces.",
        "output_format": "Return true if balanced, otherwise false.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "sample_cases": [
            {"input_data": "()[]{}", "expected_output": "true", "explanation": "All brackets close in order.", "order_index": 1},
            {"input_data": "([)]", "expected_output": "false", "explanation": "The order is invalid.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "{[()]}", "expected_output": "true", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "[(])", "expected_output": "false", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "", "expected_output": "true", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Binary Search Range",
        "slug": "binary-search-range",
        "description": "Locate the first and last position of a target in a sorted array.",
        "difficulty": DifficultyLevel.MEDIUM,
        "topic": TopicType.SEARCHING,
        "constraints": "1 <= n <= 10^5",
        "input_format": "The first line contains n and target. The second line contains sorted values.",
        "output_format": "Print the first and last index positions.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "sample_cases": [
            {"input_data": "8 4\n1 2 4 4 4 6 7 8", "expected_output": "2 4", "explanation": "The target appears in a range.", "order_index": 1},
            {"input_data": "5 9\n1 2 3 4 5", "expected_output": "-1 -1", "explanation": "The value is absent.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1 2\n2", "expected_output": "0 0", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "6 0\n0 0 0 0 0 0", "expected_output": "0 5", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "7 6\n1 2 3 4 5 7 8", "expected_output": "-1 -1", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Merge Sort Count",
        "slug": "merge-sort-count",
        "description": "Count how many inversions exist in an array using a divide-and-conquer approach.",
        "difficulty": DifficultyLevel.MEDIUM,
        "topic": TopicType.SORTING,
        "constraints": "1 <= n <= 10^5",
        "input_format": "The first line contains n. The second line contains n integers.",
        "output_format": "Print the inversion count.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "sample_cases": [
            {"input_data": "5\n2 4 1 3 5", "expected_output": "2", "explanation": "Two inversions exist.", "order_index": 1},
            {"input_data": "4\n1 2 3 4", "expected_output": "0", "explanation": "The array is already sorted.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "3\n3 2 1", "expected_output": "3", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "6\n6 5 4 3 2 1", "expected_output": "15", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "1\n7", "expected_output": "0", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Hash Lookup",
        "slug": "hash-lookup",
        "description": "Use a hash-based structure to check whether a target exists in a collection.",
        "difficulty": DifficultyLevel.EASY,
        "topic": TopicType.HASHING,
        "constraints": "1 <= n <= 10^5",
        "input_format": "The first line contains n and target. The second line contains n integers.",
        "output_format": "Print true if present, otherwise false.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "sample_cases": [
            {"input_data": "5 9\n1 2 3 4 9", "expected_output": "true", "explanation": "The target exists.", "order_index": 1},
            {"input_data": "4 8\n1 2 3 4", "expected_output": "false", "explanation": "The target is missing.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1 1\n1", "expected_output": "true", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "3 6\n1 2 3", "expected_output": "false", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "6 0\n0 0 0 0 0 0", "expected_output": "true", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "String Reverse",
        "slug": "string-reverse",
        "description": "Reverse a string while preserving word order.",
        "difficulty": DifficultyLevel.EASY,
        "topic": TopicType.STRINGS,
        "constraints": "1 <= n <= 10^4",
        "input_format": "A single string.",
        "output_format": "Print the reversed string.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "sample_cases": [
            {"input_data": "hello", "expected_output": "olleh", "explanation": "The letters are reversed.", "order_index": 1},
            {"input_data": "world", "expected_output": "dlrow", "explanation": "The string reverses fully.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "a", "expected_output": "a", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "racecar", "expected_output": "racecar", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "code", "expected_output": "edoc", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Tree Height",
        "slug": "tree-height",
        "description": "Compute the height of a binary tree from its structure.",
        "difficulty": DifficultyLevel.MEDIUM,
        "topic": TopicType.TREES,
        "constraints": "1 <= n <= 10^4",
        "input_format": "A tree represented as an array of node values.",
        "output_format": "Print the maximum depth.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 256,
        "sample_cases": [
            {"input_data": "7\n1 2 3 4 5 6 7", "expected_output": "3", "explanation": "The height is three levels.", "order_index": 1},
            {"input_data": "3\n8 9 10", "expected_output": "2", "explanation": "The tree is two levels high.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1\n1", "expected_output": "1", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "5\n1 2 3 4 5", "expected_output": "3", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "9\n1 2 3 4 5 6 7 8 9", "expected_output": "4", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Shortest Route",
        "slug": "shortest-route",
        "description": "Find the shortest path in a weighted graph using an exploration strategy.",
        "difficulty": DifficultyLevel.HARD,
        "topic": TopicType.GRAPHS,
        "constraints": "1 <= n <= 10^4",
        "input_format": "The graph is provided as edges with weights.",
        "output_format": "Print the shortest path length.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 512,
        "sample_cases": [
            {"input_data": "4 5\n1 2 3\n2 4 2\n1 3 1\n3 4 1\n2 3 5", "expected_output": "2", "explanation": "The shortest route is through 1-3-4.", "order_index": 1},
            {"input_data": "3 2\n1 2 4\n2 3 1", "expected_output": "5", "explanation": "The path length is 5.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1 0", "expected_output": "0", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "4 4\n1 2 1\n2 3 1\n3 4 1\n1 4 5", "expected_output": "3", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "5 7\n1 2 2\n2 3 3\n3 4 2\n4 5 4\n1 5 10\n1 3 6\n2 4 5", "expected_output": "7", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Recursive Fibers",
        "slug": "recursive-fibers",
        "description": "Generate the first n values in a recursive number sequence.",
        "difficulty": DifficultyLevel.MEDIUM,
        "topic": TopicType.RECURSION,
        "constraints": "1 <= n <= 30",
        "input_format": "An integer n.",
        "output_format": "Print the nth value.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "sample_cases": [
            {"input_data": "5", "expected_output": "5", "explanation": "The fifth sequence value is 5.", "order_index": 1},
            {"input_data": "8", "expected_output": "21", "explanation": "The eighth value is 21.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1", "expected_output": "1", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "2", "expected_output": "1", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "10", "expected_output": "55", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Queue Rotation",
        "slug": "queue-rotation",
        "description": "Rotate the contents of a queue by one step and preserve its order.",
        "difficulty": DifficultyLevel.EASY,
        "topic": TopicType.QUEUES,
        "constraints": "1 <= n <= 10^3",
        "input_format": "An integer n followed by n values.",
        "output_format": "Print the rotated queue.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "sample_cases": [
            {"input_data": "4\n1 2 3 4", "expected_output": "4 1 2 3", "explanation": "The queue rotates right by one.", "order_index": 1},
            {"input_data": "3\n7 8 9", "expected_output": "9 7 8", "explanation": "The queue rotates right by one.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1\n42", "expected_output": "42", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "2\n5 6", "expected_output": "6 5", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "5\n1 2 3 4 5", "expected_output": "5 1 2 3 4", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Linked List Scan",
        "slug": "linked-list-scan",
        "description": "Traverse a linked list and report the number of nodes visited.",
        "difficulty": DifficultyLevel.MEDIUM,
        "topic": TopicType.LINKED_LISTS,
        "constraints": "1 <= n <= 10^4",
        "input_format": "A list of node values.",
        "output_format": "Print the node count.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
        "sample_cases": [
            {"input_data": "5\n1 2 3 4 5", "expected_output": "5", "explanation": "The list contains five nodes.", "order_index": 1},
            {"input_data": "2\n10 20", "expected_output": "2", "explanation": "Two nodes are traversed.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1\n9", "expected_output": "1", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "3\n7 8 9", "expected_output": "3", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "4\n1 3 3 4", "expected_output": "4", "explanation": "Hidden case", "order_index": 3},
        ],
    },
    {
        "title": "Backtracking Grid",
        "slug": "backtracking-grid",
        "description": "Use a search strategy to explore a grid and determine whether a path exists.",
        "difficulty": DifficultyLevel.HARD,
        "topic": TopicType.BACKTRACKING,
        "constraints": "1 <= n <= 10^3",
        "input_format": "A grid of characters.",
        "output_format": "Print true when a path exists.",
        "starter_code": {"python": "def solve():\n    pass", "javascript": "function solve() {\n\n}", "java": "public class Main {\n    public static void main(String[] args) {\n    }\n}"},
        "time_limit_ms": 1000,
        "memory_limit_mb": 512,
        "sample_cases": [
            {"input_data": "2 2\nSG\nGE", "expected_output": "true", "explanation": "The path exists through the grid.", "order_index": 1},
            {"input_data": "2 2\nSS\nGE", "expected_output": "false", "explanation": "No valid path exists.", "order_index": 2},
        ],
        "hidden_cases": [
            {"input_data": "1 1\nS", "expected_output": "true", "explanation": "Hidden case", "order_index": 1},
            {"input_data": "3 3\nSSS\nSSE\nEEE", "expected_output": "false", "explanation": "Hidden case", "order_index": 2},
            {"input_data": "3 3\nSSE\nSSE\nEEE", "expected_output": "true", "explanation": "Hidden case", "order_index": 3},
        ],
    }),
]


def seed_problems():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        if session.query(Problem).count() > 0:
            return
        admin = session.query(User).filter(User.role == "ADMIN").first()
        if not admin:
            admin = User(full_name="System Admin", email="admin@codemind.local", password_hash="seed", role="ADMIN")
            session.add(admin)
            session.commit()
            session.refresh(admin)
        for payload in PROBLEMS:
            problem = Problem(
                title=payload["title"],
                slug=payload["slug"],
                description=payload["description"],
                difficulty=payload["difficulty"],
                topic=payload["topic"],
                constraints=payload["constraints"],
                input_format=payload["input_format"],
                output_format=payload["output_format"],
                starter_code=payload["starter_code"],
                time_limit_ms=payload["time_limit_ms"],
                memory_limit_mb=payload["memory_limit_mb"],
                created_by=admin.id,
            )
            session.add(problem)
            session.flush()
            for case in payload.get("sample_cases", []):
                session.add(
                    TestCase(
                        problem_id=problem.id,
                        input_data=case["input_data"],
                        expected_output=case["expected_output"],
                        explanation=case.get("explanation"),
                        is_sample=True,
                        order_index=case.get("order_index", 1),
                    )
                )
            for case in payload.get("hidden_cases", []):
                session.add(
                    TestCase(
                        problem_id=problem.id,
                        input_data=case["input_data"],
                        expected_output=case["expected_output"],
                        explanation=case.get("explanation"),
                        is_sample=False,
                        order_index=case.get("order_index", 1),
                    )
                )
        session.commit()


if __name__ == "__main__":
    seed_problems()
    print("Seeded development problems")
