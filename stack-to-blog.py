#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#
#       stack-to-blog.py - Convert Stack Exchange Answers with a score >= 2 or
#           accepted into a Jekyll blog post.
#
#       Oct. 24 2021 - Initial version.
#       Nov. 06 2021 - Two passes to count number of #, ##, etc. in first pass.
#       Nov. 13 2021 - Add TOC support and SE "<!-- language" conversion.
#       Nov. 17 2021 - Support for Pseudo-tags from keywords in answers.
#       Nov. 24 2021 - Check self-answered questions and not accepted yet.
#       Dec. 04 2021 - Copy fenced code block to clipboard.
#
# ==============================================================================

"""
    USAGE
    ============================================================================

    Using your Stack Exchange UserID (EG mine is: 4775729), run the
        Stack Exchange Data Explorer query:
        "https://data.stackexchange.com/stackoverflow/query/1505559/
        all-my-posts-on-the-se-network-with-markdown-and-html-content-
        plus-editors-and-s"

    A copy of the query has been saved in pippim.github.io/StackBlogPost. A
    copy of the output file QueryResults.csv can also be found in the same
    root directory.

    Run the query and Save the results in CSV format as QueryResults.csv

    Move query results to your website folder. In Linux use:
        mv ~/Downloads/QueryResults.csv ~/website

    Run ~/website/stack-to-blog.py which will populate "~/website/_posts"
    sub-directory with one Jekyll blog post file for each Stack Exchange
    post that qualifies.

    Each post file begins with:

        ---
        layout: post
        title:  What is the question in Stack Exchange?
        ---

"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens
from datetime import datetime as dt
# Above for error: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# AttributeError: 'module' object has no attribute 'now'
# Credit: https://stackoverflow.com/a/32463688/6929343
import csv
from random import randint

INPUT_FILE = 'QueryResults.csv'
RANDOM_LIMIT = 10000        # On initial trials limit the number of blog posts
PRINT_RANDOM = False        # Print out matching random record found (10 lines)
OUTPUT_DIR = "_posts/"      # Subdirectory name. Use "" for current directory
QUESTIONS_QUALIFIER = True  # Convert questions to blog posts
VOTE_QUALIFIER = 2          # Posts need at least 2 votes to qualify
ACCEPTED_QUALIFIER = True   # All accepted answers are uploaded
# Don't confuse above with row 'ACCEPTED' index or the flag 'FRONT_ACCEPTED'

''' Table of Contents (TOC) options. '''
# If TOC is never wanted, set to None
CONTENTS = "{% include toc.md %}"
TOC_HDR_MIN = 6             # Number of Headers required to qualify TOC insert
TOC_WORD_MIN = 1000         # Minimum 1,000 words for TOC
TOC_LOC = 2                 # Insert TOC as 2nd header (Don't go below 2!)

NAV_BAR_OPT = 4             # Insert Navigation Bar into markdown?
''' 0 = No navigation bar
    1 = single line. EG <a id=... </div>
    2 = two lines. EG <a id= then new line then with <div>...</div>
    3 = Option 2 plus empty (blank) line above for readability
    4 = Option 3 plus empty (blank) line above for even more readability
    5 = Option 4 plus comment for ultimate readability

    Note: Markdown compresses all blank lines into a single blank line between
          paragraphs. HTML code inserted simply counts as another blank line to
          be compressed into a single blank line.
'''
NAV_BAR_LEVEL = 2           # Only for "#" or "##". Not for "###", "####", etc.
NAV_FORCE_TOC = True        # Put TOC to navigation bar regardless of "#"
NAV_BAR_MIN = 3             # Minimum number of # & ## headers required
NAV_WORD_MIN = 1000         # Minimum 1,000 words for navigation button bar

''' Copy code block contents to clipboard options. '''
# If Copy button is never wanted, set to None
COPY_TO_CLIPBOARD = "{% include copyHeader.html %}"
COPY_LINE_MIN = 20          # Number of lines required to qualify for button

""" TODO: 

https://talk.jekyllrb.com/t/plugin-for-show-more-code-block/4149/2

<details>
<summary>
Preview
</summary>

{% highlight ruby %}
puts 'Expanded message'
{% endhighlight %}

</details>

