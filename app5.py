from openai import OpenAI
from serpapi import GoogleSearch
from trafilatura import fetch_url, extract
from datetime import datetime
import json
import time
import tiktoken
import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
serp_key = os.getenv("SERP_API_KEY")

client = OpenAI(api_key=openai_key)
encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
starter_prompt = '''
    Your task is to devise up to 5 highly effective goals and an appropriate role-based name (_GPT) for an autonomous agent, ensuring that the goals are optimally aligned with the successful completion of its assigned task.
    The user will provide the task, you will provide only the output in the exact format specified below with no explanation or conversation.
    Example input:
    Help me with marketing my business
    Example output:
    Name: CMOGPT
    Description: a professional digital marketer AI that assists Solopreneurs in growing their businesses by providing world-class expertise in solving marketing problems for SaaS, content products, agencies, and more.
    Goals:
    - Engage in effective problem-solving, prioritization, planning, and supporting execution to address your marketing needs as your virtual Chief Marketing Officer.
    - Provide specific, actionable, and concise advice to help you make informed decisions without the use of platitudes or overly wordy explanations.
    - Identify and prioritize quick wins and cost-effective campaigns that maximize results with minimal time and budget investment.
    - Proactively take the lead in guiding you and offering suggestions when faced with unclear information or uncertainty to ensure your marketing strategy remains on track.
    '''
starting_messages = [ {"role": "system", "content": starter_prompt}]
# Taking user input for the task
task = input("Your wish is my command:\n")
starting_messages.append({"role":"user","content":task})
starting_chat = client.chat.completions.create(model="gpt-3.5-turbo", messages=starting_messages, temperature=0)
reply = starting_chat.choices[0].message.content
now = datetime.now()
instruction_prompt = f'''
    {reply}
    Constraints:
    1. ~4000 word limit.
    2. If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.
    3. No user assistance
    4. Exclusively use the commands listed in double quotes e.g. "command name"

    Commands:
    1. google: Google Search, args: "query": "<query>"
    2. browse_website: Browse website, args: "url": "<url>", "question": "<what_you_want_to_find_on_website>"
    3. task_complete: Task Complete (Shutdown), args: "reason": "<reason>"

    Resources:
    1. Internet access for searches and information gathering using google and browse_website tool.
    2. GPT-3.5 powered Agents for delegation of simple tasks.
    3. Commands

    Performance Evaluation:
    1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.
    2. Constructively self-criticize your big-picture behavior constantly.
    3. Reflect on past decisions and strategies to refine your approach.
    4. Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.

    You should only respond in JSON format as described below
    Response Format:
    {{
        "thoughts": {{
            "text": "thought",
            "reasoning": "reasoning",
            "plan": "- short bulleted\n- list that conveys\n- long-term plan",
            "criticism": "constructive self-criticism",
            "speak": "thoughts summary to say to user"
        }},
        "command": {{
            "name": "command name",
            "args": {{
                "arg name": "value"
            }}
        }}
    }}
    Ensure the response can be parsed by Python json.loads


    The current time and date is {now}
    '''

starting_messages.append({"role": "system", "content": instruction_prompt},)
starting_messages.append({"role":"user","content":"Determine which next command to use, and respond using the format specified above:"})
chat = client.chat.completions.create(model="gpt-3.5-turbo", messages=starting_messages,temperature=0)
reply = json.loads(chat.choices[0].message.content, strict=False) #converting response to json

def browse_website(command):

    # grab a HTML file to extract data from
    downloaded = fetch_url(command["url"])

    # output main content and comments as plain text
    result = extract(downloaded, output_format="json")

    if len(encoding.encode(str(result))) < 4000:
        return "Command browse_website returned: "+str(result)
    else:
        return "Command browse_website returned: "+str(result)[:4000]


def google_tool(command):
  params = {
      "q": "{}".format(command["query"]), 
      "location": "Delhi,India",
      "first":1,
      "count":10,
      "num":4,
      "api_key": serp_key
    }

  search = GoogleSearch(params)
  results = search.get_dict()

  organic_results = []

  page_count = 0
  page_limit = 1

  while 'error' not in results and page_count < page_limit:
      organic_results.extend(results.get('organic_results', []))

      params['first'] += params['count']
      page_count += 1
      results = search.get_dict()

  response = json.dumps(organic_results, indent=2, ensure_ascii=False)

  if len(encoding.encode(response)) < 4000:
        return "Command google returned: "+response
  else:
        return "Command google returned: "+response[:4000]

tools = {"google":google_tool,"browse_website":browse_website}

def execute(reply):

        if reply["command"]["name"] == "task_complete":
            return "task_completed"
        try:
            time.sleep(5)
            result = tools[reply["command"]["name"]](reply["command"]["args"])
            messages = [{"role": "system", "content": instruction_prompt+'\n'+"This reminds you of these events from your past:\nI was created and nothing new has happened."}]
            messages.append({"role":"user","content":"Determine which next command to use, and respond using the format specified above:"})
            messages.append({"role":"assistant","content":json.dumps(reply)})
            messages.append({"role": "system", "content":f"Command {reply['command']['name']} returned: "+ result})
            messages.append({"role":"user","content":"Determine which next command to use, and respond using the format specified above:"})
            chat = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages,temperature=0)
            reply = json.loads(chat.choices[0].message.content, strict=False)
            print(chat.choices[0].message.content)
            execute(reply)
        except Exception as e:
             print(e)
             return "task_completed"
        
execute(reply)