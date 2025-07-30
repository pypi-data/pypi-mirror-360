from flask import Blueprint, request, jsonify
from src.core.document_summary.summarizer import DocumentSummaryEngine
from src.core.numerical_summary.summarizer import NumericalSummaryEngine
from src.utils.logger import get_logger, time_function, log_function_call

logger = get_logger(__name__)
summarize_bp = Blueprint('summarize', __name__)

@summarize_bp.route('/document-summary', methods=['POST'])
@time_function
@log_function_call
def document_summarize():
    logger.info("Received summarize request")
    
    req = request.get_json()
    goal = req.get("goal")
    project_name = req.get("project_name", "rag-engine")
    
    if not goal:
        logger.error("No goal provided")
        return jsonify({"error": "No goal provided"}), 400
    
    logger.info(f"Processing summarize: '{goal[:50]}...'")
    
    try:
        rag_engine = DocumentSummaryEngine(project_name=project_name)
        
        result = rag_engine.document_summarization(goal)
        response_data = {
            "response": {
                "goal": result["goal"],
                "enriched_goal": result["enriched_goal"],
                "summary": result["summary"]
            }
        }
        
        logger.info(f"Summarize completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error during summarize: {str(e)}")
        return jsonify({"error": str(e)}), 500

@summarize_bp.route('/numerical-summary', methods=['POST'])
@time_function
@log_function_call
def numerical_summarize():
    logger.info("Received numerical summarize request")
    
    req = request.get_json()
    goal = req.get("goal")
    database_name = req.get("database_name", "c291cd37_17a5_49dd_9af0_38104c8002be")

    if not goal:
        logger.error("No goal provided")
        return jsonify({"error": "No goal provided"}), 400

    if not database_name:
        logger.error("No database name provided")
        return jsonify({"error": "No database name provided"}), 400
    
    logger.info(f"Processing numerical summarize: '{goal[:50]}...'")
    
    # try:
    rag_engine = NumericalSummaryEngine(database_name=database_name)
    result = rag_engine.numerical_summarization(goal)
    response_data = {
        "response": {
            "goal": result["goal"],
            "summary": result["summary"]
        }
    }
    
    logger.info(f"Numerical summarize completed successfully")
    return jsonify(response_data)   
    
    # except Exception as e:
    #     logger.error(f"Error during numerical summarize: {str(e)}")
    #     return jsonify({"error": str(e)}), 500