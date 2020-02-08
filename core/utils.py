from vk_api import VkApi, audio


def get_vk_auth(user):
    login = user.username
    vk_session = VkApi(login=login, password=user.vk_password, config_filename='config.json')
    vk_session.auth()
    vk_session.get_api()
    return vk_session


def get_vk_songs(vk_session, user_id=None):
    vk_audio = audio.VkAudio(vk_session)
    return vk_audio.get(owner_id=user_id) if user_id else vk_audio.get()


def get_vk_user_data(vk_session):
    return vk_session.method('users.get')[0]
