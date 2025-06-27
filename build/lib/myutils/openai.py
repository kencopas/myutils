import openai
from myutils.logging import gotenv, path_log
import time


class EasyGPT:

    def __init__(self, assistant_id: str = None) -> None:
        try:

            # Save the assistant id
            self.assistant_id = assistant_id if assistant_id else gotenv('ASSISTANT_ID')

            # Create thread
            self.thread = openai.beta.threads.create()

        except Exception as err:
            path_log('Failed to initialize thread', err)

    def create(self, message: str) -> None:
        try:

            # Add a message to the thread
            openai.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message
            )

            # Run the assistant
            run = openai.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant_id
            )

        except Exception as err:
            path_log('Filed to create message:', err)
            return

        # Wait for the run to complete (if incomplete)
        while True:
            run_status = openai.beta.threads.runs.retrieve(
                run.id,
                thread_id=self.thread.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled"]:
                raise Exception(f"Run failed with status: {run_status.status}")
            time.sleep(1)

    def retrieve(self) -> str:

        # Retrieve messages from the thread
        messages = openai.beta.threads.messages.list(thread_id=self.thread.id)

        # Find and print the assistant's latest message
        for message in reversed(messages.data):  # messages are returned in reverse chronological order
            if message.role == "assistant":
                return message.content[0].text.value