"""

# If question or answer contains one of these "pseudo tags" then jekyll front
# will have tag added as if it were really on the question. Essentially you
# are tagging your answers and adding them to OP's question tags.
PSEUDO_TAGS = ["conky", "eyesome", "cpuf", "iconic", "multi-timer"]

fields = []                 # The column names used by Stack Exchanges
data = []                   # Returned rows, less record #1 (field names)
row_count = 0               # How many data rows (Answers / Blog posts)
random_row_nos = []         # Random row numbers exported during trail runs
all_tag_names = []          # Every tag name appearing on stack exchange answers
all_tag_counts = []         # Count of times tag has been used on SE answers

now = dt.now().strftime("%Y-%m-%d %H:%M:%S")

# Copy terminal output of record #1 with column names and paste below.
# Then change names to uppercase and assign each column a 0-based index.
SITE = 0
POST_ID = 1
URL = 2
LINK = 3
TYPE = 4
TITLE = 5
HTML = 6
MARKDOWN = 7
TAGS = 8
CREATED = 9
LAST_EDIT = 10
EDITED_BY = 11
SCORE = 12
FAVORITES = 13
VIEWS = 14
ANSWERS = 15
ACCEPTED = 16
CW = 17
CLOSED = 18

''' Custom Front Matter for Jekyll blog posts

Typical front matter contains:
    ---
    layout: post
    title: How do I make XYZ work in ABC?
    ---

If you change "FRONT_URL = None" below to: "FRONT_URL = stack_url" you get:

    ---
    layout: default
    title: How do I make XYZ work in ABC?
    stack_url: https://askubuntu.com/questions/1039357/
    ---

This allows a button that links to the original Stack Exchange answer 

'''

FRONT_SITE      = "site:         "  # EG "site:         Ask Ubuntu"
FRONT_POST_ID   = None              # EG "post_id:      1104017"
FRONT_URL       = "stack_url:    "  # EG "stack_url:    https://askubuntu.com/q/1104017"
                                    # If selected you MUST select FRONT_SITE & FRONT_TYPE too
FRONT_LINK      = None              # EG "post_link:    https://askubuntu.com/q/1104017|How can I
                                    # send mobile text message from terminal?"
FRONT_TYPE      = "type:         "  # EG "type:         Question"
FRONT_TITLE     = "title:        "  # Always appears in front matter!
FRONT_HTML      = None              # This will NEVER be put into front matter
FRONT_MARKDOWN  = None              # This will NEVER be put into front matter
FRONT_TAGS      = "tags:         "  # EG "tags:         command-line bash sms
FRONT_CREATED   = "created_date: "  # EG "created_date: 2020-01-15 15:21:55"
FRONT_LAST_EDIT = "edit_date:    "  # EG "edit_date:    2020-05-27 17:27:45"
FRONT_EDITED_BY = None              # EG "edit_user:    Community (-1)"
FRONT_SCORE     = "votes:        "  # EG "votes:        64" or blank/nil
FRONT_FAVORITES = "favorites:    "  # EG "favorites:    33" or blank/nil
FRONT_VIEWS     = "views:        "  # EG "views:        72,056" or blank/nil
FRONT_ANSWERS   = None              # EG "answers:      3" or blank/nil
FRONT_ACCEPTED  = "accepted:     "  # EG "accepted:     Accepted" or blank/nil
FRONT_CW        = None              # EG "community:    CW" blank/nil
FRONT_CLOSED    = None              # EG "closed:       Closed" or blank/nil

# Extra front matter generated by `stack-to-blog.py` actions:
FRONT_LAYOUT    = "layout:       post"  # "layout:" MUST be used "post" can be changed
FRONT_UPLOADED  = "uploaded:     "  # Date & Time this program was run
FRONT_TOC       = "toc:          "  # Table of Contents? "true" or "false"
FRONT_NAV_BAR   = "navigation:   "  # Section navigation bar? "true" or "false"
# Variables below aren't necessary because Liquid has variables
# See: https://stackoverflow.com/a/53251634/6929343
FRONT_LINES     = None  # Number of lines and number of paragraphs are the same thing!
FRONT_PARAGRAPHS = None
FRONT_WORDS     = None
FRONT_READ_TIME = None              # Reading Time = Number of words / 250

'''
Totals for all Stack Exchange posts even those not converted
'''
row_number = 1                  # Current row number in query
accepted_count = 0              # How many posts were accepted
question_count = 0              # How many posts are questions
answer_count = 0                # How many posts are answers
unknown_count = 0               # How many posts are unknown, EG wiki-tags
most_lines = 0                  # Lines in the longest post
qualifying_blog_count = 0       # How many blogs could be saved
save_blog_count = 0             # How many blogs were saved given random limit

total_views = 0                 # Number of times viewed
total_votes = 0                 # How many up votes across all posts
total_lines = 0                 # Total lines of all posts
total_header_spaces = 0         # Total headers we added a space behind lsat "#"
total_headers = 0               # Total header count
total_quote_spaces = 0          # Total block quotes requiring two spaces at end
total_paragraphs = 0            # How many paragraphs are there?
total_words = 0                 # How many words by splitting whitespace
total_pseudo_tags = 0           # Words in answer that qualify as tags for question
total_tag_names = []            # All the tags added for all the posts
total_code_blocks = 0           # How many code blocks are there?
total_code_block_lines = 0      # How many lines are inside code blocks?
total_pre_codes = 0             # How many times does <pre><code> appear?
total_header_levels = [0, 0, 0, 0, 0, 0]
total_alternate_h1 = 0          # Alternate H1 lines followed by "=="
total_alternate_h2 = 0          # Alternate H2 lines followed by "--"
total_force_end = 0             # How many last empty lines added?
total_toc = 0                   # How many table of contents added?
total_nav_bar = 0               # How many navigation bars added?
total_self_answer = 0           # How many self-answered questions?
total_self_accept = 0           # Of those how many have been accepted?
self_not_accept_url = []        # List of URLs not accepted
language_forced = 0             # How many times was language fenced?

'''
Totals for single blog post - reinitialized between blog posts
'''
contents = ""               # Not used, placeholder
blog_filename = ""          # YYYY-MM-DD-blog-title.md
lines = []                  # Markdown lines list being processed
curr_index = 0              # Current line index within lines []
header_count = 0            # How many headers were found in blog post
header_space_count = 0      # How many header spaces had to be added after #?
alternate_h1 = 0            # Alternate H1 lines followed by "=="
alternate_h2 = 0            # Alternate H2 lines followed by "--"
''' Counts of header levels - H1, H2 ... H6 '''
header_levels = [0, 0, 0, 0, 0, 0]
paragraph_count = 0         # How many paragraphs in post last one not counted
word_count = 0              # How many words by splitting whitespace
pseudo_tag_count = 0        # Words in answer that qualify as tags for question
pseudo_tag_names = []       # All tag names added for this post
self_answer = False         # Is this a self-answered question?
self_accept = False         # Is this self-answered question accepted?

in_code_block = False       # Are we in a code block? Then no # Header formatting
old_in_code_block = False
code_block_index = 0
code_block_line_count = 0
language_used = ""          # What language when fenced code blocks have none?
image_links = []            # Links to images found at bottom of SE posts
''' Used for each post '''
tags = ""                   # Front matter format: tags: TAG1 TAG2 TAG3

''' Functions
    ====================================================================
    
    Functions must be defined prior to being called.  The following
    functions are defined:

    dump(r)
    header_space(ln)
    block_quote(ln) 
    check_paragraph(ln) 
    check_code_block(ln) 
    check_copy_clipboard(curr_index)
    check_pre_code(ln) - NOT USED!
    check_contents(ln) - NOT USED!
    navigation_bar(level, skip_btn=True)  
    front_matter(r)
    create_blog_filename()
    check_self_answer(r)
    write_md(md)
    fatal_error(msg)

'''


def dump(r):
    """ Dump contents of one row to terminal in good-looking format
    """
    print('Site:   ', r[SITE], '  |  Post ID:', r[POST_ID], '  |  Type:', r[TYPE])
    print('Title:  ', r[TITLE][:80])
    print('URL:    ', r[URL][:80])
    print('blog:   ', blog_filename)

    limit = r[HTML].find('\n')      # Limit HTML to first line or 80 chars
    if limit > 80 or limit == -1:
        limit = 80
    print('HTML:   ', r[HTML][:limit])

    limit = r[MARKDOWN].find('\n')  # Limit MD to first line or 80 chars
    if limit > 80 or limit == -1:
        limit = 80
    print('MARK_DN:', r[MARKDOWN][:limit])
    print('Created:', r[CREATED], ' |  Edited: ', r[LAST_EDIT],
          ' |  Edited by:', r[EDITED_BY])  # Compensate for time having extra space
    print('Tags In:', r[TAGS], '  |  Tags Out:', tags)
    print('pseudo_tag_count:', pseudo_tag_count,
          '  |  total_pseudo_tags:', total_pseudo_tags)
    print('Votes:  ', r[SCORE], '  |  Views:', r[VIEWS], '  |  Answers:', r[ANSWERS],
          '  |  Accepted:', r[ACCEPTED])
    print('header_count:', header_count, '  |  paragraph_count:', paragraph_count,
          '  |  word_count:', word_count)
    print('Alternate H1:', alternate_h1, '  |  Alternate H2:', alternate_h2,
          '  |  6 Header level counts', header_levels, '\n')


def header_space(ln):
    """ Add space after # for headers if necessary

        Count the number of headers to header_count and header_levels

        If inside fenced code block, ignore # lines and don't count as header.

        Convert alternate H1 and H2 ('==', '--' line follows) to # and ##.
            This will simply things during second pass when navigation bar
            buttons need to be inserted.

    """
    global header_count, header_space_count
    global lines, curr_index, header_levels
    global alternate_h1, alternate_h2

    if in_code_block:
        return ln

    if ln[0:1] == "#":
        #print('Found header:', ln)
        header_count += 1   # For current post, reset between posts
        # How many '#' are there at line start?
        hash_count = len(ln) - len(ln.lstrip('#'))
        # Is first character after "#" a space?
        if ln[hash_count:hash_count+1] != " ":
            #print('Forcing space at:', hash_count, ln)
            ln = ln[0:hash_count] + " " + ln[hash_count:]
            header_space_count += 1
            #print('After forcing:   ', hash_count, ln)

        # Increment count at level
        header_levels[hash_count - 1] += 1

    elif curr_index == line_count - 1:
        pass  # Don't go past size of list

    # If current line is empty or starts with < (HTML) skip alternate test
    elif ln == "" or ln[0:1] == "<":
        pass

    elif lines[curr_index + 1][0:1] == "=":
        ''' This is an H1 Line because next line is "=="
        '''
        header_count += 1   # For current post, reset between posts
        alternate_h1 += 1
        ln = "# " + ln
        lines[curr_index + 1] = ""  # Blank out "=="
        # Increment count at level
        header_levels[0] += 1

    elif lines[curr_index + 1][0:2] == "--":
        ''' This is an H2 Line because next line is "--"
            NOTE: Kramdown requires two "--" and a single one won't do.
        '''
        #print(ln)  # Uncomment this and next 2 lines to test alternate H2
        #print(lines[curr_index + 1])
        #print(row[URL])

        header_count += 1   # For current post, reset between posts
        alternate_h2 += 1
        ln = "## " + ln
        lines[curr_index + 1] = ""  # Blank out "--"
        # Increment count at level
        header_levels[1] += 1

    # Append HTML header ID. EG: <a> id="hdr9"></a>
    ''' Move this to second pass
    if hash_count <= TOC_HDR_LEVEL:
        ln = ln + '<a id="hdr' + str(header_count) + '"></a>'
        # Second pass will insert lines to GOTO this "id" name
    '''
    return ln


def block_quote(ln):
    """ Append two spaces at end of block quote ('>') if necessary

        If inside fenced code block, ignore # lines and don't count as header.

    """
    global total_quote_spaces

    if in_code_block:
        return ln

    if ln[0:1] == ">":
        #print('Found block quote:', ln)
        if ln[-2:] != "  ":
            #print('Forcing two spaces after:', ln)
            ln = ln + "  "
            total_quote_spaces += 1
    return ln


def check_paragraph(ln):
    """ If line is empty it means it's a paragraph.  Note if line ends in
        two spaces it forces a new line but not a paragraph break.  Also
        note if three lines were written in a row they would be merged
        into one paragraph.

        FUTURE?: The paragraph number indicates where to insert TOC.

        Count number of words. Check if word qualifies as a pseudo
        tag.

    """
    global total_paragraphs, paragraph_count, total_words, word_count
    global pseudo_tag_count, total_pseudo_tags, pseudo_tag_names, total_tag_names

    if len(ln) == 0:
        total_paragraphs += 1   # For all posts
        paragraph_count += 1    # For current post

    ''' Add to word counts '''
    word_list = ln.split()
    count = len(word_list)
    word_count += count
    total_words += count

    ''' Add to pseudo-tags '''
    for pseudo in PSEUDO_TAGS:
        search = pseudo.lower()
        for word in word_list:
            if search == word.lower():
                pseudo_tag_count += 1
                total_pseudo_tags += 1
                if search not in pseudo_tag_names:
                    if search not in tags:
                        # All tag names added for this post
                        pseudo_tag_names.append(search)
                if search not in total_tag_names:
                    if search not in tags:
                        # All the tags added for all the posts
                        total_tag_names.append(search)


def check_code_block(ln):
    """ If line starts with ``` we are now in code block.

        If already in code block and line begins with ```
            then we are now out of code block.

        Set default syntax language when none on code block. SE standard:
            <!-- language: bash -->
            <!-- language-all: lang-bash -->

    """
    global in_code_block, total_code_blocks, language_used, language_forced

    ''' Code blocks may be indented so left strip spaces before test
    
        To end code block you must use ``` in Kramdown. Stack Exchange lets
        you end code block with "``` some-text" but that breaks Kramdown.
        
        TODO: count number of backticks that initiate a code block.
              For example ```` (4) can start a code block then if ``` (3)
              appears it doesn't terminate code block but is interpreted
              literally as backticks. EG
              
              This is an example of using fenced code backticks:
              
              ````
              ``` html
              <element code>Stuff stuff stuff</element code>
              ```
              ```` 
    '''
    if ln.startswith("<!-- language"):
        # Get "bash" inside of <!-- language-all: lang-bash -->
        # Store as language_used for inside of code block.
        language_used = ln.split(": ")[1]
        # Strip off " -->" at end of string
        language_used = language_used[:-4]
        if language_used.startswith("lang-"):
            # Strip off "lang-" at start of string
            language_used = language_used[5:]
        if language_used == "none":
            # "none" is best set as "text" for universal recognition
            language_used = "text"

        #print('language_used:', language_used, 'length:', len(language_used))
        return ""  # Former "<!-- language" line is now an empty line

    if ln.lstrip()[0:3] == "```":
        # Add language if not used already
        if in_code_block is False:
            total_code_blocks += 1      # Total for all posts
            in_code_block = True        # Code block has begun
            if ln[-1] == "`" or ln[-1] == " ":
                ln = ln + " " + language_used
                language_forced += 1
        else:
            in_code_block = False       # Code block has ended
            # Remove extra text after ``` whilst maintaining indenting
            # NOTE: This breaks '````' coding (4 backticks)
            before = ln
            ln = ln.split('```')[0] + '```'
            if before.strip() != ln.strip():
                print(curr_index, 'of', len(lines) - 1, blog_filename)
                print('OLD ln:', before)
                print('NEW ln:', ln)
                print('       ', lines[curr_index+1])

    return ln


def check_copy_clipboard(this_index):
    """ Check to insert copy to clipboard include.

        If already in code block and line begins with ```
            then we are now out of code block.

        Set default syntax language when none on code block. SE standard:
            <!-- language: bash -->
            <!-- language-all: lang-bash -->

    """
    global total_code_block_lines, old_in_code_block, code_block_index
    global code_block_line_count, lines, line_count, curr_index

    inserted_command = ""
    if in_code_block is True:
        total_code_block_lines += 1
        if old_in_code_block is False:
            # Set index for start of code block
            code_block_index = this_index
            # print('Start code block:', lines[this_index])
    elif old_in_code_block is True:
        # Just ended code block how many lines?
        code_block_line_count = this_index - code_block_index
        # Sanity check, lines[index] must contain fenced code block ```
        code = lines[code_block_index]
        if code.lstrip()[0:3] != "```":
            dump(row)
            fatal_error('lines at index: ' + str(this_index) +
                        ' should contain ``` but it is: ' + code)

        # print('  End code block:', lines[this_index])
        if code[0:3] == "```":
            # Copy to clipboard only supported when fenced code
            # block is NOT indented
            if COPY_TO_CLIPBOARD is not None and \
               code_block_line_count >= COPY_LINE_MIN:
                # line_count += 1
                # curr_index += 1  # Not sure this is needed...
                # print()
                # print('BEFORE:', lines[code_block_index])
                inserted_command = COPY_TO_CLIPBOARD
                # print('AFTER :', lines[code_block_index])
                # print('       ', lines[code_block_index+1])
                # print('CLIP:', blog_filename)
        else:
            # If lines[index] fenced code block ``` isn't left justified.
            # Probably within list item and copy to clipboard doesn't work.
            print('Unable to decipher code block:', code)

    old_in_code_block = in_code_block
    return inserted_command


