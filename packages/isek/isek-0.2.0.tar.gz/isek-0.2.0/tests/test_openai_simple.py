#!/usr/bin/env python3
"""Super simple test for OpenAIModel."""

import os
from isek.models.openai import OpenAIModel
from isek.models.base import SimpleMessage
import dotenv

dotenv.load_dotenv()


def test_openai_model():
    """Test the OpenAIModel implementation."""

    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set, skipping test")
        return

    try:
        model = OpenAIModel(model_id="gpt-3.5-turbo")
        messages = [SimpleMessage(role="user", content="Say 'Hello from OpenAI!'")]
        response = model.response(messages)
        print(f"Response: {response.content}")

    except Exception as e:
        print(f"Test failed: {e}")


if __name__ == "__main__":
    test_openai_model()
