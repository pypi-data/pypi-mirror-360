# keynet-train

MLflow와 통합된 모델 훈련 유틸리티

## 설치

```bash
pip install keynet-train
```

## 주요 기능

### 🚀 자동화된 훈련 API

- 모델에서 자동으로 스키마 추론
- PyTorch 모델을 ONNX로 자동 변환
- MLflow에 자동 로깅 및 버전 관리

### 📊 지원 프레임워크

- PyTorch (TorchScript, ONNX 변환)
- ONNX (네이티브 지원)
- 다중 입력/출력 모델 지원

### 🔧 MLflow 통합

- 실험 자동 생성 및 관리
- 모델 아티팩트 자동 저장
- 메트릭 및 파라미터 추적

## 🚀 기본 사용법

```python
from keynet_train import trace
import torch

# 🎯 decorator에 샘플 입력을 제공하고, 함수에서는 모델만 반환
@trace("my_experiment", torch.randn(1, 3, 224, 224))
def train_model():
    model = MyModel()

    # 학습 코드...
    for epoch in range(10):
        # 실제 학습 로직
        pass

    return model  # ⚠️ 반드시 torch.nn.Module만 반환
```

## 📋 반환값 제약사항

**`@trace` 데코레이터를 사용하는 함수는 반드시 `torch.nn.Module` 객체만 반환해야 합니다.**

### ✅ 올바른 사용법

```python
@trace("experiment", torch.randn(1, 784))
def train_mnist():
    model = torch.nn.Sequential(
        torch.nn.Linear(784, 128),
        torch.nn.ReLU(),
        torch.nn.Linear(128, 10)
    )

    # 훈련 로직
    optimizer = torch.optim.Adam(model.parameters())
    for epoch in range(100):
        # 실제 훈련...
        loss = train_one_epoch(model, optimizer, train_loader)

        # 메트릭은 mlflow.log_* 함수로 기록
        mlflow.log_metric("train_loss", loss, step=epoch)

    return model  # 🎯 모델만 반환!
```

### ❌ 잘못된 사용법들

```python
@trace("experiment", torch.randn(1, 784))
def wrong_usage1():
    model = MyModel()
    loss = train(model)
    return model, loss  # ❌ 튜플 반환 불가

@trace("experiment", torch.randn(1, 784))
def wrong_usage2():
    model = MyModel()
    train(model)
    return {
        "model": model,
        "accuracy": 0.95
    }  # ❌ 딕셔너리 반환 불가

@trace("experiment", torch.randn(1, 784))
def wrong_usage3():
    model = MyModel()
    train(model)
    return "model_saved.pth"  # ❌ 문자열 반환 불가
```

### 💡 왜 이런 제약이 있나요?

`@trace` 데코레이터는 내부적으로 다음 작업을 자동화합니다:

1. **MLflow 모델 로깅**: `mlflow.pytorch.log_model(pytorch_model=model, ...)`
2. **ONNX 변환**: `torch.onnx.export(model, ...)`
3. **Triton 배포**: 자동 `config.pbtxt` 생성

이 모든 작업이 `torch.nn.Module` 객체를 필요로 하므로, 다른 타입의 반환값은 지원하지 않습니다.

## 📝 ONNX 모델 입출력 파라미터명 규칙

`@trace` 데코레이터를 사용할 때 생성되는 ONNX 모델의 입출력 파라미터명은 다음과 같이 결정됩니다:

### 입력 파라미터 (Inputs)

```python
# ✅ Dictionary 형태로 입력하면 키 이름을 사용 (권장)
@trace("my_experiment", {"image": torch.randn(1, 3, 224, 224), "label": torch.randn(1, 10)})
def train_model():
    # 생성되는 ONNX의 입력명: "image", "label"
    ...

# ✅ 단일 텐서로 입력하면 자동 생성
@trace("my_experiment", torch.randn(1, 3, 224, 224))
def train_model():
    # 생성되는 ONNX의 입력명: "input_0"
    ...
```

### 출력 파라미터 (Outputs)

```python
# 출력명은 항상 자동 생성됩니다
@trace("my_experiment", torch.randn(1, 3, 224, 224))
def train_model():
    # 단일 출력: "output_0"
    return model

# 다중 출력 모델의 경우
def train_multi_output_model():
    class MultiOutputModel(torch.nn.Module):
        def forward(self, x):
            return output1, output2  # 튜플 반환

    # 실제로는 MLflow가 튜플을 하나의 배열로 처리하여 "output_0"만 생성됨
    return model
```

### ⚠️ 중요한 제한사항

- **지원되는 입력 형태**: `torch.Tensor` 또는 `Dict[str, torch.Tensor]`만 지원
- **튜플 입력 미지원**: `(tensor1, tensor2)` 형태의 튜플 입력은 현재 지원되지 않음
- **다중 출력 처리**: PyTorch 모델이 튜플로 다중 출력을 반환해도 MLflow signature 추론에 의해 `output_0` 하나로 처리됨
- **MLflow 의존성**: 파라미터명 생성은 MLflow의 자동 signature 추론에 의존하므로 일부 제한사항이 있음

### 💡 권장사항

```python
# 🎯 최적의 사용법: Dictionary 입력으로 명시적인 이름 지정
@trace("experiment", {
    "image": torch.randn(1, 3, 224, 224),
    "mask": torch.randn(1, 1, 224, 224)
})
def train_model():
    # 생성되는 config.pbtxt에서 명확한 입력명 확인 가능:
    # input { name: "image", data_type: TYPE_FP32, dims: [-1, 3, 224, 224] }
    # input { name: "mask", data_type: TYPE_FP32, dims: [-1, 1, 224, 224] }
    return model
```

> **Note:** 생성된 ONNX 모델은 Triton Inference Server 배포 시 자동으로 `config.pbtxt` 파일이 생성되어 정확한 입출력 스키마를 확인할 수 있습니다.

### 다중 입력 모델

```python
@trace("multi_input_exp", {
    "image": torch.randn(1, 3, 224, 224),
    "mask": torch.randn(1, 1, 224, 224)
})
def train_multi_input():
    model = MultiInputModel()

    # 모델이 여러 입력을 받는 경우
    class MultiInputModel(torch.nn.Module):
        def forward(self, image, mask):
            # image와 mask를 함께 처리
            combined = torch.cat([image, mask], dim=1)
            return self.classifier(combined)

    # 훈련 로직...
    return model
```

## 라이선스

MIT License
