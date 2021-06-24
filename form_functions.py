import logging
import os
from tabulate import tabulate
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db_functions import creating_csv_for_each_form, db_connect, extract_form, title_check_db, title_extraction
from telegram import Update, user
from telegram.ext import CallbackContext, ConversationHandler
# from variables import inline_markup

logging.basicConfig(
    filename="logs.log",
    filemode="w",
    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)

def displaying_each_form(update: Update, context: CallbackContext, flist: list) -> str:
    print(flist)

    tracker = 1

    if context.user_data.get("last_form", None):
        tracker = context.user_data["last_form"]
        context.user_data.clear()

    else:
        formid = flist[0][1]
        db = db_connect()
        cur = db.cursor()
        cur = db.execute(f"select form_id from form_table where user_id = {update.effective_user.id}")
        form_list = cur.fetchall()
        for i in form_list:
            if i[0] == formid:
                tracker = form_list.index(i) + 1
                break


    title = ""
    id = 0
    questions = []
    for i in flist:
        if title == "":
            title += i[2]
            id = i[1]

        if i[2] == title:
            questions.append(i[4])

        if len(questions) == i[0]:
            # form_dict[title] = questions
            print("question list : ",questions)
            complete_form_text = f"Form {tracker} : \n\n"
            complete_form_text += f"Title : {title}\n"
            complete_form_text += f"Questions : \n"
            count = 1
            for j in questions:
                complete_form_text += f"{count}. {j}\n"
                count += 1
            form_link = f"https://t.me/{context.bot.username}?start={update.effective_user.id}_{id}"
            complete_form_text += form_link
            if update.callback_query == None:
                update.effective_message.reply_text(complete_form_text)
            else:
                update.callback_query.edit_message_text(complete_form_text)
            
            title = ""
            questions = []
            tracker+=1



### displaying all forms
def view_forms(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    flist = extract_form(formid=None, userid=userid)
    if flist == []:
        update.effective_message.reply_text(
            "No forms created !\nType /create to start creating forms"
        )
        return
    displaying_each_form(update, context, flist)


### unfinished
### displaying specific form by title
def showing_specific_form(update: Update, context: CallbackContext):
    title = update.effective_message.text  ##get the title of the form the user wants
    userid = int(update.effective_user.id)
    form = title_check_db(userid, title)
    if form == []:
        update.effective_message.reply_text(f"There is no form named {title}!")
        return
    else:
        formid = form[0]  ## this gives the form id for the given title
        flist = extract_form(formid, userid)
        displaying_each_form(update, context, flist)


def view_query(update : Update,context : CallbackContext):
    query = update.callback_query
    data = query.data
    userid = update.effective_user.id
    formid = int(data.split("_")[1])
    flist = extract_form(formid, userid)
    displaying_each_form(update, context, flist)


def view_forms_ck(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    numbering = []
    title_text = "Your forms :\n"
    title_list = title_extraction(userid)
    count = 1
    temp_list = []
    for form_id, title in title_list:
        title_text += f"{count}. {title}\n"

        temp_list.append(InlineKeyboardButton(text=str(count), callback_data="view_" + str(form_id)))
        
        if len(temp_list) == 4 :
            numbering.append(temp_list)
            temp_list = []

        count += 1

    if temp_list:
        numbering.append(temp_list)

    # update.effective_message.reply_text(title_text)
    update.effective_message.reply_text(title_text,reply_markup=InlineKeyboardMarkup(numbering))

    return 0


