"""Focused integrity tests: source fabrication, review gating and tampering."""
import copy, tempfile, unittest
from pathlib import Path
import engine as e

class Integrity(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='steer-test-',dir=e.ROOT);self.old=e.RUNS;e.RUNS=Path(self.tmp.name)
        self.id='abcdef123456';self.p=e.RUNS/self.id;self.p.mkdir()
        self.source=dict(pages=[dict(page=1,text='This is an exact supporting sentence from a test paper.')])
        b=dict(headline='A test question?',body='Editorial invitation.',claim_ids=[])
        self.pack=dict(claims=[dict(id='C1',text='Test claim',quote='an exact supporting sentence',page=1,population='test population',limitations='test limits',section='test')],carousel=[b]*5,static=b,reel=[b]*4,caption='Test caption',caption_claim_ids=['C1'])
        e.write(self.p/'source.json',self.source);e.save_pack(self.id,self.pack)
        self.pack=e.read(self.p/'pack.json');(self.p/'assets').mkdir();(self.p/'assets'/'static.png').write_bytes(b'test bytes')
        import hashlib
        e.write(self.p/'assets'/'manifest.json',dict(pack_version=self.pack['version'],files={'static.png':hashlib.sha256(b'test bytes').hexdigest()}))
    def tearDown(self):
        e.RUNS=self.old
        assert Path(self.tmp.name).resolve().parent==e.ROOT.resolve()
        self.tmp.cleanup()
    def approval(self):return dict(version=self.pack['version'],reviewer='TEST ONLY',decisions={'C1':'approve'},final_assets=True)
    def test_wrong_quote_blocked(self):
        p=copy.deepcopy(self.pack);p['claims'][0]['quote']='invented supporting sentence';self.assertFalse(e.validate(self.source,p)['passed'])
    def test_wrong_page_blocked(self):
        p=copy.deepcopy(self.pack);p['claims'][0]['page']=2;self.assertFalse(e.validate(self.source,p)['passed'])
    def test_unknown_reference_blocked(self):
        p=copy.deepcopy(self.pack);p['caption_claim_ids']=['C99'];self.assertFalse(e.validate(self.source,p)['passed'])
    def test_unreviewed_release_blocked(self):
        with self.assertRaises(ValueError):e.release(self.id)
    def test_approved_release(self):
        e.review(self.id,self.approval());self.assertEqual(e.release(self.id),'approved-review-package.zip')
    def test_changed_asset_blocked(self):
        e.review(self.id,self.approval());(self.p/'assets'/'static.png').write_bytes(b'changed')
        with self.assertRaises(ValueError):e.release(self.id)
    def test_content_change_resets_review(self):
        e.review(self.id,self.approval());p=copy.deepcopy(self.pack);p['caption']='Changed caption';e.save_pack(self.id,p)
        with self.assertRaises(ValueError):e.release(self.id)
    def test_stale_review_blocked(self):
        r=self.approval();r['version']='old'
        with self.assertRaises(ValueError):e.review(self.id,r)
    def test_incomplete_review_blocked(self):
        r=self.approval();r['decisions']={}
        with self.assertRaises(ValueError):e.review(self.id,r)

if __name__=='__main__':unittest.main()
