from osbot_utils.helpers.Safe_Id                        import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__Path__Handler import Schema__Memory_FS__Path__Handler


class Path__Handler__Versioned(Schema__Memory_FS__Path__Handler):    # Handler that stores files with version numbers (calculated from chain)
    name : Safe_Id = Safe_Id("versioned")

    # todo: file_id and file_ext should use Safe_Str helpers rather than raw str types
    def generate_path(self, file_id: str, file_ext: str, is_metadata: bool = True, version: int = 1) -> Safe_Str__File__Path:
        ext = ".json" if is_metadata else f".{file_ext}"
        return Safe_Str__File__Path(f"v{version}/{file_id}{ext}")
