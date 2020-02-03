import tensorflow as tf # deep learning library
from matplotlib import pyplot as plt # image plotting library
import numpy as np # used to extract classes from logits

# Construct model
model = tf.keras.models.Sequential([
  tf.keras.layers.Flatten(), # flatten the 28 by 28 picture to 1 by 784
  tf.keras.layers.Dense(500, activation=tf.nn.relu), # A relu layer with 500 weights
  tf.keras.layers.Dense(10, activation=tf.nn.softmax) # A softmax layer that generates probabilities
])

sgd = tf.keras.optimizers.SGD(lr=0.7) # Stochastic Gradient Descent with Learning Rate of 0.7

model.compile(optimizer=sgd,
              loss='sparse_categorical_crossentropy', # Loss function is a special version of cross entropy
              metrics=['accuracy'])

# Load data
mnist = tf.keras.datasets.mnist

(x_train, y_train),(x_test, y_test) = mnist.load_data()
x_train, x_test = x_train / 255, x_test / 255

# Train model
print("training:")
model.fit(x_train, y_train,batch_size=100, epochs=2) # trains with batch size of 100 and trains over the data 2 times
print("\ntesting:")
loss, accuracy = model.evaluate(x_test, y_test) # Checks accuracy
print("\naccuracy: {:2.2f}%".format(accuracy * 100))

def display(i):
  plt.axis('off')
  plt.imshow(x_test[i], cmap='gray')
  print("image:")
  plt.show()
  prob = np.max(model.predict(x_test[i:i+1])) * 100
  pred = np.argmax(model.predict(x_test[i:i+1]))
  print("The model is {:2.2f}% sure it is {}".format(prob, pred))
  print("real value: {}".format(y_test[i]))
  print()
print("Everything's ready. Please proceed to visualizing the predictions. ")


#@title Test Sample Number
i = 80 #@param {type:"integer"}

display(i)