# Django Notifications WebSocket

A Django app for both real-time and HTTP API notifications, utilizing WebSocket, Django Rest Framework (DRF), Channels, and Redis. This package enables easy integration of WebSocket notifications into your Django project, allowing you to efficiently broadcast real-time events to users while also providing HTTP API support for managing notifications.

## Features

- **Real-time notifications** using WebSocket and Channels.
- **Notifications HTTP API** using Django Rest Framework (DRF).
- **Redis support** for efficient message broadcasting and scalability.
- **Django Integration**: Easily integrate this app into your Django project with minimal configuration.

## Installation

To install the package, use pip:

```bash
pip install django-notifications-websocket
```

### Prerequisites

This package provides both REST API and WebSocket API for notifications. To use the REST API and token-based authentication, the following packages must be installed in your environment:

- `djangorestframework` – for REST API support.
- `djangorestframework-simplejwt` – for token-based authentication.

You can install these packages by running:

```bash
pip install djangorestframework djangorestframework-simplejwt
```


## Configuration

### 1. Update `settings.py`

1. **Add Daphne to `INSTALLED_APPS`:**

   Add `daphne` at the top of your `INSTALLED_APPS` list:

   ```python
   INSTALLED_APPS = [
       'daphne',
       'django.contrib.admin',
       ...
       'notifications',
   ]
   ```

2. **Add `DRFCurrentUserMiddleware` to `MIDDLEWARE`:**

   In your `MIDDLEWARE` setting, add `DRFCurrentUserMiddleware` below `AuthenticationMiddleware`:

   ```python
   MIDDLEWARE = [
       "django.middleware.security.SecurityMiddleware",
       ...
       "django.contrib.auth.middleware.AuthenticationMiddleware",
       "notifications.middleware.current_user_middleware.DRFCurrentUserMiddleware",
       ...
   ]
   ```

3. **Set up `ASGI_APPLICATION`:**

   Configure the `ASGI_APPLICATION` setting to point to your project’s ASGI application:

   ```python
   ASGI_APPLICATION = "(your_project_name).asgi.application"
   ```

4. **Set up Channel Layers:**

   Add the `CHANNEL_LAYERS` configuration to use Redis as the backend for Channels:

   ```python
   CHANNEL_LAYERS = {
       "default": {
           "BACKEND": "channels_redis.core.RedisChannelLayer",
           "CONFIG": {
               "hosts": [("127.0.0.1", 6379)],
           },
       },
   }
   ```

5. **Set up User Serializer**

    To configure the user serializer for the notification system, you need to specify it in your settings file. You have two options for the `NOTIFICATION_USER_SERIALIZER`:

Define a custom user serializer specific to your project:

   ```python
   # Use your custom user serializer by specifying its full import path
   NOTIFICATION_USER_SERIALIZER = 'your_app.serializers.UserSerializerName'
   ```

Use the package's built-in custom user serializer:

   ```python
   # Use the default custom user serializer provided by the notifications package
   NOTIFICATION_USER_SERIALIZER = 'notifications.serializers.CustomUserSerializer'
   ```

This configuration ensures that the system knows which serializer to use when handling user data in notifications.

---

### 2. Update `asgi.py`

Modify your `asgi.py` file to handle both HTTP and WebSocket connections. Below is an example:

```python
import os

from django.core.asgi import get_asgi_application

from notifications.routing import websocket_urlpatterns
from notifications.middleware.jwt_middleware import JWTAuthMiddleware

from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "(your_project_name).settings")

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(websocket_urlpatterns)),
    }
)
```

---

### 3. Update `urls.py`

