import csv
import json
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime
from functions import FUNCTION_MAP
from openai import OpenAI
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EvaluationResult:
    prompt: str
    selected_function: str
    expected_function: str
    is_correct: bool
    timestamp: datetime
    llm_response: Dict[str, Any]

class AmbiguityEvaluator:
    AMBIGUITY_TYPE_RANGES = [
        (2, 21, "Lexical Ambiguity"),
        (22, 41, "Syntactic Ambiguity"),
        (42, 61, "Scopal Ambiguity"),
        (62, 81, "Elliptical Ambiguity"),
        (82, 101, "Collective/Distributive Ambiguity"),
        (102, 121, "Implicative Ambiguity"),
        (122, 141, "Presuppositional Ambiguity"),
        (142, 161, "Idiomatic Ambiguity"),
        (162, 181, "Coreferential Ambiguity"),
        (182, 201, "Generic/Non-generic Ambiguity"),
        (202, 221, "Type/Token Ambiguity")
    ]

    def __init__(self, csv_path: str, openai_api_key: str):
        self.csv_path = csv_path
        self.results: List[EvaluationResult] = []
        self.function_stats = defaultdict(lambda: {"correct": 0, "total": 0})
        self.overall_stats = {"total": 0, "correct": 0}
        self.ambiguity_type_stats = {t[2]: {"correct": 0, "total": 0} for t in self.AMBIGUITY_TYPE_RANGES}
        self.client = OpenAI(api_key=openai_api_key)

    def get_ambiguity_type(self, row_index: int) -> str:
        for start, end, ambiguity_type in self.AMBIGUITY_TYPE_RANGES:
            if start <= row_index + 1 <= end:  # +1 because row_index is 0-based
                return ambiguity_type
        return "Unknown"

    def load_prompts(self) -> List[Dict[str, str]]:
        """Load prompts from CSV file."""
        prompts = []
        with open(self.csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                prompt_data = {
                    "prompt": row["prompt"],
                    "expected_function": row["function(s) to call"],
                    "ambiguity_type": self.get_ambiguity_type(i)
                }
                prompts.append(prompt_data)
        return prompts

    def get_llm_function_selection(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Get function selection from LLM."""
        system_prompt = """You are an AI assistant that needs to select the most appropriate function to call based on the user's request.
        Available functions are:
        - weatherCheck(location, date)
        - scheduleAppointment(date, time, purpose)
        - sendMessage(recipient, content)
        - searchWeb(query)
        - calculateMath(expression)
        - translateText(text, source_language, target_language)
        - playMedia(title, platform)
        - orderFood(restaurant, items, delivery_address)
        - findDirections(origin, destination, mode)
        - manageFinance(action, account, amount)

        Respond with a JSON object containing:
        {
            "selected_function": "function_name",
            "parameters": {param_name: param_value},
            "reasoning": "explanation of why this function was chosen"
        }
        """

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        try:
            result = json.loads(response.choices[0].message.content)
            return result["selected_function"], result
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None, {"error": str(e)}

    def evaluate_prompt(self, prompt_data: Dict[str, str]) -> EvaluationResult:
        """Evaluate a single prompt."""
        try:
            prompt = prompt_data["prompt"]
            expected_function = prompt_data["expected_function"]
            ambiguity_type = prompt_data.get("ambiguity_type", "Unknown")
            
            selected_function, llm_response = self.get_llm_function_selection(prompt)
            
            is_correct = selected_function == expected_function
            
            result = EvaluationResult(
                prompt=prompt,
                selected_function=selected_function,
                expected_function=expected_function,
                is_correct=is_correct,
                timestamp=datetime.now(),
                llm_response=llm_response
            )
            
            # Update statistics
            self.overall_stats["total"] += 1
            if is_correct:
                self.overall_stats["correct"] += 1
                self.function_stats[expected_function]["correct"] += 1
                self.ambiguity_type_stats[ambiguity_type]["correct"] += 1
            self.function_stats[expected_function]["total"] += 1
            self.ambiguity_type_stats[ambiguity_type]["total"] += 1
            
            return result
        except KeyError as e:
            logger.error(f"Error processing prompt: {e}")
            raise

    def run_evaluation(self):
        """Run the full evaluation on all prompts."""
        prompts = self.load_prompts()
        for prompt_data in prompts:
            try:
                result = self.evaluate_prompt(prompt_data)
                self.results.append(result)
                logger.info(f"Processed prompt: {result.prompt[:50]}...")
            except Exception as e:
                logger.error(f"Error processing prompt: {e}")

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive evaluation report."""
        accuracy = (self.overall_stats["correct"] / self.overall_stats["total"]) * 100 if self.overall_stats["total"] > 0 else 0
        
        function_breakdown = {
            func: {
                "total": stats["total"],
                "correct": stats["correct"],
                "accuracy": (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            }
            for func, stats in self.function_stats.items()
        }
        
        ambiguity_type_breakdown = {
            ambiguity_type: {
                "total": stats["total"],
                "correct": stats["correct"],
                "accuracy": (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            }
            for ambiguity_type, stats in self.ambiguity_type_stats.items()
        }
        
        # Find interesting examples
        interesting_examples = {
            "successes": [
                r for r in self.results 
                if r.is_correct and len(r.prompt) > 50  # Longer prompts are more interesting
            ][:3],
            "failures": [
                r for r in self.results 
                if not r.is_correct and len(r.prompt) > 50
            ][:3]
        }
        
        return {
            "total_prompts": self.overall_stats["total"],
            "overall_accuracy": accuracy,
            "function_breakdown": function_breakdown,
            "ambiguity_type_breakdown": ambiguity_type_breakdown,
            "interesting_examples": interesting_examples
        } 