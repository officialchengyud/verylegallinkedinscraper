from app import MainAgent

basic_info = {
    "first_name": "John",
    "last_name": "Doe",
    "company": "Tech Corp",
    "role": "Developer",
    "industry": "Software",
    "city": "New York",
    "country": "USA",
}

agent = MainAgent(basic_info)

while True:
    print("--------------------------------------------")
    input_text = input("You: ")
    response = agent.handle_input({"text": input_text})
    print("Agent:", response["text"])