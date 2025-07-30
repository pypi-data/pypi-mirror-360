from osbot_utils.helpers.Safe_Id                        import Safe_Id
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.schemas.Schema__Memory_FS__Path__Handler import Schema__Memory_FS__Path__Handler


class Path__Handler__Custom(Schema__Memory_FS__Path__Handler):       # Handler that uses a custom path
    name        : Safe_Id               = Safe_Id("custom")
    custom_path : Safe_Str__File__Path

    # todo: file_id and file_ext should use Safe_Str helpers instead of raw str
    def generate_path(self, file_id: str, file_ext: str, is_metadata: bool = True) -> Safe_Str__File__Path:
        # Return the custom path as-is
        return self.custom_path
