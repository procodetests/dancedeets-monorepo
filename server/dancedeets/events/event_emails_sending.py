import logging
from dancedeets import render_server
from dancedeets.events import eventdata
from dancedeets.logic import api_format
from dancedeets.mail import mandrill_api


def send_event_add_emails(event_id):
    event = eventdata.DBEvent.get_by_id(event_id)
    emails = get_emails_for_event(event)
    for address in emails:
        try:
            email_contents = email_for_event(address, event, should_send=False)
            logging.info('Sent email: %s', email_contents)
        except NoEmailException as e:
            logging.info("Not sending email for event %s to address %s: %s", event.id, address, e)
            continue
        except Exception:
            logging.exception("Not sending email for event %s to address %s", event.id, address)
            continue


def email_for_event(email, event, should_send=False):
    locale = 'en_US'
    api_event = api_format.canonicalize_event_data(event, (2, 0))
    props = {
        'currentLocale': locale.replace('_', '-'),
        'event': api_event,
        'emailTo': email,
    }
    response = render_server.render_jsx('eventAddMail.js', props, static_html=True)
    if response.error:
        message = 'Error rendering weeklyMail.js: %s' % response.error
        logging.error(message)
        raise NoEmailException(message)
    mjml_response = render_server.render_mjml(response.markup)
    rendered_html = mjml_response['html']

    message = {
        'from_email': 'events@dancedeets.com',
        'from_name': 'DanceDeets Events',
        'subject': 'Event Added',  # TODO
        'to': [{
            'email': email,
            'type': 'to',
        }],
        'html': rendered_html,
        'metadata': {
            'event_id': event.id,
            'email_type': 'add-event',
        },
        'tags': 'add-event',
    }
    if should_send:
        # And send the message now.
        mandrill_api.send_message(message)
    return message
