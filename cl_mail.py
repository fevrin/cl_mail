#!/usr/bin/env python3

import requests
import urllib.parse
import validators
import sys
import subprocess
import re
import os
from bs4 import BeautifulSoup
import webbrowser
from typing import Optional, Tuple
from datetime import datetime


def grab_content(arg: str) -> Tuple[str, Optional[str]]:
    """
    Grabs the HTML content from a URL
    Args:
        arg: The user-provided URL argument

    Returns:
        A tuple containing the URL (if provided) and the parsed BeautifulSoup object.
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
    """
    Returns the body within the passed HTML content.
    Args:
        contents: The BeautifulSoup object representing the HTML content.

    Returns:
        The extracted subject text with leading/trailing whitespace removed.
    """
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
    """
    Returns the body within the passed contents
    Args:
        contents (): the posting's contents

    Returns:
        body: the body of the post
    """
    # get the body text
    body: str = re.sub('<[^>]+>', '', contents.find(id="postingbody").text.strip())

    laundry_regex = re.compile('(^\[ *\] - Laundry|(w/d|laundry) in (unit|bldg))')
    name = os.environ.get('NAME', '${NAME}')
    email = os.environ.get('EMAIL', '${EMAIL}')

    # get any attributes
    attributes = list()
    for paragraph in contents.find_all("div", {"class": "attrgroup"}):
        for attr in paragraph.find_all("span", class_=["valu", "attr important"]):
            data_date = attr.get('data-date')
            if data_date and datetime.today() >= datetime.strptime(data_date, '%Y-%m-%d'):
#                print(f"{attr.get('data-date') = }")
#                print(f"{attr.get('data-today_msg') = }")
                attributes.append(attr.get('data-today_msg'))
            else:
                attributes.append(attr.text.strip())

    HAS_LAUNDRY: int = 0
    for attr in attributes:
        if laundry_regex.match(attr):
            HAS_LAUNDRY = 1

    body = re.sub('\n\n\n+', '\n', body)

    # generate email body using the template
    lines: str = ""
    with open("cl_template.tmpl", 'r') as template:
        for line in template:
            # don't include the laundry checkbox if the listing mentions the laundry_regex
            if not HAS_LAUNDRY == 1 or not laundry_regex.match(line):
                lines += line \
                    .replace('${NAME}', name) \
                    .replace('${EMAIL}', email)
        if lines:
            body = f"{lines}\n{body}"

    if attributes:
        print("adding attributes")
        body += "\n\n"
        for attr in attributes:
            body += f"* {attr}\n"

    return body


def generate_mailto(arg: str) -> Tuple[str, Optional[str]]:
    """
    Generates the `mailto` line
    Args:
        arg: either a file name or a URL

    Returns:
        A tuple containing the generated mailto link and the URL.
    """
    MAX_HTTP_LENGTH = 5597  # 8163
    MAX_MAILTO_LENGTH = 2048
    contents, url = grab_content(arg)

    # detect if the listing shows it's been removed
    if msg := contents.find("div", {"class": "removed"}):
        print(msg.text.strip())
        sys.exit(1)

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
        {"subject": urllib.parse.quote(subject), "body": body},
        safe='/'
    ) \
       .replace('&', '%26') \
       .replace('%2B', '%252B')

#    print(f"{urllib.parse.quote(body) = }")
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

    while True:
        if re.match('^y$', user_input := input("ready to continue? [y/N] ")):
            break


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

    #webbrowser.open(mailto, new=0)
    #subprocess.Popen(['sensible-browser', mailto],
    #                           stdout=subprocess.PIPE,
    #                           stderr=subprocess.PIPE
    #                 )
#    stdout, stderr = process.communicate()


if __name__ == "__main__":
    open_browser(generate_mailto(sys.argv[1]))
