# Babagaboosh
Simple app that lets you have a verbal conversation with OpenAi's GPT 4o.
Written by DougDoug. Feel free to use this for whatever you want! Credit is appreciated but not required.

If you would like a crappy video explanation of this project, I made a video covering the basics here: https://www.youtube.com/watch?v=vYE1rkIMj9w

## SETUP:
1) This was written in Python 3.9.2. Install page here: https://www.python.org/downloads/release/python-392/

2) Run `pip install -r requirements.txt` to install all modules.

3) This uses the Microsoft Azure TTS, Elevenlabs, and OpenAi services. You'll need to set up an account with these services and generate an API key from them. Then add these keys as windows environment variables named AZURE_TTS_KEY, AZURE_TTS_REGION, ELEVENLABS_API_KEY, and OPENAI_API_KEY respectively.

4) This app uses the GPT-4o model from OpenAi. As of this writing (Sep 3rd 2024), you need to pay $5 to OpenAi in order to get access to the GPT-4o model API. So after setting up your account with OpenAi, you will need to pay for at least $5 in credits so that your account is given the permission to use the GPT-4o model when running my app. See here: https://help.openai.com/en/articles/7102672-how-can-i-access-gpt-4-gpt-4-turbo-gpt-4o-and-gpt-4o-mini

5) Elevenlabs is the service I use for Ai voices. Once you've made an Ai voice on the Elevenlabs website, open up chatgpt_character.py and replace the ELEVENLABS_VOICE variable with the name of your Ai voice.

## Using the App

1) Run 'chatgpt_character.py'

2) Click the 'ASK ME A QUESTION' button.

3) Wait a few seconds for OpenAi to generate a response and for Elevenlabs to turn that response into audio. Once it's done playing the response, you can press 'ASK ME A QUESTION' again.


## Deploying to Azure

The repository includes a GitHub Action that builds the frontend and backend and deploys the app to Azure App Service.
To enable it, add the `AZURE_WEBAPP_PUBLISH_PROFILE` secret along with your API keys in the repository settings.
During startup Azure executes `startup.sh` which installs dependencies and launches Gunicorn.
