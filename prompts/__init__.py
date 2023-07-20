import pkg_resources
import Query-GPT.utils as U


def load_prompt(prompt):
    package_path = pkg_resources.resource_filename("Query-GPT", "")
    return U.load_text(f"{package_path}/prompts/{prompt}.txt")
    
print(load_prompt("router"))