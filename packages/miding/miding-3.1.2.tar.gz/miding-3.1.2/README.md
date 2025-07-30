# Midi Neuronal Generator (miding)

This program aims to generate listenable midi sequences, attempting to create fair scores.

Sincerely thanks for keras, the neuronal network model we have applied.
In this program, we have combined a LSTM layer, a Dense layer with the activation Sigmoid and an Activation of Softmax layer before v3.0.
And after v3.1, the construction has been changed into two GRU layer and a Dense layer with the activation Softmax, due to GRU has a faster processing speed than LSTM.

### Download

Here is our website: https://github.com/JerrySkywolf/Midi-Neuronal-Generator.
This package could also be downloaded through PyPi by:

`pip install miding`

View at the webpage
* https://pypi.org/project/midi-neuronal-generator
* https://pypi.org/project/miding

### How to use our model?

For example,

`from miding import Predict, get_seed`

`Predict(seed=get_seed(), epoch=256, model_version=1751770203)`



 