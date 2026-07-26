from markitdown import MarkItDown
import secrets
import string
import os
import re
import aiofiles
def doc_to_markdown(doc_path) -> str : 
    """A fucntion to convert doc file to markdown
    Args:
        doc_path: a path to doc file
    return:
        a full string of the doc as markdown
    """
    md=MarkItDown()
    
    return md.convert(doc_path).text_content

def generate_unique_filepath(original_name:str):
    random_key= generate_random_string()
    clean_filename=get_clean_filename(original_name)

    new_file_path= os.path.join(
        "../files",
        random_key + "_"+ clean_filename
    )

    while os.path.exists(new_file_path):
        random_key= generate_random_string()
        new_file_path= os.path.join(
             "../files",
            random_key + "_"+ clean_filename
        )

    return new_file_path



def get_clean_filename(orig_filename:str):
    clean_file_name= re.sub(r'[^\w.]','',orig_filename.strip())
    cleaned_file_name= clean_file_name.replace(" ","_")
    return cleaned_file_name


def generate_random_string():
    alphabet = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(alphabet) for _ in range(16))
    return random_string


async def save_file(file_path,file):
    try:
        async with aiofiles.open(file_path,'wb') as f :
            while chunk := await file.read():
                await f.write(chunk)
    except Exception as e:
        print(e)