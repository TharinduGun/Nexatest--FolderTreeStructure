from app.utils.folder_tree import create_folder_tree, generate_tree_summary, get_flat_path_map
import os

# 1. Define the Chatbot Data Structure
chatbot_structure = {
    "chatbot_data": {
        "raw_uploads": {
            "images": {},       # Store original uploaded images
            "documents": {},    # Store original PDFs/Text files
        },
        "processed": {
            "images": {         # Resized/Normalized images
                "thumbnails": {}
            },
            "texts": {          # Extracted text content
                "chunks": {}    # Text chunks for RAG
            },
            "embeddings": {}    # Vector embeddings
        },
        "metadata": {           # JSON/DB files
            "users": {},
            "sessions": {},
            "logs": {}
        },
        "README.txt": "This directory contains all persistent data for the Chatbot."
    }
}

def main():
    base_dir = "./"  # Create in current directory
    
    print(" Chatbot Folder Structure Plan:")
    print(generate_tree_summary(chatbot_structure))
    
    print("\nCreating Folders...")
    paths = create_folder_tree(base_dir, chatbot_structure)
    
    # Example of accessing paths
    # We can use the flat map for easy access
    flat_paths = get_flat_path_map(base_dir, chatbot_structure)
    
    # Let's say we want to save an image
    img_path = flat_paths["chatbot_data_raw_uploads_images"]
    print(f"\n Structure Created Successfully!")
    print(f"   Image Upload Path: {img_path.resolve()}")
    print(f"   Metadata Path:     {flat_paths['chatbot_data_metadata'].resolve()}")

if __name__ == "__main__":
    main()
