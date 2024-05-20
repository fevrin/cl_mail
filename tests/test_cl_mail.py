import pytest
from cl_mail import grab_content, get_subject, get_body, generate_mailto, requests
from bs4 import BeautifulSoup
import os

def test_grab_content_url():
  """Tests grabbing content from a valid URL."""
  url = "https://www.example.com/craigslist-listing"
  contents, _ = grab_content(url)
  assert isinstance(contents, BeautifulSoup)

def test_grab_content_file(tmp_path):
  """Tests grabbing content from a valid file."""
  # Create a temporary test file with sample HTML content
  tmp_file = os.path.join(tmp_path, "test_file.html")
  with open(tmp_file, "w") as f:
    f.write("<html><body><h1>Test content</h1></body></html>")
  contents, _ = grab_content("test_file.html")
  assert isinstance(contents, BeautifulSoup)

def test_grab_content_invalid_argument():
  """Tests handling of invalid arguments (not URL or file)."""
  with pytest.raises(SystemExit):
    grab_content("invalid_argument")

def test_get_subject_empty():
  """Tests subject extraction from empty content."""
  contents = BeautifulSoup("<html></html>", "html.parser")
  subject = get_subject(str(contents))
  assert subject == ""

def test_get_subject_with_text():
  """Tests subject extraction with text and address."""
  contents = BeautifulSoup(
      """<html><body>
      <span class="postingtitletext">Craigslist Listing Title</span>
      <div class="mapaddress">123 Main St, New York, NY</div>
      </body></html>""",
      "html.parser",
  )
  subject = get_subject(str(contents))
  assert subject == "Craigslist Listing Title (123 Main St, New York, NY)"

def test_get_body_empty():
  """Tests body extraction from empty content."""
  contents = BeautifulSoup("<html></html>", "html.parser")
  body = get_body(str(contents))
  assert body == ""

def test_get_body_with_text():
  """Tests body extraction with sample text."""
  contents = BeautifulSoup(
      """<html><body>
      <div id="postingbody">This is the body of the craigslist listing.</div>
      </body></html>""",
      "html.parser",
  )
  body = get_body(str(contents))
  assert body.startswith("This is the body of the craigslist listing.")

def test_get_body_with_laundry(tmp_path):
  """Tests body handling with laundry attribute in template."""
  # Mock the template file content
  tmp_file = os.path.join(tmp_path, "temp_template.tmpl")
  with open(tmp_file, "w") as f:
    f.write("[ ] - laundry in unit\nSome other line")
  contents = BeautifulSoup(
      """<html><body>
      <div id="postingbody">This is the body of the craigslist listing.</div>
      <p class="attrgroup"><span>laundry in bldg</span></p>
      </body></html>""",
      "html.parser",
  )
  body = get_body(str(contents))
  assert "laundry in bldg" not in body

def test_generate_mailto_url():
  """Tests mailto generation with a valid URL."""
  url = "https://www.example.com/craigslist-listing"
  mailto, url_out = generate_mailto(url)
  assert mailto.startswith("mailto:")
  assert url_out == url

@pytest.mark.usefixtures("mocker")
def test_generate_mailto_file(mocker, tmp_path):
  """Tests mailto generation with a valid file (mocking requests)."""
  # Mock the requests library to avoid real network calls during test
  tmp_file = os.path.join(tmp_path, "test_file.html")
  mocker.patch("cl_mail.requests.get")
  with open(tmp_file, "w") as f:
    f.write("<html><body></body></html>")
  mailto, url_out = generate_mailto("test_file.html")
  assert mailto.startswith("mailto:")
  assert url_out is None


def test_generate_mailto_invalid_argument():
  """Tests handling of invalid arguments (not URL or file)."""
  with pytest.raises(SystemExit):
    generate_mailto("invalid_argument")
