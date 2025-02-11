from api_chat import Chat

from pathlib import Path
from ReadFile import ReadFile

dir:str
    
def get_titles(path,bot:Chat):
       for flie_path in path:
            file=ReadFile(flie_path)
        #to save tokens so it limit 1024
            title=bot.get_title(file.get_file())
            yield title

    

def main():
    chat_bot=Chat(api_key='18fe4ef8894bb43f50817a3c00703760.ckOTflSYYwlWZvHz',log=True)  

    manger_path=[file_path for file_path in Path(dir).iterdir() if file_path.is_file()]
    
    manger_title=get_titles(manger_path,chat_bot)

    for file_path in manger_path:
        try: 
            path=Path(file_path)
            print(f"Now rename:{path.name}")
            path.rename(path.parent/(next(manger_title)+path.suffix.lower()))
        except PermissionError:
            print('PermissionError some file is open')
        except StopIteration:
            print('StopIteration ! It is the end!')
            break
        except FileExistsError:
            print('FileExistsError! File already exists!')
        
        
   


if __name__ == '__main__':
    dir=input('Please input the dir:')
    main()
