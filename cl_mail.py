#!/usr/bin/env python3

import requests
import urllib.parse
import validators
import sys
import subprocess
import re
from os import path
from bs4 import BeautifulSoup


def grab_content(arg):
    """
    Grabs the HTML content
    Args:
        arg: the user-provided argument on the command line

    Returns:
    email:
    subject:
    body:
    """
    if validators.url(arg) is True:
        # argument is a URL
        # download CL listing

        try:
            response = requests.get(arg)
        except response.raise_for_status() as e:
            print(e)

        contents = BeautifulSoup(response.text, 'html.parser')
    elif path.isfile(arg):
        with open(arg, 'r') as file:
            contents = BeautifulSoup(file.read(), 'html.parser')
    #    print(ET.tostring(ET.parse(arg).getroot(), encoding='utf-8', method='xml'))
    #    listing_content = xmltojson.parse(ET.tostring(ET.parse(response.data).getroot(), encoding='utf-8', method='xml'))
    else:
        print(f"error: {arg} is not a valid URL or file")
        sys.exit(1)

    # remove an unwanted div in the posting body
    contents.find("div", {"class": "print-information print-qrcode-container"}).extract()

    subject = re.sub('<[^>]+>', '', contents.find("span", {"class": "postingtitletext"}).text.strip())
    subject = subject.join([s for s in subject.splitlines() if s])
    print(f"subject = '{subject}'")
    body = re.sub('<[^>]+>', '', contents.find(id="postingbody").text.strip())
    print(f"body = '{body}'")
#        print(contents.find("span", {"class": "price"}).string, contents.find(id="postingbody").text)
    email = "test@example.com"

    if not validators.email(email):
        print(f"error: '{email}' is not a valid email address")
        sys.exit(1)

    return email, subject, body


def generate_mailto(email, subject, body):
    """
    Generates the `mailto` line
    Args:
        email ():
        subject ():
        body ():

    Returns:

    """
    arg = sys.argv[1]
    
#    try:
#        validators.url(arg)
#        url = arg
#    except ValidationFailure as e:
#        print(e)
#        sys.exit(1)

    # generate email body using the template
    with open("cl_template.tmpl", 'r') as template:
        body = f"{template.read()}{body}"
#    print(ET.tostring(ET.fromstring(response.data).getroot(), encoding='utf-8', method='xml'))
#    print(listing_content)
#
#
#    subject = f"{listing_subject} ({listing_neighborhood}) ({listing_crosstreets})"
#
#    link = f"mailto:{email}?subject={subject}&body={body}"
    params = urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    mailto = f"mailto:{email}?{params}"

    return mailto


def open_browser(mailto):
    """
    Opens the browser with the generated `mailto` value
    Args:
        mailto ():
    """
    print(f"google-chrome-stable {mailto}")
    #subprocess.Popen(['google-chrome-stable', mailto],
    #                           stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE
    #                           )
#    stdout, stderr = process.communicate()


if __name__ == "__main__":
    email, subject, body = grab_content(sys.argv[1])
    open_browser(generate_mailto(email, subject, body))
