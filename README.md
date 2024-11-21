# CS337_Proj2
Northwestern CS337 Proj2 - Recipes and Conversational Interaction


## Question Answering Goals and Examples

### 1. **Retrieve/Display Recipe Details** m
- **Q:** "Show me the ingredients list."
- **A:** A list of ingredients with quantities and measurements


### 2. **Navigation Utterances**
- **Q:** "Go to the next step."
- **A:** The bot advances to the next step


- **Q:** "Repeat this step."
- **A:** The bot repeats the current step


- **Q:** "Take me to the 3rd step."
- **A:** The bot displays the specified step 


### 3. **Ask About Parameters of the Current Step**
- **Q:** "How long do I mix?"
- **A:** The bot identifies the time in the current step, e.g., Mix for 5 minutes.

- **Q:** "What temperature?"
- **A:** The bot retrieves the temperature mentioned in the step or the recipe, e.g., The temperature is: 350 degrees F.


- **Q:** "What can I use instead of butter?"
- **A:** The bot suggests alternatives based on the query, e.g., Here's suggestions for alternatives to butter: https://www.google.com/search?q=alternatives+to+butter



### 4. **"When is it done?"**
- **Q:** "When is it done?"
- **A:** The bot determines completion indicators based on the last sentence of the step:
- **Example:**
  - Step: `"Mix until thoroughly combined; ready to serve."`
  - Response: `"It is done when it is thoroughly combined."`


### 5. **Simple "What is" Questions**
- **Q:** "What is a whisk?"
- **A:** The bot provides directs the user to more information, e.g., Here's some information: https://www.google.com/search?q=whisk