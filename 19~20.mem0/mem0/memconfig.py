import os
import dotenv
from mem0 import Memory

dotenv.load_dotenv()

config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "qwen-max",
            "api_key": os.environ.get("TONGYI_API_KEY"),
            "openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-v2",
            "api_key": os.environ.get("TONGYI_API_KEY"),
            "openai_base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test",
            "host": "116.153.88.164",
            "port": 6333,
            #"embedding_model_dims": 1536
        }
    }
}

m = Memory.from_config(config)