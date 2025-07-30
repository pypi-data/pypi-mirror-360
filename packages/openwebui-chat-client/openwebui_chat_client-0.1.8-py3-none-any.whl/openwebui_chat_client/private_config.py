# from openwebui_chat_client import OpenWebUIClient
# import logging
# from PIL import Image, ImageDraw, ImageFont
# from dotenv import load_dotenv

# # Load environment variables from a .env file if it exists
# load_dotenv()

# # --- Configuration ---
# BASE_URL = "http://localhost:3003"  # Replace with your OpenWebUI server URL
# # Obtain your JWT token or API key for authentication from your account settings.
# AUTH_TOKEN = "sk-26c968f00efd414a839ee725e3b082e8"
# MODEL_ID = "gpt-4.1"
# SINGLE_MODEL = "gpt-4.1"
# MULTIMODAL_MODEL = "gemini-2.0-flash"  # 单模型对话使用的默认模型

# # examples/basic_usage.py

# # 确保这些模型在你的 Open WebUI 中都可用
# PARALLEL_MODELS = ["gpt-4.1", "gemini-2.5-flash"]
# # 多模态测试模型

# # --- 为应用程序配置日志 ---
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )


# def create_test_image(text: str, filename: str) -> str:
#     """辅助函数，用于创建带文字的测试图片。"""
#     try:
#         img = Image.new("RGB", (500, 100), color=(20, 40, 80))
#         d = ImageDraw.Draw(img)
#         try:
#             font = ImageFont.truetype("arial.ttf", 30)
#         except IOError:
#             font = ImageFont.load_default()
#         d.text((10, 10), text, fill=(255, 255, 200), font=font)
#         img.save(filename)
#         logging.info(f"✅ Created test image: {filename}")
#         return filename
#     except ImportError:
#         logging.warning("Pillow library not installed. Cannot create test image.")
#         return None


# def run_tagging_demo():
#     """
#     Demonstrates creating a chat with tags and updating them.
#     """
#     if not AUTH_TOKEN:
#         logging.error(
#             "🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key."
#         )
#         return

#     # Initialize the client
#     client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)

#     # --- SCENE 1: Create a new chat with initial tags ---
#     print("\n" + "#" * 20 + " SCENE 1: Creating Chat with Tags " + "#" * 20)

#     chat_title = "Project Alpha Kick-off"
#     initial_tags = ["project-alpha", "planning", "Q4-2024"]

#     response, _ = client.chat(
#         question="What are the first three steps to kick-off a new software project?",
#         chat_title=chat_title,
#         folder_name="Active Projects",
#         tags=initial_tags,
#     )

#     if response:
#         print(f"\n🤖 [AI's Initial Plan]:\n{response}\n")

#     # --- SCENE 2: Continue the conversation and add a new tag ---
#     print("\n" + "#" * 20 + " SCENE 2: Continuing Chat & Adding More Tags " + "#" * 20)

#     # The client will find the existing chat by its title.
#     # We provide a new list of tags. The client should be smart enough
#     # to only add the new tag ('urgent') and not duplicate the existing ones.
#     updated_tags = ["project-alpha", "planning", "Q4-2024", "urgent"]

#     response, _ = client.chat(
#         question="Excellent. Now, please elaborate on the 'Requirement Gathering' step.",
#         chat_title=chat_title,  # Same title to continue the conversation
#         folder_name="Active Projects",
#         tags=updated_tags,
#     )

#     if response:
#         print(f"\n🤖 [AI's Elaboration]:\n{response}\n")

#     logging.info("\n🎉 Tagging demo completed. Please check your Open WebUI interface.")
#     logging.info(
#         f"Navigate to the '{chat_title}' chat to see the final tags: {updated_tags}"
#     )


# def run_all_demos():
#     """运行所有功能的演示。"""
#     if AUTH_TOKEN == "YOUR_AUTH_TOKEN":
#         logging.error("🛑 Please set your 'AUTH_TOKEN' in the script.")
#         return

#     # 使用一个默认模型初始化客户端，这个模型可以在 chat() 方法中被覆盖
#     client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=SINGLE_MODEL)

#     # # --- 场景 1: 单模型对话 ---
#     # print("\n" + "#" * 20 + " SCENE 1: Single-Model Chat " + "#" * 20)
#     # response, _ = client.chat(
#     #     question="What is the difference between a library and a framework?",
#     #     chat_title="Tech Concepts: Library vs Framework",
#     #     folder_name="Tech Discussions",
#     #     model_id=SINGLE_MODEL,  # 可以显式指定模型
#     # )
#     # if response:
#     #     print(f"\n🤖 [{SINGLE_MODEL}'s Response]:\n{response}\n")

