from typing import Any

def llm_complete(bedrock_client: Any, modelId: str, inferenceConfig: dict[str, Any], prompt: str, messages: list) -> str:
    """Completes a conversation using AWS Bedrock's LLM service.
    
    Processes and sends conversation data to AWS Bedrock's LLM, handling various input formats
    and returning the model's text response.

    Args:
        bedrock_client: AWS Bedrock runtime client
        modelId (str): Identifier of the Bedrock model to use
        inferenceConfig (dict): Configuration parameters for model inference
        prompt (str): System prompt/instruction for the LLM
        messages: Conversation history, can be:
                 - A single user message string
                 - List of message dictionaries in AWS format
                 - List of mixed strings/dictionaries

    Returns:
        str: The generated text response from the LLM

    Notes:
        - Automatically formats different message input types to AWS-compatible format
        - Expects Bedrock client to be properly authenticated
        - Handles both string and structured message content
    """
    system_prompt = {
        'text': prompt,
    }
    
    # Ensure "messages" is a list of dictionaries (AWS expected format)
    if isinstance(messages, str):
        messages = [{'role': 'user', 'content': [{'text': messages}]}]  
    
    for message in messages:
        if isinstance(message.get('content'), str):
            message['content'] = [{'text': message['content']}]
        elif isinstance(message.get('content'), list):
            # If content is already a list, ensure each item is properly formatted
            message['content'] = [{'text': item} if isinstance(item, str) else item for item in message['content']]
    
    response = bedrock_client.converse(
        modelId=modelId, 
        messages=messages, 
        system=[system_prompt], 
        inferenceConfig=inferenceConfig
    )

    return response['output']['message']['content'][0]['text']

def generate_embeddings(embed_model: Any, text: str) -> list[float]:
    """Generates text embeddings using the specified embedding model.
    
    Args:
        embed_model: An embedding model instance that implements get_text_embedding()
        text: Input text string to generate embeddings for

    Returns:
        list[float]: The generated embedding vector as a list of floats

    Raises:
        Exception: If embedding generation fails, prints the error and re-raises
        
    Example:
        >>> embeddings = generate_embeddings(model, "sample text")
        >>> len(embeddings)
        768  # Dimension of embedding vector
    """
    try:
        return embed_model.get_text_embedding(text)
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        raise