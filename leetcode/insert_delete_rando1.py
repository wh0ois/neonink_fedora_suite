#https://leetcode.com/problems/insert-delete-getrandom-o1-duplicates-allowed/submissions/

class RandomizedCollection:

    def __init__(self):
        self.elements = []  # List to store the elements
        self.indices = {}   # Dictionary to store the indices of each element
                             # The value for each key in the dictionary is a set of indices

    def insert(self, val: int) -> bool:
        if val in self.indices:
            self.indices[val].add(len(self.elements))
            self.elements.append(val)
            return False
        else:
            self.indices[val] = {len(self.elements)}
            self.elements.append(val)
            return True

    def remove(self, val: int) -> bool:
        if val in self.indices:
            index_to_remove = self.indices[val].pop()  # Get an index of the element to remove
            last_element = self.elements[-1]  # Get the last element in the list
            self.elements[index_to_remove] = last_element  # Replace the element to remove with the last element
            self.indices[last_element].add(index_to_remove)  # Update the index of the last element
            self.indices[last_element].remove(len(self.elements) - 1)  # Remove the old index of the last element
            self.elements.pop()  # Remove the last element from the list

            if not self.indices[val]:  # If there are no more occurrences of val, remove it from the dictionary
                del self.indices[val]
            return True
        else:
            return False

    def getRandom(self) -> int:
        return random.choice(self.elements)
