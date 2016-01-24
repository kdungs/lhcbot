from flask import (Flask, g, jsonify, redirect, request)
from io import BytesIO
from random import choice
import os
import requests

from bot import SimpleBot

TELEGRAM_BOT_NAME = os.getenv('TELEGRAM_BOT_NAME')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


class ImageRelayBot(SimpleBot):
    def __init__(self, token, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sendurl = 'https://api.telegram.org/bot{}/sendPhoto'.format(token)

    def _send_image(self, chat_id, image_file, caption=None):
        res = requests.post(self.sendurl,
                            data={'chat_id': chat_id,
                                  'caption': caption},
                            files={'photo': ('photo.png', image_file)})
        return '{}'.format(caption)

    def _relay_image_action(self, image_url, caption):
        from bot import get_

        def relay_image_action_impl(_, request):
            img = requests.get(image_url)
            if img.ok:
                chat_id = get_(request, 'message', 'chat', 'id')
                if chat_id is not None:
                    self._send_image(chat_id, BytesIO(img.content), caption)

        return relay_image_action_impl

    def add_image_action(self, name, url, caption):
        self.add_action(name, self._relay_image_action(url, caption))


def vs(fn):
    return 'https://vistar-capture.web.cern.ch/vistar-capture/{}'.format(fn)


pages = {
    'ADE': (vs('ade.png'), 'ADE'),
    'CPS': (vs('cps.png'), 'CPS'),
    'CPSBLM': (vs('cpsblm.png'), 'CPS BLM'),
    'CTF': (vs('ctf.png'), 'CTF'),
    'CTF3Operation': (vs('ctfgen.png'), 'CTF3 Operation'),
    'GPS': (vs('gps.png'), 'GPS'),
    'HRS': (vs('hrs.png'), 'HRS'),
    'LARGER1': (vs('larger1.png'), 'SPS LARGER 1'),
    'LARGER2': (vs('larger2.png'), 'SPS LARGER 2'),
    'LARGER3': (vs('larger3.png'), 'SPS LARGER 3'),
    'LARGER4': (vs('larger4.png'), 'SPS LARGER 4'),
    'LEIR': (vs('leir.png'), 'LEIR'),
    'LHC1': (vs('lhc1.png'), 'LHC Page 1'),
    'LHC2': (vs('lhc2.png'), 'LHC Cryogenics'),
    'LHC3': (vs('lhc3.png'), 'LHC Operation'),
    'LHCABORTGAP': (vs('lhcabortgap.png'), 'LHC BLM Abort Gap'),
    'LHCBDS': (vs('lhcbds.png'), 'LHC Beam Dump'),
    'LHCBLMDiamond': (vs('lhcdiamond.png'), 'LHC BLM Diamond'),
    'LHCBSRT': (vs('lhcbsrt.png'), 'LHC BSRT (temporary)'),
    'LHCCMS': ('https://cmspage1.web.cern.ch/cmspage1/data/page1.png',
               'LHC CMS Experiment'),
    'LHCCOLLB1': (vs('lhccolli1.png'), 'LHC Collimator Beam 1'),
    'LHCCOLLB2': (vs('lhccolli2.png'), 'LHC Collimator Beam 2'),
    'LHCCOLLI': (vs('lhccolli.png'), 'LHC Collimators Summary'),
    'LHCCONFIG': (vs('lhcconfig.png'), 'LHC Configuration'),
    'LHCCOORD': (vs('lhccoord.png'), 'LHC Coordination'),
    'LHCDASHBOARD': ('https://lhcdashboard-images.web.cern.ch/' +
                     'lhcdashboard-images/images/lhc/prod/dashboard.png',
                     'LHC Dashboard'),
    'LHCEXPMAG': (vs('lhcexpmag.png'), 'LHC Exp Magnets'),
    'LHCLUMINOSITY': (vs('lhclumi.png'), 'LHC Luminosity'),
    'LHCRFTiming': (vs('lhcrftiming.png'), 'LHC RF Timing'),
    'LHCfExperiment': (vs('lhcf.png'), 'LHCf Experiment'),
    'LIN': (vs('lin.png'), 'Linac II'),
    'Linac3': (vs('ln3.png'), 'Linac 3'),
    'PEA': (vs('pea.png'), 'CPS EAST Area'),
    'PSB': (vs('psb.png'), 'PSB'),
    'SPS1': (vs('sps1.png'), 'SPS Page 1'),
    'T9_CPS_EAST': (vs('t9blfs.png'), 'T9 BLFS')
}
bot = ImageRelayBot(TELEGRAM_BOT_TOKEN)
for key, (url, title) in pages.items():
    bot.add_image_action(key.lower(), url, title)


app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    return redirect('https://telegram.me/{}'.format(TELEGRAM_BOT_NAME))


@app.route('/f6635aa6ef2662237084a193e33d06bcc27bcc31/', methods=['POST'])
def handle():
    resp = bot.respond(request.json)
    if resp is None:
        return 'OK'
    return jsonify(resp)


if __name__ == '__main__':
    app.run()
