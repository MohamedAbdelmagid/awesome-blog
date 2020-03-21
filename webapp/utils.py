import os
import secrets
import json
import time
import requests
import urllib.parse as encode
from threading import Thread

from PIL import Image
from flask import render_template
from flask_mail import Message

from webapp import app, mail



# Method for randomise image's name and save in the static/pic file 
def store_image(form_image):
    # Get a random hex 
    random_hex = secrets.token_hex(8)
    # Get the extention of the pic file and concatenate it the hex
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    # Make a path to the static/pics directory
    image_path = os.path.join(app.root_path, 'static/pics', image_fn)

    # Resize the image before saving it
    output_size = (125, 125)
    image = Image.open(form_image)
    image.thumbnail(output_size)
    image.save(image_path)

    return image_fn


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# Method for sending email from a sender to many recipients 
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    Thread(target=send_async_email, args=(app, msg)).start()


# Method for sending password reset email 
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('Reset Your Password [Awesome Blog]',
        sender=app.config['MAIL_ADMIN'],
        recipients=[user.email],
        text_body=render_template('email/reset_password.txt', user=user, token=token),
        html_body=render_template('email/reset_password.html', user=user, token=token)
    )


# Method for translation using Microsoft API
def translate_with_microsoft(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in app.config or not app.config['MS_TRANSLATOR_KEY']:
        return 'Error: the translation service is not configured.'

    subscription_key = app.config['MS_TRANSLATOR_KEY']
    auth = { 'Ocp-Apim-Subscription-Key': subscription_key }

    base_url = 'https://api.microsofttranslator.com/v2/Ajax.svc'
    path = '/Translate'
    params = '?text={}&from={}&to={}'.format(text, source_language, dest_language)
    constructed_url = base_url + path + params
    # print('url ::  ' + constructed_url)

    response = requests.get(constructed_url, headers=auth)
    if response.status_code != 200:
        return 'Error: the translation service failed.'

    return json.loads(response.content.decode('utf-8-sig'))


# Method for translation using Google API
def translate_with_google(article, scr_lang, dest_lang):
    # To know which API we are using now
    # print('+++++ \n Using Google API for translation !! \n ++++++')   # For debugging, 
    
    # Because the free google API has a limited number of characters to translate, we have
    # to split the article to sentences and translate each sentence on its own.
    list_sentences = turn_to_list_sentences(article)
    threads = [None] * len(list_sentences)
    results = [None] * len(list_sentences)

    translatedText = ''
    for i in range(len(threads)):
        threads[i] = Thread(target=translate_sentence, args=(list_sentences[i], scr_lang, dest_lang, results, i))
        threads[i].start()
        # time.sleep(1)     We could make the main thread sleep to give other threads time to finish.
    
    for i in range(len(threads)):
        threads[i].join()

    return " ".join(results)    # concatenate all translated sentences and return the result

# Method that prepare the text for translation by encoding it and turn it to list of sentences
def turn_to_list_sentences(text):

    list_of_words = text.split()

    # Turn the list of words to a list of sentences no longer than 30-35 characters 
    list_of_sens = []
    sen=''
    for word in list_of_words:
        sen = sen + ' ' + word
        if len(sen) > 30 or word == list_of_words[-1]:
            list_of_sens.append(sen)
            sen = ''

    return list_of_sens

# Method for translation a single sentence using Google API
def translate_sentence(sentence, src_lang, dest_lang, result, index):

    base_url = 'https://translate.googleapis.com'
    path = '/translate_a/single'
    params = '?client=gtx&sl={}&tl={}&dt=t&q={}'.format(src_lang, dest_lang, encode.quote(sentence))
    constructed_url = base_url + path + params
    # print('url ::  ' + constructed_url)

    response = requests.get(constructed_url)
    if response.status_code != 200:
        return 'Error: the translation service failed.'
    
    jsonResponse = json.loads(response.content.decode('utf-8-sig'))
    # print(jsonResponse)
    translatedText = jsonResponse[0][0][0]
    result[index] = translatedText
        
    return translatedText



# Method for informing the admins about an error by sending emails to all of them 
def tell_admin_with_error(subject, error):
    send_email(subject=subject,
            sender=app.config['MAIL_ADMIN'],
            recipients=app.config['ADMINS'],
            text_body=render_template('email/microsoft_translator_failure.txt', error=error),
            html_body=render_template('email/microsoft_translator_failure.html', error=error)
        )