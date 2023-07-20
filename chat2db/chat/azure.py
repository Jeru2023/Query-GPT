import openai


class Azure():

    def __init__(self, api_key, api_base, engine):
        openai.api_version = "2023-05-15"
        openai.api_type = "azure"
        openai.api_key = api_key
        openai.api_base = api_base
        self.engine = engine

    def azure_ask(self, messages):
        for response in openai.ChatCompletion.create(
                engine=self.engine,
                messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                stream=True,
        ):
            print(response)
            full_response = response.choices[0].delta.get("content", "")
            yield full_response

    def used_db(self):
        pass

    def choice_db(self):
        pass

    def keyword_extract(self):
        pass


if __name__ == '__main__':
    azure = Azure("ced27977c8aa4c03b037bd5c0c0572b0", "https://gz-uk-0613.openai.azure.com/", "gz_0613")
    for i in azure.azure_ask([{"role": "user", "content": "写一个hello world程序"}]):
        pass
