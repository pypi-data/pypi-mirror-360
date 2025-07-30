import re
from typing import Any

def transform_payload(payload_front: dict) -> list[dict]:
    """
    Transforms the input payload structure into a simplified format for interactions,
    ignoring messages where 'role' is 'system'.

    Parameters
    ----------
    - payload_front (dict): The original payload dictionary containing conversation interactions.

    Returns
    -------
    - list of dict: A transformed list of dictionaries, where each dictionary represents an
                    interaction with keys:
                    - "role": The role of the speaker ("user" or "assistant").
                    - "content": A list containing a dictionary with the text of the interaction,
                                under the key "text".
    
    Example
    -------
    >>> payload_front = {
    ...     "inputs": [
    ...         [
    ...             {"role": "user", "content": "oi", "id_interaction": "...", "media": []},
    ...             {"role": "assistant", "content": "text here", "media": []},
    ...             {"role": "user", "content": "a parede", "id_interaction": "...", "media": []}
    ...         ]
    ...     ],
    ...     "parameters": {...}
    ... }
    >>> transform_payload(payload_front)
    [
        {'role': 'user', 'content': [{'text': 'oi'}]},
        {'role': 'assistant', 'content': [{'text': 'text here'}]},
        {'role': 'user', 'content': [{'text': 'a parede'}]}
    ]
    """

    # Extract the list of interactions from the payload
    interactions = payload_front.get("inputs", [[]])[0]

    # Transform and filter interactions
    transformed_payload = []
    for interaction in interactions:
        if interaction["role"] == "system":
            continue  # Ignore system messages

        transformed_entry = {
            "role": interaction["role"],
            "content": [{"text": interaction["content"]}]
        }
        transformed_payload.append(transformed_entry)

    return transformed_payload

def structure_to_conversation(structure: list[dict]) -> tuple[str, str]:
    """Converts a structured conversation format into a flattened conversation history.
    
    Processes a list of message dictionaries containing roles and content, and transforms
    them into a formatted conversation string while tracking the last user input separately.

    Args
    ----
        structure (list): A list of message dictionaries where each contains:
            - role (str): Either 'user' or 'assistant'
            - content (list): List of content items where the first contains:
                - text (str): The message content
    
    Returns
    -------
        tuple: A tuple containing two elements:
            - str: The formatted conversation history with each message prefixed by **role**:
                   Example: "**user**: Hello\n**assistant**: Hi there"
            - str: The last user input in the structure (excluding the very last one if
                   it's a user message without a following assistant response)
    
    Note
    ----
        - The function skips adding the very last user message to the conversation history
          if it appears at the end of the structure (no following assistant response)
        - All messages are joined with newline characters
    
    Example
    -------
        >>> structure = [
        ...     {"role": "user", "content": [{"text": "Hello"}]},
        ...     {"role": "assistant", "content": [{"text": "Hi there"}]},
        ...     {"role": "user", "content": [{"text": "How are you?"}]}
        ... ]
        >>> structure_to_conversation(structure)
        ('**user**: Hello\\n**assistant**: Hi there', 'How are you?')
    """
    conversation_history = []
    user_last_input = ""

    for i, entry in enumerate(structure):
        role = entry["role"]
        text = entry["content"][0]["text"]
        
        if role == "user":
            user_last_input = text  # Store last user input
            if i == len(structure) - 1:
                break  # Skip adding last user input to conversation history
        
        conversation_history.append(f"**{role}**: {text}")
    
    return "\n".join(conversation_history), user_last_input

def remove_parentheses_around_url(text: str) -> str:
    """
    Remove surrounding parentheses and punctuation around URLs with paths in the provided text.

    This function identifies URLs that include paths or additional segments beyond the domain 
    (e.g., https://example.com/path) and removes any parentheses, brackets, braces, or punctuation 
    marks that might surround them.

    Args
    ----
        text (str): The input text containing URLs.

    Returns
    -------
        str: The text with cleaned URLs, without surrounding parentheses or punctuation.
    """
    pattern = r'[\(\[\{.,;]*(https?://[^\s\)\]\}\.,;]+(?:\.[^\s\)\]\}\.,;]+)*[^\s\)\]\}\.,;]*)[\)\]\}.,;]*'
    return re.sub(pattern, r'\1', text)

def handle_domain_only_urls(text: str) -> str:
    """
    Remove surrounding parentheses and punctuation around domain-only URLs in the provided text.

    This function targets URLs that consist only of a domain name (e.g., https://example.com) 
    and ensures that any surrounding parentheses, brackets, braces, or punctuation marks are 
    properly removed.

    Args
    ----
        text (str): The input text containing domain-only URLs.

    Returns
    -------
        str: The text with cleaned domain-only URLs, without surrounding parentheses or punctuation.
    """
    pattern = r'[\(\[\{.,;]*(https?://[^\s\)\]\}\.,;]+\.[^\s\)\]\}\.,;]+(?:\.[^\s\)\]\}\.,;]+)*)[\)\]\}.,;]*'
    return re.sub(pattern, r'\1', text)

def clean_text_with_urls(text: str) -> str:
    """
    Clean URLs in the input text by removing surrounding parentheses, brackets, braces, and punctuation.

    This function first applies `remove_parentheses_around_url()` to handle full URLs that include 
    paths, then applies `handle_domain_only_urls()` to clean domain-only URLs. It also adjusts the 
    formatting for certain HTML tags (`<li>`, `</li>`, `<p>`, `</p>`) to ensure proper spacing.

    Args
    ----
        text (str): The input text containing URLs and optional HTML content.

    Returns
    -------
        str: The cleaned text with properly formatted URLs and HTML tags.
    """
    text = remove_parentheses_around_url(text)
    text = handle_domain_only_urls(text)
    return text.replace('</li>', ' </li> ').replace('</p>', ' </p> ').replace('<li>', ' <li> ').replace('<p>', ' <p> ')
