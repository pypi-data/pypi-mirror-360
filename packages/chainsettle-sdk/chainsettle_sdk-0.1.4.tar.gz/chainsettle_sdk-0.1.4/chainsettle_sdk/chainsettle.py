from gc import is_finalized
from token import OP
import requests
from typing import Dict, Optional, List
from datetime import datetime
from chainsettle_sdk.config import get_settings
from chainsettle_sdk.utils.error_handler import handle_api_error
import time
import json
import secrets
import os

global settings
settings = get_settings()

class ChainSettleService:
    def __init__(self, id_hash: Optional[str] = None, contract: Optional[object] = None, 
                 account_address: Optional[str] = None):
        """ Initializes the ChainSettleService with the given parameters.
        Args:
            id_hash (Optional[str]): The ID hash of the settlement.
            contract (Optional[object]): The contract object for on-chain interactions.
            account_address (Optional[str]): The account address for on-chain interactions.
        """
        self.base_url = settings.CHAINSETTLE_API_URL
        self.supported_networks = settings.CHAINSETTLE_SUPPORTED_NETWORKS
        self.supported_apis = settings.CHAINSETTLE_SUPPORTED_APIS
        self.supported_asset_categories = settings.CHAINSETTLE_SUPPORTED_ASSET_CATEGORIES
        self.supported_jurisdictions = settings.CHAINSETTLE_SUPPORTED_JURISDICTIONS
        self.zero_address = settings.ZERO_ADDRESS
        self.id_hash = id_hash
        self.contract = contract
        self.account_address = account_address if account_address is not None else os.getenv("ACCOUNT_ADDRESS", None)

        self.get_settlement_types()
        print(f"ChainSettle Node {'live' if self.is_ok() else 'not responding'} at {self.base_url}")

    @handle_api_error
    def is_ok(self):
        r = requests.get(f"{self.base_url}/api/health")
        if r.json().get("status") == "ok":
            return True
        
    @handle_api_error
    def get_settlement_types(self) -> Dict:
        """
        Fetch supported settlement types and networks from ChainSettle.
        """
        response = requests.get(f"{self.base_url}/api/settlement_types")
        response.raise_for_status()
        data = response.json()

        self.supported_apis = data.get("supported_types", [])
        self.supported_networks = data.get("supported_networks", [])
        self.supported_asset_categories = data.get("supported_asset_categories", [])
        self.supported_jurisdictions = data.get("supported_jurisdictions", [])

        return data
    
    @handle_api_error
    def get_config_map(self) -> Dict:
        """
        Fetches the configuration map from the ChainSettle API.
        """
        response = requests.get(f"{self.base_url}/api/config")
        response.raise_for_status()
        return response.json()

    @handle_api_error
    def initiate_attestation(
        self,
        settlement_type: str,
        network: str,
        user_email: str,
        settlement_id: Optional[str] = None,
        amount: Optional[float] = 0.0,
        witness: Optional[str] = None,
        counterparty: Optional[str] = None,
        details: Optional[str] = None,
        recipient_email: Optional[str] = None,
    ) -> Dict:
        """
        Initiates the attestation process for a settlement.
        """
        if settlement_id is None:
            settlement_id = secrets.token_hex(4)
        if witness is None:
            witness = self.zero_address
        if counterparty is None:
            counterparty = self.zero_address
        if details is None:
            details = ""
        if recipient_email is None:
            recipient_email = ""

        payload = {
            "settlement_id": settlement_id,
            "user_email": user_email,
            "settlement_type": settlement_type,
            "network": network,
            "amount": amount,
            "witness": witness,
            "counterparty": counterparty,
            "details": details,
            "recipient_email": recipient_email,
        }

        response = requests.post(
            f"{self.base_url}/api/init_attest",
            json=payload
        )
        response.raise_for_status()

        self.id_hash = response.json().get('settlement_info').get("id_hash")

        if self.id_hash:
            print(f"Settlement initiated with ID Hash: {self.id_hash}")
            
        return response.json()
    
    @handle_api_error
    def attest_settlement(self, id_hash: Optional[str] = None):
        """
        Attests a settlement with the given ID.
        """
        if id_hash is None:
            if self.id_hash is None:
                raise ValueError("No ID hash provided and no previous ID hash available.")
            id_hash = self.id_hash
        payload = {
            "id_hash": id_hash,
        }
        try:
            res = requests.post(f"{self.base_url}/api/attest", json=payload)
            res.raise_for_status()
            data = res.json()

            if 'internal_status' not in data or data['internal_status'] != 'attested':
                print("Unexpected response from backend. Settlement may not be valid or pending further action.")

            return data
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                try:
                    err = e.response.json().get("error") or e.response.text
                    print(f"Attestation request failed: {err}")
                except Exception:
                    print(f"Attestation request failed with status {e.response.status_code}")
            else:
                print(f"Attestation request failed: {e}")

    @handle_api_error
    def get_settlement_status(self, id_hash: Optional[str] = None) -> Optional[int]:
        """
        Obtains the status of a settlement.
        If the HTTP response is not 200, returns None instead of raising.
        """
        if id_hash is None:
            if self.id_hash is None:
                raise ValueError("No ID hash provided and no previous ID hash available.")
            id_hash = self.id_hash

        response = requests.get(
            f"{self.base_url}/api/get_settlement_status/{id_hash}"
        )
        if response.status_code != 200:
            return None

        payload = response.json()
        return payload

    @handle_api_error
    def get_settlement_info(self, id_hash: Optional[str] = None) -> Dict:
        """
        Retrieves detailed information about a settlement.
        If the HTTP response is not 200, returns an empty dictionary.
        """

        if id_hash is None:
            if self.id_hash is None:
                raise ValueError("No ID hash provided and no previous ID hash available.")
            id_hash = self.id_hash

        response = requests.get(f"{self.base_url}/api/get_settlement/{id_hash}")
        if response.status_code != 200:
            return {}

        payload = response.json().get("data", {})
        return payload
        
    @handle_api_error
    def get_validator_list(self):
        """
        Retrieves the list of available validators.
        """
        response = requests.get(f"{self.base_url}/api/validator_list")
        response.raise_for_status()
        return response.json()
        
    @handle_api_error
    def simulate_signing(self, id_hash: str, envelope_id: str, recipient_id: str) -> Dict:
        """
        Simulates the signing of an envelope by a specific recipient.
        """
        payload = {
            "envelope_id": envelope_id,
            "recipient_id": recipient_id
        }
        
        response = requests.post(
            f"{self.base_url}/api/simulate_signing",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def generate_salt(self, length: Optional[str] = 16) -> str:
        """
        Generates a random salt for settlement.
        """
        return secrets.token_hex(length)
    
    @handle_api_error
    def store_salt(self, salt: str,
                   email: str, 
                   recipient_email: Optional[str] = None,
                   id_hash: Optional[str] = None,
                   
                   ) -> Dict:
        """
        Stores a salt for a specific settlement.
        """

        if id_hash is None:
            if self.id_hash is None:
                raise ValueError("No ID hash provided and no previous ID hash available.")
            id_hash = self.id_hash

        payload = {
            "id_hash": id_hash,
            "salt": salt,
            "email": email,
            "recipient_email": recipient_email
        }
        
        response = requests.post(
            f"{self.base_url}/api/store_salt",
            json=payload
        )
        response.raise_for_status()
        return response.json()
        
    @handle_api_error
    def poll_settlement_activity(
        self,
        id_hash: Optional[str] = None,
        statuses: Optional[List[int]] = None,
        finalized_flag: bool = True,
        interval: float = 5.0,
        max_attempts: int = 120
    ) -> Dict:
        """
        Polls the API until the settlement reaches one of the given statuses
        and matches the finalized_flag condition. Then returns the full
        settlement-info dictionary.
        """
        if id_hash is None:
            if self.id_hash is None:
                raise ValueError("No ID hash provided and no previous ID hash available.")
            id_hash = self.id_hash

        if statuses is None:
            statuses = [3, 4]  # confirmed or failed

        for attempt in range(1, max_attempts + 1):
            try:
                status_response = self.get_settlement_status(id_hash)
                status_code = status_response.get("status_enum")
                is_finalized = status_response.get("is_finalized", False)

                if status_code is None:
                    print(f"[Attempt {attempt}] Status is None. Retrying in {interval}s...")
                    time.sleep(interval)
                    continue
            except requests.exceptions.RequestException as e:
                if hasattr(e, "response") and e.response is not None:
                    code = e.response.status_code
                    if code == 404:
                        print(f"[Attempt {attempt}] 404 not found. Retrying in {interval}s...")
                        time.sleep(interval)
                        continue
                    else:
                        print(f"[Attempt {attempt}] HTTP error {code}. Retrying in {interval}s...")
                        time.sleep(interval)
                        continue
                else:
                    print(f"[Attempt {attempt}] Unknown error: {e}. Retrying in {interval}s...")
                    time.sleep(interval)
                    continue

            # Only return if both the status matches and finalization flag matches
            if status_code in statuses and is_finalized == finalized_flag:
                try:
                    info = self.get_settlement_info(id_hash)
                    return info.get("data", info)
                except requests.exceptions.RequestException as e:
                    print(f"[Attempt {attempt}] error fetching info: {e}. Retrying in {interval}s...")
                    time.sleep(interval)
                    continue

            print(
                f"[Attempt {attempt}] status={status_code}, finalized={is_finalized} "
                f"→ waiting {interval}s to retry..."
            )
            time.sleep(interval)

        raise TimeoutError(
            f"Settlement '{id_hash}' did not meet conditions (statuses={statuses}, "
            f"finalized={finalized_flag}) after {max_attempts} attempts "
            f"({max_attempts * interval:.0f}s)."
        )

    def poll_settlement_status_onchain(self, 
        contract: Optional[object] = None, 
        id_hash_bytes: Optional[bytes] = None,
        account_address: Optional[str] = None,
        finalized_flag: bool = True,
        max_attempts: Optional[int] = 60, 
        delay: Optional[int] = 5,
        statuses: Optional[List[int]] = [3, 4]) -> int:
        """
        Polls the on-chain settlement status every 5 seconds for up to 5 minutes (default).
        Exits early if the status reaches 3 (Confirmed) or 4 (Failed).
        """
        status = None
        
        if id_hash_bytes is None:
            if self.id_hash is None:
                raise ValueError("No ID hash provided and no previous ID hash available.")
            id_hash_bytes = bytes.fromhex(self.id_hash)
        
        if contract is None:
            if self.contract is None:
                raise ValueError("No ramp contract provided and no previous contract available.")
            contract = self.contract
        
        if account_address is None:
            if self.account_address is None:
                raise ValueError("No account address provided and no previous address available.")
            account_address = self.account_address

        print(f"Polling settlement status for idHash: {id_hash_bytes.hex()} ...")
        for attempt in range(1, max_attempts + 1):
            # Fetch on-chain status
            try:
                status = contract.functions.getSettlementStatus(id_hash_bytes).call({'from': account_address})
                is_finalized = contract.functions.isFinalized(id_hash_bytes).call({'from': account_address})
            except Exception as e:
                print(f"[Attempt {attempt}] Error fetching on-chain status: {e}")
                time.sleep(delay)
                continue

            print(f"[Attempt {attempt}] status: {status}, finalized: {is_finalized}")
            
            # If status is Confirmed (3) or Failed (4), exit early
            if status in statuses and is_finalized == finalized_flag:
                print(f"Settlement finalized with status: {status}")
                return status
            
            # Wait before next attempt
            time.sleep(delay)
        else:
            print("Polling timed out after 5 minutes.")
            return status
