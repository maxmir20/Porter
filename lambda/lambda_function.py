import logging
import json
import helpers
import config


logger = logging.getLogger()
logger.setLevel(logging.INFO)

#FOR KENDRA INTENT
def lambda_handler(event, context):
    logger.info('Lex event info = ' + json.dumps(event))

    session_attributes = event.get('sessionAttributes', None)

    if session_attributes is None:
        session_attributes = {}    
    
    logger.debug('<<help_desk_bot> lambda_handler: session_attributes = ' + json.dumps(session_attributes))
    

    return fallback_intent_handler(event, session_attributes)



def fallback_intent_handler(intent_request, session_attributes):
    # session_attributes['fallbackCount'] = '0'
    # fallbackCount = helpers.increment_counter(session_attributes, 'fallbackCount')
    
    # try:
    #     slot_values = helpers.get_latest_slot_values(intent_request, session_attributes)
    # except config.SlotError as err:
    #     return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'CustomPayload','content': str(err)})   

    # logger.debug('<<help_desk_bot>> fallback_intent_handler(): slot_values = %s', json.dumps(slot_values))

    query_string = ""
    if intent_request.get('inputTranscript', None) is not None:
        query_string += intent_request['inputTranscript']

    logger.debug('fallback_intent_handler(): calling get_kendra_answer(query="%s")', query_string)
        
    kendra_response = helpers.get_kendra_answer(query_string)
    if kendra_response is None:
        response = "Sorry, I was not able to understand your question."
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'CustomPayload','content': response})
    else:
        logger.debug('fallback_intent_handler(): kendra_response = %s', kendra_response)
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'CustomPayload','content': kendra_response})
