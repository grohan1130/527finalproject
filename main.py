import os
import json
from evaluator import AmbiguityEvaluator
import argparse
from datetime import datetime
from dotenv import load_dotenv

def display_report(report: dict):
    """Display the evaluation report in a readable format."""
    print("\n=== Ambiguity Resolution Evaluation Report ===")
    print(f"\nTotal Prompts Processed: {report['total_prompts']}")
    print(f"Overall Accuracy: {report['overall_accuracy']:.2f}%")
    
    print("\nFunction Breakdown:")
    for func, stats in report['function_breakdown'].items():
        print(f"\n{func}:")
        print(f"  Total Calls: {stats['total']}")
        print(f"  Correct Calls: {stats['correct']}")
        print(f"  Accuracy: {stats['accuracy']:.2f}%")
    
    print("\nInteresting Examples:")
    
    print("\nSuccessful Resolutions:")
    for example in report['interesting_examples']['successes']:
        print(f"\nPrompt: {example.prompt}")
        print(f"Selected Function: {example.selected_function}")
        print(f"Expected Function: {example.expected_function}")
        print(f"LLM Reasoning: {example.llm_response.get('reasoning', 'N/A')}")
    
    print("\nFailed Resolutions:")
    for example in report['interesting_examples']['failures']:
        print(f"\nPrompt: {example.prompt}")
        print(f"Selected Function: {example.selected_function}")
        print(f"Expected Function: {example.expected_function}")
        print(f"LLM Reasoning: {example.llm_response.get('reasoning', 'N/A')}")

def save_report(report: dict, output_dir: str = "results"):
    """Save the evaluation report to a file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(output_dir, f"evaluation_report_{timestamp}.json")
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nReport saved to: {filename}")

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
    
    parser = argparse.ArgumentParser(description="Evaluate LLM's ability to resolve linguistic ambiguity in function selection")
    parser.add_argument("--csv", required=True, help="Path to the CSV file containing ambiguous prompts")
    parser.add_argument("--output-dir", default="results", help="Directory to save evaluation reports")
    
    args = parser.parse_args()
    
    evaluator = AmbiguityEvaluator(args.csv, api_key)
    print("Starting evaluation...")
    evaluator.run_evaluation()
    
    report = evaluator.generate_report()
    display_report(report)
    save_report(report, args.output_dir)

if __name__ == "__main__":
    main() 