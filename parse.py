#!/usr/bin/env python

# this file will parse the emails out

from bs4 import *
from os import listdir
import mailbox
import re
import unicodedata

debug_mode = False # Set to true when running this module by itself

# For readability when accessing lists
SOCIAL_INDEX    = 0
SHOPPING_INDEX  = 1
SPAM_INDEX      = 2
OTHER_INDEX     = 3

# Files to parse
MBOX_FILES = []

# Which content types we should attempt to parse meaningful text out of
acceptable_content_types = ('text/plain', 'text/html')

# Dictionary returned from parse_emails, providing useful information
# used in later steps in the program (classifiers, etc.)
data_from_parsing = \
{
  'vocabSize' : 0, \
  'classCount' : [0,0,0,0], \
  'docCount' : 0, \
  'termCounts' : {}, \
  'emails' : [] \
}

# List of stop_words to be stripped from the email content
stop_words = set()


def get_charsets(msg):
    charsets = set({})
    for c in msg.get_charsets():
        if c is not None:
            charsets.update([c])
    return charsets
#END get_charsets()


def handle_error(errmsg, emailmsg,cs):
    if debug_mode:
        print("")
        print(errmsg)
        print("This error occurred while decoding with ",cs," charset.")
        print("These charsets were found in the one email.",get_charsets(emailmsg))
        print("This is the subject:",emailmsg['subject'])
        print("This is the sender:",emailmsg['From'])
#END handle_error()


def get_text_only(soup):
    """ Remove all tags, return a list of words (one word per line)
    from the text content of a BeautifulSoup object. """

    v = soup.string     # try to get string between open and close tags
    if v == None:         # if None, then recursively do the same for each child
        c = soup.contents
        resulttext = ''
        for tag in c:
            # Skip over Comments and Doctype elements
            if type(tag) != None and \
               (tag.__class__.__name__ == 'Comment' \
                or tag.__class__.__name__ == 'Doctype'):
                continue
            subtext = ''
            # If t has attribute "alt", try to get the alt text out of it,
            # then append the call below to that
            if tag.name == 'img' and tag.has_attr('alt'):
                subtext = tag.get('alt')
            # Get all the text for this tag (and child tags, recursively)
            subtext += get_text_only(tag)
            resulttext += subtext + '\n'
        return resulttext
    else:
        return v.strip()    # remove whitespace from front and back of v
#END get_text_only()


def separate_words(text):
    """Separate the terms in a given string by the regex '\\W*',
    make sure the meet the criteria described below, and return
    them in a list object.
    Criteria for a term to be valid:
    * length of the term must be > 1 character
    * terms cannot start with a numeric character (0-9)
    * term cannot be in the set "stop_words"  """

    output = []
    # Matches any non-alphanumeric character, 0 or more
    # Control characters (like \n, \r, etc.) don't need to have the
    # backslash escaped; however, special characters (\W, \A, etc.)
    # need to be read in the string as "\W", "\A", etc., so to get
    # the literal backslash, you'll need to escape it.
    splitterRE = re.compile('\\W*')
    words = splitterRE.split(text)  # split text by occurrences of the RE
    # convert list entries to lower case (via list comprehension format)
    #words = [s.lower() for s in words] # ERR: sometimes throws an exception
    for s in words:
        try:
            s = str(s.lower())
        except:
            pass;
        if not(len(s) < 2          # Eliminate 0- and 1-char entries \
               or (s[0] >= '0' and s[0] <= '9') # if first char is numeric \
               or s in stop_words):   # if s is a stop word
            output.append(s)
            #print("Appending word \"%s\" to list" % s) # debug
        # debug
        #else:
        #    print("Omitted word: %s" % s)
    return output
#END separate_words()


