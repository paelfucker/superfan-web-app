from openai import OpenAI
import tiktoken
from rich import print
from config import OPENAI_API_KEY



def num_tokens_from_messages(messages, model='gpt-4o'):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += 4
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += -1
        num_tokens += 2
        return num_tokens
    except Exception:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not presently implemented for model {model}.
            See https://github.com/openai/openai-python/blob/main/chatml.md"""
        )


class OpenAiManager:
    def __init__(self):
        self.chat_history = []
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def chat(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        chat_question = [{"role": "user", "content": prompt}]
        if num_tokens_from_messages(chat_question) > 8000:
            print("The length of this chat question is too large for the GPT model")
            return

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=chat_question
        )

        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer

    def chat_with_history(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return

        self.chat_history.append({"role": "user", "content": prompt})
        print(f"[coral]Chat History has a current token length of {num_tokens_from_messages(self.chat_history)}")
        while num_tokens_from_messages(self.chat_history) > 8000:
            self.chat_history.pop(1)
            print(f"Popped a message! New token length is: {num_tokens_from_messages(self.chat_history)}")

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.chat_history
        )

        self.chat_history.append({
            "role": completion.choices[0].message.role,
            "content": completion.choices[0].message.content
        })

        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer


if __name__ == '__main__':
    openai_manager = OpenAiManager()

    chat_without_history = openai_manager.chat("Hey ChatGPT what is 2 + 2? But tell it to me as Yoda")

    FIRST_SYSTEM_MESSAGE = {
        "role": "system",
        "content": "Act like you are Captain Jack Sparrow from the Pirates of Carribean movie series!"
    }
    FIRST_USER_MESSAGE = {
        "role": "user",
        "content": "Ahoy there! Who are you, and what are you doing in these parts? Please give me a 1 sentence background on how you got here."
    }
    openai_manager.chat_history.append(FIRST_SYSTEM_MESSAGE)
    openai_manager.chat_history.append(FIRST_USER_MESSAGE)

    while True:
        new_prompt = input("\nType out your next question Jack Sparrow, then hit enter: \n\n")
        openai_manager.chat_with_history(new_prompt)