#     # # --- 场景 2: 多模型并行对话 (第一轮) ---
#     # print("\n" + "#" * 20 + " SCENE 2: Multi-Model Parallel Chat (Round 1) " + "#" * 20)
#     # parallel_responses = client.parallel_chat(
#     #     question="In one sentence, what is the most exciting thing about space exploration?",
#     #     chat_title="Space Exploration Insights",
#     #     model_ids=PARALLEL_MODELS,
#     #     folder_name="Science",
#     # )
#     # if parallel_responses:
#     #     for model, content in parallel_responses.items():
#     #         print(f"\n🤖 [{model}'s Response]:\n{content}\n")

#     # # --- 场景 3: 继续多模型并行对话 (第二轮) ---
#     # print("\n" + "#" * 20 + " SCENE 3: Multi-Model Parallel Chat (Round 2) " + "#" * 20)
#     # # 客户端会自动找到 "Space Exploration Insights" 这个聊天并继续
#     # parallel_responses_2 = client.parallel_chat(
#     #     question="Based on your previous answer, name one specific mission that exemplifies this.",
#     #     chat_title="Space Exploration Insights",
#     #     model_ids=PARALLEL_MODELS,
#     #     folder_name="Science",
#     # )
#     # if parallel_responses_2:
#     #     for model, content in parallel_responses_2.items():
#     #         print(f"\n🤖 [{model}'s Response]:\n{content}\n")

#     # # --- 场景 4: 多模态对话 (使用单模型chat方法) ---
#     # print("\n" + "#" * 20 + " SCENE 4: Multimodal Chat " + "#" * 20)
#     # image_path = create_test_image("Welcome to the Future!", "multimodal_test.png")
#     # if image_path:
#     #     # 我们使用标准的 chat() 方法，但传入图片路径和多模态模型ID
#     #     response, _ = client.chat(
#     #         question="What message is written in this image?",
#     #         chat_title="Multimodal Test",
#     #         folder_name="Tech Demos",
#     #         image_paths=[image_path],
#     #         model_id=MULTIMODAL_MODEL,
#     #     )
#     #     if response:
#     #         print(f"\n🤖 [{MULTIMODAL_MODEL}'s Response]:\n{response}\n")
#     # else:
#     #     logging.warning(
#     #         "Skipping multimodal demo because test image could not be created."
#     #     )

#     # **************************************************************************
#     # --- Scene 3: Multi-Model, Multimodal Parallel Chat ---
#     # This is the ultimate test case.
#     # **************************************************************************
#     print("\n" + "#" * 20 + " SCENE 3: Multi-Model & Multimodal Chat " + "#" * 20)
#     image_path = create_test_image(
#         "Project 'Phoenix' Status: GREEN", "multimodal_status.png"
#     )

#     if image_path:
#         # We use the parallel_chat() method with both text and an image.
#         multimodal_responses = client.parallel_chat(
#             question="Summarize the status update from this image. Be concise.",
#             chat_title="Project Phoenix Status Report",
#             folder_name="Project Updates",
#             image_paths=[image_path],
#             model_ids=PARALLEL_MODELS,
#         )
#         if multimodal_responses:
#             for model, content in multimodal_responses.items():
#                 print(f"\n🤖 [{model}'s Response]:\n{content}\n")
#     else:
#         logging.warning(
#             "Skipping multimodal demo because test image could not be created."
#         )

#     print("\n🎉 All demo scenarios completed. Please check your Open WebUI interface.")


# def run_tagging_demo():
#     """
#     Demonstrates creating a chat with tags and updating them.
#     """
#     if not AUTH_TOKEN:
#         logging.error(
#             "🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key."
#         )
#         return

#     # Initialize the client
#     client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=MODEL_ID)

#     # --- SCENE 1: Create a new chat with initial tags ---
#     print("\n" + "#" * 20 + " SCENE 1: Creating Chat with Tags " + "#" * 20)

#     chat_title = "Project Alpha Kick-off"
#     initial_tags = ["project-alpha", "planning", "Q4-2024"]

#     response, _ = client.chat(
#         question="What are the first three steps to kick-off a new software project?",
#         chat_title=chat_title,
#         folder_name="Active Projects",
#         tags=initial_tags,
#     )

#     if response:
#         print(f"\n🤖 [AI's Initial Plan]:\n{response}\n")

#     # --- SCENE 2: Continue the conversation and add a new tag ---
#     print("\n" + "#" * 20 + " SCENE 2: Continuing Chat & Adding More Tags " + "#" * 20)

#     # The client will find the existing chat by its title.
#     # We provide a new list of tags. The client should be smart enough
#     # to only add the new tag ('urgent') and not duplicate the existing ones.
#     updated_tags = ["project-alpha", "planning", "Q4-2024", "urgent"]

