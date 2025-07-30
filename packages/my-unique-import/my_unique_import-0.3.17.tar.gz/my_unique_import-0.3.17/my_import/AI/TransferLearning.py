from torch import nn

from .AI import Trainer, MyDataLoader


class TLTrainer(Trainer):

    def __init__(self, model: nn.Module, data_loader: MyDataLoader, criterion=None, optimizer=None, device=None,
                 auto_classifer=True, log_dir=None, is_model_graph=True, auto_save=True, writer=None,
                 verbose=0, evaluation_interval=10, mem_threshold=0.9, lr=0.01, scheduler=None,
                 patience=5, save_interval=10, freeze_layers_num=-1, **kwargs):

        super().__init__(model, data_loader, criterion, optimizer, device, auto_classifer, log_dir, is_model_graph,
                         auto_save, writer, verbose, evaluation_interval, mem_threshold, lr, scheduler, patience,
                         save_interval, **kwargs)
        layer_count = 0
        if freeze_layers_num == -1:
            freeze_layers_num = self.num_layers - 1
        # print(self.num_layers)
        for name, param in self.model.named_parameters():
            if layer_count < freeze_layers_num:
                param.requires_grad = False
                layer_count += 1
            else:
                param.requires_grad = True
        print(f'Freezing layers: {freeze_layers_num}')