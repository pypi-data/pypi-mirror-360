# PSEUDOCODE: Prompt Definitions
#
# DEFINE PROMPT_CATEGORIES = {
#   "validation_proof": [array of validation prompts],
#   "api_data_integration": [array of API prompts],
#   "database_infrastructure": [array of DB prompts],
#   "testing_apis": [array of testing prompts],
#   "config_environment": [array of config prompts],
#   "status_progress": [array of status prompts],
#   "bdd_testing": [array of BDD prompts]
# }

PROMPT_CATEGORIES = {
    "validation_proof": [
        "Are you sure the features are really completed? Prove it.",
        "What did you find? What should you work on next (keep it simple happy path) to bring this MVP to a finish?",
        "Did you take screenshots and compare to our goal?",
        "If you could test one single thing that represents the most important action this app should do, what would you test? Go test it."
    ],
    "api_data_integration": [
        "Did you really connect the UI to the actual API calls? Are you sure your data being passed from any UI to API is correctly used? Read the swagger or whatever API documentation and codebase to make sure and fix anything, and test it.",
        "Imagine the data that needs to pass back and forth - is it real? Is it correct? How would you know?"
    ],
    "database_infrastructure": [
        "Did you do your database migrations and other commands?",
        "Did you model the domain and data? If so, did you keep it simple and stay within the correct tech stack?"
    ],
    "testing_apis": [
        "What data model tests can you perform? Keep it simple and prove the main paths exist.",
        "Did you create the correct APIs? Did you keep them as simple as possible? Do they achieve the main goal of the app?"
    ],
    "config_environment": [
        "Do you need to ask the human for any API keys? Have you looked for them in the OS env and any .env files?",
        "Did you fake any 'your-api-key-here' that is keeping this project from really working?",
        "Can you run the app? Are you getting errors just starting up the server or environment?"
    ],
    "status_progress": [
        "What's the current status? Write a brief progress report."
    ],
    "bdd_testing": [
        "Do you see the BDD features and features/steps?",
        "Have you run the correct behave command for this technology? (like manage.py behave for Django, or behave for Python or cucumber for JavaScript?) Did you use clever focused params like --feature and --scenario and --format progress3 to see only what you need?",
        "What is the next focused BDD feature and/or feature and scenario that you should focus to get the main purpose of the app finished? Run those and fix any errors you see from that feedback.",
        "Make sure the steps fail until they are connected to real code. No mock, no 'pass' no 'assert True' - fail fast in the red is ideal until you connect to passing green code.",
        "Remove any ambiguous steps and BDD gherkin so that our behave environment works perfectly.",
        "Create any environment.py setup files as needed - keep it simple but make it work.",
        "Do any system checks so we know behave is working and the server is working.",
        "Read any ddd.md features folder and any mission.md and statediagram.md to understand if the features have been implemented."
    ]
}