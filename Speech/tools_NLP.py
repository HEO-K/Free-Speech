import numpy as np
import os


def load_stopword(input_list=None):
    """ 불용어 불러오기

    Args:
        input_list (_list_): 추가할 불용어, [["단어","품사"]]
        
    Returns
        list: [단어, 품사]가 들어있는 리스트
    """
    # get information
    script_path = __file__
    if __file__[0] == "/":
        # linux
        script_path = "/".join(script_path.split("/")[:-1])
        file_path = os.path.join(script_path,"/_data_NLP/stopwords.txt")[0]
    else:
        # window
        script_path = "\\".join(script_path.split("\\")[:-1])
        file_path = script_path+"/_data_NLP/stopwords.txt"

    stopwords_f = open(file_path, 'r', encoding="utf-8")

    stopwords_list = stopwords_f.readlines()
    stopwords_f.close()
    stopwords = []
    for words in stopwords_list:
        words = words.replace("\n", '')
        stopwords.append(words.split('/'))
    if input_list:
        for words in input_list: stopwords.append([words[0], words[1]])
    return(stopwords)


#  구어 태깅
def etri_spokentagger(input, wordlevel=False, stopwords=True):
    """_ETRI 구어 태깅_

    Args:
        input (_str_): 텍스트
        wordlevel (_bool_,optional): 단어 구분의 return 여부
            - Defaults to False, 형태소 구분
            - True: 형태소를 단어 리스트로 (자동으로 불용어 처리 안됨)
        stopwords (_bool_,optional): 불용어 제외 여부
            - Defaults to True, 기본 불용어 (load_stopword)
            - False: 하지 않음
            - list: [["단어", "품사]] 형태의 커스텀 불용어
            
    Returns: 
        문장으로 나뉜 리스트
    """
    import urllib3
    import json
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU_spoken"
    accessKey = "9d3f4f60-ac44-43c9-9ae4-a3df0ee86686"  # 개인 accessKey
    analysisCode = "morp"
    requestJson = {
    "argument": {
        "text": input,
        "analysis_code": analysisCode
        }
    }
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        openApiURL,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization" :  accessKey},
        body=json.dumps(requestJson)
    )

    results = response.data.decode('utf-8')
    results = json.loads(results)['return_object']['sentence']
    tagged_results = []
    
    
    # 불용어 불러오기
    if not wordlevel:
        if stopwords:
            stopwords_list = load_stopword()
            stopword_tag = []
            for word in stopwords_list:
                if not word[0]: stopword_tag.append(word[1])
    
    # 결과값 저장
    for sent_result in results:
        sentence = []  
        if wordlevel:
            for word in sent_result['morp_eval']:
                word_tag = word['result']
                word_tag = word_tag.split("+")
                word_res = []
                for word in word_tag:
                    word_res.append(word.split("/"))
                sentence.append(word_res)
            tagged_results.append(sentence)   
        else:
            for word in sent_result['morp']:
                if stopwords:
                    if word['type'] in stopword_tag: pass
                    elif [word['lemma'], word['type']] in stopwords_list: pass
                    else: sentence.append([word['lemma'], word['type']])
                else: sentence.append([word['lemma'], word['type']])
            tagged_results.append(sentence)   
    return(tagged_results)
