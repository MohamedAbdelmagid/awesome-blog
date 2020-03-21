import json
import requests
import time

import urllib.parse as encode
from threading import Thread

from flask import current_app


# Method for translation using Microsoft API
def translate_with_microsoft(text, source_language, dest_language):
    if 'MS_TRANSLATOR_KEY' not in current_app.config or not current_app.config['MS_TRANSLATOR_KEY']:
        return 'Error: the translation service is not configured.'

    subscription_key = current_app.config['MS_TRANSLATOR_KEY']
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

