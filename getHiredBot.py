
#####Done! Congratulations on your new bot. You will find it at t.me/Get_HiredBot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.
#####For a description of the Bot API, see this page: https://core.telegram.org/bots/api

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import Filters
import requests

# Replace 'YOUR_TOKEN' with the actual token you obtained from the BotFather
TOKEN = '6732676851:AAEH0pEJ1lmcn4CpIbG_iANDwTH5mXTkA10'
BASE_URL = 'http://localhost:8000'
CHAT_ENDPOINT = 'chat'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please enter a number.")

def handle_number(update: Update, context: CallbackContext) -> None:
    try:
        user_input = int(update.message.text)
        result = user_input + 1
        update.message.reply_text(f"You entered: {user_input}\nI added 1, and the result is: {result}")
    except ValueError:
        update.message.reply_text("Please enter a valid number.")

### handle_chat
def handle_chat(update: Update, context: CallbackContext) -> None:
    try:
        user_input = update.message.text
        #result = user_input + 1
        response = make_post_request(BASE_URL, CHAT_ENDPOINT, user_input)
        if response is not None:
            print(f"Response: {response}")
        else:
            print("Request failed.")
        update.message.reply_text(f"{response}")
    except ValueError:
        update.message.reply_text("Please enter a valid response.")

def reset(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Resetting...')  # Add your reset logic here
    return reset_dbs()
    
def set_role(update: Update, context: CallbackContext) -> None:
    # Get the parameter after "/role"
    try:
        rle = update.message.text
        rle = rle.replace("/role","")
    
        if rle is not None:
            print(f"Setting role to: {rle}")
            update.message.reply_text(f"Setting role to: {rle}")
            return setting_role(rle) 
        else:
            print("You need to enter a valid role that you are interviewing for....")
            update.message.reply_text("You need to enter a valid role that you are interviewing for....")
    except ValueError:
        update.message.reply_text("You need to enter a valid role that you are interviewing for....")



####

##Process Requests
def setting_role(input_string):
    try:
            full_url = f"{BASE_URL}/set_role/?role={input_string}"
            response = requests.post(full_url, data={})
        
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Return the response content as a string
                return response.text
            else:
                # Print an error message if the request was not successful
                print(f"Error: {response.status_code}")
                return None
    except requests.exceptions.RequestException as e:
        # Handle exceptions, e.g., network errors
        print(f"Exception: {e}")
        return None

def reset_dbs():
    try:
            full_url = f"{BASE_URL}/reset"
            response = requests.post(full_url, data={})
        
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Return the response content as a string
                return response.text
            else:
                # Print an error message if the request was not successful
                print(f"Error: {response.status_code}")
                return None
    except requests.exceptions.RequestException as e:
        # Handle exceptions, e.g., network errors
        print(f"Exception: {e}")
        return None

def make_post_request(url, endpoint, input_string):
    """
    Make an HTTP POST request with string data.
    :param url: Base URL.
    :param endpoint: Endpoint to append to the base URL.
    :param data: String data to be sent in the request body.
    :return: Response content as a string.
    """
    try:
        # Construct the full URL
        #full_url = f"{url}/{endpoint}"
        full_url = f"{url}/{endpoint}/?user_message={input_string}"

        #data = {"input_string": input_string}



        # Set up the headers
        #headers = {'Content-Type': 'application/json'}

        # Make the POST request
        response = requests.post(full_url, data={})
        #response = requests.post(full_url, data=data, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Return the response content as a string
            return response.text
        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        # Handle exceptions, e.g., network errors
        print(f"Exception: {e}")
        return None



def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("reset", reset))
    dispatcher.add_handler(CommandHandler("role", set_role))



    # Message handler for handling numbers
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_chat))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()