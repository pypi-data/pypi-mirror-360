from docx import Document
import json
import os
from termcolor import colored



def extract_text(text,split_text, index0=None, index1=None, ):
    try:
        if split_text not in text:
            raise ValueError
        processed=text.split(split_text)
    except:
        print(colored(F'REVIEW TAG {split_text} on {name_file}, may be left it or it have been witten bad ', 'red'))
        raise ValueError
    if index0 and index1:
        processed=processed[index0:index1]

    if index0:
        processed=processed[index0:]

    if index1:
        processed=processed[:index1]

    return '\n'.join(processed)

def get_title(text_docx):
   return  extract_text(text_docx,'{title}', index1=1).replace('\n', ' ')

def get_body(text_docx):
    return extract_text(text_docx,'{title}', index0=1)

def get_themes(text_body, result_array=True):
    sections_text=extract_text(text_body, '{themes}',index1=1)

    if result_array:

        result_themes=[]        
        if '{WITHOUT-THEME}' in text_body:
            result_themes.append('WITHOUT-THEME')

        if '{theme}' in sections_text or '{last-theme}' in sections_text:
            section_array=sections_text.split('{theme}')
            result_themes+=list(map(lambda tema: tema.replace('\n', '').replace('{last-theme}', '').strip(), section_array)) # para limpiar cualquier salto de linea, etiqueta no servible o espacios de mas que tenga el texto
       

        return result_themes
   
    
    return sections_text



def questions_theme_text_dict(questions_text):
    # print(questions_text, 'entrada')
    clean_questions_texts='\n'.join([line for line in questions_text.splitlines() if '{no-use}' not in line])
    json_questions=[]
    try:
        split_questions=clean_questions_texts.split('{question}')
    except:
        print(colored('REVIEW FORMAT QUESTION, LEFT {question} TAG'+ name_file, 'red'))
        print(colored(clean_questions_texts, 'yellow'))
        raise ValueError



    while len(split_questions)>1:
        try:
            split_question=split_questions[0].split('{answer}')
        except:
            print(colored('REVIEW FORMAT QUESTION, LEFT {answer} TAG'+ name_file, 'red'))
            print(colored(split_question, 'yellow'))
            raise ValueError


        question=split_question[0].replace('\n','')
        answers=split_question[1]

        #para poner un limite al while, borra contenido y genera un nuevo split para avanzar cuando acabe
        clean_questions_texts=clean_questions_texts.replace(split_questions[0]+'{question}' , '')
        split_questions=clean_questions_texts.split('{question}')

        dict_tmp={}
        dict_tmp['question']=question     
        dict_tmp['answers']=[]
        for answer in answers.splitlines():
            if answer not in ['', '\n', '\t']:
                try:
                    answer_cleaned=answer.split('.-')[1].replace('{question}', '')
                except:
                    print(colored(split_questions, 'cyan'))
                    print(colored(question +'\n' +answers, 'yellow'))
                    print(colored(answer.split('.-'), 'yellow'))
                    print(colored('REVIEW FORMAT ANSWER, LEFT .-, or left other tag at the top question, ({question}, {answer})'+ name_file, 'red'))
                    raise ValueError
                if '*' in answer_cleaned:

                    dict_tmp['answers'].append({answer_cleaned.replace('*',''):True})
                else:
                     dict_tmp['answers'].append({answer_cleaned:False})

        json_questions.append(dict_tmp)
    # for question in json_questions:
    #     print(question)



    return json_questions

def get_questions(text_body, themes):

    theme_questions_text=extract_text(text_body, '{themes}',index0=1)

    json_questions={}

    if len(themes)!=0: 
        for theme in themes:

                # print('{'+theme+'}')
                # print(theme_questions_text.split('{'+theme+'}')[0])

                text_theme=theme_questions_text.split('{'+theme+'}')[0]
                json_questions[theme]=questions_theme_text_dict(text_theme)

                # print(text_theme+'{'+theme+'}', '\n\n\n\n\n\n')

                theme_questions_text=theme_questions_text.replace(text_theme+'{'+theme+'}', '')
                # print(len(theme_questions_text))
            
    return json_questions

     
def extractor_json( origin_dir, output_dir):
    for root, dirnames,files in os.walk(origin_dir):
        for file in files:
            global name_file
            name_file=file
            if file.endswith('.docx'):
                final_json={}
                doc= Document(f'{root}/{file}')
                text_docx='\n'.join([parrafo.text for parrafo in doc.paragraphs])
                title=get_title(text_docx)
                body=get_body(text_docx)
                themes=get_themes(body)
                questions=get_questions(body, themes)
                final_json['title']=title
                final_json['themes']=themes
                final_json['questions']=questions

                path_final=os.path.join(output_dir,f'{file.replace('.docx', '')}.json')
                with open(path_final, 'w', encoding='UTF-8') as f:
                    json.dump(final_json,f,ensure_ascii=False, indent=2)