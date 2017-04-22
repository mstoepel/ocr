import os
import numpy as np
import pandas as pd
from keras.models import Sequential, model_from_json, Model
from sklearn.utils import shuffle
from keras.models import Sequential, model_from_json, Model
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D, ZeroPadding2D
from keras.layers.normalization import BatchNormalization
import pandas as pd
import numpy as np
from sklearn.utils import shuffle


fp_train = "training.csv"

df = pd.read_csv(fp_train)

def load(test=False,cols=None):
    df = pd.read_csv(fp_train)
    df['pixels'] = df['pixels'].apply(lambda im: np.fromstring(im,sep=' '))

    print(df.count())

    X = np.vstack(df['pixels'].values) / 255.
    X = X.astype(np.float32)

    if not test:
        y = df[df.columns[:]].drop(['filename','pixels'],axis=1).values
        # y = y.drop(['filename','pixels'],axis=1)
        # y = (y-48) / 48
        X,y = shuffle(X,y,random_state=311)
        # y = y.astype(np.float32)
    else:
        y = None

    return X, y

X, y = load()

def load2d(test=False,cols=None):
    X, y = load(test=test)
    X = X.reshape(-1,765,990,1)
    return X , y

X, y = load2d()


batch_size = 100
nb_classes = 20
nb_epoch = 250
img_rows, img_cols = 765, 990
im_channels = 3
nb_filters1 = 12
nb_filters2 = 24
nb_filters3 = 48
nb_filters4 = 64
nb_pool = 3
nb_conv = 3


net1 = Sequential()
net1.add(Convolution2D(nb_filters1, nb_conv, nb_conv, border_mode='valid', input_shape=(img_rows,img_cols,1)))
convout1 = Activation('relu')
net1.add(convout1)
net1.add(MaxPooling2D(pool_size=(nb_pool,nb_pool)))
net1.add(Convolution2D(nb_filters2, nb_conv, nb_conv))
convout2 = Activation('relu')
net1.add(convout2)
net1.add(MaxPooling2D(pool_size=(nb_pool,nb_pool))) #new
net1.add(Convolution2D(nb_filters3, nb_conv, nb_conv)) #new
convout3 = Activation('relu') #new
net1.add(BatchNormalization())
net1.add(convout3) #new
net1.add(MaxPooling2D(pool_size=(nb_pool,nb_pool)))
net1.add(Dropout(0.25))

net1.add(Flatten())
net1.add(Dense(128))
net1.add(Activation('relu'))
net1.add(Dropout(0.5))
net1.add(Dense(3*nb_classes))
net1.add(Dense(2*nb_classes))
net1.add(Dense(nb_classes))
net1.add(Activation('softmax'))
net1.compile(loss='categorical_crossentropy',optimizer='adadelta',metrics=['accuracy'])

net1.fit(X,y)