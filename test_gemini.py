import io,json,os,unittest
from unittest.mock import patch
from urllib.error import HTTPError
import engine
from gemini_provider import generate_gemini

class GeminiAdapter(unittest.TestCase):
    def call(self,result=None,error=None):
        pack={k:[] if v['type']=='array' else {} if v['type']=='object' else 'Example' for k,v in engine.SCHEMA['properties'].items()}
        response=result or {'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':json.dumps(pack)}]}}]}
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test-only','GEMINI_MODEL':'gemini-3.8-flash'}),patch.object(engine,'folder',return_value=engine.ROOT),patch.object(engine,'read',return_value={'warnings':[],'pages':[{'page':1,'text':'A'*10000},{'page':2,'text':'B'*10000}]}),patch.object(engine,'save_pack') as save,patch.object(engine,'log'),patch('urllib.request.urlopen',side_effect=error,return_value=io.BytesIO(json.dumps(response).encode())) as network:
            value=generate_gemini('test',draft={})
            request=network.call_args.args[0];payload=json.loads(request.data)
            self.assertNotIn('test-only',request.full_url)
            self.assertEqual(payload['generationConfig']['responseMimeType'],'application/json')
            self.assertEqual(len(json.loads(payload['contents'][0]['parts'][0]['text'])['source_pages']),2)
            save.assert_called_once()
            return value
    def test_full_source_and_provenance(self):
        p=self.call();self.assertTrue(p['provenance']['coverage']['full_text_included']);self.assertEqual(p['provenance']['coverage']['excerpt_characters'],20000)
    def test_incomplete_rejected(self):
        with self.assertRaisesRegex(ValueError,'incomplete'):self.call({'candidates':[{'finishReason':'MAX_TOKENS'}]})
    def test_unsafe_error_body_not_exposed(self):
        error=HTTPError('https://example.com',429,'Quota',{},io.BytesIO(b'secret value'))
        with self.assertRaisesRegex(ValueError,'quota exceeded') as caught:self.call(error=error)
        self.assertNotIn('secret',str(caught.exception))
    def test_missing_schema_rejected(self):
        with self.assertRaisesRegex(ValueError,'omitted'):self.call({'candidates':[{'finishReason':'STOP','content':{'parts':[{'text':'{}'}]}}]})
if __name__=='__main__':unittest.main()
