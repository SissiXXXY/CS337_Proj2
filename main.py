import urllib.request
import re
import json


# URL Fetching
def fetch_url(url):
    try:
        response = urllib.request.urlopen(url)
        data = response.read()
        html = data.decode("utf-8")
        # plese do not remove the following comments.
        # openfile = open("recipe.html", "w")
        # openfile.write(html)
        # openfile.close()
        # print(html)
    except:
        print("Error fetching URL")
    return html


# Recipe Structure
recipe = {
    "title": "",
    "description": "",
    "ingredients": [],  # List of ingredients
    "steps": [],  # List of steps
}


def parse_recipe(html):
    title = re.search(r"<title>(.*?)</title>", html)
    # print(title.group(1))

    findjson = re.search(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if findjson:
        try:
            jsondata = json.loads(findjson.group(1))
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return
    else:
        print("JSON-LD not found in the HTML.")
        return

    if isinstance(jsondata, list):
        jsondata = jsondata[0] if jsondata else {}

    recipe["title"] = title.group(1)
    des = re.search(r'<meta name="description" content="(.*?)"', html)
    # print(des.group(1))
    recipe["description"] = des.group(1)
    ingredients = jsondata.get("recipeIngredient", [])
    recipe["ingredients"] = ingredients
    # print(ingredients)
    steps = []
    for step in jsondata["recipeInstructions"]:
        steps.append(step["text"])
    recipe["steps"] = steps
    # print(steps)
    print(recipe)


# Conversational Interface
def handle_user_input(user_input):
    global current_step
    user_input = user_input.lower().strip()
    
    if user_input == "1" or "ingredients" in user_input:
        # come up with a bunch of different ways they could ask for ingredients...
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

    # take me to the nth step:
    elif "step" in user_input:
        step_number = re.search(r"\d+", user_input)
        if step_number:
            step_number = int(step_number.group())
            if 1 <= step_number <= len(recipe["steps"]):
                current_step = step_number - 1  # Adjust to 0-based index (internally)
                return f"Step {step_number}: {recipe['steps'][current_step]}"  # Display the step number from user input
            return f"Step {step_number} is out of range. There are only {len(recipe['steps'])} steps."
        return "I didn't understand the step number."

    # if repeat in there just repeat the current step
    elif "repeat" in user_input:
        return f"Step {current_step + 1}: {recipe['steps'][current_step]}"
    
    # needs to have the part about "how do i do that" instead of just how do i ___. will need multiple phrasings for "that" and reference the step before
    elif "how do i" in user_input or "how to" in user_input:
        search_term = user_input.replace("how do i", "").replace("how to", "").strip()
        return f"Here's a video that might help: https://www.youtube.com/results?search_query=how+to+{search_term.replace(' ', '+')}"
        
    elif "what is" in user_input:
        search_term = user_input.replace("what is", "").strip()
        return f"Here's some information: https://www.google.com/search?q={search_term.replace(' ', '+')}"
        
    return "I don't understand. You can:\n1. View ingredients\n2. Go through steps\n- Say 'next' or 'previous' to navigate steps\n- Ask 'how do I...' or 'what is...'"

def conversational_interface():
    print("Welcome to Recipe Helper!")
    url = input("Please enter an AllRecipes URL (or press Enter for default recipe): ")
    
    if not url:
        url = "https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/"
    
    html = fetch_url(url)
    parse_recipe(html)
    
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

if __name__ == "__main__":
    conversational_interface()
