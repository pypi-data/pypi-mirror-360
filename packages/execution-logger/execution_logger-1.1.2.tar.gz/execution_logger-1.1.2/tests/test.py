
CLIENT_ID = ""
CLIENT_SECRET = ""
TENANT_ID = ""
AUTHORITY = f""
SCOPE = ""
TOKEN_URL = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'
SHAREPOINT_URL= ""

DRIVE_NAME = ""  # Usually "Documents"
FOLDER_PATH = ""  # Adjust as needed

#!/usr/bin/env python3
"""
Simplified ExecutionLogger Tests - 3 Basic Scenarios

Basic test functions for ExecutionLogger:
1. Local logging only
2. SharePoint upload using sharepoint-uploader module
3. SharePoint + Dataverse error logging

Replace credentials with your actual values before running.
"""

from execution_logger import ExecutionLogger

# =============================================================================
# TEST 1: LOCAL LOGGING ONLY
# =============================================================================
def test_1_local_logging():
    """Test 1: Save locally and test all log types."""
    print("TEST 1: Local Logging Only")
    print("-" * 30)
    
    logger = ExecutionLogger(script_name="test_1_local")
    
    # Test all log types
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.debug("This is a debug message")
    logger.critical("This is a critical message")
    
    print(f"Log saved to: {logger.get_log_file_path()}")
    logger.finalize()
    print("✓ Test 1 completed\n")


# =============================================================================
# TEST 2: SHAREPOINT UPLOAD
# =============================================================================
def test_2_sharepoint_upload():
    """Test 2: Upload log file using sharepoint-uploader module."""
    print("TEST 2: SharePoint Upload")
    print("-" * 25)
    

    try:
        logger = ExecutionLogger(
            script_name="test_2_sharepoint",
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            tenant_id=TENANT_ID,
            sharepoint_url=SHAREPOINT_URL,
            drive_name=DRIVE_NAME,
            folder_path=FOLDER_PATH
        )
        
        logger.info("Testing SharePoint upload using sharepoint-uploader module")
        logger.warning("Sample warning for SharePoint")
        logger.error("Sample error for SharePoint")
        
        print(f"Will upload to: {logger.get_log_file_path()}")
        logger.finalize()
        print("✓ Test 2 completed\n")
        
    except Exception as e:
        print(f"❌ Test 2 failed: {str(e)}")
        print("Common issues:")
        print("- Install sharepoint-uploader: pip install sharepoint-uploader")
        print("- Check your SharePoint URL format")
        print("- Verify credentials and permissions\n")


# =============================================================================
# TEST 3: SHAREPOINT + DATAVERSE
# =============================================================================
def test_3_sharepoint_plus_dataverse():
    """Test 3: Upload log file + send errors to Dataverse."""
    print("TEST 3: SharePoint + Dataverse")
    print("-" * 30)
    
    try:
        logger = ExecutionLogger(
            script_name="test_3_sp_plus_dv",
            # SharePoint config
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            tenant_id=TENANT_ID,
            sharepoint_url=SHAREPOINT_URL,
            drive_name=DRIVE_NAME,
            folder_path=FOLDER_PATH,
            
            # Dataverse config
            # dv_client_id=CLIENT_ID,
            # dv_client_secret=CLIENT_SECRET,
            # dv_tenant_id=TENANT_ID,
            # dv_api_url = "https://orgcf43c216.crm4.dynamics.com/api/data/v9.0/cr672_app_errors"
        )
        
        logger.info("Testing SharePoint + Dataverse integration")
        logger.warning("This warning goes to SharePoint only")
        logger.error("Test| No action needed | This error goes to SharePoint AND Dataverse", "Error details for Dataverse")
        logger.error("Test| No action needed | Another error for Dataverse testing", "More error context")
        
        print(f"SharePoint: {logger.get_log_file_path()}")
        print("Dataverse: Check cr672_app_errors table")
        logger.finalize()
        print("✓ Test 3 completed\n")
        
    except Exception as e:
        print("This is Test")
        print(f"❌ Test 3 failed: {str(e)}")
        print("Common issues:")
        print("- Install sharepoint-uploader: pip install sharepoint-uploader")
        print("- Check SharePoint credentials and permissions")
        print("- Check Dataverse credentials and API access")
        print("- Verify Dataverse table 'cr672_app_errors' exists\n")


# =============================================================================
# CREDENTIAL HELPER
# =============================================================================
def show_credential_format():
    """Helper function to show the correct credential format."""
    print("CREDENTIAL FORMAT REFERENCE")
    print("=" * 40)
    print("\n1. SharePoint Credentials:")
    print("   CLIENT_ID = 'your-azure-app-client-id'")
    print("   CLIENT_SECRET = 'your-azure-app-client-secret'")
    print("   TENANT_ID = 'your-azure-tenant-id'")
    print("   SHAREPOINT_URL = 'https://yourcompany.sharepoint.com/sites/yoursitename'")
    print("   DRIVE_NAME = 'Documents'  # or 'Logs' or your document library name")
    print("   FOLDER_PATH = 'Logs/MyApp'  # folder path within the document library")
    
    print("\n2. Dataverse Credentials:")
    print("   DV_CLIENT_ID = 'your-dataverse-app-client-id'")
    print("   DV_CLIENT_SECRET = 'your-dataverse-app-client-secret'")
    print("   DV_TENANT_ID = 'your-tenant-id'  # can be same as SharePoint")
    
    print("\n3. Required Installation:")
    print("   pip install sharepoint-uploader")
    
    print("\n4. SharePoint URL Format:")
    print("   - Site URL: https://yourcompany.sharepoint.com/sites/yoursitename")
    print("   - NOT the full document library URL")
    print("   - Just the site URL")
    print()


# =============================================================================
# MAIN FUNCTION
# =============================================================================
def main():
    """Run all tests or individual test."""
    print("Simplified ExecutionLogger - 3 Basic Test Scenarios")
    print("=" * 55)
    print("Uses sharepoint-uploader module for SharePoint uploads")
    print("IMPORTANT: Replace credentials in each test function before running!")
    print("=" * 55)
    
    tests = [
        ("Local Logging Only", test_1_local_logging),
        ("SharePoint Upload", test_2_sharepoint_upload),
        ("SharePoint + Dataverse", test_3_sharepoint_plus_dataverse),
        ("Show Credential Format", show_credential_format)
    ]
    
    print("\nAvailable Tests:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"{i}. {name}")
    print("5. Run All Tests")
    
    try:
        choice = input("\nEnter test number (1-5): ").strip()
        
        if choice == "5":
            print("\nRunning all tests...")
            for name, test_func in tests[:3]:  # Skip credential helper in "run all"
                test_func()
        elif choice in ["1", "2", "3", "4"]:
            test_num = int(choice) - 1
            name, test_func = tests[test_num]
            print(f"\nRunning: {name}")
            test_func()
        else:
            print("Invalid choice")
            
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()