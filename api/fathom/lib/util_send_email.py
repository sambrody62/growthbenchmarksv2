from postmarker.core import PostmarkClient # pylint: disable=import-error
from flask import current_app

def send_email(email, subject, html_body):
    postmark = PostmarkClient(server_token=current_app.config['POSTMARK_SERVER_API_TOKEN'])
    postmark.emails.send(
        From='mike@ladder.io',
        To=email,
        Subject=subject,
        HtmlBody=html_body
    )
    return {"success": f"Email sent to {email}"}