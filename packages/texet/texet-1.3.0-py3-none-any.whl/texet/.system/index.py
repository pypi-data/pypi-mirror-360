from imports import *


class index:
    ####################################################################################// Load
    def __init__(self, app="", cwd="", args=[]):
        self.app, self.cwd, self.args = app, cwd, args
        # ...
        cli.dev = "-dev" in args
        self.lng = cli.read(self.app + "/.system/sources/lng.yml").splitlines()
        self.sysdir = self.__loadSysDir("texet")
        self.keyfile = f"{self.sysdir}/key"
        self.key = cli.read(self.keyfile)
        self.current_proc = None
        self.sounds = True
        self.aiclass = AI(self.key)
        pass

    def __exit__(self):
        if self.current_proc:
            self.__stopSpeak()
        pass

    ####################################################################################// Main
    def start(self, cmd=""):  # Start the system
        shortcuts = self.__shortcuts()
        if not shortcuts:
            return "Invalid shortcuts!"

        return self.__start(shortcuts)

    def aikey(self, remove="", cmd=""):  # (-r) - Set OpenAI key, -r to remove it
        if remove.strip() == "-r" and self.__delKey():
            return "API key removed successfully"

        file = self.keyfile.replace("\\", "/")
        key = cli.input("Enter your OpenAI API key", True).strip()

        cli.trace("Writing the API key file")
        cli.write(file, key)
        print()

        return "API key was stored at the location: " + file

    ####################################################################################// Methods
    def translateText(self, task: str, returns: str):
        content = self.__copy().strip()
        if not content:
            return False

        parts = content.split("/")
        lng = parts.pop().strip()
        if not lng or lng not in self.lng:
            cli.error('Specify language by adding e.g. "/en" to the end of the text')
            return False

        parsed = "/".join(parts)
        if not parsed.strip():
            return False

        cli.trace("Translating text to: " + lng)
        translated = asyncio.run(self.__translate(parsed, lng)) or parsed

        return self.__paste(translated)

    def readText(self, task: str, returns: str):
        content = self.__copy().strip()
        if not content:
            return False

        self.sounds = False
        self.__speak(content, 150, 0)

        return True

    def stopReadingText(self, task: str, returns: str):
        if self.current_proc:
            self.sounds = False
            self.__stopSpeak()

        return True

    def writeText(self, task: str, returns: str):
        self.sounds = False
        content = cli.listen()
        if not content:
            return False

        return self.__paste(" " + content)

    def writeFixedText(self, task: str, returns: str):
        if not self.key:
            cli.error("You need to set up your OpenAI API key to continue")
            return False

        self.sounds = False
        content = cli.listen()
        if not content:
            return False

        task += " Below is my text that you must fix:\n\n" + content
        text = self.aiclass.response(task, returns).text() or text

        return self.__paste(" " + text)

    def parseText(self, task: str, returns: str):
        content = self.__copy().strip()
        if not content:
            return False

        parsed = self.aiclass.parse(content).text() or content

        return self.__paste(parsed)

    def writeCode(self, task: str, returns: str):
        if not self.key:
            cli.error("You need to set up your OpenAI API key to continue")
            return False

        command = cli.listen()
        if not command:
            return False

        cli.trace(f"Me: " + command)
        task += f" Now, {command}"
        code = self.aiclass.response(task, returns).code().strip() or ""

        return self.__paste(code)

    def fixText(self, task: str, returns: str):
        if not self.key:
            cli.error("You need to set up your OpenAI API key to continue")
            return False

        content = self.__copy().strip()
        if not content:
            return False

        task += " Below is my text that you must fix:\n\n" + content
        text = self.aiclass.response(task, returns).text() or text

        return self.__paste(text)

    def fixCode(self, task: str, returns: str):
        if not self.key:
            cli.error("You need to set up your OpenAI API key to continue")
            return False

        content = self.__copy()
        hinted = " >> " in content
        command = (
            cli.listen()
            if not hinted
            else 'Implement logic specified in comments beginning with " >> ", and remove that comments'
        )

        if not content.strip() or not command:
            cli.error("Select the code sample and ask what needs to be fixed")
            return False

        cli.trace(f"Me: " + command)
        task += f" {command}, this is my code:\n\n" + content
        code = self.aiclass.response(task, returns).code().strip() or content

        return self.__paste(code)

    def addVersions(self, task: str, returns: str):
        if not self.key:
            cli.error("You need to set up your OpenAI API key to continue")
            return False

        content = self.__copy()
        if not content:
            return False

        task += " This is my content:\n\n" + content
        text = self.aiclass.response(task, returns).text().strip() or text
        space = self.__space(content)

        return self.__paste(space + text)

    def answerMessage(self, task: str, returns: str):
        if not self.key:
            cli.error("You need to set up your OpenAI API key to continue")
            return False

        content = self.__copy().strip()
        if not content:
            return False

        task += " Below is a given sample message:\n\n" + content
        text = self.aiclass.response(task, returns).text().strip() or text
        pyperclip.copy(text)

        return True

    ####################################################################################// Helpers
    def __start(self, methods: dict):
        if not methods:
            return "Invalid system methods!"

        ready = []
        for each in methods:
            if not hasattr(self, each):
                cli.trace("Invalid method: " + each)
                continue
            desc, key, task, returns = methods[each].values()
            keyboard.add_hotkey(key, partial(self.__execute, each, task, returns))
            cli.trace("Binded keyboard shortcut method: " + each)
            ready.append(f"Press [{key}] to " + desc.lower())

        if not ready:
            return "No methods have been registered!"

        cli.info("\n".join(ready))
        cli.info("Press [ctrl+c] to shut TexeT down")
        print()

        cli.trace("Waiting for keyboard shortcuts")
        keyboard.wait()
        pass

    def __execute(self, name, task, returns):
        try:
            cli.trace("Running the method: " + name)
            method = getattr(self, name)
            if not method(task, returns):
                cli.sound("error")
            elif self.sounds:
                cli.sound("done")
            self.sounds = True
        except Exception as e:
            cli.error(f"Error: {str(e)}")

    def __copy(self):
        previous = pyperclip.paste()
        subprocess.run(
            [sys.executable, "-c", "import pyautogui; pyautogui.hotkey('ctrl','c')"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        deadline = time.time() + 0.5
        while time.time() < deadline:
            new = pyperclip.paste()
            if new != previous:
                content = new
                break
            time.sleep(0.01)
        else:
            content = new

        return content

    def __paste(self, text: str):
        if not text:
            return False

        pyperclip.copy(text)
        time.sleep(0.5)
        keyboard.press_and_release("ctrl+v")

        return True

    async def __translate(self, text: str, dest: str):
        translator = Translator()
        result = await translator.translate(text, dest=dest)

        return result.text

    def __loadSysDir(self, name=""):
        if not name:
            cli.error("Invalid system folder name")
            sys.exit()

        sysdir = Path.home()
        if not os.path.exists(sysdir):
            cli.error("Invalid system folder")
            sys.exit()

        folder = f"{sysdir}/.{name}"
        os.makedirs(folder, exist_ok=True)

        return folder

    def __delKey(self):
        if not cli.isFile(self.keyfile):
            return False

        cli.trace("Deleting the API key")
        os.remove(self.keyfile)
        return True

    def __space(self, text: str):
        return text[: len(text) - len(text.lstrip())]

    def __speak(self, text="", speed=150, voice=0):
        file = self.app + f"/.system/modules/speak.py"
        if not cli.isFile(file):
            return False

        if self.current_proc:
            self.__stopSpeak()

        cmd = [sys.executable, file, text, str(speed), str(voice)]
        popen_kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}

        if os.name != "nt":
            popen_kwargs["start_new_session"] = True

        cli.trace("Starting new speaker")
        self.current_proc = subprocess.Popen(cmd, **popen_kwargs)

        return True

    def __stopSpeak(self):
        cli.trace("Terminating running speaker")
        if self.current_proc.poll() is not None:
            return

        self.current_proc.terminate()
        try:
            self.current_proc.wait(timeout=0.2)
        except subprocess.TimeoutExpired:
            self.current_proc.kill()
            self.current_proc.wait()

        return True

    def __shortcuts(self):
        return {
            "translateText": {
                "desc": 'Translate the selected editable text by appending e.g. "/en" to the end',
                "key": "ctrl+alt+t",
                "task": "",
                "returns": "",
            },
            "readText": {
                "desc": "Read the selected text aloud",
                "key": "ctrl+alt+r",
                "task": "",
                "returns": "",
            },
            "stopReadingText": {
                "desc": "Stop reading the selected text aloud",
                "key": "ctrl+shift+alt+r",
                "task": "",
                "returns": "",
            },
            "writeText": {
                "desc": "Listen and transcribe the text",
                "key": "ctrl+alt+w",
                "task": "",
                "returns": "",
            },
            "writeFixedText": {
                "desc": "Listen, transcribe and fix the text with grammar",
                "key": "ctrl+shift+alt+w",
                "task": "Fix given text with grammar without changing the context.",
                "returns": "TXT format block of fixed text",
            },
            "parseText": {
                "desc": "Parse the selected text for unusual characters.",
                "key": "ctrl+alt+p",
                "task": "",
                "returns": "",
            },
            "writeCode": {
                "desc": "Listen and write the code",
                "key": "ctrl+alt+c",
                "task": "Generate clearly structured code designed to perform the described functionalities.",
                "returns": "required CODE block",
            },
            "fixText": {
                "desc": "Fix the selected text",
                "key": "ctrl+alt+f",
                "task": "Fix given text with grammar without changing the context.",
                "returns": "TXT format block of fixed text",
            },
            "fixCode": {
                "desc": "Fix the selected code",
                "key": "ctrl+shift+alt+f",
                "task": "Keep or improve the given code sample, ensuring that the spacing of the code body remains unchanged.",
                "returns": "CODE block with relevant format and same spacing",
            },
            "addVersions": {
                "desc": "Add versions of the selected content",
                "key": "ctrl+alt+v",
                "task": "Evolve the given text or code up to 4 more versions with the same context. Add the new versions as new lines while maintaining the same spacing in the text or code body.",
                "returns": "TXT format block of text, or CODE block with relevant format",
            },
            "answerMessage": {
                "desc": "Reply to the selected text message",
                "key": "ctrl+alt+a",
                "task": "Generate a relevant response message to the given message sample. Maintain a tone that matches the given message sample.",
                "returns": "TXT format block of response message",
            },
        }
