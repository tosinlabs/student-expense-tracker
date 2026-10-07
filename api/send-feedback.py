from http.server import BaseHTTPRequestHandler
import json
import os
import resend


class handler(BaseHTTPRequestHandler):

    def do_POST(self):

        try:
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            data = json.loads(body)

            rating = data.get("rating", "")
            feedback_type = data.get("feedback_type", "")
            title = data.get("title", "")
            feedback = data.get("feedback", "")
            name = data.get("name", "")
            email = data.get("email", "")
            app_version = data.get("app_version", "2.0.0")

            resend.api_key = os.environ["RESEND_API_KEY"]

            params = {
                "from": "onboarding@resend.dev",
                "to": [os.environ["FEEDBACK_EMAIL"]],
                "subject": f"Student Expense Tracker Feedback: {title}",
                "html": f"""
                    <h2>New Feedback</h2>

                    <p><strong>Rating:</strong> {rating}/5</p>

                    <p><strong>Type:</strong> {feedback_type}</p>

                    <p><strong>Title:</strong> {title}</p>

                    <p><strong>Feedback:</strong></p>
                    <p>{feedback}</p>

                    <hr>

                    <p><strong>Name:</strong> {name or "Not provided"}</p>
                    <p><strong>Email:</strong> {email or "Not provided"}</p>
                    <p><strong>App Version:</strong> {app_version}</p>
                """
            }

            resend.Emails.send(params)

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "success": True
                }).encode()
            )

        except Exception as error:

            self.send_response(500)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.end_headers()

            self.wfile.write(
                json.dumps({
                    "success": False,
                    "error": str(error)
                }).encode()
            )