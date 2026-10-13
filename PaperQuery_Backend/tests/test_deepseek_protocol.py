import importlib
import json
import httpx
from langchain_openai import ChatOpenAI

def test_deepseek_sdk_standard_and_streaming_protocol(monkeypatch):
    module=importlib.import_module('core.llm.LLM')
    requests=[]
    def handle(request):
        body=json.loads(request.content); requests.append(body)
        assert request.url.path == '/chat/completions'
        assert body['model'] == 'deepseek-flash'
        assert body['thinking'] == {'type':'disabled'}
        if body.get('stream'):
            chunk={'id':'test','object':'chat.completion.chunk','created':1,'model':'deepseek-flash',
                   'choices':[{'index':0,'delta':{'content':'SDK streaming works'},'finish_reason':None}]}
            return httpx.Response(200,headers={'Content-Type':'text/event-stream'},content='data: '+json.dumps(chunk)+'\n\ndata: [DONE]\n\n')
        return httpx.Response(200,json={'id':'test','object':'chat.completion','created':1,'model':'deepseek-flash',
            'choices':[{'index':0,'message':{'role':'assistant','content':'SDK works'},'finish_reason':'stop'}],
            'usage':{'prompt_tokens':1,'completion_tokens':1,'total_tokens':2}})
    transport=httpx.MockTransport(handle)
    client=httpx.Client(transport=transport)
    monkeypatch.setenv('DEEPSEEK_API_KEY','local-protocol-test-only')
    monkeypatch.setenv('DEEPSEEK_MODEL','deepseek-flash')
    monkeypatch.setenv('DEEPSEEK_THINKING','disabled')
    monkeypatch.setenv('DEEPSEEK_API_BASE','https://api.deepseek.com')
    monkeypatch.setattr(module,'ChatOpenAI',lambda **kwargs:ChatOpenAI(http_client=client,**kwargs))
    manager=module.LLM()
    assert manager.get_llm('deepseek').invoke('hello').content == 'SDK works'
    assert ''.join(chunk.content for chunk in manager.get_stream_llm('deepseek').stream('hello')) == 'SDK streaming works'
    assert len(requests)==2
    client.close()
