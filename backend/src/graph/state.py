import operator
from typing import Any, Annotated, List, Dict, Optional, TypedDict

#define schema for a single compliance result
#error report
class ComplianceIssue(TypedDict):
    category:str
    description:str  #specific detail of violation
    severity:str  #critical|warning
    timestamp:Optional[str]

#define the global graph state
#defines the state that gets passed around in the agentic workflow
class VideoAuditState(TypedDict):
    '''
    defines the data schema for langgraph execution content
    Main container - holds all information about the audit right from initial url 
    to the final report'''

    #input params
    video_id:str
    video_url:str

    #ingestion and extraction data
    local_file_path:Optional[str]
    video_metadata:Dict[str,Any]  #{"duration":15, "resolution":"1080p"}
    transcript:Optional[str]       #fully extracted speech to text
    ocr_text:List[str]

    #analysis result
    #stores a list of all violations found by AI
    compliance_result:Annotated[List[ComplianceIssue], operator.add]

    #final deliverables
    final_status:str #PASS|FAIL
    final_report:str #markdown

    #system observability
    #errors: API timeout, system-level errors
    errors:Annotated[List[str], operator.add]
