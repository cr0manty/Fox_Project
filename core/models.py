import json
import random

from django.db import models
from vk_api import VkApi, TwoFactorError, TWOFACTOR_CODE, BadPassword, CAPTCHA_ERROR_CODE, Captcha, AuthError, \
    AccountBlocked, PasswordRequired
from vk_api.utils import search_re, cookies_to_list
from vk_api.vk_api import RE_AUTH_HASH, RE_CAPTCHAID, RE_LOGIN_HASH


class Log(models.Model):
    from_user = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    exception = models.TextField(blank=True, null=True)
    additional_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return '{} - {}'.format(self.from_user, self.created_at)


class RQLog(models.Model):
    from_user = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_exception = models.BooleanField(default=False)
    exception_text = models.TextField(null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.from_user, self.created_at)


class TelegramBotLogs(models.Model):
    LOG_TYPE = (
        (0, 'Error'),
        (1, 'Not Sended'),
        (2, 'Not Found'),
        (3, 'Success')
    )

    chat_id = models.IntegerField(blank=True)
    group = models.BooleanField(default=False)
    log_type = models.IntegerField(choices=LOG_TYPE, default=0)
    content = models.TextField(blank=True, null=True)
    exception = models.TextField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_kwargs(message, e='', log_type=0):
        return {
            'chat_id': message.chat.id,
            'group': message.chat.type == 'group',
            'log_type': log_type,
            'content': message.text,
            'exception': e,
            'user_id': message.from_user.id,
            'username': message.from_user.username,
            'language': message.json['from'].get('language_code')
        }

    def __str__(self):
        return '{} ({})'.format(self.username or '', self.created_at)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Telegram Bot Log'
        verbose_name_plural = 'Telegram Bot Logs'


class VKApiTwoStep(VkApi):

    def _vk_login(self, captcha_sid=None, captcha_key=None):
        """ Авторизация ВКонтакте с получением cookies remixsid

        :param captcha_sid: id капчи
        :type captcha_key: int or str

        :param captcha_key: ответ капчи
        :type captcha_key: str
        """

        self.logger.info('Logging in...')

        if not self.password:
            raise PasswordRequired('Password is required to login')

        self.http.cookies.clear()

        # Get cookies
        response = self.http.get('https://vk.com/')

        values = {
            'act': 'login',
            'role': 'al_frame',
            '_origin': 'https://vk.com',
            'utf8': '1',
            'email': self.login,
            'pass': self.password,
            'lg_h': search_re(RE_LOGIN_HASH, response.text)
        }

        if captcha_sid and captcha_key:
            self.logger.info(
                'Using captcha code: {}: {}'.format(
                    captcha_sid,
                    captcha_key
                )
            )

            values.update({
                'captcha_sid': captcha_sid,
                'captcha_key': captcha_key
            })

        response = self.http.post('https://login.vk.com/', values)

        if 'onLoginCaptcha(' in response.text:
            self.logger.info('Captcha code is required')

            captcha_sid = search_re(RE_CAPTCHAID, response.text)
            captcha = Captcha(self, captcha_sid, self._vk_login)

            return self.error_handlers[CAPTCHA_ERROR_CODE](captcha)

        if 'onLoginReCaptcha(' in response.text:
            self.logger.info('Captcha code is required (recaptcha)')

            captcha_sid = str(random.random())[2:16]
            captcha = Captcha(self, captcha_sid, self._vk_login)

            return self.error_handlers[CAPTCHA_ERROR_CODE](captcha)

        if 'onLoginFailed(4' in response.text:
            raise BadPassword('Bad password')

        if 'act=authcheck' in response.text:
            self.logger.info('Two factor is required')

            response = self.http.get('https://vk.com/login?act=authcheck')

            return self._pass_twofactor(response)

        if self._sid:
            self.logger.info('Got remixsid')

            self.storage.cookies = cookies_to_list(self.http.cookies)
            self.storage.save()
        else:
            raise AuthError(
                'Unknown error. Please send bugreport to vk_api@python273.pw'
            )

        response = self._pass_security_check(response)

        if 'act=blocked' in response.url:
            raise AccountBlocked('Account is blocked')

    def _pass_twofactor(self, auth_response):
        """ Двухфакторная аутентификация

        :param auth_response: страница  с приглашением к аутентификации
        """

        if not self.auth_hash:
            self.auth_hash = search_re(RE_AUTH_HASH, auth_response.text)
            return self.auth_hash

        code, remember_device = self.error_handlers[TWOFACTOR_CODE]()

        values = {
            'act': 'a_authcheck_code',
            'al': '1',
            'code': code,
            'remember': int(remember_device),
            'hash': self.auth_hash,
        }

        response = self.http.post('https://vk.com/al_login.php', values)
        data = json.loads(response.text.lstrip('<!--'))
        status = data['payload'][0]

        if status == '4':  # OK
            path = json.loads(data['payload'][1][0])
            return self.http.get('https://vk.com' + path)

        elif status in [0, '8']:  # Incorrect code
            return self._pass_twofactor(auth_response)

        elif status == '2':
            raise TwoFactorError('Recaptcha required')

        raise TwoFactorError('Two factor authentication failed')


class VKAuthMixin(object):
    captcha_key = None
    captcha_url = None
    captcha_sid = None

    def auth_handler(self):
        key = input()
        return key, False
        # if self.two_step_auth is not None:
        #     auth = self.two_step_auth
        #     self.two_step_auth = None
        #     return auth, True
        # self.two_step_auth_need = True

    def captcha_handler(self, captcha):
        if self.captcha_key and self.captcha_sid:
            captcha.sid = self.captcha_sid
            self.captcha_key, self.captcha_sid = None, None
            return captcha.try_again(self.captcha_key)
        else:
            self.captcha_url, self.captcha_sid = captcha.get_url(), captcha.sid

    def try_auth(self, post, username, password=None, token=None):
        try:
            if not password and not token:
                return

            self.captcha_key = post.get('captcha')
            self.captcha_sid = post.get('sid')

            if token:
                vk_session = VkApi(login=username, config_filename='config.json', token=token,
                                   captcha_handler=self.captcha_handler, auth_handler=self.auth_handler)
            else:
                vk_session = VkApi(login=username, config_filename='config.json', password=password,
                                   captcha_handler=self.captcha_handler,
                                   auth_handler=self.auth_handler)
            vk_session.auth(token_only=True)
            return vk_session
        except Exception as e:
            Log.objects.create(exception=e, additional_text=username)
            return None


class TelegramLogs(models.Model):
    chat_id = models.IntegerField()
    is_group = models.BooleanField(default=False)
    user_id = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=16, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def create_object(message):
        is_group = message.chat.type == 'group'
        try:
            TelegramLogs.objects.get(chat_id=message.chat.id, user_id=message.from_user.id,
                                     is_group=is_group)
        except TelegramLogs.DoesNotExist:
            TelegramLogs.objects.create(chat_id=message.chat.id, user_id=message.from_user.id,
                                        username=message.from_user.username, is_group=is_group,
                                        language=message.from_user.language_code)
