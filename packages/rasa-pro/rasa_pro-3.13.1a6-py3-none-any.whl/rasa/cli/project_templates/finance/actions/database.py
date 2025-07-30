import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


class Database:
    def __init__(self, csv_path: Optional[Path] = None) -> None:
        """Initialize the database with CSV file paths."""
        self.project_root_path = Path(__file__).resolve().parent.parent
        self.csv_path = csv_path or self.project_root_path / "csvs"
        self.logger = self.setup_logger()

    def setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s %(levelname)8s %(name)s  - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def get_user_by_name(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username."""
        try:
            df = pd.read_csv(self.csv_path / "users.csv")
            user_data = df[df["name"] == username]
            if user_data.empty:
                return None
            return user_data.iloc[0].to_dict()
        except Exception as e:
            self.logger.error(f"Error getting user by name: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by user_id."""
        try:
            df = pd.read_csv(self.csv_path / "users.csv")
            user_data = df[df["id"] == user_id]
            if user_data.empty:
                return None
            return user_data.iloc[0].to_dict()
        except Exception as e:
            self.logger.error(f"Error getting user by id: {e}")
            return None

    def get_account_by_user_and_number(
        self, user_id: int, account_number: str
    ) -> Optional[Dict[str, Any]]:
        """Get account information by user_id and account number."""
        try:
            df = pd.read_csv(self.csv_path / "accounts.csv")
            account_data = df[
                (df["user_id"] == user_id) & (df["number"] == account_number)
            ]
            if account_data.empty:
                return None
            return account_data.iloc[0].to_dict()
        except Exception as e:
            self.logger.error(f"Error getting account: {e}")
            return None

    def get_accounts_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all accounts for a user."""
        try:
            df = pd.read_csv(self.csv_path / "accounts.csv")
            accounts_data = df[df["user_id"] == user_id]
            return accounts_data.to_dict("records")
        except Exception as e:
            self.logger.error(f"Error getting accounts by user: {e}")
            return []

    def get_payees_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all payees for a user."""
        try:
            df = pd.read_csv(self.csv_path / "payees.csv")
            payees_data = df[df["user_id"] == user_id]
            return payees_data.to_dict("records")
        except Exception as e:
            self.logger.error(f"Error getting payees by user: {e}")
            return []

    def get_payee_by_name_and_user(
        self, payee_name: str, user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get payee information by name and user_id."""
        try:
            df = pd.read_csv(self.csv_path / "payees.csv")
            payee_data = df[(df["name"] == payee_name) & (df["user_id"] == user_id)]
            if payee_data.empty:
                return None
            return payee_data.iloc[0].to_dict()
        except Exception as e:
            self.logger.error(f"Error getting payee by name and user: {e}")
            return None

    def get_cards_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all cards for a user."""
        try:
            df = pd.read_csv(self.csv_path / "cards.csv")
            cards_data = df[df["user_id"] == user_id]
            return cards_data.to_dict("records")
        except Exception as e:
            self.logger.error(f"Error getting cards by user: {e}")
            return []

    def get_card_by_number(self, card_number: str) -> Optional[Dict[str, Any]]:
        """Get card information by card number."""
        try:
            df = pd.read_csv(self.csv_path / "cards.csv")
            card_data = df[df["number"] == card_number]
            if card_data.empty:
                return None
            return card_data.iloc[0].to_dict()
        except Exception as e:
            self.logger.error(f"Error getting card by number: {e}")
            return None

    def update_card_status(self, card_number: str, status: str) -> bool:
        """Update card status."""
        try:
            df = pd.read_csv(self.csv_path / "cards.csv")
            df.loc[df["number"] == card_number, "status"] = status
            df.to_csv(self.csv_path / "cards.csv", index=False)
            return True
        except Exception as e:
            self.logger.error(f"Error updating card status: {e}")
            return False

    def add_payee(
        self,
        user_id: int,
        name: str,
        sort_code: str,
        account_number: str,
        payee_type: str,
        reference: str = "",
    ) -> bool:
        """Add a new payee."""
        try:
            df = pd.read_csv(self.csv_path / "payees.csv")

            # Get the next ID
            next_id = df["id"].max() + 1 if not df.empty else 1

            # Create new payee record
            new_payee = {
                "id": next_id,
                "user_id": user_id,
                "name": name,
                "sort_code": sort_code,
                "account_number": account_number,
                "type": payee_type,
                "reference": reference,
                "added_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            # Add to dataframe and save
            df = pd.concat([df, pd.DataFrame([new_payee])], ignore_index=True)
            df.to_csv(self.csv_path / "payees.csv", index=False)
            return True
        except Exception as e:
            self.logger.error(f"Error adding payee: {e}")
            return False

    def remove_payee(self, payee_name: str, user_id: int) -> bool:
        """Remove a payee."""
        try:
            df = pd.read_csv(self.csv_path / "payees.csv")
            df = df[~((df["name"] == payee_name) & (df["user_id"] == user_id))]
            df.to_csv(self.csv_path / "payees.csv", index=False)
            return True
        except Exception as e:
            self.logger.error(f"Error removing payee: {e}")
            return False

    def check_sufficient_funds(
        self, user_id: int, account_number: str, amount: float
    ) -> bool:
        """Check if account has sufficient funds."""
        try:
            account = self.get_account_by_user_and_number(user_id, account_number)
            if not account:
                return False
            return float(account["balance"]) >= amount
        except Exception as e:
            self.logger.error(f"Error checking sufficient funds: {e}")
            return False

    def get_branches(self) -> List[Dict[str, Any]]:
        """Get all branches."""
        try:
            df = pd.read_csv(self.csv_path / "branches.csv")
            return df.to_dict("records")
        except Exception as e:
            self.logger.error(f"Error getting branches: {e}")
            return []

    def get_advisors_by_branch(self, branch_id: int) -> List[Dict[str, Any]]:
        """Get all advisors for a branch."""
        try:
            df = pd.read_csv(self.csv_path / "advisors.csv")
            advisors_data = df[df["branch_id"] == branch_id]
            return advisors_data.to_dict("records")
        except Exception as e:
            self.logger.error(f"Error getting advisors by branch: {e}")
            return []

    def get_appointments_by_advisor(self, advisor_id: int) -> List[Dict[str, Any]]:
        """Get all appointments for an advisor."""
        try:
            df = pd.read_csv(self.csv_path / "appointments.csv")
            appointments_data = df[df["advisor_id"] == advisor_id]
            return appointments_data.to_dict("records")
        except Exception as e:
            self.logger.error(f"Error getting appointments by advisor: {e}")
            return []

    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context related to this object."""
        self.logger.info("Database connection closed")
