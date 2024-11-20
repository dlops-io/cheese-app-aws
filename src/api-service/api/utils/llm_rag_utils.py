import os
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
import base64
import io
from PIL import Image
from pathlib import Path
import traceback
import chromadb
# from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
# from vertexai.generative_models import GenerativeModel, ChatSession, Part
import boto3
from botocore.config import Config

# Setup
# Update environment variables and setup
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1").strip()
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID").strip()
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY").strip()

EMBEDDING_MODEL = "amazon.titan-embed-text-v1"
GENERATIVE_MODEL = "anthropic.claude-3-sonnet-20240229-v1:0"
CHROMADB_HOST = os.environ["CHROMADB_HOST"]
CHROMADB_PORT = os.environ["CHROMADB_PORT"]

# Initialize AWS Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

# Initialize the GenerativeModel with specific system instructions
SYSTEM_INSTRUCTION = """
You are an AI assistant specialized in cheese knowledge. Your responses are based solely on the information provided in the text chunks given to you. Do not use any external knowledge or make assumptions beyond what is explicitly stated in these chunks.

When answering a query:
1. Carefully read all the text chunks provided.
2. Identify the most relevant information from these chunks to address the user's question.
3. Formulate your response using only the information found in the given chunks.
4. If the provided chunks do not contain sufficient information to answer the query, state that you don't have enough information to provide a complete answer.
5. Always maintain a professional and knowledgeable tone, befitting a cheese expert.
6. If there are contradictions in the provided chunks, mention this in your response and explain the different viewpoints presented.

Remember:
- You are an expert in cheese, but your knowledge is limited to the information in the provided chunks.
- Do not invent information or draw from knowledge outside of the given text chunks.
- If asked about topics unrelated to cheese, politely redirect the conversation back to cheese-related subjects.
- Be concise in your responses while ensuring you cover all relevant information from the chunks.

Your goal is to provide accurate, helpful information about cheese based solely on the content of the text chunks you receive with each query.
"""
# generative_model = GenerativeModel(
# 	GENERATIVE_MODEL,
# 	system_instruction=[SYSTEM_INSTRUCTION]
# )
# # https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
# embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

# Initialize chat sessions
chat_sessions: Dict[str, List[Dict]] = {}


# Connect to chroma DB
client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
method = "recursive-split"
collection_name = f"{method}-collection"
# Get the collection
collection = client.get_collection(name=collection_name)

def generate_query_embedding(query: str) -> List[float]:
    """Generate embeddings using AWS Bedrock Titan model"""
    body = json.dumps({"inputText": query})
    response = bedrock.invoke_model(
        modelId=EMBEDDING_MODEL,
        body=body
    )
    response_body = json.loads(response['body'].read())
    return response_body['embedding']


def create_chat_session() -> List[Dict]:
    """Create a new chat session"""
    return [{"role": "system", "content": SYSTEM_INSTRUCTION}]


def generate_chat_response(chat_session: List[Dict], message: Dict) -> str:
    """Generate a response using AWS Bedrock Claude model"""
    try:
        # Process message content and images similar to before
        message_parts = []
        
        # Handle image processing (similar to before, but format for Claude)
        if message.get("image"):
            # Convert base64 to Claude's image format
            # ... (image processing logic remains similar)
            pass
            
        # Handle text content
        if message.get("content"):
            query_embedding = generate_query_embedding(message["content"])
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            message_content = f"""
            {message["content"]}
            {"\n".join(results["documents"][0])}
            """
            message_parts.append({"role": "user", "content": message_content})
        
        # Update chat session with new message
        chat_session.extend(message_parts)
        
        # Prepare request for Claude
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "messages": chat_session,
            "max_tokens": generation_config["max_tokens"],
            "temperature": generation_config["temperature"],
            "top_p": generation_config["top_p"]
        })
        
        # Call Claude
        response = bedrock.invoke_model(
            modelId=GENERATIVE_MODEL,
            body=body
        )
        response_body = json.loads(response['body'].read())
        
        # Add assistant's response to chat history
        assistant_message = response_body['content'][0]['text']
        chat_session.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
        
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