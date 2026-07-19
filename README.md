# Home Assistant TickTick Integration

![Static Badge](https://img.shields.io/badge/made%20with-fun-green?style=for-the-badge)‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎
![GitHub Repo stars](https://img.shields.io/github/stars/Hantick/ticktick-home-assistant?style=for-the-badge&color=%23AFB0CC)
![GitHub Release](https://img.shields.io/github/v/release/Hantick/ticktick-home-assistant?style=for-the-badge&color=%231CB00A)

Integration implements [TickTick Open API](https://developer.ticktick.com/docs#/openapi) and [Dida365 Open API](https://developer.dida365.com/docs#/openapi) with support for [To-do list](https://www.home-assistant.io/integrations/todo/) entities and exposes them as services in Home Assistant, allowing you to manage your tasks and projects programmatically 😎

## Buy me a coffee or beer 🍻
<a href="https://paypal.me/hantick" target="_blank" rel="noopener noreferrer">
    <img src="https://www.paypalobjects.com/marketing/web/logos/paypal-mark-color.svg" alt="PayPal" height="40"></a>

## Installation

1. Based on where your account is registered, go to [TickTick Developer](https://developer.ticktick.com/manage) for **TickTick (international)** or [Dida365 Developer](https://developer.dida365.com/manage) for **Dida365 (China)**, then click `New App`.
2. Name your app and set `OAuth redirect URL` to `https://my.home-assistant.io/redirect/oauth` or your instance url i.e `http://homeassistant.local:8123`
3. Add this repository in HACS and download TickTick Integration via HACS
4. In Settings → Devices & services, use the dotted menu to create new application credentials (`/config/application_credentials`) and enter the OAuth client ID and secret from the app you created.
5. Add the TickTick integration and select the same service you used for the developer app: **TickTick (international)** or **Dida365 (China region)**.
6. Your TickTick/Dida365 lists should now each turn up as a todo list in Home Assistant.

If you don’t want all of your lists to show up in the todo list app, you can disable selected lists in the entities list
(enter selection mode → Disable selected).

## Exposed Services

### Task Services

Get, Create, Update, Delete, Complete Task

### Project Services

Get (Create, Update, Delete are missing for now)

## Left to be done:

- Create/Update Task Service: `items` - The list of subtasks
- Create/Update Task Service: `reminders` - Can create some better builder for reminders
- Create/Update Task Service: `repeatFlag` - Can create some better builder for reminders
- Get Project By ID Service
- Get Project By ID With Data Service
- Create Project
- Update Project
- Delete Project
