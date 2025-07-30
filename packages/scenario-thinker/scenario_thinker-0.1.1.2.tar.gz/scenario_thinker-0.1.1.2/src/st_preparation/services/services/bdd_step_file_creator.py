import random
import string
from re import sub


def create_bdd_step_method(command, actions):
    prefix = command.split(" ")[0].lower()

    command_without_prefix = ' '.join(command.split(" ")[1:])

    method_mention = "_".join(command.split(" ")[1:3])
    method_name = f"step_{method_mention}_{_random_char(10)}"

    actions_with_context = actions.replace("driver", "context.driver")
    actions_in_array = actions_with_context.split(";")
    ready_actions = []
    for action in actions_in_array:
        ready_actions.append(f"\t{action}")
    ready_actions = "\n".join(ready_actions)

    full_method = f"""@{prefix}('{command_without_prefix}')
def {method_name}(context):
{ready_actions}
    """

    return full_method
# print(create_bdd_step_method("Given visiting site localhost:3000/button_with_redirect", "driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()));driver.get('http://localhost:3000/button_with_redirect')"))
def _random_char(y):
       return ''.join(random.choice(string.ascii_letters) for x in range(y))
