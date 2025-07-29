from datapipelab.app.node.tnode import TNode



class TeamsNotificationSinkNode(TNode):
    def __init__(self, spark, tnode_config, df=None):
        from pyspark.sql import DataFrame
        import json
        super().__init__(spark=spark)
        self.teams_msg_body = tnode_config['options']['teams_msg_body']
        self.teams_msg_title = tnode_config['options'].get('teams_msg_title', 'Notification')
        self.teams_users = tnode_config['options'].get('teams_users', None)
        self.teams_channel_webhook_url = tnode_config['options']['teams_channel_webhook_url']
        self.df = df

    def __prepare_teams_notification_payload(self, teams_msg_body: list, teams_msg_title: str = "Notification",
                                           teams_users: list = None):
        if teams_users is not None:
            teams_msg_body.extend([f'<at>{user}</at>' for user in teams_users])
            print(teams_msg_body)
            final_msg = '   \n'.join(teams_msg_body)
            entities = []
            for user_id in teams_users:
                mention = {
                    "type": "mention",
                    "text": f"<at>{user_id}</at>",
                    "mentioned": {
                        "id": f"{user_id}@cantire.com",
                        "name": f"{user_id}"
                    }
                }
                entities.append(mention)
            payload = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "size": "Medium",
                                    "weight": "Bolder",
                                    "text": f"{teams_msg_title}"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"{final_msg}",
                                    "wrap": "true",
                                    "maxLines": 0
                                }
                            ],
                            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                            "version": "1.0",
                            "msteams": {
                                "entities": entities
                            }
                        }
                    }]
            }
        else:
            final_msg = '   \n'.join(teams_msg_body)
            payload = {
                "text": f"{final_msg}",
                "title": f"{teams_msg_title}"
            }
        return payload
    def __send_teams_notification(self):
        import requests
        payload = self.__prepare_teams_notification_payload(self.teams_msg_body, self.teams_msg_title, self.teams_users)
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.teams_channel_webhook_url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                print("Message sent successfully!")
            else:
                print(f"Failed to send message: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"An error occurred: {e}")


    def _process(self):
        self.__send_teams_notification()
