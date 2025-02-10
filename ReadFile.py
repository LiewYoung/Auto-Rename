from pathlib import Path
from docx import Document
import PyPDF2

class ReadFile:
    def __init__(self,file_path,max_read_size=1024):
        self.path=file_path
        self.max_read_size=max_read_size
        self.extension=Path(self.path).suffix.lower()
        
        
    def get_file(self):

        
        try:
            if self.extension not in ('.pdf','.docx'):
                with open(self.path,'r') as file:
                    file_include=file.read(self.max_read_size)
                    return file_include
        
            elif self.extension=='.pdf':
                with open(self.path,'rb') as file:
                    reader=PyPDF2.PdfReader(file)
                    page=reader.pages[0]
                    file_include=page.extract_text()
                    return file_include[:self.max_read_size]
        
            elif self.extension=='.docx':
                doc=Document(self.path)
                text=doc.paragraphs[0].text
                return text[:self.max_read_size]
            else:
                return 'Unsupported file type'
        except UnicodeDecodeError:
            print('UnicodeDecodeError!')
            print(self.extension)
            return Path(self.path).name
        

if __name__ == '__main__':
    path=input('Please input the path:')
    read_file=ReadFile(path)
    print(read_file.get_file())
            
