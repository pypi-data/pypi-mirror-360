from memory_fs.file_fs.File_FS                          import File_FS
from memory_fs.storage_fs.Storage_FS                    import Storage_FS
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Target_FS(Type_Safe):
    file__config : Schema__Memory_FS__File__Config
    storage_fs   : Storage_FS

    @cache_on_self
    def file_fs(self):
        return File_FS(file__config=self.file__config, storage_fs=self.storage_fs)          # todo: refactor this so that we pass a schema object (for example Schema__Target_FS) that has the references to the file_config and storage objects