Add the notifications API to your project’s `urlpatterns`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path("api/v1/me/notifications", include("notifications.urls")),
    ...
]
```
---

## Notes

- Ensure Redis is installed and running on your system.
- This package relies on `daphne` to run ASGI applications. Make sure you’ve properly configured your project to use ASGI.
- Use the provided HTTP API endpoints to manage notifications, and WebSocket for real-time notification updates.

---

---

## HTTP API Endpoints

Sure! Here's your **Notifications API** section in compact table format as requested:

---

## Notifications API

| **Endpoint**                                  | **Method** | **Description**                                                                                          | **Headers**                         | **Query Parameters**                   | **Payload Example**                                                                                            |
| --------------------------------------------- | ---------- | -------------------------------------------------------------------------------------------------------- | ----------------------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `/api/v1/me/notifications`                    | `GET`      | Retrieve authenticated user’s notifications. Supports filtering and pagination.                          | `Authorization: Bearer <JWT_TOKEN>` | `page=<num>`<br>`is_read=<true/false>` | None                                                                                                           |
| `/api/v1/me/notifications`                    | `PATCH`    | Perform an action to update multiple notifications.                                                      | `Authorization: Bearer <JWT_TOKEN>` | None                                   | `{"action_choice":"MARK_AS_READ", "notification_uids": ["uid1", "uid2"]}`<br>`{"action_choice":"REMOVED_ALL"}` |
| `/api/v1/me/notifications/<notification_uid>` | `GET`      | Retrieve detailed information of a specific notification. Automatically marks it as read if not already. | `Authorization: Bearer <JWT_TOKEN>` | None                                   | None                                                                                                           |
| `/api/v1/me/notifications/<notification_uid>` | `PATCH`    | Update the status of a specific notification.                                                            | `Authorization: Bearer <JWT_TOKEN>` | None                                   | `{"status": "REMOVED"}`<br>`{"status": "DELETED"}`                                                             |

---


### Action Choices for Notification List PATCH Endpoint

The following table explains the valid choices for `action_choice` and their required payloads:

| **Action Choice**       | **Description**                      | **Payload Example**                                                                                       |
|--------------------------|--------------------------------------|----------------------------------------------------------------------------------------------------------|
| `MARK_AS_READ`           | Marks specific notifications as read. | `{"action_choice":"MARK_AS_READ", "notification_uids": ["uid1", "uid2"]}`                                |
| `MARK_AS_REMOVED`        | Marks specific notifications as removed. | `{"action_choice":"MARK_AS_REMOVED", "notification_uids": ["uid1", "uid2"]}`                             |
| `MARK_ALL_AS_READ`       | Marks all notifications as read.      | `{"action_choice":"MARK_ALL_AS_READ"}`                                                                   |
| `REMOVED_ALL`            | Removes all notifications.            | `{"action_choice":"REMOVED_ALL"}`                                                                        |
| `UNDEFINED`              | No specific action defined.           | Not applicable                                                                                           |

---

Here's how the sample response can be incorporated into the API documentation:

---

### Sample Responses

#### **GET Notifications**

**Request:**

```http
GET http://localhost:8000/api/v1/me/notifications?page=1&is_read=false HTTP/1.1
Authorization: Bearer <JWT_TOKEN>
```

**Response:**

```json
{
    "total_notifications": 497,
    "read_notifications": 55,
    "unread_notifications": 442,
    "notifications": [
        {
            "id": 501,
            "uid": "9d032eaa-860e-4587-98ac-358c8b49741d",
            "user": {
                "id": 1,
                "first_name": "test",
                "last_name": "user",
                "email": "testuser@gmail.com"
            },
            "notification": {
                "message": "New blog post by test user",
                "model": "Blog",
                "instance": {
                    "id": 1,
                    "title": "New Blog",
                    "content": "Blog content"
                },
                "method": "POST",
                "changed_data": {}
            },
            "is_read": true,
            "custom_info": null,
            "created_by": {
                "id": 2,
                "first_name": "Admin",
                "last_name": "user",
                "email": "admin@gmail.com"
            },
            "status": "ACTIVE",
            "created_at": "2024-12-14T07:32:10.269207Z",
            "updated_at": "2024-12-14T07:35:39.155092Z"
        }
    ]
}
```

---

This response format provides additional context for developers integrating with the notifications API, illustrating the structure of the `GET` request payload and the detailed information returned. Here's what each field represents:

- **`total_notifications`**: Total number of notifications for the authenticated user.
- **`read_notifications`**: Count of read notifications.
- **`unread_notifications`**: Count of unread notifications.
- **`notifications`**: List of notifications with detailed fields:
  - **`id`**: Internal ID of the notification.
  - **`uid`**: Unique identifier for the notification.
  - **`user`**: Details of the user receiving the notification.
  - **`notification`**: Object containing:
    - `message`: The notification text.
    - `model`: The associated model's name.
    - `instance`: Details of the related instance.
    - `method`: HTTP method related to the event.
    - `changed_data`: Information about any data changes.
  - **`is_read`**: Boolean indicating whether the notification has been read.
  - **`custom_info`**: Additional custom information (if any).
  - **`created_by`**: Details of the user who triggered the notification.
  - **`status`**: Current status of the notification (e.g., ACTIVE).
  - **`created_at`**: Timestamp of notification creation.
  - **`updated_at`**: Timestamp of the last update to the notification.


---

## WebSocket API Documentation for Real-Time Notifications

### **WebSocket Endpoint**

* **URL**: `ws://localhost:8000/ws/me/notifications`
* **Authentication**: Pass the **JWT token only**  using the `Sec-WebSocket-Protocol` header.

