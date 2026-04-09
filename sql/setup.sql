-- Replace the placeholder identifiers before running this setup.
-- Run with a role that can grant account/database access to the application role.

GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE CORTEX_DEV_ROLE;
GRANT USAGE ON WAREHOUSE DEV_XS_WH TO ROLE CORTEX_DEV_ROLE;
GRANT USAGE ON DATABASE DEV_DB TO ROLE CORTEX_DEV_ROLE;
GRANT USAGE ON SCHEMA DEV_DB.PUBLIC TO ROLE CORTEX_DEV_ROLE;
