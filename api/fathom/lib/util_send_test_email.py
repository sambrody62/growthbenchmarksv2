from postmarker.core import PostmarkClient # pylint: disable=import-error
from flask import current_app

def send_test_email(email):
    postmark = PostmarkClient(server_token=current_app.config['POSTMARK_SERVER_API_TOKEN'])
    postmark.emails.send(
        From='mike@ladder.io',
        To=email,
        Subject='Anomaly: CPC for Ladder is up by 10%',
        HtmlBody='<html><body><strong>CPC is up by 10%</strong> so I suggest you fix it.</body></html>'
    )
    return {"success": f"Email sent to {email}"}