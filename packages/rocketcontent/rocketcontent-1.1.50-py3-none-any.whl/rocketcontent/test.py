import os

class ArchiveMetadata:
    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value
    
    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value
        }

class ArchiveDocument:
    def __init__(self, document_class_id: str, file: str):
        self.document_class_id = document_class_id
        self.file = file
        self.type = os.path.splitext(file)[1][1:].upper() if os.path.splitext(file)[1] else "UNKNOWN"
        self.metadata = []
        self.section_set = False  # Track if SECTION has been set
    
    def set_section(self, section_value: str):
        """
        Set or update section value, truncated to 20 characters.
        """
        section_value = section_value[:20]
        for item in self.metadata:
            if item.name == "SECTION":
                item.value = section_value
                self.section_set = True
                return
        # If SECTION doesn't exist, add it
        self.metadata.append(ArchiveMetadata("SECTION", section_value))
        self.section_set = True
    
    def set_file(self, file: str):
        self.file = file
        self.type = os.path.splitext(file)[1][1:].upper() if os.path.splitext(file)[1] else "UNKNOWN"
    
    def add_metadata(self, name: str, value: str):
        """
        Adds a new name-value pair to the metadata, only if the name does not already exist.
        """
        if name == "SECTION":
            self.set_section(value)  # Use set_section for "SECTION"
        else:
            # Check if the name already exists in the metadata list
            if not any(item.name == name for item in self.metadata):
                self.metadata.append(ArchiveMetadata(name, value))
            else:
                raise ValueError(f"The index name '{name}' already exists in the metadata.")
    
    def to_dict(self):
        return {
            "documentClassId": self.document_class_id,
            "type": self.type,
            "metadata": [m.to_dict() for m in self.metadata]
        }

class ArchiveDocumentCollection:
    def __init__(self):
        self.objects = []
    
    def add_document(self, document: ArchiveDocument):
        self.objects.append(document)
    
    def to_dict(self):
        return {
            "objects": [doc.to_dict() for doc in self.objects]
        }
    
    def get_files(self):
        return [doc.file for doc in self.objects]

# Ejemplo de uso
if __name__ == "__main__":
    # Crear una colección
    collection = ArchiveDocumentCollection()
    
    # Crear primer documento
    doc1 = ArchiveDocument("LISTFILE", "file1.txt")
    doc1.set_section("se1FRUIT")
    doc1.add_metadata("M_BAR", "Apple")
    doc1.add_metadata("M_FOO", "Blue")
    
    # Crear segundo documento
    doc2 = ArchiveDocument("LISTFILE", "file2.txt")
    doc2.set_section("ce2FRUIT")
    doc2.add_metadata("M_BAR", "Apple")
    doc2.add_metadata("M_FOO", "Blue")
    
    # Crear tercer documento
    doc3 = ArchiveDocument("LISTFILE", "file3.pdf")
    doc3.set_section("se3FRUIT")
    doc3.add_metadata("M_BAR", "Orange")
    doc3.add_metadata("M_FOO", "Red")
    
    # Agregar documentos a la colección
    collection.add_document(doc1)
    collection.add_document(doc2)
    collection.add_document(doc3)
    
    # Iterar por los files
    print("Lista de files:")
    for file in collection.get_files():
        print(file)
    
    # Convertir a JSON
    import json
    print("\nJSON output:")
    print(json.dumps(collection.to_dict(), indent=2))