def get_email_text(msg):
    body = None
    # Search through all parts of the email to find relevant text 
    if msg.is_multipart():
        for part in msg.walk():
            # Check each part of the message for text (if there are several)
            if part.is_multipart():
                for subpart in part.walk():
                    if subpart.get_content_type() in acceptable_content_types:
                        # Get the subpart payload (i.e the message body)
                        body = subpart.get_payload(decode=True)
                        #charset = subpart.get_charset()
            elif part.get_content_type() in acceptable_content_types:
                body = part.get_payload(decode=True) 
 
    elif msg.get_content_type() in acceptable_content_types:
        body = msg.get_payload(decode=True)

    if body is None:
        body = ""
    else:
        # Try different encodings listed in the Content-Type header until you
        # find the right one that will decode the email text
        for charset in get_charsets(msg):
            try:
                body = body.decode(charset)
                break
            except UnicodeEncodeError as e:
                handle_error("UnicodeEncodeError!",msg,charset)
            except UnicodeDecodeError as e:
                handle_error("UnicodeDecodeError!",msg,charset)
            except AttributeError as e:
                handle_error("AttributeError!" ,msg,charset)

    if msg['subject'] is None:
        return body
    else:
        return msg['subject'] + " " + body
#END get_email_text()


def parse_emails():
    """ Parse all the emails we have in each file (these are hard-coded),
    given a category for each one. """

    global data_from_parsing

    # Add all mbox files (and their corresponding category) to MBOX_FILES
    categories = [("data/categories/other/", OTHER_INDEX), \
                  ("data/categories/shopping/", SHOPPING_INDEX), \
                  ("data/categories/social/", SOCIAL_INDEX), \
                  ("data/categories/spam/", SPAM_INDEX)]
    for dirpath, category in categories:
        for filename in listdir(dirpath):
            MBOX_FILES.append((dirpath + filename, category))

    # Read in stop_words from a file into the stop_words set
    stop_txt_file = open("data/stopwords.list", "r")
    for line in stop_txt_file:
        stop_words.add(line.strip().lower())
    stop_txt_file.close() # We don't need this anymore

    # Read in each mbox file
    for mbox_file_path, category in MBOX_FILES:
        box = mailbox.mbox(mbox_file_path)
        for msg in box:
            data_from_parsing['docCount'] += 1
            data_from_parsing['classCount'][category] += 1

            # Extract email text and enclose it in html tags so that
            # BeautifulSoup will be able to parse it and extract the text
            email_text = "<html><body>" + get_email_text(msg) + "</body></html>"

            # Parse and remove garbage
            soup = BeautifulSoup(email_text)
            [s.extract() for s in soup('script')] # Remove 'script' elements
            [s.extract() for s in soup('style')]  # Remove 'style' elements

            # Get text from the cleaned up XML
            email_text = get_text_only(soup)
            email_text = separate_words(email_text)

            # Keep track of the number of unique terms
            for term in email_text:
                if term not in data_from_parsing['termCounts']:
                    data_from_parsing['termCounts'][term] = [ [0,0], [0,0], [0,0], [0,0] ]

            data_from_parsing['emails'].append( \
                { \
                    'terms' : email_text, \
                    'truthCategory' : category, \
                    'bernoulliCategory' : -1,
                    'multinomialCategory' : -1 \
                } \
            )
    
    data_from_parsing['vocabSize'] = len(data_from_parsing['termCounts'])

    if debug_mode == True:
        print("*** Raw email term lists: ")
        for item in data_from_parsing['emails']:
            print(item['terms'])
            print("")

        print("\n*** Terms found: ")
        for key in sorted(data_from_parsing['termCounts']):
            print(key)

        print("\n*** Number of terms found (vocabSize): " + str(data_from_parsing['vocabSize']))

        print("\n*** Doc count: " + str(data_from_parsing['docCount']))

        print("\n*** Class count: ")
        for c in data_from_parsing['classCount']:
            print c

    return data_from_parsing
#END parse_emails()

if __name__ == '__main__':
    debug_mode = True
    parse_emails()
