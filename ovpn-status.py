import argparse
import logging
import time
import urllib2


class StatusParser:
    def __init__(self, chat, key):
        self.chat = chat
        self.key = key
        self.clients = {}
        pass

    def notify(self, message):
        logging.info(message)
        try:
            urllib2.urlopen(
                'https://api.telegram.org/bot{key}/sendMessage'.format(key=self.key),
                data={
                    'chat_id': self.chat,
                    'parse_mode': 'html',
                    'text': message
                }
            )
        except:
            logging.exception('notify error')

    def parse_clients(self, fp):
        for i in range(3):
            fp.readline()
        clients = {}
        while True:
            line = fp.readline().strip()
            if line.startswith('ROUTING TABLE'):
                break
            client = line.split(',')
            clients[client[1]] = {
                'name': client[0],
                'ip': client[1],
                'recv': client[2],
                'sent': client[3],
                'since': client[4]
            }
        return clients

    def process(self, fp):
        current = self.parse_clients(fp)
        try:
            for idx in current:
                if idx not in self.clients:
                    self.notify("{name} {ip} is connected".format(**current[idx]))

            for idx in self.clients:
                if idx not in current:
                    self.notify("{name} {ip} is disconnected".format(**self.clients[idx]))
        except:
            pass
        self.clients = current
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('-v', dest='debug', action='store_true', default=False, help='Toggle debug logging')
    parser.add_argument('--chat', required=True)
    parser.add_argument('--key', required=True)
    parser.add_argument('-i', '--interval', type=int, default=60)
    parser.add_argument('status_file')

    params = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if params.debug else logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    parser = StatusParser(params.chat, params.key)
    while True:
        logging.debug('parsing {params.status_file}'.format(params=params))
        try:
            with open(params.status_file) as fp:
                parser.process(fp)
        except:
            logging.exception('Error')
        time.sleep(params.interval)