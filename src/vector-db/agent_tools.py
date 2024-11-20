import json
import boto3


# Specify a function declaration and parameters for an API request
# Define the function schema as a dictionary instead of FunctionDeclaration
get_book_by_author_schema = {
    "name": "get_book_by_author",
    "description": "Get the book chunks filtered by author name",
    "parameters": {
        "type": "object",
        "properties": {
            "author": {"type": "string", "description": "The author name", "enum": ["C. F. Langworthy and Caroline Louisa Hunt", "J. Twamley", "George E. Newell", "T. D. Curtis", "Charles Thom and W. W. Fisk", "Thomas Wilson Reid", "Bob Brown", "Charles S. Brooks", "Pavlos Protopapas"]},
            "search_content": {"type": "string", "description": "The search text to filter content from books. The search term is compared against the book text based on cosine similarity. Expand the search term to a a sentence or two to get better matches"},
        },
        "required": ["author", "search_content"]
    }
}





def get_book_by_author(author, search_content, collection, embed_func):

    query_embedding = embed_func(search_content)

    # Query based on embedding value 
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        where={"author":author}
    )
    return "\n".join(results["documents"][0])


get_book_by_search_content_schema = {
    "name": "get_book_by_search_content",
    "description": "Get the book chunks filtered by search terms",
    "parameters": {
        "type": "object",
        "properties": {
            "search_content": {"type": "string", "description": "The search text to filter content from books. The search term is compared against the book text based on cosine similarity. Expand the search term to a a sentence or two to get better matches"},
        },
        "required": ["search_content"]
    }
}


def get_book_by_search_content(search_content, collection, embed_func):

    query_embedding = embed_func(search_content)

    # Query based on embedding value 
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10
    )
    return "\n".join(results["documents"][0])

# Define all functions available to the cheese expert
available_functions = {
    "get_book_by_author": {
        "function": get_book_by_author,
        "schema": get_book_by_author_schema
    },
    "get_book_by_search_content": {
        "function": get_book_by_search_content,
        "schema": get_book_by_search_content_schema
    }
}


def execute_function_calls(function_calls, collection, embed_func):
    responses = []
    for function_call in function_calls:
        function_name = function_call.get('name')
        arguments = function_call.get('arguments', {})
        
        if function_name == "get_book_by_author":
            response = get_book_by_author(
                arguments["author"], 
                arguments["search_content"],
                collection, 
                embed_func
            )
        elif function_name == "get_book_by_search_content":
            response = get_book_by_search_content(
                arguments["search_content"],
                collection, 
                embed_func
            )
        
        responses.append({
            "function_name": function_name,
            "content": response
        })
    
    return responses
