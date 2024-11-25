import requests
import json
import pandas as pd
import os
from dotenv import load_dotenv



def tide_add_record(headers, id_campaign, phone_reciver, ext_id, dialplan=None, priority=False, priotiry_num=0):
    # method: POST
    # dodanie rekordu do kampanii, domyślnie bez priorytetu, phone sender nie można ustawić z tego poziomu
    # przykładowa zwrotka:
    # {'Contacts':
    # [{'ID': 1, 'ContactsID': 51824446, 'ExternalID': 1000000012, 'PhoneNumber': '603246424', 'Status': 0}]}
    json_data = {
        'Campaign': {
            'CampaignsID': id_campaign
        },
        # 'CustomerPhoneNumber': phone_sender,
        'VoiceDialPlansID': dialplan,
        "Priority": priority,
        "PriorityValue": priotiry_num,
        'PhoneNumbers': [
            {
                'Number': phone_reciver,
                'ExternalID': ext_id
            }
        ]
    }

    response = requests.post('https://tidecc.tideplatformgate.com/CallCenterCampaignsContactsInsert',
                             headers=headers,
                             json=json_data,
                             timeout=1)

    data = response.json()

    return data


def tide_close_record(headers, rec_ext_id):
    # method: POST
    # zakmnięcie rekordu po id (external)
    json_data = {
        'Contacts': [
            {
                'ID': {
                    # 'ID': rec_id,
                    'ExternalID': rec_ext_id,
                }
            },
        ],
    }

    response = requests.post('https://tidecc.tideplatformgate.com/CallCenterCampaignsContactsClose',
                             headers=headers,
                             json=json_data,
                             timeout=1)

    data = response.json()
    return data


def tide_open_record(headers, rec_ext_id):
    # method: POST
    # otwarcie rekordu po id (external)
    json_data = {
        'Contacts': [
            {
                # 'ID': rec_id,
                'ExternalID': rec_ext_id,
            },
        ],
    }

    response = requests.post('https://tidecc.tideplatformgate.com/CallCenterCampaignsContactsOpen',
                             headers=headers,
                             json=json_data,
                             timeout=1)

    data = response.json()
    return data


def tide_get_campaign_records(headers, id_campaign):
    # method: POST
    # lista rekordów z kampanii (po ID, opcjonalnie można dodać ID rekordu, czasy od/do)
    json_data = {
        'Campaign': {
            'CampaignsID': id_campaign,
            # 'CampaignsExternalID': 0,
        },
        # 'DateTimeFrom': '2024-01-24T00:00:00.000Z',
        # 'DateTimeTo': '2024-10-24T12:00:00.000Z',
        # 'IDs': [
        #     {
        #         'ID': 0,
        #         'ExternalID': 0,
        #     },
        # ],
    }

    response = requests.post('https://tidecc.tideplatformgate.com/CallCenterCampaignsContactsGet',
                             headers=headers,
                             json=json_data,
                             timeout=.01)

    data = response.json()
    return data


def tide_stop_campaign(headers, id_campaign):
    # method: POST
    # zatrzymuje kampanie (nie będzie dostępna z poziomu aplikacji tide do wydzwonienia)
    # można dodać rekord do kampanii, ale nie wydzwoni się, przyjmuje id kampanii
    json_data = {
        'Campaign': {
            'CampaignsID': id_campaign  # id kampanii
        }
    }

    response = requests.post('https://tidecc.tideplatformgate.com/CallCenterCampaignsStop',
                             headers=headers,
                             json=json_data,
                             timeout=.01)

    data = response.json()
    return data


def tide_start_campaign(headers, id_campaign):
    # method: POST
    # jeśli kampania została zamknięta, to tutaj ją otwieramy, przyjmuje id kampanii
    # przykładowe zwrotki: {'Description': 'Success'}, {'Error': 3, 'Description': 'Kampania nie została znaleziona'}
    json_data = {
        'Campaign': {
            'CampaignsID': id_campaign  # id kampanii
        }
    }

    response = requests.post('https://tidecc.tideplatformgate.com/CallCenterCampaignsStart',
                             headers=headers,
                             json=json_data,
                             timeout=.01)

    data = response.json()
    return data


def tide_list_campaings(headers):
    # method: GET
    # wszystkie niezamknięte kampanie - jeśli kampanie zamknięmy, nie będzie tutaj widoczna
    response = requests.get('https://tidecc.tideplatformgate.com/CallCenterCampaignsActiveList',
                            headers=headers,
                            timeout=.01)
    data = response.json()

    return data


