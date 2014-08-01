
# this is the magic interpreted by Sonata, referring to tab_construct below:

### BEGIN PLUGIN INFO
# [plugin]
# plugin_format: 0, 0
# name: YouTube
# version: 0, 0, 1
# description: YouTube stream searcher/player
# author: Daniel Kochmanski
# author_email: dkochmanski@hellsgate.pl
# url: http://sonata.berlios.de
# license: GPL v3 or later
# [capabilities]
# tab_construct: tab_construct
### END PLUGIN INFO

from gi.repository import GLib, Gtk
from sonata import ui
from sonata import launcher

import threading
import subprocess

# nothing magical here, this constructs the parts of the tab when called:
def tab_construct():
    builder = ui.builder('youtube', 'plugins')
    phrase = builder.get_object('phrase')
    search = builder.get_object('search')

    lambda_search = lambda *args: search_phrase_in_separate_thread(
        builder,
        [builder, phrase.get_text()])
    
    phrase.connect('activate', lambda_search)
    search.connect('clicked', lambda_search)
    
    builder.get_object('results_view').connect(
        'row_activated', lambda *args: trigger_row(builder))

    window = builder.get_object('youtube_scrolledwindow')
    window.show_all()
    tab_widget = builder.get_object('youtube_tab_eventbox')

    return (window, tab_widget, "YouTube", None)

def trigger_row(builder):
    tree_view = builder.get_object('results_view')
    value = builder.get_object('results').get_value(
        tree_view.get_selection().get_selected()[1], 1)
    
    launcher._global_sonata.stream_parse_and_add(value)

my_thread = None
def search_phrase_in_separate_thread(builder, arguments):
    global my_thread
    if my_thread != None:
        my_thread.cancel()

    results = builder.get_object('results').clear()

    my_thread = threading.Thread(
        target=search_phrase,
        args=arguments).start()

def search_phrase(builder, phrase):
    tree_view = builder.get_object('results_view')
    results = builder.get_object('results');

    tree_view.get_selection().unselect_all()
    process = subprocess.Popen(
        ["youtube-dl", "-fbestaudio", "--skip-download", "-ge",
         "ytsearch4:"+phrase], stdout=subprocess.PIPE)
    for (title, url) in zip ( iter(process.stdout.readline, b''),
                              iter(process.stdout.readline, b'')):
        results.append([title.rstrip().decode(),
                        url.rstrip().decode()])
