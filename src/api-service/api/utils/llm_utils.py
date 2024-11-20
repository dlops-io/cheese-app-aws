import os
import boto3
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import base64
import io
from PIL import Image
from pathlib import Path
import traceback
import json
import botocore


# Setup
# GCP_PROJECT = os.environ["GCP_PROJECT"]
# GCP_LOCATION = "us-central1"
# EMBEDDING_MODEL = "text-embedding-004"
# EMBEDDING_DIMENSION = 256
# GENERATIVE_MODEL = "gemini-1.5-flash-002"


# Update environment variables and setup
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1").strip()
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID").strip()
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY").strip()


# Setup
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)
MODEL_ID = "anthropic.claude-3-5-sonnet-20240620-v1:0"  # or your preferred Claude model

# Configuration settings for the content generation
generation_config = {
    "max_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}
# Initialize the GenerativeModel with specific system instructions
SYSTEM_INSTRUCTION = """
You are an AI assistant specialized in cheese knowledge.

When answering a query:
1. Demonstrate expertise in cheese, including aspects like:
  - Production methods and techniques
  - Flavor profiles and characteristics
  - Aging processes and requirements
  - Regional varieties and traditions
  - Pairing recommendations
  - Storage and handling best practices
2. Always maintain a professional and knowledgeable tone, befitting a cheese expert.

Your goal is to provide accurate, helpful information about cheese for each query.
"""
# generative_model = GenerativeModel(
# 	GENERATIVE_MODEL,
# 	system_instruction=[SYSTEM_INSTRUCTION]
# )

# Initialize chat sessions
chat_sessions: Dict[str, List[Dict]] = {}

def create_chat_session() -> List[Dict]:
    """Create a new chat session"""
    return []  # Start with empty list, we'll add system instruction in the first message


def generate_chat_response(chat_session: List[Dict], message: Dict) -> str:
    try:
        messages = chat_session.copy()
        
        # Prepare the message content
        content = []
        
        # Add text content if present
        if message.get("content"):
            content.append({
                "type": "text",
                "text": message["content"]
            })
            
        # Process image if present
        if message.get("image"):
            try:
                base64_string = message.get("image")
                if ',' in base64_string:
                    _, base64_data = base64_string.split(',', 1)
                else:
                    base64_data = base64_string
                
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": base64_data
                    }
                })
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Image processing failed: {str(e)}"
                )
        
        # Add the user message to the chat history
        messages.append({
            "role": "user",
            "content": content
        })
        
        try:
            # Prepare the request body exactly as shown in console
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": generation_config["max_tokens"],
                "messages": messages
            }
            
            # Call Bedrock
            response = bedrock.invoke_model(
                modelId=MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            assistant_message = response_body['content'][0]['text']
            
            # Add the assistant's response to the chat history
            messages.append({
                "role": "assistant",
                "content": [{"type": "text", "text": assistant_message}]
            })
            
            return assistant_message
            
        except botocore.exceptions.ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"AWS Error: {error_code} - {error_message}")
            print(f"Request body: {json.dumps(body, indent=2)}")
            raise HTTPException(
                status_code=500,
                detail=f"AWS Error: {error_code} - {error_message}"
            )
                
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )

def rebuild_chat_session(chat_history: List[Dict]) -> List[Dict]:
    """Rebuild a chat session with complete context"""
    new_session = create_chat_session()
    
    for message in chat_history:
        if message["role"] == "user":
            generate_chat_response(new_session, message)
    
    return new_session