def check_pre_code(ln):
    """ Check if line starts with <pre><code> or <code>
    """
    global total_pre_codes
    if ln.startswith("<pre><code>") or ln.startswith("<code>"):
        ''' NOT SUPPORTED. Print line to terminal '''
        print('===========:', ln)
        total_pre_codes += 1


def check_contents(ln):
    """ check if TOC should be inserted here

    CREDIT: https://www.aleksandrhovhannisyan.com/blog/
            jekyll-table-of-contents/#how-to-create-a-table-of-contents-in-jekyll

    For TOC to work you need to create an include file named
    '_includes/toc.md" and fill it with this markup:

## Table of Contents
{:.no_toc}

* TOC
{:toc}

    Then, in your post, all you have to do is insert this one-liner wherever
    you want your table of contents to appear:

{% include toc.md %}

    So, here's the Sass that'll get the job done by creating the file
    '_sass/someSassFile.scss':

.screen-reader-only {
    position: absolute;
    left: -5000px;

    &:focus {
        left: 0;
    }
}

    """

    global contents, total_quote_spaces
    if CONTENTS is None:
        return  # Global CONTENTS variable is null, so no TOC

    return ln


def navigation_bar(level, skip_btn=True):
    """ Return Navigation Bar. Verbosity driven by NAV_BAR_OPT

        The first header doesn't contain "Top" or "ToS" because it is already
        at the top.

        The TOC header doesn't contain option for "ToC" because it is already
        there.

    """
    bar = ""  # Create new navigation bar

    if NAV_BAR_OPT >= 3:
        bar = bar + "\n"  # Empty line before navigation bar

    bar = bar + '<a id="hdr' + str(level) + '"></a>'
    if NAV_BAR_OPT >= 2:
        bar = bar + "\n"    # ID tag on separate line

    # Calculate jump points
    hdr_ToS = level - 1
    hdr_Skip = level + 1
    bar = bar + '<div class="hdr-bar">'
    # If first Navigation Bar then no Top or Tos
    if level != 1:
        bar = bar + '  <a href="#" class ="hdr-btn">Top</a>'
        bar = bar + '  <a href="#hdr' + str(hdr_ToS) + '" class ="hdr-btn">ToS</a>'

    # TOC button only appears when active and if this isn't the TOC header itself.
    if insert_toc and level != TOC_LOC:
        bar = bar + '  <a href="#hdr' + str(TOC_LOC) + '" class ="hdr-btn">ToC</a>'

    # Skip button will always appear except on footer
    if skip_btn:
        bar = bar + '  <a href="#hdr' + str(hdr_Skip) + '" class ="hdr-btn">Skip</a>'

    bar = bar + '</div>\n'

    if NAV_BAR_OPT >= 4:
        bar = bar + "\n"

    return bar


