from therix.core.prompt import Prompt



variables = {
    "history": "User asked about product building",
    "input": "I want to build a new app.",
    "todays_date": "2024-07-10",
    "current_time": "10:00 AM",
    "calendar": "List of booked events",
    "working_hours_start": "9:00 AM",
    "working_hours_end": "6:00 PM"
}

prompt = Prompt.get_prompt("chatbot", variables=variables)
print(prompt)
