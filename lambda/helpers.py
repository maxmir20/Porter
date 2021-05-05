#
# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import boto3
import time
import logging
import json
import pprint
import os
import config as help_desk_config
import re


logger = logging.getLogger()
logger.setLevel(logging.INFO)

kendra_client = boto3.client('kendra')

#FOR KENDRA INTENT


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
    logger.info('<<help_desk_bot>> "Lambda fulfillment function response = \n' + pprint.pformat(response, indent=4)) 

    return response


def increment_counter(session_attributes, counter):
    counter_value = session_attributes.get(counter, '0')

    if counter_value: count = int(counter_value) + 1
    else: count = 1
    
    session_attributes[counter] = count

    return count


def get_kendra_answer(question):
    try:
        KENDRA_INDEX = os.environ['KENDRA_INDEX']
    except KeyError:
        return 'Configuration error - please set the Kendra index ID in the environment variable KENDRA_INDEX.'
    
    try:
        response = kendra_client.query(IndexId=KENDRA_INDEX, QueryText=question)
    except:
        return None
        
    try:
        website_url = getObjectWebsiteURL(KENDRA_INDEX, response)
    except:
        logger.info('<<Porter>> failed to retrieve url') 

    # kendra_data_stores = kendra_client.list_data_sources(IndexId=KENDRA_INDEX)
    # s3_datastore_id = kendra_data_stores['SummaryItems'][0]['Id']
    # s3_datastore = kendra_client.describe_data_source(Id=s3_datastore_id,IndexId=KENDRA_INDEX)
    # logger.info('<<Porter>> datastore for kendra is %s ', s3_datastore) 
    # bucket_name = s3_datastore['Configuration']['S3Configuration']['BucketName']
    # logger.info('<<Porter>> bucketname is ' + bucket_name) 
    # prefix , object_ext = os.path.splitext(response['ResultItems'][0]['DocumentId'])
    # prefix_split = prefix.split('/')
    # object_name = prefix_split[-1] + object_ext
    # logger.info('<<Porter>> object_name is ' + object_name) 

    # logger.info('<<Porter>> datastore for kendra are %s ', kendra_data_stores) 



    logger.info('<<Porter>> get_kendra_answer() - response = ' + json.dumps(response)) 
    
    #
    # determine which is the top result from Kendra, based on the Type attribue
    #  - QUESTION_ANSWER = a result from a FAQ: just return the FAQ answer
    #  - ANSWER = text found in a document: return the text passage found in the document plus a link to the document
    #  - DOCUMENT = link(s) to document(s): check for several documents and return the links
    #
    
    not_found_msg = "Sorry, I don't have an answer to that at the moment. Please try to rephrase the question, or try another one."
    
    first_result_type = ''
    try:
        first_result_type = response['ResultItems'][0]['Type']
    except KeyError:
        return None

    if first_result_type == 'QUESTION_ANSWER':
        try:
            faq_answer_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
        except KeyError:
            faq_answer_text = not_found_msg

        return faq_answer_text

    
    elif first_result_type == 'ANSWER':
        # return the text answer from the document, plus the URL link to the document
        try:
            if response['ResultItems'][0]['ScoreAttributes']['ScoreConfidence'] != "LOW" : 
                document_title = response['ResultItems'][0]['DocumentTitle']['Text']
                document_excerpt_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
                #document_excerpt_text = response['ResultItems'][0][0]['Text']
                document_url = response['ResultItems'][0]['DocumentURI']
                
                document_excerpt_text = document_excerpt_text.replace("\n","")
                document_excerpt_text = document_excerpt_text.encode("ascii", errors="ignore").decode()
                #document_excerpt_text = re.sub(r'[^\x00-\x7f]',r'', document_excerpt_text)
                
                answer_text = "I found: "
                answer_text += document_excerpt_text + "\n\n"     
                URL =  "URL:" + website_url if website_url else ""
                answer_text+= URL                
                
            else : 
                answer_text = not_found_msg
        except KeyError:
            answer_text = not_found_msg

        return answer_text
    
    elif first_result_type == 'DOCUMENT':
        # return the text answer from the document, plus the URL link to the document
        try:
            if response['ResultItems'][0]['ScoreAttributes']['ScoreConfidence'] != "LOW" : 
                document_title = response['ResultItems'][0]['DocumentTitle']['Text']
                document_excerpt_text = response['ResultItems'][0]['DocumentExcerpt']['Text']
                #document_excerpt_text = response['ResultItems'][0][0]['Text']
                document_url = response['ResultItems'][0]['DocumentURI']
                
                document_excerpt_text = document_excerpt_text.replace("\n","")
                document_excerpt_text = document_excerpt_text.encode("ascii", errors="ignore").decode()
                #document_excerpt_text = re.sub(r'[^\x00-\x7f]',r'', document_excerpt_text)
                
                
                answer_text = "I found: "
                answer_text += document_excerpt_text + "\n\n"
                URL =  "URL:" + website_url if website_url else ""
                answer_text+= URL
                
            else : 
                answer_text = not_found_msg
        except KeyError:
            answer_text = not_found_msg

        return answer_text

    
    # elif first_result_type == 'DOCUMENT':
    #     # assemble the list of document links
    #     document_list = "Here are some documents you could review:\n"
    #     for item in response['ResultItems']:
    #         document_title = None
    #         document_url = None
    #         if item['Type'] == 'DOCUMENT':
    #             if item.get('DocumentTitle', None):
    #                 if item['DocumentTitle'].get('Text', None):
    #                     document_title = item['DocumentTitle']['Text']
    #             if item.get('DocumentId', None):
    #                 document_url = item['DocumentURI']
            
    #         if document_title is not None:
    #             document_list += '-  <' + document_url + '|' + document_title + '>\n'

    #     return document_list

    else:
        return not_found_msg

def getObjectWebsiteURL(KENDRA_INDEX, response):
    
    #access kendra data stores and retrieve bucket name from data source
    kendra_data_stores = kendra_client.list_data_sources(IndexId=KENDRA_INDEX)
    s3_datastore_id = kendra_data_stores['SummaryItems'][0]['Id']
    s3_datastore = kendra_client.describe_data_source(Id=s3_datastore_id,IndexId=KENDRA_INDEX)
    logger.info('<<Porter>> datastore for kendra is %s ', s3_datastore) 
    
    #retrieve bucket_name and object name and use to make boto3 Object
    bucket_name = s3_datastore['Configuration']['S3Configuration']['BucketName']
    logger.info('<<Porter>> bucketname is ' + bucket_name) 
    prefix , object_ext = os.path.splitext(response['ResultItems'][0]['DocumentId'])
    prefix_split = prefix.split('/')
    object_name = prefix_split[-1] + object_ext
    logger.info('<<Porter>> object_name is ' + object_name) 
    
    s3 = boto3.resource('s3')
    object = s3.Object(bucket_name, object_name)
    logger.info('<<Porter>> object is %s', object )
    logger.info('<<Porter>> objectUrl is %s', object.website_redirect_location )
    return object.website_redirect_location


    