#     response, _ = client.chat(
#         question="Excellent. Now, please elaborate on the 'Requirement Gathering' step.",
#         chat_title=chat_title,  # Same title to continue the conversation
#         folder_name="Active Projects",
#         tags=updated_tags,
#     )

#     if response:
#         print(f"\n🤖 [AI's Elaboration]:\n{response}\n")

#     logging.info("\n🎉 Tagging demo completed. Please check your Open WebUI interface.")
#     logging.info(
#         f"Navigate to the '{chat_title}' chat to see the final tags: {updated_tags}"
#     )


# if __name__ == "__main__":
#     run_tagging_demo()



import logging
import os
import time
from openwebui_chat_client import OpenWebUIClient
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
# Load environment variables from a .env file if it exists
load_dotenv()

# --- Configuration from Environment Variables ---
BASE_URL = os.getenv("OUI_BASE_URL", "http://localhost:3000")
AUTH_TOKEN = os.getenv("OUI_AUTH_TOKEN")

# *** Models for Testing ***
# Ensure these models are available in your Open WebUI instance.
DEFAULT_MODEL = "gpt-4.1"  # Default model for single chat
PARALLEL_MODELS = ["gpt-4.1", "gemini-2.5-flash"]
MULTIMODAL_MODEL = "gpt-4.1"
RAG_MODEL = "gemini-2.5-flash" # A good model for RAG tasks

