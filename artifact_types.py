from abc import ABC, abstractmethod


class AbstractArtifact(ABC):
    """This is template of what an artifact should look like:
        1. it can have categories, by which it can be looked up,
        and one of those categories should be itself,
        also, if contents of artifact contain another type of artifact,
        category of parent should contain categories of all children
        (TODO: maybe not the last line?)
        2. it should have an export function, which returns its
        contents in json format"""

    @abstractmethod
    def __init__(self):
        self.content = {}
        self.category = set()
        self.category.add(type(
            self).__name__)  # TODO: maybe put this in init of implemented class

    @abstractmethod
    def export(self):
        return self.content  # maybe tostring could be used


class BrowserArtifact(AbstractArtifact):
    def __init__(self):
        super().__init__()
        self.content["meta"] = {}

    def export(self):
        return super().export()


class FileMetaArtifact(AbstractArtifact):

    def __init__(self):
        super().__init__()

    def export(self):
        return super().export()


class LogFile(AbstractArtifact):
    def __init__(self):
        super().__init__()

    def export(self):
        return super().export()


class LogLine(AbstractArtifact):
    def __init__(self):
        super().__init__()

    def export(self):
        return super().export()
# TODO: descriptions of artifacts
# TODO: maybe load from config file
