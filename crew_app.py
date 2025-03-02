from crewai import Crew, LLM
from agents import travel_researcher, itinerary_planner, local_expert
from tasks import research_task, itinerary_task, local_expert_task
import streamlit as st
from openai import OpenAI 
import os
from dotenv import load_dotenv
import datetime
import io
import contextlib

def load_environment_variables():
    """Loads environment variables from a .env file."""
    load_dotenv()
    os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
    os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY2')  # Keep this for CrewAI

def run_crew(destination, start_date, end_date, interests, question):
    """Runs the CrewAI crew with the given inputs."""
    crew = Crew(
        agents=[travel_researcher, itinerary_planner, local_expert],
        tasks=[research_task, itinerary_task, local_expert_task],
        verbose=True
    )
    start_date_str = start_date.strftime("%Y-%m-%d") if start_date else ""
    end_date_str = end_date.strftime("%Y-%m-%d") if end_date else ""

    results = crew.kickoff(
        inputs={
            "destination": destination,
            "interests": interests,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "question": question
        }
    )
    return results

def get_user_inputs():
    """Gets user inputs for destination, dates, interests, and question."""
    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input("Destination:")
        interests = st.text_area("Interests (optional):", placeholder="e.g., hiking, food, museums")
        question = st.text_input("Ask a local expert (optional):", placeholder="e.g., vegetarian options")
    with col2:
        today = datetime.date.today()
        start_date = st.date_input("Start Date", min_value=today, value=today)
        end_date = st.date_input("End Date", min_value=start_date or today, value=start_date or today)
    return destination, start_date, end_date, interests, question

def display_results(results):
    """Displays the itinerary and expert's answer (if available)."""
    if results:
        st.markdown("## Itinerary and Recommendations")
        for task_result in results.tasks_output:
            if task_result.agent == itinerary_planner.role:
                st.markdown(task_result.raw)
            if task_result.agent == local_expert.role and st.session_state.get('question'): #Use session
                st.subheader("Local Expert's Answer:")
                st.markdown(task_result.raw)

def display_thought_process(captured_output):
    """Displays the captured agent thought process."""
    with st.expander("Agent Thought Process (unformatted)"):
        st.text(captured_output.getvalue())

def initialize_session_state():
    """
    Initialize the session state with default values if they are not already set.
    """
    if "query_count" not in st.session_state:
        st.session_state['query_count'] = 0
        st.session_state['submit_disabled'] = False

def manage_query_count():
    """
    Manages the query count in the session state.

    If the query count reaches or exceeds 2, a warning message is displayed,
    and the submit button is disabled. Otherwise, the query count is incremented
    by 1, and the submit button remains enabled.
    """
    if st.session_state['query_count'] >= 2:
        st.warning("You have reached the limit of 2 queries. Please try again later.")
        st.session_state['submit_disabled'] = True
    else:
        st.session_state['query_count'] += 1
        st.session_state['submit_disabled'] = False

def create_app():
    """
    Creates a Streamlit application for exploring PDFs conversationally.
    """
    st.title("Travel Itinerary Planner using AI agents")
    st.write("")
    st.markdown("""
        This app creates a personalized travel itinerary based on your destination, dates, and interests.
        It uses a team of AI agents (powered by CrewAI and OpenAI) to research attractions, plan a daily schedule,
        and even answer questions like a local expert!
                """)
    st.write("")

def generate_image(destination):
    """Generates an image using DALL-E 3 based on the destination."""
    try:
        client = OpenAI()  # Use the OpenAI client
        response = client.images.generate(
            model="dall-e-2",
            prompt=f"A wide, panoramic, vibrant view of {destination}, showcasing its most iconic and beautiful features.  High quality, suitable for a travel website banner.",
            size="1024x1024",  # Or other supported sizes
            quality="standard",  # Or "hd" for higher quality (more expensive)
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None
    
def main():
    """Main function to run the Streamlit app."""

    load_environment_variables()
    create_app()
    initialize_session_state()

    destination, start_date, end_date, interests, question = get_user_inputs()
    st.session_state['question'] = question #store in session

    if st.button("Plan Itinerary"):
        manage_query_count()
        if not st.session_state['submit_disabled']:
            if destination and start_date and end_date:
                with st.spinner("Planning your itinerary..."):
                    image_url = generate_image(destination)
                    if image_url:
                        st.image(image_url, caption=f"Image of {destination}")

                    captured_output = io.StringIO()
                    with contextlib.redirect_stdout(captured_output):
                        results = run_crew(destination, start_date, end_date, interests, question)

                    display_results(results)
                    display_thought_process(captured_output)
            else:
                st.warning("Please fill in the destination and dates.")

if __name__ == "__main__":
    main()
