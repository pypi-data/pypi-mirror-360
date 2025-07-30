from setuptools import setup, find_packages

setup(
    name='CTkFileDialog',           
    version='0.1.5',                    
    author='Tu Nombre o Alias',
    author_email='tuemail@ejemplo.com',
    description='Selector de archivos personalizado usando CustomTkinter',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FlickGMD/CTkFileDialog',  
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',       
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    install_requires=[
        'customtkinter',
        'Pillow',
        "opencv-python",
        "CTkMessagebox",
        "CTkToolTip",
    ],
    include_package_data=True,
)

