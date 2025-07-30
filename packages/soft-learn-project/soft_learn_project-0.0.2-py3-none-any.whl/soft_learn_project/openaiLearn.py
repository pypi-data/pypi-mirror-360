
import openai


class OpenaiLearn():
  def __init__(self) -> None:
    # 我的openai 信息
    openai_API_KEY = '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'
    openai_organization = "org-21cqFihM8fsXffandwabhCKv"
    openai.api_key = openai_API_KEY

  def example(self,):
    user_message = '太阳系八大行星'
    response = openai.ChatCompletion.create(model='gpt-3.5-turbo',
                                            messages=[
                                                {'role': 'user', 'content': user_message}]
                                            )
    assistant_response = response['choices'][0]['message']['content']
    print('ChatGPT:', assistant_response.strip('\n').strip())
    pass


class OpenaiLearnDeepSeek():
  def __init__(self):
    """https://api-docs.deepseek.com/zh-cn/
    """
    self.deepseek_API_key = 'sk-171c25b9f5ca488aa6ba6005492662a1'
    pass

  def install(self):
    # !pip install openai
    pass

  def get_response(self):
    client = openai.OpenAI(api_key=self.deepseek_API_key,
                           base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )

    # print(response.choices[0].message.content)
    return response.choices[0].message.content
