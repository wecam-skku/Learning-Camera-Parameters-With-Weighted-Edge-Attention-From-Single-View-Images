import torch
import importlib
from data.base_dataset import BaseDataset


def find_dataset_using_name(dataset_name):
    # Given the option --dataset [datasetname],
    # the file "datasets/datasetname_dataset.py"
    # will be imported.
    dataset_filename = "data." + dataset_name + "_dataset"
    datasetlib = importlib.import_module(dataset_filename)

    # In the file, the class called DatasetNameDataset() will
    # be instantiated. It has to be a subclass of BaseDataset,
    # and it is case-insensitive.
    dataset = None
    target_dataset_name = dataset_name.replace('_', '') + 'dataset'
    for name, cls in datasetlib.__dict__.items():
        if name.lower() == target_dataset_name.lower() \
                and issubclass(cls, BaseDataset):
            dataset = cls

    if dataset is None:
        raise ValueError("In %s.py, there should be a subclass of BaseDataset "
                         "with class name that matches %s in lowercase." %
                         (dataset_filename, target_dataset_name))

    return dataset


def get_option_setter(dataset_name):
    dataset_class = find_dataset_using_name(dataset_name)
    return dataset_class.modify_commandline_options


def create_dataloader(opt):
    dataset = find_dataset_using_name(opt.dataset_mode)
    instance = dataset()
    instance.initialize(opt)
    print("dataset [%s] of size %d was created" %
          (type(instance).__name__, len(instance)))

    val_dataloader = None

    if opt.dataset_mode == "focalens":
        torch.manual_seed(777)
        dataset_len = len(instance)
        val_len = round(dataset_len * 0.2)
        instance, val_set = torch.utils.data.random_split(instance, [dataset_len-val_len, val_len])

        if opt.phase == "train":
            val_dataloader = torch.utils.data.DataLoader(
                val_set,
                batch_size=opt.batchSize,
                shuffle=False,
                num_workers=int(opt.nThreads),
                drop_last=opt.isTrain
            )

    dataloader = torch.utils.data.DataLoader(
        instance,
        batch_size=opt.batchSize,
        shuffle=(not opt.serial_batches) and (opt.phase=="train"),
        num_workers=int(opt.nThreads),
        drop_last=opt.isTrain
    )

 
    return dataloader, val_dataloader
