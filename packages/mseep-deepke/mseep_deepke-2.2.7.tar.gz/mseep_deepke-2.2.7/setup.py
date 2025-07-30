from setuptools import setup, find_packages


# with open("requirements.txt") as requirements_file:
#     requirements = requirements_file.read().splitlines()
    
setup(
    name="mseep-deepke",  
    long_description="Package managed by MseeP.ai",
    long_description_content_type="text/plain",# 打包后的包文件名
    version="2.2.7",    #版本号
    keywords=["pip", "RE","NER","AE"],    # 关键字
    description='DeepKE is a knowledge extraction toolkit for knowledge graph construction supporting low-resource, document-level and multimodal scenarios for entity, relation and attribute extraction.',  # 说明
    license="MIT",  # 许可
    url='https://github.com/zjunlp/deepke',
    author="mseep",
    author_email='zhangningyu@zju.edu.cn',
    
    maintainer="mseep",
    maintainer_email="support@skydeck.ai",include_package_data=True,
    platforms="any",
    package_dir={"": "src"},
    packages=find_packages("src"),
    # install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
