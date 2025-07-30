from email.mime import application
import os
import pymsteams
import requests
import json
from dotenv import load_dotenv

load_dotenv()


testing_web_hook_url = os.getenv("testing_web_hook_url")


def send_teams_notification(web_hook_url: str, title: str, message: str,application_name: str="LB_UNNAMED_APPLICATION",employee_email: str="tech@learnbasics.fun") -> None:

    message_to_send = ""

    for each_line in message.splitlines():
        message_to_send += f"{each_line.strip()}  \n"

    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.0",
                    "body": [
                        {
                            "type": "Container",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": title,
                                    "weight": "bolder",
                                    "size": "large"
                                }
                            ]
                        },
                        {
                            "type": "Container",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": message_to_send,
                                    "wrap": True
                                },
                                {
                                    "type": "FactSet",
                                    "facts": [
                                        {
                                            "title": "Application Name:",
                                            "value": application_name
                                        },
                                        {
                                            "title": "Process Started By:",
                                            "value": employee_email
                                        }
                                    ]
                                },
                                {
                                    "type": "TextBlock",
                                    "text": "Is the Above Info Correct?",
                                    "wrap": True
                                }
                            ]
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.ShowCard",
                            "title": "Correct",
                            "card": {
                                "type": "AdaptiveCard",
                                "body": [
                                    {
                                        "type": "Input.Date",
                                        "id": "dueDate"
                                    }
                                ],
                                "actions": [
                                    {
                                        "type": "Action.Submit",
                                        "title": "OK"
                                    }
                                ]
                            }
                        },
                        {
                            "type": "Action.ShowCard",
                            "title": "Wrong",
                            "card": {
                                "type": "AdaptiveCard",
                                "body": [
                                    {
                                        "type": "Input.Text",
                                        "id": "Wrong",
                                        "isMultiline": True,
                                        "placeholder": "Enter your comment"
                                    }
                                ],
                                "actions": [
                                    {
                                        "type": "Action.Submit",
                                        "title": "OK"
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }

    reponse = requests.post(url=web_hook_url, json=payload)

    print(reponse.content)


if __name__ == "__main__":

    message = """
    1. Test ID - 4000 - PVA 6A - CH9 - HQ2 - Success
    2. Test ID - 4001 - PVA 6A - CH9 - HQ3 - Success
    3. Test ID - 4002 - PVA 6A - CH9 - HQ4 - Success
    4. Test ID - 4003 - PVA 6A - CH9 - HQ5 - Success
"""

    title = "Release Summary"

    application_name = "Test Release"

    employee_email = "johnson@basics.fun"

    send_teams_notification(web_hook_url=testing_web_hook_url, message=message, title=title,application_name=application_name,employee_email=employee_email)
