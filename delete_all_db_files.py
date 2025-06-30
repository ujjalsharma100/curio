import os

# Walk through all directories and delete .db files
def delete_db_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.db'):
                file_path = os.path.join(dirpath, filename)
                print(f"Deleting: {file_path}")
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.abspath(__file__))
    delete_db_files(project_root)
    print("All .db files deleted.") 