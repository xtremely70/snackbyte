from snackbyte import MyWindow

form_class = uic.loadUiType("mainwindow.ui")[0]

class MyWindow4Test(MyWindow):

    def __init__(self):
        super().__init__()
