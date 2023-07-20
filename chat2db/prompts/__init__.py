import pkg_resources
import chat2db.utils as U


def load_prompt(prompt):
    package_path = pkg_resources.resource_filename("chat2db", "")
    return U.load_text(f"{package_path}/prompts/{prompt}.txt")
   