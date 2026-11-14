
import torch
import torch.nn as nn


class CrackCNN(nn.Module):
    """
    Lightweight CNN for binary concrete crack classification.
    Input: RGB images of shape (3, 128, 128)
    Output: 2 class logits
    """

    def __init__(self, num_classes=2):
        super().__init__()

        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),

            # Block 4
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),

            nn.AdaptiveAvgPool2d((1, 1)),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.4),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


if __name__ == "__main__":
    model = CrackCNN()

    sample = torch.randn(2, 3, 128, 128)
    output = model(sample)

    print("Model:", model.__class__.__name__)
    print("Input shape:", sample.shape)
    print("Output shape:", output.shape)
    print("Parameters:", sum(p.numel() for p in model.parameters()))
    print("CNN model test successful!")
