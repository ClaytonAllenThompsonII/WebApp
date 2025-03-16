# Passed Testing

import logging

# Configure detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(pathname)s:%(lineno)d - %(message)s')

def lambda_handler(event, context):
    logging.info("Lambda handler started - Phase 1: Static Response Test")
    
    # Simply return a static response
    static_response = {'status': 'success', 'message': 'Static response received.'}
    
    logging.info(f"Returning static response: {static_response}")
    return static_response