"""Constants for the TickTick Integration integration."""

DOMAIN = "ticktick"

CONF_REGION = "region"
REGION_TICKTICK = "ticktick"
REGION_DIDA365 = "dida365"

REGIONS = {
    REGION_TICKTICK: {
        "name": "TickTick (international)",
        "authorize_url": "https://ticktick.com/oauth/authorize",
        "token_url": "https://ticktick.com/oauth/token",
        "api_base_url": "https://api.ticktick.com/open/v1",
    },
    REGION_DIDA365: {
        "name": "Dida365 (China region)",
        "authorize_url": "https://dida365.com/oauth/authorize",
        "token_url": "https://dida365.com/oauth/token",
        "api_base_url": "https://api.dida365.com/open/v1",
    },
}
DEFAULT_REGION = REGION_TICKTICK
DEFAULT_API_BASE_URL = REGIONS[DEFAULT_REGION]["api_base_url"]

# === Parameters === #
PROJECT_ID = "projectId"
TASK_ID = "taskId"

# === Endpoints === #

# === Task Scope ===
GET_TASK = f"project/{{{PROJECT_ID}}}/task/{{{TASK_ID}}}"
CREATE_TASK = "task"
UPDATE_TASK = f"task/{{{TASK_ID}}}"
COMPLETE_TASK = f"project/{{{PROJECT_ID}}}/task/{{{TASK_ID}}}/complete"
DELETE_TASK = GET_TASK

# === Project Scope ===
GET_PROJECTS = "project"
GET_PROJECTS_WITH_TASKS = f"project/{{{PROJECT_ID}}}/data"
