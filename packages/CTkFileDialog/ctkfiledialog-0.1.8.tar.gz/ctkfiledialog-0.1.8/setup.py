from setuptools import setup, find_packages

setup(
    name="CTkFileDialog",
    version="0.1.8", 
    author="FlickGMD",
    description="Selector de archivos con soporte de íconos",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "CTkFileDialog": ["icons/*.png", "icons/*/*.png"],  
    },
    install_requires=[
        "opencv-python",
        "customtkinter",
        "Pillow",
        "CTkMessagebox",
        "CTkToolTip"
        ],
    python_requires='>=3.7',
)