def front_matter(r):
    """ Output Jekyll front matter to md string """
    md = "---\n" + FRONT_LAYOUT + "\n"
    md = md + FRONT_TITLE + r[TITLE] + '\n'
    if FRONT_SITE is not None:
        md = md + FRONT_SITE + r[SITE] + '\n'
    if FRONT_URL is not None:
        md = md + FRONT_URL + r[URL] + '\n'
        ''' NOTE: When FRONT_URL is used then FRONT_SITE and FRONT_TYPE must
            also be used because "_layouts/post.html" contains:
              {% if page.stack_url and page.stack_url != "" and page.stack_url != nil %}
                <h2 class="project-tagline"><a href="{{ page.stack_url }}"
                       >🔍 See Original {{ page.type }} on {{ page.site }}</a>
                </h2>
              {% endif %}
        '''
    if FRONT_POST_ID is not None:
        md = md + FRONT_POST_ID + r[POST_ID] + '\n'
    if FRONT_LINK is not None:
        md = md + FRONT_LINK + r[LINK] + '\n'
    if FRONT_TYPE is not None:
        md = md + FRONT_TYPE + r[TYPE] + '\n'

    if FRONT_TAGS is not None:
        md = md + FRONT_TAGS + tags + '\n'

    if FRONT_CREATED is not None:
        md = md + FRONT_CREATED + r[CREATED] + '\n'
    if FRONT_LAST_EDIT is not None:
        md = md + FRONT_LAST_EDIT + r[LAST_EDIT] + '\n'
    if FRONT_EDITED_BY is not None:
        md = md + FRONT_EDITED_BY + r[EDITED_BY] + '\n'
    if FRONT_SCORE is not None:
        if r[SCORE] == "":
            md = md + FRONT_SCORE + r[SCORE] + '\n'
        else:
            md = md + FRONT_SCORE + '{:,}'.format(int(r[SCORE])) + '\n'
    if FRONT_FAVORITES is not None:
        if r[FAVORITES] == "":
            md = md + FRONT_FAVORITES + r[FAVORITES] + '\n'
        else:
            md = md + FRONT_FAVORITES + '{:,}'.format(int(r[FAVORITES])) + '\n'
    if FRONT_VIEWS is not None:
        if r[VIEWS] == "":
            md = md + FRONT_VIEWS + r[VIEWS] + '\n'
        else:
            md = md + FRONT_VIEWS + '{:,}'.format(int(r[VIEWS])) + '\n'
    if FRONT_ANSWERS is not None:
        md = md + FRONT_ANSWERS + r[ANSWERS] + '\n'
    if FRONT_ACCEPTED is not None:
        md = md + FRONT_ACCEPTED + r[ACCEPTED] + '\n'
    if FRONT_CW is not None:
        md = md + FRONT_CW + r[CW] + '\n'
    if FRONT_CLOSED is not None:
        md = md + FRONT_CLOSED + r[CW] + '\n'

    # Extra front matter generated by `stack-to-blog.py` actions:
    md = md + FRONT_UPLOADED + now + '\n'
    if insert_toc is True:
        jekyll_boolean = "true"
    else:
        jekyll_boolean = "false"
    md = md + FRONT_TOC  + jekyll_boolean + '\n'
    if insert_nav_bar is True:
        jekyll_boolean = "true"
    else:
        jekyll_boolean = "false"
    md = md + FRONT_NAV_BAR + jekyll_boolean + '\n'

    md = md + "---\n\n"

    return md


