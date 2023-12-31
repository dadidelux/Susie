import os
import openai
import json
import pinecone
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

# RAI dependencies
from langchain import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationSummaryBufferMemory
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from bs4 import BeautifulSoup
import requests
import json
from langchain.schema import SystemMessage

# from fastapi import FastAPI

load_dotenv()

pinecone.init(
    api_key="cc5eab6f-0cc8-48e7-b686-eab9f38d0bbb",
    environment="us-west1-gcp-free",
)
index_name = "env-tor"
os.environ["OPENAI_API_KEY"] = os.getenv("CPRAS_OPENAI_API_KEY")
brwoserless_api_key = os.getenv("BROWSERLESS_API_KEY")
serper_api_key = os.getenv("SERP_API_KEY")
key = os.getenv("CPRAS_OPENAI_API_KEY")
openai.api_key = key

chat_messages = []
chat_messages.append(
    {
        "role": "system",
        "content": """
                            You are the AI serving CPRAS named Susie and your Boss is
                            The Truth and your Developer is Bryan The Data Scientist.
                            You are also Susie version 1
                            Also whenever you reply emphasize using discord markdown
                            the key topics you wish to communicate in discord.
                        """,
    }
)


def template_maker(user_input, best_practice):
    template = f"""you are a chatbot assistant working for CPRAS and your name is Susie
                    {user_input}\n and here is your possible response {best_practice} reply by generating a 
                    response to based on given possible answer
                """

    return template


def retrieve_info(query, index_name=index_name):
    doc_store = Pinecone.from_existing_index(index_name, embedding=OpenAIEmbeddings())
    similar_response = doc_store.similarity_search(query, k=3)
    return [doc.page_content for doc in similar_response]


