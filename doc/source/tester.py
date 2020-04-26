import fpclib
import json
import re

class NewgroundsCuration(fpclib.Curation):
    def parse(self, soup):
        # Get Title
        # Get Launch Command
        text = str(soup) # The swf url is inside of json, so we have to search for it manually
        swf = json.loads(re.findall(r'embedController\(\[(.+),callback:', text)[0]+'}')['url']
        self.set_meta(cmd=fpclib.normalize(swf)) # Normalizes the url to fix escaped slashes and make it use http.

urls = [('https://www.newgrounds.com/portal/view/218014', {'title':'Interactive Buddy'}), 'potatomanyou.life', ('https://www.newgrounds.com/portal/view/59593', {'title':'Alien Hominid'})]
print(fpclib.curate_regex(urls, [('.*', NewgroundsCuration)], True, True, True))