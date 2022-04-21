# -394474582
# 1661163213:AAFlUcjLL3ny5mR4peNiXx9aJdB_Lau66kk

import locale
import os
import sys
from datetime import date, datetime
# Import necessary libraries:
from getpass import getuser

import gspread
import gspread_dataframe
import pandas as pd
import telegram
from oauth2client.service_account import ServiceAccountCredentials
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.conversationhandler import ConversationHandler
from telegram.ext.filters import Filters
from telegram.ext.messagehandler import MessageHandler
from telegram.ext.updater import Updater
from telegram.update import Update

BOT_KEY = '1661163213:AAFlUcjLL3ny5mR4peNiXx9aJdB_Lau66kk'

# Set your path:
path = 'C:\\Users\\Dreambuilds\\Desktop\\Python\\fx-legends'
# Set sheet name
sheet_name = 'fxlegends'
# Set scope to use when authenticating:
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']
# Authenticate using your credentials, saved in JSON in Step 1:
creds = ServiceAccountCredentials.from_json_keyfile_name(path + '\\credentials.json', scope)

# Initialize the client, and open the sheet by name:
client = gspread.authorize(creds)

######  ######  ######
######   BOT    ######
######  ######  ######
updater = Updater(BOT_KEY,use_context=True)

def start(update: Update, context: CallbackContext):

    sheet = client.open(sheet_name).worksheet('Dashboard')

    # Get user information once bot is started
    chat_id = update.message.chat_id
    first_name = update.message.chat.first_name
    last_name = update.message.chat.last_name
    username = update.message.chat.username

    # CHECK USER AUTHENCITY
    gspread_getChatIds = sheet.col_values(1)

    # If user exist
    if (str(chat_id)) in gspread_getChatIds:
        update.message.reply_text("""Welcome back {}!, this is SWK-Algo-Bot.
    
        You can manage your trades with the following commands:
        
        <b>Commands</b>
        /open - open a trade
        /manage - view all your opened trades
        /modify - make changes to your existing trades
        /history - view your past trades
        /legends - view all the legends

        """.format(username),parse_mode=telegram.ParseMode.HTML)

        # Update user information, if there is a change
        findChatId = sheet.find(str(chat_id))
        getRow = findChatId.row
        if (first_name is None):
            first_name = ''
        if (last_name is None):
            last_name = ''
        sheet.update_cell(getRow,2,first_name)
        sheet.update_cell(getRow,3,last_name)
        sheet.update_cell(getRow,4,username)


    # If user does not exist
    else:
        update.message.reply_text("""Hello {}, this is SWK-Algo-Bot.
    
        You can manage your trades with the following commands:
        
        <b>Commands</b>
        /open - open a trade
        /manage - view all your opened trades
        /modify - make changes to your existing trades
        /history - view your past trades
        /legends - view all the legends

        """.format(username),parse_mode=telegram.ParseMode.HTML)

        # Add user to database
        firstCol = len(sheet.col_values(1))
        sheet.update_cell(firstCol+1,1,chat_id)
        sheet.update_cell(firstCol+1,2,first_name)
        sheet.update_cell(firstCol+1,3,last_name)
        sheet.update_cell(firstCol+1,4,username)

        # Create a trading sheet for user
        sheet = client.open(sheet_name).add_worksheet(title=str(chat_id), rows=1000, cols=8)
        sheet.update_cell(1,1,'Date')
        sheet.update_cell(1,2,'Symbol')
        sheet.update_cell(1,3,'Entry')
        sheet.update_cell(1,4,'TP')
        sheet.update_cell(1,5,'SL')
        sheet.update_cell(1,6,'Type')
        sheet.update_cell(1,7,'Status')
        sheet.format('1', {'textFormat': {'bold': True}})

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Sorry '%s' is not a valid command" % update.message.text)

