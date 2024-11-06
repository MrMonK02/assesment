from flask import Flask, request, jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Contact, LinkPrecedence

app = Flask(_name_)

# Database setup (example with SQLite)
engine = create_engine("sqlite:///contacts.db")
Session = sessionmaker(bind=engine)
session = Session()

@app.route("/identify", methods=["POST"])
def identify():
    data = request.json
    email = data.get("email")
    phone_number = data.get("phoneNumber")

    # Query to find matching contacts by email or phone number
    matching_contacts = session.query(Contact).filter(
        (Contact.email == email) | (Contact.phoneNumber == phone_number)
    ).all()

    if not matching_contacts:
        # No matches: create a new primary contact
        new_contact = Contact(email=email, phoneNumber=phone_number, linkPrecedence=LinkPrecedence.PRIMARY)
        session.add(new_contact)
        session.commit()

        response = {
            "primaryContactId": new_contact.id,
            "emails": [new_contact.email],
            "phoneNumbers": [new_contact.phoneNumber],
            "secondaryContactIds": []
        }
    else:
        # Process matching contacts
        primary_contact = None
        secondary_contact_ids = []
        emails = set()
        phone_numbers = set()

        for contact in matching_contacts:
            if contact.linkPrecedence == LinkPrecedence.PRIMARY:
                primary_contact = contact
            else:
                secondary_contact_ids.append(contact.id)
            if contact.email:
                emails.add(contact.email)
            if contact.phoneNumber:
                phone_numbers.add(contact.phoneNumber)

        # Update primary if needed, or create secondary link
        if primary_contact:
            if email and email not in emails:
                primary_contact.email = email
            if phone_number and phone_number not in phone_numbers:
                primary_contact.phoneNumber = phone_number
            session.commit()

            response = {
                "primaryContactId": primary_contact.id,
                "emails": list(emails),
                "phoneNumbers": list(phone_numbers),
                "secondaryContactIds": secondary_contact_ids
            }
        else:
            # Handle case where a new primary needs to be created
            pass  # additional handling as per requirements

    return jsonify(response), 200

if _name_ == "_main_":
    app.run(debug=True)