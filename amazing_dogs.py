"""

Amazing Dogs Bot shows you the amazing world of Dogs.

"""
from __future__ import annotations

from typing import AsyncIterable

from fastapi_poe import PoeBot, run
from fastapi_poe.types import QueryRequest
from sse_starlette.sse import ServerSentEvent

from fastapi_poe import PoeBot, run
from fastapi_poe.client import MetaMessage, stream_request
from fastapi_poe.types import QueryRequest, SettingsResponse, ProtocolMessage
from sse_starlette.sse import ServerSentEvent
from urllib.parse import urlparse, parse_qs

import requests

BOT = "claude-instant"

TEMPLATE = """
You are a chatbot who expertise in facts related to Dogs.
You can tell interesting facts about dogs that the user asks.

If the user asks for dog images, just give them some facts and
do not mention anything about the image. Basically you just ignore any image requests.

Your output should use the following template: 

BEGIN TEMPLATE

### Here are some interesting fact: 
{one or two sentence about dog breed fact that user has asked for}
{If user has not mentioned any breed, then give a random fact about any dog breed}

END TEMPLATE


If you are not given a dog breed name, then please give actionable
steps to the user so that they ask about certain dog breeds.
Make the conversation interesting and engaging. Only talk about dogs and nothing else.
"""

DOG_BREED_REPO = ['affenpinscher', 'african', 'airedale', 'akita', 'appenzeller', 'australian', 'basenji', 'beagle', 
    'bluetick', 'borzoi', 'bouvier', 'boxer', 'brabancon', 'briard', 'buhund', 'bulldog', 'bullterrier', 'cattledog', 
    'chihuahua', 'chow', 'clumber', 'cockapoo', 'collie', 'coonhound', 'corgi', 'cotondetulear', 'dachshund', 'dalmatian', 
    'dane', 'deerhound', 'dhole', 'dingo', 'doberman', 'elkhound', 'entlebucher', 'eskimo', 'finnish', 'frise', 'germanshepherd', 
    'greyhound', 'groenendael', 'havanese', 'hound', 'husky', 'keeshond', 'kelpie', 'komondor', 'kuvasz', 'labradoodle', 'labrador', 
    'leonberg', 'lhasa', 'malamute', 'malinois', 'maltese', 'mastiff', 'mexicanhairless', 'mix', 'mountain', 'newfoundland', 'otterhound', 
    'ovcharka', 'papillon', 'pekinese', 'pembroke', 'pinscher', 'pitbull', 'pointer', 'pomeranian', 'poodle', 'pug', 'puggle', 'pyrenees', 
    'redbone', 'retriever', 'ridgeback', 'rottweiler', 'saluki', 'samoyed', 'schipperke', 'schnauzer', 'segugio', 'setter', 'sharpei', 'sheepdog', 
    'shiba', 'shihtzu', 'spaniel', 'spitz', 'springer', 'stbernard', 'terrier', 'tervuren', 'vizsla', 'waterdog', 'weimaraner', 'whippet', 'wolfhound']

def get_dog_breed_from_user_text(user_text):
    """Parse through the user text to detect if user has mentioned any dog breed name. Return the dog breed name."""
    user_text = user_text.lower()
    user_text = user_text.replace("?", "")
    user_text = user_text.replace(".", "")
    user_text = user_text.replace(",", "")
    user_text = user_text.replace("!", "")
    for word in user_text.split():
        if word.lower() in DOG_BREED_REPO:
            return word.lower()
    return None

def get_random_dog_image_breed(breed_name):
    """Fetch the image url with API https://dog.ceo/api/breed/{breed_name}//images/random"""
    url = f"https://dog.ceo/api/breed/{breed_name}/images/random"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['message']
    else:
        return None

def get_random_dog_image():
    """Fetch the random image using the API: https://dog.ceo/api/breeds/image/random"""
    url = "https://dog.ceo/api/breeds/image/random"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['message']
    else:
        return None


SETTINGS = SettingsResponse(
    allow_user_context_clear=True,
    context_clear_window_secs=60*5
)

class AmazingDogs(PoeBot):
    async def get_response(self, query: QueryRequest) -> AsyncIterable[ServerSentEvent]:

        # prepend system message onto query
        query.query = [ProtocolMessage(role="system", content=TEMPLATE)] + query.query

        last_message = query.query[-1]
        breed_name = get_dog_breed_from_user_text(last_message.content)
        if breed_name:
            yield self.text_event(f"\n\nWelcome to the world of Dogs. One cute dog image gauranteed! \n\n")
            url = get_random_dog_image_breed(breed_name)
            yield self.text_event(f"![{breed_name}]({url}) \n\n")
        else:
            url = get_random_dog_image()
            yield self.text_event(f"![{breed_name}]({url}) \n\n")

        async for msg in stream_request(query, BOT, query.api_key):
            if isinstance(msg, MetaMessage):
                continue
            elif msg.is_suggested_reply:
                yield self.suggested_reply_event(msg.text)
            elif msg.is_replace_response:
                yield self.replace_response_event(msg.text)
            else:
                yield self.text_event(msg.text)

    async def get_settings(self, settings: SettingsRequest) -> SettingsResponse:
        """Return the settings for this bot."""
        return SETTINGS


if __name__ == "__main__":
    run(AmazingDogs())

