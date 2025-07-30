import os
import sys
import base64
import ast
import openai
import Orange
from Orange.data import StringVariable
from Orange.widgets.widget import OWWidget, Input, Output
from AnyQt.QtWidgets import QApplication

class ChatGpt(OWWidget):
    name = "CallChatGptApi"
    description = "Call to chatgpt API. You need to provide a prompt and an api_keys. You call also add an image_paths and a system_prompt if you want."
    icon = "icons/chatgpt.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/chatgpt.png"
    priority = 3000

    class Inputs:
        data = Input("Data", Orange.data.Table)

    @Inputs.data
    def set_data(self, in_data):
        if in_data is None:
            return
        if "prompt" not in in_data.domain:
            self.error("input table need a prompt column")
            return
        self.prompt = in_data.get_column("prompt")[0]
        if "image_paths" in in_data.domain:
            self.image_paths = in_data.get_column("image_paths")[0]
        if "api_keys" not in in_data.domain:
            self.error("input table need a api_keys column")
        self.api_keys = in_data.get_column("api_keys")[0]
        if "system_prompt" in in_data.domain:
            self.system_prompt = in_data.get_column("system_prompt")[0]
        self.data = in_data
        self.run()

    class Outputs:
        data = Output("Data", Orange.data.Table)

    def __init__(self):
        super().__init__()
        self.data = None
        self.prompt = None
        self.image_paths = None
        self.api_keys = None
        self.system_prompt = ""
        self.max_tokens = 4000
        self.temperature = 0
        self.model = "gpt-4.1"
        self.run()

    def run(self):
        self.error("")
        self.warning("")

        if self.data is None:
            return

        if self.prompt == "" or self.prompt is None:
            self.error("No prompt provided.")
            return

        if self.api_keys is None:
            self.error("No api keys provided.")
            return

        self.prompt = [{"type": "text", "text": self.prompt}]

        if self.image_paths is not None and self.image_paths != []:
            if type(self.image_paths) == str:
                self.image_paths = ast.literal_eval(self.image_paths)
            for img_path in self.image_paths:
                with open(img_path, "rb") as f:
                    b64_img = base64.b64encode(f.read()).decode("utf-8")
                    self.prompt.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_img}"
                        }
                    })

        try:
            openai.api_key = self.api_keys
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": self.prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            text_response = response.choices[0].message.content
        except Exception as e:
            self.error(f"Error: {e}")
            return
        if text_response is None:
            self.error("No response from chatgpt.")
            return
        new_name_column = StringVariable("answer")
        table = self.data.add_column(new_name_column, [text_response])
        self.Outputs.data.send(table)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = ChatGpt()
    my_widget.show()

    if hasattr(app, "exec"):
        sys.exit(app.exec())
    else:
        sys.exit(app.exec_())
