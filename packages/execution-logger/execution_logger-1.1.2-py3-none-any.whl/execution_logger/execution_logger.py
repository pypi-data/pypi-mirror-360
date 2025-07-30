import os
import logging
import traceback
from datetime import datetime
import sys
import requests
import tempfile
import msal
import inspect


class ExecutionLogger:
    """
    A simplified logging solution with 3 storage options:
    
    1. Local only: Save logs in the same directory as the calling script
    2. SharePoint: Upload logs using sharepoint-uploader module
    3. Optional Dataverse: Send errors to Dataverse table for tracking
    
    Examples:
        Local logging only:
        >>> logger = ExecutionLogger(script_name="my_app")
        >>> logger.info("Application started")
        >>> logger.finalize()  # Saves to same directory as script
        
        SharePoint integration:
        >>> logger = ExecutionLogger(
        ...     script_name="my_app",
        ...     client_id="87654321-4321-4321-4321-210987654321",
        ...     client_secret="your-secret",
        ...     tenant_id="12345678-1234-1234-1234-123456789012",
        ...     sharepoint_url="https://company.sharepoint.com/sites/sitename",
        ...     drive_name="Documents",
        ...     folder_path="Logs/MyApp"
        ... )
        
        SharePoint + Dataverse:
        >>> logger = ExecutionLogger(
        ...     script_name="critical_app",
        ...     client_id="client-id",
        ...     client_secret="client-secret",
        ...     tenant_id="tenant-id",
        ...     sharepoint_url="https://company.sharepoint.com/sites/sitename",
        ...     drive_name="Documents",
        ...     folder_path="Logs",
        ...     dv_client_id="dataverse-client-id",
        ...     dv_client_secret="dataverse-secret"
        ... )
    """
    
    def __init__(self, script_name: str, 
                 # SharePoint parameters (optional - all required if using SharePoint)
                 client_id: str = None,
                 client_secret: str = None,
                 tenant_id: str = None,
                 sharepoint_url: str = None,
                 drive_name: str = None, 
                 folder_path: str = None,
                 
                 # Dataverse parameters (optional)
                 dv_client_id: str = None, 
                 dv_client_secret: str = None, 
                 dv_tenant_id: str = None, 
                 dv_scope: str = None, 
                 dv_api_url: str = None,
                 
                 # Local storage options
                 local_log_directory: str = None,
                 
                 # General options
                 debug: bool = False):
        """
        Initialize the ExecutionLogger.
        
        Args:
            script_name (str): Name of the script/application for identification and log file naming.
            
            SharePoint Parameters (all required for SharePoint upload):
            client_id (str, optional): Azure app registration client ID for SharePoint access.
            client_secret (str, optional): Azure app registration client secret.
            tenant_id (str, optional): Azure AD tenant ID for SharePoint authentication.
            sharepoint_url (str, optional): SharePoint site URL (e.g., "https://company.sharepoint.com/sites/sitename").
            drive_name (str, optional): SharePoint document library name (e.g., "Documents", "Logs").
            folder_path (str, optional): Target folder path within the document library.
            
            Dataverse Parameters (optional for error tracking):
            dv_client_id (str, optional): Dataverse client ID for error tracking.
            dv_client_secret (str, optional): Dataverse client secret for error tracking.
            dv_tenant_id (str, optional): Dataverse tenant ID (defaults to SharePoint tenant_id).
            dv_scope (str, optional): Dataverse API scope (has default).
            dv_api_url (str, optional): Dataverse API endpoint (has default).
            
            Local Storage Parameters:
            local_log_directory (str, optional): Directory for local log storage (defaults to script directory).
            
            General Parameters:
            debug (bool, optional): Enable debug logging. Defaults to False.
        """
        
        self.script_name = script_name
        self.start_time = datetime.now()
        self.error_count = 0
        self.debug_mode = debug

        # Set up log file paths FIRST (needed for both SharePoint and local)
        log_filename = f"{script_name}_{self.start_time.strftime('%Y%m%d_%H%M%S')}.log"
        self.temp_log_file_path = os.path.join(tempfile.gettempdir(), log_filename)

        # Determine SharePoint configuration
        sharepoint_params = [client_id, client_secret, tenant_id, sharepoint_url, drive_name, folder_path]
        sharepoint_provided = [p for p in sharepoint_params if p is not None]
        
        if len(sharepoint_provided) == 6:
            # Use SharePoint upload
            self.use_sharepoint = True
            self.client_id = client_id
            self.client_secret = client_secret
            self.tenant_id = tenant_id
            self.sharepoint_url = sharepoint_url
            self.drive_name = drive_name
            self.folder_path = folder_path
            self.local_log_directory = None
            self.final_log_file_path = None
            storage_info = f"SharePoint ({sharepoint_url})"
        elif len(sharepoint_provided) > 0:
            raise ValueError("If using SharePoint, all parameters must be provided: "
                           "client_id, client_secret, tenant_id, sharepoint_url, drive_name, folder_path")
        else:
            # Use local storage
            self.use_sharepoint = False
            if local_log_directory:
                self.local_log_directory = local_log_directory
            else:
                # Use the directory of the calling script
                caller_frame = inspect.stack()[1]
                caller_file = caller_frame.filename
                self.local_log_directory = os.path.dirname(os.path.abspath(caller_file))
            
            # Ensure local directory exists
            os.makedirs(self.local_log_directory, exist_ok=True)
            # Set final log file path for local storage
            self.final_log_file_path = os.path.join(self.local_log_directory, log_filename)
            storage_info = f"Local ({self.local_log_directory})"

        # Determine Dataverse configuration
        dataverse_params = [dv_client_id, dv_client_secret]
        dataverse_provided = [p for p in dataverse_params if p is not None]
        
        if len(dataverse_provided) > 0 and len(dataverse_provided) < 2:
            raise ValueError("If using Dataverse, both dv_client_id and dv_client_secret must be provided")
            
        self.use_dataverse = len(dataverse_provided) == 2
        
        if self.use_dataverse:
            self.dv_client_id = dv_client_id
            self.dv_client_secret = dv_client_secret
            self.dv_tenant_id = dv_tenant_id or tenant_id
            self.dv_scope = dv_scope or f"https://orgcf43c216.crm4.dynamics.com/.default"
            self.dv_api_url = dv_api_url or "https://orgcf43c216.crm4.dynamics.com/api/data/v9.0/cr672_app_errors"

        # Configure logging
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            filename=self.temp_log_file_path,
            level=level,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.logger = logging.getLogger(script_name)
        self._add_console_handler(level)
        
        # Initialize Dataverse token
        self.dv_token = None
        
        # Log initialization info
        dataverse_info = "enabled" if self.use_dataverse else "disabled"
        self.info(f"Logger initialized - Storage: {storage_info}, Dataverse: {dataverse_info}")

        # Get Dataverse authentication token if needed
        if self.use_dataverse:
            try:
                self.dv_token = self._get_dv_access_token()
                self.info("Dataverse authentication successful")
            except Exception as e:
                self.warning(f"Dataverse authentication failed: {str(e)}")
                self.use_dataverse = False  # Disable Dataverse on auth failure

    def _add_console_handler(self, level):
        """Add console output handler to the logger for real-time monitoring."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _log(self, level, message, details=None, exc_info=False):
        """Internal unified logging method that handles all log levels."""
        log_method = {
            logging.DEBUG: self.logger.debug,
            logging.INFO: self.logger.info,
            logging.WARNING: self.logger.warning,
            logging.ERROR: self.logger.error,
            logging.CRITICAL: self.logger.critical,
        }.get(level)

        if log_method:
            log_method(message, exc_info=exc_info)
            if details:
                self._log_details(details)

    def _log_details(self, details):
        """Helper method to format and print additional details with proper indentation."""
        for line in str(details).splitlines():
            print(f"  {line}")

    def info(self, message, details=None):
        """Log an informational message."""
        print(f"[INFO] {message}")
        self._log(logging.INFO, message, details)

    def warning(self, message, details=None):
        """Log a warning message."""
        print(f"[WARNING] {message}")
        self._log(logging.WARNING, message, details)

    def error(self, message, details=None, exc_info=True):
        """
        Log an error message with optional Dataverse integration.
        
        Args:
            message (str): The main error message describing what went wrong.
            details (str, optional): Additional error context or diagnostic information.
            exc_info (bool, optional): Whether to include exception traceback information.
                                     Defaults to True for full diagnostic capture.
        """
        self.error_count += 1
        print(f"[ERROR] {message}")
        self._log(logging.ERROR, message, details, exc_info=exc_info)

        # Send to Dataverse if configured and available
        if self.use_dataverse and self.dv_token:
            try:
                self._log_to_dataverse(
                    script_name=self.script_name,
                    error_message=message,
                    timestamp=datetime.now(),
                    context=message[:200],
                    details=f"{details or ''}\n{traceback.format_exc() if exc_info else ''}"
                )
            except Exception as e:
                self.warning(f"Failed to send error to Dataverse: {str(e)}")

    def debug(self, message, details=None):
        """Log a debug message for detailed diagnostic information."""
        print(f"[DEBUG] {message}")
        self._log(logging.DEBUG, message, details)

    def critical(self, message, details=None):
        """Log a critical error message for severe system failures."""
        print(f"[CRITICAL] {message}")
        self._log(logging.CRITICAL, message, details)

    def _get_dv_access_token(self):
        """Acquire Dataverse API access token using client credentials flow."""
        authority = f'https://login.microsoftonline.com/{self.dv_tenant_id}'
        app = msal.ConfidentialClientApplication(
            self.dv_client_id,
            authority=authority,
            client_credential=self.dv_client_secret
        )

        result = app.acquire_token_for_client(scopes=[self.dv_scope])
        if "access_token" in result:
            return result['access_token']
        else:
            raise Exception(f"Dataverse Token acquisition failed: {result.get('error_description')}")

    def upload_to_sharepoint(self):
        """Upload log file using sharepoint-uploader module."""
        if not self.use_sharepoint:
            self.warning("SharePoint not configured. Skipping upload.")
            return

        try:
            from sharepoint_uploader import SharePointUploader
            
            self.info(f"Uploading {self.temp_log_file_path} to SharePoint...{self.folder_path}")
            
            uploader = SharePointUploader(
                self.client_id,
                self.client_secret,
                self.tenant_id,
                self.sharepoint_url,
                self.drive_name
            )
            
            uploader.upload_file(self.temp_log_file_path, self.folder_path)
            self.info(f"SharePoint upload successful: {os.path.basename(self.temp_log_file_path)}")
            
        except ImportError:
            raise Exception("sharepoint-uploader module not installed. Install with: pip install sharepoint-uploader")
        except Exception as e:
            self.warning(f"SharePoint upload error: {str(e)}")
            raise

    def save_to_local(self):
        """Save the log file to the local directory."""
        if not self.final_log_file_path:
            self.warning("Local storage not configured. Cannot save locally.")
            return
        
        try:
            import shutil
            shutil.copy2(self.temp_log_file_path, self.final_log_file_path)
            self.info(f"Log file saved locally: {self.final_log_file_path}")
        except Exception as e:
            self.warning(f"Failed to save log file locally: {str(e)}")

    def _log_to_dataverse(self, script_name, error_message, timestamp, context, details):
        """Send error information to Dataverse for centralized tracking."""
        if not self.use_dataverse or not self.dv_token:
            return
            
        headers = {
            'Authorization': f'Bearer {self.dv_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        log_data = {
            "cr672_app": script_name,
            "cr672_message": error_message[:1000],
            "cr672_source": str(context)[:200],
            "cr672_details": f"{timestamp} - {details}"[:4000],
            "cr672_id": "0"
        }

        response = requests.post(self.dv_api_url, headers=headers, json=log_data)
        if response.status_code in [200, 201, 204]:
            self.info("Successfully posted error log to Dataverse.")
        else:
            self.warning(f"Failed to post error to Dataverse: {response.status_code} - {response.text}")

    def finalize(self):
        """
        Finalize logging session with summary and cleanup.
        """
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        status = "FAILED" if self.error_count > 0 else "SUCCESS"
        summary = f"Script: {self.script_name}, Errors: {self.error_count}, Duration: {duration:.2f}s, Status: {status}"
        self.info(summary)
        
        # Save/upload based on configuration
        if self.use_sharepoint:
            self.upload_to_sharepoint()
        else:
            self.save_to_local()
        
        self.cleanup()

    def cleanup(self):
        """Clean up resources and temporary files."""
        try:
            logging.shutdown()
            if os.path.exists(self.temp_log_file_path):
                os.remove(self.temp_log_file_path)
                print(f"[INFO] Temporary log file deleted: {self.temp_log_file_path}")
        except PermissionError as e:
            print(f"[WARNING] Permission denied while deleting log file: {str(e)}")
        except Exception as e:
            print(f"[WARNING] Failed to delete temporary log file: {str(e)}")

    def get_log_file_path(self):
        """Get the path where the final log file will be/is saved."""
        if self.use_sharepoint:
            return f"SharePoint: {self.sharepoint_url} -> {self.drive_name}/{self.folder_path}/{os.path.basename(self.temp_log_file_path)}"
        else:
            return self.final_log_file_path

    def get_configuration_summary(self):
        """Get a summary of the current logger configuration."""
        storage_type = "SharePoint" if self.use_sharepoint else "Local"
            
        return {
            "script_name": self.script_name,
            "storage_type": storage_type,
            "storage_location": self.get_log_file_path(),
            "dataverse_enabled": self.use_dataverse,
            "debug_mode": self.debug_mode,
            "start_time": self.start_time.isoformat(),
            "error_count": self.error_count,
            "uses_sharepoint": self.use_sharepoint,
        }

    # ===== LEGACY METHODS FOR BACKWARD COMPATIBILITY =====
    
    def log_info(self, message, details=None):
        """Legacy method for backward compatibility. Use info() instead."""
        self.info(message, details)
    
    def log_warning(self, message, details=None):
        """Legacy method for backward compatibility. Use warning() instead."""
        self.warning(message, details)
    
    def log_error(self, message, details=None, exc_info=True):
        """Legacy method for backward compatibility. Use error() instead."""
        self.error(message, details, exc_info)
    
    def log_debug(self, message, details=None):
        """Legacy method for backward compatibility. Use debug() instead."""
        self.debug(message, details)
    
    def log_critical(self, message, details=None):
        """Legacy method for backward compatibility. Use critical() instead."""
        self.critical(message, details)
    
    # Alternative legacy naming patterns
    def info_log(self, message, details=None):
        """Alternative legacy method for backward compatibility."""
        self.info(message, details)
    
    def warning_log(self, message, details=None):
        """Alternative legacy method for backward compatibility."""
        self.warning(message, details)
    
    def error_log(self, message, details=None, exc_info=True):
        """Alternative legacy method for backward compatibility."""
        self.error(message, details, exc_info)
    
    def debug_log(self, message, details=None):
        """Alternative legacy method for backward compatibility."""
        self.debug(message, details)
    
    def critical_log(self, message, details=None):
        """Alternative legacy method for backward compatibility."""
        self.critical(message, details)
    
    # Standard Python logging method names
    def warn(self, message, details=None):
        """Standard Python logging method name. Use warning() instead."""
        self.warning(message, details)