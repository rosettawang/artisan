__version__ = '4.2.1'
__revision__ = ''
__build__ = '0'
__artisan_os__ = 'Linux'

# Fork marker shown in the main window title so a build from this source tree is
# never mistaken for the installed release while both are open. Deliberately NOT
# part of application_name: that string keys QSettings (main.py:560), and changing
# it would give the fork a different preferences file.
# Set to '' to make the fork title-identical to upstream.
__fork_label__ = ' [FORK]'

__release_sponsor_name__ = 'LABEL!ISTEN'
__release_sponsor_domain__ = 'labelisten.com'
__release_sponsor_url__ = 'https://labelisten.com/'
__signature__ = '4857e858c31f5a78c45bbee1a8e3d89d7b177feacefe47052d5029d4f8fc6ff4f82829c4e6b04b9ee11e1602613b523a98e6bffe0581793afb50238dafeb1e08'
