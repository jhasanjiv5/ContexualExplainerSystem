import time
import json
import config
from slackclient import SlackClient
from keywordExtract import keyword_extract
import getSesorValues

slack_client = SlackClient("xoxb-1818593977888-1791692698677-6SFm9litSJsXZ6RaJURDx09x")


def connectbot():
    user_list = slack_client.api_call("users.list")
    for user in user_list.get('members'):
        if user.get('name') == "pam-pibot":
            slack_user_id = user.get('id')
            print(slack_user_id)
            break

    if slack_client.rtm_connect():
        print("Connected!")
        data = getSesorValues.get_current_values_of_active_sensors2()
        while True:
            for message in slack_client.rtm_read():
                if 'text' in message and slack_user_id in message['text']:
                    print("Message received: %s" % json.dumps(message, indent=2))
                    message_keywords = keyword_extract(message['text'].replace('<@' + slack_user_id + '>', ''), config.stopWordsPath)
                    message_keywords_lower = [x.lower() for x in message_keywords]
                    if 'hey' in message_keywords_lower:
                        Hello_msg = 'Hey Hey!'

                        slack_client.api_call(
                            "chat.postMessage",
                            channel=message['channel'],
                            text="{} {}.".format(Hello_msg, message['user']),
                            as_user=True)

                    if isinstance(data, str):
                        slack_client.api_call(
                            "chat.postMessage",
                            channel=message['channel'],
                            text="{}.".format(data),
                            as_user=True)

                    for item in message_keywords_lower:

                        if item in data.keys():
                            slack_client.api_call(
                                "chat.postMessage",
                                channel=message['channel'],
                                text="{} is {}.".format(item.upper(), data[item]),
                                as_user=True)

                    # if 'robot11' in message_keywords_lower:
                    #      location, sensor_name = discover.discover()
                    #      slack_client.api_call(
                    #          "chat.postMessage",
                    #          channel=message['channel'],
                    #          text="robot11 is in {}, and it has context entities {}.".format(location, sensor_name),
                    #          as_user=True)

                        
                    # if 'people' in message_keywords_lower:
                    #     number_of_faces = facesetect.detect_faces(capture.videoStream())[0]
                    #     slack_client.api_call(
                    #         "chat.postMessage",
                    #         channel=message['channel'],
                    #         text="The room is currently occupied by {} people.".format(number_of_faces),
                    #         as_user=True)
                    #
                    # if 'status' in message_keywords_lower:
                    #     number_of_faces, frame = facesetect.detect_faces(capture.videoStream())
                    #     cv2.imwrite('detected-frame/detected-frame.jpg', frame)
                    #     with open('detected-frame/detected-frame.jpg', 'rb') as f:
                    #         slack_client.api_call(
                    #             "files.upload",
                    #             channels=message['channel'],
                    #             filename='sample.jpg',
                    #             title='Image of the room',
                    #             initial_comment=f"Here is the recently captured image of the room, and the current sensor values are {data}. The room is currently occupied by {number_of_faces} people.",
                    #             file=io.BytesIO(f.read())
                    #         )

                time.sleep(1)
