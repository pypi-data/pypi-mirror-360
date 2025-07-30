"""
Core chat functionality for interacting with LLM providers
"""


def chat_with_ai(client, provider, model, messages, stream=False):
    """
    Handle chat interactions with different AI providers.

    Args:
        client: The initialized client instance for the provider
        provider (str): The name of the provider ('groq', 'openai', etc.)
        model (str): The model name to use
        messages (list): List of message dictionaries containing the conversation history
        stream (bool): Whether to stream the response (default: False)

    Returns:
        str or generator: The AI's response text or a stream of response chunks
    """
    try:
        if provider == "groq":
            response = client.chat.completions.create(
                messages=messages,
                model=model,
                stream=stream,  # Ensure we pass the stream flag
            )
            if stream:
                # For streaming, yield chunks as they arrive
                for chunk in response:
                    yield chunk.choices[0].delta.content or ""
            else:
                return response.choices[0].message.content

        elif provider == "openai":
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,  # Ensure we pass the stream flag
            )
            if stream:
                # If streaming, yield chunks
                for chunk in response:
                    yield chunk.choices[0].delta.content or ""
            else:
                return response.choices[0].message.content

        elif provider == "anthropic":
            if stream:
                with client.messages.stream(
                    max_tokens=4096, messages=messages, model=model
                ) as stream_response:
                    for delta in stream_response.text_stream:
                        yield delta
            else:
                response = client.messages.create(
                    model=model, messages=messages, max_tokens=4096, stream=False
                )
                return response.content[0].text

        elif provider == "cerebras":
            response = client.chat.completions.create(
                model=model, messages=messages, stream=stream
            )
            if stream:
                # For streaming, yield chunks as they arrive
                for chunk in response:
                    yield chunk.choices[0].delta.content or ""
            else:
                return response.choices[0].message.content

    except Exception as e:
        print(f"Error occurred while communicating with {provider}: {str(e)}")
        return None
