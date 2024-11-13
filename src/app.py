from fastapi import FastAPI, HTTPException
from llm2vec import LLM2Vec
import torch
from transformers import AutoTokenizer, AutoModel, AutoConfig
from peft import PeftModel
from huggingface_hub import login
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize models and tokenizer
try:
    # Ensure HF_TOKEN is available
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable is not set")
    
    # Login to Hugging Face
    login(token=hf_token)
    logger.info("Successfully logged in to Hugging Face")
    
    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
            "McGill-NLP/LLM2Vec-Meta-Llama-3-8B-Instruct-mntp",
            token=hf_token
    )
    logger.info("Tokenizer initialized successfully")
    
    # Load configuration
    config = AutoConfig.from_pretrained(
            "McGill-NLP/LLM2Vec-Meta-Llama-3-8B-Instruct-mntp",
            trust_remote_code=True,
            token=hf_token
    )
    logger.info("Config loaded successfully")
    
    # Initialize model
    model = AutoModel.from_pretrained(
            "McGill-NLP/LLM2Vec-Meta-Llama-3-8B-Instruct-mntp",
            token=hf_token,
            trust_remote_code=True,
            config=config,
            torch_dtype=torch.bfloat16,
            device_map="cuda" if torch.cuda.is_available() else "cpu"
    )
    logger.info(f"Model loaded successfully on {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    
    # Load PEFT model
    model = PeftModel.from_pretrained(
            model,
            "McGill-NLP/LLM2Vec-Meta-Llama-3-8B-Instruct-mntp",
            token=hf_token
    )
    logger.info("PEFT model loaded successfully")
    
    # Initialize LLM2Vec
    l2v = LLM2Vec(model, tokenizer, pooling_mode="mean", max_length=512)
    logger.info("LLM2Vec initialized successfully")

except Exception as e:
    logger.error(f"Error during initialization: {str(e)}")
    raise

@app.post("/encode")
async def encode_text(data: dict):
    try:
        texts = data.get("texts", [])
        if not texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        instruction = data.get("instruction", "")
        
        if instruction:
            queries = [[instruction, text] for text in texts]
            embeddings = l2v.encode(queries)
        else:
            embeddings = l2v.encode(texts)
        
        return {"embeddings": embeddings.tolist()}
    
    except Exception as e:
        logger.error(f"Error during encoding: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Encoding error: {str(e)}")

@app.get("/health")
async def health_check():
    try:
        # Basic model health check
        if not model or not tokenizer or not l2v:
            raise HTTPException(status_code=500, detail="Model components not properly initialized")
        
        return {
                "status": "healthy",
                "model_device": str(next(model.parameters()).device),
                "cuda_available": torch.cuda.is_available()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    logger.info("Application starting up")
    # You can add additional startup checks here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutting down")
    # Clean up resources if needed
