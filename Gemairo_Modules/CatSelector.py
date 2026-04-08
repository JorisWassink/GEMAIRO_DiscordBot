import requests
import io
import discord


def tryGetCatImage(number):
    response = requests.get(f'https://http.cat/{number}')

    if response.status_code == 200:
        img = response.content
        file = discord.File(io.BytesIO(img), filename="cat.jpg")
        return file
    
    elif response.status_code == 404:
        print(f"Not a valid number")
        return None
    else:
        print('something else went wrong')
        return None