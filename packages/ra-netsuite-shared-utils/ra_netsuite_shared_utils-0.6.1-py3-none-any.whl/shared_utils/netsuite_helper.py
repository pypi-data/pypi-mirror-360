import json
from decimal import Decimal

import requests
from requests_oauthlib import OAuth1
from shared_utils.file_utils import has_memo_been_posted, record_posted_memo
from shared_utils.helper import get_posting_period_val
from shared_utils.utils import DecimalEncoder


class NetsuiteHelper:
    def __init__(
        self, env, consumer_key, consumer_secret, access_token, token_secret, realm
    ):
        self.env = env
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.token_secret = token_secret
        self.realm = realm

    def get_base_url(self):
        if self.env == "staging":
            return "https://6722500-sb1.suitetalk.api.netsuite.com/services/rest"
        else:
            return "https://6722500.suitetalk.api.netsuite.com/services/rest"

    def get_journal_request_url(self):
        base_url = self.get_base_url()
        return f"{base_url}/record/v1/journalentry/"

    def get_auth_token(self):
        auth = OAuth1(
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.token_secret,
            signature_method="HMAC-SHA256",
            realm=self.realm,
        )
        return auth

    def fetch_posting_period_id(self, period_name):
        url = f"{self.get_base_url()}/query/v1/suiteql"
        auth_token = self.get_auth_token()
        headers = {
            "Prefer": "transient",
            "Content-Type": "application/json",
        }
        payload = {
            "q": f"select id from accountingperiod where periodname='{period_name}'"
        }

        try:
            response = requests.post(
                url, auth=auth_token, headers=headers, json=payload
            )
            response_data = response.json()
            if "items" in response_data and len(response_data["items"]) > 0:
                return response_data["items"][0]["id"]
            else:
                raise ValueError(
                    f"No posting period item found in the response for {period_name}."
                )
        except Exception as e:
            raise ConnectionError(
                "An error occurred while fetching posting period ID: ", e
            )

    def get_posting_period(self, journal_date):
        posting_period_val = get_posting_period_val(journal_date)
        posting_period_id = self.fetch_posting_period_id(posting_period_val)

        return (posting_period_val, posting_period_id)

    def fetch_mappings(self, name_key, id_key, table_name):
        url = f"{self.get_base_url()}/query/v1/suiteql"
        auth_token = self.get_auth_token()
        headers = {
            "Prefer": "transient",
            "Content-Type": "application/json",
        }
        payload = {
            "q": f"select {name_key}, {id_key} from {table_name} where isinactive = 'F'"
        }

        try:
            response = requests.post(
                url, auth=auth_token, headers=headers, json=payload
            )
            response_data = response.json()
            if "items" in response_data and len(response_data["items"]) > 0:
                return response_data["items"]
            else:
                raise ValueError(f"No items found in response for {table_name}.")
        except Exception as e:
            raise ConnectionError("An error occurred while fetching mappings: ", e)

    def get_class_to_id_mapping(self):
        class_id_mapping = {}
        mappings = self.fetch_mappings("name", "id", "classification")
        if mappings:
            for item in mappings:
                class_id_mapping[item["name"]] = int(item["id"])

        return class_id_mapping

    def get_department_to_id_mapping(self):
        department_id_mapping = {}
        mappings = self.fetch_mappings("name", "id", "department")
        if mappings:
            for item in mappings:
                department_id_mapping[item["name"]] = int(item["id"])

        return department_id_mapping

    def get_location_to_id_mapping(self):
        location_id_mapping = {}
        mappings = self.fetch_mappings("name", "id", "location")
        if mappings:
            for item in mappings:
                location_id_mapping[item["name"]] = int(item["id"])

        return location_id_mapping

    def get_account_to_id_mapping(self):
        account_id_mapping = {}
        mappings = self.fetch_mappings("accountsearchdisplaynamecopy", "id", "account")
        if mappings:
            for item in mappings:
                account_id_mapping[item["accountsearchdisplaynamecopy"]] = item["id"]

        return account_id_mapping

    def get_subsidiary_to_id_mapping(self):
        subsidiary_id_mapping = {}
        mappings = self.fetch_mappings("name", "id", "subsidiary")
        if mappings:
            for item in mappings:
                subsidiary_id_mapping[item["name"]] = item["id"]
        return subsidiary_id_mapping

    def get_customer_to_id_mapping(self):
        customer_id_mapping = {}
        mappings = self.fetch_mappings("altname", "id", "customer")
        if mappings:
            for item in mappings:
                customer_id_mapping[item["altname"]] = item["id"]
        return customer_id_mapping

    def post_journal_entry(
        self, memo, journal_items, journal_date, posting_period, subsidiary_id=1
    ):
        if has_memo_been_posted(memo):
            print(f"Skipping already posted journal entry: {memo}")
            return

        url = self.get_journal_request_url()

        items = [item.to_dict() for item in journal_items]

        payload = json.dumps(
            {
                "subsidiary": subsidiary_id,
                "currency": 1,
                "exchangerate": 1,
                "postingperiod": posting_period,
                "approvalstatus": 1,
                "memo": memo,
                "trandate": journal_date,
                "line": {"items": items},
            },
            cls=DecimalEncoder,
        )

        auth = self.get_auth_token()

        headers = {
            "Content-Type": "application/json",
            "Prefer": "respond-async"
        }
        
        try:
            response = requests.post(url, auth=auth, headers=headers, data=payload)
            response.raise_for_status()
            print(f"Successfully posted journal entry: {memo}, Status Code: {response.status_code}")
            record_posted_memo(memo)
            return True
        except Exception as e:
            print(f"Failed to post journal entry: {memo}, Error: {str(e)}")
            return False


    def get_hsn_code(self, memo):
        if "PTL" in memo and ("CGST" in memo or "SGST" in memo or "IGST" in memo):
            return 2996 if self.env == "staging" else 2973
        return None
   