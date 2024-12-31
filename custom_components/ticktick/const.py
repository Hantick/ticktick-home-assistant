"""Constants for the TickTick Integration integration."""

DOMAIN = "ticktick"

OAUTH2_AUTHORIZE = "https://ticktick.com/oauth/authorize"
OAUTH2_TOKEN = "https://ticktick.com/oauth/token"
TICKTICK_HOST = "api.ticktick.com"
API = "open/v1"
BASE_API_URL = f"{TICKTICK_HOST}/{API}"

# === Parameters === #
PROJECT_ID = "projectId"
TASK_ID = "taskId"

# === Endpoints === #

# === Task Scope ===
GET_TASK = f"{BASE_API_URL}/project/{{{PROJECT_ID}}}/task/{{{TASK_ID}}}"
CREATE_TASK = f"{BASE_API_URL}/task"
UPDATE_TASK = f"{BASE_API_URL}/task/{{{TASK_ID}}}"
COMPLETE_TASK = f"{BASE_API_URL}/project/{{{PROJECT_ID}}}/task/{{{TASK_ID}}}/complete"
DELETE_TASK = GET_TASK

# === Project Scope ===
GET_PROJECTS = f"{BASE_API_URL}/project"
GET_PROJECTS_WITH_TASKS = f"{BASE_API_URL}/project/{{{PROJECT_ID}}}/data"
