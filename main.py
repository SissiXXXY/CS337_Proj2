import urllib.request
import re
import json
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Initialize Slack Bolt app
app = App(token="xoxb-8035210513302-8041742658787-Srg5e71VY5EuipjrYpX8saZi")

# Recipe Structure
recipe = {
    "title": "",
    "description": "",
    "ingredients": [],
    "steps": [],
}

COMMON_TOOLS = [
    "pan", "skillet", "grater", "whisk", "knife", "spatula", "bowl",
    "oven", "mixer", "peeler", "measuring cup", "blender", "microwave",
    "cutting board", "tongs", "pressure cooker", "baking sheet"
]

current_step = 0  # Track the current step in the conversation

# URL Fetching
def fetch_url(url):
    try:
        print(f"Fetching URL: {url}")
        # remove any trailing characters after the URL - from slack
        print(url.strip('>'))
        url = url.strip('>')
        # now good to fetch the URL
        print(f"Fetching URL: {url}")
        response = urllib.request.urlopen(url)
        data = response.read()
        html = data.decode("utf-8")
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""
    return html

def parse_recipe(html):
    title = re.search(r"<title>(.*?)</title>", html)

    findjson = re.search(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if findjson:
        try:
            jsondata = json.loads(findjson.group(1))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return False
    else:
        print("JSON-LD not found in the HTML.")
        return False

    if isinstance(jsondata, list):
        jsondata = jsondata[0] if jsondata else {}

    recipe["title"] = title.group(1) if title else "Unknown Title"
    des = re.search(r'<meta name="description" content="(.*?)"', html)
    recipe["description"] = des.group(1) if des else "No description available"
    recipe["ingredients"] = jsondata.get("recipeIngredient", [])
    recipe["steps"] = [step["text"] for step in jsondata.get("recipeInstructions", [])]


    tools_found = set()
    for step in recipe["steps"]:
        for tool in COMMON_TOOLS:
            if re.search(rf"\b{tool}\b", step, re.IGNORECASE):
                tools_found.add(tool)
    recipe["tools"] = list(tools_found) 
    return True

def handle_user_input(user_input):
    global current_step
    user_input = user_input.lower().strip()

    if user_input == "1" or "ingredients" in user_input:
        return "Here are the ingredients for \"" + recipe["title"] + "\":\n" + "\n".join(recipe["ingredients"])

    elif user_input == "2" or "steps" in user_input:
        current_step = 0
        return f"Step 1: {recipe['steps'][0]}"

    elif "next" in user_input or "continue" in user_input:
        if current_step < len(recipe["steps"]) - 1:
            current_step += 1
            return f"Step {current_step + 1}: {recipe['steps'][current_step]}"
        return "That was the last step!"

    elif "previous" in user_input or "back" in user_input:
        if current_step > 0:
            current_step -= 1
            return f"Step {current_step + 1}: {recipe['steps'][current_step]}"
        return "You're already at the first step!"

    

    elif "repeat" in user_input:
        if "step" not in user_input:
            if recipe["steps"]:
                return f"Step {current_step + 1}: {recipe['steps'][current_step]}"
            return "No recipe loaded yet."

        step_number = re.search(r"\d+", user_input)
        if step_number:
            step_number = int(step_number.group())
            if 1 <= step_number <= len(recipe["steps"]):
                return f"Step {step_number}: {recipe['steps'][step_number - 1]}"
            return f"Step {step_number} is out of range. There are only {len(recipe['steps'])} steps."
        
        return "I didn't understand the step number."
    elif "step" in user_input:
        step_number = re.search(r"\d+", user_input)
        if step_number:
            step_number = int(step_number.group())
            if 1 <= step_number <= len(recipe["steps"]):
                current_step = step_number - 1
                return f"Step {step_number}: {recipe['steps'][current_step]}"
            return f"Step {step_number} is out of range. There are only {len(recipe['steps'])} steps."
        return "I didn't understand the step number."

    elif "how do i" in user_input or "how to" in user_input:
        search_term = user_input.replace("how do i", "").replace("how to", "").strip()
        return f"Here's a video that might help: https://www.youtube.com/results?search_query=how+to+{search_term.replace(' ', '+')}"

    elif "what is" in user_input:
        search_term = user_input.replace("what is", "").strip()
        return f"Here's some information: https://www.google.com/search?q={search_term.replace(' ', '+')}"

    elif "how long" in user_input or "time" in user_input:
        curr_step = recipe["steps"][current_step]
        # print(curr_step)
    
        match = re.search(r"(\d+)\s?(minutes?|seconds?)", curr_step, re.IGNORECASE)
        
        if match:
            time_info = match.group(0)
            # print(time_info)
            return f"The time is: {time_info}"
        else:
            return "No time is mentioned in this step."

    elif "what can i use instead of" in user_input:
        ingredient = user_input.replace("what can i use instead of", "").strip()
        # print(ingredient)
        if ingredient:
            search_url = f"https://www.google.com/search?q=alternatives+to+{ingredient.replace(' ', '+')}"
            return f"Here's suggestions for alternatives to {ingredient}: {search_url}"
        else:
            return "Please specify an ingredient you'd like to substitute."


    elif "what temperature" in user_input or "temperature" in user_input:
        cur_step = recipe["steps"][current_step]
        # print(cur_step)
        
        match = re.search(r"(\d{2,})\s?degrees", cur_step, re.IGNORECASE)
        
        if match:
            temperature_info = match.group(0)
            return f"The temperature is {temperature_info}"
        else:
            for index, step in enumerate(recipe["steps"]):
                match = re.search(r"(\d{2,})\s?degrees", step, re.IGNORECASE)
                if match:
                    temperature_info = match.group(0)
                    # step_context = step.strip()
                    return (f"No temperature is mentioned in this step, "
                        f"but Step {index + 1} says: {temperature_info} ")
            return "No temperature is mentioned in this recipe."
    elif "tools" in user_input:
        if recipe.get("tools"):
            return f"The tools needed for this recipe are:\n" + ", ".join(recipe["tools"])
        return "No specific tools are mentioned in this recipe."

    elif "when is it done" in user_input:
        curr_step = recipe["steps"][current_step]
        # print(curr_step)
        
        sentences = re.split(r'\.|\?|\!', curr_step)
        last_sentence = sentences[-2].strip() if len(sentences) > 1 else curr_step.strip()

        trigger_keywords = [r"until\s.*$", r"when\s.*$", r"after\s.*$", r"then\s.*$"]
        completion_keywords = r"(done|brown|tender|cooked|ready|through|combined|crumbly)"
        
        for trigger in trigger_keywords:
            trigger_match = re.search(trigger, last_sentence, re.IGNORECASE)
            if trigger_match:
                condition = trigger_match.group().strip() 
                condition = re.sub(r'^(until|when|after|then)\s+', '', condition, flags=re.IGNORECASE)

                for separator in [',', ';', '-']:
                    if separator in condition:
                        parts = condition.split(separator)
                        for part in parts[1:]:
                            if re.search(completion_keywords, part, re.IGNORECASE):
                                break
                        else:
                            condition = parts[0].strip()

                return f"This step is done when {condition}."
        state_match = re.search(completion_keywords, last_sentence, re.IGNORECASE)
        if state_match:
            state = state_match.group().strip()

            for separator in [',', ';', '-']:
                if separator in last_sentence:
                    parts = last_sentence.split(separator)
                    for part in parts[1:]:
                        if re.search(completion_keywords, part, re.IGNORECASE):
                            break
                    else:
                        last_sentence = parts[0].strip()

            return f"This step is done when {state}."

        return "I couldn't find any indicators for when it's done at this step. Refer to other steps."
            
    #     # completion_match = re.search(r"(until\s.*?(done|brown|tender|cooked|ready|through))", curr_step, re.IGNORECASE)
    #     # if completion_match:
    #     #     completion_info = completion_match.group(1).strip()
            
    #     #     completion_info = completion_info.replace("until", "").strip()
    #     #     completion_info = completion_info[0] + completion_info[1:]
            
    #     # return f"This step is done when {completion_info}."

    #     return "I couldn't find any indicators for when it's done at this step. Refer to other steps."



    return "I don't understand. You can:\n1. View ingredients\n2. Go through steps\n- Say 'next' or 'previous' to navigate steps\n- Ask 'how do I...' or 'what is...'"

def process_url(url, say):
    """Helper function to process URLs and return appropriate messages"""
    html = fetch_url(url)
    if html and parse_recipe(html):
        recipe_loaded_message = (
            f"Loaded recipe: {recipe['title']}\n"
            f"What would you like to do?\n"
            f"[1] See ingredients list\n"
            f"[2] Start cooking (go through steps)"
        )
        say(recipe_loaded_message)
        return True
    else:
        say("Sorry, I couldn't parse that recipe. Make sure it's from AllRecipes.com")
        return False

# Dictionary to track if welcome message has been sent to a channel
channel_welcomed = {}

@app.event("app_mention")
def mention_handler(event, say):
    channel_id = event["channel"]
    text = event["text"].lower()
    
    # Send welcome message if this is the first interaction in the channel
    if channel_id not in channel_welcomed:
        welcome_message = "Welcome to Recipe Helper!\nTo get started, share an AllRecipes URL or say 'fetch' followed by the URL."
        say(welcome_message)
        channel_welcomed[channel_id] = True
        
        # Check if URL is already included in the first message
        url_match = re.search(r"https?://[^\s]+", text)
        if url_match:

            url = url_match.group(0)
            process_url(url, say)
        return

    # Check for URL in the message
    url_match = re.search(r"https?://[^\s]+", text)
    if url_match:
        url = url_match.group(0)
        process_url(url, say)
    else:
        # Only handle other commands if no URL is present
        response = handle_user_input(text)
        say(response)

def conversational_interface():
    print("Welcome to Recipe Helper!")
    print("You can:")
    print("1. Use the command line interface")
    print("2. Start the Slack bot")
    choice = input("Enter your choice (1 or 2): ")

    if choice == "1":
        # Command line interface
        url = input("Please enter an AllRecipes URL (or press Enter for default recipe): ")
        
        if not url:
            url = "https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/"
        
        html = fetch_url(url)
        if html and parse_recipe(html):
            print(f"\nLoaded recipe: {recipe['title']}")
            print("\nWhat would you like to do?")
            print("[1] See ingredients list")
            print("[2] Start cooking (go through steps)")
            
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break
                    
                response = handle_user_input(user_input)
                print("\nBot:", response)
        else:
            print("Error loading recipe. Please try again.")

    elif choice == "2":
        # Start Slack bot
        print("Starting Slack bot...")
        handler = SocketModeHandler(app, "xapp-1-A080T8KTBEK-8044350362004-85927f8b944de02ed402c8241e77c111fe2cd96da586e229f9bb67f5da770933")
        handler.start()
    else:
        print("Invalid choice. Please try again.")

if __name__ == "__main__":
    conversational_interface()