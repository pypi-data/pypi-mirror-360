import torch

class Node:
    def __init__(self, input_size, output_size, init_type, scale, device):
        if init_type == 'he':
            stddev = torch.sqrt(torch.tensor(2 / input_size, device=device))
        elif init_type == 'xavier':
            stddev = torch.sqrt(torch.tensor(1 / input_size, device=device))
        else:
            stddev = scale
        self.w = torch.normal(0, stddev, (input_size, output_size), device=device)
        self.b = torch.zeros(1, output_size, device=device)


# Activation Functions

def Identity(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return X

def Tanh(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return (torch.exp(X) - torch.exp(-X)) / (torch.exp(X) + torch.exp(-X))

def Sigmoid(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return 1 / (1 + torch.exp(-X))

def ReLU(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return torch.maximum(torch.tensor(0.0, device=device), X)

def LeakyReLU(X, device='cpu', alpha=0.01):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return torch.where(X > 0, X, alpha * X)

def GaussianErrorLinearUnit(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return 0.5 * X * (1 + torch.tanh(torch.sqrt(torch.tensor(2 / torch.pi, device=device)) * (X + 0.044715 * torch.pow(X, 3))))

def Swish(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return X * (1 / (1 + torch.exp(-X)))

def Softmax(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    e_x = torch.exp(X - torch.max(X))
    return e_x / e_x.sum()

def BinaryStep(X, device='cpu'):
    if not isinstance(X, torch.Tensor):
        raise ValueError("Error: X must be a torch.Tensor.")
    X = (X.float()).to(device)
    return (X > 0).int()



# Loss Functions

def CrossEntropy(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("Error: X and Y must be a torch.Tensor.")
    X = (X.float()).to(device)
    Y = (Y.float()).to(device)
    import torch.nn.functional as F
    return F.cross_entropy(X, Y.to(torch.long).to(device))

def MeanSquaredError(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("Error: X and Y must be a torch.Tensor.")
    X = (X.float()).to(device)
    Y = (Y.float()).to(device)
    return torch.mean((Y - X)**2)

def MeanAbsoluteError(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("Error: X and Y must be a torch.Tensor.")
    X = (X.float()).to(device)
    Y = (Y.float()).to(device)
    return torch.mean(torch.abs((Y - X)))

def CrossCategoricalEntropy(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.float().to(device)
    Y = Y.float().to(device)
    import torch.nn.functional as F
    log_probs = F.log_softmax(X, dim=1)
    loss = -torch.sum(Y * log_probs, dim=1)
    return torch.mean(loss)

def BinaryCrossEntropy(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.float().to(device)
    Y = Y.float().to(device)
    X = torch.clamp(X, 1e-7, 1 - 1e-7)
    loss = -(Y * torch.log(X) + (1 - Y) * torch.log(1 - X))
    return torch.mean(loss)

def KullbackLeiblerDivergence(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = torch.clamp(X, 1e-7, 1.0)
    Y = torch.clamp(Y, 1e-7, 1.0)
    X = X.float().to(device)
    Y = Y.float().to(device)
    return torch.mean(torch.sum(Y * (torch.log(Y) - torch.log(X)), dim=1))

def CosineLoss(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.float().to(device)
    Y = Y.float().to(device)
    return 1 - torch.nn.functional.cosine_similarity(X, Y).mean()


# Metric Functions
def Accuracy(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.float().to(device)
    Y = Y.float().to(device)
    X = X.argmax(dim=1)
    correct = (X == Y).sum().item()
    total = Y.size(0)
    return correct / total

def Precision(X, Y, positive_class=1, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.to(device)
    Y = Y.to(device)
    X = X.argmax(dim=1)
    tp = ((X == positive_class) & (Y == positive_class)).sum().item()
    fp = ((X == positive_class) & (Y != positive_class)).sum().item()
    if tp + fp == 0:
        return 0.0
    return tp / (tp + fp)

def Recall(X, Y, positive_class=1, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.to(device)
    Y = Y.to(device)
    X = X.argmax(dim=1)
    tp = ((X == positive_class) & (Y == positive_class)).sum().item()
    fn = ((X != positive_class) & (Y == positive_class)).sum().item()
    if tp + fn == 0:
        return 0.0
    return tp / (tp + fn)

def F1Score(X, Y, positive_class=1, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    p = Precision(X, Y, positive_class, device)
    r = Recall(X, Y, positive_class, device)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)

def ConfusionMatrix(X, Y, num_classes, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.to(device)
    Y = Y.to(device)
    X = X.argmax(dim=1)
    cm = torch.zeros((num_classes, num_classes), dtype=torch.int64, device=device)
    for t, p in zip(Y, X):
        cm[t.long(), p.long()] += 1
    return cm

def IoU(X, Y, threshold=0.5, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.to(device)
    Y = Y.to(device)
    pred_bin = (X > threshold).float()
    intersection = (pred_bin * Y).sum().item()
    union = pred_bin.sum().item() + Y.sum().item() - intersection
    if union == 0:
        return 1.0
    return intersection / union

def R2Score(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    X = X.to(device).view(-1)
    Y = Y.to(device).view(-1)
    ss_res = ((Y - X) ** 2).sum()
    ss_tot = ((Y - Y.mean()) ** 2).sum()
    if ss_tot.item() == 0.0:
        return 1.0
    return 1 - ss_res.item() / ss_tot.item()

def MeanAbsolutePercentageError(X, Y, device='cpu'):
    if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
        raise ValueError("X and Y must be torch.Tensor.")
    epsilon = 1e-8
    try:
        epsilon = float(epsilon)
    except Exception:
        raise ValueError(f"epsilon must be float-like, got {type(epsilon)}: {epsilon}")

    X = X.to(device).view(-1)
    Y = Y.to(device).view(-1)
    result = (torch.abs((Y - X) / (Y + epsilon))).mean().item() * 100
    return result

from typing import Callable
class GEO:
    def __init__(self, layer_size: list[int], device: str='cpu', init_type: str='he', scale: int=2, hidden_fn: Callable=LeakyReLU, output_fn: Callable=Sigmoid, loss_fn: Callable=MeanSquaredError, metric: Callable=Accuracy):
        self.device = device
        self.layer_size = layer_size
        self.loss_fn = loss_fn
        self.hidden_fn = hidden_fn
        self.output_fn = output_fn
        self.metric = metric
        self.init_type = init_type
        self.loss_history = []

        if len(self.layer_size) < 2:
            raise ValueError('Error: Expected at least 2 layers (input and output).')
        
        if init_type not in ['xavier', 'he'] and (not scale or scale <= 0):
            raise ValueError("Error: Expected init_type to be 'xavier', 'he' or 'none'. If 'none', then scale must be > 0")

        if self.device not in ['cuda', 'cpu']:
            raise ValueError('Error: Device must be cuda (for gpu) or cpu.')
        
        try:
            test_tensor = torch.tensor([[1], [1], [1]])
            self.hidden_fn(test_tensor, self.device)
            self.output_fn(test_tensor, self.device)
            self.loss_fn(test_tensor, test_tensor, self.device)
            self.metric(test_tensor, test_tensor, self.device)
        except:
            raise ValueError('Error: hidden_fn, output_fn, loss_fn and metric must be valid functions.')

        self.layers: list[Node] = []
        for i in range(1, len(layer_size)):
            self.layers.append(Node(layer_size[i-1], layer_size[i], init_type, scale, device))

    def mutate(self, X: torch.Tensor, mr: float) -> torch.Tensor:
        return X + torch.normal(0, mr, X.shape, device=self.device)

    def reproduce(self, p1, p2):
        return (p1 + 0.5*p2) / 1.5

    def CalculateLoss(self, X: torch.Tensor, Y: torch.Tensor) -> float:
        if not isinstance(Y, torch.Tensor):
            raise ValueError("Error: Y must be a torch.Tensor.")
        Y = (Y.float()).to(self.device)

        loss = self.loss_fn(self.forward(X), Y)
        return loss.item() if isinstance(loss, torch.Tensor) else loss
    
    def CalculateMetric(self, X: torch.Tensor, Y: torch.Tensor) -> float:
        if not isinstance(Y, torch.Tensor):
            raise ValueError("Error: Y must be a torch.Tensor.")
        Y = (Y.float()).to(self.device)

        metric = self.metric(self.forward(X), Y)
        return metric.item() if isinstance(metric, torch.Tensor) else metric

    def evolve(self, X: torch.Tensor, Y: torch.Tensor, mr: float=0.1, dr: float=0.999, generations: int=1000, population: int=50, batch_size=None, progress_style: str='tqdm', early_stop=None, optim_mr: bool=False, threshold: int=50) -> None:
        if not isinstance(X, torch.Tensor) or not isinstance(Y, torch.Tensor):
            raise ValueError("Error: X and Y must be a torch.Tensor.")
        X = (X.float()).to(self.device)
        Y = (Y.float()).to(self.device)
        
        x_batch = X
        y_batch = Y

        best = [float('inf'), None, None]
        prev_loss = float('inf')

        n = 0

        if batch_size and (not isinstance(batch_size, int) or batch_size <= 0):
            raise ValueError(f"Error: batch_size must be either >= 1 or None.")

        if progress_style not in ['tqdm', 'rich', 'halo']:
            raise ValueError(f"Error: progress_style must be tqdm, rich or halo.")

        if population < 2 or generations < 0:
            raise ValueError("Error: Training not possible. Population must be >=2 and generations >=1.")
        else:
            progress = None
            spinner = None
            desc = 'Evolving'
            if progress_style == 'tqdm':
                from tqdm.auto import tqdm
                progress = tqdm(range(generations), desc=(desc+': '))
            elif progress_style == 'rich':
                from rich.progress import track
                progress = track(range(generations), description=(desc+': '))
            elif progress_style == 'halo':
                from halo import Halo
                spinner = Halo(text=(desc+'...'))
                spinner.start()

            try:
                for gen in (progress if progress else range(generations)):
                    if batch_size and 1 <= batch_size < len(X):
                        idx = torch.randperm(len(X))[:batch_size]
                        x_batch = X[idx]
                        y_batch = Y[idx]
                    
                    losses = []
                    for _ in range(population):
                        weights = []
                        biases = []

                        for i in range(len(self.layers)):
                            w = self.mutate(self.layers[i].w, mr)
                            b = self.mutate(self.layers[i].b, mr)
                            weights.append(w)
                            biases.append(b)
                        
                        h = x_batch
                        for i in range(len(self.layers)):
                            h = self.calc(h, weights[i], biases[i], self.layers[i])

                        losses.append([self.loss_fn(h, y_batch, device=self.device), weights, biases])
                        
                    p1, p2 = sorted(losses, key=lambda x: x[0])[:2]

                    if best[0] > p1[0]:
                        best = p1

                    self.loss_history.append(best[0])

                    for i in range(len(self.layers)):
                        self.layers[i].w = self.reproduce(p1[1][i], p2[1][i])
                        self.layers[i].b = self.reproduce(p1[2][i], p2[2][i])

                    loss = self.loss_fn(self.forward(x_batch), y_batch, device=self.device)

                    if early_stop != None and loss <= early_stop:
                        print(f"Loss reached {early_stop}. Training stopped...")
                        break
                    
                    if optim_mr:
                        if prev_loss > loss:
                            mr *= dr
                            n = 0
                        else:
                            n += 1
                            if n >= threshold:
                                mr += mr*(1-dr)*dr
                                n = 0
                    else:
                        mr *= dr

                    mr = max(0, min(0.5, mr))

                    prev_loss = loss

                    if loss <= p2[0]:
                        if loss <= p1[0]:
                            for i in range(len(self.layers)):
                                self.layers[i].w = self.reproduce(self.layers[i].w, p1[1][i])
                                self.layers[i].b = self.reproduce(self.layers[i].b, p1[2][i])
                        else:
                            for i in range(len(self.layers)):
                                self.layers[i].w = self.reproduce(p1[1][i], self.layers[i].w)
                                self.layers[i].b = self.reproduce(p1[2][i], self.layers[i].b)
                    else:
                        for i in range(len(self.layers)):
                            self.layers[i].w = self.reproduce(p1[1][i], p2[1][i])
                            self.layers[i].b = self.reproduce(p1[2][i], p2[2][i])
                
                loss = self.loss_fn(self.forward(x_batch), y_batch, device=self.device)
                if loss > best[0]:
                    for i in range(len(self.layers)):
                        self.layers[i].w = best[1][i]
                        self.layers[i].b = best[2][i]
            except Exception as e:
                import traceback
                print(f"[Error at {gen}]: {e}")
                traceback.print_exc()
            finally:
                if spinner:
                    spinner.succeed('Training Complete.')

    def calc(self, X: torch.Tensor, W: torch.Tensor, B: torch.Tensor, layer: Node) -> torch.Tensor:
        if not isinstance(X, torch.Tensor):
            raise ValueError("Error: X must be a torch.Tensor.")
        X = (X.float()).to(self.device)
        X = torch.addmm(B, X, W)
        if layer == self.layers[-1]:
            return self.output_fn(X)
        else:
            return self.hidden_fn(X)

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        if not isinstance(X, torch.Tensor):
            raise ValueError("Error: X must be a torch.Tensor.")
        X = (X.float()).to(self.device)
        for i in range(len(self.layers)):
            X = self.calc(X, self.layers[i].w, self.layers[i].b, self.layers[i])
        return X

    def save(self, file_name: str='model') -> None:
        model_data = {
            'layer_size' : self.layer_size,
            'layers' : self.layers,
            'loss_fn' : self.loss_fn,
            'hidden_fn' : self.hidden_fn,
            'output_fn' : self.output_fn,
            'metric' : self.metric,
            'weights' : {f'w{i}': layer.w.cpu() for i, layer in enumerate(self.layers)},
            'biases' : {f'b{i}': layer.b.cpu() for i, layer in enumerate(self.layers)}
        }

        torch.save(model_data, file_name + '.pt')

    @classmethod
    def load(cls, file_name: str='model', device: str='cpu'):
        data = torch.load(file_name + '.pt', map_location=device, weights_only=False)

        model = cls(data['layer_size'], device=device)

        model.layers = data['layers']
        model.loss_fn = data['loss_fn']
        model.hidden_fn = data['hidden_fn']
        model.output_fn = data['output_fn']

        for layer in model.layers:
            layer.w = layer.w.to(device)
            layer.b = layer.b.to(device)
        
        return model

    def graph(self, title: str='Training Progress') -> None:
        if hasattr(self, "loss_history"):
            loss_history = [loss.item() if isinstance(loss, torch.Tensor) else loss for loss in self.loss_history]

            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 4))
            plt.plot(loss_history, label="Loss", color="blue")
            plt.xlabel("Generation")
            plt.ylabel("Loss")
            plt.title(title)
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
            print("No training history found. Run `train()` first.")
    
    def __str__(self):
        return (
            f"GEO(\n"
            f"  Layer Sizes : {self.layer_size}\n"
            f"  Device      : {self.device}\n"
            f"  Init Type   : {self.init_type}\n"
            f"  Hidden Fn   : {self.hidden_fn.__name__ if hasattr(self.hidden_fn, '__name__') else str(self.hidden_fn)}\n"
            f"  Output Fn   : {self.output_fn.__name__ if hasattr(self.output_fn, '__name__') else str(self.output_fn)}\n"
            f"  Loss Fn     : {self.loss_fn.__name__ if hasattr(self.loss_fn, '__name__') else str(self.loss_fn)}\n"
            f"  Metric      : {self.metric.__name__ if hasattr(self.metric, '__name__') else str(self.metric)}\n"
            f")"
        )