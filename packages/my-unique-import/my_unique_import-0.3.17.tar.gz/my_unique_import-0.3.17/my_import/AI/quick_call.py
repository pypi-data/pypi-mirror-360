# from .AI import MyDataLoader

def transfer_to_pt(dataload):

    try:
        dataload.save_datasets()
        return True
    except:
        return False
