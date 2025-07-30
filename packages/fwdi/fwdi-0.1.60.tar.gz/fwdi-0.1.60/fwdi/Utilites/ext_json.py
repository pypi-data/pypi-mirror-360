import json
import re
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound='BaseModel')

regex = r"(\b\{).+(\}\B)"
regex_2 = r"\[.+\]"

@staticmethod
def get_only_dict(src_text:str)->str:
    try:
        text:str = ''
        matches = re.finditer(regex, src_text, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            st:int = int(match.start())
            en:int = int(match.end())
            text = src_text[st:en]
        
        return text.replace('\\n', '\n') if text else None
    
    except Exception as ex:
        print(f"get_only_dict:{ex}")
        return None

@staticmethod
def get_only_list(src_text:str)->str:
    try:
        text:str = ''
        matches = re.finditer(regex_2, src_text, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            st:int = int(match.start())
            en:int = int(match.end())
            text = src_text[st:en]
        
        return text.replace('\\n', '\n') if text else None
    
    except Exception as ex:
        print(f"get_only_dict:{ex}")
        return None   

@staticmethod
def get_all_exp(src_text:str, betwen:tuple)->list[str]:
    lst_data:list[str] = []

    lst_symb:str=""
    start_symb:bool = False
    for symb in src_text[1:-1]:
        if betwen[0] in symb:
            start_symb = True
        if betwen[1] in symb:
            start_symb = False
            lst_symb += symb
            lst_data.append(lst_symb)
            lst_symb = ""

        if start_symb:
            lst_symb += symb

    return lst_data

class LazyDecoder(json.JSONDecoder):
    def decode(self, s, **kwargs):
        regex_replacements = [
            (re.compile(r'([^\\])\\([^\\])'), r'\1\\\\\2'),
            (re.compile(r',(\s*])'), r'\1'),
        ]
        for regex, replacement in regex_replacements:
            s = regex.sub(replacement, s)
        return super().decode(s, **kwargs)

class ExtJson():
    
    @staticmethod
    def check_json(src_text:str)->bool:
        return True if '```json' in src_text else False
    
    @staticmethod
    def from_json_v3(src_text:str, type_object:type[T])->T|None:
        try:
            src_text = src_text.replace('\n', '')

            parsed_text = get_only_dict(src_text)
            if not parsed_text:
                parsed_text = get_only_list(src_text)
                if parsed_text:
                    lst_text:list = get_all_exp(parsed_text, ("(",")"))
            else:
                lst_text:list = get_all_exp(parsed_text, ("{","}"))
            
            if not lst_text:
                raise Exception(f"Error no way get list or dict data")
            
            
            lst_data = [ExtJson.json_str_to_dict(item) for item in lst_text]
            inst = type_object.from_list(lst_data)

            return inst
        except Exception as ex:
            print(f"Error: {ex}")
            return None

    @staticmethod
    def from_json(src_text:str, type_object:type[T])->BaseModel|None:
        try:
            inst_dict = ExtJson.json_str_to_dict(src_text)
            
            if isinstance(inst_dict, list):
                instance = type_object.from_list(inst_dict)
                return instance
            else:
                inst_model = type_object.model_validate(inst_dict)
                if inst_model is None:
                    inst_model = type_object(**inst_dict)

            return inst_model
        except Exception as ex:
            print(f"ExtJson->from_json, Error:{ex}")
            return None

    @staticmethod
    def json_str_to_dict(src_text:str)->dict:
        try:
            start_text_json:int = -1
            end_text_json:int = -1

            for index_start in range(len(src_text)):
                if src_text[index_start] == '{' or src_text[index_start] == '[' or src_text[index_start] == '(':
                    start_text_json = index_start
                    break
            if start_text_json != -1:
                for index_end in range(len(src_text), 0, -1):
                    if src_text[index_end-1] == '}' or src_text[index_end-1] == ']' or src_text[index_end-1] == ')':
                        end_text_json = index_end
                        break
            else:
                print(f"Start json not found.")
                return {}
            
            if start_text_json != -1 and end_text_json != -1:
                to_json_struct:str = src_text[start_text_json:end_text_json]
                if to_json_struct[0] == '(':
                    to_json_struct = to_json_struct.replace('(', '{', 1)
                    to_json_struct = to_json_struct.replace(')', '}', 1)
                json_object:dict = json.loads(to_json_struct, cls=LazyDecoder)
            else:
                print(f"End json not found.")
                return {}

            if len(json_object) == 1:
                if 'questions' in json_object:
                    json_object = json_object['questions']
                elif 'вопросы' in json_object:
                    question_t = [item for item in json_object.keys() if item.lower() == 'вопросы']
                    if len(question_t) > 0:
                        json_object = json_object['вопросы']
            
            return json_object
        except Exception as ex:
            print(ex)
            return to_json_struct if to_json_struct else src_text