import os

current_dir = os.path.abspath(os.getcwd())

# cria nova pasta para cachorros e gatos atendendo a estrutura do Keras/Tensorflow
folder = "\\cats_and_dogs_dataset"
train_folder = current_dir + folder + "\\train"
val_folder = current_dir + folder + "\\validation"
test_folder = current_dir + folder + "\\test"

import tensorflow as tf


'''print(tf.__version__)
print(tf.econfig.list_physical_devics('GPU'))'''

from tensorflow.keras.utils import image_dataset_from_directory

train_dataset = image_dataset_from_directory(train_folder,
                                             image_size=(180, 180),
                                             batch_size=32)

validation_dataset = image_dataset_from_directory(val_folder,
                                                  image_size=(180, 180),
                                                  batch_size=32)

test_dataset = image_dataset_from_directory(test_folder,
                                            image_size=(180, 180),
                                            batch_size=32)

for data_batch, labels_batch in train_dataset:
    print("data batch shape:", data_batch.shape)
    print("labels batch shape:", labels_batch.shape)
    print(data_batch[0].shape)
    break

from matplotlib import pyplot as plt


def showSingleImage(img, title, size):
    fig, axis = plt.subplots(figsize=size)

    axis.imshow(img, 'gray')
    axis.set_title(title, fontdict={'fontsize': 20, 'fontweight': 'medium'})
    plt.show()


def showMultipleImages(imgsArray, titlesArray, size, x, y):
    if (x < 1 or y < 1):
        print("ERRO: X e Y não podem ser zero ou abaixo de zero!")
        return
    elif (x == 1 and y == 1):
        showSingleImage(imgsArray, titlesArray)
    elif (x == 1):
        fig, axis = plt.subplots(y, figsize=size)
        yId = 0
        for img in imgsArray:
            axis[yId].imshow(img, 'gray')
            axis[yId].set_anchor('NW')
            axis[yId].set_title(titlesArray[yId], fontdict={'fontsize': 18, 'fontweight': 'medium'}, pad=10)

            yId += 1
    elif (y == 1):
        fig, axis = plt.subplots(1, x, figsize=size)
        fig.suptitle(titlesArray)
        xId = 0
        for img in imgsArray:
            axis[xId].imshow(img, 'gray')
            axis[xId].set_anchor('NW')
            axis[xId].set_title(titlesArray[xId], fontdict={'fontsize': 18, 'fontweight': 'medium'}, pad=10)

            xId += 1
    else:
        fig, axis = plt.subplots(y, x, figsize=size)
        xId, yId, titleId = 0, 0, 0
        for img in imgsArray:
            axis[yId, xId].set_title(titlesArray[titleId], fontdict={'fontsize': 18, 'fontweight': 'medium'}, pad=10)
            axis[yId, xId].set_anchor('NW')
            axis[yId, xId].imshow(img, 'gray')
            if (len(titlesArray[titleId]) == 0):
                axis[yId, xId].axis('off')

            titleId += 1
            xId += 1
            if xId == x:
                xId = 0
                yId += 1
    plt.show()


from tensorflow import keras
from tensorflow.keras.layers import Rescaling
from tensorflow.keras.layers import RandomFlip, RandomRotation, RandomZoom

dt_model = keras.Sequential(
    [
        Rescaling(scale=1.0 / 255),
        RandomFlip("horizontal"),
        RandomRotation(0.1),
        RandomZoom(0.2),
    ]
)

images_list = []
for images, labels in train_dataset.take(1):
    first_image = images[0].numpy().astype("uint8")
    images_list.append(first_image)
    for i in range(8):
        augmented_image = dt_model(images[0])
        images_list.append(augmented_image)

titles = [str(i) for i in range(9)]
showMultipleImages(images_list, titles, (10, 11), 3, 3)

from tensorflow import keras
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.layers import RandomFlip, RandomRotation, RandomZoom
from tensorflow.keras.layers import Rescaling

model = keras.Sequential(
    [
        Rescaling(scale=1.0 / 255),
        RandomFlip("horizontal"),
        RandomRotation(0.1),
        RandomZoom(0.2),
    ]
)

model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(64, kernel_size=(3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(128, kernel_size=(3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(256, kernel_size=(3, 3), activation='relu'))
model.add(BatchNormalization())
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(1, activation="sigmoid"))

model.compile(loss="binary_crossentropy",
              optimizer="adam",
              metrics=["accuracy"])

from tensorflow.keras.callbacks import ModelCheckpoint

callbacks = [
    ModelCheckpoint(
        filepath="model1.keras",
        save_best_only=True,
        monitor="val_loss"
    )
]

history = model.fit(
    train_dataset,
    epochs=100,
    validation_data=validation_dataset,
    callbacks=callbacks)

import matplotlib.pyplot as plt

accuracy = history.history["accuracy"]
val_accuracy = history.history["val_accuracy"]
loss = history.history["loss"]
val_loss = history.history["val_loss"]
epochs = range(1, len(accuracy) + 1)
plt.plot(epochs, accuracy, "r", label="Treino acc")
plt.plot(epochs, val_accuracy, "b", label="Val acc")
plt.xlabel("Épocas")
plt.ylabel("%s")
plt.title("Acurácia de Treino e Validação")
plt.legend()
plt.figure()
plt.plot(epochs, loss, "r", label="Treino loss")
plt.plot(epochs, val_loss, "b", label="Val loss")
plt.xlabel("Épocas")
plt.ylabel("%s")
plt.title("Loss de Treino e Validação")
plt.legend()
plt.show()

from tensorflow import keras
model = keras.models.load_model("model.keras")

test_loss, test_acc = model.evaluate(test_dataset)
print(f"Test accuracy: {test_acc:.3f}")

from matplotlib import pyplot as plt


def showSingleImage(img, title, size):
    fig, axis = plt.subplots(figsize=size)

    axis.imshow(img, 'gray')
    axis.set_title(title, fontdict={'fontsize': 20, 'fontweight': 'medium'})
    plt.show()


import cv2

img_name = "./download.jpeg"
ada_img = cv2.imread(img_name)
ada_img = cv2.cvtColor(ada_img, cv2.COLOR_BGR2RGB)
ada_img = cv2.resize(ada_img, (180, 180), interpolation=cv2.INTER_AREA)

showSingleImage(ada_img, "ada", (12, 8))

from keras.preprocessing import image
import numpy as np

ada_img = image.load_img(img_name, target_size=(180, 180))
x = image.img_to_array(ada_img)
x = np.expand_dims(x, axis=0)
pred = (model.predict(x) > 0.5).astype('int32')[0][0]

if pred == 1:
    print("Não Tem")
else:
    print("tem")

print(model.predict(x))
