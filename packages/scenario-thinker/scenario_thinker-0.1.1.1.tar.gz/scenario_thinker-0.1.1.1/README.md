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

Start server with flask run and and start working with your scenario.
