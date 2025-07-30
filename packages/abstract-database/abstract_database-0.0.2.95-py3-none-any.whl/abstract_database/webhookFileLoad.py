import requests
webhook = "https://discordapp.com/api/webhooks/1278595755812327424/3xvzS30Bx8bOhooNJeY9gnYj2KjFb2-ZfV2rHpBdkS71tuibNeu56_mRFE38MrmQRa_j"
#response = requests.get()
from abstract_utilities import *
#input(response.json())
# pip install discord_webhook 
from discord_webhook import DiscordWebhook, DiscordEmbed

#Replace the webhook URL with your own
webhook_url = webhook

#Create a Discord webhook object
webhook = DiscordWebhook(url=webhook_url)

#Create a Discord embed object
embed = DiscordEmbed()

#Set the title and description of the embed
embed.set_title('File Upload')
embed.set_description('This is an example file upload')


webhook.add_file(read_from_file("/home/joben/Desktop/testsol/abstract_it.py"), '/home/joben/Desktop/testsol/abstract_it.py')

#Add the embed to the webhook
webhook.add_embed(embed)
#Send the webhook
response = webhook.execute()
