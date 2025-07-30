from setuptools import setup, find_packages

setup(
    name='strive-ranker',
    version='2.3',
    author='Carlo Moro',
    author_email='cnmoro@gmail.com',
    description="Semantic Tokenized Ranking via Vectorization & Embeddings",
    packages=find_packages(),
    package_data={
        "strive": ["resources/*"]
    },
    include_package_data=True,
    install_requires=[
        "numpy<2",
        "nltk",
        "scikit-learn",
        "fasttext",
        "model2vec",
        "faiss-cpu",
        "bm25s"
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)