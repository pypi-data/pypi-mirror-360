from collections import OrderedDict


class InMemoryDB:
    """
    A simple key-value data store that stores data in memory

    Example:
        .. code-block:: python

            # Create a new in-memory database with a maximum of 100 keys
            db = InMemoryDB(max_keys=100)

            # Set a key-value pair
            db.set('key1', 'value1')

            # Get the value for a key
            value1 = db.get('key1')
            print(value1)  # Output: 'value1'

            # Delete a key-value pair
            db.delete('key1')

    Parameters:
        max_keys (``int``, *optional*):
            The maximum number of keys that can be stored in the database
            If None (default), there is no limit on the number of keys

    """

    def __init__(self, max_keys: int = 1000):
        self.data = OrderedDict()
        self.max_keys = max_keys

    def set(self, key, value):
        """
        Sets the value associated with a key in the database

        Parameters:
            key (``str``):
                The key to set the value for

            value:
                The value to associate with the key

        Returns:
            None
        """
        if self.max_keys is not None and len(self.data) >= self.max_keys:
            self._remove_oldest_key()

        self.data[key] = value

    def get(self, key):
        """
        Gets the value associated with a key in the database

        Parameters:
            key (``str``):
                The key to get the value for

        Returns:
            The value associated with the given key, or ``None`` if the key is not found
        """
        return self.data.get(key, None)

    def delete(self, key):
        """
        Deletes the key-value pair with the given key from the database

        Parameters:
            key (``str``):
                The key to delete

        Returns:
            None
        """
        del self.data[key]

    def _remove_oldest_key(self):
        self.data.popitem(last=False)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        self.delete(key)
