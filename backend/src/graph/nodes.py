import json
import os
import re
import logging
from typing import List, Dict, Any
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

#import state schema
from backend.src.graph.state import VideoAuditState, ComplianceIssue

#import  service
from backend.src.services.video_indexer import VideoIndexerService

logger = logging.getLogger("brand-guardian")
logging.basicConfig(level=logging.INFO)

def index_video_node(state:VideoAuditState)->Dict[str, Any]:
    '''
    Downloads the youtube video from the url
    Uploads to the Azure video indexer
    Extracts the insights
    '''
    video_url = state.get("video_url")
    video_id_input = state.get("video_id", "vid_demo")

    logger.info(f"---[Node:Indexer] Processing: {video_url}")
    local_filename = "temp_audio_video.mp4"

    
