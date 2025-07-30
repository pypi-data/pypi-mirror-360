import requests
from datetime import datetime, timezone

class MailerHelper:
    def __init__(self, env, daakiya_url, bundle_uuid, sender_email_id, recipient_emails):
        self.env = env
        self.daakiya_url = daakiya_url
        self.bundle_uuid = bundle_uuid
        self.sender_email_id = sender_email_id
        self.recipient_emails = recipient_emails

    def send_email(self, bucket_name, object_key, subject, body):
        try:
            url = self.daakiya_url
            headers = {"Content-Type": "application/json"}
            payload = {
                "event_type": "publish_event",
                "bundle": {
                    "bundle_type": "direct_bundle",
                    "bundle_uuid": self.bundle_uuid,
                    "request_ts": int(datetime.now(timezone.utc).timestamp() * 1000),
                    "mail_packet": {
                        "packet_type": "solo_packet",
                        "sender_mail_id": self.sender_email_id,
                        "receivers_mail_id_info": {
                            "to": self.recipient_emails,
                            "cc": [],
                            "bcc": []
                        },
                        "subject": subject,
                        "body": {
                            "body_type": "file_attachment_body",
                            "content": {
                                "content_type": "html",
                                "html_content": body
                            }
                        }
                    }
                }
            }

            if bucket_name and object_key:
                payload["bundle"]["mail_packet"]["body"]["attachments"] = [
                    {
                        "location": {
                            "storage_provider": "GCS",
                            "bucket": bucket_name,
                            "key": object_key
                        }
                    }
                ]

            response = requests.post(url, headers=headers, json=payload)

            if not response.ok:
                print(f"Error response from server: {response.text}")

            response.raise_for_status()
            print(f"Email sent successfully: {response.text}")

        except requests.exceptions.RequestException as req_error:
            print(f"Failed to send email: {req_error}")
            print(f"Response content: {req_error.response.text if hasattr(req_error, 'response') else 'No response content'}")
            raise RuntimeError(f"Error sending email: {req_error}")

    def get_missing_mappings_subject(self, env, business_unit, period):
        return f"{business_unit} {env} NetSuite Pipeline Failure Notification - {period}"

    def get_failure_subject(self, env, business_unit):
        return f"{env.capitalize()} {business_unit} Pipeline Failed"

    def get_revenue_report_subject(self, business_unit, posting_period_val):
        return f"Monthly {business_unit} Report - {posting_period_val}"

    def get_missing_mappings_body(self, missing_mappings, period):
        body = f"""\
        <html>
          <body style="font-family: Roboto, sans-serif; color: #333;">
            <table width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr>
                <td style="padding: 20px;">
                  <p>Dear Team,</p>

                  <p>We have identified missing mappings in the system for the specified posting period <strong>{period}</strong>. 
                  Kindly review the details below:</p>

                  <table width="100%" cellpadding="10" cellspacing="0" border="1" style="border-collapse: collapse; margin: 20px 0;">
                    <tr style="background-color: #f2f2f2;">
                      <th align="left">Field</th>
                      <th align="left">Missing Value</th>
                    </tr>"""

        for field, values in missing_mappings.items():
            for value in values:
                body += f"""\
                    <tr>
                      <td>{field}</td>
                      <td>{value}</td>
                    </tr>"""

        body += f"""\
                  </table>

                  <p><strong>Action Required:</strong> Please update the missing fields at the earliest. 
                  Once done, notify us to manually rerun the workflow for <strong>{period}</strong>.</p>

                  <p>For any assistance or queries, feel free to reach out to the Revenue Assurance Team.</p>

                  <p>Thank you for your prompt attention.</p>

                  <p>Best regards,<br/>
                  <strong>Revenue Assurance Team</strong></p>
                </td>
              </tr>
            </table>
          </body>
        </html>
        """
        return body

    def get_failure_body(self, error_message, business_unit):
        return f"""<html>
        <body>
            <p>An error occurred while executing the {business_unit} Pipeline:</p>
            <pre>{error_message}</pre>
            <p>Please check logs for more information.</p>
        </body>
    </html>"""
 
    def get_revenue_report_body(self, env, business_unit, period):
        env_context = "NetSuite Production" if env.lower() == "production" else "NetSuite Sandbox"
        return f"""<html>
        <body>
           <p>Dear Team,</p>
           <p>The revenue data for the {business_unit} business unit for the month of <strong>{period}</strong> has been successfully processed and uploaded to {env_context}.</p>
           <p>Best regards,<br>Revenue Assurance Team</p>
        </body>
    </html>"""

    def get_success_subject(self, env, business_unit, period):
        return f"{business_unit} {env} NetSuite Pipeline Success Notification - {period}"

    def get_success_body(self, env, business_unit, period):
        env_context = "NetSuite Production" if env.lower() == "production" else "NetSuite Sandbox"
        return f"""<html>
        <body>
            <p>Dear Team,</p>
            <p>The revenue data for the {business_unit} business unit for the month of <strong>{period}</strong> has been successfully processed and uploaded to {env_context}.</p>
            <p>Best regards,<br>Revenue Assurance Team</p>
        </body>
        </html>"""
