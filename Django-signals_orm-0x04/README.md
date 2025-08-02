# Django Messaging System with Notifications and Threaded Conversations

A robust messaging system built with Django that includes real-time notifications and threaded conversations using Django's ORM.

---

## Features

- **User Authentication**: Secure user registration and authentication
- **Conversations**: Create and manage conversations between users
- **Real-time Messaging**: Send and receive messages in conversations
- **Threaded Conversations**: Reply to specific messages in a thread
- **Message History**: Track and view complete edit history of messages
- **Notifications**: Automatic notifications for new messages and replies
- **Account Deletion**: Delete user account and associated data
- **RESTful API**: Built with Django REST Framework
- **Unread Messages**: Track and manage unread messages for each user
- **Performance Caching**: Optimized response times with view-level caching

---

## Models

### User

- Authentication and basic user information
- Related names: `sent_messages`, `received_messages`, `notifications`

### Conversation

- Groups of users in a conversation
- Fields: `conversation_id`, `participants`, `created_at`
- Related name: `messages`

### Message

- Individual messages within a conversation
- Fields: `message_id`, `sender`, `receiver`, `conversation`, `content`, `timestamp`, `edited`, `is_thread`, `parent_message`, `read`
- Related names: `notifications`, `history`, `replies`
- The `edited` flag indicates if the message has been modified
- `is_thread` indicates if a message has replies
- `parent_message` references the parent message for threaded replies
- `read` indicates if the message has been read by the recipient

### MessageHistory

- Tracks all edits made to messages
- Fields: `message` (FK to Message), `content` (previous content), `edited_at`, `edited_by` (FK to User)
- Ordered by `edited_at` in descending order

### Notification

- Tracks message notifications for users
- Fields: `user`, `message`, `is_read`, `created_at`

---

## API Endpoints

### Authentication

- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Conversations

- `GET /api/conversations/` - List all conversations
- `POST /api/conversations/` - Create new conversation
- `GET /api/conversations/{id}/` - Retrieve conversation details

### Messages

- `GET /api/conversations/{id}/messages/` - List top-level messages in conversation
- `POST /api/conversations/{id}/messages/` - Send new message or reply
- `GET /api/conversations/{id}/messages/{message_id}/thread/` - Get a message and all its replies
- `PATCH /api/messages/{id}/` - Update message (automatically tracks edit history)
- `DELETE /api/messages/{id}/` - Delete message
- `GET /api/messages/{id}/history/` - View edit history of a message
- `GET /api/messages/unread/` - List all unread messages for the current user
- `PATCH /api/messages/unread/` - Mark messages as read

### Notifications

- `GET /api/notifications/` - List user notifications
- `PATCH /api/notifications/{id}/` - Mark notification as read

### User Account

- `DELETE /api/user/delete/` - Delete the authenticated user's account and all associated data

---

## Performance Caching

The application implements view-level caching to improve response times and reduce server load:

### Caching Features

- **View Caching**: Message list view is cached for 60 seconds
- **Memory-Efficient**: Uses Django's built-in LocMemCache backend
- **Automatic Invalidation**: Cache automatically expires after the timeout period
- **User-Specific**: Cache is user-specific to maintain data privacy

### Implementation Details

- **Cache Backend**: Local memory cache (LocMemCache)
- **Cache Key**: Automatically generated based on request URL and user session
- **Cache Timeout**: 60 seconds for message list view
- **Cache Invalidation**: Automatic after timeout or server restart

### Cached Endpoints

- `GET /api/conversations/{id}/messages/` - Cached for 60 seconds

### Example Configuration

```python
# Cache settings in settings.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# View implementation
@method_decorator(cache_page(60))
def list(self, request, *args, **kwargs):
    """List all messages in a conversation with caching."""
    return super().list(request, *args, **kwargs)
```

### Best Practices

1. **Cache Invalidation**: The cache automatically invalidates after the timeout period
2. **Sensitive Data**: Cache respects authentication and permissions
3. **Development**: Disable caching in development by setting `CACHES['default']['BACKEND']` to `'django.core.cache.backends.dummy.DummyCache'`
4. **Production**: Consider using Redis or Memcached for production deployments

---

## Threaded Conversations

The system supports threaded conversations where users can reply to specific messages:

### Threaded Conversations Features

- **Threaded Replies**: Reply directly to any message to start a thread
- **Nested Conversations**: View complete conversation threads
- **Efficient Queries**: Optimized with `select_related` and `prefetch_related`
- **Thread Indicators**: Messages with replies are marked with `is_thread: true`

