#!/usr/bin/env python3
"""
Dual / Stereo Camera Viewer — Gearway OV9732 (15aa:1555)
Professional Qt5 GUI — Windows (DirectShow) / Linux (V4L2)

Requirements:
    pip install PyQt5 opencv-python numpy
"""

import sys
import os
import time
import base64
import subprocess
import cv2
import numpy as np

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QLabel, QDialog,
        QVBoxLayout, QHBoxLayout, QDialogButtonBox,
        QListWidget, QListWidgetItem, QComboBox, QPushButton,
        QToolBar, QAction, QMessageBox, QFileDialog,
        QGroupBox, QFrame, QSizePolicy,
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QSize
    from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QIcon
except ImportError:
    print("[ERROR] PyQt5 tidak terinstall. Jalankan: pip install PyQt5")
    sys.exit(1)

# -- Embedded application icon (ICO multi-size)
_ICON_B64 = "AAABAAYAEBAAAAAAIACIAwAAZgAAACAgAAAAACAAeQcAAO4DAAAwMAAAAAAgACoPAABnCwAAQEAAAAAAIAC1DwAAkRoAAICAAAAAACAAuCEAAEYqAAAAAAAAAAAgAFcLAAD+SwAAiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAADT0lEQVR4nJWT228bRRTGvzO7ttfeuEkcx4mTxkaJ4jQxvURCcorVplCpDregSlQU9QUhhMoTgn+AviAhVepr+8ILAokHRFuJAqGEa5OUqk2kqg4yDpdcnKRbEzs4vuzO7g4aByohnjgPM0cz8x2dy2+AXSP8H6N/uwRAJJPpY5ZtHYDrugCY4zgECAJIyIeKoggoirtTrDCjWM452JiSWpKX+/enx8rl8pzjOCAiCCEQ0IPwebWafGRx01evVVijaiF5ZBDJIwlcPv/1iQ3j3nV1NxFmCeFy2+aCiEiI5mYwRanJLJijaLZjd9k2B6nC8elehTmCS6UqF6/XH9P8QeHxcJUYa5bFudXDLfNhpQF/ELreiqWbBfbzjYLoikX7Cn9kQadOvelfWJi5x23eb5s1h5t1BcSgBYIgpsj2NEuy6hUh++L1+V2vX2cKY0YymRxSS6W1TiFEpFHdRiQ+osRGUjCrFeRvfwnHtpo9ka0aOjxJe0IRFHLzVMjPQ28NhYrFrV6mtUdh1ivu8OPPI/Py25bKqN7WFXefeu08fIEgmKJC+okD6YbVqFqpydfp0PEzMGsV1xcMC7aRnUFbpI/2jT2H8aHgzBOjA3PfffjOWiF3yzz45EsYHJtErLtj/ezJ1Bf1wt3855feKg6MHke4b4hWFn8Eyy7eQVc8ScZyFh9/cDF496dcR/SRYXMl+/2fLe1RdMdH8O0nl9jVa1OdwtPi9TDaXl9acKVmc2URrCfaj5KxLDr3JnB96lrsxlefBipbaxTqTeiNahn1ShHC39F+8cK53q37q4Jz0x/em2BlY1mEuruhHjo8QbduTov7v2fx9NkL4dzsVX+gLeJJpJ7Vpt8/B27WMfHquz5/QI+WNn+zHpt8Q99+sIr1/LwYPHiCKJM5E11ayuWqlVJgX+oZ1pMYJd6oIfvDZVF+sCqBQktbRDx69AXS9CA2f82Kxdkrrqa3un398WSTuuHh9GeWZU3sbBchhAsIAY+mQ/X4mhjJcVr1HUg+5FT1PWF4vZ6506czR5vUjY+f7DUM4z1u87TUyjMZSAK0yyGBGJNQCQLZquq5HYp2vjL7zZVfHv5GGflY5sUBvuP6gH8Q/q9pms6npz/K/x2c/gLmlHmPlrbGvwAAAABJRU5ErkJggolQTkcNChoKAAAADUlIRFIAAAAgAAAAIAgGAAAAc3p69AAAB0BJREFUeJy1V3twVNUZ/865Z+/dV/aVbDZAIDTVoaVg0BmlbapASEuVOh1Gt1WbmdrJDLbT8Q87/af8QSZaLVMQp1P/kOlrinamEKu1CjU6xQRTbQVNEYmAKQuFhNB9JJt933sene9usm5CMNsO/Sbn3pt79/e9zvc6BK5NBK4vqRp/10MBANf1JgLRqHb1y7mEgiU+KKUIYw71X/nmGjZybhHGNCWEnEWrhVhRFN7evnVjajK1wzTN5vJ3NVecUkRKSRcQRyilEgiZ854QqqSQipdksnFJ5Knjx/tfqDaU4KWnp4f29vbKTZu+0Xb+/EfvFApZXSm1gKkKNI2B0+kqqHkfUdOSWXJxy6zgCAEQXIDh1qFlTTOMn05AQyDy1WPv9fdHo1Gtr69PzDDZwAAG+Zo1X3o6lUp8XwirRAh1zJeulCRebzAZDDXGpeSsygtovchk04GpVDxCyl4ghBKwihZs//n9sOmBL/IX9/Y7Xt5z9NDYlffvllJhPAhkUkXSWdacaAsEYpkpsd9TlFmtgMI/Nfut/NsZXuD2uUEHRj1+NzrKVc2UlrdgI+4H8fkantF1IyeEpFJKJaWEqkVwW/L5nCedjgcz0yl/9ZpOJwL53LRXqSqMKN9//cMD8NPuZ8iLu1/nwVDDz6RUNBqN2gowvPT2li30Bny6LxfimqaBlGLBcFegnJZZsj01nzTGwMN8ldiyHzwAPC/Uu386TRqawiK8NKLDKZCrV6+2jSczAai+/s2HWs59ePrE1GTKxxiTlNJPqAVzI71Kvas0nt03QkCViiXw+fywbGXr5187tP9YNBqlbGBgAAXxsdiFnmwmg+pzzu0Ag+tcJVEPkc1mtfjE+C5CSEdfX5+ig4ODvKfnaW8hn9vKLUthANoaU2qnHC5KtfIzw2c6Y9ECaxEMBq4QXBXyudu3bfteC0a9benw8HvLhOBhDGMCRCEjKQTk82nbiRRjwq5iCgyXFyjTQdkxUmVebRjUQioJbCo71QoAF65yNWpuFnPAdBfc8pUu1dq2EbzBCOSnU+T8B0MwMvQSFLIpMFx1M4GKwjWwasbIufJgjnAKpWIWQks/DQ8+8UfY/OBjxPCEyOSVi4QZbujo2gHduw/DslW3QTGftgWj5WahVsy0bWA1sY8jhIJlFiEQXgEP7PwdpOPj8O6+hydjI3/XkvE4ZQ5d8wSbXHdufxy+tfO38OzO+2EidtJmGGhcXjNmbHQY3B7vPA8Yun2T3IIt3U9AIZuFyeE/nH1yz96B3/S9/ub6O7bEGppWjFNVGjv4k++I8dERuOu7e0BjOnCrBFu6d6naMQ5QUlYsp2X5BlilAjQsXwUrb7qNHD3wJHR2bLoEzMEiEb9Y27Yul89nmL++KevxeuN/2f9jaGxpgabWteAPN8On2m6tDbOiRS3/zPpyjDmdHyugGzoIy4TIyjXATaEunTmu+vv/XM+5gFMfnHW+PTQQcDpdwizmmcdXn0tdHhWZVBYiLZ+DhuZVICwFtWCmk2my5MZblBBWZffZ7F5gCmIUCy7tjPrr0KA/9lDXDdlsluUyGaYbulRS2fmMDV5YpsZ0p43hXAKloBbDcMvUdMONfXVuDJglAKoxmLz8TzDcDlUXWkolt/RkMuEo5HOzjAjVNGmZRYfTG2LeYBAmJ2IwdSUGhluDWjB1oXpIXDxDqjOB4qVkZkA3XHD53PuQSSbh1ru6YSpxuUEjlBpOt0WJJhlzCEIojY/Hwus2dxEsMuOjw5AcG4XpRKomjJJK/evUW+Aw3MB5sSoLSqbtAcznI889Dm0dW6D93h/oYxfOLk+Mx4KZqbg7ceWi/+K5U803be5y3XFfNxw9sBcyqQkQ3IIj+x+rDXPwKZJOXAKmG9hw5saAlAIMjw8+fOslOLwvDHdu/xG0rutwnDz6fHg6MQYefxg++4Wvwer22+HNg7+Cdw7ts0sstrmRtxHTuCjm2Cv7wOnxVypoRQHOLdsTmJ+oxLHDv4DkpVFov+dh+PK3e5TGGA6iKjn2ETm46xE4/beXQXd6cUazA8rp9teGcXnL/UHZBtOKAs3NrfHYhXNZAsSLSqCW508OQuzkINSFmoi7LgjFfIZMJ8btJmS4fYCTTyWDVM0Y1BiLLtS56ibsCoyDDPbpm2/ufC2ZTHSqcptjmIuoqeCm3eXwf+bQ7VFwfieslPPFMQIbbiAUOnPiH2+sJYRIezZDTzY2LnnU4/ESwTkqJdATaBmWTofTZTOyPX4N4bNb+AkYITiXbm8dDdY3PEoIERs2bNAozuY4lr366rND9eH6R/yBECapNjNYSiGERCDepcS1OC2AQUW0Ol/QEQyFdg++8fzvUSYOQ1WjFZ7b+kRn531bk6nEjkIhtx6NgetAOAwZLteJQLB+z+CRvueuOhlBhfBg2iuxdG7btv3GXC67DLMVz4n/m2CiMMoNn/ffr7zwyxGMi2rhCxIemf4PR/Nq3nPoP9t1oGex/qAdAAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAO8UlEQVR4nO1aeXSV5Zn/vd/33e+uuUuWm4QsQACjWAgIsiphkcGCilIRBmGUQg86nlbtGdsyninG9mino7ZHZ46F0bGnQl0ytDAztChFWWQpsjYxLIEQErLd5CY3ufv9lnfO892bGMJNSDedP+Y55+Py3fsuz+/Zn/cN8P/05RK70e/Lly8XfD7fjcb9Vcjr9fLKykodAP/jZ2/aJOD/CC1fvlwc7Le0kt20aZNQUVGhc86FJUu/fnssFM7XhrHRoLsMoOGuJdvsXQvKVx5/5plFYQAkUNLGjQCQ5Cv0xYsfmdTU3PhGKNQ9RdfUYVgbwPnwNM3YjddiAjMMx+F01efk5j6194P3dvbyNiiAlOT5smWPjz537swxv789S9c1nTHGh2OGkiTHBUHQAD4oh5yDKUrcMgTrIIpH4pCtMlNiipDtzcWocaV3/W73tr1kTpWVlX1KlPpPrampodl649W6iu7urixAT4iSJNOuQxOHJJnj3twRzQCBHXQcY0zQ/R2tI6LRsCMpmGuFSJKPRxJYtL4c8x+dhbqTDcq27+8wtTU1vsw5vy01p4/6OyojZO9XV8uhUHC2qiicMUG6MfOGVCEITCfmdV0XBn+4kBwrquk0KggCYqE4bp5RgpWb7oXb68Tch2eYFm2Yw/1tHbc+9b3niknAZCnpABgUbrcLnHMT/nRigz+8/2fambrOYXGYIckiElHFeLe7bIwCSjgUl68D3V+Q5Pxr542O2Wz2KlGSDHMaLteck3kwLoqiShJO+4iSSj5CY9OtoWs6rBkWVO+7gD1vfAKzXcb531/Sdm/eD1eW++pTj6+uJ5jkp/2lNdCJsWjRw5Mu1Z3/sDvg9zAmEGPDSmRmiy1EAPgQTgyds1gs4iCJIg3RVgREUzVkF2WiqzWgy5JNLSktXXPg4+2VlFgHdeKKiuQWbrejMze3MCiKUmY0EuSapg0LgKrEHapy43GiOHTGECUJshnoaQtzp8uD7Jz8hNOV2ZYuI7OBIXTFo98ubKitPdLSdLVAlETdbLZQRB4eJQcOw+uHkVSIGIOiJHg0EmW5+fmJwhEjF+zYseWT/qFUGpiI7phz/9ttrS0FqppQNU2Q4rHYsBJPP/qL1U08GQHJgnVfa4ssitI769ZtKnvzTQSSgYAl7bC8vFyi0mHxvY8u7Q4EymPRiCqSFzNmhDb6/DIeQRBS+wuCpmlKoLOzsK7+3LcoG5eXzzXs0ADg9e43oPYEuh4Ph4JcksRhlwVfDHHyGzESCfFQsHvt00+/bN2/fz+ZECMArLIS2rqnN2VGo9HbFSVBqhnCy3ollNTMn0usby3BsPkhxlEyRDweL25oOH8roaKIJNA/NCDY1DJKVVU3TwX06xYgVQqkGR1qIg4lHoWqJIzfBEFMMvBHMJ2cw6CpirGWkoiCa5qxD/02kFIWoWmqimAkMp5eqE/pc2JNM8yJGL/GdgwsjOqToFEzWBwuuHIKjFCXiEYQ7GpDLNwDk2yGyWyDrg9dLBNzqhJHIhaByWyB3Z0Di90FrnOEu9sR7ek01jDbnMbeJLA01IdQGlpSAnRNgZKIoaSsHLfMvBd5Y8rgzC6EJJkQjwbR1VqPxrNHUH1wB3xXzsLqcKekla7WERENB+DMKsDUr67F6LK5yMwfA2uGxwAQ7GxGe8NZnD/2W1w4ttsAIqcRCuG6IQBSpZqIQbbYsXDtDzBx3gOwOsCjIaCnw49gLAJbRiaKx09gJZMmYOK8v8Wh7a/ixAdvQbY6ruOfzC8a6sJN0xZj/up/RH5JAdd1INiZQLevydCoK7uA5ZUUYPzsu1B7Yhn2vPUcAm31MFszBtVsegAp2yTm739qM0qnTeH+5iD7+N2fs7pTexHraUciHjVUn1UwFhPnrkDp9Ltw9zeehc2VjYPv/4uxaa/6DcmHAphQvgJLHvsRTBag6tBhdvLDt9HVXIt4uNsQWIYnD6Mm3IHJC9fg5hmz4fb+HNtfWo+uljqDF03ThgmAc5B47nniNYybOgUXz9SwY9tfijvEqM9l1s3BeES2mC2qGgtKl8/ss188udd028LVmLtqI+Y8tMHwl6M7/9XQEFEs3I1xU/8Gix97EToHPn7ndfhr9rR7bJZ4txqxM+hcEiQeaKuzHL50yn7u6C4sWv8ibrp9Jh749ha8+4MVSZBpAsV1AEhasUgPpt/zGG6ePpO31F1lx7f/uOeZp588Onnm5LASh/Dmz/49Z+f2d7wOl1t3e7LFcDic+emuNzwUIRZv+CFmL3sCDTWH4btSQ10a7G4v5j38T5AtjO97dzPLUi9/9krlry5QYKs932R+4bnvFPva2sxOl4crWXlWv6/J++ufbJBXbNyKkrKJuPOh7+C3W/7BCBLX8Xud6WgK7M5slM1fBbLRfe++hEXz7zw7ZebkcP3Fdqu/PWha+fDXOwuLihLRcMSkcx12h8OXUzS288zebag+sIs7s62YNH8VuK4hEY8Yzj9ibAG/cPIEaz2zq/N7FT+ubW8LmhvqO8wjRxUo9z2w0q8kYpKmqaLIWDQnr7hJU2Lq3l9UIBSI4paZi+EdOd4w22TqGgQAhS0lHkFeyQRkFxWiufYSu3RyD/JGjlV6AhAFUeCqqsJkFnWrza712rimqpLdau80ma2J0x9tZdGgjuLxs2BNmdDosnLjkwCKAlMoBSTicSaKIlcSYBkul2a0ioyCERcZuOLJGeFvvngKF08e5BlZMorHzzSCitHsDwoAVItryCm6BWYLR2vdaU72u2/PBx6TDO52Z6kjRniUo4c+cdTV1drMZotO4Y+mktc4nJ6ezpY6BHxt3JWTi4zMfMOZswrGIdytorOpFo2NDbZTn1ZZRxRlJ9xuj0Yi+N3u//JQBkqeQxAIXZBlS5gMorn2uJFVvcXjkwmOD+UDKXBks4Q00NbAZFnWjx877Kh4dmPxrDlze1qbm+Rd/709W1NUJplMPAWAg3N6V0PBLgT9zcxbnA+LzQmT2QpbRhYiwR5EQ51USasv/ej7xV+954HOrByvcmDvB+7Tp447LVarruupRohTUGK6IJjU7varIp3q2D05EEQp2YAP5cREuposEWhzGm82W/Xjvz/k+vToQTd1W2azVevH/OfzdM4EQYIkW0BhW9dVI5pRMqQ4L4omQEwgFA6Lb7+1uUBgjDOBcWJ+4FqpFRnxQGavG51SmuR4zRtP+oG/tQ6EOquo1ChlE4mYxWqzqRabXbfbM1QKZwM2pIqMx2MRq9WZBXfuSB7ujiIU8BkRrbu9EQ53BnPmFCIWCVklUYLN7lCtdodqtqRhnoFrum5SVcWUXTgOJHgyTaP2GsoHOJWtkoz2KzUIBxQUlt4Gd24xegJ+D2EjaSbby4HlEtN0zi2hbr+DnM2V7WAdVy8g1OWDqsTQerkKshUYM2kB4tGwJZGIOxig6ZompJE8EwRRDwe7PbLVwUZPnMcTMaD10hkj2Q1UwrUAdN0wG6ppGmqOwZPrwvT7/p6yqCUcCuaIoqQLgnBNdUWnDIwJYqevxWt3e4VpS75hqPz8sd9AiYUhijIoMcXDwMR5yzBi3G3oaGnw6oBFEASVpN1f8nR6EY/H3V3tV52T71qDwtJS5mtoxpXPDhvZeGBxl6YGTqro8K9fNbQwecGDmH7f4/C3Nrg7O1oLNE2zCoJIIZDqGyGRSGS0Nl8u0jTVsmjdCygsHYMr1WdRte89Y0OTxYr6qgOoPvgbuHNduHv9i7B7vGLLldrCaDSSSYdntBY9nDO5u6czr62x1ls6fQnu+No3DXRHdryKSI8/6UM3cmJCKFvtuHr+U3y09QUsWrcJ89dshNtbhCM7/s3W0njJRpKjPlXXdSrqxfySiZi3+lmUlE1FR1MHdr/xXaPGNzInT5rlx9ueR2b+KIy8dTxWPvsOPnr7eeHyHw5k65qSSVKn4KBrmonqq1nLnsTsZU/C5pRxZOdWVB/YbpTXapojj7RRiEyJymKqLMlhFzzyLGYuXY2xUxbi8h8OoL3hnEQ9gDMrH3klE1FSNhcOjwTflWbs+OkT8NXXwGJ39lWQokk2irlfvbwe9z/1OkaXleHB776BK1VHcfXCCSHga5Alk4zsgpsw8iuzkT+mxKgCjuz4BT7a+nzSdAY57OgD0BeD+9412DI8OPHhW+houoA7lz9tOPXMpcuTWiSvJp/SgR5/FCd2/w8OvP8KQl2t1zDfKxDSBoF4/58fwcylT2BC+YO4adoM3DJrhrEGWS75aCwCtNZdwpGdr6Pm0A6jNDe6rH6mQyfc1wEwmcwU/FNL9YLQYbG70Xj2KN57YY3hgPljJiK78CZIshnRYJfh8E0XTqC98TxIirRhutqd6iLJZDZyw75fvojTe3+JoptvN2qcjMw84zSus7UObZer0XjumFF9ktkQ4wOlLwhI9AFI3UEhNzfr8qU6yc8Yy6G+uBcIbUxMUbgjIPVVB5MpnYKpTgmYwyRbYLZlpMrwwVtK8i9qbMg8wwEfqvZXGt/3hkcCTmubLHaYjTbz87VSbTqd9nB7RkZV7x2alOruxddeq+iZfef9h2TZvFRRElRc9WnHaJ3oyofUafSpqUX7GEv2D8MizqFzDaJkgmTyJL/qZTL1f1proCA455ooisxisdQKpd5zvdcB14TRzOzs1xwOJ9M0Ne2RSbIs0IzF6dFTzyCN9w1w8M/n91svyfi1JmOcXmiqbnc4BafL9bPKiopEeXm5eP3Z6PPP63PmLPvPlpamr0XCwYQkSfKXfcDFDOY1RZJMpvwRRZ9NWLhkWj6aY6kj9s+PuOlYHZwLkyd9ZX1ubu4Zq80uK4pCt3upO7IvnnFQDacqBvN5+fkdhQUjH9pSsSGSGpKs4wfMM64y167dmFNXf/Etf4dvSbCnuzeBXK/bvyL/ME7hRdgdTmRlZZ/OyvP+3c7KLVUDL/nYYHfEJIG7lzyyKtDZ+c1IJDRVVdVh3Zf9ucSTnS2oYrVa7dUZbvd/jJ4+ZvOWiorIQObTAhjwPR0zYtWqb5V29XTfqmncyRjdfw9xA/MXIBFC3O7Oqn5/2yufUcnSX7B/yhX/l/J3EkgRHf0PxcOwmCP0+/bt+0L/dmLu3Ll6b6QZatz/AuHYW7KNznY9AAAAAElFTkSuQmCCiVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAPfElEQVR4nO1bC5CU1ZU+9/7v7unueTAzzBMY5DFDQIKihUQegQQ1Ep+jSSnIGlxN3C1qE3cru9k46WyF7JqsppLNg6hlMKKEScKShBUoBQZDVAIGUAcFYYYZmPf0u/vv/3Xv1r3dAwN0z0wPDkIVp+qv6v773nvOPffcc75z7m2Aq3SVrtJVGp7QwoULxfr6egEA8GX+CExWJjN8HNTQ0MAGvSIpvWBDEhr6ZzZ5P1m3br/0h60//XIoGFhkmWY1BYJGoWGaY/tRjI9AwELI6yt8o2Zizcu/+IW/hy2g3+8no2BCEQCid9/96JTTne0vhAL98+PxGDiODQihHOaTYkFpbvPnLCA3PqwPFgTQNBd4PPkd40orHt6+9VfbBxYyu3RZ3q9Y8c3C95sP7OvqbK8xTcMSBAExymUx0/NGGGM7h1WllBKB9U0pYngeWMBgJS1Ixg3eWfOqUllFFZ1YPfWmP/7xubeyKUHMNGB9fT1ubGx0Wls/eLqvt6vGsk1TkiT57CqO3DoRotTrLexzubwRAkQYofaoZZlKMNAznlI67D4WBAR6zICKqaUwd/m1kIwZwp83/dXuaGsXVUV7saFh3Wy//1E9k0nhTDKzyT/++NqicCR0ZzIZpwIWpVxN+MxgCFOX2xtBGBFmBQhjZ9gHYapp7rgkyeZwfBFGYOgWTJxVCU+8/Pdw19c/Dw989w74x+dWiYpbciLh8JSD7x2YxybOFvb8/vj8FwON2ts/mmEk9TxKKUXo4kIKpQRT5lMojOxJ7YER83RsB27/h89CwXgvBLsjEDgdgrrPTIEF999AAz0BGotFmAKgp6fngjHxEGIzk78iQiBzS6pbAdtyuEUwFRKbgOpRufNFiCrZ+uLzXzQ2NnKb8/lKjkqyoqd2cc4h7DwB8WhCIHOBw/YbWNI9G/eBIGBw+zTwFXsg2BWGt7a8gzz5HqTIrkOsTUlJCR2JEyRMMTU1/3nq2EfL94eDfTdbtuUghIZ1RpmImbJpJhVVdccBETz8pHj4dRzHlmzbklIhNzsRQkHNU+DtLQf595u/dAMYcQO2/nQX6TzWI0yePi1aUF69J+3bLogCKPOwPGTAXXc9Vnf02HvberpPl2MssJUcTp4Lp0MpYIyJJMnJke5rhBC1bUt2HEccCUMeBjGLBEm+HRyHACBCSsvLrIqqyX+367WNr+QUBgG+QwH81O2OtVRUTjglimJ5f183NU0TjSYaOI6NTdNw5QAD0mBr5Np2HADZlZqOS9Sox5uPxpdVR/I9+e+yd/X1zaix8cJ+CLK8u/POxwtjenB7R3vbdaZlEK83H9u2CY7jpIW7HCmlOElSQdfj1DRMVFE9MeTx+ZZt/d/n92WCxShTAlFXV0f3vnlse+fpU0uDwV5bEESRrbwsyxxqXpxLHFticpomR4McESqKiqsmTOopqS65tnH9z7rTcyYZt0B9fb3AQNCtX1j5b4H+vqWBQI8lywoHQUyzlmUBNc0UPL3clDAgEwMtZx9sJHW7p6uzRBTE9QCwrKGhAfn9/nO6nfP5wQcfK25p7ThysrUlH+McN+JlSEwRpmk6lVUThMqKyiWbNz+3c2ChYTAOWLiwgYU5GggkVsZisUJKuSu9oifPiFmvKAgQCgUhFI08wd4NdoZ44ENTE5CGhgYxnojXRyMRivFI85bLn1gqqicS1ND1+StX/lMFAF99vrgDCkAsRra1mQWmZdSapsGy3isCBo+E2GQIcVgY90ajkZmDcx48+Es43F9rW7abEIek8v5hh2bgCBhIYtEBCyL/jDD+mEPlxfFJ1xUIiw66YV43ODESz21I2HemDDKkOCjF2HEssAwDiGOzvmeEFQQRBEkGQWI5CAVKhhzukvFhiqCUyoPfiecxHHbTsxWwkjpYZhLy8ouhpLoWiqumgaeojDMwElHoOdkMwa4WiPSdZhsQVJcHCBM8BxQ5dnzOzUXEEUvEiwIIEpEAlE6YATMX3QuTP70UPIXjQZQlwOlUifG3LQp6tA/amt+E9/ZshpbDu0HW8rjpDmsNl4pPLgpACPFwYpk6zL31KzD/3jXg8nrBsQEEMS2MmWrLBJQUBIJYDDM+80WonbccDr6+Ad7Y9AzvL8oqUOJ8onxyUwBKCWUm47DsK2vhulvuAz1q8S2XCPdCy+E3oOfkB9DfcRyx/ektKoNxVVPphLr5qHjCFLAtG66/7UEYXzMLfvuD1WAmoiAq6oUrdKn45KoABMD34bLV34c5n6sHPWaBKImwa+OP0IHtL0KkvwMURQFRlPkECHUYU+TyFMC0G2+DBfc/AYKYD2XXzIJ7//l5+N0PHwEzGeMObHBmObZ8RqkALAiQCPfDzff9C1y/rB4SUQNMPQ6///k3QDF7u5cvvyMUCIfU5sOHXLZt2qIsE8dyJMsyNSOZyPvbaxvQqQ/3w+1f+28omVAHFVNmwu1ffRoan1rF9+ml4jNUpBSzLz3mQlTPmAc3Ln8EElGLFTbo5h99DebPmfbet9a+cCyRACyJQN/eezDvh99/slrXE4KkSglVVcOapimyopYEOlvU3z61Gh74TiN4i8ph0uyb4Lplq+Cvrz4PqtvHw9dY89E4nyyLDNnmz8CAY8ONt38VJEUGRZPojhfXokml7tYnn/IfPfFRv9bbFZJPtweVT8+dra98+LFu0zQEChQTQgRRFE2Px9fuyR8Xj0f6YNuz/wqEOOBYBObe9gi4vUVAHIsr+pLwyZLT4YyTZ6mvqUNx9XSonHY9r7t1tx6Dwzs3wJJb7ukK9IIkigIVRZFKkkQjYR3XzZydyM8vsBzb5okpIZSXwl0uV7fbW2S1vvsGfPDmVhBEDJ7CcVAzezFYRgIcMznmfAw9AdlKmjiz9WOwTQPKrpkDap6b19ua927m4MOwTZH7FULP1vwYznQI2LY9GEGzWjIWBNFWVS0oygq8u6cRLMMCLCKoqmOlegS2ZUD5mPMhrLad+xYorprOLJQDju7WZhBECfbuft3HIpYkK5QJwtr6ClRn9+uv+mKxiIgFYTAnSijBsizFJVklwa5WiEf6+Q9FZZNBVt08TDELGFM+mhtIlnCIM73k2hYlKCqv4YrQowEIdrUit8fnvHv4HfW//sNfZdsWyvN6HVlR6MvrXxr3u8YNpYqikYEVOzsYMyjBlmTF1GMBCHWd5GN6xpWBmpfPNV1UPnns+BQxPoXcz2RKnMRsFjCgCH7Kwp2KwU8qXC63/eemnQVH3j+cV1ZeZYRC/eLp9jZNkuShEQfClDgOOAzKoTOZySXlk4nEocZiA7G+oiSD7PJAMh5mKAyrqmqFgwGpr7dbxoJIZUW5cEXOVSUijoNFSQFZ86RkImzsVJ9UljeWfLLrDGd6yVNQy4De9iNcSC0vHwrHT2QOC1mWpbI2giRRTXM5siyfcVQZCQG1HSLaZlJ2eYugoLSavw52t3GTZ8vd2zaGfHraQI/0c7+S6UwDZ1Yk21AC9LZ9AJQgwCJAxbQbwCEOGIbB0QslFBFC0dArws4qMWF9TDOJSifOAM2Tz3/oP30MbCvJUWDPmPMxeG0hJycoKRqcProfYoE+IDaFGfPvAG9hGSQTUU3X9QKMcXZ0MSAUxjaHq3rCx5Q6e+kKfpPDNgm0HNrNhWJZ21jzwfjcvGNEChAkBUI9bXD84C4QJATugmJYcN8TPFvT9fg4w0h6+LUXdqKfEnDww+Csbdu2kkgkSuPhHjx7yQMwceY8Dnb6Th2Hk81vgqS4QBDlseejuYBSJzccQAnhcfqtLf8Dkb4+cGwbZi6+B66/5WGIBjpRLBopj8djxUCpgDF2mCDph3NKJvX8aDRcFe7vkKvrboLFD3wTbNPi/mXPpqfAMQ0OuJjnH2s+eIiDbTG7ZVFgqCrU0w47X/oe3LnmGUgmDPjsim+Dy1cEe3//Y0jGIwVJt8cryaouihIvVRDiiKaZ1Ew9LrH0duaCe2HpQw2ABAk0twxv/WE9fPTOa6DlFZwpWIw1n2wgaERhkHnmI3/Zwutty1Z/F8ykCfPveRwqps6BfX96Fk59uF+IhnrzWChLoREBREmF4upamPP5FfCpm+9m0BVUlwQHdjTCrg3f41ng4GrN2PNBoy+IEJIS7sCO9XwTfm7Vk8CSq+raeVA1/UboO3UMAh0noL/zOGXbhqWiRRWTUXFVLciayq+tqJoEB7ZthB0vfBtk1fWJ8hlSAShLxsCEY2nlodc38Ji9ZOW/Q/k11wK7QjR+0jQYXzONd+eN066KYw8EoEd6YduzP4DmvVv4Xh+o+31SfM6fo5jhXCCrcMykOo8fhN+sXQmTZi3ghchxVdPA7SsBWdW4TMS2IR7ug1D3CTi2fwcc3f8aRPs7QM1j5siPrIdakDHlkzoyJ9IFCqirq+OtBQF3YCwYCGE5m3Cs7MxM8MO3/w8+3PcqN1tfcSW4feM49DSTCV6rZyjPsS2OJ1gb1nek9HHz4XdbKSBJkkAQhZYLFOD3+7kCKiuntnR2dfcJgliRxp0XeI+BKquSLmcxlMWqtYTYZ05zGKZnMV5WmRmSnCY/dnwQliSJeN3aO+zbokWLSFNT0xkcQOvrNwnPPPMNXdO0nS43y5/ZrZvs3pMnGYQVGgSufcXl4Q/LvVGqksEFGu0N04+TDyWEsNstiqKeKC6ubWbaGLgqg882Sx2ae/I8L3g8HoakRni+yfcVF3LgyeUIbOQ0Wj7sbNEhHo8PufM8L/3kJ2uM9F2I9K/nUANG4CeLl9Q3tbe1LdD1mIOxeHlfChqeCNPThImTonWVk6/55StPp0pF6UnhwS0bGlLXMz15vjWlZeUJBJjl5eymCFyJxEKeZZlOeUUV9hUUfP2Xrzzdl74KQIe8JdbY2Oh8Yfmqh4KBwK/aTp7gUUcQBOFi9/OlojQGSE9+glhUXLxux6svPTb4btCZtpCBFi5sEJua/PatX3zokUgg9LPOzlNiMpGwBVHE6dui7P7wZUUD/ooQ5r4dIoqiWFZeCQVFReu2bf31wOSZ4ztHcpRtQPbPq6amJnv53Y/Oj4aD68LBwIxwOAhmMsk2lcOUDJcTpa7ZY0lWkMfjhfzCoh5ffsG3/rTl+eeyTZ7RkJt7wGTqGxpk41D7g9FYfHU8Gp1r27ZoWelz6suAmDVKkggM6Ggu1xGXK2+Tz+P7+caNP+6+iD9Npej8Ae5fsabWjCWnG5Y+KxWJRv7HhrFydBhjhmJPakre+7W1d/3N71/M0VKmPT9qPvWp/+BdEeEgF1lRroMzi2hubkaZ/n7yydEiANjN/xCRba9fJchM/w9gd++N3XDrTQAAAABJRU5ErkJggolQTkcNChoKAAAADUlIRFIAAACAAAAAgAgGAAAAwz5hywAAIX9JREFUeJztfQmYlNWV9rn3W2vvql7YbBAQmk1cWMQFmhgkRBCBpJ9R80+emRiXJKLJ5NE/T/I7LZnJMvM7iRMck5hk/jyJ0YmdxAUREERaJWF1QWxFFkGUpZvu2qu+/f7PuV9V0yAN3U1V0xT1PhTQ1VXf951zzzn33HPPORegjDLKKKOMMsooo4wyyiijjDLKKKOMMsoofZBiXnfKlDvFIl3/gsKoUVGnqanJyf3IYACD1NfXlwe9iGhoaBAGpAVobGyky5Yt41JaX9/gHzo0rCZS9h2CQGTHyQtvGb0BIcyRJA81LO1vIZ9v0x/+sDyR/1WhLEFBBGDKlDul7dsfN2fMbYhUe4L36rr+DdM01FQy4WdsQFusgQ0CwBwGsixBMBSOSZKyWRDJT5/7y6/XADTShoYW0tTUZJ/lLQqDhYvvnK9r2d91dLRF4tF2SCYTYJq6xcoScFZA9kmSLMmyApHKahQEqAhVrljx/K8XA4B9ttbgbASANDQ00NZW8ARCgW9HO9r/T+vRT8T2Y0dNUZJEQihQSovlZF5QYC7AMk1HlCS4qHaUUF0zeK3DnP+rrzr4Sk1DDeurJSBna/ZvXPAPjbqmP7Tj7c0WABNEUSau0pdNf0FA8M/xYULe6rpmDRlaK15UOyqbCOiVm5qasgBAAcDpJwFAT7TJvmnRVxdEO449tev9HTIlVEKNP9cWnxBSbI+TOI5DCCmycSOAFhQsw+I/IlsFiVtV7hfoumbWDBoqXDyq7kU7bN+y9gldA+BLxV4NQF+o4HPO/Pm3hXWTfXxg/25vLNruiKJEz+ngM8bCkZojsurNAHNoMe8U7WgdrOtZL05zxQAKF66csgkNKgaHAGdSQgmkomkwdQu8QQ84NgPLMsyJk6ZKqsezbM2q3z+Ut8q9uldvHy53E2vBoq/+89FDHzfu3fOupSheibFzutRj4XD1EY8vkHRsWwBSpPmHAQFK+LU72g4P1XXNSwj/uWDmAAfbNCwQJRHm3TULrvniVBAECqIswsGWQ7Bi+cvw3sY94A/7wDRMJsmyM37iFXFT8tc1v/D4sd46hb0VYYISVl/f4DO07NJ4vJ2IoiSe48FHjWGK6s06jk07B6oYL4TDKCXUkWU1y+1yAYGzim07AIzAHY/cAg3fnc8H2hvygKSIMP66S+DbT3wVLp8zAVIdaZBkkZiG7hi6HvET4/a+RF/7ZMMCQ2tV0zSUZDIOxTKDvQVjTr+uOBhjhb8fIWBkTbhz+S0wdcFkaDsYBcd2wLEc7vylY1mwTBvu+dWXuTBkEhowcCCZiOFQVvTFEvVq9PLSxVLxO1LJpM80DLO81CsMqEBAS+pcu6fMuxQSbUmQZIFbhfywCiI6hTYIkgALll6PFgAEKorHjh2FbDZ9+8Kv3O/P+QA9FoQ+qS+lTEUNONcefymBoPbrJoy+cjiIstDt7EIFCnragOEThoI/7AXbdIC5oXaPoWvFtQB5MAa98jTL6LkQoJd/xs9Rwi2B4zA3TsDNBOvTmPRxAic8xl+2AAUGOoGWzdf5p/Pjke/oLOLncPBtmwcB/ZahF9cCbN8edd19ytarqpqVJBnX/uV5oABAZ88bUGHjn7ZDrC0Jilfia/2TgU5gqDoAf23aBtGjCaAiOIFgCERBWicmFQ03iYq4DHSTEvZJtRs8Xi+RFUUoj39hgGokSgLEWxPw2/v/xN+TVZHP8baFL5trfXhwEDY98yasfvxV8AZVFAi7oqKKyYqyefXq5fqECS3FXQZiQkLwYIsgScqWSKTGsSwT46IwAJCXelLcl0MIpQUN/uSBc7rqV2Dryh3w86//AbS0DoEqHwSr/BCsDoIv6IHNz70JP//6E9wSIN8FQRT8gSDRbHMrXqOlhe8Q9hikLwKAO08Ll9w5K9p+rPmD93eYhBAJziUYA1lR05HqIYcFQnEGLRoIoSyTigej0bZBffehTg/09LWUBqGaIFz7xSkgiAIPBO194yN4a10LyB6Jv2cahlVVPUSsrb24+aU1T87Oj02v6OnLA+ZvdONN//h865FPbtq39z1bVb3Cucz8waWQonqykqxmgLFezYO9BEmnExU8XFe0lErX07dNG7JJzV0SYl6AKoHqU/jvbdvGrVdn8mXTmEjF61euHLGxLwkifaWA1Nc3CjU1QGPJ3WsOHvhwdlvrIVuWz61PkF+ZFHtCIrR/op9o4jFAlAdG3JE+x7FRHpwxdRNpIBRcuPqFJ1YA5gr2ISegr5SwtrYW2tS0zHAc599GjR5nVFUPAssyO5eG58IvcOdEgdEivogg9JuE8+We5fDVgPuywbIs3BK268ZPpsFQ5BUcfJ4o2tTUp+fq0yjltx1nz7llvkdRHte0TI1t2yI+3IEPd4NlGmDZFojiuXUNSgWOg3sBDoiiCBXhKhg6bDjTdcMJhkIJx7I3atmDi5ubZ+fmXzcxt6cQ+z74DfO9que5RCImfLR/L5e+6prBUDf+UjB0HXCjqL29lT9814yWMnq7O2hDKBSGUEUEAsEKMAwdDn3yMUnEY0JFOBIeNbpuASO1zwIsuxmgMb866bE1IH1x/tzB9z8Xj3WQA/v3oGdM0fyiBVAUTF6sAkGUwOv1crNcDhX1FRjpo5j9A6ZpQjqVhEQ8yodNEATMEQR/MGSOGTtBMkx9pZ45uAi/1dzcbPdUCHosAFjw0dzcbM2Z03CdrPo35AefYo5S7jL5TJZcaBJkRSnr/lkDFcvkyoWDztmdU3JX6UzwB1wh0PTsinVrnlxYX98oNjcvswopANzrB9gAHt+I9ZqWnblnV4tFBeGUU0jeASwXhBQGyE/Xkn5aqbkQmCYEK8LmqEvqpGwqtXD9+qe5Y9iTJWGPBCB/sTlzb3leUbw37d61085k0gKOfzkUPBCAltditSNG25FIJWSNzPXrZ4zb2NBy5rgA7eHgO3Pm3FqPg79v7y4znS4P/sACA0oFcnD/XsikU6JIpX+BXJleoeIAjErCslQqzhKxKBHEsuYPNOSmXfHQoYO2KEr1qLCo/WcqJqU9Mf033HDbLLzokcOf4MaPWF7UDTzgVEwFAdLJJKRTCSbIwrKCWIApU6ZIVBT+JZWIM7w43qQ87w9oKyCgolIq1N9ww5fmnskKnE4AuAMRCg2NACEzEoko5gDy9X4ZAxN8H4RSyKbTjmM7jIh0Hg7+vn3hbseZnikDWJKCtwhUEOKxmEkFoZwIOsCBcQIMy0c72lBXb2tqauK1HN2t+LoTAIJtSebNm6eAQOenknHBMs2y9p8nwMLFZCLhECCROZ+79bPuuw20VxYAzX8iIcuEwGyM6zuOUxaA82gaSKeSNqVUokSsx/enTDn1NHBaJ1CSHAWAZMrz/vkHFALMG+jSRAJ6LAD5+V9WK+4gQIId7cfK8/95BF5WbprisbajmFl09zXXLOy2Yuj0y0AKKn6pvOw7j6cDAqplGaRP+QAEKw/7E90tMc/X/WRy7ulhZ+gaco57+rmND3iFMU9/Mj69ic0wS1YAmtt45PMa/9BAFApy3tFzTgSAUsFNbHRsMDHZwdD5vBWIDD6h3JzxTQ4K2VQcMol2zjRZ9fHPYMIJpkkNhOmJnsf09KMAkFyQwgItHQdJ8YGoyDB80jVw0ZjLwHEoTJr5BRAkuZMJyBAsgf5411vwye7tnNHvvvZnMA0N0rFWEGUvCJLEGYjM71+QkqBH7D8NsSCbSoAnEIZhk2fCVTfdATXDx4OkBMETEAHpNbRPp3Uj70ZfMQvGXTULsOxgytx/wN44sGPDH2Hnq3+EVKwdbFMHj78CbKt/ipZpCdFTdAFA05ZJdoDiCcCsv7sfJl63BPwVg0CQAEwdTZ4NqWi2k7GIE4wgATCyDPSMw50qyeMDmQRg5he/AVPn/T0c+fAd+Ntzv4S9b6wDf0UN157c+rdMz7kUAJ7CBACJ9sMw+srPwjWLvgaXXHE1ZFNY6GiAaeJ86Jbb8YHPtUU9Vb8h/D0h+BnCTaPDbLBMBwTBCyMvvRaGXjIdtqz8BWxd+RvQMjHw+MPg2D1Kibtg6SmqAGAUCpkiCDLMvu07MH3+3aB4JEh0ZLCYkRNOOfGuBRAlhTNXUrAb1okmAP+LFgCBTMDiCM5AKnCnKpvWuNZ/5ralUDtuKvz1mcfgwM7XwROIFIxppMToKaoA8BCkbXHpX3DvT2HitbMh0aFzwnA6QPCWJoSA4lWwvh0Sx2IgShQOvPs2fLxrC0iy19UcxrgThdMGMkn1hcAbkEBLO7z4BO+VnzYS7RkYMfFqqB03Hf7yk2/AB1tXga+iGpyznEdJidFTVAHIMwtfi775C6ibXg+x1nSnZ4vij1KOjELseaMZPmrZxImzLR20dAq0VJQzAT+Hf/Cab6z5LVimDsPGToERE6dD3fSbITy4mvsF6CjhZ3AwtHQWMF1t8bcehWd+es9ZM42UGD2npPF01T9z5/2vRkEQHmrZ+ZbpOI50uk0hbiZRU7owC9uaUTEX8EBTl2t4iCZt66rfwoF3NoJlaCB7A50BEkGQsMTzhGtbps5bs+JnUVMqamph8mduhcuvvw18oTDo2Sz/LpKD2oj58zjFPvPIPfDBllXgC1X12nyS85ieXKo4Gzx0GKkaNCQRbWut3bJldeJUVUOFKXPlBSFuIKQ7Zqk+lfe6XfHofeyPP/4K7H2zGQRZ5XObKMkMtYozxzKIbZknvCgVucbJngBD4rOpGLzW9DD893fmwp43NkCoyuNqI98KFXhhCrMBFn/zURg77fOQTXZ0Rt4uSHpOg4LVOZtaGhbe81+nYJYFHr8KB9/bDE//6B9h20v/QxTVD+GqwaYiK5YoiXYmlSJYTyjLSsbj9bd7vL6ox+PtyL2i2AcJm0A7tkXweoIgMm+gEvRMElb+/Fvw8hPLuVijpuCg5ZmGFbVL/ulRGDHpOsimokC4Vl2Y9HSHsxYjfDhDS0Hd9PkwdtpnIJPQO5mF5ssX8sDuba9C079/FQQKrOHLd+29/PKp7TOumd2e1dJCNp0RmzesiXzwfovY8s7b/kAwZNi2fcJcgwzEW2Uz6ZCuaxU8OYWZIMkePre+8sQP4OiHLbDomz/jcyYyy/XcLZAUFa5Zci8c2fd2rp/e6WsnSYnRU1wLgKKMUStfCObe/gPeuy7vJqDkYluTD7ZsgD89fCeaLHb/Qw9vffg///Wtz9246KisKk44XGkOvag2+7Wl9xz4/r8t33/pFVOS8VhUxTJ/x3HE/AvbshBKbX8gdKwiXHnA4/V3uLud7ho7VFMLu7ashGcfuRdsO+v2iuZp0iJkUxpccsU0mDb/bh5uRYZeMPQUWwCw7BvXx3Nv/zF4fD43dMnj2A6XVEPTYMVj3+akPfDgj7cu/sLCT3a9f8yXSMZFx7aJZVnEskxy+FBUNnSdPvj9hz+6bMq0eDqVEijlff+PnzzBeJ9+ZJ7j9wfa/IHgEX5AAu66mQb4w4OgZeNfYOuLv4NAROmMBmIvnXRMh+nzvwyXXHmDazpzS61Sp6eoAoA31bUkjL7is1B31WfB0C33QVBS+UEHaXjxFw+Ankmw+x/88bbFDQs/OXIopiiy6gi0a5cNApIksVz3C4JMmzD58qSm6ci0k20b/xlXJLwpVGXNfkmS0/iebZnMHxkC2158HHa+9gooHrXTROIaXvH4YcbN3wBBVE4ZnSMlRk/xBQDNpaFD7firAbum5HevUFJVvwRbVv4/2NH8NFQOGmbO+syc1mOtKVkURXb6Xrk68fllZ/LlU5KWic3Hun08vrNKCLH9geBR3rOfMb60wp21Vb96ANLxqGsec0mSRtaGwSMv5fsFqOUnJ2uQEqOnuALA15k6hAePhLqrPs8DGDyCxRiIsgKxtnbY+erTTPKE4KqrZ34UjgRM1IYzXRY1J5XQ6MxZcxIVkbBpmsbpng+blAqUCrbPH+DmEzVEVv2Qjh+Dt9Y/BYrX3afnc7tjgscvw6T6BjD1bK7OvkTp6QX62C1cQFMIE65bDJHBNTyYwdfOfL+bwdsvPwXxto95NEsURAdrSXtzfUlRGO3ZOQScaarqTaiqJ8a7hDkWk1Uv7HjlKeg40oprcteMEzTjBCbP/juuNVhTDzmtKTV6+m0KkD3+ro+OUS/QMibsfPVPPNMF98zxSBNczvb0ug42fZQVtH89/QpzmCN4vL44ds/CNvaipELs6AHYtWUVqL6c1nQevCSDJKtuz7USpqd4ApAzl8HKYTDx2kWd5pIfcChTOPjeFkjH2/iSBXfK3n/vnUhbW1bG9m1nurTt2Nh/mO14a7s3k05TeoJzdRrwwljRVBQ1nusVyDAq99HOjXzTxg2r8hAsBCoCMGHmF/han/Jt2xKjpz8sgBtrxrw3DHe6ks3bmMmEpzphihQ6PNjW7OD+fbKWyWK/oDM2FseO2aEQtd99Z7svk8kIPWFyF62hqteXoJTi3ElQKw7xZ9Fyz5kjWMjtwfNYOilJeooqAPlNjGFjp4LiU7lZ7NrsGJdOvIQ8X6joOM7yn/xwqMMcIkhSt0xDp6qqJmytfH5txesb1od9fr99cgTtjM/WZZ2N9xFwX97BnbN880oKpsFg2JgpuSQLk79XSvT0gwDgTTW4qG4aj4nnb4pJEMmOBLS89mfuuWJgBOPdgUAwvm3zXyM/aHygFhkoq3jaDJ55h0ET94Xfr6yusNavXRt89Cc/HI7eMqZX9wrHzWaCa6+ksET7IXj39WdA8bhpYq7wMv7sqr+CD3ap0dNbR7DPU4BpZHN+x4nHmuY96K7vBUMh6+3t24I/anygNhHrEFBzBg2uMJFJ4UiFhYvgtavXhB79jx8Ox3lSEPEkuj7Htzu/iIxzn6frs0Pu2Y+XzJUaPb1BnwPJ3QU1TuXtYttYX8Bvv7vz7cDSO/5+7Jhx49Jjx03KGIZObMsmm/72akUyHhMJxX687tGohcKpnsd99pMDQaVFz7lLCeuGkcgEkYdIHdi5483Am9u3BnkLWQqgKiq2NGFoJgvJLB7dP8tzDUmJ0VNAC3CyxLnEojk66XfHTVjukCNF9TgeDz91g8PGQx8xg7YgzMrH213v2H2eMz07lBw9/RAKNk4oY0IHRPV7uEOCXnWusyUxTcNDOolwgYxBjzj/QmYVAMxxHMGyTA9vWWtjqLSCPw96yp2aQyD37F0CJ6VGTzEFAL1P3Ilqef0vkGjH7Fc3IdJ9QBWGjpniSinlB4oRyzSVQh+wfErw8XGIbVset3OmTTDr9qKxU7mn7PYxtkFWKS/HSnYc4c+OA11K9PS28riv5wZyc4QhyuP3QynFqJXtpkvzs3X5mXYqBjWKXP5KKKEMByenxfwvKkhgmai9XddW7tZv1/U+lBw9/bAZpKUTcPD9LTxaxpsUUgFMDWDCtUvA44/wjFrUFNM0vKauezGiVUSt4WvxbDYdQS3FwA1u7oyd/nkIVVXwKB9/bkGCbDIDn3ywzU2/Yk5J0lNcAUDmYL1fqgOO7n8HJM6w3BalZUIgHILBoyaDaWR45CxHSDj/bSg8CG6aGLrmsywL50tuOkVZhdoJ14BtuZ22+QcJnrTlwOHdb4DAtZ2VHj39cnYwz4/zQtuB912HBMth8vFzSYFp8+/i6VVYB5E7SMKT1TIBJKwIWsPj5jgoec3F7NqLJ82EMVdeB3oGK25wcwfTuii0Hmjhkb+u++esxOjpBwHAI9r8sHvbatjz5mugqFJn+rKWNmDkpdP5A2vpWD5/naWTiUG6rvkKzDQenk3GY0NM0/WW+XHKzIGpN96R+4hrFtFrxmqdzc//HAw905nuVYr09FNOIOV17Qff2wTIk+Pmx33Aqxbe7XrZuEuVW0JlM6lK3EQpFNMopaamZwOmafjQVPKs2WQHjJ2+AEZOmg56xjye1ycIkIom4MiHO/je/snzJSkxenp8z74+LF8OeoOwa9MLkIymcpkqjptcmTFg5OTpsHDpY2BoaZRWlGxmmqaaiHUM03XNexZMy1ljgFQyXo2ayAkRRILbthdfOhMWLn0YLAOdNvcLmFfv8Qvw7ut/5gzN59aVMj09Rd/jirg9KWKJ9GF46b+/B6Ls1rK5Dy9ANqnzwgosZcpgQoWIpYUEDz/yJBOxYZqW8SPTct60y4ju4RbeE2A8S8ZxaDIRG5zNZiKuNRR4YiRqzLVL7uPPhQctc021bfAGPLDnra2wecVjfJBPeZQNKzF6eoizCiy7SYs+2LXlRdi15WVeOIEPyClE5mgG3HTPT6DuqgWQjra6e+vuwcuQTMSHxKLtw3Qt68V0aUqp1ck81IicVuSYhL+zmOMIqWS8MhZtvzhvJvGauDZG07z4n34JIyZN5Ycu86wZ1ApKQM+m4K/PLOf/8nKqbrSFlRg9PUEBdhYI4BJlza+/A1omA6Is5+rlcc8al1kEbr7vZzD+mpv4WtZd12JxJGqP4U0kYsNiseiQVDJRqWsZTMojyBj+Yg4vnkilkpVoHmPR9hGoJdi2njdlEERi6hmQFR/cfN8voG5aPWST+cpanlsPwYgCW1b+jreQwfq7/IBeOPQUezeQOSCIMujZBLz4y/th0X0/40WNbj0b/uug0MLib/0XfLB1HTy//F4uuRjWpLm51zR0nwm6T9NwjZv8lD3D2rnOs3QpllUJBE1kvOMITLpuCXz+rh+B4gm5dXz5/nuWBf6wD97d2MyLK3w8f9688Og5Awqyt+iuo32wa/NKeOaRpbyWvbOyNXdwpJ7RYdyMOdDwv38DIy+bCUY2BZqrQTzZUhAlrJfDnyk6uZ0v7g9JTBRl3vcUS6+wxx4y/PovfQ/mf/0RUNQQ78+XP9QZmeWr8MCuLc3w7CN3g42pX70oomQlRk+/5AMgc1AqsYEBNjLAWnYB8pqDFo5AJqHB8AlX89f+d17l1TZH9u2AbDKKoVYiyQo3v50HUOcycDQtxsuokUn+UCVMuulrcNn1t0FFdQS0tImmt7M+7mRmoQbhyy2runDp6ZeEEGxdgi1MjjNtOYgUNzBcgnAuM7IYxyYw6rJZMHzCLEhGj8J7G58FQmz4ePcO+KRLTx03EVKG6Qvu4qYVkx9rx10Jqs/PI3bphDs/dh6qyFhBmeWUGD39khF0nGkvwrP/SeHGu34EqhdNmts3N2/WsujZEsKrWq79wl18Vwtbrmmp2PGeOrmIVyASBPwapsNhyXa+k1Z+fkRt5VU7sgDv/W0dPP/ofYBdOArBLKfE6OmXNnHING+wCva99TL86ts3wOdu/yHUTZ/DieXag8TmGIeOTCbherJIIHbe7Lqswf9lkppbFEkob8acr9tDM4qaKKsqaOkovPDYg7Bry2qQVC9QIhSMWU6J0dMvjSLzjhQua9B81U2fB3O/8n3wh7HfHYCeNXJOFUo+MsD93qc6YGGaXZc4N5Zd8weXFPAEZMDI7K4t62DNb77LCzjy5V1nUzJ9IdDTL61iuSnDecvjh11b18Dhve9A3Yz5MHz8VbxfriTLrhk0He4g8ZTnU3i2fO7jnTAIeDzYeREgeqQN3lz7LHz03jbY++Yr3GTymHgR28SyEqPnjALAyNkvE/MeMKZdZZPtsOm5R2Hrysdh7LS5UD18DAy6+EqoHXcFZ1qwsgLjLZ08c6txcC61QUvFuYnc9uKzoGspaHn9GYge2Q+CrICi+tzP90OHbXae0ePmKffVAjigAYXeVLZ2C5y/iCCCL1TN/79721p49/XnwRsMg+L183o37KDZtb065NqrH8T26h9s42YSq2Pw94o3wJ0z7l0XYW4sBXpyMQuNxxy6+8xp3mf19QuqPP7IntYjh0JHDx9ioiQV7Pwgdy2d78SJks54MOXEpoqks0kDz9cDzMVHk+kmRA6ko2TIAKLHTSSh5viJkyXHgX99afXv/xkPAssdHNVzC2CaVPcA8xbjFAveWDm3155vw+YNVZ36s1wreOCs02kaaGADjB58ntxJJhhR6nYAu50f8MzZYNAwGIMNgUAIJcop2nEmuaBHvi/vyS/XJLqfOS/Azh093OxjP0N/AFvTmQ6zmvH97dujTm8EgOGBw6tXr9bBdlb6AyFblKTiCUAZBU8pDgSDlAHrWLfmqZfdd5t6JQCwffvjPNHcNBP/Yzu2HaqokBzbLohDWEbxgMkhgiBY4Ug16uuTDQ0NDJt/dzcNnLZrFU4D8fihDmBsUzAYxsEvW4EBjLz59/h8lAqUMMtZjWdA40Hg3X3njOv87du3m45lP+gPhogvEOBOS9kKDEzkpmh78JBh1HHs5rVr//ASKjEKQZ8EAL+IF1i79slXLctsxgszxqyyJzDw4BaQ2oBK6vMHiW3YjT35Xk8jfcQx7Ua/P0SCFWGGXavLVmBAar81dGgtVhQ3r1v3VPOZtL9HApCzAhQvqOuZFaNG10k+n8/O1coVkoYy+gweSGK1F48Gr89vWY75IDQ29ki5e/ShpqYmp76+UTT1w0ts23pt6EUjcIPbKi8Lzz1IvoYxWGFFKqvEbDq9ZP2aP77W0NJCzqT9vZkCGMAGaG5utiwj+12v12+PGHkJOhp4FFbRS+XLODXcOkUT/MGQOfqScZKuayvWr396BSprTwafXwN6gfycMntOw3yv6n8uHusgB/bvwRg4YkAc5HzBDX4gZI4ZO0EyTH2lnjm4CH/X3Nzsbkb05Dq9vXH+RLG8ECTiUeGjA/uwukXgDRXLQlBU5PMFMTk1GAzZo8eMEwzTWPnSqiduBmhkAMuOH0rRA/R6vx8HH4Vgw7qmlVktvTAQDHWMnzBZ8PmDpmHo/MZl57AYcKvJ0PnG06ZGXDzKGTm6TjB0fYWr+Tj4HL0yw32evPPTwYwZcyPBcM3vZFmdf+jj/dB+rM0yTRP74vLauc4M1zL6AOSfu8TDEC9jzPb7A2TI0Frq9fpsyzEWvbTqyRcA0ON/CCvJe83os/Le8kJQX18vKp7a7wmCsJQxVtnWepgLArZNxSoYFAZ+s5xAlHF64GC7TaD4oDNBoLbH4xMGDxlGfP4AJh+s0dLJ/1i/vmltY2MjXbZsWZ8zSAoxGp0lKjNmNEQCIfleQaBLKRUiyWQCkokYxKIduGRkjmNT23Ywe7q4LZbOUzC3Yx2IooQ9qZnPH5ACgSBEKqt51rEgCKs13Xxk3Zrfr8HP9yTQcyYUrLNFfX29gMtE/KG+/tYqWSV3CIJYLwjCtZZl+TGZMpmMYw18rq99WQJOBi/+pRQqqwbxf7HzF6W0VRCE35i61bwmN/CYrdnY+BA5G83Po9D2+ARBQCxYcGuVYdG7AIhICVwtiNLVtm05rNA9T0sA1A3pGozZv5Qk1dQy2U2HDh3a2NLSnMp9hGBU9my1viuKNSGT7nLQ5s37UjCRSDI8U7dI9z6vkfJknZbmzgHnQB+rpqaGFXLg8+iPQSD19Y1CKnWYnEogyvg0cMBTqTqC+/gYhi/mfHkutLCs+WdG2UEqo4wyyiijjDKgmPj/Umb4eZGmbUIAAAAASUVORK5CYIKJUE5HDQoaCgAAAA1JSERSAAABAAAAAQAIBgAAAFxyqGYAAAseSURBVHic7d2xjxtVEMdx+5T/4KJI0FCkMJFi0ZCG/nRINNBGlFS4S01Jne6oKFFaaJCI3NMkDbpI4YoUNCBF5G8IWiFHK8f2etfvvfnNzPdTRZDLvd1589vZtc83mwEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAobj5z6uLy4VvrNQB966dP3PWTmwXT8PBm7SAQ5l4b//qPZ+0XAxyw/OSBuyCYe2p8mh6ew2AtGARyC9pufpoekcJgLRYCZzMxND+iue7drqo9y5JJIxofGSzFpgGJCYDmRxbXYtOARABscL+PDK6FXsEyD4BNCiqdFKC2zX63ngJMA4DmR2bXAiFwy+obWyefBx98+NGrWRD//P3XXes1KLu4fPjW4qGg+S0Ao3/85o94PFH2v8nLEIz+eZsl2iTw+Nl3e//fowffj355sPUUYHYLgHzNvzm+CCHw+EDjb/+dMUEQ/haAe39kaP6pf791f5xlvfcBWjT/sV9n1Q/mDwGB6M1f6utrIACAhs2rFgJNA4Cn/4DWG4OYAIDGV22lKYAAABIjAIDECAAgMQIASIwAABIjAIDECABgQOkf5lH64aCmAbD5Ucd9v0EFyGxp8CPBTABAw6u20tW/QwAAjZpXrflNA4DbAHj0aGITD32dVT80DwCF34YCtAyBRyP+Ph8Jllz3cVmRPxYswseB9Zu61GcCWjG7GvOjwYdFDIEozV+a1QeCSjwE5FlAjmaJdjxR9r/p/ThTALJbGl79zScA3hiEzJbGzS9xC0AIICOF5pcIAKX7ISDbPpcIgH4KKp0coLT+/ra++nfMF3DoE1D55SGIYnngwpb2GcCu5r95+eLdn5kGEMGy1/z9/a3w6/LM3wi078Qs7t1/72uYCODFcscVf2iPW0wCpr8e/FAqHgqCDmEANcs9Y/6Y/d06BObKzX9MEACqbibu7ZYhMPfQ/LsQCFBzU3A/twqBucfmByJaGIRAk1cBaH5g2PZFscWrA81fBuTKD+j0R/UA6KcYzQ8M6/dJ7SmgagBYvsEBiOKiYh9VCwDu+wH95wFNngEw+gOafVMlALjvB3w8D5D4cWAANooHAFd/wM8UwAQAJFY0ALj6A76mACYAILFiAcDVH/A3BTABAIkRAEBiRQKA8R/weRvABAAkRgAAiZ0cAIz/gN/bACYAIDECAEiMAAASIwCAxE4KAB4AAr4fBDIBAIkRAEBiBACQGAEAJEYAAIkRAEBiBACQGAEAJEYAAIndsl6AqtUPz0d/zdW3n1ZZC95HfcogACZupmP/HUKhznkt9e9cJQ/tlAFQakNN+V7ZN9wxqE87qQKg5cYaWgNBsP/cWFolq0/4AFDYVEPryrLZdqE+tsIGgOrG2iXbVadDfTSEfBnQ0+aKsO4sx7lyuu40E0CEAkWeBqiPnjATQITN1cfxaFsF2W/uJ4AohYg6DVAfba4ngMibK8Jxel13puN0OwG0OOljrry119P9+54mAerjw9zjpwLX2Fw1msvLOrMe98rJOvdZ3Lv/7s/rp0/mKQKgZNFaFsvrurMc58rhutMFQKkiWTZQhGOIfGwrR8eQKgBKFEapaTie91GfcdIEwKnNorSxIh5bhGPweGwlAkD+ZUDlApRw6vqsX4KiPtr1cR0A0TeX9xCgPv5DQPYW4JSTVqrxz2/feXXs333z7+u7UY7byzqz12dR4BbA7RuBppzkn3/7/dd9/++rzz/7YsyG2rb9tVM3XLd+5SvGqaiPFskJYGoD7Npch5p+n2++/vLjWSFTg6DkOSiN+mjUJ+RDQOvN1fnxp1/+nBXSTQZTJoupG6XFW5KnoD7/U5vu5ALAenPVCIGpQeDlIeYQ6qPrLOJnvZ/a/LVCoNMiBGpdZaiPdn1cB0Cpk1Kq+ZVCYIrSm4z6lKUSAjIBMMV2+pZu/tohcGwQeL0VoD76JAKgxGhZq/lrhkCnZgjU/I06Q6iPjylAIgDG8npF3CfaJOBlnVnr4z4AAAQJgLFjUM2n/la3ATWvMqeOmdRHuz7uAwBtXx3AdOcB62MaACWuLhk3WaurDPXRrk8JTABAYm4CIMPVv+ZVpja19dR07rA+7gMAQKAAsH76me2B09jzTX2065NqAhgap7oP82ixjpKfE1CCyphJfbTr4z4AMr48E+m4ohxHxOMKEQAAkgdA7fFcbfz3hvpoMgmAWg88am2yKM1/7HmnPjYsHgTKTwBDD1K278NKN6t18w/dZ1o/aKI+d6Tr4z4ALJvWuvmjoj46QgZAiU1G89dFfTSEDYBTNhnN3wb1sRfuNwMd2mSHfp6fprdBfWyFD4A+mlwb9Wkv9C0AgMMIACAxAgBIjAAAEiMAgMTOvL8/+s2/r+/OAhs6PusP7qA+2vWRDAD190dHdex5pz42LM67/AQAoB4CAEgsRABEfQ4Q5biiHEfE43IRAOoPUrKfF5V1qFk5OC9nUR54REjjmscz9nxTH+36pJoAACQPgGPGqShTwDHHoTZeUh/t+rgPAADBAqDGr1H2PgXUuPpPvb+kPtr1KSHkBOA1BLyuO8txvnG6bukAqHGV8VisY9fb+upCfbTr4z4AANhxGQDRpoBaVxcr1McPiQCYMgZF2WQ1m7/UeEl9tOvjPgCmGhMCakEwZk1ervzbqI8+mQBokYYqIdBiHaXPJ/UpS+HqLxUAtUdNlRAY+/2VRkvqo10f9wEw1ZQQaB0EU76n19F/G/XRJRcAU9NxSrO0CIKp32Nq89e+ulAf7fq4D4DWm6xWEJzyb6pvLurzvOl5qync7wbsmmfqid5u2PPbd15N/dqpooz9+1AfLfNTvvji8uHbzZ9vXr6YlXZqMygmbqRj9bjmSMe6uHf/3Z/XT5/Mw9wClDppXq6mipurxfelPvakAyDDJvPa/KW+P/WxJX0LUHqjWDdLH8fzPurT/hbATQCUvFpYbrQIxxD52FaOjiFdAJQeGVtuNK/rznKcK4frThkAte4baxTNyzqzHvfKyTr3SRsArR4ejSmm2nqsqZ0PtfWUkDoAPDxBztr8G9SnrvDvA4jYFJmO0+u6Mx3nrSgnP+LVxvPG2qA+2lxPANGapY/j0XYVZL+5nwCiXW2ibKxdqI+eMBNAhCbyuu4sx3nldN1pJgCvV5uIG2sI9dEQNgB2NZdSGGRs+l2oj63wAaB21aHxh88N9WknVQDsa8KaG46GP/2cUZ96UgbAMU3q/eOeI6E+9RAAe9DM2qiPwMuA/fcf99+XDED/5wDCvg8AwHEIACAxAgBIjAAAEjs5AHgQCPh8ANhhAgASIwCAxIoEALcBgL/xv8MEACRGAACJFQsAbgMAX+N/hwkASKxoADAFAH6u/h0mACCx4gHAFAD4uPp3mACAxKoEAFMAoH/1bzYB8GlBgGbfVAuA7bQiBIDjbfdLjat/9Qmg1qKBTNYV+6j6LQDPAwCt+37TVwG4FQB0+qNJAPA8ANC57zeZAAgBQKv5m98CEAKATvObPAMgBACN5jd7KzAhAMzMm79j+jr9xeXDt9v/7eblC5vFAIZP+q3eM2P6w0C7DpqXCRHZQqj5OzLv1NueBpgEEM1CYOTfZr6APm4JENFC7KrfJ7GIoRDoMBHAm8Wed/WpNH9HZiHbCAJ4tXDQ+BtyCzo2CDpMBVCxOPAefsXG35Bd2Jgg6BAGaG0x8IM7yo2/Ib/AsUHQRyiglMWIn9Lz0PgbbhZ6ahgANa0dNX2fy0XvQhigtbXTpu9zfwCHEAooZR2g2QEAAAAAAAAAAAAAAAAAAAAAAAAAwMyh/wAtONO4o5PVdwAAAABJRU5ErkJggg=="


