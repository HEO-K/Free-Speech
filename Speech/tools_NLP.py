import numpy as np
import os
import urllib3
import json
import time
from .tools import isWSL

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
    accessKey = "9d3f4f60-ac44-43c9-9ae4-a3df0ee86686"  # 개인 accessKey
    analysisCode = "morp"
    
    
    # 만약 글자수가 5000자 이상이면, 여러번 나눠서 해야 한다. 문장(온점, ". ") 단위로 쪼갠다.
    input_sent = input.split(". ")
    sent_tmp = ''
    input_split = []
    for sent in input_sent:
        if len(sent_tmp)+len(sent)>5000:
            input_split.append(sent_tmp)
            sent_tmp = sent+". "
        else: sent_tmp = sent_tmp+sent+". "
    input_split.append(sent_tmp)
    
    
    results = []
    for sent in input_sent:
        requestJson = {
        "argument": {
            "text": sent,
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

        response_results = response.data.decode('utf-8')
        try:
            results = results + json.loads(response_results)['return_object']['sentence']
        except: print(json.loads(response_results))
        time.sleep(0.2)
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
    accessKey = "9d3f4f60-ac44-43c9-9ae4-a3df0ee86686"  # 개인 accessKey
    analysisCode = "dparse"


    # 만약 글자수가 5000자 이상이면, 여러번 나눠서 해야 한다. 문장(온점, ". ") 단위로 쪼갠다.
    input_sent = input.split(". ")
    sent_tmp = ''
    input_split = []
    for sent in input_sent:
        if len(sent_tmp)+len(sent)>5000:
            input_split.append(sent_tmp)
            sent_tmp = sent+". "
        else: sent_tmp = sent_tmp+sent+". "
    input_split.append(sent_tmp)
    
    
    # 나눠진 문장마다 돌린다.
    results = []
    for sent in input_sent:
        requestJson = {
        "argument": {
            "text": sent,
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

        response_results = response.data.decode('utf-8')
        try:
            results = results + json.loads(response_results)['return_object']['sentence']
        except: print(json.loads(response_results))
        
        # 너무 빠르게 돌리면 오류뜸
        time.sleep(0.2)
    
    return results 





# 키워드 추출 모델
def keyword_extraction(model, input_lines:list, filtered_lines:list, 
                    min_n:int, max_n:int, top_keywords:int, diversity=0.5,
                     print_keywords=True):
    """ 문장의 키워드 추출

    Args:
        input_lines (list): 원 문장의 리스트 ["문장", ...]
        filtered_lines (list): 키워드를 구성할 때 사용할 형태소 리스트 ["형태소들",...]
        min_n (int): 키워드(구)를 구성하는 최소 단어수
        max_n (int): 키워드(구)를 구성하는 최대 단어수
        top_keywords (int): 뽑을 키워드 개수
        diversity (float, optional): MMR(다양한 키워드가 뽑히는 정도, 0~1). Default to 0.5

    Returns:
        list: 각 문장마다 [키워드, 스코어]
    """
    
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    
    # 키워드 찾기
    results = []
    n_gram_range = (min_n, max_n)  # 키워드(구)를 만들 수 있는 단어 개수
    key_embed = np.empty((0,768))
    for i in range(len(filtered_lines)):
        if len(filtered_lines[i]) == 0:
            if print_keywords: print("no candidate, just return NO keyword")
            result = []
            for n in range(top_keywords):
                result.append(["", 0])
        else:
            count = CountVectorizer(ngram_range=n_gram_range).fit([" ".join(set(filtered_lines[i]))]) 
            candidates = count.get_feature_names_out()  # 모든 단어 조합 -> keyword candidate
            doc_embedding = model.encode(input_lines[i])  # 원본 문장 embedding
            candidate_embeddings = model.encode(candidates)   # keyword candidate embedding
            word_doc_sim = cosine_similarity(candidate_embeddings,
                                            doc_embedding.reshape(1,768))  # 키워드 후보 & 원문의 유사도
            word_word_sim = cosine_similarity(candidate_embeddings)  # 키워드 후보 끼리의 유사도
            
            
            # Maximum Limit Relegance로 키워드를 다양화
            # top n개의 키워드를 쓰면 지나치게 유사한 키워드들만 추출된다.
            keywords_idx = [np.argmax(word_doc_sim)]  # 최고의 키워드
            # 위를 제외한 나머지
            candidates_idx = [n for n in range(len(candidate_embeddings)) if n != keywords_idx[0]]
            # 키워드-1 만큼 최고의 키워드 찾는 것 반복
            for _ in range(top_keywords - 1):
                try:
                    candidate_similarities = word_doc_sim[candidates_idx, :]
                    target_similarities = np.max(word_word_sim[candidates_idx][:, keywords_idx], axis=1)
                    mmr = (1-diversity) * candidate_similarities - diversity * target_similarities.reshape(-1,1)
                    mmr_idx = candidates_idx[np.argmax(mmr)]
                    keywords_idx.append(mmr_idx)
                    candidates_idx.remove(mmr_idx)
                except:
                    pass
        
            # 유사도 높은 top n개의 키워드
            keyword = candidates[keywords_idx]
            if print_keywords: print(keyword)
            
            
            # 그 유사도 값
            score = np.array(word_doc_sim[keywords_idx])
            # score = score/(np.mean(score)*len(score))  # [1,1,3] -> [0.2,0.2,0.6]
            
            result = []
            for n in range(top_keywords):
                try: result.append([keyword[n], score[n][0]])
                except: result.append(["", 0])
                
            

        results.append(np.array(result, dtype='object'))
        
        
    return results