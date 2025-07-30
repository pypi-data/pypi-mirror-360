# Overview

nacwrap is a python package for interacting with the Nintex Automation Cloud system. Creating workflow instances, delegating tasks, etc. Essentially just a wrapper for the NAC API.

## Installation

`pip install nacwrap`

## Usage

Several environment variables are required for nacwrap to function.

| Required? | Env Variable         | Description                                                                                                                                                                                                     |
| --------- | -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Yes       | NINTEX_CLIENT_ID     | Client ID for connecting to Nintex API. Created in Apps and Tokens page in NAC.                                                                                                                                 |
| Yes       | NINTEX_CLIENT_SECRET | Client secret for connecting to Nintex API. Created in Apps and Tokens page in NAC.                                                                                                                             |
| Yes       | NINTEX_GRANT_TYPE    | Value should be 'client_credentials'.                                                                                                                                                                           |
| Yes       | NINTEX_BASE_URL      | Value depends on which Nintex region you are in. US is, for example 'us.nintex.io'. <https://developer.nintex.com/docs/nc-api-docs/d2924cfeea6e8-welcome-to-the-nintex-automation-cloud-api#choose-your-region> |

### Instances - Create Instance

Function to create a workflow instance. Takes in two parameters.

| Param       | Description                                                                                                                   |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------- |
| workflow_id | The ID of the workflow you want to create an instance for.                                                                    |
| start_data  | Optional, any start data the worklfow requires. Should be provided in dictionary format. Returns JSON response if successful. |

### Instances - List Instances

Function to return instance data. Takes a number of parameters for filtering what instance data to get.

### Tasks - Delegate Assignment (TODO)

Make function to delegate tasks from one user to another.

### Tasks - Task Search

Returns Nintex Tasks as a list of NintexTask objects. Takes a number of parameters for filtering what tasks to retrieve.

| Param         | Description                                           |
| ------------- | ----------------------------------------------------- |
| workflow_name | Limit results to workflows matching this name.        |
| instance_id   | Return tasks for a specific workflow instance id.     |
| status        | Limit results to tasks with a particular status.      |
| assignee      | Limit results to tasks assigned to a particular user. |
| dt_from       | Begin date of date filter range.                      |
| dt_to         | End date of date filter range.                        |

### Users - List Users

Returns Nintex Users as a list of NintexUser objects. Takes a number of parameters for filtering what users to retrieve.

| Param  | Description                                       |
| ------ | ------------------------------------------------- |
| id     | Limit results to user matching this guid          |
| email  | Limit results to user matching this email         |
| filter | Limit results to user matching this email or name |
| role   | Limit results to users matching this role         |