def create_blog_filename():
    """ Return blog filename.
        Replace all spaces in title with "-"
        Replace all forward slash (/) with ∕ DIVISION SLASH U+2215
    """
    filename = '_posts/' + row[CREATED].split()[0] + '-' + \
        row[TITLE].replace(' ', '-').replace('/', '∕') + '.md'

    return filename


def check_self_answer(r):
    """ Called for every question.

        If same title exists in an answer this is a self-answered question.

        When self-answered question we skip blogging the question and the
        answer is blogged assuming it reaches the required minimum vote. If
        the answer is accepted (and it should be) it still needs the minimum
        votes.

        An error dump is printed if the question is self-answered but not
        accepted. This happens when answer was forgotten after the 2 day
        waiting period to accept answers had expired.

    """

    global self_answer, self_accept, total_self_answer, total_self_accept
    for search in data:
        if search[TITLE] == r[TITLE] and search[TYPE] == "Answer":
            self_answer = True  # Is this a self-answered question?
            total_self_answer += 1
            # print('SELF_ANSWERED')
            if search[ACCEPTED] == "Accepted":
                self_accept = True  # Is this self-answered question accepted?
                total_self_accept += 1
                # dump(r)
                # dump(search)
            else:
                # print('NOT ACCEPTED')
                self_not_accept_url.append(search[URL])
                # dump(r)
                # dump(search)