### How It Works (Threaded Conversations)

1. **Creating a Thread**:
   - Send a message with a `parent_message` ID to create a reply
   - The system automatically marks the parent message as a thread

2. **Viewing Threads**:
   - Top-level messages are fetched by default
   - Use the thread endpoint to view a message and all its replies
   - Each message includes a `reply_count` and `thread_depth`

3. **Performance**:
   - Uses Django's ORM optimizations
   - Database indexes on frequently queried fields
   - Efficient recursive querying of thread hierarchies

### Example API Usage

1. **Create a new thread**:

   ```http
   POST /api/conversations/{conversation_id}/messages/
   {
       "content": "This is a new thread"
   }
   ```

2. **Reply to a message**:

   ```http
   POST /api/conversations/{conversation_id}/messages/
   {
       "content": "This is a reply",
       "parent_message": "message_id_here"
   }
   ```

3. **View a thread**:

   ```http
   GET /api/conversations/{conversation_id}/messages/{message_id}/thread/
   ```

---

## Message Edit History

The application automatically tracks all edits made to messages:

- Each time a message is edited, the previous version is saved to the `MessageHistory` model
- The `edited` flag on the Message model is automatically set to `True` when content is modified
- Edit history includes:
  - Previous content
  - Timestamp of edit
  - User who made the edit

### Viewing Edit History

Edit history can be viewed:

1. Through the Django admin interface
2. Via the API endpoint: `GET /api/messages/{id}/history/`
3. Each history entry shows the previous content and when/why it was changed

---

## Unread Messages

The system tracks unread messages for each user, allowing for efficient message status management:

### Unread Messages Features

- **Read Status Tracking**: Each message includes a `read` boolean field
- **Efficient Queries**: Custom manager with optimized queries using `select_related` and `only()`
- **Bulk Operations**: Mark multiple messages as read in a single request
- **Performance**: Database indexes on the `read` field for fast lookups

### How It Works (Unread Messages)

1. **Message Status**:
   - New messages are created with `read=False` by default
   - The `read` status is automatically updated when the recipient views the message

2. **Retrieving Unread Messages**:
   - Use the custom manager: `Message.unread.unread_for_user(user)`
   - Returns a queryset with only unread messages for the specified user
   - Optimized to fetch only necessary fields

3. **Marking Messages as Read**:
   - Single endpoint for marking multiple messages as read
   - Only marks messages that belong to the requesting user
   - Returns the count of messages updated

### Example API Usage (Unread Messages)

1. **Get Unread Messages**:

   ```http
   GET /api/messages/unread/
   ```

   Response:

   ```json
   {
     "count": 3,
     "next": null,
     "previous": null,
     "results": [
       {
         "message_id": "550e8400-e29b-41d4-a716-446655440000",
         "content": "Hello, this is an unread message",
         "sender": {"id": 1, "username": "user1"},
         "timestamp": "2025-07-30T10:00:00Z",
         "read": false
       }
     ]
   }
   ```

2. **Mark Messages as Read**:

   ```http
   PATCH /api/messages/unread/
   {
     "message_ids": ["550e8400-e29b-41d4-a716-446655440000"]
   }
   ```

   Response:

   ```json
   {
     "status": "Marked 1 message(s) as read"
   }
   ```

### Performance Considerations

- The unread messages query is optimized with:
  - Database index on the `read` field
  - `select_related` to prevent N+1 queries for related objects
  - `only()` to fetch only necessary fields
- The `mark_as_read` operation is atomic and uses a single database query

---

## Account Management

### Account Deletion

Users can delete their accounts, which automatically triggers cleanup of all their data:

1. **What Gets Deleted**:
   - User account
   - All messages sent or received by the user
   - All notifications related to the user
   - All message history entries where the user was the editor

2. **How It Works**:
   - Uses Django's `post_delete` signal for clean data removal
   - Ensures referential integrity with proper cascade deletion
   - Performs cleanup in a transaction to maintain data consistency

3. **Security**:
   - Only authenticated users can delete their own accounts
   - Operation is irreversible
   - Protected against CSRF attacks

---

## Setup

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd Django-signals_orm-0x04
    ```

2. Create and activate virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Run migrations:

    ```bash
    python manage.py migrate
    ```

5. Create superuser (optional):

    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

---

## Testing

Run the test suite with:

```bash
python manage.py test messaging.tests
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Security settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

---

## License

This project is licensed under the ALX ProDEV Curriculum.
