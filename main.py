import json
import subprocess

from ulauncher.api import Extension, Result
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction

from rapidfuzz import process, fuzz


ICON = 'edit-paste'


class Ringboard(Extension):

    def on_input(self, input_text, trigger_id):
        try:
            output = subprocess.check_output(['ringboard', 'dev', 'dump'], text=True)
        except Exception as err:
            return [Result(icon=ICON,
                           name='Hmm, something went wrong',
                           description=str(err),
                           on_enter=True)]

        rb_history = json.loads(output)
        if not rb_history:
            return [Result(icon=ICON,
                           name='Ringboard history is empty',
                           description='Try to first copy a few strings',
                           on_enter=True)]

        rb_history_list = [i['data'].strip() for i in rb_history if i['kind'] == 'Human']
        rb_history_list.reverse()

        if not input_text:
            matches = rb_history_list
        else:
            if trigger_id == 'fuzzy':
                fuzzy_matches = process.extract(input_text, rb_history_list, limit=None, scorer=fuzz.partial_ratio, score_cutoff=50)
                matches = [i[0] for i in fuzzy_matches]
            else:
                matches = [i for i in rb_history_list if input_text.lower() in i.lower()]

        if not matches:
            return [Result(icon=ICON,
                           name='No matches found',
                           description='Try to change the search request',
                           on_enter=True)]

        items = []
        for i in matches:
            items.append(Result(icon=ICON,
                                name=i,
                                compact=True,
                                highlightable=True,
                                on_enter=CopyToClipboardAction(i)))
        return items


if __name__ == '__main__':
    Ringboard().run()
