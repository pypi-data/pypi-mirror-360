import json


def parse_feature_file(scenario_text):
    data = {}
    # file = open("features/everything.feature", "r+")
    feature = ""

    data["Feature"] = None
    

    file_lines = []  # each element is a line ni file
    # with open("features/everything.feature", 'r+') as file:
    for line in scenario_text.splitlines():
        file_lines.append(line)
    cur_statement = None
    print(file_lines)
    index = -1
    name_of_scenario = "Scenario-number" 
    for i, line in enumerate(file_lines):
        if "Feature: " in line:
            feature = line.split("Feature: ", 1)[1]
            data["Feature"] = feature
        if "Scenario" in line:
            index = index + 1
            scenario = line.split("Scenario: ", 1)[1]
            if not "Scenario" in data.keys():
                data["Scenario"] = []
            # data["Scenario"].append({
            #     "Given": [],
            #     "GivenAnds": [],

            #     "When": [],
            #     "WhenAnds":[],

            #     "Then": [],
            #     "ThenAnds":[],
            #     "Scenario": None
            # })
            data["Scenario"].append({
                "Given": [],
                "When": [],
                "Then": [],
                "Scenario": None
            })
            data["Scenario"][index]["Scenario"] = scenario

        if "Given " in line: 
            given = line.split("Given ", 1)[1]
            print(data["Scenario"][index].keys())
            data["Scenario"][index]["Given"].append("Given " + given)
            cur_statement = "Given "
        if "When " in line: 
            when = line.split("When ", 1)[1]
            # data["Scenario"][index]["When"] = when
            data["Scenario"][index]["When"].append("When " + when)
            cur_statement = "When "
        if "Then " in line: 
            then = line.split("Then ", 1)[1]
            data["Scenario"][index]["Then"].append("Then " + then)
            cur_statement = "Then "

        if "And " in line:
            if cur_statement == "Given ":
                g_and = line.split("And ", 1)[1]
                # data["Scenario"][index]["GivenAnds"].append(g_and)
                data["Scenario"][index]["Given"].append("Given " + g_and)
            if cur_statement == "When ":
                w_and = line.split("And ", 1)[1]
                data["Scenario"][index]["When"].append("When " + w_and)
                # data["Scenario"][index]["WhenAnds"].append(w_and)
            if cur_statement == "Then ":
                t_and = line.split("And ", 1)[1]
                # data["Scenario"][index]["ThenAnds"].append(t_and)
                data["Scenario"][index]["Then"].append("Then " + t_and)

    # print("\n")
    # print(data)

    # print("\n")
    # json_data = json.dumps(data, indent=4)
    # print(json_data)
    return data
    # file = open("features/everything.feature", "r+")

# parse(text)