---

### **Connection Request**

Use a WebSocket client (e.g. Postman, browser, frontend) and include the JWT token directly:

```
Sec-WebSocket-Protocol: <JWT_TOKEN>
```

---

### **Initial Response on Connection**

Upon a successful connection, the server sends a structured response containing notification data and pagination info.

**Example Initial Response:**

```json
{
  "results": {
    "total_notifications": 497,
    "read_notifications": 56,
    "unread_notifications": 441,
    "notifications": [
      {
        "id": 501,
        "uid": "9d032eaa-860e-4587-98ac-358c8b49741d",
        "user": {
          "id": 1,
          "first_name": "test",
          "last_name": "user",
          "email": "testuser@gmail.com"
        },
        "notification": {
          "message": "New blog post by test user",
          "model": "Blog",
          "instance": {
            "id": 1,
            "title": "New Blog",
            "content": "Blog content"
          },
          "method": "POST",
          "changed_data": {}
        },
        "is_read": true,
        "custom_info": null,
        "created_by": {
          "id": 2,
          "first_name": "Admin",
          "last_name": "user",
          "email": "admin@gmail.com"
        },
        "status": "ACTIVE",
        "created_at": "2024-12-14T07:32:10.269207Z",
        "updated_at": "2024-12-14T07:35:39.155092Z"
      }
      // ... more notifications
    ]
  },
  "pagination": {
    "page": 1,
    "page_size": 25,
    "total_pages": 20,
    "total_items": 497
  }
}
```

---

### **Real-Time Updates**

Any changes to notifications (e.g., creation, read status update) are pushed as a real-time message using the same structure:

* `results`: notification counts and list
* `pagination`: current pagination context

---

### **Client-Side Interaction for Pagination and Filtering**

To request specific data (e.g., next page or filtered list), send a JSON message through the WebSocket:

#### **Pagination Request**

```json
{
  "page": 2
}
```

#### **Filter by Read Status**

```json
{
  "is_read": true
}
```

#### **Combined Example**

```json
{
  "page": 2,
  "is_read": false
}
```

The server will respond with the updated `results` and `pagination` blocks accordingly.


---



### How to Create Notifications Using the Notification Service

This guide explains how to use the **NotificationService** provided by the `notifications` app to generate notifications for users. Notifications can be created in any part of your application, such as serializers, views, or other services.

---

#### **Import NotificationService**
Before using the service, import it in the required module:
```python
from notifications.service import NotificationService
```

---

#### **Example: Notification for a Blog Model**
Assume we have a `Blog` model where notifications are triggered when a blog is created or updated.

**Model Definition:**
```python
from django.db import models

class Blog(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    status = models.CharField(
        max_length=20, choices=BlogStatus.choices, default=BlogStatus.PUBLISHED
    )

    def __str__(self):
        return self.title
```

