from setuptools import setup, find_packages
from pathlib import Path

# Definir la ruta base
base_dir = Path(__file__).resolve().parent

# Leer el contenido de los archivos externos
requirements_file = base_dir / 'requirements.txt'
readme_file = base_dir / 'README.md'

requirements = requirements_file.read_text().splitlines() if requirements_file.exists() else []
# long_description = readme_file.read_text() if readme_file.exists() else ""

version="1.3.35"

setup(
    name="pywebwizard",
    version=version,
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    description="Definitive Python 3 library for automatize Web Browser actions...",
    # include_package_data=True,
    author="ConnorLilHomer",
    author_email="info@parendum.com",
    maintainer="ConnorLilHomer",
    maintainer_email="info@parendum.com",
    url="https://gitlab.com/connorlilhomer/pywebwizard",
    download_url=f"https://gitlab.com/connorlilhomer/pywebwizard/-/archive/main/webwizard-{version}.tar.gz",
    packages=find_packages(exclude=["scripts", "devtools", "spells", "screenshots"]),
    install_requires=requirements or [
        'selenium',
        'requests',
        'pyyaml'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    license="MIT",
    keywords=[
        "web", "automation", "browser", "scraping", "python", "selenium",
        "headless", "browsing", "task", "data", "extraction", "multi-browser",
        "support", "workflow", "UI", "testing", "YAML", "configuration",
        "cross-platform", "form", "filling", "Selenium", "integration",
        "dynamic", "web", "interactions", "automated", "navigation",
        "control", "navegador", "extracción", "datos", "pruebas",
        "automatización", "interacciones", "sin", "cabeza", "automatización de navegadores",
        "scrape", "bot", "robot", "web scraping", "crawler", "form automation",
        "dom manipulation", "page load automation", "multi-tab support", "parallel tasks",
        "captcha bypass", "cookies management", "session handling", "proxy support",
        "task scheduling", "ciberseguridad", "automatización avanzada", "análisis de datos",
        "control remoto de navegadores", "descarga masiva", "gestión de sesiones", "trabajo en paralelo",
        "soporte de proxies", "web crawling", "extracción avanzada"
    ],
    platforms=["Windows", "Linux", "MacOS"],
    python_requires='>=3.8',
)

