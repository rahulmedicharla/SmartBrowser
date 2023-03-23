# SmartBrowser

A personalized voice assistant browser. Helps make AI more accessible and helpful to people under the three most common use cases, academia, development, and assistant.
Developed using Django, SQL, and OpenAi's whisper and gpt-3.5-turbo api's. The browser gives different responses to questions under each different use case so that academic questions
can receive proper explanations and examples, development questions receive proper code and updated API's, and assistant can be used for general cases.

How to use:
1) clone repo
2) create a new venv environment and install everything in requirements.txt
3) create a keys.py file in the root directory with the field openaikey = "<your open ai api key>"
3) run python manage.py runserver to start up that server and use!
