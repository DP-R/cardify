import os
import telebot
from rc_converter import parse_rc_a4, generate_rc_card
from dl_converter import parse_dl_a4, generate_dl_card
import fitz

# Replace with your actual bot token from @BotFather
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
bot = telebot.TeleBot(BOT_TOKEN)

def detect_doc_type(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = doc[0].get_text().upper()
        if "FORM 23" in text or "REGISTRATION CERTIFICATE" in text or "VEHICLE REGISTRATION" in text:
            return 'rc'
        elif "DRIVING LICENCE" in text or "FORM 7" in text:
            return 'dl'
    except Exception:
        pass
    return 'unknown'

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Welcome to *Cardify Bot*! 🚗📄\n\n"
        "Send me your standard A4 PDF (RC or Driving Licence), "
        "and I'll convert it into a compact, printable Smart Card PDF in seconds.\n\n"
        "Just upload your PDF file below!"
    )
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        file_name = message.document.file_name.lower()
        
        if not file_name.endswith('.pdf'):
            bot.reply_to(message, "❌ Please upload a valid PDF file.")
            return
            
        status_msg = bot.reply_to(message, "Processing your document... ⚙️")
        
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_path = f"temp_input_{message.chat.id}.pdf"
        output_path = f"converted_card_{message.chat.id}.pdf"
        
        with open(input_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        doc_type = detect_doc_type(input_path)
        
        if doc_type == 'rc':
            data = parse_rc_a4(input_path)
            generate_rc_card(data, output_path)
            card_name = "RC Smart Card"
        elif doc_type == 'dl':
            data = parse_dl_a4(input_path)
            generate_dl_card(data, output_path)
            card_name = "Driving Licence Smart Card"
        else:
            bot.edit_message_text("⚠️ Could not automatically detect if this is an RC or DL. Please make sure it's a valid RTO A4 PDF.", 
                                  chat_id=message.chat.id, message_id=status_msg.message_id)
            os.remove(input_path)
            return
            
        # Send the file back
        with open(output_path, 'rb') as doc:
            bot.send_document(
                message.chat.id, 
                doc, 
                caption=f"✅ Here is your {card_name}!\n\n_Powered by Cardify_",
                parse_mode='Markdown'
            )
            
        # Cleanup
        bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)
        
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred during conversion:\n`{str(e)}`", parse_mode='Markdown')
        # Cleanup on error
        if os.path.exists(f"temp_input_{message.chat.id}.pdf"): os.remove(f"temp_input_{message.chat.id}.pdf")
        if os.path.exists(f"converted_card_{message.chat.id}.pdf"): os.remove(f"converted_card_{message.chat.id}.pdf")

if __name__ == '__main__':
    print("🚀 Cardify Telegram Bot is running...")
    bot.infinity_polling()
