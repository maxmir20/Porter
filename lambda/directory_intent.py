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

import time
import logging
import json
import porter_config as porter
import porter_helpers as helpers
import porter_userexits as userexits

# SELECT statement for Count query
COUNT_SELECT = "SELECT distinct {} FROM departments d, addresses a, hours h, dep_phones dp, phones p "
COUNT_JOIN = " WHERE d.addressID = a.id AND h.depID = d.depID AND d.depID = dp.depID AND p.id = dp.phoneID "
COUNT_WHERE = " AND LOWER({}) LIKE LOWER('%{}%') "   

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    logger.debug('<<Porter>> Lex event info = ' + json.dumps(event))

    config_error = helpers.get_porter_config()

    session_attributes = event['sessionAttributes']
    
    if session_attributes is None:
        session_attributes = {}
    
    logger.debug('<<Porter>> lambda_handler: session_attributes = ' + json.dumps(session_attributes))

    if config_error is not None:
        return helpers.close(session_attributes, 'Fulfilled',
            {'contentType': 'PlainText', 'content': config_error})   
    else:
        return count_intent_handler(event, session_attributes)


def count_intent_handler(intent_request, session_attributes):
    method_start = time.perf_counter()
    
    logger.debug('<<Porter>> count_intent_handler: intent_request = ' + json.dumps(intent_request))
    logger.debug('<<Porter>> count_intent_handler: session_attributes = ' + json.dumps(session_attributes))
    
    session_attributes['greetingCount'] = '1'
    session_attributes['resetCount'] = '0'
    session_attributes['finishedCount'] = '0'
    session_attributes['lastIntent'] = 'Directory_intent'

    # Retrieve slot values from the current request
    slot_values = session_attributes.get('slot_values')

    try:
        slot_values = helpers.get_slot_values(slot_values, intent_request)
    except porter.SlotError as err:
        return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': str(err)})   
    
    logger.debug('<<Porter>> "count_intent_handler(): slot_values: %s', slot_values)

    # Retrieve "remembered" slot values from session attributes
    slot_values = helpers.get_remembered_slot_values(slot_values, session_attributes)
    logger.debug('<<Porter>> "count_intent_handler(): slot_values afer get_remembered_slot_values: %s', slot_values)

    # Remember updated slot values
    helpers.remember_slot_values(slot_values, session_attributes)
    
    
    #Max - Build helper to parse medium and alter select query as necessary
    
    # build and execute query
    select_clause = COUNT_SELECT    
    where_clause = COUNT_JOIN
    for dimension in porter.DIMENSIONS:
        slot_key = porter.DIMENSIONS.get(dimension).get('slot')
        if slot_values[slot_key] is not None:
            value = userexits.pre_process_query_value(slot_key, slot_values[slot_key])
            if slot_key == 'Department':
                where_clause += COUNT_WHERE.format(porter.DIMENSIONS.get(dimension).get('column'), value)
            elif slot_key == 'Medium':
                if value == "address":
                    select_clause = COUNT_SELECT.format('address, secondary_address, address_url')
                elif value == "hours":
                    select_clause = COUNT_SELECT.format(value + ', weekend_hours')
                else:
                    select_clause = COUNT_SELECT.format(value)
            else:
                logger.debug('<<Porter>> "something went wrong count_intent_handler(): slot_key is: %s', slot_key)

    
    query_string = select_clause + where_clause
    logger.debug('<<Porter>> "query string is: %s', query_string)

    #runs SQL query on S3 buckets using Athena
    response = helpers.execute_athena_query(query_string)

    rows = response['ResultSet'].get('Rows')

    response_string = ''
    if rows:
        #use helper function to format response string
        response_string = userexits.post_process_string(rows ,slot_values['Department'])

        for i in range(1, len(rows)):
            logger.debug('<<Porter>> "data row is %s', rows[i]['Data'])
            data_rows = rows[i]['Data']
            for j in range(len(data_rows)):
                response_string+= '\n'+data_rows[j]['VarCharValue'] 
    else:
        response_string = 'Could not find the {} for {}'.format(slot_values['Medium'], slot_values['Department'])
        logger.debug('<<Porter>> "no row data in response')

    logger.debug('<<Porter>> "Response Strins is: %s' % response_string) 


    response_string += '.'

    return helpers.close(session_attributes, 'Fulfilled', {'contentType': 'PlainText','content': response_string})   


