'''
Main execution point for the Compliance QA pipeline
'''
import uuid
import json
import logging
from pprint import pprint
from dotenv import load_dotenv
load_dotenv(override=True)

from backend.src.graph.workflow import app
logging.basicConfig(
    level=logging.INFO,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("brand-guardian-runner")

def run_cli_simulation():
    '''
    Simulates the video compliance audit request
    '''
    #generate the session id
    session_id = str(uuid.uuid4())
    logger.info(f"Starting Audit session: {session_id}")

    #define the initial state
    initial_inputs = {
        "video_url": "",
        "video_id": f"vid_{session_id[:8]}",
        "compliance_results": [],
        "errors": {}
    }

    print("-----------Initialize workflow-------")
    print(f"input payload: {json.dumps(initial_inputs, indent=2)}")
    try:
        final_state = app.invoke(initial_inputs)
        print("\n---------Workflow complete-------")
        print("\n--------Compliance Audit Report--------")
        print(f"Video ID: {final_state.get('video_id')}")
        print(f"Status: {final_state.get('final_status')}")
        print("\n Violations detected")
        results = final_state.get('compliance_results', [])
        if results:
            for issue in results:
                print(f" - [{issue.get('severity')}] [{issue.get('category')}] : [{issue.get('description')}]")
        else:
            print("No violations detected")

        print("\nFinal summary")
        print(final_state.get('final_report'))

    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")

if __name__=="main":
    run_cli_simulation()
