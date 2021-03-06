import logging
import mandrill

from dancedeets import keys

mandrill_client = mandrill.Mandrill(keys.get('mandrill_api_key'))


def send_message(message):
    try:
        result = mandrill_client.messages.send(message=message, async=False)
        logging.info('Message Contents: %s', message)
        logging.info('Message Result: %s', result)
        return result
    except mandrill.Error, e:
        logging.error('A mandrill error occurred: %s: %s', e.__class__, e)
        logging.error('Erroring message is %s', message)
        return None
