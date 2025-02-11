import asyncio
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.ext import CallbackContext
from PIL import Image
from io import BytesIO
import re
import os

# Bot Token and Logo URL
#BOT_TOKEN = "7660007316:AAHis4NuPllVzH-7zsYhXGfgokiBxm_Tml0"
LOGO_URL = "http://ob.saleh-kh.lol:2082/download.php?f=BQACAgQAAxkBAAEFAAFPZ5sF0_AaeoJXCudvLt_r7b_TR_4AAvEbAAI6g6lQXl4349rqy1cvBA&s=1097030&n=Picsart_25-01-25_12-27-36-849_5812321079229684721.png&m=image%2Fpng&T=MTczODIyNzIyMA=="

# Path to save the logo
LOGO_PATH = "downloaded_logo.png"

# Download the logo image from the URL
def download_logo(url: str, save_path: str):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Logo saved to {save_path}")
    else:
        print(f"Failed to download logo. Status code: {response.status_code}")

# Ensure the logo is downloaded once at the start
if not os.path.exists(LOGO_PATH):
    download_logo(LOGO_URL, LOGO_PATH)

# Define the customized caption with title support
def get_custom_caption(links, title):
    # Start caption with basic information
    caption = f"""
🎃 ᴘᴏᴡᴇʀᴇᴅ ʙʏ↓ Telegram                
                🍯 @HotError      

Title - {title}
⌬ Hot Error
"""

    # If only one link, display as a single link
    if len(links) == 1:
        caption += f"╰─➩ {links[0]} \n"

    # If multiple links, format them with part numbers
    elif len(links) > 1:
        for idx, link in enumerate(links, 1):
            caption += f"(Part {idx})─➩ {link} \n\n"

    # Append other categories
    caption += """
Other Categories ↓ 🥵⚡
https://t.me/HotError
"""
    return caption

# Function to add logo to image
def add_logo_to_image(photo: Image.Image, logo_path: str) -> Image.Image:
    # Open the logo image
    logo = Image.open(logo_path)

    # Resize logo if necessary (optional, adjust as needed)
    logo_width = photo.width // 3  # Resize logo to 1/3rd of the image width
    logo_height = int((logo_width / logo.width) * logo.height)
    logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)

    # Position the logo at the bottom left corner of the photo
    position = (0, photo.height - logo.height)  # Bottom-left corner

    # Paste the logo on the photo
    photo.paste(logo, position, logo.convert("RGBA"))
    return photo


# Function to handle received media and customize the caption
async def handle_media(update: Update, context: CallbackContext):
    media = None
    caption = None
    links = []  # List to store all the links
    title = "No Title"  # Default title if no links are found

    # Only handle media messages that have a caption (e.g., photo, video, etc.)
    if update.message.photo:
        caption = update.message.caption
        media = update.message.photo[-1]  # Take the highest quality photo
    elif update.message.video:
        caption = update.message.caption
        media = update.message.video
    elif update.message.document:
        caption = update.message.caption
        media = update.message.document
    elif update.message.voice:
        caption = update.message.caption
        media = update.message.voice
    elif update.message.animation:
        caption = update.message.caption
        media = update.message.animation

    # If a caption exists, extract the title and links
    if caption:
        # Use a regex to extract all links (http or https)
        links = re.findall(r"https?://[^\s]+", caption)

        # Remove all links from the caption to get the title
        title = re.sub(r"https?://[^\s]+", "", caption).strip()

        custom_caption = get_custom_caption(links, title)  # Use extracted title and links

        # If the media is a photo, download, process and send with the custom caption
        if update.message.photo:
            # Download the image
            photo_file = await media.get_file()
            photo_bytes = await photo_file.download_as_bytearray()

            # Open the image with Pillow
            photo = Image.open(BytesIO(photo_bytes))

            # Add the logo to the photo
            photo_with_logo = add_logo_to_image(photo, LOGO_PATH)

            # Save the modified image to a BytesIO object
            output = BytesIO()
            photo_with_logo.save(output, format="PNG")
            output.seek(0)

            # Send the modified image with the custom caption
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=output, caption=custom_caption)

        # For video, document, voice note, and animation, just send the media with the custom caption
        elif update.message.video:
            await context.bot.send_video(chat_id=update.effective_chat.id, video=media.file_id, caption=custom_caption)
        elif update.message.document:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=media.file_id, caption=custom_caption)
        elif update.message.voice:
            await context.bot.send_voice(chat_id=update.effective_chat.id, voice=media.file_id, caption=custom_caption)
        elif update.message.animation:
            await context.bot.send_animation(chat_id=update.effective_chat.id, animation=media.file_id, caption=custom_caption)

# Function to start the bot and process incoming updates
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Bot is running and ready to process media.")
