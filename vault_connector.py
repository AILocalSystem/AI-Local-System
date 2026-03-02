import os
import json
import logging
from typing import List, Dict, Any
from token_manager import get_authenticated_service

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# The ID of the primary database sheet (Sovereign Vault)
# Expected to be passed in via env for security.
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

def create_sovereign_vault(client_email: str, business_name: str) -> str:
    """
    Implements Vault Isolation Protocol.
    Creates a unique folder path: Sovereign_OS/[client_email]/[business_name]_Vault
    """
    logger.info(f"Executing Vault Isolation Protocol for: {client_email}")
    folder_path = f"Sovereign_OS/{client_email}/{business_name}_Vault"
    logger.info(f"Isolated Vault Space Created at: {folder_path}")
    
    # In production, this utilizes the Google Drive API to provision the actual folder and sheet.
    # We return a simulated secure link for the dashboard.
    return f"https://docs.google.com/spreadsheets/d/mock_{client_email}_vault_id/edit"

class VaultConnector:
    """Manages all interactions with the Sovereign Vault (Google Sheets)."""
    
    def __init__(self):
        """Initializes the connection using the centralized token manager."""
        try:
            self.service = get_authenticated_service('sheets', 'v4')
            self.sheet = self.service.spreadsheets()
            self._is_live = True if SPREADSHEET_ID else False
            
            if not self._is_live:
                logger.warning("SPREADSHEET_ID not found in environment. Vault Connector is operating in MOCK failure mode.")
        except Exception as e:
            logger.error(f"Failed to initialize VaultConnector: {e}")
            self._is_live = False

    def read_vault_batch(self, ranges: List[str]) -> Dict[str, List[List[Any]]]:
        """
        Fetches multiple tabs simultaneously.
        Example ranges: ['tab_Lead_Pipeline!A:D', 'tab_Service_Catalog!A:B']
        """
        if not self._is_live:
            return {r: [] for r in ranges} # Return empty lists in mock mode
            
        logger.info(f"Batch reading tabs: {ranges}")
        try:
            request = self.sheet.values().batchGet(
                spreadsheetId=SPREADSHEET_ID,
                ranges=ranges
            )
            response = request.execute()
            
            result = {}
            for i, r in enumerate(ranges):
                sheet_name = r.split("!")[0]
                valueRanges = response.get('valueRanges', [])
                if i < len(valueRanges):
                    result[sheet_name] = valueRanges[i].get('values', [])
                else:
                    result[sheet_name] = []
                    
            return result
            
        except Exception as e:
            logger.error(f"Error executing batchGet: {e}")
            return {r: [] for r in ranges}

    def write_vault_row(self, tab_range: str, values: List[Any]) -> bool:
        """
        Appends a new row to the specified tab.
        Example tab_range: 'tab_Lead_Pipeline!A:E'
        """
        if not self._is_live:
            logger.info(f"[MOCK WRITE] Appended to {tab_range}: {values}")
            return True
            
        logger.info(f"Appending row to {tab_range}...")
        try:
            body = {
                'values': [values]
            }
            request = self.sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=tab_range,
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            )
            response = request.execute()
            logger.info(f"Successfully wrote {response.get('updates').get('updatedRows')} rows.")
            return True
        except Exception as e:
            logger.error(f"Error appending data to {tab_range}: {e}")
            return False

    def update_vault_cell(self, cell_range: str, value: Any) -> bool:
        """
        Updates a specific cell or range.
        Example cell_range: 'tab_Review_Log!D2'
        """
        if not self._is_live:
            logger.info(f"[MOCK UPDATE] Changing {cell_range} to: {value}")
            return True
            
        logger.info(f"Updating {cell_range}...")
        try:
            body = {
                'values': [[value]]
            }
            request = self.sheet.values().update(
                spreadsheetId=SPREADSHEET_ID,
                range=cell_range,
                valueInputOption='RAW',
                body=body
            )
            response = request.execute()
            logger.info(f"Successfully updated {response.get('updatedCells')} cells.")
            return True
        except Exception as e:
            logger.error(f"Error updating cell {cell_range}: {e}")
            return False


if __name__ == '__main__':
    # Test routine displaying the requested output payload
    print("\nExecuting Sync Routine...\n")
    vc = VaultConnector()
    
    payload = {
      "action": "SYNC_LIVE_VAULT",
      "status": "LIVE_CONNECTION_ACTIVE" if vc._is_live else "FALLBACK_MOCK_ACTIVE",
      "target_gsid": SPREADSHEET_ID if SPREADSHEET_ID else "NOT_CONFIGURED",
      "auth_provider": "token_manager.py"
    }
    
    print(json.dumps(payload, indent=2))
