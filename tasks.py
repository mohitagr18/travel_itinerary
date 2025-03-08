from crewai import Task
from agents import travel_researcher, itinerary_planner, local_expert
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# Define your tools.  For this example, we're just using DuckDuckGo Search.
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# --- Tasks (using f-strings) ---
research_task = Task(
    description=f"""Research the best attractions, restaurants, and activities in {{destination}}.
    Consider the user's interests: {{interests}}. Focus on providing a diverse range of options.
    """,
    tools=[search_tool, scrape_tool],
    agent=travel_researcher,
    async_execution=True,
    expected_output="A list of attractions, restaurants, and activities.",
)

itinerary_task = Task(
    description=f"""Create a detailed day-by-day itinerary for a trip to {{destination}} from {{start_date}} to {{end_date}}.

    First, provide a brief overview of the top recommended places to visit and restaurants to try, based on the research.

    Then, create a detailed itinerary. Remember most hotels allow check-in at 4.00pm and checkout at 11.00am.
    Format the output as follows:

    **Top Recommendations:**

    *   **Places to Visit:**
        *   [Place 1] - [Brief Description]
        *   [Place 2] - [Brief Description]
        ...
    *   **Restaurants:**
        *   [Restaurant 1] - [Brief Description]
        *   [Restaurant 2] - [Brief Description]
        ...

    **Itinerary:**

    **Day 1: [Date]**
    *   [Time]: [Activity/Location] - [Brief Description]

    **Day 2: [Date]**
    *   [Time]: [Activity/Location] - [Brief Description]
     ...

    **If You Have More Time:**

    *   **Places to Visit:**
        *   [Additional Place 1] - [Brief Description]
        *    ...
    *   **Restaurants:**
        *   [Additional Restaurant 1] - [Brief Description]
        *   ...
    Consider travel times. Be realistic. Prioritize activities for {{interests}}.
    """,
    agent=itinerary_planner,
    context=[research_task],
    expected_output="A detailed, well-formatted, day-by-day itinerary with recommendations.",
)


local_expert_task = Task(
    description=f"""Answer specific questions about the travel destination: {{destination}} and question: {{question}}""",
    tools=[search_tool, scrape_tool],
    agent=local_expert,
    # async_execution=True,
    expected_output="A detailed answer."
)
