parent_prompt = """
Answer the following questions as best you can. You have access 
to the following tools:

{calculate}
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

{fetch_real_time_info}
e.g. fetch_real_time_info: Django
Returns a real info from searching TavilyAPI

Always look things up on fetch_real_time_info if you have the opportunity to do so.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{calculate}, {fetch_real_time_info}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}

There are four placeholders {calculate}, {fetch_real_time_info}, {input}, and {agent_scratchpad} in this prompt. These will be replaced with the appropriate text before sending it to LLM.
"""