from crewai import Agent
from crewai_tools import SerperDevTool
# from langchain_community.tools import DuckDuckGoSearchRun

# Define your tools.  For this example, we're just using DuckDuckGo Search.
search_tool = SerperDevTool()

# --- Agents ---
travel_researcher = Agent(
    role='Travel Researcher',
    goal='Gather comprehensive information about a given travel destination.',
    backstory="""Seasoned travel researcher. Finds hidden gems and popular hotspots.""",
    tools=[search_tool],
    # llm = llm,
    allow_delegation=True,
    verbose=True
)

itinerary_planner = Agent(
    role='Itinerary Planner',
    goal='Structure travel information into a day-by-day itinerary and incorporate expert answers.',
    backstory="""
    Meticulous itinerary planner. Creates efficient and enjoyable plans.
    You MUST output a day-by-day itinerary, with specific dates and times and includes expert advice.
    """,
    tools=[],
    # llm = llm,
    verbose=True
)

local_expert = Agent(
    role='Local Expert',
    goal='Provide insider tips and answer specific questions.',
    backstory="""Long-time resident, knows the destination intimately.""",
    tools=[search_tool],
    verbose=True,
    allow_delegation=False
)
