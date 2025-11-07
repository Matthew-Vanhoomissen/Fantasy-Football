import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load the dataset with player comparison pairs
pairs_df = pd.read_csv("../data/player_pairs_dataset.csv")

# Separate features from target variable
# Exclude 'target' (what we're predicting) and actual points (only used for creating target)
feature_cols = [col for col in pairs_df.columns if col not in ['target', 'p1_actual_points', 'p2_actual_points']]
X = pairs_df[feature_cols].values  # Input features as numpy array
y = pairs_df['target'].values      # Target labels (1 if player1 better, 0 if player2 better)

print(f"Dataset size: {len(X)} pairs")
print(f"Number of features: {len(feature_cols)}")

# Standardize features to have mean=0 and std=1 (helps neural network train better)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data into training (80%) and testing (20%) sets
# stratify=y ensures both sets have similar class distribution
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training samples: {len(X_train)}, Test samples: {len(X_test)}")

# Convert numpy arrays to PyTorch tensors (required for PyTorch)
X_train_tensor = torch.FloatTensor(X_train)
y_train_tensor = torch.FloatTensor(y_train).unsqueeze(1)  # unsqueeze adds dimension for batch processing
X_test_tensor = torch.FloatTensor(X_test)
y_test_tensor = torch.FloatTensor(y_test).unsqueeze(1)


# Custom Dataset class for PyTorch DataLoader
class PlayerPairDataset(Dataset):
    def __init__(self, X, y):
        self.X = X  # Store features
        self.y = y  # Store labels
    
    def __len__(self):
        # Return total number of samples
        return len(self.X)
    
    def __getitem__(self, idx):
        # Return a single sample (features, label) at given index
        return self.X[idx], self.y[idx]


# Create dataset objects
train_dataset = PlayerPairDataset(X_train_tensor, y_train_tensor)
test_dataset = PlayerPairDataset(X_test_tensor, y_test_tensor)

# DataLoader handles batching and shuffling
# batch_size=128 means process 128 samples at once
# shuffle=True randomizes order each epoch (helps training)
train_loader = DataLoader(train_dataset, batch_size=512, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=512, shuffle=False)


# Define the Neural Network architecture
class StartSitModel(nn.Module):
    def __init__(self, input_size):
        super(StartSitModel, self).__init__()
        # Sequential means layers are applied in order
        self.network = nn.Sequential(
            # Layer 1: input_size -> 256 neurons
            nn.Linear(input_size, 256),  # Fully connected layer
            nn.ReLU(),                    # Activation function (adds non-linearity)
            nn.BatchNorm1d(256),          # Normalizes activations (stabilizes training)
            nn.Dropout(0.3),              # Randomly drops 30% of neurons (prevents overfitting)
            
            # Layer 2: 256 -> 128 neurons
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.25),             # Drop 25% of neurons
            
            # Layer 3: 128 -> 64 neurons
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2),              # Drop 20% of neurons
            
            # Layer 4: 64 -> 32 neurons
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.1),              # Drop 10% of neurons
            
            # Output layer: 32 -> 1 output (probability)
            nn.Linear(32, 1),
            nn.Sigmoid()                  # Squashes output to 0-1 range (probability)
        )
    
    def forward(self, x):
        # Defines how data flows through the network
        return self.network(x)


# Initialize the model with correct input size
input_size = X_train.shape[1]  # Number of features
model = StartSitModel(input_size)

# Loss function: measures how wrong predictions are
# BCELoss = Binary Cross Entropy (for binary classification)
criterion = nn.BCELoss()

# Optimizer: adjusts model weights to minimize loss
# Adam is an advanced version of gradient descent
# lr=0.001 is learning rate (how big the weight updates are)
# weight_decay=1e-5 adds regularization to prevent overfitting
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)

# Learning rate scheduler: reduces learning rate when accuracy plateaus
# mode='max' means we're tracking accuracy (want to maximize)
# patience=5 means wait 5 epochs before reducing lr
# factor=0.5 means multiply lr by 0.5 when reducing
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=5, factor=0.5)

# Training loop
epochs = 50  # Number of times to go through entire dataset
best_accuracy = 0  # Track best validation accuracy

for epoch in range(epochs):
    # === TRAINING PHASE ===
    model.train()  # Set model to training mode (enables dropout, batch norm updates)
    train_loss = 0  # Accumulate loss for this epoch
    
    # Loop through batches of training data
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()  # Reset gradients to zero (required each iteration)
        outputs = model(X_batch)  # Forward pass: get predictions
        loss = criterion(outputs, y_batch)  # Calculate loss (how wrong we are)
        loss.backward()  # Backward pass: calculate gradients
        optimizer.step()  # Update weights based on gradients
        train_loss += loss.item()  # Accumulate loss for logging
    
    # === VALIDATION PHASE ===
    model.eval()  # Set model to evaluation mode (disables dropout, batch norm training)
    correct = 0  # Count correct predictions
    total = 0    # Count total predictions
    
    # Don't calculate gradients during validation (saves memory and time)
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            outputs = model(X_batch)  # Get predictions
            predicted = (outputs > 0.5).float()  # Convert probabilities to binary (0 or 1)
            total += y_batch.size(0)  # Count samples in batch
            correct += (predicted == y_batch).sum().item()  # Count correct predictions
    
    # Calculate accuracy as percentage
    accuracy = 100 * correct / total
    
    # Update learning rate based on accuracy
    scheduler.step(accuracy)
    
    # Save model if this is the best accuracy so far
    if accuracy > best_accuracy:
        best_accuracy = accuracy
        torch.save({
            'model_state_dict': model.state_dict(),  # Model weights
            'scaler': scaler,  # Feature scaler (needed for predictions)
            'feature_cols': feature_cols,  # Feature names (for reference)
            'input_size': input_size  # Input dimension (needed to recreate model)
        }, '../models/start_sit_model.pth')
    
    # Print progress every 10 epochs
    if (epoch + 1) % 5 == 0:
        print(f'Epoch [{epoch+1}/{epochs}], Loss: {train_loss/len(train_loader):.4f}, Accuracy: {accuracy:.2f}%, Best: {best_accuracy:.2f}%')

print(f'\n✅ Best Accuracy: {best_accuracy:.2f}%')
print('Model saved to ../models/start_sit_model.pth')