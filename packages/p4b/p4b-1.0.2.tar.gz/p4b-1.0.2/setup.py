from setuptools import setup, find_packages

setup(
    name="p4b",
    author="p4b-admin",
    version="1.0.2",
    description="god bless you.",
    packages=find_packages(),
    install_requires=[
        "rich==14.0.0",
        "keyboard>=0.13.5",
        "pyperclip>=1.9.0",
        "pillow>=11.2.1",
        "pyautogui>=0.9.54",
        "setuptools==66.1.1",
        "google-generativeai==0.8.5",
        "openai==1.83.0",
        "pythonw==3.0.3",
        "setproctitle==1.3.6",
    ],
    entry_points={
        "console_scripts": [
            "p4b=p4b.core:main",
        ],
    },
    package_data={
        "p4b": ["*.pyd", "*.py"],
    },
    include_package_data=True,
    zip_safe=False,
)