def write_md(md):
    """ Write to SE converted to Jekyll markdown to blog_filename """
    with open(blog_filename, 'w') as fh:
        if force_end_line:
            # Write everything except last character ('\n`)
            fh.write(md[:-1])
        else:
            # Write everything
            fh.write(md)


def fatal_error(msg):
    """ Print fatal error and exit program """
    print('#' * 80)
    print('#', ' ' * 31, "FATAL ERROR", ' ' * 32, '#')
    print('#' * 80)
    print()
    print(msg)
    exit()


''' INITIALIZATION
    =======================================================================

    - Sanity Check on front matter
    - Read S.E.D.E. CSV file and convert to Python list: data []
    - Ensure file is not empty
    - Set Random Record Limit list 
'''

# Bailout if incompatible front matter picked
if not FRONT_LAYOUT.startswith('layout:'):
    fatal_error('FRONT_LAYOUT does not begin with "layout:". CONTENT IS: '
                + FRONT_LAYOUT)
if FRONT_URL is not None:
    # FRONT_SITE and FRONT_TYPE required by: _includes/page.html
    if FRONT_SITE is None:
        fatal_error('When FRONT_URL is used then FRONT_SITE is required.')
    if FRONT_TYPE is None:
        fatal_error('When FRONT_URL is used then FRONT_TYPE is required.')

# Read CSV file into list
with open(INPUT_FILE) as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:
        # The first row are column headings / field names
        if row_count == 0:
            print('Column names\n', row)
            fields = row
        else:
            data.append(row)
        row_count += 1

    #print('Total rows:', row_count)

# If less than 2 records consider an empty file
row_count = len(data)
if row_count < 2:
    fatal_error('No CSV records found in INPUT_FILE:' + INPUT_FILE)

# Number of blog posts converted controlled by RANDOM_LIMIT
random_row_nos = [randint(1, row_count) for p in range(0, RANDOM_LIMIT)]
if RANDOM_LIMIT < 100:
    print('RANDOM_LIMIT:', RANDOM_LIMIT,
          'Random record numbers to convert:', random_row_nos)


''' MAIN LOOP to process All query records
    ======================================

    - Match criteria for answer up votes or accepted check mark
    - Check if in fenced code block (``` bash) for example. If not then:
        - Reformat '#Header 1' to '# Header 1'. Same for "##H2" to "## H2", etc.
        - Count number of '#' header lines
        - Count number of lines, paragraphs and number of words.
        - Tally counts at header levels [H1, H2, H3, H4, H5 and H6]
        - Add two spaces after "< Block Quote" lines

    - Second pass to insert '{% include toc.md %}' at paragraph # (TOC_LOC)
    - Anytime a TOC is inserted, following header_index []
        entries and bump index number up by 1
    - Insert Navigation Bar Buttons: 
        HTML anchors for #hdr1, #hdr2. etc. Then apply "<a href" links for:
        Top, ToS, ToC and, Skip (Top of Page, Top of Section, Table of
        Contents and, Skip section).  
    - If RANDOM_LIMIT is used then only output matching random_rec_nos []
'''

