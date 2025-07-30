# Scenario Thinker
BDD and AI combined - generate yourself Python scripts in selenium using BDD scenarios.

# Setup
Before all, the best approach would be to make virtual environment:
```bash
python3 -m venv venv
```

After installing this library,
you can initialize all the files:
```bash
st_prepare
```

This will create flask server code in your project location. Also it will copy view for interacting with generating code itself, view for controlling generated 
and their styles and js scripts for them + .env file . It's highly recommended to not change them, unless you know what you're doing. 



Add .env file

Add there token from AI ML API like this:
AI_ML_API_VALUE = "xxx"


Start server with `flask run` and and start working with your scenario. Open file in generated `views` that means views/index.html and put there scenario feature. 
Scenario feature should look like this
```feature
 Feature: showing off behave
Scenario: run a simple test
Given visiting site localhost:3000/button_with_redirect
When I click button with text "Go to my favorites"
Then I will be redirected into site localhost:3000/my_favourites
```
After that, start program and hope for the best. 