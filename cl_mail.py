#!/usr/bin/env python3

import requests
import urllib.parse
import validators
import sys
import subprocess
import re
from os import path
from bs4 import BeautifulSoup
import webbrowser


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
    url = str()
    if validators.url(arg) is True:
        # argument is a URL
        # download CL listing

        try:
            response = requests.get(arg)
            url = arg
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

    return contents, url


def generate_mailto(arg):
    """
    Generates the `mailto` line
    Args:
        email ():
        subject ():
        body ():

    Returns:

    """
    contents, url = grab_content(arg)

    # remove an unwanted div in the posting body
    contents.find("div", {"class": "print-information print-qrcode-container"}).extract()

    # get the subject text
    subject = re.sub('<[^>]+>', '', contents.find("span", {"class": "postingtitletext"}).text.strip())
    mapaddress = contents.find("div", {"class": "mapaddress"})
    if mapaddress is not None:
        subject += f" ({mapaddress.text})"

    # remove empty lines
    subject = subject.join([s for s in subject.splitlines() if s])
    print(f"subject = '{subject}'")

    # get the body text
    body = re.sub('<[^>]+>', '', contents.find(id="postingbody").text.strip())
    print(f"body = '{body}'")

    # get any attributes
    attributes = list()
    for paragraph in contents.find_all("p", {"class": "attrgroup"}):
        for attr in paragraph.find_all("span"):
            attributes.append(attr.text)

    email = "test@example.com"

    if not validators.email(email):
        print(f"error: '{email}' is not a valid email address")
        sys.exit(1)

    # generate email body using the template
    with open("cl_template.tmpl", 'r') as template:
        body = f"{template.read()}\n{body}"

    if attributes:
        print()
        body += "\n\n"
        for attr in attributes:
            print(f"* {attr}")
            body += f"* {attr}\n"

    if url:
        body += f"\n{url}"
    else:
        # make the email a reminder to include the URL
        email = f"don't forget to add the URL!"
#    print(ET.tostring(ET.fromstring(response.data).getroot(), encoding='utf-8', method='xml'))
#    print(listing_content)
#
#
#    subject = f"{listing_subject} ({listing_neighborhood}) ({listing_crosstreets})"
#
#    link = f"mailto:{email}?subject={subject}&body={body}"
    params = urllib.parse.urlencode({"subject": subject, "body": body}, quote_via=urllib.parse.quote)
    mailto = f"mailto:{email}?{params}"

    return mailto, url


def open_browser(link):
    """
    Opens the browser with the generated `mailto` value
    Args:
        mailto: the `mailto` string
        url: the URL of the listing
    """
    mailto, url = link
    print(f"google-chrome-stable {mailto}")
    if not url:
        print("\ndon't forget to add the URL to the bottom")
        user_input = input("ready to continue? [y/N] ")
        while not re.match('^y$', user_input):
            user_input = input("ready to continue? [y/N] ")

    webbrowser.open(mailto, new=0)
    #subprocess.Popen(['sensible-browser', mailto],
    #                           stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE
    #                 )
#    stdout, stderr = process.communicate()


if __name__ == "__main__":
    open_browser(generate_mailto(sys.argv[1]))