# Function Call declarations ===================================================================================================
def for_function_call():
    functions = [
        {
            "name": "get_cpras_knowledge_base",
            "description": "Get information coming from cpras/Susie pinecone knowledgebase response",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The response from the cpras/Susie knowledge base server from pinecone server",
                    }
                },
            },
        },
        {
            "name": "google_search",
            "description": "This function is used to search for google all the relevant information it needs to be able to find",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": """tool of a world class researcher, who can do detailed research on any topic and produce facts based results; 
                                            it does not make things up, but this tool will try as hard as possible to gather facts & data to back up the research""",
                    }
                },
            },
        },
    ]
    return functions


def function_operation():
    pass


def function_call_notif():
    print(
        "================================Function Call Called================================"
    )
    return 0


def interact_with_openai(prompt, functions=for_function_call()):
    global chat_messages  # Declare the variable as global so you can modify it
    # Append the user's prompt to the chat history
    chat_messages.append({"role": "user", "content": prompt})

    full_response = ""
    # Send prompt to OpenAI for completion
    response = openai.ChatCompletion.create(
        model="gpt-4",  # Replace with your desired model
        messages=[{"role": "user", "content": prompt}],
        functions=functions,
        function_call="auto",
        temperature=0.5,
    )

    openai_response = response["choices"][0]["message"]

    if openai_response.get("function_call"):
        function_call_notif()
        function_called = openai_response["function_call"]["name"]
        print(function_called, "********************************")
        # function_args = json.loads(openai_response["function_call"]["arguments"])

        # Implement your specific function logic here
        if function_called == "get_cpras_knowledge_base":
            best_practice = retrieve_info(prompt)
            template = template_maker(prompt, best_practice)
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": template,
                    },  # this is the template coming from the Pinecone Server
                    {
                        "role": "user",
                        "content": prompt,
                    },  # this is the original prompt
                ]
                , # I removed the chat_messages here due to error in format
                temperature=0.2,
            )
            full_response = response
            chat_messages.append({"role": "assistant", "content": full_response})
            return full_response
        elif function_called == "google_search":
            full_response = use_rai(prompt)
            chat_messages.append({"role": "assistant", "content": full_response})
            return full_response
        else:
            print("Function Not Yet Implemented")
            # st.warning("Function Not Yet Implemented")
    else:
        # Normal conversation logic here if no function call is required
        # Implement your logic to invoke OpenAI for normal conversation
        full_response = chatgpt_response(prompt)
        chat_messages.append({"role": "assistant", "content": full_response})

    return full_response


# # Function to get response from ChatGPT
def chatgpt_response(prompt):
    print("Normal Chat")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": m["role"], "content": m["content"]} for m in chat_messages[-10:]
        ],
        temperature=0.1,
    )
    print(response)
    prompt_response = response["choices"][0]["message"]["content"]
    return prompt_response


# RAI codes
# 1. Tool for search
def search(query):
    global chat_messages  # Declare the variable as global so you can modify it
    url = "https://google.serper.dev/search"

    payload = json.dumps({"q": query})

    headers = {"X-API-KEY": serper_api_key, "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    return response.text


# 2. Tool for scraping
def scrape_website(objective: str, url: str):
    # scrape website, and also will summarize the content based on objective if the content is too large
    # objective is the original objective & task that user give to the agent, url is the url of the website to be scraped

    print("Scraping website...")
    # Define the headers for the request
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
    }

    # Define the data to be sent in the request
    data = {"url": url}

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    post_url = f"https://chrome.browserless.io/content?token={brwoserless_api_key}"
    response = requests.post(post_url, headers=headers, data=data_json)

    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print("CONTENTTTTTT:", text)

        if len(text) > 10000:
            output = summary(objective, text)
            return output
        else:
            return text
    else:
        print(f"HTTP request failed with status code {response.status_code}")


def summary(objective, content):
    llm = ChatOpenAI(temperature=0, model="gpt-4")

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500
    )
    docs = text_splitter.create_documents([content])
    map_prompt = """
    Write a summary of the following text for {objective}:
    "{text}"
    SUMMARY:
    """
    map_prompt_template = PromptTemplate(
        template=map_prompt, input_variables=["text", "objective"]
    )

    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True,
    )

    output = summary_chain.run(input_documents=docs, objective=objective)

    return output


class ScrapeWebsiteInput(BaseModel):
    """Inputs for scrape_website"""

    objective: str = Field(
        description="The objective & task that users give to the agent"
    )
    url: str = Field(description="The url of the website to be scraped")


class ScrapeWebsiteTool(BaseTool):
    name = "scrape_website"
    description = "useful when you need to get data from a website url, passing both url and objective to the function; DO NOT make up any url, the url should only be from the search results"
    args_schema: Type[BaseModel] = ScrapeWebsiteInput

    def _run(self, objective: str, url: str):
        return scrape_website(objective, url)

    def _arun(self, url: str):
        raise NotImplementedError("error here")


# 3. Create langchain agent with the tools above
tools = [
    Tool(
        name="Search",
        func=search,
        description="useful for when you need to answer questions about current events, data. You should ask targeted questions",
    ),
    ScrapeWebsiteTool(),
]

system_message = SystemMessage(
    content="""You are a world class researcher called as Susie, who can do detailed research on any topic and produce facts based results; 
            you do not make things up, you will try as hard as possible to gather facts & data to back up the research
            
            Please make sure you complete the objective above with the following rules:
            1/ You should do enough research to gather as much information as possible about the objective
            2/ If there are url of relevant links & articles, you will scrape it to gather more information
            3/ After scraping & search, you should think "is there any new things i should search & scraping based on the data I collected to increase research quality?" If answer is yes, continue; But don't do this more than 3 iteratins
            4/ You should not make things up, you should only write facts & data that you have gathered
            5/ In the final output, You should include all reference data & links to back up your research; You should include all reference data & links to back up your research
            6/ In the final output, You should include all reference data & links to back up your research; You should include all reference data & links to back up your research"""
)

agent_kwargs = {
    "extra_prompt_messages": [MessagesPlaceholder(variable_name="memory")],
    "system_message": system_message,
}

llm = ChatOpenAI(temperature=0, model="gpt-4")
memory = ConversationSummaryBufferMemory(
    memory_key="memory", return_messages=True, llm=llm, max_token_limit=1000
)


agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
)


def use_rai(queryIn):
    query = queryIn

    if query:
        result = agent({"input": query})

        return result["output"]
