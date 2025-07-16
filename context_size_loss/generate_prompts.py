

import lorem
import os

# Define the core instruction for the LLM
instruction = "Analyze the following text which contains a code file and an exception stack trace. Your task is to identify the full path to the file where the exception originated from the stack trace. The content of the file is also provided. Return only the file path."

# The code file where the exception occurs
code_file_content = """
# my_app/utils.py
import os

def calculate_sum(a, b):
    '''This function calculates the sum of two numbers.'''
    return a + b

def process_data(data):
    '''Processes a dictionary of data.'''
    if not isinstance(data, dict):
        raise TypeError("Input data must be a dictionary.")
    
    result = 0
    for key, value in data.items():
        if isinstance(value, (int, float)):
            result += value
        else:
            # This is where the error will happen
            result += int(value) 
    return result

def main():
    data = {"a": 1, "b": 2, "c": "not_a_number"}
    total = process_data(data)
    print(f"Total: {total}")

if __name__ == "__main__":
    main()
"""

# The stack trace pointing to the code file
stack_trace = """
Traceback (most recent call last):
  File "/home/user/project/main.py", line 21, in <module>
    main()
  File "/home/user/project/main.py", line 18, in main
    total = process_data(data)
  File "/home/user/project/my_app/utils.py", line 17, in process_data
    result += int(value)
ValueError: invalid literal for int() with base 10: 'not_a_number'
"""

# Define the target token counts
token_counts = {
    "small": 1000,
    "medium": 200000,
    "large": 900000
}

# Approximate characters per token
chars_per_token = 4

def generate_prompt_file(size, count):
    filename = f"{size}.txt"
    target_chars = count * chars_per_token
    
    instruction_and_trace = f"\n--- Instruction ---\n{instruction}\n\n--- Stack Trace ---\n{stack_trace}"
    code_section = f"--- Code File ---\n{code_file_content}"

    if size == "small":
        # For small, needle is at the beginning.
        content_base = instruction_and_trace + "\n\n" + code_section
        
        distractor_text = ""
        if len(content_base) < target_chars:
            distractor_chars = target_chars - len(content_base)
            while len(distractor_text) < distractor_chars:
                distractor_text += "\n" + lorem.paragraph()
            distractor_text = distractor_text[:distractor_chars]
        
        content = content_base + "\n\n--- Distractor Text ---\n" + distractor_text
    
    else: # medium and large
        # For medium and large, needle is at the end.
        distractor_chars = target_chars - len(code_section) - len(instruction_and_trace)
        
        distractor_text = ""
        if distractor_chars > 0:
            while len(distractor_text) < distractor_chars:
                distractor_text += "\n" + lorem.paragraph()
            distractor_text = distractor_text[:distractor_chars]

        content = code_section + "\n\n--- Distractor Text ---\n" + distractor_text + "\n\n" + instruction_and_trace

    final_content = content[:target_chars]

    with open(filename, "w") as f:
        f.write(final_content)
    print(f"Generated {filename} with approximately {count} tokens.")

if __name__ == "__main__":
    for size, count in token_counts.items():
        generate_prompt_file(size, count)

