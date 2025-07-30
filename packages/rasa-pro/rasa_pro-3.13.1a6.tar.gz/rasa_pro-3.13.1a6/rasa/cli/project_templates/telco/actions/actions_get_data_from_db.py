import pandas as pd
from rasa_sdk import Action
from rasa_sdk.events import SlotSet


class ActionGetCustomerInfo(Action):
    def name(self):
        return "action_get_customer_info"

    def run(self, dispatcher, tracker, domain):
        # Load CSV file
        file_path = "csvs/customers.csv"  # get information from your DBs
        df = pd.read_csv(file_path)
        customer_id = tracker.get_slot("customer_id")

        # Filter data for the given customer ID
        customer_info = df[df["customer_id"] == int(customer_id)]

        if customer_info.empty:
            dispatcher.utter_message("No customer found with this ID.")
            return []

        # Extract customer details
        first_name = customer_info.iloc[0]["first_name"]

        # Set the retrieved name in a slot
        return [SlotSet("customer_first_name", first_name)]
