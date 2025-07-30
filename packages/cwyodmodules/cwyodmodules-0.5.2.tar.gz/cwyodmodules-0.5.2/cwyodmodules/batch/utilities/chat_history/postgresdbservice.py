import asyncpg
from datetime import datetime, timezone
from .database_client_base import DatabaseClientBase
from ...utilities.helpers.env_helper import EnvHelper
from mgmt_config import logger, identity
env_helper: EnvHelper = EnvHelper()
log_execution = env_helper.LOG_EXECUTION
log_args = env_helper.LOG_ARGS
log_result = env_helper.LOG_RESULT


class PostgresConversationClient(DatabaseClientBase):

    def __init__(
        self, user: str, host: str, database: str, enable_message_feedback: bool = False
    ):
        self.user = user
        self.host = host
        self.database = database
        self.enable_message_feedback = enable_message_feedback
        self.conn = None

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def connect(self):
        try:
            access_information = identity.get_token(scopes="https://ossrdbms-aad.database.windows.net/.default")
            token = access_information.token
            self.conn = await asyncpg.connect(
                user=self.user,
                host=self.host,
                database=self.database,
                password=token,
                port=5432,
                ssl="require",
            )
            logger.info("Successfully connected to PostgreSQL")
        except Exception as e:
            logger.error("Failed to connect to PostgreSQL: %s", e, exc_info=True)
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def close(self):
        if self.conn:
            await self.conn.close()
            logger.info("PostgreSQL connection closed")

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def ensure(self):
        if not self.conn:
            logger.warning("PostgreSQL client not initialized correctly")
            return False, "PostgreSQL client not initialized correctly"
        logger.info("PostgreSQL client initialized successfully")
        return True, "PostgreSQL client initialized successfully"

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def create_conversation(self, conversation_id, user_id, title=""):
        utc_now = datetime.now(timezone.utc)
        createdAt = utc_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        query = """
            INSERT INTO conversations (id, conversation_id, type, "createdAt", "updatedAt", user_id, title)
            VALUES ($1, $2, 'conversation', $3, $3, $4, $5)
            RETURNING *
        """
        try:
            conversation = await self.conn.fetchrow(
                query, conversation_id, conversation_id, createdAt, user_id, title
            )
            if conversation:
                logger.info(f"Conversation created with id: {conversation_id}")
                return dict(conversation)
            else:
                logger.warning(
                    f"Failed to create conversation with id: {conversation_id}"
                )
                return False
        except Exception as e:
            logger.error(
                f"Error creating conversation with id: {conversation_id}: {e}",
                exc_info=True,
            )
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def upsert_conversation(self, conversation):
        query = """
            INSERT INTO conversations (id, conversation_id, type, "createdAt", "updatedAt", user_id, title)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                "updatedAt" = EXCLUDED."updatedAt",
                title = EXCLUDED.title
            RETURNING *
        """
        try:
            updated_conversation = await self.conn.fetchrow(
                query,
                conversation["id"],
                conversation["conversation_id"],
                conversation["type"],
                conversation["createdAt"],
                conversation["updatedAt"],
                conversation["user_id"],
                conversation["title"],
            )
            if updated_conversation:
                logger.info(f"Conversation upserted with id: {conversation['id']}")
                return dict(updated_conversation)
            else:
                logger.warning(
                    f"Failed to upsert conversation with id: {conversation['id']}"
                )
                return False
        except Exception as e:
            logger.error(
                f"Error upserting conversation with id: {conversation['id']}: {e}",
                exc_info=True,
            )
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def delete_conversation(self, user_id, conversation_id):
        query = (
            "DELETE FROM conversations WHERE conversation_id = $1 AND user_id = $2"
        )
        try:
            await self.conn.execute(query, conversation_id, user_id)
            logger.info(
                f"Conversation deleted with conversation_id: {conversation_id} and user_id: {user_id}"
            )
            return True
        except Exception as e:
            logger.error(
                f"Error deleting conversation with conversation_id: {conversation_id} and user_id: {user_id}: {e}",
                exc_info=True,
            )
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def delete_messages(self, conversation_id, user_id):
        query = "DELETE FROM messages WHERE conversation_id = $1 AND user_id = $2 RETURNING *"
        try:
            messages = await self.conn.fetch(query, conversation_id, user_id)
            logger.info(
                f"Messages deleted for conversation_id: {conversation_id} and user_id: {user_id}"
            )
            return [dict(message) for message in messages]
        except Exception as e:
            logger.error(
                f"Error deleting messages for conversation_id: {conversation_id} and user_id: {user_id}: {e}",
                exc_info=True,
            )
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def get_conversations(self, user_id, limit=None, sort_order="DESC", offset=0):
        try:
            offset = int(offset)  # Ensure offset is an integer
        except ValueError:
            logger.error("Offset must be an integer.", exc_info=True)
            raise ValueError("Offset must be an integer.")
        # Base query without LIMIT and OFFSET
        query = f"""
            SELECT * FROM conversations
            WHERE user_id = $1 AND type = 'conversation'
            ORDER BY "updatedAt" {sort_order}
        """
        # Append LIMIT and OFFSET to the query if limit is specified
        if limit is not None:
            try:
                limit = int(limit)  # Ensure limit is an integer
                query += " LIMIT $2 OFFSET $3"
                # Fetch records with LIMIT and OFFSET
                conversations = await self.conn.fetch(query, user_id, limit, offset)
                logger.info(
                    f"Retrieved conversations for user_id: {user_id} with limit: {limit} and offset: {offset}"
                )
            except ValueError:
                logger.error("Limit must be an integer.", exc_info=True)
                raise ValueError("Limit must be an integer.")
        else:
            # Fetch records without LIMIT and OFFSET
            conversations = await self.conn.fetch(query, user_id)
            logger.info(
                f"Retrieved conversations for user_id: {user_id} without limit and offset"
            )
        return [dict(conversation) for conversation in conversations]

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def get_conversation(self, user_id, conversation_id):
        query = "SELECT * FROM conversations WHERE id = $1 AND user_id = $2 AND type = 'conversation'"
        try:
            conversation = await self.conn.fetchrow(query, conversation_id, user_id)
            if conversation:
                logger.info(
                    f"Retrieved conversation with id: {conversation_id} and user_id: {user_id}"
                )
                return dict(conversation)
            else:
                logger.warning(
                    f"No conversation found with id: {conversation_id} and user_id: {user_id}"
                )
                return None
        except Exception as e:
            logger.error(
                f"Error retrieving conversation with id: {conversation_id} and user_id: {user_id}: {e}",
                exc_info=True,
            )
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def create_message(self, uuid, conversation_id, user_id, input_message: dict):
        message_id = uuid
        utc_now = datetime.now(timezone.utc)
        createdAt = utc_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        query = """
            INSERT INTO messages (id, type, "createdAt", "updatedAt", user_id, conversation_id, role, content, feedback)
            VALUES ($1, 'message', $2, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        feedback = "" if self.enable_message_feedback else None
        try:
            message = await self.conn.fetchrow(
                query,
                message_id,
                createdAt,
                user_id,
                conversation_id,
                input_message["role"],
                input_message["content"],
                feedback,
            )

            if message:
                update_query = 'UPDATE conversations SET "updatedAt" = $1 WHERE id = $2 AND user_id = $3 RETURNING *'
                await self.conn.execute(
                    update_query, createdAt, conversation_id, user_id
                )
                logger.info(
                    f"Message created with id: {message_id} in conversation: {conversation_id}"
                )
                return dict(message)
            else:
                logger.warning(
                    f"Failed to create message with id: {message_id} in conversation: {conversation_id}"
                )
                return False
        except Exception as e:
            logger.error(
                f"Error creating message with id: {message_id} in conversation: {conversation_id}: {e}",
                exc_info=True,
            )
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def update_message_feedback(self, user_id, message_id, feedback):
        query = "UPDATE messages SET feedback = $1 WHERE id = $2 AND user_id = $3 RETURNING *"
        try:
            message = await self.conn.fetchrow(query, feedback, message_id, user_id)
            if message:
                logger.info(
                    f"Message feedback updated for message_id: {message_id} and user_id: {user_id}"
                )
                return dict(message)
            else:
                logger.warning(
                    f"Failed to update message feedback for message_id: {message_id} and user_id: {user_id}"
                )
                return False
        except Exception as e:
            logger.error(
                f"Error updating message feedback for message_id: {message_id} and user_id: {user_id}: {e}",
                exc_info=True,
            )
            raise

    @logger.trace_function(log_execution=log_execution, log_args=log_args, log_result=log_result)
    async def get_messages(self, user_id, conversation_id):
        query = 'SELECT * FROM messages WHERE conversation_id = $1 AND user_id = $2 ORDER BY "createdAt" ASC'
        try:
            messages = await self.conn.fetch(query, conversation_id, user_id)
            logger.info(
                f"Retrieved messages for conversation_id: {conversation_id} and user_id: {user_id}"
            )
            return [dict(message) for message in messages]
        except Exception as e:
            logger.error(
                f"Error retrieving messages for conversation_id: {conversation_id} and user_id: {user_id}: {e}",
                exc_info=True,
            )
            raise
