#!/usr/bin/env python

# this file will parse the emails out

from bs4 import *
import mailbox
import re

# For readability when accessing lists
SOCIAL_INDEX    = 0
SHOPPING_INDEX  = 1
SPAM_INDEX      = 2
OTHER_INDEX     = 3

stop_words = set()
doc_count = 0
term_freq = {}

def get_charsets(msg):
    charsets = set({})
    for c in msg.get_charsets():
        if c is not None:
            charsets.update([c])
    return charsets


def handle_error(errmsg, emailmsg,cs):
    print("")
    print(errmsg)
    print("This error occurred while decoding with ",cs," charset.")
    print("These charsets were found in the one email.",get_charsets(emailmsg))
    print("This is the subject:",emailmsg['subject'])
    print("This is the sender:",emailmsg['From'])


def get_text_only(soup):
    """ Remove all tags, return a list of words (one word per line)
    from the text content of a BeautifulSoup object. """

    v = soup.string     # try to get string between open and close tags
    if v==None:         # if None, then recursively do the same for each child
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
    #words = [s.lower() for s in words]
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
    #Walk through the parts of the email to find the text body.    
    if msg.is_multipart():    
        for part in msg.walk():

            # If part is multipart, walk through the subparts.            
            if part.is_multipart(): 

                for subpart in part.walk():
                    if subpart.get_content_type() == 'text/plain':
                        # Get the subpart payload (i.e the message body)
                        body = subpart.get_payload(decode=True) 
                        #charset = subpart.get_charset()

            # Part isn't multipart so get the email body
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
                #charset = part.get_charset()

    # If this isn't a multi-part message then get the payload (i.e the message body)
    elif msg.get_content_type() == 'text/plain':
        body = msg.get_payload(decode=True) 

    # No checking done to match the charset with the correct part. 
    for charset in get_charsets(msg):
        try:
            if (body is not None):
                body = body.decode(charset)
            else:
                body = ""
        except UnicodeDecodeError as e:
            print("HANDLING ERROR:")
            print(e)
            handle_error("UnicodeDecodeError: encountered.",msg,charset)
        except AttributeError as e:
            print("HANDLING ERROR:")
            print(e)
            handle_error("AttributeError: encountered" ,msg,charset)
    return body    
#END get_email_text()


def show_mbox(mboxPath):
    box = mailbox.mbox(mboxPath)
    for msg in box:
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

        print(email_text)   # debugging

        print("")
        print('**********************************')
        print("")
#END show_mbox()



def parse_emails():
    """ Parse all the emails we have in each file (these are hard-coded),
    given a category for each one. """

    # Read in stop_words from a file into the stop_words set
    stop_txt_file = open("data/stopwords.list", "r")
    for line in stop_txt_file:
        stop_words.add(line.strip().lower())
    stop_txt_file.close() # We don't need this anymore


    show_mbox('data/Shopping1.mbox')

if __name__ == '__main__':
    parse_emails()