for row in data:

    row_number += 1
    ''' Reset counters for each stack exchange Q&A '''
    save_blog = True        # Default until a condition turns it off
    lines = []              # Markdown lines list being processed
    curr_index = 0          # Current line index within lines []
    header_count = 0        # How many headers were found in blog post
    header_space_count = 0  # How many spaces had to be added after #?
    ''' Counts of header levels - H1, H2 ... H6 '''
    header_levels = [0, 0, 0, 0, 0, 0]
    paragraph_count = 0     # How many paragraphs (headers count as 2) in post
    word_count = 0          # How many words (includes "## ") in post
    pseudo_tag_count = 0    # Words in answer that qualify as tags for question
    pseudo_tag_names = []   # Reset pseudo tag names from last post
    language_used = ""      # What language when fenced code blocks have none?
    in_code_block = False   # In a code block # Header formatting is skipped
    old_in_code_block = False
    code_block_index = 0
    code_block_line_count = 0
    force_end_line = False  # Did Pass #1 force an empty blank line at end?
    self_answer = False     # Is this a self-answered question?
    self_accept = False     # Is this self-answered question accepted?

    ''' YYYY-MM-DD-Title-with-spaces-converted-to-dashes.md '''
    blog_filename = create_blog_filename()

    ''' SCORE = (Up Votes - Down Votes) in string format'''
    if row[SCORE] != '':
        score = int(row[SCORE])
    else:
        score = 0
    total_votes += score    # score is up-votes - down-votes can be negative
    if score < VOTE_QUALIFIER:
        save_blog = False   # Below up-vote requirement

    ''' VIEWS '''
    if row[VIEWS] != '':
        views = int(row[VIEWS])
    else:
        views = 0
    total_views += views    # score is up-votes - down-votes can be negative

    ''' If Accepted turned on save blog (but it might be question) '''
    if row[ACCEPTED] != '':
        accepted_count += 1
        if ACCEPTED_QUALIFIER:
            save_blog = True  # Previous tests may have turned off

    ''' TYPE = "Question" or "Answer" or "Wiki"'''
    if row[TYPE] == "Question":
        question_count += 1
        check_self_answer(row)
        if not QUESTIONS_QUALIFIER or self_answer:
            save_blog = False  # Questions aren't posted
    elif row[TYPE] == "Answer":
        answer_count += 1
    else:
        unknown_count += 1  # Happens when managing stack exchange site
        #print('Unknown Type:', dump(row))

    ''' If we aren't saving this blog, grab the next '''
    if save_blog is False:
        if row_number in random_row_nos:
            # This random record doesn't qualify so replace
            # with next record number
            index = random_row_nos.index(row_number)
            random_row_nos[index] = row_number + 1
        continue

    ''' convert SE tags: "<tag1><tag2><tag3>" to: "tag1 tag2 tag3"
        NOTE: pseudo_tag_names will be appended to this list later.
    '''
    tags = row[TAGS].replace("><", " ")
    tags = tags.replace("<", "").replace(">", "")

    #if row_number == 15:
    #    print('tags before:', works)
    #    print('tags after: ', tags)

    lines = row[MARKDOWN].splitlines()
    line_count = len(lines)
    if lines[line_count - 1] != "":
        # We need to force empty blank line at end to prevent searching
        # past end of list when checking next line's contents
        lines.append("")
        line_count += 1
        force_end_line = True
        total_force_end += 1

    ''' Pass #1: Count markdown elements '''
    new_lines = []
    copy_clipboard_count = 0
    for curr_index, line in enumerate(lines):
        line = check_code_block(line)  # Turn off formatting when in code block
        line = header_space(line)  # Change #Header to # Header and Alt-H1, Alt-H2
        line = block_quote(line)  # Formatting for block quotes
        check_paragraph(line)  # Check if Markdown paragraph (empty line)
        new_lines.append(line)  # Modified version of original lines
        command = check_copy_clipboard(curr_index)  # Insert command for clipboard?
        if command:
            # Code block qualifies for copy to clipboard button
            offset = code_block_index + copy_clipboard_count
            # offset will account for previous command inserted
            new_lines.insert(offset, command)
            # New lines list is now longer than original lines list
            copy_clipboard_count += 1
            # print('inserted line:', command)

    lines = new_lines
    #if copy_clipboard_count > 1:
    #    print()
    #    print('copy_clipboard_count:', copy_clipboard_count)
    #    dump(row)

    ''' Add to total lines '''
    total_lines += line_count
    if line_count > most_lines:
        most_lines = line_count
        #print('====== THE MOST LINES ======', most_lines)
        #dump(row)

    insert_toc = False  # Does not qualify for TOC yet
    if CONTENTS is not None:
        if header_count >= TOC_HDR_MIN and word_count >= TOC_WORD_MIN:
            insert_toc = True
            total_toc += 1
            # print('total_toc:    ', total_toc, blog_filename)

    insert_nav_bar = False  # Does not qualify for Navigation Buttons yet
    if NAV_BAR_OPT > 0:
        qualifier = sum(header_levels[:NAV_BAR_LEVEL])
        if qualifier >= NAV_BAR_MIN and word_count >= TOC_WORD_MIN:
            insert_nav_bar = True
            total_nav_bar += 1
            # print('total_nav_bar:', total_nav_bar, blog_filename)

    ''' Pass #2: Generate new markdown (kramdown) '''
    # Add SE Question tags + our answer key tags (if any)
    string = ' '.join(pseudo_tag_names)
    if len(string) > 0:
        tags = tags + " " + string

    # Generate Markdown (MD)  with front matter file start
    new_md = front_matter(row)

    ''' Add to totals using header_space() counts '''
    total_headers += header_count
    total_header_spaces += header_space_count
    total_alternate_h1 += alternate_h1
    total_alternate_h2 += alternate_h2
    total_header_levels = [x + y for x, y in zip(total_header_levels,
                                                 header_levels)]

    ''' Reset counts used in header_space() '''
    header_count = 0
    header_levels = [0, 0, 0, 0, 0, 0]
    alternate_h1 = 0
    alternate_h2 = 0
    if in_code_block:
        print('still in code block when post ended')
        dump(row)
    in_code_block = False   # In a code block # Header formatting is skipped
    toc_inserted = False    # Has TOC been inserted yet?
    sum2 = 0                # Track for new header to insert Navigation Bar

    for curr_index, line in enumerate(lines):
        check_code_block(line)      # Turn off formatting when in code block
        # Did this post qualify for adding navigation bar?
        # Save header levels counts we have now to "old_"
        old_header_levels = list(header_levels)
        line = header_space(line)   # Formatting for #Header or # Header lines
        if insert_nav_bar:
            sum1 = sum(old_header_levels[:NAV_BAR_LEVEL])
            sum2 = sum(header_levels[:NAV_BAR_LEVEL])
            # For next qualifying header level insert HTML for navigation bar.
            if sum1 != sum2:
                # First check if at TOC_LOC and insert TOC if needed
                if insert_toc:
                    if sum2 == TOC_LOC:
                        new_md = new_md + navigation_bar(TOC_LOC)
                        if NAV_BAR_OPT <= 3:
                            # If Option "4" a blank line already inserted before us
                            new_md = new_md + "\n"
                        new_md = new_md + CONTENTS + "\n"
                        new_md = new_md + "\n"  # When 4 a blank line already inserted before us
                        toc_inserted = True  # Not necessary but is consistent
                    if sum2 >= TOC_LOC:
                        sum2 += 1   # All heading levels after TOC are 1 greater

                new_md = new_md + navigation_bar(sum2)

        elif insert_toc:
            # No navigation bar, but we still need TOC at header count
            if header_count == TOC_LOC and toc_inserted is False:
                if NAV_BAR_OPT <= 3:
                    # If Option "4" a blank line already inserted before us
                    new_md = new_md + "\n"
                new_md = new_md + CONTENTS + "\n"
                new_md = new_md + "\n"
                toc_inserted = True  # Prevents regeneration next line read
                # print('toc only:', blog_filename)

        new_md = new_md + line + '\n'

    ''' Add tag for footer to jump to when 'Skip' button used on last #hdr'''
    if insert_nav_bar:
        # sum2 has last header id number used. Skip ID tag is 1 greater
        hdr_id = sum2 + 1
        if insert_toc and sum2 >= TOC_LOC:
            hdr_id += 1  # All heading levels after TOC are 1 greater
        if force_end_line:
            force_end_line = False  # Keep EOF empty line we added
        else:
            new_md = new_md + "\n"  # Empty line before HTML ID tag
        new_md = new_md + navigation_bar(hdr_id, skip_btn=False)

    qualifying_blog_count += 1
    if row_number in random_row_nos:
        if save_blog is True:
            save_blog_count += 1
            #print('Random upload row number: {:>6,}'.format(row_number))
            # print(new_md)
            if PRINT_RANDOM:
                dump(row)
            write_md(new_md)
        else:
            # This random record doesn't qualify so replace
            # with next record number
            #print('Random row record number: {:>6,}'.format(row_number),
            #      " - Does NOT qualify as blog so using next number.")
            index = random_row_nos.index(row_number)
            random_row_nos[index] = row_number + 1


