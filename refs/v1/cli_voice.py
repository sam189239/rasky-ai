from utils import *

import sounddevice as sd
from kokoro import KPipeline
# from langchain_community.llms import HuggingFaceHub
import os
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
import torch
# import keyboard
import numpy as np
import time

if torch.cuda.is_available(): device = 'cuda'
else: device = 'cpu'
print(f"Using: {device}")


import sys
# sys.excepthook = sys.__excepthook__

## LLM - OLLAMA / HUGGINGFACE ##

def init_llama():

    # chat_model = HuggingFaceHub(
    # repo_id="meta-llama/Llama-3.2-3B-Instruct",  # Replace with your desired model
    # model_kwargs={"temperature": 0.7, "max_length": 100},
    # )

    # llama_model = ChatOllama(
    #     model="llama3.2",
    #     temperature=0.8,
    #     num_predict=256
    # )
    
    chat_model = ChatOllama(model="llama3.2")
    return chat_model

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and friendly AI assistant. Respond conversationally and helpfully. Here is the conversation history: {chat_history}"),
    ("user", "{user_input}")
])
voice_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and friendly AI voice assistant. Respond conversationally and briefly (less than 20 words) unless user asks for more info. You can ask follow up questions after answering the query. Here is the conversation history: {chat_history}"),
    ("user", "{user_input}")
])

def chat(user_input, voice_mode=True):
    global chat_history
    # Assuming voice_prompt.format_messages is defined elsewhere
    messages = voice_prompt.format_messages(user_input=user_input, chat_history=chat_history)
    chat_history.append(messages[1])  # Add user's input to chat history

    # Get model response
    response = chat_model.invoke(messages)  

    chat_history.append(AIMessage(response.content))  # Add AI response to history

    if voice_mode: 
        # Generate and play AI response as audio
        generator = generate_audio(response.content)
        play_audio(generator)
    
    return response.content


## KOKORO ##

pipeline = KPipeline(lang_code='a', device=device)
# pipeline = KPipeline(lang_code='a', device=device, model="af_bella", speed=1, split_pattern=r'\n+')

chat_model =  init_llama() 
chat_history = []



def generate_audio(text, voice='af_bella', speed=1, split_pattern=r'\n+', play=True):
    generator = pipeline(
        text, voice=voice, speed=speed, split_pattern=split_pattern
    )
    if play:
        play_audio(generator) #####
    return generator

# class AudioPlayer:
#     def __init__(self, sample_rate=24000):
#         self.sample_rate = sample_rate
#         self.audio_data = None
#         self.playback_position = 0
#         self.is_paused = False

#     def play(self, audio_data):
#         """Play or resume audio from the last paused position."""
#         if self.is_paused:
#             sd.play(self.audio_data[self.playback_position:], samplerate=self.sample_rate)
#         else:
#             self.audio_data = audio_data
#             self.playback_position = 0
#             sd.play(self.audio_data, samplerate=self.sample_rate)

#         self.is_paused = False

#     def pause(self):
#         """Pause the audio playback and store playback position."""
#         if sd.get_stream().active:
#             self.playback_position = int(sd.get_stream().time * self.sample_rate)
#             sd.stop()
#             self.is_paused = True

#     def stop(self):
#         """Stop playback completely."""
#         sd.stop()
#         self.playback_position = 0
#         self.is_paused = False

# def play_new_audio(generator, sample_rate=24000):
#     """Stop current audio and play something else."""
#     global keep_going_gen
#     player = AudioPlayer()
#     def test_play(audio):  
#         player.play(audio)      
#         while sd.get_stream().active:
#             if keyboard.is_pressed('p'):  # Pause original audio
#                 player.pause()
#                 print("Audio paused.")
#                 play_new_audio(keep_going_gen)
#                 time.sleep(0.5)  # Prevent rapid re-triggering
#                 user_choice=input()
#                 if user_choice == 'y':
#                     print("Resuming original message...")
#                     player.play(generator)
#                 else:
#                     print("Stopping.")
#                     player.stop()
#                     break  # Exit loop

#             elif keyboard.is_pressed('s'):  # Stop everything
#                 print("Stopping.")
#                 player.stop()
#                 break  # Exit loop

#     sd.stop()
#     for i, (gs, ps, audio) in enumerate(generator):
#         # sd.play(audio, sample_rate)  # 24000 is the sample rate
#         test_play(audio)  # 24000 is the sample rate
#         sd.wait()
    
def play_audio(generator):
    for i, (gs, ps, audio) in enumerate(generator):
        # print(i)  # i => index
        # print(gs)  # gs => graphemes/text
        # print(ps)  # ps => phonemes
        sd.play(audio, 24000)  # 24000 is the sample rate
        # while sd.get_stream().active:
        #     if keyboard.is_pressed("space"):  # Press space to stop
        #         sd.stop()
        #         break
        sd.wait()  # Wait until the audio is finished playing



def voice_assistant():            
    global keep_going_gen
    print("Rasky initialized. Say 'bye', 'goodbye', or 'end' to stop.")
    generate_audio("Hello, how can I help you?")
    while True:
        # Get user input (you can use speech-to-text here for real-time voice input)
        user_input = input("You: ")  # Replace this with actual voice input logic if needed

        # Break the loop if the user says 'bye', 'goodbye', or 'end'
        if any(phrase in user_input.lower() for phrase in ['bye', 'goodbye', 'end']):
            generate_audio("Goodbye!")
            break
        
        # Get response from the assistant and print it
        response = chat(user_input)
        print(f"Assistant: {response}")

# Run the assistant
# keep_going_gen = generate_audio("Would you like me to keep going?", play = False)
if __name__ == '__main__':
    voice_assistant()


