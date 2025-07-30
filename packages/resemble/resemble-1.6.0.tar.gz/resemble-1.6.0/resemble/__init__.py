import requests
from typing import List, Union
import time


from resemble.stream_decoder import StreamDecoder

V2_STREAMING_BUFFER_SIZE = 4 * 1024
V2_STREAMING_CHUNK_SIZE = 2

class Resemble:
    """
    Resemble - A Python library for interacting with the Resemble AI API.

    This library contains various functions and classes for making requests 
    to the Resemble AI platform.

    Email: team@resemble.ai
    """
    _token = None
    _base_url = 'https://app.resemble.ai/api/'
    _headers = { 'Content-Type': 'application/json', 'Authorization': f"Token token={_token}" }

    _syn_server_url = None
    _syn_server_headers = { 'Content-Type': 'application/json', 'x-access-token': f"{_token}" }

    _direct_syn_server_url = 'https://f.cluster.resemble.ai/synthesize'
    _direct_syn_server_headers =  { "Authorization": f"Bearer {_token}", "Content-Type": "application/json", "Accept-Encoding": "gzip" }

    @staticmethod
    def api_key(api_key):
        """
        Sets the API Key for the class instance usage

        Args:
            api_key (str): The API Key to set found at https://app.resemble.ai/account/api

        Returns:
            None
        """
        Resemble._token = api_key
        Resemble._headers['Authorization'] = f"Token token={Resemble._token}"
        Resemble._syn_server_headers['x-access-token'] = f"{Resemble._token}"
        Resemble._direct_syn_server_headers['Authorization'] = f"Bearer {Resemble._token}"

    @staticmethod
    def base_url(url):
        Resemble._base_url = url

    @staticmethod
    def endpoint(version, endpoint):
        api_endpoint = endpoint if endpoint.startswith('/') else f"/{endpoint}"
        return f"{Resemble._base_url}{version}{api_endpoint}"

    @staticmethod
    def syn_server_url(url):
        url = url if url.endswith('/') else f"{url}/"
        Resemble._syn_server_url = url

    @staticmethod
    def syn_server_endpoint(endpoint):
        if Resemble._syn_server_url is None:
            raise ValueError("Please initialize the synthesis server url by calling Resemble.syn_server_url before "
                             "using the streaming API. If you're not sure what your streaming URL is, "
                             "please contact team@resemble.ai. The Streaming API is currently in beta and is not "
                             "available to all users. Please reach out to team@resemble.ai to inquire more.")
        api_endpoint = endpoint[:-1] if endpoint.startswith('/') else endpoint
        return f"{Resemble._syn_server_url}{api_endpoint}"
    
    @staticmethod
    def direct_syn_server_url(url):
        Resemble._direct_syn_server_url = url

    class _V2:
        class _PhonemesV2:
            def all(self, page: int, page_size: int = None):
                """
                Retrieves all phonemes: https://docs.app.resemble.ai/docs/resource_phonemes/resource 
                Args:
                    page (str): The page number to retrieve
                    page_size (str): The number of items to retrieve per page

                Returns:
                    dict: JSON dictionary of the response
                """
                query = { 'page': page }
                if page_size:
                    query['page_size'] = page_size
                r = requests.get(Resemble.endpoint('v2', f"phonemes"), headers=Resemble._headers, params=query)
                return r.json()

            def create(self, word: str, phonetic_transcription: str):
                """
                Creates a new phoneme: https://docs.app.resemble.ai/docs/resource_phonemes/create 

                Args:
                    word (str): text being transcribed e.g pressure
                    phonetic_transcription (str):IPA transcription e.g ˈprɛʃər

                Returns:
                    dict: a JSON dictionary containing the reponse
                """
                options = {k: v for k, v in ({
                    'word': word,
                    'phonetic_transcription': phonetic_transcription,
                }).items() if v is not None}

                r = requests.post(Resemble.endpoint('v2', f"phonemes"), headers=Resemble._headers, json=options)
                return r.json()

            def delete(self, phoneme_uuid: str):
                """
                Deletes a phoneme by UUID: https://docs.app.resemble.ai/docs/resource_phonemes/delete 

                Args:
                    phoneme_uuid (str): UUID of the phoneme to remove

                Returns:
                    dict: JSON dictionary of the response
                """
                r = requests.delete(Resemble.endpoint('v2', f"phonemes/{phoneme_uuid}"), headers=Resemble._headers)
                return r.json()

        class _TermSubstitutionV2:
            def all(self, page: int, page_size: int = None):
                """
                Retrieves all term substitution: https://docs.app.resemble.ai/docs/resource_term_substitutions/resource 
                Args:
                    page (int): The page number to retrieve
                    page_size (int): The number of items to retrieve per page

                Returns:
                    dict: JSON dictionary of the response
                """
                query = { 'page': page }
                if page_size:
                    query['page_size'] = page_size
                r = requests.get(Resemble.endpoint('v2', f"term_substitutions"), headers=Resemble._headers, params=query)
                return r.json()

            def create(self, original_text: str, replacement_text: str):
                """
                Creates a new term substitution: https://docs.app.resemble.ai/docs/resource_term_substitutions/create 

                Args:
                    original_text (str): text being replaced e.g Vodaphone
                    replacement_text (str): text being replaced e.g Voduhphone

                Returns:
                    dict: a JSON dictionary containing the reponse
                """
                options = {k: v for k, v in ({
                    'original_text': original_text,
                    'replacement_text': replacement_text,
                }).items() if v is not None}

                r = requests.post(Resemble.endpoint('v2', f"term_substitutions"), headers=Resemble._headers, json=options)
                return r.json()

            def delete(self, term_substitution_uuid: str):
                """
                Deletes a term substitution by UUID: https://docs.app.resemble.ai/docs/resource_term_substitutions/delete 

                Args:
                    term_substitution_uuid (str): UUID of the project to which the batch belongs

                Returns:
                    dict: JSON dictionary of the response
                """
                r = requests.delete(Resemble.endpoint('v2', f"term_substitutions/{term_substitution_uuid}"), headers=Resemble._headers)
                return r.json()

        class _BatchesV2:
            def all(self, project_uuid: str, page: int, page_size: int = None):
                """
                Retrieves all Batchs: https://docs.app.resemble.ai/docs/resource_batch/one 

                Args:
                    project_uuid (str): UUID of the project to which the batch belongs
                    page (int): The page number to retrieve
                    page_size (int): The number of items to retrieve per page

                Returns:
                    dict: JSON dictionary of the response
                """
                query = { 'page': page }
                if page_size:
                    query['page_size'] = page_size
                r = requests.get(Resemble.endpoint('v2', f"projects/{project_uuid}/batch"), headers=Resemble._headers, params=query)
                return r.json()

            def get(self, project_uuid: str, batch_uuid: str):
                """
                Retrieves a Batch by UUID: https://docs.app.resemble.ai/docs/resource_batch/one 

                Args:
                    project_uuid (str): UUID of the project to which the batch belongs
                    batch_uuid (str): UUID of the batch to fetch

                Returns:
                    dict: JSON dictionary of the response
                """

                r = requests.get(Resemble.endpoint('v2', f"projects/{project_uuid}/batch/{batch_uuid}"), headers=Resemble._headers)
                return r.json()

            def create(self, project_uuid: str, voice_uuid: str, body: Union[List[str], List[List[str]]], callback_uri: str = None, sample_rate: int = None, precision: str = None, output_format: str = None):
                """
                Creates a new Batch request: https://docs.app.resemble.ai/docs/resource_batch/create 

                Args:
                    project_uuid (str): UUID of the project to which the clip should belong
                    voice_uuid (str): UUID of the voice to use for synthesizing
                    body (string[] or string[string[]]): An array of strings where each string is content to be synthesized (this can be raw text or ssml) or an array of arrays where each element in the nested array conforms to the shape of ["title", "ssml"]
                    callback_uri (str): The URL to POST the result of the batch to.
                    sample_rate (int): The sample rate (Hz) of the generated audio
                    precision (str): The audio bit depth of generated audio
                    output_format (str): The format of the generated audio

                Returns:
                    dict: a JSON dictionary containing the reponse
                """
                options = {k: v for k, v in ({
                    'voice_uuid': voice_uuid,
                    'body': body,
                    'sample_rate': sample_rate,
                    'output_format': output_format,
                    'precision': precision,
                }).items() if v is not None}

                if callback_uri:
                    options['callback_uri'] = callback_uri

                r = requests.post(Resemble.endpoint('v2', f"projects/{project_uuid}/batch"), headers=Resemble._headers, json=options)
                return r.json()

            def delete(self, project_uuid: str, batch_uuid):
                """
                Deletes a Batch by UUID: https://docs.app.resemble.ai/docs/resource_batch/delete 

                Args:
                    project_uuid (str): UUID of the project to which the batch belongs
                    batch_uuid (str): UUID of the batch to delete

                Returns:
                    dict: JSON dictionary of the response
                """
                r = requests.delete(Resemble.endpoint('v2', f"projects/{project_uuid}/batch/{batch_uuid}"), headers=Resemble._headers)
                return r.json()

        class _ProjectsV2:
            def all(self, page: int, page_size: int = None):
                query = { 'page': page }
                if page_size:
                    query['page_size'] = page_size
                r = requests.get(Resemble.endpoint('v2', 'projects'), headers=Resemble._headers, params=query)
                return r.json()

            def create(self, name: str, description: str, is_collaborative: bool = False, is_archived: bool = False):
                r = requests.post(Resemble.endpoint('v2', 'projects'), headers=Resemble._headers, json={
                    'name': name,
                    'description': description,
                    'is_collaborative': is_collaborative,
                    'is_archived': is_archived
                })
                return r.json()

            def update(self, uuid: str, name: str, description: str, is_collaborative: bool = False, is_archived: bool = False):
                r = requests.put(Resemble.endpoint('v2', f"projects/{uuid}"), headers=Resemble._headers, json={
                    'name': name,
                    'description': description,
                    'is_collaborative': is_collaborative,
                    'is_archived': is_archived
                })
                return r.json()

            def get(self, uuid: str):
                r = requests.get(Resemble.endpoint('v2', f"projects/{uuid}"), headers=Resemble._headers)
                return r.json()

            def delete(self, uuid: str):
                r = requests.delete(Resemble.endpoint('v2', f"projects/{uuid}"), headers=Resemble._headers)
                return r.json()

        class _VoicesV2:
            def all(self, page: int, page_size: int = None, sample_url: bool = None, filters: bool = None):
                query = { 'page': page }
                if page_size:
                    query['page_size'] = page_size
                if sample_url:
                    query['sample_url'] = sample_url
                if filters:
                    query['filters'] = filters
                r = requests.get(Resemble.endpoint('v2', 'voices'), headers=Resemble._headers, params=query)
                return r.json()

            def create(self, name: str, consent: str, dataset_url: str = None, callback_uri: str = None,
                       voice_type: str = 'professional'):
                json = {
                    'name': name,
                    'consent': consent
                }
                if dataset_url:
                    json['dataset_url'] = dataset_url
                if callback_uri:
                    json['callback_uri'] = callback_uri
                if voice_type:
                    json['voice_type'] = voice_type
                r = requests.post(Resemble.endpoint('v2', 'voices'), headers=Resemble._headers, json=json)
                return r.json()

            def update(self, uuid: str, name: str, dataset_url: str = None):
                json = {
                    'name': name
                }
                if dataset_url:
                    json['dataset_url'] = dataset_url
                r = requests.put(Resemble.endpoint('v2', f"voices/{uuid}"), headers=Resemble._headers, json=json)
                return r.json()
                
            def build(self, uuid: str, fill=False):
                json = {
                    'fill': fill
                }
                r = requests.post(Resemble.endpoint('v2', f"voices/{uuid}/build"), headers=Resemble._headers, json=json)
                return r.json()

            def get(self, uuid: str, sample_url: bool = None, filters: bool = None):
                query = {}
                if sample_url:
                    query['sample_url'] = sample_url
                if filters:
                    query['filters'] = filters
                r = requests.get(Resemble.endpoint('v2', f"voices/{uuid}"), headers=Resemble._headers, params=query)
                return r.json()

            def delete(self, uuid: str):
                r = requests.delete(Resemble.endpoint('v2', f"voices/{uuid}"), headers=Resemble._headers)
                return r.json()

        class _ClipsV2:
            def all(self, project_uuid: str, page: int, page_size: int = None):
                query = { 'page': page }
                if page_size:
                    query['page_size'] = page_size
                r = requests.get(Resemble.endpoint('v2', f"projects/{project_uuid}/clips"), headers=Resemble._headers, params=query)
                return r.json()

            def create_sync(self, project_uuid: str, voice_uuid: str, body: str, title: str = None, sample_rate: int = None, output_format: str = None, precision: str = None, include_timestamps: bool = None, is_archived: bool = None, raw: bool = None):
                options = {k: v for k, v in ({
                    'voice_uuid': voice_uuid,
                    'body': body,
                    'title': title,
                    'sample_rate': sample_rate,
                    'output_format': output_format,
                    'precision': precision,
                    'include_timestamps': include_timestamps,
                    'is_archived': is_archived,
                    'raw': raw
                }).items() if v is not None}

                r = requests.post(Resemble.endpoint('v2', f"projects/{project_uuid}/clips"), headers=Resemble._headers, json=options)
                return r.json()

            def create_async(self, project_uuid: str, voice_uuid: str, callback_uri: str, body: str, title: str = None, sample_rate: int = None, output_format: str = None, precision: str = None, include_timestamps: bool = None, is_archived: bool = None):
                options = {k: v for k, v in ({
                    'voice_uuid': voice_uuid,
                    'body': body,
                    'title': title,
                    'sample_rate': sample_rate,
                    'output_format': output_format,
                    'precision': precision,
                    'include_timestamps': include_timestamps,
                    'is_archived': is_archived,
                    'callback_uri': callback_uri
                }).items() if v is not None}

                r = requests.post(Resemble.endpoint('v2', f"projects/{project_uuid}/clips"), headers=Resemble._headers, json=options)
                return r.json()

            def update_async(self, project_uuid: str, clip_uuid: str, voice_uuid: str, callback_uri: str, body: str, title: str = None, sample_rate: int = None, output_format: str = None, precision: str = None, include_timestamps: bool = None, is_archived: bool = None):
                options = {k: v for k, v in ({
                    'voice_uuid': voice_uuid,
                    'body': body,
                    'title': title,
                    'sample_rate': sample_rate,
                    'output_format': output_format,
                    'precision': precision,
                    'include_timestamps': include_timestamps,
                    'is_archived': is_archived,
                    'callback_uri': callback_uri
                }).items() if v is not None}
                
                r = requests.put(Resemble.endpoint('v2', f"projects/{project_uuid}/clips/{clip_uuid}"), headers=Resemble._headers, json=options)
                return r.json()

            def create_direct(self, project_uuid: str, voice_uuid: str, data: str, title: str = None, precision: str = None, output_format: str = None, sample_rate: int = None):            
                options = {k:v for k, v in ({
                    'voice_uuid': voice_uuid,
                    'project_uuid': project_uuid,
                     'data': data,
                    'title': title,
                    'precision': precision,
                    'output_format': output_format,
                    'sample_rate': sample_rate
                }).items() if v is not None}
                r = requests.post(Resemble._direct_syn_server_url, headers=Resemble._direct_syn_server_headers, json=options)
                return r.json()

            def stream(self, project_uuid: str, voice_uuid: str, body: str, buffer_size: int = V2_STREAMING_BUFFER_SIZE, ignore_wav_header=True, sample_rate=None):
                options = {
                    "project_uuid": project_uuid,
                    "voice_uuid": voice_uuid,
                    "data": body,
                    "precision": "PCM_16" # Do not change - output will sound like static noise otherwise.
                }
                if sample_rate:
                    options["sample_rate"] = sample_rate

                r = requests.post(Resemble.syn_server_endpoint('stream'), headers=Resemble._syn_server_headers, json=options, stream=True)
                r.raise_for_status()
                stream_decoder = StreamDecoder(buffer_size, ignore_wav_header)
                # Iterate over the stream and start decoding, and returning data
                for chunk in r.iter_content(chunk_size=V2_STREAMING_CHUNK_SIZE):
                    if chunk:
                        stream_decoder.decode_chunk(chunk)
                        buffer = stream_decoder.flush_buffer()
                        if buffer:
                            yield buffer

                # Keep draining the buffer until the len(buffer) < buffer_size or len(buffer) == 0
                buffer = stream_decoder.flush_buffer()
                while buffer is not None:
                    buff_to_return = buffer
                    buffer = stream_decoder.flush_buffer()
                    yield buff_to_return

                # Drain any leftover content in the buffer, len(buffer) will always be less than buffer_size here
                buffer = stream_decoder.flush_buffer(force=True)
                if buffer:
                    yield buffer

            def get(self, project_uuid: str, clip_uuid: str):
                r = requests.get(Resemble.endpoint('v2', f"projects/{project_uuid}/clips/{clip_uuid}"), headers=Resemble._headers)
                return r.json()

            def delete(self, project_uuid: str, clip_uuid: str):
                r = requests.delete(Resemble.endpoint('v2', f"projects/{project_uuid}/clips/{clip_uuid}"), headers=Resemble._headers)
                return r.json()

        class _RecordingsV2:
            def all(self, voice_uuid: str, page: int, page_size: int = None):
                query = { 'page': page }
                if page_size:
                    query['page_size'] = page_size
                r = requests.get(Resemble.endpoint('v2', f"voices/{voice_uuid}/recordings"), headers=Resemble._headers, params=query)
                return r.json()

            def create(self, voice_uuid: str, file, name: str, text: str, is_active: bool, emotion: str, fill: bool = False):
                r = requests.request(
                    "POST",
                    Resemble.endpoint('v2', f"voices/{voice_uuid}/recordings"),
                    headers={'Authorization': Resemble._headers['Authorization']},
                    data={
                        'emotion': emotion,
                        'is_active': ("true" if is_active else "false"),
                        'name': name,
                        'fill': ("true" if fill else "false"),
                        'text': text
                    },
                    files={
                        'file': file,
                    }
                )
                return r.json()

            def update(self, voice_uuid: str, recording_uuid: str, name: str, text: str, is_active: bool, emotion: str, fill: bool = False):
                r = requests.put(Resemble.endpoint('v2', f"voices/{voice_uuid}/recordings/{recording_uuid}"), headers=Resemble._headers, json={
                    'name': name,
                    'text': text,
                    'is_active': is_active,
                    'emotion': emotion,
                    'fill': fill
                })
                return r.json()

            def get(self, voice_uuid: str, recording_uuid: str):
                r = requests.get(Resemble.endpoint('v2', f"voices/{voice_uuid}/recordings/{recording_uuid}"), headers=Resemble._headers)
                return r.json()

            def delete(self, voice_uuid: str, recording_uuid: str):
                r = requests.delete(Resemble.endpoint('v2', f"voices/{voice_uuid}/recordings/{recording_uuid}"), headers=Resemble._headers)
                return r.json()

        class _EditsV2:
            def all(self, page: int):
                query = { 'page': page }
                r = requests.get(Resemble.endpoint('v2', 'edit'), headers=Resemble._headers, params=query)
                return r.json()

            def get(self,  uuid: str):
                r = requests.get(Resemble.endpoint('v2', f"edit/{uuid}"), headers=Resemble._headers)
                return r.json()

            def create(self, original_transcript: str, target_transcript: str, voice_uuid: str, file):
                headers={'Authorization': Resemble._headers['Authorization']},
                data = {
                    'original_transcript': original_transcript,
                    'target_transcript': target_transcript,
                    'voice_uuid': voice_uuid
                }
                files = {
                    'input_audio': file
                }
                r = requests.request(
                    'POST',
                    Resemble.endpoint('v2', 'edit'), 
                    headers={'Authorization': Resemble._headers['Authorization']},
                    data=data,
                    files=files)
                return r.json()

            def create_and_get(self,  original_transcript: str, target_transcript: str, voice_uuid: str, file, retries = 10, wait_time = 3):
                """
                This function creates an audio edit and then poll until the result_audio_url is in the response or until the max number of retries is exceeded.
                """
                create_r = self.create(original_transcript, target_transcript, voice_uuid, file)
                if create_r['success'] is True:
                    edit_uuid = create_r['item']['uuid']
                    for i in range(retries):
                        time.sleep(wait_time)
                        get_r = self.get(edit_uuid)
                        if 'result_audio_url' in get_r['item'] and get_r['item']['result_audio_url']:
                            #return the Audio Edit with the result_audio_url when the result_audio_url is present
                            return get_r
                    # return the API response to the Create request if the Audio Edit is not done processing after the max number of retries
                    return create_r
                else:
                    # return the API response to the Create request if the request was not successful
                    return create_r

        projects = _ProjectsV2()
        clips = _ClipsV2()
        voices = _VoicesV2()
        recordings = _RecordingsV2()
        batches = _BatchesV2()
        term_substitutions = _TermSubstitutionV2()
        phonemes = _PhonemesV2()
        edits = _EditsV2()

    v2 = _V2()

