# ailia Tokenizer Python API

!! CAUTION !!
“ailia” IS NOT OPEN SOURCE SOFTWARE (OSS).
As long as user complies with the conditions stated in [License Document](https://ailia.ai/license/), user may use the Software for free of charge, but the Software is basically paid software.

## About ailia Tokenizer

The ailia Tokenizer is an NLP tokenizer that can be used from Unity or C++. The tokenizer is an API for converting text into tokens (sequences of symbols) that AI can handle, or for converting tokens back into text.

Traditionally, tokenization has been performed using Pytorch's Transformers. However, since Transformers only work with Python, there has been an issue of not being able to tokenize from applications on Android or iOS.

With ailia Tokenizer, this problem is solved by directly performing NLP tokenization without using Pytorch's Transforms. This makes it possible to perform tokenization on Android and iOS as well.

Since ailia Tokenizer includes Mecab and SentencePiece, it is possible to perform complex tokenizations, such as those for BERT Japanese or Sentence Transformer, on the device.

## Install from pip

You can install the ailia SDK free evaluation package with the following command.

```
pip3 install ailia_tokenizer
```

## Install from package

You can install the ailia SDK from Package with the following command.

```
python3 bootstrap.py
pip3 install ./
```

## API specification

https://github.com/axinc-ai/ailia-sdk