# --- Configure Logging for the Application ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Helper function to create test files ---
def create_test_file(filename: str, content: str):
    """Creates a local text file for testing RAG and KB features."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"✅ Created test file: {filename}")
        return filename
    except Exception as e:
        logging.error(f"Failed to create test file {filename}: {e}")
        return None

def cleanup_files(filenames: list):
    """Removes test files created during the demo."""
    for filename in filenames:
        if filename and os.path.exists(filename):
            os.remove(filename)
            logging.info(f"🧹 Cleaned up test file: {filename}")

# # --- Demo Scenarios ---

# def demo_knowledge_base(client: OpenWebUIClient):
#     print("\n" + "#"*20 + " SCENE 1: Knowledge Base Management " + "#"*20)
#     kb_name = "Project Apollo Documents"
#     file_content = "Project Apollo's primary objective was to land humans on the Moon and bring them back safely to Earth. The Apollo 11 mission was the first to achieve this in 1969."
#     test_file = create_test_file("apollo_brief.txt", file_content)
    
#     if not test_file:
#         return

#     success = client.add_file_to_knowledge_base(
#         file_path=test_file,
#         knowledge_base_name=kb_name
#     )

#     if success:
#         logging.info(f"Successfully added '{test_file}' to the '{kb_name}' knowledge base.")
#         # Note: Chatting with the collection would be the next step.
#         # This can be implemented by passing `rag_collections=[kb_name]` to the chat method.
#     else:
#         logging.error("Failed to complete the knowledge base operation.")
    
#     cleanup_files([test_file])

# def demo_rag_chat(client: OpenWebUIClient):
#     print("\n" + "#"*20 + " SCENE 2: RAG Chat with a File " + "#"*20)
#     file_content = "The Ouroboros protocol is a family of proof-of-stake blockchain protocols that provide verifiable security guarantees."
#     test_file = create_test_file("blockchain_protocol.txt", file_content)

#     if not test_file:
#         return
        
#     response, _ = client.chat(
#         question="Based on the document, what is the Ouroboros protocol?",
#         chat_title="Blockchain RAG Test",
#         rag_files=[test_file],
#         model_id=RAG_MODEL
#     )
#     if response:
#         print(f"\n🤖 [RAG Response]:\n{response}\n")

#     cleanup_files([test_file])


# def demo_parallel_chat(client: OpenWebUIClient):
#     print("\n" + "#"*20 + " SCENE 3: Multi-Model Parallel Chat " + "#"*20)
#     responses = client.parallel_chat(
#         question="What is the most exciting thing about space exploration in one sentence?",
#         chat_title="Space Exploration Insights",
#         model_ids=PARALLEL_MODELS,
#         folder_name="Science",
#         tags=["space", "exploration", "multi-model"]
#     )
#     if responses:
#         for model, content in responses.items():
#             print(f"\n🤖 [{model}'s Response]:\n{content}\n")
            
def run_knowledge_base_chat_demo():
    """
    Demonstrates creating a knowledge base, adding a file,
    and then chatting with that knowledge base.
    """
    if not AUTH_TOKEN:
        logging.error("🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key.")
        return
        
    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)

    # --- Setup: Define KB and file content ---
    # Use a unique name for the KB to avoid conflicts during testing.
    kb_name = f"ProjectApolloDocs-{int(time.time())}"
    file_content = "Project Apollo's primary objective was to land humans on the Moon and bring them back safely to Earth. The program, which ran from 1961 to 1972, was one of the most ambitious scientific undertakings in history. The Apollo 11 mission, in 1969, was the first to achieve this."
    test_file = create_test_file("apollo_mission_brief.txt", file_content)
    
    if not test_file:
        return

    try:
        # --- Step 1: Create Knowledge Base and Add File ---
        print("\n" + "#"*20 + " SCENE 1: Populating Knowledge Base " + "#"*20)
        success = client.add_file_to_knowledge_base(
            file_path=test_file,
            knowledge_base_name=kb_name
        )

        if not success:
            logging.error("Failed to set up the knowledge base. Aborting demo.")
            return
        
        logging.info("Knowledge base is ready. Waiting a moment for processing...")
        time.sleep(5) # Give the backend a moment to process the file

        # --- Step 2: Chat with the Knowledge Base ---
        print("\n" + "#"*20 + " SCENE 2: Chatting with the Knowledge Base " + "#"*20)
        
        response, _ = client.chat(
            question="According to the documents, what was the primary objective of Project Apollo?",
            chat_title=f"Inquiry about {kb_name}",
            # Reference the knowledge base by its name
            rag_collections=[kb_name]
        )

        if response:
            print(f"\n🤖 [RAG Response from Knowledge Base]:\n{response}\n")
            # You can check if the response correctly uses the info from the test file.

    finally:
        # --- Cleanup ---
        cleanup_files([test_file])
        # Optional: Add a method to the client to delete the knowledge base for a full cleanup.
        # client.delete_knowledge_base(kb_name)

    print("\n🎉 Knowledge base chat demo completed.")

# def main():
#     """Runs all demo scenarios."""
#     if not AUTH_TOKEN:
#         logging.error("🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key.")
#         return
        
#     # Initialize the client with a default model
#     client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)
#     run_knowledge_base_chat_demo()

#     # # Run the demos sequentially
#     # demo_knowledge_base(client)
#     # time.sleep(2) # Pause between demos for clarity
#     # demo_rag_chat(client)
#     # time.sleep(2)
#     # demo_parallel_chat(client)

#     print("\n🎉 All demo scenarios completed. Please check your Open WebUI interface to see the results.")



# from openwebui_chat_client import OpenWebUIClient

# client = OpenWebUIClient(
#     base_url="http://localhost:3003",
#     token=AUTH_TOKEN,
#     default_model_id="gpt-4.1"
# )

# responses = client.parallel_chat(
#     question="Compare the strengths of GPT-4.1 and Gemini 2.5 Flash for document summarization.",
#     chat_title="Model Comparison: Summarization",
#     model_ids=["gpt-4.1", "gemini-2.5-flash"]
# )

# for model, resp in responses.items():
#     print(f"{model} Response:\n{resp}\n")
# # if __name__ == "__main__":
# #     main()


def run_models_management_demo():
    """
    Demonstrates the model management functionality of the OpenWebUIClient.
    """
    if not AUTH_TOKEN:
        logging.error(
            "🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key."
        )
        return

    # 1. Initialize the client
    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)

    # 2. List all models
    logging.info("--- Listing all available models ---")
    models = client.list_models()
    print("\nAvailable Models:")
    for model in models:
        print(f"- {model}")

    # 3. Get details of a specific model
    logging.info("--- Getting details for the default model ---")
    model_details = client.get_model('gpt-4.1')
    print(f"\nDetails for {DEFAULT_MODEL}: {model_details}")
    
    
def rename_chat_demo():
    """
    Demonstrates renaming a chat.
    """
    if not AUTH_TOKEN:
        logging.error(
            "🛑 Environment variable 'OUI_AUTH_TOKEN' is not set. Please set it to your API key."
        )
        return

    # 1. Initialize the client
    client = OpenWebUIClient(BASE_URL, AUTH_TOKEN, default_model_id=DEFAULT_MODEL)

    # 2. Rename a chat
    old_title = "Old Chat Title"
    new_title = "test"
    
    success = client.rename_chat('9b1e1c97-c3ea-4a67-9b92-dffba3abc597', new_title)
    
    client.chat(
        question="What is the capital of France?",
        chat_title=new_title,  # This will create a new chat with the new title
    )
    
    if success:
        print(f"✅ Successfully renamed chat from '{old_title}' to '{new_title}'")
    else:
        print(f"❌ Failed to rename chat from '{old_title}' to '{new_title}'")
    
if __name__ == "__main__":
    # Uncomment the line below to run the models management demo
    # run_models_management_demo()
    # Uncomment the line below to run the knowledge base chat demo
    run_knowledge_base_chat_demo()
    # Uncomment the line below to run all demos
    # main()
    # rename_chat_demo()