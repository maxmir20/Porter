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
import time
import logging

#
# See additional configuration parameters at bottom 
#

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# adjust dimension values as necessary prior to inserting into where clause
def pre_process_query_value(key, value):
    logger.debug('<<Porter>> pre_process_query_value(%s, %s)', key, value)
    value = value.replace("'", "''")    # don't allow any 's in WHERE clause
    if key == 'Department':
        format_list = value.split(' ')
        format_list = [x.capitalize() for x in format_list]
        value = ' '.join(format_list)
    elif key == 'Medium':
        value = value.lower()
        # else:
        #     return value
        

    logger.debug('<<BIBot>> pre_process_query_value() - returning key=%s, value=%s', key, value)
       
    return value


# adjust slot values as necessary after reading from intent slots

#Max: Change as appropriate
def post_process_string(rows, department):
    medium = rows[0]['Data'][0]['VarCharValue']

    response_string = "The " if medium != 'hours' else ""
    plural = True if len(rows) > 2 or medium == 'hours' else False
    
    medium = MEDIUM_ALTERNATE[medium] if medium in MEDIUM_ALTERNATE else medium
    response_string += medium + '{} for '.format('s' if plural else '')
    
    response_string +=  'the ' + department if department in THE_DEPARTMENTS else department 
    response_string += ' {}:'.format('are' if plural else 'is')

    return response_string


MEDIUM_ALTERNATE = {
    'hours': 'Business hour',
    'phone': 'phone number'
}


THE_DEPARTMENTS = {
    'Fire Department', 
    'City of Porterville',
    'Police', 
    'DMV',
    'ADA',
    'First Time',
    'Airport',
    'Transit Department'
}


