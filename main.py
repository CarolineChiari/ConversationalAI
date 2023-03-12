from dotenv import load_dotenv
import re
import os
from datetime import date, datetime, timedelta
from openai_helper import complete_openai
from speech_processing import Start_recording, speak



# ---------------------------------------------------------------------------- #
#                                     Setup                                    #
# ---------------------------------------------------------------------------- #

load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    # Feel free to hardcode the language
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}




output_folder = f'./Output/{datetime.now().strftime("%Y%m%d_%H%M%S")}/'

os.makedirs(output_folder)
conversation = []
while (True):
    res = Start_recording(output_folder=output_folder)[0]['DisplayText']
    conversation.append(res)
    print(res)
    prompt = ""
    for i in range(len(conversation)-4, len(conversation)):
        if (i >= 0):
            if (i % 2 == 0):
                prompt += f"Q: {conversation[i]}\n"
            else:
                prompt += f"A: {conversation[i]}\n"
    prompt += "A: "
    print(prompt)
    result = complete_openai(
        prompt=prompt, token=3000)
    conversation.append(result)
    speak(result, output_folder=output_folder)
# if __name__ == "__main__":

    # while (True):
