def payload_to_conversation(payload: dict) -> tuple[str, str]:
    """Extracts conversation history and user input from a chat payload.

    Processes a chat payload dictionary to separate:
    - The conversation history (all messages except last user message)
    - The current user input (last message if from user)

    Args:
        payload: Dictionary containing chat messages with keys:
                - 'messages': List of message dictionaries with:
                  * 'role': Sender role ('user' or other)
                  * 'content': Message text

    Returns:
        tuple: Contains two strings:
              - conversation_history: Formatted conversation transcript
              - user_input: Current user message (empty string if none)

    Example:
        >>> payload = {
                'messages': [
                    {'role': 'user', 'content': 'Hello'},
                    {'role': 'assistant', 'content': 'Hi there!'},
                    {'role': 'user', 'content': 'How are you?'}
                ]
            }
        >>> history, current_input = payload_to_conversation(payload)
        >>> print(history)
        **user**: Hello
        **assistant**: Hi there!
        >>> print(current_input)
        How are you?
    """
    messages = payload['messages']
    conversation_history = []
    user_input = ""
    
    # Process all messages except last one (if it's from user)
    for message in messages[:-1]:
        conversation_history.append(f"**{message['role']}**: {message['content']}")

    # Extract last user input (if last message is from user)
    if messages and messages[-1]['role'] == 'user':
        user_input = f"{messages[-1]['content']}"
    
    # Join conversation history with line breaks
    conversation_history_str = "\n".join(conversation_history)
    
    return conversation_history_str, user_input