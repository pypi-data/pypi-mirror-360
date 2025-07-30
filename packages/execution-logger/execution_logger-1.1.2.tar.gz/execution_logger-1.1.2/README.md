# ExecutionLogger

A Python logging solution with 3 storage options: Local files, SharePoint uploads, and optional Dataverse error tracking.

## Quick Start

```python
from execution_logger import ExecutionLogger

# Local only
logger = ExecutionLogger(script_name="my_app")
logger.info("Hello World")
logger.finalize()
```

## Dependencies

```bash
pip install requests msal sharepoint-uploader
```

## 3 Storage Scenarios

### 1. Local Only
```python
logger = ExecutionLogger(script_name="my_app")
```
- Saves logs to script directory
- No additional setup required

### 2. SharePoint Upload
```python
logger = ExecutionLogger(
    script_name="my_app",
    client_id="your-azure-client-id",
    client_secret="your-azure-client-secret",
    tenant_id="your-azure-tenant-id",
    sharepoint_url="https://company.sharepoint.com/sites/sitename",
    drive_name="Documents",
    folder_path="Logs/MyApp"
)
```
- Uploads logs to SharePoint using [sharepoint-uploader](https://pypi.org/project/sharepoint-uploader/)
- Requires Azure App Registration with SharePoint permissions

### 3. SharePoint + Dataverse
```python
logger = ExecutionLogger(
    script_name="my_app",
    # SharePoint params (same as above)
    client_id="your-azure-client-id",
    client_secret="your-azure-client-secret", 
    tenant_id="your-azure-tenant-id",
    sharepoint_url="https://company.sharepoint.com/sites/sitename",
    drive_name="Documents",
    folder_path="Logs/MyApp",
    # Dataverse params (often same as SharePoint - see note below)
    dv_client_id="your-dataverse-client-id",  # Usually same as SharePoint
    dv_client_secret="your-dataverse-client-secret",  # Usually same as SharePoint
    dv_tenant_id="your-tenant-id",  # Usually same as SharePoint
    dv_scope="https://yourorg.crm.dynamics.com/.default",
    dv_api_url="https://yourorg.crm.dynamics.com/api/data/v9.0/your_table_name"
)
```
- Uploads logs to SharePoint
- Sends **only errors** to Dataverse table

> **💡 Microsoft Tools Integration**: Since SharePoint and Dataverse are both Microsoft tools, you can typically use the **same Azure App Registration** for both services. This means `client_id`, `client_secret`, and `tenant_id` are often identical for SharePoint and Dataverse - just add the appropriate API permissions to one app registration.

## Dataverse Table Setup

### Required Table Structure
Create a Dataverse table with these **exact column names**:

| Column Name | Data Type | Max Length | Description |
|-------------|-----------|------------|-------------|
| `cr672_app` | Text | 1000 | Application name |
| `cr672_message` | Text | 1000 | Error message |
| `cr672_source` | Text | 200 | Error context |
| `cr672_details` | Text | 4000 | Full error details with timestamp |
| `cr672_id` | Text | 50 | Record identifier |

### Dataverse Table Creation Steps
1. Go to [Power Apps](https://make.powerapps.com)
2. Select your environment
3. **Data** → **Tables** → **New table**
4. Name: `App Errors` (or your preferred name)
5. Add the 5 columns above with exact names and data types
6. Save and publish

### API URL Format
```
https://yourorg.crm.dynamics.com/api/data/v9.0/cr672_app_errors
```
Replace:
- `yourorg` with your organization name
- `cr672_app_errors` with your table's plural name

## Azure App Registration Setup

> **💡 Single App Registration**: Since SharePoint and Dataverse are both Microsoft tools, you can use **one Azure App Registration** for both services. Simply add permissions for both APIs to the same app.

### For SharePoint Access
1. [Azure Portal](https://portal.azure.com) → **App Registrations** → **New registration**
2. Note **Application (client) ID** and **Directory (tenant) ID**
3. **Certificates & secrets** → Create **client secret**
4. **API permissions** → Add **Microsoft Graph** → **Sites.ReadWrite.All**
5. Grant admin consent

### For Dataverse Access (Same App Registration)
1. **Same app registration** → **API permissions** → Add **Dynamics CRM** → **user_impersonation**
2. Grant admin consent
3. In Dataverse, assign appropriate security role to the app

### Credential Reuse
When using the same app registration:
- `client_id` = Same for both SharePoint and Dataverse
- `client_secret` = Same for both SharePoint and Dataverse  
- `tenant_id` = Same for both SharePoint and Dataverse
- Only `dv_scope` and `dv_api_url` are Dataverse-specific

## Logging Methods

```python
logger.info("Information message", "Optional details")
logger.warning("Warning message", "Warning context")
logger.error("Error message", "Error details")  # Only errors go to Dataverse
logger.debug("Debug message", "Debug context")
logger.critical("Critical message", "Critical details")
```

## Parameter Reference

### SharePoint Parameters (All required for SharePoint upload)
- `client_id`: Azure app client ID
- `client_secret`: Azure app client secret  
- `tenant_id`: Azure tenant ID
- `sharepoint_url`: Site URL (e.g., `https://company.sharepoint.com/sites/sitename`)
- `drive_name`: Document library name (e.g., `Documents`, `Logs`)
- `folder_path`: Target folder (e.g., `Logs/MyApp`)

### Dataverse Parameters (Optional)
- `dv_client_id`: Dataverse app client ID (typically same as SharePoint `client_id`)
- `dv_client_secret`: Dataverse app client secret (typically same as SharePoint `client_secret`)
- `dv_tenant_id`: Dataverse tenant ID (typically same as SharePoint `tenant_id`)
- `dv_scope`: Dataverse scope (e.g., `https://yourorg.crm.dynamics.com/.default`)
- `dv_api_url`: Dataverse API endpoint (e.g., `https://yourorg.crm.dynamics.com/api/data/v9.0/cr672_app_errors`)

> **Note**: Since both SharePoint and Dataverse are Microsoft services, most organizations use the same Azure App Registration for both, meaning the first three parameters are identical.

### Other Parameters
- `local_log_directory`: Custom local directory (defaults to script directory)
- `debug`: Enable debug logging (default: `False`)

## Error Handling

- **SharePoint upload fails**: Warning logged, execution continues
- **Dataverse fails**: Warning logged, execution continues  
- **Authentication fails**: Exception raised during initialization
- **Local save fails**: Warning logged

## Troubleshooting

### SharePoint Issues
```
❌ sharepoint-uploader module not installed
```
**Fix**: `pip install sharepoint-uploader`

```
❌ Authentication failed
```
**Fix**: Check Azure app permissions and credentials

### Dataverse Issues
```
❌ Failed to post error to Dataverse: 404
```
**Fix**: Verify table exists and API URL is correct

```
❌ Failed to post error to Dataverse: 401
```
**Fix**: Check app registration has Dataverse permissions

### Common URL Formats
- ✅ **Correct SharePoint URL**: `https://company.sharepoint.com/sites/sitename`
- ❌ **Wrong**: `https://company.sharepoint.com/sites/sitename/Shared Documents`
- ✅ **Correct Dataverse URL**: `https://orgname.crm.dynamics.com/api/data/v9.0/tablename`

## Complete Example

```python
import os
from execution_logger import ExecutionLogger

def main():
    # Using same Azure app registration for both SharePoint and Dataverse
    azure_client_id = os.getenv('AZURE_CLIENT_ID')
    azure_client_secret = os.getenv('AZURE_CLIENT_SECRET')
    azure_tenant_id = os.getenv('AZURE_TENANT_ID')
    
    logger = ExecutionLogger(
        script_name="daily_processor",
        # SharePoint
        client_id=azure_client_id,
        client_secret=azure_client_secret,
        tenant_id=azure_tenant_id,
        sharepoint_url="https://company.sharepoint.com/sites/logs",
        drive_name="Documents",
        folder_path="ApplicationLogs",
        # Dataverse (reusing same credentials)
        dv_client_id=azure_client_id,  # Same app registration
        dv_client_secret=azure_client_secret,  # Same app registration
        dv_tenant_id=azure_tenant_id,  # Same app registration
        dv_scope="https://company.crm.dynamics.com/.default",
        dv_api_url="https://company.crm.dynamics.com/api/data/v9.0/cr672_app_errors"
    )
    
    try:
        logger.info("Process started")
        # Your application logic
        process_data()
        logger.info("Process completed successfully")
    except Exception as e:
        logger.error("Process failed", f"Exception: {str(e)}")
    finally:
        logger.finalize()

if __name__ == "__main__":
    main()
```

## Key Features

- **3 flexible storage options**: Local, SharePoint, or SharePoint + Dataverse
- **Automatic error tracking**: Only errors sent to Dataverse
- **Robust error handling**: Graceful degradation when services unavailable
- **Easy authentication**: Uses proven sharepoint-uploader module
- **Production ready**: Environment variable support and comprehensive logging