from .core import generate_code

print("👋 Hi, I'm Sara — your AI code assistant!")
try:
    user_input = input("🧠 What can I generate for you today?\n>>> ")
    code = generate_code(user_input)
    print("\n💡 Generated Code:\n")
    print(code)
except Exception as e:
    print(f"⚠ Error: {e}")