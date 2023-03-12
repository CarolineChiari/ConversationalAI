import azure.cognitiveservices.speech as speechsdk
import time
from datetime import datetime
# from main import settings, already_spoken, output_folder
from sounds import play_sound
import simpleaudio as sa
from dotenv import load_dotenv
import os
import sounddevice as sd

# List the available audio devices and their IDs
devices = sd.query_devices()
for i, device in enumerate(devices):
    # print(device)
    print(f"Device {i}: {device['name']} (ID: {device['index']})")


load_dotenv(override=True)

settings = {
    'speechKey': os.environ.get('SPEECH_KEY'),
    'region': os.environ.get('SPEECH_REGION'),
    # Feel free to hardcode the language
    'language': os.environ.get('SPEECH_LANGUAGE'),
    'openAIKey': os.environ.get('OPENAI_KEY')
}

prop = False

# Some sounds need to be generated over and over, like "thank you" or "I didn't get that".
# There is no need to waste money re-generating them, so we will keep track of them here
already_spoken = {}


def Start_recording(output_folder):

    # Creates an instance of a speech config with specified subscription key and service region.
    speech_config = speechsdk.SpeechConfig(
        subscription=settings['speechKey'], region=settings['region'])

    speech_config.request_word_level_timestamps()
    speech_config.set_property(
        property_id=speechsdk.PropertyId.SpeechServiceResponse_OutputFormatOption, value="detailed")

    # Creates a speech recognizer using the default microphone (built-in).
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config)

    # initialize some variables
    results = []
    done = False

    # update the last time speech was detected.
    def speech_detected():
        nonlocal lastSpoken
        lastSpoken = int(datetime.now().timestamp() * 1000)

    # Event handler to add event to the result list
    def handleResult(evt):
        import json
        nonlocal results
        nonlocal lastSpoken
        results.append(json.loads(evt.result.json))

        # print the result (optional, otherwise it can run for a few minutes without output)
        # print('RECOGNIZED: {}'.format(evt))
        speech_detected()

        # result object
        res = {'text': evt.result.test, 'timestamp': evt.result.offset,
               'duration': evt.result.duration, 'raw': evt.result}

        if (evt.result.text != ""):
            results.append(res)

            # print(evt.result)

    # Event handler to check if the recognizer is done

    def stop_cb(evt):
        # print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    # Connect callbacks to the events fired by the speech recognizer & displays the info/status
    # Ref:https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-speech/azure.cognitiveservices.speech.eventsignal?view=azure-python
    speech_recognizer.recognizing.connect(lambda evt: speech_detected())
    # speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(
        lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(
        lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(
        lambda evt: print('CANCELED {}'.format(evt)))
    speech_recognizer.recognized.connect(handleResult)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start speech recognition
    result_future = speech_recognizer.start_continuous_recognition_async()
    result_future.get()

    # Play sound to indicate that the recording session is on.
    play_sound()

    lastSpoken = int(datetime.now().timestamp() * 1000)

    # Wait for speech recognition to complete
    while not done:
        time.sleep(1)
        now = int(datetime.now().timestamp() * 1000)
        inactivity = now - lastSpoken
        # print(inactivity)
        # After 1 second of no speech detected, play a sound to indicate the recoding session could close.
        if (inactivity > 1000):
            play_sound()
        if (inactivity > 3000):  # Close the recoding session if no input is detected after 3s
            print('Stopping async recognition.')
            speech_recognizer.stop_continuous_recognition_async()
            speak("Thank you!")
            while not done:
                time.sleep(1)

    output = ""
    for res in results:
        output += res['NBest'][0]['Display']

    return results


def speak(text, silent=False, output_folder="./Output"):

    if text in already_spoken:  # if the speech was already synthetized
        if not silent:
            play_obj = sa.WaveObject.from_wave_file(
                already_spoken[text]).play()
            play_obj.wait_done()
        return

    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=settings['speechKey'], region=settings['region'])
    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    file_name = f'{output_folder}/{datetime.now().strftime("%Y%m%d_%H%M%S")}.wav'
    audio_config = speechsdk.audio.AudioOutputConfig(
        use_default_speaker=True, filename=file_name)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=audio_config)

    speech_synthesis_result = speech_synthesizer.speak_text(text)  # .get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
        if not silent:
            play_obj = sa.WaveObject.from_wave_file(file_name).play()
            play_obj.wait_done()
        already_spoken[text] = file_name
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")


def speak_ssml(text):
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=settings['speechKey'], region=settings['region'])
    # audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # The language of the voice that speaks.
    speech_config.speech_synthesis_voice_name = 'en-US-JennyNeural'

    speech_synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config, audio_config=None)

    speech_synthesis_result = speech_synthesizer.speak_ssml(
        text)  # .speak_text(text) #.get()

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(
                    cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
