# Abstract Message  

## Usage:

```python
from message_local.Message import Message, Importance

# SpecialMessage for example SMSMessage, WhatsApp Message, EmailMessage
class SpecialMessage(Message):
    def __init__(self, body: str, importance: Importance, subject: str = None) -> None:
        super().__init__(body, importance, subject)  # now you got self.body, self.importance and self.subject (optional)

    def send(self, recipients: list, cc: list = None):  # cc and bcc are optional
        logger.info("Message sent to " + " ".join(recipients))

    def was_read(self):
        return True

    def display(self):
        logger.info("Message displayed")
        
    def _can_send(self) -> bool:
        """Implement this with API management https://github.com/circles-zone/api-management-local-python-package"""
        pass

    def _after_send_attempt(self) -> None:
        """Update the DB if sent successfully, or with the problem details"""
        pass

  ```

Same RDS MySQL permissions/credential as message-local you only should add label_message to find which messages are in
Outbox for the Outbox Message Queue Worker - TODO We should split the credentials.<br>