def legends(update: Update, context: CallbackContext):

    sheet = client.open(sheet_name).worksheet('Dashboard')

    username = update.message.chat.username
    chat_id = update.message.chat_id

    findUsername = sheet.find(str(username))
    findChatId = sheet.find(str(chat_id))
    getUsernames = sheet.col_values(findUsername.col)
    getchatIds = sheet.col_values(findChatId.col)

    displayLegends = '[Legends]\n\n'
    idx = 0
    for user_chat_id in getchatIds[1:]:
        displayLegends += getUsernames[1:][idx] + '\n'
        sheet = client.open(sheet_name).worksheet(str(user_chat_id))
        tradeDate = sheet.col_values(1)
        tradeSym = sheet.col_values(2)
        tradeEntry = sheet.col_values(3)
        tradeTP = sheet.col_values(4)
        tradeSL = sheet.col_values(5)
        tradeType = sheet.col_values(6)
        tradeStatus = sheet.col_values(7)

        df = pd.DataFrame(list(zip(tradeDate[1:], tradeSym[1:], tradeEntry[1:],
        tradeTP[1:], tradeSL[1:], tradeType[1:], tradeStatus[1:])), columns = ['DATE', 'SYMBOL', 'ENTRY', 'TP', 'SL', 'TYPE', 'STATUS'])
        df.index += 1

        indexNames = df[df['STATUS'] != 'Open' ].index
        df.drop(indexNames , inplace=True)

        if (df.empty == False):

            displayLegends += df.to_string() + '\n\n'

        else:

            displayLegends += ":- No active trades" + '\n\n'
        
        idx+=1

        
    
    update.message.reply_text(displayLegends)

def opentrade(update: Update, context: CallbackContext):
    
    getUserMessage = update.message.text
    
    if (len(getUserMessage.split()) != 6):

        update.message.reply_text(
            "Invalid format. /open <SYM> <TYPE> <ENTRY> <TP> <SL>"
        )
    
    else:

        tSYM = getUserMessage.split()[1]
        tType = getUserMessage.split()[2]
        tEntry = getUserMessage.split()[3]
        tTP = getUserMessage.split()[4]
        tSL = getUserMessage.split()[5]

        chat_id = update.message.chat_id
        sheet = client.open(sheet_name).worksheet(str(chat_id))

        # Add entry to user's database
        firstCol = len(sheet.col_values(1))

        currentDate = date.today().strftime("%d/%m/%Y")

        sheet.update_cell(firstCol+1,1,currentDate)
        sheet.update_cell(firstCol+1,2,tSYM)
        sheet.update_cell(firstCol+1,3,tEntry)
        sheet.update_cell(firstCol+1,4,tTP)
        sheet.update_cell(firstCol+1,5,tSL)
        sheet.update_cell(firstCol+1,6,tType)
        sheet.update_cell(firstCol+1,7,"Open")

        update.message.reply_text(
            "You have opened a trade! Use /manage to view your trades"
        )

def manage(update: Update, context: CallbackContext):

    username = update.message.chat.username
    
    chat_id = update.message.chat_id
    sheet = client.open(sheet_name).worksheet(str(chat_id))
    tradeDate = sheet.col_values(1)
    tradeSym = sheet.col_values(2)
    tradeEntry = sheet.col_values(3)
    tradeTP = sheet.col_values(4)
    tradeSL = sheet.col_values(5)
    tradeType = sheet.col_values(6)
    tradeStatus = sheet.col_values(7)

    df = pd.DataFrame(list(zip(tradeDate[1:], tradeSym[1:], tradeEntry[1:],
    tradeTP[1:], tradeSL[1:], tradeType[1:], tradeStatus[1:])), columns = ['DATE', 'SYMBOL', 'ENTRY', 'TP', 'SL', 'TYPE', 'STATUS'])
    df.index += 1

    indexNames = df[df['STATUS'] != 'Open' ].index
    df.drop(indexNames , inplace=True)

    if (df.empty == False):

        update.message.reply_text("""Hello {}, these are your opened trades.
        
            {}

            """.format(username, df.to_string()),parse_mode=telegram.ParseMode.HTML)
    else:

        update.message.reply_text("""Hello {}, you do not have any trades open.
        
            Use the /open command to execute a trade.

            """.format(username),parse_mode=telegram.ParseMode.HTML)

