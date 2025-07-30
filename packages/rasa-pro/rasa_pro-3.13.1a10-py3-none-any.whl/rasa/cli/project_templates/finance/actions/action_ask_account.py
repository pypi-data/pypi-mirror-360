from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from actions.database import Database


class ActionAskAccount(Action):
    def name(self) -> Text:
        return "action_ask_account"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        username = tracker.get_slot("username")

        db = Database()

        # Get user information
        user = db.get_user_by_name(username)
        if not user:
            dispatcher.utter_message(text="User not found.")
            return []

        # Get all accounts for the user
        accounts = db.get_accounts_by_user(user["id"])

        if not accounts:
            dispatcher.utter_message(text="No accounts found for this user.")
            return []

        buttons = [
            {
                "content_type": "text",
                "title": f"{account['number']} ({account['type'].title()})",
                "payload": str(account["number"]),
            }
            for account in accounts
        ]
        message = "Which account would you like the balance for?"
        dispatcher.utter_message(text=message, buttons=buttons)

        selected_account = tracker.get_slot("account")

        return [SlotSet("account", selected_account)]
