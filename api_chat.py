import requests as rq
from pathlib import Path 
import json

class Chat:
    def __init__(
            self,
            api_key:str,
            max_token=1024,
            temperature=0.9,
            top_p=0.9,
            model='glm-zero-preview',
            CC_Chat=False,#连续对话预留参数
            log=False,#是否保存每次对话的log
        ):
        self.max_token=max_token
        self.temperature=temperature
        self.top_p=top_p
        self.model=model
        self.CC_Chat=CC_Chat#连续对话预留参数
        self.log=log
        self.api_key='Bearer '+api_key
    
    def __get_header(self):
        header={
            'Authorization': self.api_key,
            'Content-Type': 'application/json',
        }
        return header
    
    def __get_data(self,file_include:str):
        data={
            'model':'glm-zero-preview',
            'messages':[
            {
                'role':'system',
                'content':'你会获得文件内容并归类为标题（title）必须是中文.您应该始终遵循指令并输出一个有效的JSON对象。请根据指令使用指定的JSON对象结构。如果不确定，请默认使用 {"answer": "$your_answer","title":"$your_title"}。确保始终以 "```" 结束代码块，以指示JSON对象的结束。',
            },
            {
                'role':'user',
                'content':file_include,
            },
        
            ],
            'response_format':{
                'type':'json_object'
                },
            'temperature':self.temperature,
            'top_p':self.top_p,
            'max_tokens':self.max_token,
        }
        return data
    
    def get_title(self,file_include:str):
        header=self.__get_header()
        data=self.__get_data(file_include=file_include)
        response=rq.post('https://open.bigmodel.cn/api/paas/v4/chat/completions',headers=header,json=data)

        #to get title if your want answer, you can change the code below to 'answer'
        try:
            title=json.loads(response.json()['choices'][0]['message']['content'])['title']
        except KeyError:
            print('KeyError!')
            print('file_include:')
            print(file_include)
            print(response.json())
            title='空文件'
        except json.JSONDecodeError:
            print('JSONDecodeError!')
            print('file_include:')
            print(response.json())
            title='解析错误'

        if self.log:
            path=Path(f'log/Title_{title}.json')
            json_data=json.dumps(response.json(),ensure_ascii=False,indent=4)
            path.write_text(json_data)

        return title
        

    
if __name__ == '__main__':
    chat_bot=Chat(api_key='c5ba6c82bc7d481baaaed21cf0fd3f08.WHAv1d83loHT75Ll')
    print(chat_bot.get_title(file_include='你好')) 