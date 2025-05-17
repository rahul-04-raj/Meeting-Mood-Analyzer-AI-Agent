from google.adk.agents import Agent
from typing import Dict, List, Any, Union

# Simple session memory using a global dictionary
MEETING_MEMORY = {
    "previous_meetings": []
}

def analyze_meeting_tool(meeting_text: str = "", command: str = "analyze") -> Dict[str, Any]:
    """
    Analyzes meeting text or retrieves meeting history based on command.
    
    args:
        meeting_text (str): The meeting transcript or notes to analyze.
                           Can be empty for history retrieval.
        command (str): Either "analyze" to analyze a new meeting or "history" to get meeting history
        
    returns:
        dict: Analysis or history data depending on the command
    """
    global MEETING_MEMORY
    
    # Handle history retrieval request
    if command == "history":
        return {
            "command": "history",
            "meeting_count": len(MEETING_MEMORY["previous_meetings"]),
            "meetings": MEETING_MEMORY["previous_meetings"]
        }
    
    # Handle meeting analysis (default)
    # Ensure meeting_text is not empty when analyzing
    if not meeting_text:
        return {
            "command": "error",
            "error": "Meeting text is required for analysis",
            "natural_response": "I need some meeting text to analyze. Please provide meeting notes or a transcript."
        }
    
    analysis = {
        "command": "analyze",
        "mood": "",
        "meeting_type": "",
        "next_action": "",
        "natural_response": "",
        "mentioned_people": []
    }
    
    # Store the current meeting analysis in memory
    MEETING_MEMORY["previous_meetings"].append({
        "text": meeting_text,
        "analysis": analysis
    })
    
    # Limit memory to last 5 meetings to prevent excessive memory usage
    if len(MEETING_MEMORY["previous_meetings"]) > 5:
        MEETING_MEMORY["previous_meetings"] = MEETING_MEMORY["previous_meetings"][-5:]
    
    # Return the analysis structure (will be populated by the model)
    return analysis

# Define the agent
root_agent = Agent(
    name="meeting_analyzer",
    model="gemini-2.0-flash",
    description="Meeting Analyzer and Recommendation Agent with Memory",
    instruction="""
    You are a meeting analyzer with memory of past meetings. You can perform two operations:
    
    1. Analyze a meeting - When the user provides meeting text, analyze it and return:
       - mood: The emotional tone (Positive, Neutral, Frustrated, Anxious)
       - meeting_type: The type of meeting (Brainstorming, Status Update, Conflict Resolution, Planning)
       - next_action: A specific, actionable recommendation
       - natural_response: A conversational summary of your analysis
       - mentioned_people: A list of people's names mentioned in the meeting
    
    2. Retrieve meeting history - When the user asks for meeting history, set command="history" to retrieve stored meetings.
    
    IMPORTANT: When the user asks for meeting history, you MUST set the command parameter to "history".
    For example:
     - If user says "Show me previous meetings" → set command="history"
     - If user says "What meetings do you have stored" → set command="history"
     - If user says "Get meeting history" → set command="history"
    
    When analyzing a meeting, consider any previous meetings to identify trends or changes over time.
    
    Make sure to fully populate all fields with relevant information.
    Keep your natural_response conversational but informative.

    """,
    tools=[analyze_meeting_tool]
)