def tide_get_campaign_status(headers, id_campaign):
    # method: POST
    # statusy kampanii - podsumowanie wydzwonień i statusów
    # zwrotka w przypadku błędnego id: {'Error': 3, 'Description': 'Nie znaleziono kampanii'}
    json_data = {
        'Campaign': {
            'CampaignsID': id_campaign  # id kampanii
        }
    }

    response = requests.post('https://tidecc.tideplatformgate.com/CallCenterCampaignsStatusGet',
                             headers=headers,
                             json=json_data)

    data = response.json()
    return data


def tide_get_token(headers):
    # method: POST
    # logowanie do API Tide, zwraca tokeny do autoryzacji, odświeżania
    load_dotenv()

    api_login = os.getenv('API_USERNAME')
    api_password = os.getenv('API_PASSWORD')

    json_data = {
        'login': api_login,
        'password': api_password
    }

    response = requests.post('https://tidecc.tideplatformgate.com/Login',
                             headers=headers,
                             json=json_data)

    data = response.json()

    token = data['AccessToken']
    refresh_token = data['RefreshToken']
    date = data['ExpirationDateTime']

    return token, refresh_token, date


def tide_refresh_token(token, headers):
    # method: POST
    # zwraca odświeżony token
    json_data = {
        'login': 'hyperionapiraporty@kancelariahyperion.pl',
        'refreshToken': token,
    }

    response = requests.post('https://tidecc.tideplatformgate.com/RefreshToken',
                             headers=headers,
                             json=json_data)

    data = response.json()
    new_token = data

    return new_token


# do scenariuszy
def tide_record_priority(ext_1, ext_2, headers, phone, camp_id, priority):
    # scanariusz - nadanie większego priorytetu dla wdzwonienia telefonu
    # poprzedni external zamykamy, otwieramy z nowym externalem
    tide_close_record(headers=headers, rec_ext_id=ext_1)
    dane = tide_add_record(headers=headers,
                           phone_reciver=phone,
                           ext_id=ext_2,
                           id_campaign=camp_id,
                           priority=bool(priority),
                           priotiry_num=priority)

    # to do -> wrzucenie zwrotki do bazy
    return dane


def tide_close_open_records(ext_open_records, headers):
    # zamykamy pootwierane rekordy, argument - lista externali
    dane = None
    for i in ext_open_records:
        dane = tide_close_record(headers=headers, rec_ext_id=i)
        # to do -> wrzucenie zwrotki do bazy

    # sprawdzanie istneinia zmiennej
    if 'dane' in locals():
        return dane

    else:
        return None


def tide_add_records(ext_priority, phone_priority, priority_list, camp_id, headers):
    # scenariusz dodawania rekordów do wydzwonienia
    # ext_priority, phone_priority - listy external i telefonów z kampanii, z nadanym priorytetem
    # można wysyłać listę z nadanym numerem priorytetu (0-255)
    # będzie konwersja na true/false (dla 0 false, reszta true)
    dane = None
    for _, j in enumerate(ext_priority):
        dane = tide_add_record(headers=headers,
                               ext_id=ext_priority[j],
                               phone_reciver=phone_priority[j],
                               id_campaign=camp_id,
                               priority=bool(priority_list[j]),
                               priotiry_num=priority_list[j])
    # to do -> wrzucenie zwrotki do bazy
    # sprawdzanie istneinia zmiennej
    if 'dane' in locals():
        return dane

    else:
        return None


# do parsowanie zwrotek z push
def tide_parse_push_request_all(date):
    """
    przekształcenia:
    1. otwieramy plik z datą w nazwie, czytamy linie w których jest "Request" i pozbywamy się początku - nie potrzebne,
        wszystko zapisujemy do listy
    2. usuwamy "ContanctCalls" z każdego elementu, z każdego łańcucha/elementu listy usuwamy "[" i "]",
        będą przeszkadzać przy przekształcaniu
    3. dodajemy "{{" i "}}" tak gdzie są pojedyncze
    4. rozdzielamy wg. "},{" - ponieważ może być kilka rekordów w jednym wierszu, trzeba je rozdzielić
    5. wracamy do pojedynczych "{" i "}", tak aby był dla jednego rekordu
    6. ładujemy listę z elementami typu string do listy słowników wg. parsera json
        (elementy już są przygotowane do parsowania)
    7. lista słowników przekszatałcamy na obiekt DataFrame,
        zmianiemy typ Externala (czyta jako float) i zapisujemy do csv
    """

    with open(f"DebtManager.DialerStatusAPI.LogFile.log{date}.txt", "r") as f:
        lista = [i[i.index(r'['):-3] for i in f if 'Request: ' in i]

    # operacje na listach
    lista_temp1 = [i.replace("{", "{{").replace("}", "}}").replace('"ContactsCalls":', "").split("},{") for i in lista]
    lista_temp2 = [j.replace("[{", "").replace("}}", "}").replace("]", "").split("},{") for i in lista_temp1 for j in i]
    lista_temp3 = [("{" + i + "}").replace("{{", "{").replace("}}", '}') for j in lista_temp2 for i in j]

    # utwórz listę słowników
    lista_slownikow = [json.loads(i) for i in lista_temp3]

    # zmiana formatu, aby zapisać do pliku bez "-"
    date = date.replace("-", "_")

    # tworzymy tabelę, zmieniamy external na int, zapis do csv
    df = pd.DataFrame(lista_slownikow)
    df['ExternalID'] = df['ExternalID'].astype("Int64")
    df.to_csv(f"tide_zwrotka_{date}.csv", index=False, sep=";", encoding="CP1250")
    # to do --> zaczytywanie ze sciezki lub przejscie do folderu


