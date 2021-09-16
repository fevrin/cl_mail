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
from typing import Tuple, Optional


def grab_content(arg) -> Tuple[str, Optional[str]]:
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


def get_subject(contents: str) -> str:
    # get the subject text
    subject = re.sub('<[^>]+>', '', contents.find("span", {"class": "postingtitletext"}).text.strip())
    mapaddress = contents.find("div", {"class": "mapaddress"})
    if mapaddress is not None:
        subject += f" ({mapaddress.text})"

    # remove empty lines
    subject = subject.join([s for s in subject.splitlines() if s])
    print(f"subject = '{subject}'")

    return subject


def get_body(contents: str) -> str:
    # get the body text
    body = re.sub('<[^>]+>', '', contents.find(id="postingbody").text.strip())

    # get any attributes
    attributes = list()
    for paragraph in contents.find_all("p", {"class": "attrgroup"}):
        for attr in paragraph.find_all("span"):
            attributes.append(attr.text)

    body = re.sub('\n\n\n+', '\n', body)

    # generate email body using the template
    with open("cl_template.tmpl", 'r') as template:
        body = f"{template.read()}\n{body}"

    if attributes:
        print("adding attributes")
        body += "\n\n"
        for attr in attributes:
            body += f"* {attr}\n"

    return body


def generate_mailto(arg: str) -> Tuple[str, str]:
    """
    Generates the `mailto` line
    Args:
        arg: either a file name or a URL

    Returns:

    """
    MAX_HTTP_LENGTH = 5597  # 8163
    MAX_MAILTO_LENGTH = 2048
    contents, url = grab_content(arg)

    # remove an unwanted div in the posting body
    contents.find("div", {"class": "print-information print-qrcode-container"}).extract()

    subject: str = get_subject(contents)
    body: str = get_body(contents)
    email: str = ""

    if url:
        body += f"\n{url}"
    else:
        # make the email a reminder to include the URL
        email = f"test@dont forget to add the URL.com"

    print(f"body = '{body}'")

    # remove whitespace in the email address so it validates properly
    email = "".join(email.split())
    if email and not validators.email(email):
        print(f"error: '{email}' is not a valid email address")
        sys.exit(1)

    # HTML encode the URL
    # lots of jank to appease Chrome
    params = urllib.parse.urlencode(
        {"subject": subject, "body": body},
        safe='/'
    ) \
        .replace('&', '%26') \
        .replace('%2B', '%252B') \
        .replace(' ', '+')

#    print(f"body = {urllib.parse.quote(body)}")
    mailto = f"{email}?{params}"

    mailto_len = len(mailto)
    if mailto_len <= MAX_MAILTO_LENGTH:
        mailto = f"mailto:{mailto}"
    elif mailto_len > MAX_MAILTO_LENGTH:
        if mailto_len > MAX_HTTP_LENGTH:
           ask_to_continue(f"URL is too long and will get cut off ({mailto_len} chars)")

        mailto = f"https://mail.google.com/mail/?extsrc=mailto&url=mailto:{email}%3F{params}"
        print(f"length after: {len(mailto)}")

        mailto_validation = validators.url(mailto)

        if mailto_validation is not True:
            print(mailto_validation)
            sys.exit(1)

    print(f"URL is {mailto_len} chars")
    return mailto, url


def ask_to_continue(prompt: str):
    print(prompt)
    user_input = input("ready to continue? [y/N] ")
    while not re.match('^y$', user_input):
        user_input = input("ready to continue? [y/N] ")


def open_browser(link):
    """
    Opens the browser with the generated `mailto` value
    Args:
        link: the `mailto` string and URL (if any)
    """
    mailto, url = link
    print(f"google-chrome-stable {mailto}")
    if not url:
        ask_to_continue("don't forget to add the URL to the bottom")

    webbrowser.open(mailto, new=0)
    #subprocess.Popen(['sensible-browser', mailto],
    #                           stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE
    #                 )
#    stdout, stderr = process.communicate()


if __name__ == "__main__":
    open_browser(generate_mailto(sys.argv[1]))
