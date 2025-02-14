from tensorflow.keras.applications import ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# 1. 데이터 준비
train_data_dir = "./mask_train/"  # 마스크된 훈련 데이터 경로
val_data_dir = "mask_val/"         # 마스크된 검증 데이터 경로
test_data_dir = "./"               # 마스크된 테스트 데이터 경로
img_width, img_height = 128, 128
num_classes = 4  # 감정 클래스 수

# 2. ResNet50 모델 로드 및 수정
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(img_width, img_height, 3))
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation='relu')(x)
predictions = Dense(num_classes, activation='softmax')(x)
model = Model(inputs=base_model.input, outputs=predictions)

# 초기에는 기본 모델의 가중치를 고정하여 상단 레이어만 훈련
for layer in base_model.layers:
    layer.trainable = False

# 3. 모델 컴파일 및 학습
model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])

train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

train_generator = train_datagen.flow_from_directory(
    train_data_dir,
    target_size=(img_width, img_height),
    batch_size=32,
    class_mode='categorical'
)

validation_generator = train_datagen.flow_from_directory(
    val_data_dir,
    target_size=(img_width, img_height),
    batch_size=32,
    class_mode='categorical'
)

model.fit(
    train_generator,
    epochs=10,
    validation_data=validation_generator
)

# 전체 레이어를 학습 (Fine-tuning)
for layer in model.layers:
    layer.trainable = True

model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(
    train_generator,
    epochs=10,
    validation_data=validation_generator
)

# 4. 모델 평가
test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
    test_data_dir,  # 테스트 데이터 경로
    target_size=(img_width, img_height),
    batch_size=32,
    class_mode='categorical'
)

loss, accuracy = model.evaluate(test_generator)
print('Test accuracy:', accuracy)

# 5. 모델 배포 (모델 저장)
model.save('emotion_classifier_resnet50.h5')
