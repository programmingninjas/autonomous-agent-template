from openai import OpenAI
from serpapi import GoogleSearch
from trafilatura import fetch_url, extract
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
serp_key = os.getenv("SERP_API_KEY")

client = OpenAI(api_key=openai_key)
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
    1. Internet access for searches and information gathering.
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

print(instruction_prompt)
