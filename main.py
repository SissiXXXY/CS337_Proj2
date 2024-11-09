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

# Main Flow
url = "https://www.allrecipes.com/recipe/218091/classic-and-simple-meat-lasagna/"
html = fetch_url(url)
parse_recipe(html)
