from flask import Flask, make_response, json, send_from_directory
from flask_cors import CORS  # Import CORS
# from services.chatgpt_service import create_request
# from services.dummy_chatgpt_service import DummyChatGptService
# from services.ollama_service import OllamaService
# from services.chatgpt_service import ChatGptService
from services.database import Database
import os
import json
from services.scenario_creator import ScenarioCreator
# from parse_scenario import parse
app = Flask(__name__)
CORS(app, expose_headers=["Content-Disposition"])  # Enable CORS for all routes and origins

from flask import request
import time

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# @app.post("/upload")
# def test():

#     file = request.files["file"]
#     filename = file.filename.split(".")[0]

#     file_insides = file.read()

#     response = create_request(file_insides)
#     with open('temp.py', 'w') as f:
#         f.write(response)
#     return send_from_directory(".", "temp.py", as_attachment=True, download_name=f"{filename}.py")

kekw = 0
@app.post("/get_scenario")
def test2():
    # global kekw
    # print()

    # file_content = dict(request.get_json()).get("input_data")
    # json_data = parse(file_content)
    llm_type = dict(request.get_json()).get("llm_type")
    result, error = ScenarioCreator(llm_type).get_response(dict(request.get_json()).get("input_data"))
    print(result)
    print(error)
    # result = OllamaService().get_response(dict(request.get_json()).get("input_data"))
    # result = OllamaService().get_response(dict(request.get_json()).get("input_data"))
    return [result, error]
#     kekw = 0
#     for i in range(4):
#         time.sleep(1)
#         kekw = kekw + 1
#     return """from behave import *
# @given('we have behave installed')
# def step_impl(context):
#     pass

# @when('we implement a test')
# def step_impl(context):
#     assert True is not False

# @then('behave will test it for us!')
# def step_impl(context):
#     assert context.failed is False"""
@app.get("/get_methods")
def get_methods():
    database = Database()
    return database.get_all_actions()


@app.post("/add_method")
def add_method():
    value_from_request = request.get_json()
    database = Database()
    result = database.insert_into_table(value_from_request["command"], value_from_request["python_script"])
    if result is False:
        return "result", 503
    else:
        return "result", 200

@app.patch("/update_method/<id>")
def update_method(id):
    value_from_request = request.get_json()
    database = Database()
    print(value_from_request["command"], value_from_request["python_script"])
    result = database.update_by_rowid(id, value_from_request["command"], value_from_request["python_script"])
    if result is False:
        return "result", 503
    else:
        return "result", 200


@app.delete("/delete_method/<id>")
def delete_method(id):
    database = Database()

    if database.delete_by_rowid(id) is False:
        return "result", 503

    return "result", 200

@app.delete("/delete_all_methods")
def delete_all_methods():
    database = Database()

    if database.destroy_table() is False:
        return "result", 503

    return "result", 200

@app.get("/which_line_now")
def line():
    return f"{kekw}"