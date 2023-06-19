from fastapi_poe import make_app
from amazing_dogs import AmazingDogs

bot = AmazingDogs()

app = make_app(bot, allow_without_key=True)
