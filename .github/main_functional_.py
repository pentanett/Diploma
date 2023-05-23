


import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
#from random import randrange
from base_info_ import my_token, side_profile_token


from my_database_ import save_vk_user, look_for_pairs_in_database, add_to_database

vk = vk_api.VkApi(token=my_token)
user_vk = vk_api.VkApi(token=side_profile_token)
long_poll = VkLongPoll(vk)

profile_pairs = {}


#изменено согласно замечаниям проверяющего
def message_send(user_id, message):
    vk.method("messages.send", {"user_id": user_id, "message": message, "random_id": get_random_id(), })


#def message_with_picture(user_id, message, photo_id):
 #   vk.method("messages.send", {"user_id": user_id, "message": message, "random_id": get_random_id(), 'attachment': f"photo{photo_id}", })


def unable_profile(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "is_closed"})
    return response[0].get("is_closed")


def profile_id_attributes(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "sex,bdate,city,relation"})[0]
    try:
        return {"user_id": response.get("id"), "sex": response.get("sex"), "age": response.get("age"),
                "city_id": response.get("city").get("id")}
    except AttributeError:
        return None



def unable_profile(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "is_closed"})
    return response[0].get("is_closed")


def profile_id_attributes(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "sex,bdate,city,relation"})[0]
    try:
        return {"user_id": response.get("id"), "sex": response.get("sex"), "age": response.get("age"),
                "city_id": response.get("city").get("id")}
    except AttributeError:
        return None


def mostliked_photos(user_id):
    try:
        response = user_vk.method("photos.get", {"owner_id": user_id, "album_id": "profile", "extended": 1})
        photos = []
        for each_case in response.get("items"):
            case = {"photo_id": f"{each_case.get('owner_id')}_{each_case.get('id')}", "likes_count": each_case.get("likes").get("count"),
                    "comments_count": each_case.get("comments").get("count")}
            photos.append(case)
        photos.sort(key=lambda dictionary: dictionary["likes_count"], reverse=True)
        return photos[:3]
    except vk_api.exceptions.ApiError:
        pass


response = user_vk.method


def alternative_pairs_profiles(user_id):
    global profile_pairs
    user_data = profile_id_attributes(user_id)
    request_data = {"count": 100, "status": 6}
    if user_data.get("age") is not None:
        request_data.update({"age_from": user_data.get("age") - 5})
        request_data.update({"age_to": user_data.get("age") + 5})
    if user_data.get("city_id") is not None:
        request_data.update({"city_id": user_data.get("city_id")})
    default_sex = 0
    if user_data.get("sex") == 1:
        default_sex = 2
    elif user_data.get("sex") == 2:
        default_sex = 1
    request_data.update({"sex": default_sex})
    response = user_vk.method("users.search", request_data, {"offset": 0, "count": 20})
    alternative_pairs = []
    db_pairs_id = look_for_pairs_in_database(user_id)
    for each_response in response.get("items"):
        if unable_profile(each_response.get("id")) is False and each_response.get("id") not in db_pairs_id:
            alternative_pairs.append(each_response.get("id"))
    profile_pairs.update({user_id: alternative_pairs})


def pairs_selection(user_id):
    global profile_pairs
    picked_pairs = profile_pairs.get(user_id)
    if picked_pairs is not None and len(picked_pairs) > 0:
        picked_pairs_id = picked_pairs.pop(0)
        add_to_database(user_id, picked_pairs_id)
        profile_pairs.update({user_id: picked_pairs})
        return picked_pairs_id
    else:
        return None


def get_domain_by_user_id(user_id):
    response = vk.method("users.get", {"user_id": user_id, "fields": "domain"})
    return f"vk.com/{response[0].get('domain')}"



start_dialogue_command = "/команда искать"
next_searching = "/команда продолжать"
no_profile_data = "/нет информации в профиле"

def start_dialogue_func(text):
    if text.lower() == start_dialogue_command:
        return True
    else:
        return False


def next_searching_func(text):
    if text.lower() == next_searching:
        return True
    else:
        return False

def no_profile_data(text):
    if text.lower() == no_profile_data:
        return True
    else:
        return False


for event in long_poll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg_text = event.text
            person_id = event.user_id
            if unable_profile(person_id):
                message_send(person_id, "Требуется открыть профиль")
            else:
                if start_dialogue_func(msg_text):
                    save_vk_user(person_id)
                    alternative_pairs_profiles(person_id)
                    message_send(event.user_id,


                             f"Возможные варианты найдены, нажмите {next_searching} чтобы "
                             f"ознакомиться "
                             f"{start_dialogue_command}")

                elif next_searching_func(msg_text):
                    connected_pair = pairs_selection(person_id)
                    if connected_pair is None:
                        message_send(event.user_id,

                                 f"Мы не смогли подобрать вам пару, возможно список анкет закончился, попробуйте "
                                 f"{start_dialogue_command}")
                    else:
                        message_send(event.user_id,
                                 f"Мы подобрали вам пару! {get_domain_by_user_id(connected_pair)}")
                        connected_pair_image = mostliked_photos(connected_pair)
                        for photo in connected_pair_image:
                            message_send(event.user_id, "Фото", photo.get("photo_id"))
                        message_send(event.user_id,

                                 f"Чтобы показать следующую анкету введите "
                                 f"{next_searching}")

                else:
                    message_send(event.user_id, {no_profile_data})


