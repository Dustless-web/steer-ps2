import copy, io, json, os, unittest
from unittest.mock import patch
from urllib.error import HTTPError
import engine

class GroqAdapter(unittest.TestCase):
    def call(self,response):
        with patch.dict(os.environ,{'AI_PROVIDER':'groq','GROQ_API_KEY':'test-only','GROQ_MODEL':'openai/gpt-oss-20b'}), patch.object(engine,'folder',return_value=engine.ROOT),patch.object(engine,'read',return_value={'warnings':[],'pages':[{'page':1,'text':'test paper'}]}),patch.object(engine,'save_pack') as save,patch.object(engine,'log'),patch.object(engine.urllib.request,'urlopen',return_value=io.BytesIO(json.dumps(response).encode())) as network:
            result=engine.generate('test')
            request=network.call_args.args[0]
            self.assertEqual(request.full_url,'https://api.groq.com/openai/v1/chat/completions')
            self.assertTrue(json.loads(request.data)['response_format']['json_schema']['strict'])
            save.assert_called_once()
            return result
    def test_dispatch_and_schema(self):
        p=self.call({'id':'test','choices':[{'finish_reason':'stop','message':{'content':'{"limitations": [], "claims": []}'}}]})
        self.assertEqual(p['provenance']['provider'],'groq')
    def test_truncated_response_rejected(self):
        with self.assertRaisesRegex(ValueError,'incomplete'):self.call({'choices':[{'finish_reason':'length','message':{'content':'{}'}}]})
    def test_missing_key_no_fallback(self):
        with patch.dict(os.environ,{'AI_PROVIDER':'groq','GROQ_API_KEY':'','OPENAI_API_KEY':'test-other'}),patch.object(engine,'folder',return_value=engine.ROOT),patch.object(engine,'read',return_value={}),patch.object(engine.urllib.request,'urlopen') as network:
            with self.assertRaisesRegex(ValueError,'GROQ_API_KEY'):engine.generate('test')
            network.assert_not_called()
    def test_typography_repair_preserves_negative_value(self):
        source={'pages':[{'page':1,'text':'Outcome was fat- free mass with effect -0.36 in this study.'}]}
        pack={'provenance':{},'claims':[{'id':'C1','page':1,'quote':'fat‑free mass with effect −0.36 in this study'}]}
        engine.restore_quote_typography(source,pack)
        self.assertIn(pack['claims'][0]['quote'],source['pages'][0]['text'])
        bad={'provenance':{},'claims':[{'id':'C1','page':1,'quote':'fat-free mass with effect 0.36 in this study'}]}
        engine.restore_quote_typography(source,bad)
        self.assertNotIn('quote_typography_repairs',bad['provenance'])
if __name__=='__main__':unittest.main()
