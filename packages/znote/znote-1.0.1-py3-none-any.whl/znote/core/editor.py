# -*- coding: utf-8 -*-

import sys
import asyncio
import os # Import os for checking file existence

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, Window
from prompt_toolkit.widgets import TextArea, Label
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.filters import Condition

from prompt_toolkit.layout.containers import ConditionalContainer
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.layout.controls import BufferControl

from zpp_ManagedFile import ManagedFile

class Editor:
    def __init__(self, filename, file):
        # --- État de l'application ---
        self.file = file # Default filename
        self.filename = filename

        # --- UI Elements ---
        self.text_area = TextArea(
            multiline=True,
            wrap_lines=True,
            scrollbar=True,
            line_numbers=True,
        )
        # Initial status bar text will be set after loading
        self.status_bar = Label(text="") # Start empty, will be set by load_file
        # --- Layout ---
        self.layout = Layout(
            HSplit([
                self.text_area,
                self.status_bar,
            ]),
        )

        # --- Key Bindings ---
        self.kb = KeyBindings()

        @self.kb.add("c-q")
        def _(event):
            """ Global shortcut to quit """
            asyncio.get_event_loop().create_task(self.quit())


        @self.kb.add("c-s") # Active only in editor mode
        def _(event):
            """ Ctrl+S shortcut to save """
            # Schedule save_file as it's an async method
            asyncio.get_event_loop().create_task(self.save_file())

        # --- Application ---
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
            # style...
        )

        # --- Initial Actions ---
        self.load_file(self.file) # Load file content on startup
        self.app.layout.focus(self.text_area) # Set initial focus

    # --- File Loading ---
    def load_file(self, filename):
        """ Loads content from a file into the text area on startup """
        try:
            if isinstance(self.file,ManagedFile) and hasattr(self.file,'read'):
                self.file.seek(0)
                self.text_area.text = self.file.read()
                self.status_bar.text = f"Fichier chargé."
            else:
                if os.path.exists(filename):
                    with open(filename, "r", encoding='utf-8') as f:
                        content = f.read()
                        self.text_area.text = content
                    self.status_bar.text = f"Fichier '{filename}' chargé."
                else:
                    self.status_bar.text = f"Nouveau fichier '{filename}'."
        except Exception as e:
            # Basic error handling for loading
            self.status_bar.text = f"Erreur de chargement : {e}"
        # Status messages set here are static until the first save/reset


    # --- File Saving ---
    # save_file must be async because it's awaited in save_and_quit
    async def save_file(self):
        """ Saves content to the default file """
        filename = self.file # Use attribute
        try:
            if isinstance(self.file,ManagedFile) and hasattr(self.file,'read'):
                self.file.seek(0)
                self.file.truncate(0)
                self.file.write(self.text_area.text)
            else:
                # Synchronous file writing
                with open(self.file, "w", encoding='utf-8') as f:
                    f.write(self.text_area.text)

            # Update status bar on success and schedule reset
            self.status_bar.text = f"Fichier '{filename}' sauvegardé."
            return True
        except Exception as e:
             # Update status bar on error and schedule reset
            self.status_bar.text = f"Erreur de sauvegarde : {e}"
            return False

    # --- Quit ---
    # async because it awaits the message_dialog
    async def quit(self, event=None):
        """ Asks for confirmation and quits the application """
        # Use the message_dialog, which is awaited
        self.app.exit()

# Entry point
if __name__ == '__main__':
    try:
        file = ManagedFile(mode='a', typefile='stringio')
        editor = Editor(file)
        editor.app.run()
        file.seek(0)
        print(file.read())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)