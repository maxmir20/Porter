#
# Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

#FOR DIRECTORY INTENT FUNCTION
import boto3
import time
import logging
import json
import pprint
import os
import porter_config as porter
import porter_userexits as userexits

#
# See additional configuration parameters at bottom 
#

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def get_porter_config():
    global ATHENA_DB
    global ATHENA_OUTPUT_LOCATION

    try:
        ATHENA_DB = os.environ['ATHENA_DB']
        ATHENA_OUTPUT_LOCATION = os.environ['ATHENA_OUTPUT_LOCATION']
    except KeyError:
        return 'I have a configuration error - please set up the Athena database information.'

    logger.debug('<<Porter>> athena_db = ' + ATHENA_DB)
    logger.debug('<<Porter>> athena_output_location = ' + ATHENA_OUTPUT_LOCATION)


def execute_athena_query(query_string):
    start = time.perf_counter()

    athena = boto3.client('athena')

    response = athena.start_query_execution(
        QueryString=query_string,
        QueryExecutionContext={'Database': ATHENA_DB},
        ResultConfiguration={
            'OutputLocation': ATHENA_OUTPUT_LOCATION,
        }
    )

    query_execution_id = response['QueryExecutionId']

    status = 'RUNNING'
    while (status == 'RUNNING' or status == 'QUEUED'):
        response = athena.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        if (status == 'RUNNING' or status == 'QUEUED'):
            #logger.debug('<<Porter>> query status = ' + status + ': sleep 200ms') 
            time.sleep(0.200)

    duration = time.perf_counter() - start
    duration_string = 'query duration = %.0f' % (duration * 1000) + ' ms'
    logger.debug('<<Porter>> query status = ' + status + ', ' + duration_string) 

    response = athena.get_query_results(QueryExecutionId=query_execution_id)
    logger.debug('<<Porter>> query response = ' + json.dumps(response)) 

    return response


def get_slot_values(slot_values, intent_request):
    if slot_values is None:
        slot_values = {key: None for key in porter.SLOT_CONFIG}
    
    slots = intent_request['currentIntent']['slots']

    #retrieve Lex slot details so we can look at enumerated values(synonyms) 
    #NOTE: If this slows down retrieval too much put in config code
    # lex = boto3.client('lex-models')
    # logger.debug('<<Porter>> client is for %s', lex)

    # logger.debug('<<Porter>> slot details for %s = %s', key, response)
    # logger.debug('<<Porter>> slot dictionary for %s = %s', key, original_values_dictionary)

    for key,config in porter.SLOT_CONFIG.items():
        slot_values[key] = slots.get(key)
        logger.debug('<<Porter>> retrieving slot value for %s = %s', key, slot_values[key])
        
        if slot_values[key]:
            if config.get('type', porter.ORIGINAL_VALUE) == porter.TOP_RESOLUTION:
            

            #unused code for transforming synonyms of slot intents if necessary
                # slot_type =  lex.get_slot_type(name=key, version = '$LATEST')
                # #build dictionary for easy slot intent check of original values
                # original_values_dictionary = {}
                # #goes through each key-value pair of our slot_types enumeration values and compares original value with synonyms if exists
                # for slot_type_value in slot_type['enumerationValues']:
                #     #sets dictionary key to the slot_type value and value to the slot_type synonym if it exists
                #     if 'synonyms' in slot_type_value:
                #         for synonym in slot_type_value['synonyms']:
                #             original_values_dictionary[synonym] = slot_type_value['value']
                #     original_values_dictionary[slot_type_value['value']] = slot_type_value['value']
                #     # original_values_dictionary[x['value']] = x['synonyms'] if 'synonyms' in x else []
                # logger.debug('<<Porter>> slot_type values dictionary %s', original_values_dictionary)

                # #synonym transformation: passes in our slot_value (e.g. address or police)
                # slot_values[key] = check_for_synonyms(slot_values[key], original_values_dictionary)
                logger.debug('<<Porter>> slot value and key is %s : %s ', key, slot_values[key])

                
                # get the resolved slot name of what the user said/typed
                if len(intent_request['currentIntent']['slotDetails'][key]['resolutions']) > 0:
                    slot_values[key] = intent_request['currentIntent']['slotDetails'][key]['resolutions'][0]['value']
                else:
                    errorMsg = porter.SLOT_CONFIG[key].get('error', 'Sorry, I don\'t understand "{}".')
                    raise porter.SlotError(errorMsg.format(slots.get(key)))
                
            slot_values[key] = userexits.post_process_slot_value(key, slot_values[key])
    
    return slot_values

#unneccessary
# def check_for_synonyms(value, enumeratedValuesDict):
#     if value in enumeratedValuesDict:
#         logger.debug('<<Porter>> %s is a value or a synonym', value)
#         logger.debug('<<Porter>> new value is %s ', enumeratedValuesDict[value])

#         return enumeratedValuesDict[value]
#     else:
#         logger.debug('<<Porter>> %s is not recognized as a synonym or value', value)

#         # #for each original value in our dictionary (e.g. Police, Fire, etc.), go through the list available and see if there's a match
#         # for slot_type_value in enumeratedValuesDict:
#         #     for j in len(enumeratedValuesDict[slot_type_value]):
#         #         #if theres a match, 
#         #         if enumeratedValuesDict[slot_type_value][j] == value:
#         #             logger.debug('<<Porter>> %s is a synonym for %s ', value, slot_type_value)
#         #             return slot_type_value
        
#         # logger.debug('<<Porter>> %s is not recognized as a synonym', value)
#         return value

def get_remembered_slot_values(slot_values, session_attributes):
    logger.debug('<<Porter>> get_remembered_slot_values() - session_attributes: %s', session_attributes)

    str = session_attributes.get('rememberedSlots')
    remembered_slot_values = json.loads(str) if str is not None else {key: None for key in porter.SLOT_CONFIG}
    
    if slot_values is None:
        slot_values = {key: None for key in porter.SLOT_CONFIG}
    
    logger.debug('<<Porter>> get_remembered_slot_values() - slot_values: %s', slot_values)
    logger.debug('<<Porter>> get_remembered_slot_values() - remembered_slot_values: %s', remembered_slot_values)
    for key,config in porter.SLOT_CONFIG.items():
        if config.get('remember', False):
            logger.debug('<<Porter>> get_remembered_slot_values() - slot_values[%s] = %s', key, slot_values.get(key))
            logger.debug('<<Porter>> get_remembered_slot_values() - remembered_slot_values[%s] = %s', key, remembered_slot_values.get(key))
            if slot_values.get(key) is None:
                slot_values[key] = remembered_slot_values.get(key)
                
    return slot_values


def remember_slot_values(slot_values, session_attributes):
    if slot_values is None:
        slot_values = {key: None for key,config in porter.SLOT_CONFIG.items() if config['remember']}
    session_attributes['rememberedSlots'] = json.dumps(slot_values)
    logger.debug('<<Porter>> Storing updated slot values: %s', slot_values)           
    return slot_values


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    
    logger.debug('<<Porter>> "Lambda fulfillment function response = \n' + pprint.pformat(response, indent=4)) 

    return response


def increment_counter(session_attributes, counter):
    counter_value = session_attributes.get(counter, '0')

    if counter_value: count = int(counter_value) + 1
    else: count = 1
    
    session_attributes[counter] = count

    return count


