import faiss

from resource.file_operator import FileOperator


class FaissIndexFileOperator(FileOperator[faiss.Index]):
    @classmethod
    def file_suffix(cls) -> str:
        return "index"

    def load(self):
        self.set_data(faiss.read_index(self.path))

    def save(self):
        faiss.write_index(self.data, self.path)
