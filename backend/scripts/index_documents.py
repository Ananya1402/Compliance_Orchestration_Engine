import os
import glob
import logging
from dotenv import load_dotenv
load_dotenv(override=True)

#document loaders and splitters
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

#azure components import
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

#setup logging and config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("indexer")
def index_docs():
    '''
    Reads the pdfs, chunks them, and uploads them to Azure AI Search'''

    #define paths, we look for data folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, "../../backend/data")

    #check the environment variables
    logger.info("="*60)
    logger.info("environment configuration check: ")
    logger.info(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION: {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"AZURE_OPENAI_EMBEDDING_DEPLOYMENT: {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-small')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT: {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME: {os.getenv('AZURE_SEARCH_INDEX_NAME')}")
    logger.info("="*60)

    #validate the reqd. env variables
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY",
        "AZURE_SEARCH_INDEX_NAME"

    ]
    missing_vars = [var for var in required_vars if  not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing reqd. environment variables: {missing_vars}")
        logger.error("Please check your .env file and ensure all the variables are set")
        return 
    
    #initialize the embedding model - turns text into vectors
    try:
        logger.info("Initializing Azure OpenAI Embeddings .....")
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT', 'text-embedding-3-small')
            azure_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY'),
            openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION', "2024-02-01"),
        )
        logger.info("Embeddings model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings model: {e}")
        logger.error("Please verify your Azure OpenAI deployment name and endpoint.")
        return
    
     
    try:
        logger.info("Initializing Azure AI Search vector store .....")
        embeddings = AzureOpenAIEmbeddings(
            azure_search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
            azure_search_api_key = os.getenv('AZURE_SEARCH_API_KEY')
            index_name = index_name,
            embeddings_function = embeddings.embed_query,
        )
        logger.info(f"Vector store initialized for the index {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Search: {e}")
        logger.error("Please verify your Azure search endpoint, API key and index name.")
        return
    
    #find PDF files
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {data_folder}. Please add files")
    logger.info(f"Found {len(pdf_files)} PDFs to process: {[os.path.basename(f) for f in pdf_files]}")

    all_splits = []

    #process each pdf
    for pdf_path in pdf_files:
        try:
            logger.info(f"Loading: {os.path.basename(pdf_path)} .....")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            #chunking strategy
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200
            )

            splits = text_splitter.split_documents(raw_docs)
            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)
            all_splits.extend(splits)
            logger.info(f"Split into {len(splits)} chunks.")

        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}")

        #upload to Azure
        if all_splits:
            logger.info(f"Uploading {len(all_splits)} chunks to Azure AI Search Index '{index_name}'")
            try:
                #azure search accepts patches automatically via this method
                vector_store.add_documents(documents = all_splits)
                logger.info("="*60)
                logger.info("Indexing Complete! Knowledge base is ready....")
                logger.info(f"Total chunks indexed: {len(all_splits)}")
            except Exception as e:
                logger.error(f"Failed to upload the documents to Azure Search: {e}")
                logger.error("Please check the Azure Search configuration and try again later")


        else:
            logger.warning("No documents were processed.")


if __name__ == "__main__":
    index_docs()
