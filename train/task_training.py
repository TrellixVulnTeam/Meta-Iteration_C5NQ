import torch
from torch.nn import functional as F

def trainingProcessTask(data_loader, learner, loss, optimizer, regs, device, ewc = None):
    learner.train()
    running_loss = 0.0
    running_corrects = 0.0
    total_batch = 0.0
    for inputs, labels in data_loader:
        inputs = inputs.to(device)
        labels = labels.long().to(device)

        optimizer.zero_grad()

        out = learner(inputs)
        _, preds = torch.max(out, 1)
        l = loss(out, labels)

        if len(regs) > 0:
            for reg in regs:
                l += reg(learner)

        if ewc is not None:
            l += ewc.penalty(learner)

        l.backward()
        optimizer.step()

        running_loss += l.item()
        running_corrects += torch.sum(preds == labels.data)
        total_batch += 1

    return running_loss / total_batch, running_corrects / len(data_loader.dataset)

def test_normal(model, data_loader, device):
    model.eval()
    correct = 0
    for input, target in data_loader:
        input, target = input.to(device), target.long().to(device)
        output = model(input)
        correct += (F.softmax(output, dim=1).max(dim=1)[1] == target).data.sum()
    return correct.item() / len(data_loader.dataset)