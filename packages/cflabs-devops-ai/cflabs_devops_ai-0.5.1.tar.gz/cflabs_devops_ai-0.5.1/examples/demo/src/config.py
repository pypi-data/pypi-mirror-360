import os
from dotenv import load_dotenv
from src.utils.logger import get_logger
load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "False")
    ENV = os.getenv("ENV", "dev")
    DB_NAME = os.getenv("DB_NAME", "my_contextual_db")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.getenv("AWS_REGION")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    logger = get_logger(__name__)
    # print all the variables
    logger.info(f"DB_NAME: {DB_NAME}")
    logger.info(f"DB_USERNAME: {DB_USERNAME}")
    logger.info(f"DB_PASSWORD: {DB_PASSWORD}")
    logger.info(f"DB_HOST: {DB_HOST}")
    logger.info(f"DB_PORT: {DB_PORT}")
    logger.info(f"PINECONE_API_KEY: {PINECONE_API_KEY}")
    logger.info(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
    logger.info(f"VOYAGE_API_KEY: {VOYAGE_API_KEY}")
    logger.info(f"DEBUG: {DEBUG}")
    logger.info(f"ENV: {ENV}")