def _app_icon():
    pix = QPixmap()
    pix.loadFromData(base64.b64decode(_ICON_B64))
    return QIcon(pix)


# ── Stylesheet (Catppuccin Mocha dark theme) ───────────────────────────────────
# -- Platform
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX   = sys.platform.startswith('linux')

CAMERA_BACKEND = cv2.CAP_DSHOW if IS_WINDOWS else cv2.CAP_V4L2
DEVICE_LABEL   = "Camera #{}" if IS_WINDOWS else "/dev/video{}"

STEREO_RESOLUTIONS = [
    ("Auto detect",  None),
    ("2560 x 720",   (2560, 720)),
    ("1280 x 480",   (1280, 480)),
    ("1600 x 600",   (1600, 600)),
]

DEVICE_NAMES_STEREO = ["USB Camera", "Gearway", "HBVCAM", "OV9732", "stereo"]


APP_STYLESHEET = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}
QMenuBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
}
QMenuBar::item:selected { background-color: #313244; }
QMenu {
    background-color: #181825;
    border: 1px solid #313244;
}
QMenu::item:selected { background-color: #45475a; }
QGroupBox {
    border: 1px solid #45475a;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
    color: #89b4fa;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QListWidget {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 4px;
    outline: none;
}
QListWidget::item {
    padding: 9px 12px;
    border-bottom: 1px solid #313244;
}
QListWidget::item:selected {
    background-color: #89b4fa;
    color: #1e1e2e;
}
QListWidget::item:hover:!selected { background-color: #313244; }
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 6px 10px;
    min-width: 160px;
}
QComboBox:hover { border-color: #89b4fa; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background-color: #313244;
    border: 1px solid #45475a;
    selection-background-color: #89b4fa;
    selection-color: #1e1e2e;
}
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover  { background-color: #45475a; border-color: #89b4fa; }
QPushButton:pressed { background-color: #89b4fa; color: #1e1e2e; }
QPushButton#btn_connect {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: none;
    padding: 9px 20px;
}
QPushButton#btn_connect:hover { background-color: #94d087; }
QPushButton#btn_refresh {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
}
QPushButton#btn_refresh:hover { background-color: #74a8f0; }
QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    spacing: 2px;
    padding: 3px 6px;
}
QToolBar QToolButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 5px 10px;
    color: #cdd6f4;
}
QToolBar QToolButton:hover  { background-color: #313244; border-color: #45475a; }
QToolBar QToolButton:checked {
    background-color: #313244;
    border-color: #89b4fa;
    color: #89b4fa;
}
QToolBar::separator { background-color: #45475a; width: 1px; margin: 4px 4px; }
QStatusBar {
    background-color: #181825;
    border-top: 1px solid #313244;
    color: #a6adc8;
    font-size: 12px;
}
QStatusBar::item { border: none; }
QLabel#cam_label {
    background-color: #000;
    border: 2px solid #313244;
    border-radius: 4px;
    color: #585b70;
    font-size: 15px;
}
QLabel#cam_title {
    background-color: #181825;
    border: 1px solid #313244;
    border-radius: 3px;
    padding: 2px 8px;
    font-weight: bold;
    font-size: 12px;
    color: #89b4fa;
}
QFrame#divider {
    background-color: #313244;
    max-width: 2px;
    min-width: 2px;
}
"""


# ── Camera enumeration ─────────────────────────────────────────────────────────
_PS_DSHOW_ENUM = r"""
$src = @"
using System;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.ComTypes;
[ComImport,Guid("29840822-5B84-11D0-BD3B-00A0C911CE86"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface ICreateDevEnum{[PreserveSig]int CreateClassEnumerator([In]ref Guid p,out IEnumMoniker e,int f);}
[ComImport,Guid("62BE5D10-60EB-11d0-BD3B-00A0C911CE86")]class SDE{}
[ComImport,Guid("55272A00-42CB-11CE-8135-00AA004BB851"),InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IPropertyBag{[PreserveSig]int Read([MarshalAs(UnmanagedType.LPWStr)]string n,ref object v,object e);[PreserveSig]int Write([MarshalAs(UnmanagedType.LPWStr)]string n,ref object v);}
public class DSE{
static Guid VID=new Guid("860BB310-5D01-11d0-BD3B-00A0C911CE86");
public static string Run(){var r="";var de=(ICreateDevEnum)new SDE();IEnumMoniker em;de.CreateClassEnumerator(ref VID,out em,0);if(em==null)return "";IMoniker[]m=new IMoniker[1];int i=0;while(em.Next(1,m,IntPtr.Zero)==0){Guid bg=typeof(IPropertyBag).GUID;object bo;m[0].BindToStorage(null,null,ref bg,out bo);var pb=(IPropertyBag)bo;object v=null;pb.Read("FriendlyName",ref v,null);r+=string.Format("{0}|{1}\n",i,v);i++;}return r;}}
"@
Add-Type -TypeDefinition $src -Language CSharp
[DSE]::Run()
"""


def _dshow_enumerate():
    try:
        result = subprocess.run(
            ['powershell', '-NoProfile', '-Command', _PS_DSHOW_ENUM],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            cameras = []
            for line in result.stdout.strip().splitlines():
                line = line.strip()
                if '|' not in line:
                    continue
                idx_str, name = line.split('|', 1)
                cameras.append((int(idx_str.strip()), name.strip()))
            return cameras
    except Exception:
        pass
    return []


def list_cameras_windows():
    cameras = _dshow_enumerate()
    if cameras:
        return cameras
    result = []
    for i in range(10):
        cap = cv2.VideoCapture(i, CAMERA_BACKEND)
        if cap.isOpened():
            result.append((i, f"Camera #{i}"))
            cap.release()
    return result


def list_cameras_linux():
    import glob
    cameras = []
    for path in sorted(glob.glob("/sys/class/video4linux/video*/name")):
        try:
            name = open(path).read().strip()
            idx  = int(path.split("video")[2].split("/")[0])
            cameras.append((idx, name))
        except Exception:
            pass
    return cameras


def list_cameras():
    return list_cameras_windows() if IS_WINDOWS else list_cameras_linux()


def find_stereo_device():
    if IS_WINDOWS:
        for idx, name in _dshow_enumerate():
            if any(s.lower() in name.lower() for s in DEVICE_NAMES_STEREO):
                return idx
        for i in range(10):
            cap = cv2.VideoCapture(i, CAMERA_BACKEND)
            if not cap.isOpened():
                continue
            for total_w, h in [(2560, 720), (1280, 480), (1600, 600)]:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH,  total_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                if (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == total_w and
                        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == h):
                    cap.release()
                    return i
            cap.release()
    else:
        import glob
        candidates = []
        for path in sorted(glob.glob("/sys/class/video4linux/video*/name")):
            try:
                name = open(path).read().strip()
                if any(s.lower() in name.lower() for s in DEVICE_NAMES_STEREO):
                    idx = int(path.split("video")[2].split("/")[0])
                    candidates.append((idx, name))
            except Exception:
                pass
        for idx, _ in candidates:
            if idx % 2 == 0:
                return idx
        if candidates:
            return candidates[0][0]
    return None


# ── Camera capture thread ──────────────────────────────────────────────────────
class CameraThread(QThread):
    frame_ready = pyqtSignal(object, object, float)  # left, right, fps
    error       = pyqtSignal(str)
    opened      = pyqtSignal(int, int)               # eye_w, eye_h

    def __init__(self, device_idx, forced_res=None):
        super().__init__()
        self._device_idx = device_idx
        self._forced_res = forced_res
        self._running    = False
        self._flip_h     = False
        self._mutex      = QMutex()

    def set_flip_h(self, value: bool):
        self._mutex.lock()
        self._flip_h = value
        self._mutex.unlock()

    def stop(self):
        self._running = False
        self.wait(3000)

    def run(self):
        cap = cv2.VideoCapture(self._device_idx, CAMERA_BACKEND)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self._device_idx)
        if not cap.isOpened():
            self.error.emit(f"Tidak bisa membuka {DEVICE_LABEL.format(self._device_idx)}")
            return

        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if self._forced_res:
            total_w, h = self._forced_res  # stored as (total_width, height), not per-eye
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  total_w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        else:
            for total_w, h in [(2560, 720), (1280, 480), (1600, 600)]:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH,  total_w)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
                if (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) == total_w and
                        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) == h):
                    break

        total_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        eye_h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        eye_w   = total_w // 2

        if eye_w == 0:
            self.error.emit("Resolusi kamera tidak valid.")
            cap.release()
            return

        self.opened.emit(eye_w, eye_h)

        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1 if IS_WINDOWS else 3)
        cap.set(cv2.CAP_PROP_AUTO_WB, 1)
        for _ in range(5):
            cap.read()

        self._running = True
        frame_count = 0
        t0  = time.time()
        fps = 0.0

        while self._running:
            ret, frame = cap.read()
            if not ret:
                continue

            fh, fw = frame.shape[:2]
            if fw < eye_w * 2:
                continue

            left  = frame[:, :eye_w].copy()
            right = frame[:, eye_w:eye_w * 2].copy()

            self._mutex.lock()
            flip = self._flip_h
            self._mutex.unlock()

            if flip:
                left  = cv2.flip(left,  1)
                right = cv2.flip(right, 1)

            frame_count += 1
            elapsed = time.time() - t0
            if elapsed >= 0.5:
                fps = frame_count / elapsed
                frame_count = 0
                t0 = time.time()

            self.frame_ready.emit(left, right, fps)

        cap.release()


# ── Camera selection dialog ────────────────────────────────────────────────────
class CameraSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pilih Kamera — Dual Stereo Viewer")
        self.setMinimumSize(520, 420)
        self.selected_idx = None
        self.selected_res = None
        self._cameras     = []
        self._build_ui()
        self._refresh_cameras()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel("Gearway OV9732 — Dual Stereo Camera")
        title.setAlignment(Qt.AlignCenter)
        f = QFont()
        f.setPointSize(13)
        f.setBold(True)
        title.setFont(f)
        title.setStyleSheet("color: #89b4fa; margin-bottom: 4px;")
        layout.addWidget(title)

        subtitle = QLabel("Pilih perangkat kamera dan mode resolusi, lalu klik Hubungkan.")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(subtitle)

        # Camera list
        cam_group = QGroupBox("Kamera yang Tersedia")
        cam_layout = QVBoxLayout(cam_group)
        cam_layout.setSpacing(8)

        self.cam_list = QListWidget()
        self.cam_list.setMinimumHeight(150)
        self.cam_list.itemDoubleClicked.connect(self._on_accept)
        cam_layout.addWidget(self.cam_list)

        btn_refresh = QPushButton("  Refresh Daftar Kamera")
        btn_refresh.setObjectName("btn_refresh")
        btn_refresh.setFixedHeight(34)
        btn_refresh.clicked.connect(self._refresh_cameras)
        cam_layout.addWidget(btn_refresh)
        layout.addWidget(cam_group)

        # Resolution selector
        res_group = QGroupBox("Resolusi Frame (lebar total × tinggi)")
        res_layout = QHBoxLayout(res_group)

        res_layout.addWidget(QLabel("Mode resolusi:"))
        self.res_combo = QComboBox()
        for label, _ in STEREO_RESOLUTIONS:
            self.res_combo.addItem(label)
        res_layout.addWidget(self.res_combo)
        res_layout.addStretch()
        layout.addWidget(res_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Batal")
        btn_cancel.setFixedSize(90, 36)
        btn_cancel.clicked.connect(self.reject)

        self.btn_connect = QPushButton("Hubungkan")
        self.btn_connect.setObjectName("btn_connect")
        self.btn_connect.setFixedSize(120, 36)
        self.btn_connect.clicked.connect(self._on_accept)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_connect)
        layout.addLayout(btn_layout)

    def _refresh_cameras(self):
        self.cam_list.clear()
        loading = QListWidgetItem("  Memindai kamera...")
        loading.setForeground(QColor("#a6adc8"))
        self.cam_list.addItem(loading)
        QApplication.processEvents()

        cameras     = list_cameras()
        default_idx = find_stereo_device()

        self.cam_list.clear()
        self._cameras = cameras

        if not cameras:
            item = QListWidgetItem("  Tidak ada kamera ditemukan")
            item.setForeground(QColor("#f38ba8"))
            self.cam_list.addItem(item)
            return

        recommended = None
        for idx, name in cameras:
            is_rec = (idx == default_idx)
            badge  = "  ★ Direkomendasikan" if is_rec else ""
            item   = QListWidgetItem(f"  [{idx}]  {name}{badge}")
            item.setData(Qt.UserRole, idx)
            if is_rec:
                item.setForeground(QColor("#a6e3a1"))
                recommended = item
            self.cam_list.addItem(item)

        if recommended:
            self.cam_list.setCurrentItem(recommended)
        elif self.cam_list.count() > 0:
            self.cam_list.setCurrentRow(0)

    def _on_accept(self):
        item = self.cam_list.currentItem()
        if item is None or item.data(Qt.UserRole) is None:
            QMessageBox.warning(self, "Peringatan", "Pilih kamera yang valid terlebih dahulu.")
            return
        self.selected_idx = item.data(Qt.UserRole)
        self.selected_res = STEREO_RESOLUTIONS[self.res_combo.currentIndex()][1]
        self.accept()


# ── Single camera display widget ───────────────────────────────────────────────
class CameraView(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self._title = title
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        self.title_label = QLabel(self._title)
        self.title_label.setObjectName("cam_title")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFixedHeight(26)
        layout.addWidget(self.title_label)

        self.image_label = QLabel("Tidak ada sinyal")
        self.image_label.setObjectName("cam_label")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_label.setMinimumSize(320, 240)
        layout.addWidget(self.image_label)

    def set_frame(self, bgr_frame):
        rgb    = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        h, w   = rgb.shape[:2]
        img    = QImage(rgb.data, w, h, w * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(img).scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.image_label.setPixmap(pixmap)

    def clear(self):
        self.image_label.clear()
        self.image_label.setText("Tidak ada sinyal")

    def set_title(self, text: str):
        self.title_label.setText(text)


# ── Info overlay helper ────────────────────────────────────────────────────────
def _draw_overlay(img, lines, start_y=28):
    for i, line in enumerate(lines):
        y = start_y + i * 22
        cv2.putText(img, line, (9, y + 1), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, line, (8, y),     cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1, cv2.LINE_AA)


# ── Main window ────────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gearway OV9732 — Dual Stereo Camera Viewer")
        self.resize(1280, 580)

        self._cam_thread   = None
        self._device_idx   = None
        self._forced_res   = None
        self._eye_w        = 0
        self._eye_h        = 0
        self._screenshot_n = 0
        self._flip_h       = False
        self._show_info    = True
        self._last_left    = None
        self._last_right   = None

        self._build_ui()
        # Open camera selection dialog on startup
        self._open_camera_dialog()

    # ── UI construction ────────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        self.view_left  = CameraView("KIRI  (Left)")
        self.view_right = CameraView("KANAN  (Right)")

        divider = QFrame()
        divider.setObjectName("divider")
        divider.setFrameShape(QFrame.VLine)

        main_layout.addWidget(self.view_left)
        main_layout.addWidget(divider)
        main_layout.addWidget(self.view_right)

        self._build_menubar()
        self._build_toolbar()
        self._build_statusbar()

    def _build_menubar(self):
        mb = self.menuBar()

        # File
        m_file = mb.addMenu("&File")

        self.act_camera = QAction("&Ganti Kamera…", self)
        self.act_camera.setShortcut("Ctrl+O")
        self.act_camera.triggered.connect(self._open_camera_dialog)

        self.act_screenshot = QAction("&Screenshot", self)
        self.act_screenshot.setShortcut("Ctrl+S")
        self.act_screenshot.triggered.connect(self._take_screenshot)

        act_exit = QAction("&Keluar", self)
        act_exit.setShortcut("Ctrl+Q")
        act_exit.triggered.connect(self.close)

        m_file.addAction(self.act_camera)
        m_file.addAction(self.act_screenshot)
        m_file.addSeparator()
        m_file.addAction(act_exit)

        # View
        m_view = mb.addMenu("&Tampilan")

        self.act_flip = QAction("&Flip Horizontal", self)
        self.act_flip.setShortcut("H")
        self.act_flip.setCheckable(True)
        self.act_flip.triggered.connect(self._toggle_flip)

        self.act_info = QAction("&Info Overlay", self)
        self.act_info.setShortcut("I")
        self.act_info.setCheckable(True)
        self.act_info.setChecked(True)
        self.act_info.triggered.connect(self._toggle_info)

        self.act_fullscreen = QAction("Layar &Penuh", self)
        self.act_fullscreen.setShortcut("F")
        self.act_fullscreen.setCheckable(True)
        self.act_fullscreen.triggered.connect(self._toggle_fullscreen)

        m_view.addAction(self.act_flip)
        m_view.addAction(self.act_info)
        m_view.addSeparator()
        m_view.addAction(self.act_fullscreen)

    def _build_toolbar(self):
        tb = QToolBar("Kontrol")
        tb.setIconSize(QSize(16, 16))
        tb.setMovable(False)
        self.addToolBar(tb)

        tb.addAction(self.act_camera)
        tb.addSeparator()
        tb.addAction(self.act_screenshot)
        tb.addSeparator()
        tb.addAction(self.act_flip)
        tb.addAction(self.act_info)
        tb.addSeparator()
        tb.addAction(self.act_fullscreen)

    def _build_statusbar(self):
        sb = self.statusBar()
        sb.showMessage("Siap — belum terhubung ke kamera")

        self._lbl_fps = QLabel("  FPS: —  ")
        self._lbl_res = QLabel("")
        self._lbl_dev = QLabel("")

        sb.addPermanentWidget(self._lbl_dev)
        sb.addPermanentWidget(self._lbl_res)
        sb.addPermanentWidget(self._lbl_fps)

    # ── Camera control ─────────────────────────────────────────────────────────
    def _open_camera_dialog(self):
        self._stop_camera()
        dlg = CameraSelectDialog(self)
        if dlg.exec_() != QDialog.Accepted:
            if self._cam_thread is None:
                self.statusBar().showMessage("Belum terhubung — pilih kamera via File > Ganti Kamera")
            return
        self._start_camera(dlg.selected_idx, dlg.selected_res)

    def _start_camera(self, device_idx, forced_res):
        self._device_idx = device_idx
        self._forced_res = forced_res

        self.view_left.clear()
        self.view_right.clear()
        self.statusBar().showMessage(f"Menghubungkan ke {DEVICE_LABEL.format(device_idx)}…")

        self._cam_thread = CameraThread(device_idx, forced_res)
        self._cam_thread.frame_ready.connect(self._on_frame)
        self._cam_thread.error.connect(self._on_error)
        self._cam_thread.opened.connect(self._on_opened)
        self._cam_thread.start()

    def _stop_camera(self):
        if self._cam_thread is not None:
            self._cam_thread.stop()
            self._cam_thread = None
        self.view_left.clear()
        self.view_right.clear()
        self._lbl_fps.setText("  FPS: —  ")
        self._lbl_res.setText("")
        self._lbl_dev.setText("")
        self._last_left  = None
        self._last_right = None

    # ── Slots ──────────────────────────────────────────────────────────────────
    def _on_opened(self, eye_w, eye_h):
        self._eye_w = eye_w
        self._eye_h = eye_h
        dev = DEVICE_LABEL.format(self._device_idx)
        self._lbl_dev.setText(f"  {dev}  ")
        self._lbl_res.setText(f"  {eye_w} × {eye_h} / mata  ")
        self.statusBar().showMessage(f"Terhubung — {dev}  ({eye_w}×{eye_h} per mata)", 5000)
        self.view_left.set_title(f"KIRI   [{eye_w}×{eye_h}]")
        self.view_right.set_title(f"KANAN  [{eye_w}×{eye_h}]")

    def _on_frame(self, left, right, fps):
        self._last_left  = left
        self._last_right = right
        self._lbl_fps.setText(f"  FPS: {fps:.1f}  ")

        if self._show_info:
            left_disp  = left.copy()
            right_disp = right.copy()
            _draw_overlay(left_disp,  [f"KIRI  {self._eye_w}x{self._eye_h}", f"FPS {fps:.1f}"])
            _draw_overlay(right_disp, [f"KANAN {self._eye_w}x{self._eye_h}"])
        else:
            left_disp  = left
            right_disp = right

        self.view_left.set_frame(left_disp)
        self.view_right.set_frame(right_disp)

    def _on_error(self, msg):
        QMessageBox.critical(self, "Error Kamera", msg)
        self.statusBar().showMessage(f"Error: {msg}")
        self._lbl_fps.setText("  FPS: —  ")

    def _take_screenshot(self):
        if self._last_left is None or self._last_right is None:
            QMessageBox.information(self, "Screenshot", "Belum ada frame — hubungkan kamera terlebih dahulu.")
            return

        divider = np.zeros((self._eye_h, 4, 3), dtype=np.uint8)
        divider[:] = (0, 200, 0)
        combined = np.hstack([self._last_left, divider, self._last_right])

        default_name = f"stereo_{self._screenshot_n + 1:03d}.jpg"
        fname, _ = QFileDialog.getSaveFileName(
            self, "Simpan Screenshot", default_name,
            "JPEG (*.jpg);;PNG (*.png);;All Files (*)"
        )
        if fname:
            cv2.imwrite(fname, combined)
            self._screenshot_n += 1
            self.statusBar().showMessage(f"Screenshot disimpan: {os.path.basename(fname)}", 5000)

    def _toggle_flip(self, checked):
        self._flip_h = checked
        if self._cam_thread:
            self._cam_thread.set_flip_h(checked)

    def _toggle_info(self, checked):
        self._show_info = checked

    def _toggle_fullscreen(self, checked):
        self.showFullScreen() if checked else self.showNormal()

    def closeEvent(self, event):
        self._stop_camera()
        event.accept()


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Dual Stereo Camera Viewer")
    app.setOrganizationName("Gearway")
    app.setWindowIcon(_app_icon())
    app.setStyleSheet(APP_STYLESHEET)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
