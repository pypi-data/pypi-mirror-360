# Malachi - Windows 10 Toast Notifications

## Overview
Malachi is a Python module designed to create Windows 10 toast notifications. It is a customized version of the `win10toast_click` module, which is no longer maintained. This module allows users to display notifications with custom icons, messages, and click callbacks.

## Features
- Display Windows 10 toast notifications.
- Support for custom icons.
- Configurable duration for notifications.
- Threaded notifications to avoid blocking.
- Callback functionality for mouse clicks within the notification window.

## Installation
To install the module, use the following command:

```bash
pip install malachi
```

## Usage
### Basic Notification
```python
from malachi import ToastNotifier

notifier = ToastNotifier()
notifier.show_toast(
    title="Notification Title",
    msg="This is a sample notification message",
    duration=5
)
```

### Notification with Custom Icon
```python
notifier.show_toast(
    title="Custom Icon Notification",
    msg="This notification has a custom icon",
    icon_path="path/to/icon.ico",
    duration=5
)
```

### Threaded Notification
```python
notifier.show_toast(
    title="Threaded Notification",
    msg="This notification runs in a separate thread",
    threaded=True
)
```

### Notification with Click Callback
```python
def on_click():
    print("Notification clicked!")

notifier.show_toast(
    title="Clickable Notification",
    msg="Click me!",
    callback_on_click=on_click
)
```

## API Reference
### `ToastNotifier`
#### `show_toast`
Displays a toast notification.

**Parameters:**
- `title` (str): The title of the notification.
- `msg` (str): The message to display.
- `icon_path` (str, optional): Path to the `.ico` file for the notification icon.
- `duration` (int, optional): Duration in seconds before the notification self-destructs. Set to `None` for no self-destruction.
- `threaded` (bool, optional): Whether to run the notification in a separate thread.
- `callback_on_click` (callable, optional): Function to call when the notification is clicked.

#### `notification_active`
Checks if there is an active notification.

**Returns:**
- `bool`: `True` if a notification is active, `False` otherwise.

## License
This project is licensed under the MIT License.

## Acknowledgments
This module is inspired by the `win10toast_click` module created by [jithurjacob](https://github.com/jithurjacob/Windows-10-Toast-Notifications).