def tide_parse_push_request_succesful(date):
    """
    przekształcenia:
    1. otwieramy plik z datą w nazwie, czytamy linie w których jest "Request" i pozbywamy się początku - nie potrzebne,
        wszystko zapisujemy do listy
    2. tworzymy listę z informacjami o zwróconych statusach, numerujemy je,
        biezemy z poprzedniej listy tylko te, które dodały się dobrze
    3. usuwamy "ContanctCalls" z każdego elementu, z każdego łańcucha/elementu listy usuwamy "[" i "]",
        będą przeszkadzać przy przekształcaniu
    4. dodajemy "{{" i "}}" tak gdzie są pojedyncze
    5. rozdzielamy wg. "},{" - ponieważ może być kilka rekordów w jednym wierszu, trzeba je rozdzielić
    6. wracamy do pojedynczych "{" i "}", tak aby był dla jednego rekordu
    7. ładujemy listę z elementami typu string do listy słowników wg. parsera json
        (elementy już są przygotowane do parsowania)
    8. lista słowników przekszatałcamy na obiekt DataFrame,
        zmianiemy typ Externala (czyta jako float) i zapisujemy do csv
    """

    with open(f"DebtManager.DialerStatusAPI.LogFile.log{date}.txt", "r") as f:
        lista = [i[i.index(r'['):-3] for i in f if 'Request: ' in i]

    with open(f"DebtManager.DialerStatusAPI.LogFile.log{date}.txt", "r") as f:
        lista_odp = [i for i in f if 'Response: ' in i]

    indexes = [i for i, x in enumerate(lista_odp) if 'problem' not in x]
    lista = [x for i, x in enumerate(lista) if i in indexes]

    # operacje na listach
    lista_temp1 = [i.replace("{", "{{").replace("}", "}}").replace('"ContactsCalls":', "").split("},{") for i in lista]
    lista_temp2 = [j.replace("[{", "").replace("}}", "}").replace("]", "").split("},{") for i in lista_temp1 for j in i]
    lista_temp3 = [("{" + i + "}").replace("{{", "{").replace("}}", '}') for j in lista_temp2 for i in j]

    # utwórz listę słowników
    lista_slownikow = [json.loads(i) for i in lista_temp3]

    # zmiana formatu, aby zapisać do pliku bez "-"
    date = date.replace("-", "_")

    # tworzymy tabelę, zmieniamy external na int, zapis do csv
    df = pd.DataFrame(lista_slownikow)
    df['ExternalID'] = df['ExternalID'].astype("Int64")
    df.to_csv(f"tide_zwrotka_{date}.csv", index=False, sep=";", encoding="CP1250")
    # to do --> zaczytywanie ze sciezki lub przejscie do folderu


def main():
    # to musi być, potrzebne do zalogowania
    headers_auth = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # tokeny do uwierzytelniania
    token, refresh_token, date = tide_get_token(headers_auth)

    # odświeżanie tokenów
    # new_token, refresh_token, date = tide_refresh_token(refresh_token, headers=headers_auth)

    # to będzie przekazywanie do wszystkich funkcji, to musi być, bez tego nie przejdzie żadna funkcja
    headers_token = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # lista aktywnych kampanii - poza nagłówkami nic przyjmuje innych argumentów
    data = tide_list_campaings(headers=headers_token)
    print(data)

    # podsumowanie kampanii
    data = tide_start_campaign(headers=headers_token, id_campaign=1998)
    print(data)

    # przykładowe wywołanie dodania rekordu
    data = tide_add_record(headers=headers_token,
                           id_campaign=1897,
                           phone_reciver='603246424',
                           ext_id=1000000013,
                           priority=True,
                           priotiry_num=255)
    print(data)

    data = tide_add_record(headers=headers_token,
                           id_campaign=10,
                           phone_reciver='662098713',
                           ext_id=1000000011,
                           priority=True,
                           priotiry_num=255)
    print(data)


if __name__ == '__main__':
    main()
