# Ntl/__init__.py
from .solver import RecaptchaSolver
from DrissionPage import ChromiumPage

def solveCaptcha():
    """Hàm public để user gọi trực tiếp mà không cần biết chi tiết class bên trong."""
    page = ChromiumPage()
    solver = RecaptchaSolver(page)
    solver.solveCaptcha()
