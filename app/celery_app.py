from celery import Celery

app = Celery('celery_app', broker="sqs://KEY:SECRET@")

@app.task
def process_sqs_message(message):
    # Add your message processing logic here
    print("Received message body:", message)
