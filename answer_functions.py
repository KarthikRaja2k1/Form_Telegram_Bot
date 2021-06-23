
import os
from tabulate import tabulate
from db_functions import creating_csv_for_each_form, db_connect, title_check_db
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from variables import inline_markup

### showing all answers for all forms
def show_answers(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    ans_ck = creating_csv_for_answers_for_all_forms(update, context, userid)
    if ans_ck == 0:
        update.effective_message.reply_text(
            "There are no answers available for your all forms!"
        )
    else:
        update.effective_message.reply_text(
            "Preview and its csv file will be uploaded !"
        )


### unfinished
### showing answers for specific form by title
def showing_specific_form_answers(update: Update, context: CallbackContext):
    title = update.effective_message.text  ##get the title of the form the user wants
    userid = int(update.effective_user.id)
    form = title_check_db(userid, title)
    if form == []:
        update.effective_message.reply_text(f"There is no form named {title}!")
        return
    else:
        formid = form[0]  ## this gives the form id for the given title

        # sending the formid arguement to get the answers for specific form
        ans_ck = creating_csv_for_answers_for_all_forms(update, context, formid)

        if ans_ck == 0:
            update.effective_message.reply_text("There is no answers for this form!")


def creating_csv_for_answers_for_all_forms(
    update: Update, context: CallbackContext, userid, formid=None
):
    db = db_connect()
    cur = db.cursor()

    ## extracting the form id for a given user id

    if formid == None:
        cur = db.execute(
            f"select ft.question_count, ft.form_id, ft.form_title from user_table ut, form_table ft where ut.user_id = {userid} and ft.user_id={userid}"
        )
    else:
        cur = db.execute(
            f"select ft.question_count, ft.form_id, ft.form_title from user_table ut, form_table ft where ut.user_id = {userid} and ft.user_id={userid} and ft.form_id = {formid}"
        )

    anslist = cur.fetchall()
    flag = 0
    # db.close()
    for i in anslist:
        csv_file, total_tab = creating_csv_for_each_form(i, userid)
        if csv_file is None:
            continue
        flag = 1
        caption_text = f"Total questions : {i[0]}\n"
        cur = db.execute(
            f"select count(distinct user_id) from answer_table where form_id={i[1]}"
        )
        user_count = cur.fetchone()[0]
        caption_text += f"Total users answered : {user_count}"

        tb = tabulate(total_tab, headers="firstrow", tablefmt="simple")
        update.effective_message.reply_html(f"<pre>Title : {i[2]}\n{tb}!</pre>")

        update.effective_message.reply_document(
            document=open(file=csv_file, mode="r"),
            filename=f"{i[2]}-Answers",
            caption=caption_text,
        )

        os.remove(csv_file)
    return flag


def answer_query(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data == "1":
        query.edit_message_text("Displaying all answers for the forms you have created !")
        show_answers(update, context)
        return ConversationHandler.END

    else :
        query.edit_message_text("Showing the titles of forms :")



def answer_ck(update: Update, context: CallbackContext):
    update.effective_message.reply_text(
        "Enter any given option : ",reply_markup = inline_markup
    )
    return 0

