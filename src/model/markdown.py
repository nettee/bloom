

class MdDoc:

    def __init__(self, text):
        self.text = text

    def text(self):
        return self.text

    def lines(self):
        return self.text.split('\n')

    def __str__(self):
        return self.text