import json
import re
import datetime

from vk_audio import Audio_obj


class GetSongUtils(object):
    ans_stupid = None

    def __init__(self, vk_session, uid):
        self.vk_session = vk_session
        self.uid = uid

    def _as_object(self, i):
        q = self.ans_stupid[i]
        song_id = i.split("_")[1]
        owner_id = i.split("_")[0]
        sig = q[1][13].split("/")
        sig = sig[2] + "_" + sig[5]
        return Audio_obj(song_id, owner_id, sig,
                         q[1][3], q[1][4], q[1][5],
                         q[1][14].split(",")[0],
                         self.encode_url, self.vk_session
                         )

    def encode_url(self, url):
        from vk_audio.decoder import decode_audio_url
        return decode_audio_url(url, self.uid)

    def _set_headers(self):
        self.vk_session.http.headers['Upgrade-Insecure-Requests'] = "1"
        self.vk_session.http.cookies.set('remixaudio_background_play_time_', '0')
        self.vk_session.http.cookies.set('remixaudio_background_play_time_limit', '1800')
        self.vk_session.http.cookies.set('remixaudio_show_alert_today', '0')
        self.vk_session.http.cookies.set('remixff', '10')
        self.vk_session.http.cookies.set('remixmaudioq', '')
        self.vk_session.http.cookies.set('remixaudio_date', datetime.datetime.now().date().strftime("%Y-%m-%d"))
        self.vk_session.http.cookies.set('remixmdevice', '1280/800/1/!!-!!!!')
        self.vk_session.http.headers['X-Requested-With'] = 'XMLHttpRequest'

    def get_vk_songs(self):
        self._set_headers()
        del self.vk_session.http.headers['X-Requested-With']
        text = self.vk_session.http.get(
            f"https://m.vk.com/audio{('s' + str(self.uid)) if self.uid is not None else ''}").text
        self.vk_session.http.headers['X-Requested-With'] = 'XMLHttpRequest'
        all_audio = re.findall(
            '"_cache":(.+?),"soft_filter":true|false,"need_invalid_keys":true|false,"top_len":\d+,', text)
        try:
            all_audio = all_audio[0][:all_audio[0].rfind(',')]
            self.ans_stupid = json.loads(all_audio)
        except:
            self.ans_stupid = json.loads(all_audio[0] if len(all_audio) > 0 and len(all_audio[0]) != 0 else "{}")
        return list(map(self._as_object, self.ans_stupid))
