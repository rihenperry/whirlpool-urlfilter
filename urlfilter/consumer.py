# sys imports
import json
import utils
from functools import partial

# local imports
import publisher
import transform_payload

log = utils.UrlfilterLogging().getLogger()

# whirlpool-urlfilter consume
def consume_from_parser_queue(channel):
    log.info('invoked {0}'.format(consume_from_parser_queue.__name__))
    on_msg_callback_with_session = partial(on_msg_callback)
    channel.basic_consume('urlfilter.q', on_msg_callback_with_session)
    log.info('consumer listening for messages on urlfilter.q')

def on_msg_callback(channel, method_frame, header_frame, body):
     log.info('delivery tag {}'.format(method_frame.delivery_tag))
     log.info('header_frame {}'.format(header_frame))

     # finally send message by call publisher
    #  msg = {
    #      "1": [{"type": "c", "url": "http://ex1.com/hola"}],
    #      "2": [{"url": "http://ex4.com/new", "type": "nc"}, {"type": "c", "url": "http://ex10.com"}],
    #      "3": [{"url": "http://ex3.com/xyz/def", "type": "nc"}]
    #  };

     msg = transform_payload.add_abs_urls(body)

     bmsg = json.dumps(msg).encode('utf-8')
     pub_confirm = publisher.publish_to_due_queue(channel, bmsg)
     if pub_confirm:
         channel.basic_ack(delivery_tag=method_frame.delivery_tag)
         log.info('message from urlfilter.q acknowledged')
     else:
         channel.basic_nack(delivery_tag=method_frame.delivery_tag)
         log.error('message from urlfilter.q acknowledgement failed. Requeued.')
