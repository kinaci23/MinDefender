import json
import random

class QuestionManager:
    def __init__(self, filename="questions.json"):
        self.filename = filename
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def generate_math_question(self, difficulty):
        """
        Generates dynamic math questions based on strict difficulty levels.
        """
        if difficulty == "kolay":
            # Simple Addition/Subtraction (0-20), No negatives
            op = random.choice(["+", "-"])
            a = random.randint(0, 20)
            b = random.randint(0, 20)
            if op == "-":
                if a < b: a, b = b, a # Ensure positive result
            
            question = f"{a} {op} {b}"
            answer = str(eval(question))
            return question, answer

        elif difficulty == "orta":
            # Multiplication (1-10 tables) or Simple Division
            if random.random() < 0.6: # 60% Multiplication
                a = random.randint(1, 10)
                b = random.randint(1, 10)
                question = f"{a} * {b}"
                answer = str(a * b)
            else: # Division (Ensure integer result)
                b = random.randint(2, 9)
                ans = random.randint(2, 9)
                a = b * ans
                question = f"{a} / {b}"
                answer = str(ans)
            return question, answer

        elif difficulty == "zor":
            # Complex 3-op equations or Modulo
            op_type = random.choice(["mixed", "mod"])
            
            if op_type == "mod":
                a = random.randint(10, 50)
                b = random.randint(3, 10)
                question = f"{a} % {b}"
                answer = str(a % b)
            else:
                # e.g., 5 * 3 + 2
                ops = ["+", "-", "*"]
                op1 = random.choice(ops)
                op2 = random.choice(ops)
                a = random.randint(1, 10)
                b = random.randint(1, 10)
                c = random.randint(1, 10)
                
                # Simplify generation to avoid complexity with eval order or huge numbers
                # Let's stick to (a op1 b) op2 c format implicitly for readability?
                # Actually standard python eval handles order of operations (PEMDAS).
                question = f"{a} {op1} {b} {op2} {c}"
                # Limit answer size and ensure int
                try:
                    res = eval(question)
                    answer = str(int(res))
                except:
                    return "5 + 5", "10" # Safe fallback
                    
            return question, answer
        
        return "1 + 1", "2"

    def get_question(self, category, difficulty="kolay"):
        """
        Retrieves a question. Falls back to easier difficulties if data is missing.
        """
        # 1. Handle Math Dynamically
        if category == "matematik":
            return self.generate_math_question(difficulty)
        
        # 2. Handle JSON Categories
        if category not in self.data:
            return None

        # Fallback Logic: Zor -> Orta -> Kolay
        target_diffs = [difficulty]
        if difficulty == "zor":
            target_diffs = ["zor", "orta", "kolay"]
        elif difficulty == "orta":
            target_diffs = ["orta", "kolay"]
        
        selected_pool = None
        for diff in target_diffs:
            if diff in self.data[category] and self.data[category][diff]:
                selected_pool = self.data[category][diff]
                break
        
        if selected_pool:
            question = random.choice(list(selected_pool.keys()))
            answer = selected_pool[question]
            return question, answer
            
        return None
