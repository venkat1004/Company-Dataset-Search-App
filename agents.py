import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

# Ensure the environment variables are set correctly
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "6f7bfe9f5e2ff59fc6dcb5d05af59ed4b2667fee")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "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")

# Initialize the search tool for web browsing
search_tool = SerperDevTool()

# Define the Research Agent
research_agent = Agent(
    role="Industry Researcher",
    goal="Research the company and its industry to gather strategic focus, key offerings, and product vision.",
    backstory="""You are a Research Agent tasked with gathering and analyzing information on the company's industry, 
                key offerings, and strategic focus areas.""",
    verbose=True,
    llm="groq/llama-3.2-90b-vision-preview"
)

# Define a Use Case Generator Agent
use_case_agent = Agent(
    role="Use Case Developer",
    goal="Create innovative and diverse use cases for the company based on the research findings.",
    backstory="""You are a Use Case Developer tasked with using research findings to create tailored and actionable 
                use cases for the company that align with their strategic focus and market opportunities.""",
    verbose=True,
    llm="groq/llama-3.2-90b-vision-preview"
)

# Define the Dataset Searcher Agent
dataset_searcher_agent = Agent(
    role="Dataset Searcher",
    goal="Search for relevant datasets based on the use cases generated for the company.",
    backstory="""You are tasked with searching for datasets that match the company's industry, market focus, 
                and strategic goals, based on the use cases generated by the Use Case Developer.""",
    verbose=True,
    llm="groq/llama-3.2-90b-vision-preview"
)

def research_task(company):
    """
    Perform research for a given company using the research agent.
    """
    print(f"Performing research for {company}...")

    research_task = Task(
        description=f"Research industry trends and strategic focus for {company}.",
        expected_output="Industry trends, key offerings, and strategic focus.",
        agent=research_agent
    )

    my_crew = Crew(agents=[research_agent], tasks=[research_task])

    try:
        print(f"Starting research task for {company}...")
        results = my_crew.kickoff(inputs={"company": company})

        # Process and debug research results
        research_results = (
            getattr(results, "output", None) or str(results) or "No data available."
        )
        print(f"Research task completed. Results for {company}: {research_results}")

        return research_results

    except Exception as e:
        print(f"Error occurred during research: {str(e)}. Verify API keys and inputs.")
        return None


def generate_use_cases(company, research_results=None):
    """
    Generate use cases based on research results using the use case agent.
    """
    if not research_results or research_results == "No data available.":
        print("Invalid or empty research results. Use case generation skipped.")
        return

    # Debug: Check the research results being passed to the use case agent
    print(f"Research results passed to use case generation: {research_results}")

    # If the research results are not structured, try parsing or structuring them
    structured_input = {
        "company": company,
        "industry_trends": research_results  # Adjust based on actual structure of results
    }

    use_case_task = Task(
        description=f"Create innovative use cases for {company} based on the research findings.",
        expected_output="List of actionable and strategic use cases.",
        agent=use_case_agent
    )

    my_crew = Crew(agents=[use_case_agent], tasks=[use_case_task])

    try:
        print(f"Starting use case generation task for {company}...")
        results = my_crew.kickoff(inputs=structured_input)

        # Debug: Print the entire results object to understand its structure
        print(f"Raw use case results: {results}")

        # Enhance output processing: check if the result is a list or dictionary and handle accordingly
        if hasattr(results, 'output'):
            if isinstance(results.output, list):
                use_case_results = "\n".join(results.output)  # Join list into a readable string
            else:
                use_case_results = results.output
        elif isinstance(results, dict) and 'output' in results:
            if isinstance(results['output'], list):
                use_case_results = "\n".join(results['output'])
            else:
                use_case_results = results['output']
        else:
            use_case_results = str(results)  # If all else fails, return the result as a string

        # Debug: Check if the results are now structured properly
        print(f"Use case generation completed. Results for {company}: {use_case_results}")

        return use_case_results

    except Exception as e:
        print(f"Error occurred during use case generation: {str(e)}. Verify API inputs and configurations.")


def search_datasets_based_on_use_cases(use_case_results, company):
    """
    Search for relevant datasets based on the generated use cases for the company.
    Dynamically adjust search terms based on the company name.
    """
    # Initialize the search tool for web browsing
    search_tool = SerperDevTool()  # Ensure search_tool is initialized properly

    # Extract relevant search terms based on use case results
    search_terms = []

    # Example: Using search terms based on the company
    if "sports" in use_case_results or "fitness" in use_case_results:
        search_terms = [f"{company} sports performance", f"{company} athletic data", f"{company} fitness datasets"]
    elif "fashion" in use_case_results or "apparel" in use_case_results:
        search_terms = [f"{company} fashion trends", f"{company} clothing datasets", f"{company} apparel sales"]
    elif "customer behavior" in use_case_results:
        search_terms = [f"{company} customer behavior", f"{company} purchasing patterns", f"{company} consumer data"]
    else:
        # Fallback search terms for general use cases
        search_terms = [f"{company} market trends", f"{company} sales data", f"{company} supply chain datasets"]

    # Now search using the SerperDevTool
    search_results = {}

    for term in search_terms:
        print(f"Searching for: {term}")
        # Perform the search using the 'run' method from SerperDevTool
        results = search_tool.run(search_query=f"{term} site:kaggle.com")

        # Debugging: print the results to check its structure
        print(f"Results for '{term}': {results}")

        search_results[term] = results

    # Processing the results into markdown format
    markdown_results = "### Relevant Datasets\n\n"
    for term, results in search_results.items():
        markdown_results += f"### Search Term: {term}\n"
        
        if isinstance(results, list):
            for result in results:
                if isinstance(result, dict):  # Check if it's a dictionary with 'title' and 'url'
                    markdown_results += f"* [{result.get('title', 'No Title')}]({result.get('url', '#')}) - {result.get('snippet', 'No Snippet')}\n"
                else:  # Handle case where result is a string (e.g., a URL or text snippet)
                    markdown_results += f"* {result}\n"
        else:
            markdown_results += f"* {results}\n"

    # Save the results to a file with UTF-8 encoding
    with open("relevant_datasets.md", "w", encoding="utf-8") as file:
        file.write(markdown_results)

    print("Dataset search completed. Relevant datasets saved in 'relevant_datasets.md'.")

    # Return a success message
    return "Relevant datasets have been saved in 'relevant_datasets.md'."
