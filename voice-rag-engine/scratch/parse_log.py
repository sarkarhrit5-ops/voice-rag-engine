import os

def main():
    log_path = r"C:\Users\soumi\.gemini\antigravity-ide\brain\8c7991c8-7540-49ee-bbca-5b5df5a4477f\.system_generated\tasks\task-149.log"
    if not os.path.exists(log_path):
        print(f"Log not found at {log_path}")
        return
        
    with open(log_path, "rb") as f:
        data = f.read()
        
    # Decode ignoring errors
    text = data.decode("utf-8", errors="ignore")
    
    # Split by \n and \r
    lines = []
    current_line = []
    for char in text:
        if char == '\n':
            lines.append("".join(current_line))
            current_line = []
        elif char == '\r':
            lines.append("".join(current_line))
            current_line = []
        else:
            current_line.append(char)
    if current_line:
        lines.append("".join(current_line))
        
    # Filter empty lines
    lines = [l.strip() for l in lines if l.strip()]
    
    print("--- Last 30 lines of parsed log ---")
    for l in lines[-30:]:
        print(l)

if __name__ == "__main__":
    main()