---

---


## **NotificationService Usage Guide**

The `NotificationService` class simplifies the creation and retrieval of notifications in your Django project. Below are three key functionalities with usage examples:

---

### **1. Creating Notifications**

To create a notification, you need to specify the `requested_user`, `message`, `instance`, `method`, and a list of users to notify. Here’s how:

```python
from notifications.services import NotificationService

# Assume `blog_instance` is an instance of the Blog model and `user_list` is a queryset of User
service = NotificationService(
    requested_user=request.user,
    message=f"New blog '{blog_instance.title}' published!",
    instance=blog_instance,
    method="POST",
    user_list=User.objects.filter(is_active=True),  # Notify all active users
)

result = service.create_notification()

```

---

### **2. Retrieve Notifications for the Current User**

To fetch all notifications for the currently logged-in user, use the following:

```python
from notifications.services import NotificationService

service = NotificationService(requested_user=request.user)
notifications = service.get_requested_user_notifications()

```

---

### **3. Retrieve Notifications for a Specific Model**

You can retrieve notifications specific to a particular model by specifying the model's name:

```python
from notifications.services import NotificationService

service = NotificationService(requested_user=request.user)
model_notifications = service.get_model_notifications("Blog")

```

---

These examples demonstrate how to use the `NotificationService` to handle notifications seamlessly. For more advanced use cases, refer to the detailed service implementation.



#### **Using NotificationService in a Serializer**

Notifications can be triggered within the `create` or `update` methods of the serializer. Here's how:

**Serializer Example:**
```python
from rest_framework import serializers
from notifications.services import NotificationService
from django.contrib.auth.models import User  # Replace with your custom User model if applicable

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["request"].user  # The user creating the blog
        blog = super().create(validated_data)  # Create the blog instance

        # Prepare notification details
        message = f"New blog '{blog.title}' published by {user.username}"
        user_list = User.objects.filter()  # List of users to notify (adjust query as needed)

        # Create and send the notification
        notification = NotificationService(
            requested_user=user,
            message=message,
            instance=blog,  # The model instance associated with the notification
            method="POST",  # HTTP method triggering the notification
            user_list=user_list,
            serializer=BlogSerializer  # Optional: Pass a serializer to include instance data in the notification
        )
        notification.create_notification()

        return blog

    def update(self, instance, validated_data):
        user = self.context["request"].user
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.status = validated_data.get("status", instance.status)

        # Prepare notification details
        message = f"Blog '{instance.title}' updated by {user.username}"
        user_list = User.objects.filter()  # List of users to notify

        # Create and send the notification
        notification = NotificationService(
            requested_user=user,
            message=message,
            instance=instance,  # Pass the instance before saving to track changes
            method="PUT",  # HTTP method triggering the notification
            user_list=user_list,
            serializer=BlogSerializer  # Optional serializer
        )
        notification.create_notification()

        instance.save()
        return instance
```

---

#### **Explanation of Parameters in NotificationService**

| **Parameter**        | **Description**                                                                                  |
|-----------------------|--------------------------------------------------------------------------------------------------|
| `requested_user`      | The user triggering the notification. Typically, the logged-in user.                            |
| `message`             | A string containing the notification message.                                                   |
| `instance`            | The model instance associated with the notification.                                            |
| `method`              | The HTTP method or action triggering the notification. Options: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `UNDEFINED`. |
| `user_list`           | A list of users who should receive the notification.                                            |
| `serializer` (Optional) | An optional serializer instance to serialize the model data for the notification.             |

---

#### **How It Works**
1. When a `Blog` instance is created or updated, the `NotificationService` is invoked with the relevant data.
2. The service creates a notification and sends it to all users in the `user_list`.
3. Notifications can include additional serialized data from the provided `instance` and `serializer`.

---

#### **Recommendations**
- Use the `NotificationService` sparingly in serializers or views to avoid overloading the system with notifications.


