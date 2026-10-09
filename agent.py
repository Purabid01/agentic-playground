import ollama
from ddgs import DDGS
from datetime import datetime
      
    

# 1. Custom tool function

def get_system_time() -> str:
    """Returns the current local date, day of the week, and time.
    Use this tool whenever you need to know today's date, day, or current time.
    """
    now = datetime.now()
    return now.strftime("%A, %B %d, %Y %H:%M:%S")   

# web search function tool
def web_search(query: str) -> str:
    """Searches the live web using DuckDuckGo and returns top results.
    
    Args:
        query: The search term or question to look up online.
    """
    
    # Guard against models passing nested dictionaries instead of strings
    if isinstance(query, dict):
        query = query.get("description") or query.get("query") or str(query)
        
    print(f"\n[Tool Execution] Searching DuckDuckGo for: '{query}'...")
    
    try:
        results = []
        with DDGS() as ddgs:
            hits = list(ddgs.text(str(query), max_results=3))
            
            for hit in hits:
                title = hit.get("title", "")
                snippet = hit.get("body", "")
                link = hit.get("href", "")
                results.append(f"Title: {title}\nSummary: {snippet}\nURL: {link}\n")
                
        if not results:
            return "No search results found."
            
        return "\n---\n".join(results)
        
    except Exception as e:
        return f"Error executing web search: {str(e)}"


# calculator function tool
def calculate(expression: str) -> str:
    """Evaluates a basic mathematical expression like '2 + 2' or '500 * 12'.
    
    Args:
        query: The mathematical expression string to evaluate.
    """
    # Defensive guard in case model sends a dict
    if isinstance(expression, dict):
        expression = expression.get("expression") or str(expression)
    
    
    print(f"\n [calculation tool executaion] evaluates the expression: ")
    
    try:
        #evaluates safely
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"
    
    
    
# memory tool
# save notes
def save_note(note_text: str) -> str:
    """Saves a note or reminder to persistent storage.
    
    Args:
        note_text: The content of the note to remember.
    """
    if isinstance(note_text, dict):
        note_text = note_text.get("note_text") or note_text.get("text") or str(note_text)

    print(f"\n[Tool: save_note] Appending note: '{note_text}'...")

    try:
        with open("note_text.txt", "a") as file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"[{timestamp}] {note_text}\n")
        return f"Note successfully saved: '{note_text}'"
    except Exception as e:
        return f"Error saving note: {str(e)}"
    
#read notes
def read_notes() -> str:
    """Reads all previously saved notes and reminders from persistent storage."""
    print("\n[Tool: read_notes] Inspecting saved memory...")
    try:
        with open("note_text.txt", "r") as file:
            content = file.read().strip()
            if not content:
                return "Your notes file is currently empty."
            return content
    except FileNotFoundError:
        return "No notes file found. No reminders have been saved yet."
    except Exception as e:
        return f"Error reading notes: {str(e)}"
    
    

# 2. Tool dispatcher mapping
TOOL_MAP = {
    "web_search": web_search,
    "calculate": calculate,
    "save_note": save_note,
    "read_notes": read_notes,
    "get_system_time": get_system_time
}

def execute_tool_call(tool_call):
    function_name = tool_call.function.name
    arguments = tool_call.function.arguments or {}
    
    if function_name in TOOL_MAP:
        # Calls web_search(query=...)
        return TOOL_MAP[function_name](**arguments)
    
    return f"Error: Tool '{function_name}' is not recognized."

# 3. Agent runtime loop
def react_agent(query):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an agentic AI assistant. "
                "You have access to two tools: "
                "1. 'get_system_time' to check the current date, day, or time. "
                "2. 'web_search' to look up real-time information or web pages. "
                "3. 'calculate' to evaluate the math expression. "
                "4. 'save_note' to save the notes in memory. "
                "5. 'read_notes' to read the notes from memory"
                "Always use 'get_system_time' when asked about the date or time."
                "Do not output tool JSON as text in your message. Always invoke tools directly using the tool interface."
                )
        },
        {
            "role": "user",
            "content": query
        }
    ]
    
# Use any model installed on your machine that supports tool calling
    # (e.g., 'llama3.2', 'llama3.1', or 'qwen2.5')
    brain = "llama3.2"
    
    print(f"[*] Starting query: {query}\n")
    
    # Available tools exposed to the LLM
    available_tools = [get_system_time, web_search, calculate, save_note, read_notes]
    
    #Agentic loop this can be x iterations
    while True:
        response = ollama.chat(
            model = brain,
            messages = messages,
            tools=available_tools
        )

        message = response.message
        messages.append(message)
        
        # Stop condition: check if the model did NOT request any tool calls
        if not message.tool_calls:
            print("\nAgent:", message.content)
            break
       
       # Action phase: execute each tool call requested by the model 
        for tool_call in message.tool_calls:
            print(f"[*] AI called '{tool_call.function.name}' with args: {tool_call.function.arguments}")
            
            result = execute_tool_call(tool_call)
            
            # Feed the real-world tool output back into short-term memory
            messages.append({
                "role": "tool",
                "content":result,
                "name": tool_call.function.name
            })
        

if  __name__ == "__main__":
    # react_agent("""What is today's date""")
    # react_agent("""What is 4523 multiplied by 879, and what day of the week is it?""")
    # react_agent("""Find out what day of the week it is today, and save a note saying 'Review Lateral SDE openings on Greenhouse'.""")
    react_agent("What reminders or notes do I have saved regarding lateral SDE openings?")