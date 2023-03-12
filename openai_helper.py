import openai
from dotenv import load_dotenv
import os
# from main import settings

# Load your API key from an environment variable or secret management service


load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    # Feel free to hardcode the language
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

openai.api_key = settings['openAIKey']


def complete_openai(prompt, token=50, stop=""):
    """
    Generates completions for a given prompt using the OpenAI API.

    Parameters:
    - prompt: The prompt for which completions are generated.
    - token: The maximum number of tokens (words) in the generated completions.
    - stop: A string that, if encountered in the generated completions, will cause the function to stop generating more completions.

    Returns:
    A list of strings containing the generated completions.
    """
    try:
        if (not stop):
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.9,
                max_tokens=token,
                top_p=1,
                presence_penalty=1.5,
                frequency_penalty=1.5
            )
            lines = response.to_dict_recursive(
            )['choices'][0]['text'].split("\n")
            
            response = '\n'.join(list(filter(lambda x: x != '', lines)))
            print(response)
            return response
        else:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=prompt,
                temperature=0.9,
                max_tokens=token,
                top_p=1,
                presence_penalty=1.5,
                frequency_penalty=1.5,
                stop=[stop]
            )
            print(response)
            lines = response.to_dict_recursive()['choices'][0]['text'].split("\n")
            response = '\n'.join(list(filter(lambda x: x != '', lines)))
            return response
    except Exception as e:
        print("An exception of type", type(e), "occurred with the message:", e)
