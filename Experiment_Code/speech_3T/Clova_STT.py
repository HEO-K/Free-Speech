# %%
import argparse   	# 내장모듈

def main(filelocate, filename):
    import requests
    import json

    invoke_url = 'https://clovaspeech-gw.ncloud.com/external/v1/2227/2752bda02f64f65c39aef44ddfe935dd3a6a7c9c061e687484f67707ee3f975c'
    secret = '03bbf8f1bea54866bbd108c26845160e'

    def req_upload(file, completion='sync', callback=None, userdata=None, forbiddens=None, boostings=None,wordAlignment=True, fullText=True, diarization=None):
        request_body = {
            'language': 'ko-KR',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': secret
        }
        print("Post request")
        files = {
            'media': open(file, 'rb'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=invoke_url + '/recognizer/upload', files=files)
        return response

    results = req_upload(filelocate+filename).text
    if results: print("Finished")
    results = json.loads(results)
    sentences = results['segments']
    full_text = results['text']

    # FA = sentences[0]['words']
    # for i in range(1,len(sentences)):
    #    FA = FA + sentences[i]['words']

    f_stt = open(filelocate+filename[:-4]+"_STT.txt", 'w')
    f_stt.write(full_text)
    f_stt.close()
    # f_FA = open(filelocate+filename[:-4]+"_FA.txt", 'w')
    # for i in range(len(FA)):
    #     f_FA.write('{0:<8}{1:<8}{2}\n'.format(FA[i][0], str(FA[i][1]), str(FA[i][2])))
    # f_FA.close()

    
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(nargs='+' ,help=': [path] [filename]', dest='filepath')

    filename_list = parser.parse_args().filepath
    filelocate = filename_list[0]
    filename = filename_list[1]
    return filelocate, filename


if __name__ == '__main__':
    filelocate, filename = get_arguments()
    main(filelocate, filename)


