import numpy as np
import os
import urllib3
import json
import time
from .tools import isWSL


def _etri_access_key():
    """ ETRI OpenAPI accessKey를 환경변수에서 읽는다.

        코드에 키를 적어 두지 않기 위한 것이다. 사용자 환경변수에 한 번만
        등록해 두면 이후로는 아무것도 입력할 필요가 없다.

            ETRI_ACCESS_KEY : aiopen.etri.re.kr에서 발급받은 개인 accessKey

        Windows에서 등록하는 법 (PowerShell, 한 번만 실행):
            [Environment]::SetEnvironmentVariable('ETRI_ACCESS_KEY','<KEY>','User')

        WSL에서도 쓰려면 Windows 사용자 환경변수 WSLENV에
        'ETRI_ACCESS_KEY/u' 를 추가해 두면 그대로 전달된다.

        Returns:
            str: accessKey
    """

    key = os.environ.get("ETRI_ACCESS_KEY")
    if not key:
        raise RuntimeError(
            "ETRI accessKey가 환경변수에 없습니다: ETRI_ACCESS_KEY\n"
            "등록 방법은 Speech/tools_NLP.py의 _etri_access_key() "
            "docstring을 참고하세요.\n"
            "이미 등록했다면 VS Code나 터미널을 껐다 켜야 새 환경변수가 반영됩니다."
        )
    return key


def _split_text(text, limit=5000):
    """ ETRI 요청 한도(5000자)에 맞춰 텍스트를 문장(". ") 단위로 이어 붙인 덩어리 리스트로.
    각 덩어리는 문장 경계에서만 끊기고, 마침표는 유지된다. """
    text = text.strip()
    if text.endswith("."): text = text[:-1]
    chunks, cur = [], ""
    for sent in text.split(". "):
        piece = sent + ". "
        if cur and len(cur) + len(piece) > limit:
            chunks.append(cur.strip())
            cur = ""
        cur += piece
    if cur.strip(): chunks.append(cur.strip())
    return chunks


def _etri_request(url, analysis_code, text):
    """ ETRI OpenAPI 한 번 호출 → return_object['sentence'] 리스트. 실패하면 응답을 담아 RuntimeError.
    (예전엔 print 만 하고 빈 결과를 정상처럼 돌려줬다 — 키 오류·쿼터 초과가 빈 태깅으로 둔갑했다) """
    http = urllib3.PoolManager()
    response = http.request(
        "POST", url,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": _etri_access_key()},
        body=json.dumps({"argument": {"text": text, "analysis_code": analysis_code}}),
    )
    body = response.data.decode("utf-8")
    try:
        parsed = json.loads(body)
        sentences = parsed["return_object"]["sentence"]
    except (ValueError, KeyError, TypeError):
        raise RuntimeError(f"ETRI {analysis_code} request failed (HTTP {response.status}): {body[:500]}")
    time.sleep(0.2)     # 너무 빠르게 돌리면 오류뜸
    return sentences


def load_stopword(input_list=None):
    """ 불용어 불러오기

    Args:
        input_list (list): 추가할 불용어, [["단어","품사"]]
        
    Returns
        list: [단어, 품사]가 들어있는 리스트
    """
    # get information
    script_path = __file__

    if isWSL():
        # linux
        script_path = "/".join(script_path.split("/")[:-1])
        file_path = os.path.join(script_path,"_data_NLP/stopwords.txt")
    else:
        # window
        script_path = "\\".join(script_path.split("\\")[:-1])
        file_path = script_path+".\\_data_NLP\\stopwords.txt"

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
    """ ETRI 구어 태깅

    Args:
        input (str): 텍스트
        wordlevel (bool,optional): 단어 구분의 return 여부
            - Defaults to False, 형태소 구분
            - True: 형태소를 단어 리스트로
        stopwords (bool,optional): 불용어 제외 여부
            - Defaults to True, 기본 불용어 (load_stopword)
            - False: 하지 않음
            - list: [["단어", "품사]] 형태의 커스텀 불용어
            
    Returns: 
        문장으로 나뉜 리스트
    """
    
    
    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU_spoken"

    # 5000자 한도에 맞춘 덩어리마다 한 번씩 요청 (예전엔 덩어리를 만들어 놓고 문장마다 요청해
    # 문장 수만큼 쿼터를 썼고, 각 문장이 마침표 없이 전송됐다)
    results = []
    for chunk in _split_text(input):
        results += _etri_request(openApiURL, "morp", chunk)
    tagged_results = []
    
    
    # 불용어 불러오기
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
                    if stopwords:
                        if not word.split("/")[1] in stopword_tag:
                            if not word.split("/") in stopwords_list:
                                word_res.append(word.split("/"))
                    else: word_res.append(word.split("/"))
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




# 의존구문분석
def etri_dparse(input):
    """ 문장의 의존구조를 분석해서 그 결과를 출력

    Args:
        input (str): 입력 텍스트

    Returns:
        list: 의존구조 분석 결과
    """


    openApiURL = "http://aiopen.etri.re.kr:8000/WiseNLU"

    results = []
    for chunk in _split_text(input):
        results += _etri_request(openApiURL, "dparse", chunk)

    return results



def get_NSP(text, model_name='klue/bert-base', raw=False):
    """ Get next sentence prediction score

    Args:
        text (1d list of strings): list of sentences
        model_name (str, optional): name of the model. Default to 'klue/bert-base'
        raw (bool, optional): get raw NSP. Default to False

    Returns:
        array (n): NSP score
    """
    
        
    import tensorflow as tf
    from transformers import TFBertForNextSentencePrediction
    from transformers import AutoTokenizer
    
    model = TFBertForNextSentencePrediction.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    
    next_sentence_probs = []
    for i in range(len(text)-1):
        encoding = tokenizer(text[i], text[i+1], return_tensors='tf')
        logits = model(encoding['input_ids'], token_type_ids=encoding['token_type_ids'])[0]
        softmax = tf.keras.layers.Softmax()
        probs = softmax(logits)
        if raw:
            next_sentence_probs.append(logits.numpy()[0,0])
        else:
            next_sentence_probs.append(np.squeeze(probs.numpy())[0])
        
    return(np.array([float(n) for n in next_sentence_probs]))


def get_NSP_embedding(text, model_name='klue/bert-base', layer=13):
    """ Get next sentence prediction embedding (hidden state of [CLS] token)

    Args:
        text (1d list of strings): list of sentences
        model_name (str, optional): name of the model. Default to 'klue/bert-base'

    Returns:
        array (n, dim): NSP embedding
    """
                
    import tensorflow as tf
    from transformers import TFBertForNextSentencePrediction
    from transformers import AutoTokenizer
    
    
    
    model = TFBertForNextSentencePrediction.from_pretrained(model_name, output_hidden_states=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    
    embeds = []
    for i in range(len(text)-1):
        encoding = tokenizer(text[i], text[i+1], return_tensors='tf')
        logits = model(encoding['input_ids'], token_type_ids=encoding['token_type_ids'])[1][layer-1]
        
        embedding = logits.numpy()[0,0,:]
        embeds.append(embedding)

    return(np.array(embeds))



def get_sentence_embedding(text, model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
    """ Get sentence embedding by sentence transformer

    Args:
        text (str list): list of sentences
        model_name (str, optional): name of the model. Defaults to 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'.

    Returns:
        array (n, dim): sentence embedding
    """
    
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    embeddings = model.encode(text)
    
    return embeddings