if len(self_not_accept_url) > 0:
    print()
    print('// ==============/   Self-Answered Questions not accepted   \\================ \\\\')
    print('')
    for url in self_not_accept_url:
        print('URL:', url)
    print('')

print('// =============================/   T O T A L S   \\============================== \\\\')
print('')
print('RANDOM_LIMIT:     {:>6,}'.format(RANDOM_LIMIT),
      ' | PRINT_RANDOM:  {:>11}'.format(str(PRINT_RANDOM)),
      ' | NAV_FORCE_TOC: {:>11}'.format(str(NAV_FORCE_TOC)))
print('accepted_count:   {:>6,}'.format(accepted_count),
      ' | total_votes:   {:>11,}'.format(total_votes),
      ' | total_views:   {:>11,}'.format(total_views))
print('question_count:   {:>6,}'.format(question_count),
      ' | answer_count:       {:>6,}'.format(answer_count),
      ' | save_blog_count:    {:>6,}'.format(save_blog_count))
print('total_self_accept:{:>6,}'.format(total_self_answer),
      ' | total_self_answer:  {:>6,}'.format(total_self_accept),
      ' | Answers need accept:{:>6,}'.format(total_self_answer -
                                             total_self_accept))
print('total_headers:    {:>6,}'.format(total_headers),
      ' | total_header_spaces:{:>6,}'.format(total_header_spaces),
      ' | total_quote_spaces: {:>6,}'.format(total_quote_spaces))
print('total_lines: {:>11,}'.format(total_lines),
      ' | total_paragraphs:{:>9,}'.format(total_paragraphs),
      ' | total_words: {:>13,}'.format(total_words))
print('total_pseudo_tags:{:>6,}'.format(total_pseudo_tags),
      ' | total_tag_names:  ', total_tag_names)
print('total_pre_codes:  {:>6,}'.format(total_pre_codes),
      ' | total_alternate_h1: {:>6,}'.format(total_alternate_h1),
      ' | total_alternate_h2: {:>6,}'.format(total_alternate_h2))
print('total_code_blocks:{:>6,}'.format(total_code_blocks),
      ' | code_block_lines:  {:>7,}'.format(total_code_block_lines),
      ' | total_toc:         {:>7,}'.format(total_toc))
print('most_lines:       {:>6,}'.format(most_lines),
      ' | total_force_end:  {:>8,}'.format(total_force_end),
      ' | total_nav_bar:     {:>7,}'.format(total_nav_bar))
print('total_header_levels:       ', total_header_levels)

    # End of stack-to-blog.py
