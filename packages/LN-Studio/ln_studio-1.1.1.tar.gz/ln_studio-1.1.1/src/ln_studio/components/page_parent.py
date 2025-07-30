from functools import partial
from qtpy.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy

from .utils import noop
from .page import ActionKind, Action

class Parent(QWidget):

    def __init__(self, child, name, back_fn, parent=None):
        super().__init__(parent)

        self.back_fn = back_fn

        actions = child.get_actions()
        backs = [Action(label=act.label, kind=act.kind, fn=partial(self._back, act.fn)) for act in actions if act.kind == ActionKind.BACK]
        others = [act for act in actions if act.kind == ActionKind.OTHER]

        if len(backs) == 0:
            backs = [Action(label="Back", fn=back_fn, kind=ActionKind.BACK)]

        toolbar = QHBoxLayout()
        for back in backs:
            button = QPushButton(back.label)
            button.setSizePolicy(QSizePolicy())
            button.clicked.connect(back.fn)
            toolbar.addWidget(button)
        toolbar.addStretch(1)
        toolbar.addWidget(QLabel(name))
        toolbar.addStretch(1)
        for other in others:
            button = QPushButton(other.label)
            button.setSizePolicy(QSizePolicy())
            button.clicked.connect(other.fn)
            toolbar.addWidget(button)
            
        l1 = QVBoxLayout(self)
        l1.addLayout(toolbar, stretch=0)
        l1.addWidget(child, stretch=2)

        self.child = child
        # self.child.setParent(self)
    
    def _back(self, fn):
        fn()
        self.back_fn()

    # def closeEvent(self, event):
    #     self.stop()

    def stop(self):
        if hasattr(self.child, 'stop'):
            self.child.stop()