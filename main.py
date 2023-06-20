from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def form():
    return render_template('form.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    from_name = request.form.get('name')
    email_message = request.form.get('email_message')
    industry = request.form.get('industry')
    subject = request.form.get('subject')

    email_list_file = request.files['email_list']

    signature_path = f"signatures/{from_name}.jpg"
    with open(signature_path, "rb") as signature_file:
        signature_data = signature_file.read()

    email_list = pd.read_csv(email_list_file)

    sender_email = 'socials@macarto.ai'  # You might want to make this configurable
    sender_password = 'vluesrrrnccubnpl'  # Ditto

    if not email_list.empty:
        for index, recipient in email_list.iterrows():
            to_name = recipient['Name']  # Make sure the 'name' column exists in your CSV
            send_emails([recipient['Email']], subject, sender_email, sender_password, to_name, from_name, signature_data, email_message)
        return jsonify({'message': 'Emails sent successfully'})
    else:
        return jsonify({'message': 'No emails found or an error occurred while reading the file.'})


def send_emails(email_list, subject, sender_email, sender_password, to_name, from_name, image_data, email_message):
    try:
        smtp_host = 'smtp.gmail.com'
        smtp_port = 587

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            for email in email_list:
                msg = MIMEMultipart()
                msg['Subject'] = subject
                msg['From'] = sender_email
                msg['To'] = email

                # Create the HTML message with embedded image
                html_message = """
                <html>
                <body>
                    <p>Hi {to_name},</p>
                    <p>{email_message}</p>
                    <p>Best Regards!</p>
                    <p>{from_name}</p>
                    <img src="cid:myimage">
                </body>
                </html>
                """.format(to_name=to_name, from_name=from_name, email_message=email_message)
                html = MIMEText(html_message, 'html')
                msg.attach(html)

                # Attach the image with the appropriate content type and encoding
                image = MIMEImage(image_data, name='signature.jpg')
                image.add_header('Content-ID', '<myimage>')
                image.add_header('Content-Disposition', 'inline', filename='signature.jpg')
                msg.attach(image)

                # Send the email
                server.sendmail(sender_email, email, msg.as_string())
                print(f"Email sent successfully to {email}")
    except smtplib.SMTPAuthenticationError:
        print("Failed to authenticate. Please check the sender's email and password.")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
