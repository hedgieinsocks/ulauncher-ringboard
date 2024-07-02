import json
import subprocess

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.utils.fuzzy_search import get_score


ICON = 'edit-paste'


class Ringboard(Extension):
    def __init__(self):
        super().__init__()
        self.rb_history = []

    def on_input(self, input_text, trigger_id):
        query = input_text.lower().strip()

        if not query:
            try:
                output = subprocess.check_output(['ringboard', 'dev', 'dump'], text=True)
            except Exception as err:
                return [Result(icon=ICON,
                               name='Something went wrong',
                               description=str(err),
                               on_enter=True)]
            self.rb_history = [i['data'].strip() for i in json.loads(output) if i['kind'] == 'Human']
            self.rb_history.reverse()
            del self.rb_history[self.preferences['scope']:]
            matches = self.rb_history
        else:
            if trigger_id == 'fuzzy':
                fuzzy_scores = sorted(self.rb_history, key=lambda fn: get_score(query, fn), reverse=True)
                matches = list(filter(lambda fn: get_score(query, fn) > self.preferences['threshold'], fuzzy_scores))
            else:
                matches = [i for i in self.rb_history if query in i.lower()]

        if not matches:
            return [Result(icon=ICON,
                           name='No matches found',
                           description='Try to change the search pattern',
                           on_enter=True)]

        items = []
        for i in matches[:25]:
            items.append(Result(icon=ICON,
                                name=i.replace('\n', ' '),
                                compact=True,
                                highlightable=self.preferences['highlight'],
                                on_enter=CopyToClipboardAction(i)))
        return items


if __name__ == '__main__':
    Ringboard().run()
