import tempfile,unittest
from pathlib import Path
from PIL import Image
import engine
from editorial import render_card,reel_layers
class EditorialLayouts(unittest.TestCase):
    def test_all_formats_and_layouts_fit(self):
        block={'headline':'A careful headline about research and the questions we ask','body':'Research needs context. '+('This is a bounded editorial sentence. '*5),'claim_ids':['C1']}
        pack={'claims':[{'id':'C1','page':1}],'carousel':[block]*5}
        with tempfile.TemporaryDirectory(prefix='steer-layout-test-',dir=engine.ROOT) as temp:
            for n in range(5):
                path=Path(temp)/f'{n}.png';render_card(block,path,(1080,1350),f'{n+1:02} / 05',{},pack)
                with Image.open(path) as im:self.assertEqual(im.size,(1080,1350))
            path=Path(temp)/'static.png';render_card(block,path,(1080,1080),'a field note',{},pack)
            layers=reel_layers(block,pack,0);self.assertEqual(len(layers),3)
            self.assertTrue(all(layer.size==(1080,1920) for layer in layers))
if __name__=='__main__':unittest.main()
