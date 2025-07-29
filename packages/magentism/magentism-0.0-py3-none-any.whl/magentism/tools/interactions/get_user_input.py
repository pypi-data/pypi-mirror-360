def get_user_input(message: str|None=None) -> str|None:
    """
    Display a message to the user and wait for their text input response.
    
    This function is designed for LLM agents to interact with users by:
    1. Displaying a prompt or question to the user
    2. Waiting for the user to type their response
    3. Returning the user's input as a string
    
    Args:
        message (str): The message, question, or prompt to display to the user.
                      Should be clear and specific about what input is expected.
                      null is returned when user exited
                      Examples: "Please enter your name:", "What would you like to do next?",
                               "Enter the file path you want to process:"
    
    Returns:
        str: The user's text input response. May be empty if user just presses Enter.
             The returned string will not include the trailing newline character.
    
    Example:
        >>> name = get_user_input("What is your name? ")
        What is your name? John Doe
        >>> print(f"Hello, {name}!")
        Hello, John Doe!
        
        >>> choice = get_user_input("Would you like to continue? (y/n): ")
        Would you like to continue? (y/n): y
        >>> if choice.lower() == 'y':
        ...     print("Continuing...")
    
    Note:
        This function will block execution until the user provides input.
        The agent should use clear, specific prompts to get the desired information.
    """
    if message:
        print(f"\n🤖\n{message}")
    print("\n👤")
    answer = None
    while True:
        try:
            answer = input()
        except EOFError:
            return None
        except KeyboardInterrupt:
            print("\r👤")
            continue
        if answer.strip():
            print()
            return answer

if __name__ == "__main__":
    get_user_input("Hello!")
