# CHANGELOG

## v1.5.2

### 2023-03-26 (Sun, Mar 26, 2023)
#### example.tmpl
* add example template file

#### README.md
* add content

#### cl_mail.py
* remove laundry from template checklist if the post indicates it's included

#### Pipfile
* update python version to use

#### Pipfile.lock
* update package versions

## v1.5.1

### 2021-09-21 (Tue, Sep 21, 2021)
#### cl_mail.py:
* fixed an issue with ampersands in the subject not being interpreted correctly

## v1.5.0

### Sun Sep 19 01:51:21 2021 -0400
#### cl_mail.py
* updated some commented debug code to utilize f-string self-documenting expressions
* added code to remove line in template for laundry if the ad indicates that's in the unit or building
* fixed a bug with the code for post removal detection

### Sat Sep 18 22:54:46 2021 -0400
#### cl_mail.py
* added post removal detection, updated code to use an assignment expression when prompting the user, and fixed a variable type hint

### Thu Sep 16 00:44:52 2021 -0400
#### cl_mail.py
* added dynamic availability detection

### Wed Sep 15 23:52:12 2021 -0400
#### cl_mail.py
* removed needless string replacement

### Wed Sep 15 23:37:51 2021 -0400
#### cl_mail.py
* added type hints, reorganized URL encoding, and removed some old comments

### Wed Sep 15 22:18:08 2021 -0400
#### cl_mail.py
* split subject and body retrieval into separate functions

## v1.0.0

### Wed Sep 15 21:31:43 2021 -0400
#### cl_mail.py
* fixed an issue with Chrome removing actual '+' symbols while encoding/decoding the data and removed email validation if the email is blank

### Tue Sep 14 05:52:58 2021 -0400
#### cl_mail.py
* Added Pipfiles and updated `cl_mail.py` to better handle large amounts of data

### Tue Sep 14 00:16:53 2021 -0400
#### cl_mail.py
* fixed a bug in which a non-existent `mapaddress` would cause the whole thing to panic

### Sun Sep 12 05:09:32 2021 -0400
#### cl_mail.py
* Updated to utilize `webbrowser` instead of a direct OS command call

### Sun Sep 12 04:57:09 2021 -0400
#### cl_mail.py
* Split out some code into `grab_content`, added `mapaddress` content to subject, and tidied up some remaining code

### Sun Sep 12 03:23:03 2021 -0400
#### cl_mail.py
* Initial commit

### Sun Sep 12 04:48:07 2021 -0400
#### cl_mail.py
* Initial commit
