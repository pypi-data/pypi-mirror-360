class AlpacaShuffler:
    def __init__(self):
        self.data = []

    def shuffler(self, data: list):
        """
        Shuffle the input data list.
        :param data: List of data to shuffle.
        :return: Shuffled list.
        """
        import random
        random.shuffle(data)
        self.data = data

    def merge_shuffler(self, data_list: list):
        """
        Merge multiple lists and shuffle the combined list.
        :param data_list: List of lists to merge and shuffle.
        :return: Merged and shuffled list.
        """
        merged_data = []
        for data in data_list:
            merged_data.extend(data)
        self.shuffler(merged_data)
        return self.data