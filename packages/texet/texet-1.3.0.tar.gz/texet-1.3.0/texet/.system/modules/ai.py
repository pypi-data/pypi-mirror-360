from imports import *


class AI:
    ####################################################################################// Load
    def __init__(self, key: str):
        self.client = OpenAI(api_key=key)
        self.extensions = self.__loadExtensions()
        self.characters = self.__loadCharacters()
        self.content = ""
        pass

    ####################################################################################// Main
    def response(self, task: str, returns: str):
        self.content = ""
        chat = [
            {
                "role": "system",
                "content": f"You are my assistant. You don't ask any questions. You must only return {returns} as requested.",
            },
            {
                "role": "user",
                "content": task,
            },
        ]

        try:
            cli.trace("Sending AI request ...")
            response = self.client.responses.create(model="gpt-4o", input=chat)
        except openai.APIConnectionError as e:
            alert = f"Detected an AI connection error: {str(e)}"
        except openai.APITimeoutError as e:
            alert = f"Detected an AI timeout: {str(e)}"
        except openai.RateLimitError as e:
            alert = f"Detected AI rate limit error: {str(e)}"
        except openai.BadRequestError as e:
            alert = f"Detected an AI invalid request error: {str(e)}"
        except openai.AuthenticationError as e:
            alert = f"Detected AI authentication error: {str(e)}"
        except Exception as e:
            cli.error(f"Error: {str(e)}")
            return ""

        self.content = response.output_text

        return self

    def parse(self, content: str):
        self.content = content

        return self

    ####################################################################################// Actions
    def full(self):
        return self.content

    def text(self):
        content = self.code()
        if not content:
            return content

        cli.trace("Parsing text characters")
        for char in self.characters:
            content = content.replace(char, self.characters[char])

        return content

    def code(self):
        if not self.content:
            cli.trace("Empty AI response content!")
            return ""

        content = self.content
        cli.trace("Parsing code extensions")
        for replacer in self.extensions:
            content = content.replace("```" + replacer, "```")

        parse = content.split("```")
        n = 0
        collect = ""
        code = ""
        for index in range(len(parse)):
            if n == 0:
                collect += parse[index].replace("\n", " ")
                n = 1
            else:
                n = 0
                code += "\n\n" + parse[index]

        if len(str(code)) > 0:
            content = str(code)

        return content

    ####################################################################################// Helpers
    def __loadExtensions(self):
        file = os.path.dirname(os.path.dirname(__file__)) + "/sources/ext.yml"
        if not cli.isFile(file):
            cli.trace("Invalid extensions file: " + file)
            return []

        cli.trace("Reading extensions file")
        collect = set(cli.read(file).splitlines())

        return sorted(collect, key=len, reverse=True)

    def __loadCharacters(self):
        return {
            "–": "-",
            "—": "-",
            "“": '"',
            "”": '"',
            "‘": "'",
            "’": "'",
            "¯": "'",
            "ツ": "-",
            "ν": "v",
            "í": "i",
            ", and": " and",
            # "": "",
        }
