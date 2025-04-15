# LLM Ambiguity Resolution Evaluator

This system evaluates how well an LLM agent resolves linguistic ambiguity when selecting functions to call. It processes a CSV file containing ambiguous prompts and their expected function calls, then uses an LLM to determine which function should be called for each prompt.

## Features

- Implements 10 dummy functions for testing
- Processes ambiguous prompts from a CSV file
- Uses GPT-4 to select appropriate functions
- Tracks and analyzes results
- Generates detailed evaluation reports
- Provides interesting examples of successes and failures

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root directory and add your OpenAI API key:

```bash
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

## CSV Format

The input CSV file should have the following columns:

- `prompt`: The ambiguous user request
- `correct interpretation`: The intended meaning
- `incorrect interpretation`: A possible incorrect interpretation
- `correct function that needs to be called`: The expected function name

## Usage

Run the evaluation with:

```bash
python main.py --csv path/to/your/prompts.csv
```

Optional arguments:

- `--output-dir`: Directory to save evaluation reports (default: "results")

## Output

The system will:

1. Process all prompts in the CSV file
2. Display a summary report in the console
3. Save a detailed JSON report in the output directory

The report includes:

- Total number of prompts processed
- Overall accuracy percentage
- Breakdown of correct/incorrect calls for each function type
- Examples of interesting successes and failures

## Example Report

```
=== Ambiguity Resolution Evaluation Report ===

Total Prompts Processed: 100
Overall Accuracy: 85.00%

Function Breakdown:
weatherCheck:
  Total Calls: 15
  Correct Calls: 13
  Accuracy: 86.67%

scheduleAppointment:
  Total Calls: 12
  Correct Calls: 10
  Accuracy: 83.33%

[...]

Interesting Examples:
[...]
```