def modify(update: Update, context: CallbackContext):

    getUserMessage = update.message.text
    
    if (len(getUserMessage.split()) != 8):

        update.message.reply_text("""Modify your existing trade, eg:

        7  21/04/2022  XAUUSD  1925.22  1932.55  1921.2   BUY   Open
        /modify 7 <SYMBOL> <TYPE> <ENTRY> <TP> <SL> <STATUS>

        :- Close a trade by setting <STATUS> to either 'TP' or 'Closed'

    """)

        update.message.reply_text(
            "Invalid format. /modify <ID> <SYMBOL> <TYPE> <ENTRY> <TP> <SL> <STATUS>"
        )
    
    else:
        chat_id = update.message.chat_id
        sheet = client.open(sheet_name).worksheet(str(chat_id))

        tradeDate = sheet.col_values(1)
        tradeSym = sheet.col_values(2)
        tradeEntry = sheet.col_values(3)
        tradeTP = sheet.col_values(4)
        tradeSL = sheet.col_values(5)
        tradeType = sheet.col_values(6)
        tradeStatus = sheet.col_values(7)

        df = pd.DataFrame(list(zip(tradeDate[1:], tradeSym[1:], tradeEntry[1:],
        tradeTP[1:], tradeSL[1:], tradeType[1:], tradeStatus[1:])), columns = ['DATE', 'SYMBOL', 'ENTRY', 'TP', 'SL', 'TYPE', 'STATUS'])
        df.index += 1

        indexNames = df[df['STATUS'] != 'Open' ].index
        df.drop(indexNames , inplace=True)

        userIndex = int(getUserMessage.split()[1])
        tSYM = getUserMessage.split()[2]
        tType = getUserMessage.split()[3]
        tEntry = getUserMessage.split()[4]
        tTP = getUserMessage.split()[5]
        tSL = getUserMessage.split()[6]
        tStatus = getUserMessage.split()[7]
        if (userIndex in df.index):
            getRow = int(getUserMessage.split()[1])+1
            sheet.update_cell(getRow,2,tSYM)
            sheet.update_cell(getRow,3,tEntry)
            sheet.update_cell(getRow,4,tTP)
            sheet.update_cell(getRow,5,tSL)
            sheet.update_cell(getRow,6,tType)
            sheet.update_cell(getRow,7,tStatus)
            update.message.reply_text("Order successfully modified!")
        else:
            update.message.reply_text(
                "Trade id does not exist!"
            )

def history(update: Update, context: CallbackContext):

    username = update.message.chat.username
    
    chat_id = update.message.chat_id
    sheet = client.open(sheet_name).worksheet(str(chat_id))
    tradeDate = sheet.col_values(1)
    tradeSym = sheet.col_values(2)
    tradeEntry = sheet.col_values(3)
    tradeTP = sheet.col_values(4)
    tradeSL = sheet.col_values(5)
    tradeType = sheet.col_values(6)
    tradeStatus = sheet.col_values(7)

    df = pd.DataFrame(list(zip(tradeDate[1:], tradeSym[1:], tradeEntry[1:],
    tradeTP[1:], tradeSL[1:], tradeType[1:], tradeStatus[1:])), columns = ['DATE', 'SYMBOL', 'ENTRY', 'TP', 'SL', 'TYPE', 'STATUS'])
    df.index += 1

    total_trades = len(df.index)

    win_count = df['STATUS'].str.contains('TP').sum()
    if win_count > 0:
        wins = df['STATUS'].value_counts()['TP']
    else:
        wins = 0

    loss_count = df['STATUS'].str.contains('Closed').sum()
    if loss_count > 0:
        losses = df['STATUS'].value_counts()['Closed']
    else:
        losses = 0

    open_count = df['STATUS'].str.contains('Open').sum()
    if open_count > 0:
        open = df['STATUS'].value_counts()['Open']
    else:
        open = 0
    
    win_rate = (int(wins) / total_trades) * 100

    if (df.empty == False):

        update.message.reply_text("""Hello {}, these is your trade history.
        
            {}

        Wins: {}    Losses: {}  Open: {}    Tota Trades: {}
        W/R: {}%

            """.format(username, df.to_string(), wins, losses, open, total_trades, round(win_rate)),parse_mode=telegram.ParseMode.HTML)

    else:

        update.message.reply_text("""Hello {}, there are no past trades available for viewing.

            """.format(username),parse_mode=telegram.ParseMode.HTML)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('legends', legends))
updater.dispatcher.add_handler(CommandHandler('open', opentrade))
updater.dispatcher.add_handler(CommandHandler('manage', manage))
updater.dispatcher.add_handler(CommandHandler('modify', modify))
updater.dispatcher.add_handler(CommandHandler('history', history))
updater.dispatcher.add_handler(MessageHandler(Filters.text, unknown))
updater.dispatcher.add_handler(MessageHandler(
    Filters.command, unknown))
  
updater.start_polling()
