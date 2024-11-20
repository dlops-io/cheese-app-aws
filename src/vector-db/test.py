## Test ChromaDB
import os
import chromadb
import time
import requests

def test_chromadb_connection():
    """Test basic ChromaDB connectivity and operations"""
    
    # Get environment variables
    CHROMADB_HOST = os.environ.get("CHROMADB_HOST", "localhost")  # Default to localhost
    CHROMADB_PORT = os.environ.get("CHROMADB_PORT", "8000")       # Default to 8000
    
    print(f"\nStarting ChromaDB tests:")
    print(f"Host: {CHROMADB_HOST}")
    print(f"Port: {CHROMADB_PORT}")
    
    # First test basic connectivity via REST API
    base_url = f"http://{CHROMADB_HOST}:{CHROMADB_PORT}"
    print(f"\nTesting REST API endpoints at {base_url}:")
    
    try:
        # Test heartbeat
        heartbeat_url = f"{base_url}/api/v1/heartbeat"
        response = requests.get(heartbeat_url)
        print(f"Heartbeat response ({response.status_code}): {response.text}")
        
        # Test version endpoint
        version_url = f"{base_url}/api/v1/version"
        response = requests.get(version_url)
        print(f"Version response ({response.status_code}): {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"REST API test failed: {str(e)}")
    
    print("\nTesting ChromaDB client operations:")
    
    try:
        # Initialize client with verbose logging
        print("Initializing ChromaDB client...")
        client = chromadb.HttpClient(
            host=CHROMADB_HOST,
            port=CHROMADB_PORT,
            settings=chromadb.Settings(
                anonymized_telemetry=False,
                allow_reset=True,
                is_persistent=True
            )
        )
        print("✅ Successfully connected to ChromaDB")
        
        # Test collection operations
        collection_name = "test_collection"
        
        # Delete collection if it exists
        print(f"\nAttempting to delete existing collection '{collection_name}'...")
        try:
            client.delete_collection(name=collection_name)
            print("✅ Successfully deleted existing test collection")
        except Exception as e:
            print(f"Note: Could not delete collection (this is normal if it didn't exist): {str(e)}")
        
        # Create a new collection
        print(f"\nCreating new collection '{collection_name}'...")
        collection = client.create_collection(name=collection_name)
        print("✅ Successfully created test collection")
        
        # Add some test data
        print("\nAdding test documents...")
        collection.add(
            documents=["This is a test document", "This is another test document"],
            metadatas=[{"source": "test1"}, {"source": "test2"}],
            ids=["id1", "id2"]
        )
        print("✅ Successfully added test documents")

        # Query the collection
        print("\nQuerying collection...")
        results = collection.query(
            query_texts=["test document"],
            n_results=2
        )
        print("✅ Successfully queried collection")
        print("Query results:", results)
        
        # Clean up
        print(f"\nCleaning up collection '{collection_name}'...")
        client.delete_collection(name=collection_name)
        print("✅ Successfully cleaned up test collection")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ChromaDB test failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Add a small delay to ensure ChromaDB is fully started
    print("Waiting for ChromaDB to start...")
    time.sleep(5)
    
    success = test_chromadb_connection()
    
    if success:
        print("\n🎉 All ChromaDB tests passed!")
    else:
        print("\n❌ ChromaDB tests failed!")
        print("\nTroubleshooting tips:")
        print("1. Check if ChromaDB container is running:")
        print("   docker ps | grep chromadb")
        print("2. Check container logs:")
        print("   docker logs cheese-app-vector-db")
        print("3. Verify environment variables are set correctly:")
        print("   echo $CHROMADB_HOST")
        print("   echo $CHROMADB_PORT")


################################################################################
# Bedrock
################################################################################
# import boto3
# import os

# # Update environment variables and setup
# AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1").strip()
# AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID").strip()
# AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY").strip()

# # Client for administrative operations
# bedrock = boto3.client('bedrock', 
#                       region_name=AWS_REGION, 
#                       aws_access_key_id=AWS_ACCESS_KEY_ID,
#                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# # Client for making inference calls
# runtime = boto3.client('bedrock-runtime',
#                       region_name=AWS_REGION, 
#                       aws_access_key_id=AWS_ACCESS_KEY_ID,
#                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY) 

# try:
#     response = bedrock.list_foundation_models()
#     print("Authentication successful!")
#     # print("Available models:", response['modelSummaries'])
# except Exception as e:
#     print("Authentication failed:", str(e))