# sara/core.py
import ollama

def generate_code(prompt):
    try:
        response = ollama.chat(
            model='starcoder',
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
    except Exception as e:
        return f"# Error: {str(e)}"